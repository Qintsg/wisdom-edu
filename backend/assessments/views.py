"""
测评模块 - 视图

提供测评、问卷相关的API端点
"""
import logging
import threading

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from typing import cast
from django.db import transaction

from common.responses import success_response, error_response
from common.utils import (
    answer_tokens,
    build_answer_display,
    clean_display_text,
    decorate_question_options,
    normalize_question_options,
    serialize_answer_payload,
)
from common.permissions import IsStudent
from users.models import HabitPreference, User
from knowledge.models import KnowledgeMastery
from learning.path_rules import apply_prerequisite_caps
from .models import (
    Assessment, Question, SurveyQuestion, AssessmentResult,
    AssessmentQuestion,
    AbilityScore, AssessmentStatus, AnswerHistory
)

# 固定ID常量，用于标识非Assessment模型的测评
HABIT_SURVEY_FIXED_ID = 5001
ABILITY_ASSESSMENT_FIXED_ID = 5002

logger = logging.getLogger(__name__)


def _get_authenticated_user(request) -> User:
    """
    将请求中的用户对象收窄为项目内 User 类型。
    :param request: DRF 请求对象。
    :return: 已认证用户。
    """
    return cast(User, request.user)


def _calculate_initial_mastery_baseline(correct_count: int, total_count: int) -> float:
    """
    初始评测掌握度基线。

    使用更保守的样本量平滑，避免少量题目或随机作答导致掌握度虚高。
    """
    prior_mean = 0.25
    prior_strength = 4.0
    if total_count <= 0:
        return round(prior_mean, 4)
    mastery = (correct_count + prior_mean * prior_strength) / (total_count + prior_strength)
    return round(max(0.0, min(0.85, mastery)), 4)


def _extract_answer_payload(answer):
    """提取题目答案载荷中的统一答案值。"""
    if isinstance(answer, dict):
        if 'answers' in answer:
            return answer.get('answers')
        return answer.get('answer', answer)
    return answer


def _answer_tokens(answer, question_type):
    """将作答内容规整为可比较的 token 集合。"""
    return answer_tokens(answer, question_type)


def _option_tokens(option):
    """将选项对象规整为 token 集合。"""
    from common.utils import option_tokens
    return option_tokens(option)


def _format_option_display(option):
    """生成选项展示文本。"""
    prefix = option.get('letter') or option.get('value') or ''
    content = option.get('label') or option.get('content') or option.get('value') or ''
    return f"{prefix}. {content}" if prefix else content


def _build_answer_display(answer, question_type, options):
    """构建学生答案或正确答案的展示文本。"""
    return build_answer_display(answer, question_type, options)


def _clean_text(value):
    """清洗文本，避免 nan、空白和脏字符直接进入响应。"""
    return clean_display_text(value)


def _get_question_title(question):
    """为题干提供稳健的显示文本，避免出现 'nan'。"""
    content = _clean_text(getattr(question, 'content', ''))
    if not content:
        content = _clean_text(getattr(question, 'title', ''))
    if not content and getattr(question, 'analysis', None):
        # 取解析首行作为兜底
        content = _clean_text(str(question.analysis).splitlines()[0])
    if not content:
        content = f"题干缺失（题目ID {question.id}），请联系教师补充"
    return content


def _normalize_options(raw_options, question_type):
    """统一规整题目选项结构。"""
    return normalize_question_options(raw_options, question_type)


def _persist_mastery_snapshot(
    user: User,
    course_id: int | str,
    mastery_map: dict[int, float],
    point_stats: dict[int, dict[str, object]],
) -> list[dict[str, object]]:
    """
    回写知识点掌握度并生成接口响应所需的掌握度列表。
    :param user: 当前学生用户。
    :param course_id: 课程 ID。
    :param mastery_map: 知识点掌握度映射。
    :param point_stats: 知识点统计信息。
    :return: 掌握度列表。
    """
    normalized_course_id = int(course_id)
    mastery_list: list[dict[str, object]] = []
    for point_id, mastery_rate in mastery_map.items():
        point_name = str(point_stats.get(point_id, {}).get('name', f'知识点{point_id}'))
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course_id=normalized_course_id,
            knowledge_point_id=point_id,
            defaults={'mastery_rate': mastery_rate}
        )
        mastery_list.append({
            'point_id': point_id,
            'point_name': point_name,
            'mastery_rate': mastery_rate
        })
    return mastery_list


def _upsert_knowledge_assessment_result(
    user: User,
    assessment: Assessment,
    course_id: int | str,
    answer_dict: dict[str, object],
    total_score: float,
    mastery_list: list[dict[str, object]],
    question_details: list[dict[str, object]],
    questions: list[Question],
    correct_count: int,
    total_question_count: int,
) -> None:
    """
    统一写入知识测评结果，避免重复组装结果载荷。
    :param user: 当前学生用户。
    :param assessment: 知识测评对象。
    :param course_id: 课程 ID。
    :param answer_dict: 作答映射。
    :param total_score: 学生得分。
    :param mastery_list: 掌握度列表。
    :param question_details: 题目明细。
    :param questions: 题目列表。
    :param correct_count: 答对题数。
    :param total_question_count: 题目总数。
    :return: None。
    """
    AssessmentResult.objects.update_or_create(
        user=user,
        assessment=assessment,
        defaults={
            'course_id': course_id,
            'answers': answer_dict,
            'score': total_score,
            'result_data': {
                'mastery': mastery_list,
                'question_details': question_details,
                'total_score': sum(float(q.score or 0) for q in questions),
                'correct_count': correct_count,
                'total_count': total_question_count,
            }
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_knowledge_assessment(request):
    """
    获取知识点掌握度测评试题
    GET /api/assessments/initial/knowledge
    
    如果课程没有预设的知识测评，会自动从题库中选取题目创建
    """
    course_id = request.query_params.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID')
    
    assessment = Assessment.objects.filter(
        course_id=course_id,
        assessment_type='knowledge',
        is_active=True
    ).first()
    
    if not assessment:
        # 自动从课程题库创建知识测评
        # 使用全部 for_initial_assessment 标记题目，不做随机裁剪
        course_questions_qs = Question.objects.filter(
            course_id=course_id
        )
        preferred_questions = course_questions_qs.filter(for_initial_assessment=True).order_by('id')
        if preferred_questions.exists():
            course_questions = preferred_questions
        else:
            course_questions = course_questions_qs.order_by('id')  # 使用全部题目
        
        if not course_questions.exists():
            return error_response(
                msg='该课程暂无知识测评题目，请联系教师添加题库',
                code=404
            )
        
        # 创建临时知识测评
        from courses.models import Course
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return error_response(msg='课程不存在', code=404)
        
        assessment = Assessment.objects.create(
            course=course,
            title=f'{course.name} 知识水平测评',
            assessment_type='knowledge',
            description='系统自动生成的知识水平测评',
            is_active=True
        )
        AssessmentQuestion.objects.bulk_create([
            AssessmentQuestion(
                assessment=assessment,
                question=q,
                order=idx,
            )
            for idx, q in enumerate(course_questions)
        ])
    
    questions: list[Question] = list(
        assessment.questions.all()
        .prefetch_related('knowledge_points')
        .order_by('assessmentquestion__order', 'id')
    )

    question_payload = []
    for idx, q in enumerate(questions, start=1):
        normalized_options = _normalize_options(q.options, q.question_type)
        title = _get_question_title(q)
        question_payload.append({
            'question_id': q.id,
            'order': idx,
            'content': title,
            'title': title,
            'options': normalized_options,
            'type': q.question_type,
            'question_type': q.question_type,
            'score': float(q.score),
            'difficulty': q.difficulty,
            'analysis': _clean_text(q.analysis),
            'points': list(q.knowledge_points.values_list('id', flat=True))
        })

    return success_response(
        data={
            'assessment_id': assessment.id,
            'title': assessment.title,
            'questions': question_payload
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudent])
def submit_knowledge_assessment(request):
    """
    提交知识点掌握度测评答案
    POST /api/student/assessments/initial/knowledge
    
    注意：仅学生可以提交测评
    """
    course_id = request.data.get('course_id')
    answers = request.data.get('answers', [])
    
    if not course_id or not answers:
        return error_response(msg='缺少必要参数')
    
    user = _get_authenticated_user(request)

    # 防止重复提交：知识测评完成后直接复用最近结果。
    existing_status = AssessmentStatus.objects.filter(user=user, course_id=course_id).first()
    if existing_status and existing_status.knowledge_done:
        existing_result = AssessmentResult.objects.filter(
            user=user, course_id=course_id,
            assessment__assessment_type='knowledge'
        ).order_by('-completed_at').first()
        if existing_result:
            return success_response(
                data={
                    'score': float(existing_result.score),
                    'completed': True,
                    'message': '知识测评已提交，请勿重复提交'
                },
                msg='知识测评已完成'
            )
    
    try:
        assessment = Assessment.objects.get(
            course_id=course_id,
            assessment_type='knowledge',
            is_active=True
        )
    except Assessment.DoesNotExist:
        return error_response(msg='未找到该课程的知识测评', code=404)
    
    # 构建答案字典
    answer_dict = {str(a['question_id']): a['answer'] for a in answers}
    
    questions: list[Question] = list(
        assessment.questions.all().prefetch_related('knowledge_points')
    )
    total_score = 0
    correct_count = 0
    total_question_count = 0
    point_stats = {}  # {point_id: {'correct': 0, 'total': 0, 'name': ''}}
    answer_history_records = []
    question_details = []  # 每题明细

    def normalize_bool(val):
        """将真假题答案归一化为布尔值。"""
        if isinstance(val, bool):
            return val
        if val is None:
            return None
        s = str(val).strip().lower()
        if s in ['true', 't', '1', 'y', 'yes', '是', '对', '正确', '√', 'right']:
            return True
        if s in ['false', 'f', '0', 'n', 'no', '否', '错', '错误', '×', 'wrong']:
            return False
        return None

    for q in questions:
        q_id = str(q.id)
        student_answer_raw = answer_dict.get(q_id)
        correct_answer_raw = q.answer.get('answer', q.answer) if isinstance(q.answer, dict) else q.answer

        is_correct = False
        if q.question_type in ['single_choice', 'true_false']:
            if q.question_type == 'true_false':
                student_bool = normalize_bool(student_answer_raw)
                correct_bool = normalize_bool(correct_answer_raw)
                is_correct = (student_bool is not None and correct_bool is not None and student_bool == correct_bool)
            else:
                is_correct = _clean_text(student_answer_raw) == _clean_text(correct_answer_raw)
        elif q.question_type == 'multiple_choice':
            correct_set = {_clean_text(x) for x in (correct_answer_raw if isinstance(correct_answer_raw, list) else [correct_answer_raw]) if _clean_text(x)}
            student_set = {_clean_text(x) for x in (student_answer_raw if isinstance(student_answer_raw, list) else [student_answer_raw]) if _clean_text(x)}
            is_correct = correct_set and (correct_set == student_set)

        if is_correct:
            total_score += float(q.score)
            correct_count += 1

        total_question_count += 1

        # 收集每题明细
        decorated_options = decorate_question_options(
            q.options,
            q.question_type,
            student_answer=student_answer_raw,
            correct_answer=correct_answer_raw,
        )

        question_details.append({
            'question_id': q.id,
            'content': _get_question_title(q),
            'question_type': q.question_type,
            'student_answer': student_answer_raw,
            'correct_answer': correct_answer_raw,
            'student_answer_display': _build_answer_display(student_answer_raw, q.question_type, decorated_options),
            'correct_answer_display': _build_answer_display(correct_answer_raw, q.question_type, decorated_options),
            'is_correct': is_correct,
            'analysis': _clean_text(q.analysis),
            'options': decorated_options,
            'knowledge_points': [
                {'id': p.id, 'name': p.name} for p in q.knowledge_points.all()
            ],
        })

        # 统计知识点
        for point in q.knowledge_points.all():
            if point.id not in point_stats:
                point_stats[point.id] = {'correct': 0, 'total': 0, 'name': point.name}
            point_stats[point.id]['total'] += 1
            if is_correct:
                point_stats[point.id]['correct'] += 1

            # 收集答题历史用于KT模型
            answer_history_records.append({
                'question_id': q.id,
                'knowledge_point_id': point.id,
                'correct': 1 if is_correct else 0
            })

            # 写入 AnswerHistory 以便后续 KT 服务（画像刷新等）可从 DB 查询
            AnswerHistory.objects.create(
                user=user,
                course_id=course_id,
                question=q,
                knowledge_point=point,
                student_answer=serialize_answer_payload(q.question_type, student_answer_raw),
                correct_answer=serialize_answer_payload(q.question_type, correct_answer_raw),
                is_correct=is_correct,
                score=float(q.score) if is_correct else 0,
                source='initial',
            )
    
    # 计算各知识点掌握度基线（更保守，不再直接使用简单正确率）
    mastery_map = {}
    mastery_map = {
        point_id: _calculate_initial_mastery_baseline(stats['correct'], stats['total'])
        for point_id, stats in point_stats.items()
    }
    with transaction.atomic():
        mastery_list = _persist_mastery_snapshot(user, course_id, mastery_map, point_stats)
        
        # 保存测评结果（含答题详情供轮询接口读取）
        _upsert_knowledge_assessment_result(
            user,
            assessment,
            course_id,
            answer_dict,
            total_score,
            mastery_list,
            question_details,
            list(questions),
            correct_count,
            total_question_count,
        )
        
        # 更新测评状态
        status, _ = AssessmentStatus.objects.get_or_create(
            user=user,
            course_id=course_id
        )
        status.knowledge_done = True
        status.save()

        # 知识测评完成后，清理旧学习路径，触发后续按最新掌握度重建
        from learning.models import LearningPath
        LearningPath.objects.filter(user=user, course_id=course_id).delete()

    # 调用KT模型融合预测（若可用），进一步细化掌握度
    try:
        from ai_services.services import kt_service
        kt_result = kt_service.predict_mastery(
            user_id=user.id,
            course_id=course_id,
            answer_history=answer_history_records
        )
        kt_predictions = kt_result.get('predictions') or {}
        if kt_predictions:
            blended_mastery_map = dict(mastery_map)
            for kp_id, rate in kt_predictions.items():
                try:
                    rate_f = float(rate)
                except Exception:
                    continue
                point_total = max(point_stats.get(kp_id, {}).get('total', 0), 0)
                baseline = float(mastery_map.get(kp_id, 0.25))
                # 初始评测阶段只允许KT做有限校准，避免少量历史把掌握度抬高过头
                kt_weight = min(0.35, 0.1 + point_total * 0.08)
                blended = baseline * (1 - kt_weight) + rate_f * kt_weight
                blended = min(blended, baseline + 0.12)
                blended_mastery_map[kp_id] = round(max(0.0, min(0.9, blended)), 4)

            blended_mastery_map = apply_prerequisite_caps(
                blended_mastery_map,
                int(course_id),
            )

            mastery_list = _persist_mastery_snapshot(
                user, course_id, blended_mastery_map, point_stats
            )
            mastery_map = blended_mastery_map
        else:
            mastery_map = apply_prerequisite_caps(mastery_map, int(course_id))
    except Exception as e:
        logger.warning(f"KT预测或更新失败: {e}")

    # 无论KT是否成功，都在最后执行一次严格前置约束并回写
    mastery_map = apply_prerequisite_caps(mastery_map, int(course_id))
    mastery_list = _persist_mastery_snapshot(user, course_id, mastery_map, point_stats)

    _upsert_knowledge_assessment_result(
        user,
        assessment,
        course_id,
        answer_dict,
        total_score,
        mastery_list,
        question_details,
        list(questions),
        correct_count,
        total_question_count,
    )

    # 标记正在异步生成中
    status.generating = True
    status.generation_error = None
    status.save(update_fields=['generating', 'generation_error'])

    # 启动后台线程执行耗时的 LLM 操作（路径生成、画像刷新、反馈报告）
    threading.Thread(
        target=_async_generate_after_assessment,
        args=(user.id, course_id, assessment.id, question_details),
        daemon=True
    ).start()

    return success_response(
        data={
            'score': total_score,
            'total_score': sum(float(q.score or 0) for q in questions),
            'correct_count': correct_count,
            'total_count': total_question_count,
            'mastery': mastery_list,
            'question_details': question_details,
            'generating': True,
            'completed': True
        },
        msg='测评提交成功，正在生成学习路径和报告…'
    )


def _async_generate_after_assessment(user_id, course_id, assessment_id, question_details):
    """
    后台线程：在知识测评提交后异步完成耗时操作
    - 生成/刷新学习路径（LLM）
    - 刷新学习者画像（LLM）
    - 生成反馈报告（LLM）
    完成后将 AssessmentStatus.generating 置为 False。
    """
    import django
    django.setup()
    from courses.models import Course

    try:
        user = User.objects.get(id=user_id)
        assessment = Assessment.objects.get(id=assessment_id)
    except Exception as e:
        logger.error(f"异步生成：无法获取用户或测评 user_id={user_id}: {e}")
        AssessmentStatus.objects.filter(user_id=user_id, course_id=course_id).update(
            generating=False, generation_error=str(e)
        )
        return

    errors = []

    # 1. 生成/刷新学习路径
    try:
        from ai_services.services import PathService
        course = Course.objects.get(id=course_id)
        PathService().generate_path(user, course)
        logger.info(f"异步生成：学习路径生成成功 user={user_id} course={course_id}")
    except Exception as e:
        logger.error(f"异步生成：学习路径生成失败 user={user_id}: {e}")
        errors.append(f"学习路径: {e}")

    # 2. 刷新学习者画像
    try:
        from users.services import get_learner_profile_service
        get_learner_profile_service(user).generate_profile_for_course(course_id)
        logger.info(f"异步生成：学习者画像刷新成功 user={user_id} course={course_id}")
    except Exception as e:
        logger.error(f"异步生成：学习画像刷新失败 user={user_id}: {e}")
        errors.append(f"学习画像: {e}")

    # 3. 生成反馈报告
    try:
        from exams.models import FeedbackReport
        from ai_services.services import llm_service as _llm

        assessment_result = AssessmentResult.objects.filter(
            user_id=user_id, assessment=assessment
        ).first()
        if assessment_result is None:
            raise AssessmentResult.DoesNotExist('未找到知识测评结果')

        mistakes = [d for d in question_details if not d['is_correct']]
        assessment_score = float(assessment_result.score or 0)
        assessment_total_score = float(assessment_result.result_data.get('total_score', 0)) if isinstance(assessment_result.result_data, dict) else 0
        report_content = _llm.generate_feedback_report(
            exam_info={'title': assessment.title, 'type': '初始知识评测'},
            score=assessment_score,
            total_score=assessment_total_score,
            mistakes=[{
                'question_text': m['content'],
                'knowledge_point_name': m['knowledge_points'][0]['name'] if m['knowledge_points'] else '',
                'student_answer': m['student_answer'],
                'correct_answer': m['correct_answer'],
                'analysis': m['analysis'],
            } for m in mistakes[:5]],
        )

        report, _ = FeedbackReport.objects.update_or_create(
            user_id=user_id,
            source='assessment',
            assessment_result=assessment_result,
            defaults={
                'exam': None,
                'status': 'completed',
                'overview': {
                    'score': assessment_score,
                    'total_score': assessment_total_score,
                    'correct_count': sum(1 for d in question_details if d['is_correct']),
                    'total_count': len(question_details),
                    'accuracy': round(sum(1 for d in question_details if d['is_correct']) / max(len(question_details), 1) * 100, 1),
                    'summary': report_content.get('summary', '') if isinstance(report_content, dict) else '',
                    'knowledge_gaps': report_content.get('knowledge_gaps', []) if isinstance(report_content, dict) else [],
                },
                'analysis': report_content.get('analysis', '') if isinstance(report_content, dict) else str(report_content),
                'recommendations': report_content.get('recommendations', []) if isinstance(report_content, dict) else [],
                'next_tasks': report_content.get('next_tasks', []) if isinstance(report_content, dict) else [],
                'conclusion': report_content.get('encouragement', '') if isinstance(report_content, dict) else '',
            }
        )
        logger.info(f"异步生成：反馈报告生成成功 user={user_id} report={report.id}")
    except Exception as e:
        logger.error(f"异步生成：反馈报告生成失败 user={user_id}: {e}")
        errors.append(f"反馈报告: {e}")

    # 更新状态
    AssessmentStatus.objects.filter(user_id=user_id, course_id=course_id).update(
        generating=False,
        generation_error='; '.join(errors) if errors else None
    )
    logger.info(f"异步生成完成 user={user_id} course={course_id} errors={len(errors)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudent])
def get_knowledge_result(request):
    """
    轮询获取知识测评结果（含异步生成状态）
    GET /api/student/assessments/initial/knowledge/result?course_id=xxx
    
    返回：评分数据 + 反馈报告 + generating状态
    """
    course_id = request.query_params.get('course_id')
    if not course_id:
        return error_response(msg='缺少course_id参数')

    user = _get_authenticated_user(request)

    status = AssessmentStatus.objects.filter(user=user, course_id=course_id).first()
    if not status or not status.knowledge_done:
        return success_response(data={
            'score': 0,
            'total_score': 0,
            'correct_count': 0,
            'total_count': 0,
            'mastery': [],
            'question_details': [],
            'feedback_report': None,
            'generating': False,
            'generation_error': None,
            'completed': False,
        }, msg='尚未完成知识测评')

    result = AssessmentResult.objects.filter(
        user=user, course_id=course_id,
        assessment__assessment_type='knowledge'
    ).order_by('-completed_at').first()

    if not result:
        return success_response(data={
            'score': 0,
            'total_score': 0,
            'correct_count': 0,
            'total_count': 0,
            'mastery': [],
            'question_details': [],
            'feedback_report': None,
            'generating': bool(status and status.generating),
            'generation_error': status.generation_error if status else None,
            'completed': False,
        }, msg='未找到评测结果')

    masteries = KnowledgeMastery.objects.filter(
        user=user, course_id=course_id
    ).select_related('knowledge_point')
    mastery_list = [
        {
            'point_id': m.knowledge_point_id,
            'point_name': m.knowledge_point.name if m.knowledge_point else '',
            'mastery_rate': float(m.mastery_rate)
        }
        for m in masteries
    ]

    feedback_report_data = None
    if not status.generating:
        try:
            from exams.models import FeedbackReport
            report = FeedbackReport.objects.filter(
                user=user, source='assessment', assessment_result=result
            ).first()
            if report and report.status == 'completed':
                feedback_report_data = {
                    'report_id': report.id,
                    'overview': report.overview or {},
                    'summary': (report.overview or {}).get('summary', ''),
                    'analysis': report.analysis if isinstance(report.analysis, str) else '',
                    'knowledge_gaps': (report.overview or {}).get('knowledge_gaps', []) or (report.analysis if isinstance(report.analysis, list) else []),
                    'recommendations': report.recommendations or [],
                    'next_tasks': report.next_tasks or [],
                    'encouragement': report.conclusion or '',
                    'conclusion': report.conclusion or '',
                }
        except Exception as e:
            logger.warning(f"获取反馈报告失败: {e}")

    question_details = result.result_data.get('question_details', []) if isinstance(result.result_data, dict) else []

    return success_response(
        data={
            'score': float(result.score),
            'total_score': float(result.result_data.get('total_score', 0)) if isinstance(result.result_data, dict) else 0,
            'correct_count': result.result_data.get('correct_count', 0) if isinstance(result.result_data, dict) else 0,
            'total_count': result.result_data.get('total_count', 0) if isinstance(result.result_data, dict) else 0,
            'mastery': mastery_list,
            'question_details': question_details,
            'feedback_report': feedback_report_data,
            'generating': status.generating,
            'generation_error': status.generation_error,
            'completed': True
        },
        msg='获取成功'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudent])
def retake_ability_assessment(request):
    """
    重新进入能力评测（重做入口）
    GET /api/student/assessments/initial/ability/retake

    说明：能力评测是全局问卷，重做时返回最新题目即可。
    """
    return get_ability_assessment(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ability_assessment(request):
    """
    获取学习能力评估测评试题
    GET /api/assessments/initial/ability
    
    可选参数：
    - course_id: 课程ID，如提供则获取该课程的能力评估
                 如未提供则获取全局能力评估问卷
    """
    course_id = request.query_params.get('course_id')
    
    # 优先使用课程级能力评估，缺失时再回退到全局问卷。
    assessment = None
    if course_id:
        assessment = Assessment.objects.filter(
            course_id=course_id,
            assessment_type='ability',
            is_active=True
        ).first()
    
    # 如果没有课程特定的评估，使用全局问卷
    if not assessment:
        from .models import SurveyQuestion
        survey_question_qs = SurveyQuestion.objects.filter(
            survey_type='ability'
        ).order_by('order')
        
        if not survey_question_qs.exists():
            # C-WAIS 简化自评量表：4维度×4题=16题
            # 维度：言语理解、知觉推理、工作记忆、处理速度
            default_questions = [
                # ===== 言语理解维度 =====
                {
                    'text': '阅读一段复杂的技术文档后，你能在多大程度上用自己的话向他人解释其核心思想？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '言语理解',
                    'options': [
                        {'value': 'A', 'label': '能完整且清晰地复述和解释', 'score': 5},
                        {'value': 'B', 'label': '能解释大部分要点', 'score': 4},
                        {'value': 'C', 'label': '只能解释部分关键概念', 'score': 3},
                        {'value': 'D', 'label': '需要反复阅读才能部分理解', 'score': 2},
                        {'value': 'E', 'label': '很难向他人解释', 'score': 1}
                    ],
                    'order': 1, 'is_global': True
                },
                {
                    'text': '当老师讲解一个有多种含义的术语时，你能区分它在不同语境下的含义吗？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '言语理解',
                    'options': [
                        {'value': 'A', 'label': '几乎总能准确区分', 'score': 5},
                        {'value': 'B', 'label': '大多数时候可以', 'score': 4},
                        {'value': 'C', 'label': '有时候会混淆', 'score': 3},
                        {'value': 'D', 'label': '经常需要查阅资料', 'score': 2},
                        {'value': 'E', 'label': '很难区分不同含义', 'score': 1}
                    ],
                    'order': 2, 'is_global': True
                },
                {
                    'text': '遇到不熟悉的专业词汇，你是否能通过上下文推断其大致含义？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '言语理解',
                    'options': [
                        {'value': 'A', 'label': '几乎总能成功推断', 'score': 5},
                        {'value': 'B', 'label': '大多数时候可以', 'score': 4},
                        {'value': 'C', 'label': '有时候能推断出来', 'score': 3},
                        {'value': 'D', 'label': '很少能推断出来', 'score': 2},
                        {'value': 'E', 'label': '完全无法推断', 'score': 1}
                    ],
                    'order': 3, 'is_global': True
                },
                {
                    'text': '在课堂讨论中，你能多好地组织语言来表达自己的观点和论据？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '言语理解',
                    'options': [
                        {'value': 'A', 'label': '逻辑清晰、论据充分', 'score': 5},
                        {'value': 'B', 'label': '能较好地表达主要观点', 'score': 4},
                        {'value': 'C', 'label': '有想法但表达不够完整', 'score': 3},
                        {'value': 'D', 'label': '较难组织语言来表达', 'score': 2},
                        {'value': 'E', 'label': '基本无法参与讨论', 'score': 1}
                    ],
                    'order': 4, 'is_global': True
                },
                # ===== 知觉推理维度 =====
                {
                    'text': '观察一组图形或数据的规律（如：2, 6, 12, 20, 30），你能多快发现其中的模式？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '知觉推理',
                    'options': [
                        {'value': 'A', 'label': '几乎立刻就能发现', 'score': 5},
                        {'value': 'B', 'label': '需要简短思考后能发现', 'score': 4},
                        {'value': 'C', 'label': '需要较长时间分析', 'score': 3},
                        {'value': 'D', 'label': '需要提示才能发现', 'score': 2},
                        {'value': 'E', 'label': '很难独自发现规律', 'score': 1}
                    ],
                    'order': 5, 'is_global': True
                },
                {
                    'text': '面对一个复杂问题，你倾向于怎样分析？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '知觉推理',
                    'options': [
                        {'value': 'A', 'label': '将问题拆解为子问题，逐步推理', 'score': 5},
                        {'value': 'B', 'label': '画图或列表来帮助分析', 'score': 4},
                        {'value': 'C', 'label': '寻找类似案例作参考', 'score': 3},
                        {'value': 'D', 'label': '尝试不同方法直到找到答案', 'score': 2},
                        {'value': 'E', 'label': '等待老师或他人的指导', 'score': 1}
                    ],
                    'order': 6, 'is_global': True
                },
                {
                    'text': '当你看到一个流程图或系统架构图时，你能多好地理解各部分之间的关系？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '知觉推理',
                    'options': [
                        {'value': 'A', 'label': '能快速理解整体结构和关系', 'score': 5},
                        {'value': 'B', 'label': '能理解大部分关系', 'score': 4},
                        {'value': 'C', 'label': '需要一些时间才能理解', 'score': 3},
                        {'value': 'D', 'label': '需要文字说明辅助才能理解', 'score': 2},
                        {'value': 'E', 'label': '看图形很难理解', 'score': 1}
                    ],
                    'order': 7, 'is_global': True
                },
                {
                    'text': '你是否擅长在脑中想象和操作空间关系（如想象一个物体旋转后的样子）？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '知觉推理',
                    'options': [
                        {'value': 'A', 'label': '非常擅长，能清晰想象', 'score': 5},
                        {'value': 'B', 'label': '大多数情况下可以', 'score': 4},
                        {'value': 'C', 'label': '简单的可以，复杂的有困难', 'score': 3},
                        {'value': 'D', 'label': '较难在脑中想象', 'score': 2},
                        {'value': 'E', 'label': '几乎无法做到', 'score': 1}
                    ],
                    'order': 8, 'is_global': True
                },
                # ===== 工作记忆维度 =====
                {
                    'text': '在课堂上听讲时，你能同时理解内容并记录笔记吗？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '工作记忆',
                    'options': [
                        {'value': 'A', 'label': '可以同时进行且不遗漏', 'score': 5},
                        {'value': 'B', 'label': '大多数时候可以兼顾', 'score': 4},
                        {'value': 'C', 'label': '有时候会记漏要点', 'score': 3},
                        {'value': 'D', 'label': '记笔记时经常跟不上讲课内容', 'score': 2},
                        {'value': 'E', 'label': '很难同时做两件事', 'score': 1}
                    ],
                    'order': 9, 'is_global': True
                },
                {
                    'text': '当你在解题过程中需要同时记住多个条件和中间结果时，你的表现如何？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '工作记忆',
                    'options': [
                        {'value': 'A', 'label': '能轻松保持跟踪所有信息', 'score': 5},
                        {'value': 'B', 'label': '能记住大部分关键信息', 'score': 4},
                        {'value': 'C', 'label': '需要写下来才能管理', 'score': 3},
                        {'value': 'D', 'label': '经常忘记中间步骤', 'score': 2},
                        {'value': 'E', 'label': '很容易混淆或遗忘', 'score': 1}
                    ],
                    'order': 10, 'is_global': True
                },
                {
                    'text': '你阅读完一篇长文章后，能记住多少内容？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '工作记忆',
                    'options': [
                        {'value': 'A', 'label': '能记住大部分要点和关键细节', 'score': 5},
                        {'value': 'B', 'label': '能记住主要框架和核心要点', 'score': 4},
                        {'value': 'C', 'label': '只能记住几个主要概念', 'score': 3},
                        {'value': 'D', 'label': '只记得大概印象', 'score': 2},
                        {'value': 'E', 'label': '读完很快就忘了', 'score': 1}
                    ],
                    'order': 11, 'is_global': True
                },
                {
                    'text': '你能在多大程度上在心算中完成多步骤运算（如连续加减乘除）？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '工作记忆',
                    'options': [
                        {'value': 'A', 'label': '能轻松完成复杂心算', 'score': 5},
                        {'value': 'B', 'label': '能完成中等难度心算', 'score': 4},
                        {'value': 'C', 'label': '只能做简单心算', 'score': 3},
                        {'value': 'D', 'label': '需要纸笔辅助', 'score': 2},
                        {'value': 'E', 'label': '几乎无法心算', 'score': 1}
                    ],
                    'order': 12, 'is_global': True
                },
                # ===== 处理速度维度 =====
                {
                    'text': '你完成一组简单但数量多的任务（如批量整理文件、重复性练习）的速度如何？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '处理速度',
                    'options': [
                        {'value': 'A', 'label': '非常快且很少出错', 'score': 5},
                        {'value': 'B', 'label': '速度较快，偶尔有小错', 'score': 4},
                        {'value': 'C', 'label': '速度一般', 'score': 3},
                        {'value': 'D', 'label': '速度较慢但准确', 'score': 2},
                        {'value': 'E', 'label': '速度慢且容易出错', 'score': 1}
                    ],
                    'order': 13, 'is_global': True
                },
                {
                    'text': '当你需要集中注意力快速浏览和提取关键信息时，你的效率如何？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '处理速度',
                    'options': [
                        {'value': 'A', 'label': '很快就能找到关键信息', 'score': 5},
                        {'value': 'B', 'label': '能较快地定位重点', 'score': 4},
                        {'value': 'C', 'label': '需要仔细逐行阅读', 'score': 3},
                        {'value': 'D', 'label': '经常漏看关键信息', 'score': 2},
                        {'value': 'E', 'label': '无法快速浏览，必须逐字阅读', 'score': 1}
                    ],
                    'order': 14, 'is_global': True
                },
                {
                    'text': '面对一道你熟悉类型的题目，你通常能多快给出答案？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '处理速度',
                    'options': [
                        {'value': 'A', 'label': '几秒内就能反应', 'score': 5},
                        {'value': 'B', 'label': '很快就能回忆起解法', 'score': 4},
                        {'value': 'C', 'label': '需要一些时间回忆', 'score': 3},
                        {'value': 'D', 'label': '需要较长时间思考', 'score': 2},
                        {'value': 'E', 'label': '即使熟悉也很慢', 'score': 1}
                    ],
                    'order': 15, 'is_global': True
                },
                {
                    'text': '你在限时考试中的时间管理能力如何？',
                    'question_type': 'single_select',
                    'survey_type': 'ability',
                    'dimension': '处理速度',
                    'options': [
                        {'value': 'A', 'label': '总能提前完成且有检查时间', 'score': 5},
                        {'value': 'B', 'label': '通常能按时完成', 'score': 4},
                        {'value': 'C', 'label': '刚好能完成或略有不足', 'score': 3},
                        {'value': 'D', 'label': '经常来不及做完', 'score': 2},
                        {'value': 'E', 'label': '总是有大量题目做不完', 'score': 1}
                    ],
                    'order': 16, 'is_global': True
                },
            ]
            for dq in default_questions:
                SurveyQuestion.objects.create(**dq)
            survey_question_qs = SurveyQuestion.objects.filter(
                survey_type='ability'
            ).order_by('order')
        survey_questions: list[SurveyQuestion] = list(survey_question_qs)
        
        return success_response(
            data={
                'assessment_id': ABILITY_ASSESSMENT_FIXED_ID,
                'title': '学习能力评估',
                'questions': [
                    {
                        'question_id': q.id,
                        'content': q.text,
                        'options': q.options,
                        'type': q.question_type,
                        'dimension': q.dimension
                    }
                    for q in survey_questions
                ]
            }
        )
    
    questions: list[Question] = list(assessment.questions.all())
    
    return success_response(
        data={
            'assessment_id': assessment.id,
            'title': assessment.title,
            'questions': [
                {
                    'question_id': q.id,
                    'content': q.content,
                    'options': q.options,
                    'type': q.question_type
                }
                for q in questions
            ]
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudent])
def submit_ability_assessment(request):
    """
    提交学习能力评估测评答案
    POST /api/student/assessments/initial/ability
    
    支持两种模式：
    1. 基于Assessment的评测（需要course_id）
    2. 基于SurveyQuestion的全局能力问卷
    """
    course_id = request.data.get('course_id')
    answers = request.data.get('answers', [])

    if not answers:
        return error_response(msg='缺少答案数据')

    user = _get_authenticated_user(request)

    if isinstance(answers, dict):
        answer_dict = {str(k): v for k, v in answers.items()}
    else:
        answer_dict = {str(a['question_id']): a['answer'] for a in answers}

    assessment = None
    if course_id:
        assessment = Assessment.objects.filter(
            course_id=course_id,
            assessment_type='ability',
            is_active=True
        ).first()

    dimension_scores = {}

    if assessment:
        questions = assessment.questions.all()
        total_score = 0
        total_possible = 0

        for q in questions:
            q_id = str(q.id)
            student_answer = answer_dict.get(q_id)
            correct_answer = q.answer.get('answer', q.answer) if isinstance(q.answer, dict) else q.answer
            total_possible += float(q.score)

            if q.question_type in ['single_choice', 'true_false']:
                if student_answer == correct_answer:
                    total_score += float(q.score)
            elif q.question_type == 'multiple_choice':
                correct_set = _answer_tokens(correct_answer, q.question_type)
                student_set = _answer_tokens(student_answer, q.question_type)
                if correct_set == student_set:
                    total_score += float(q.score)

        score_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
    else:
        total_score = 0
        total_possible = 0

        for q_id_str, answer_val in answer_dict.items():
            try:
                sq = SurveyQuestion.objects.get(id=int(q_id_str))
            except (SurveyQuestion.DoesNotExist, ValueError):
                continue

            score = 3
            for opt in _normalize_options(sq.options, sq.question_type):
                if opt.get('value') == answer_val:
                    score = opt.get('score', 3)
                    break

            total_score += score
            total_possible += 5
            dim = sq.dimension or '综合'
            if dim not in dimension_scores:
                dimension_scores[dim] = {'total': 0, 'max': 0}
            dimension_scores[dim]['total'] += score
            dimension_scores[dim]['max'] += 5

        score_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0

    if dimension_scores:
        ability_analysis = {}
        for dim, ds in dimension_scores.items():
            ability_analysis[dim] = round(ds['total'] / ds['max'] * 100, 1) if ds['max'] > 0 else 0
    else:
        ability_analysis = {}

    with transaction.atomic():
        if course_id:
            AbilityScore.objects.update_or_create(
                user=user,
                course_id=course_id,
                defaults={'scores': ability_analysis}
            )
        else:
            from courses.models import Enrollment

            enrollment = Enrollment.objects.filter(user=user).first()
            resolved_course_id = None

            if enrollment and enrollment.class_obj:
                class_courses = enrollment.class_obj.class_courses.filter(is_active=True)
                if class_courses.exists():
                    first_class_course = class_courses.first()
                    if first_class_course is not None:
                        resolved_course_id = first_class_course.course_id

            if resolved_course_id:
                AbilityScore.objects.update_or_create(
                    user=user,
                    course_id=resolved_course_id,
                    defaults={'scores': ability_analysis}
                )
                course_id = resolved_course_id

        if assessment:
            AssessmentResult.objects.update_or_create(
                user=user,
                assessment=assessment,
                defaults={
                    'course_id': course_id,
                    'answers': answer_dict,
                    'score': total_score,
                    'result_data': {'ability_analysis': ability_analysis}
                }
            )

        if course_id:
            status, _ = AssessmentStatus.objects.get_or_create(
                user=user,
                course_id=course_id
            )
            status.ability_done = True
            status.save()

    return success_response(
        data={
            'score': round(score_percentage, 1),
            'ability_analysis': ability_analysis,
            'completed': True
        },
        msg='测评提交成功'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_habit_survey(request):
    """
    获取学习习惯问卷题目
    GET /api/assessments/initial/habit
    """
    course_id = request.query_params.get('course_id')

    habit_question_qs = (
        SurveyQuestion.objects.filter(survey_type='habit', is_global=True)
        | SurveyQuestion.objects.filter(survey_type='habit', course_id=course_id)
    ).order_by('order')

    if not habit_question_qs.exists():
        default_questions = [
            {
                'text': '你更喜欢通过哪种形式获取新知识？',
                'question_type': 'single_select',
                'options': [
                    {'value': 'video', 'label': '观看教学视频'},
                    {'value': 'document', 'label': '阅读文字资料'},
                    {'value': 'exercise', 'label': '通过练习题实践'},
                    {'value': 'mixed', 'label': '多种形式混合学习'}
                ],
                'order': 1
            },
            {
                'text': '通常哪段时间你的学习效率最高？',
                'question_type': 'single_select',
                'options': [
                    {'value': 'morning', 'label': '早上（6:00-12:00）'},
                    {'value': 'afternoon', 'label': '下午（12:00-18:00）'},
                    {'value': 'evening', 'label': '晚上（18:00-22:00）'},
                    {'value': 'night', 'label': '深夜（22:00以后）'}
                ],
                'order': 2
            },
            {
                'text': '你希望的学习节奏是怎样的？',
                'question_type': 'single_select',
                'options': [
                    {'value': 'fast', 'label': '快节奏：快速推进，挑战高难度'},
                    {'value': 'moderate', 'label': '正常节奏：稳步推进'},
                    {'value': 'slow', 'label': '慢节奏：仔细理解每个知识点'}
                ],
                'order': 3
            },
            {
                'text': '你每天计划花多少时间学习这门课程？',
                'question_type': 'single_select',
                'options': [
                    {'value': '30', 'label': '约30分钟'},
                    {'value': '60', 'label': '约1小时'},
                    {'value': '90', 'label': '约1.5小时'},
                    {'value': '120', 'label': '2小时以上'}
                ],
                'order': 4
            },
            {
                'text': '你希望每周学习几天？',
                'question_type': 'single_select',
                'options': [
                    {'value': '3', 'label': '3天'},
                    {'value': '5', 'label': '5天'},
                    {'value': '7', 'label': '每天都学'}
                ],
                'order': 5
            },
            {
                'text': '你倾向于哪种复习频率？',
                'question_type': 'single_select',
                'options': [
                    {'value': 'daily', 'label': '每天复习当天内容'},
                    {'value': 'weekly', 'label': '每周末集中复习'},
                    {'value': 'before_exam', 'label': '考前集中复习'},
                    {'value': 'spaced', 'label': '按记忆曲线间隔复习'}
                ],
                'order': 6
            },
            {
                'text': '你的学习风格更偏向哪种？',
                'question_type': 'single_select',
                'options': [
                    {'value': 'visual', 'label': '视觉型：喜欢图表、思维导图'},
                    {'value': 'auditory', 'label': '听觉型：喜欢听讲解'},
                    {'value': 'reading', 'label': '阅读型：喜欢查阅文本资料'},
                    {'value': 'kinesthetic', 'label': '动手型：喜欢实验和实操'}
                ],
                'order': 7
            },
            {
                'text': '你喜欢接受有挑战性的学习任务吗？',
                'question_type': 'single_select',
                'options': [
                    {'value': 'yes', 'label': '喜欢，越有挑战越有动力'},
                    {'value': 'moderate', 'label': '适度挑战，太难会焦虑'},
                    {'value': 'no', 'label': '不太喜欢，更愿循序渐进'}
                ],
                'order': 8
            },
            {
                'text': '遇到学习困难时，你更倾向于怎么做？',
                'question_type': 'single_select',
                'options': [
                    {'value': 'self', 'label': '自己查资料解决'},
                    {'value': 'ai', 'label': '使用AI工具辅助'},
                    {'value': 'peer', 'label': '与同学讨论'},
                    {'value': 'teacher', 'label': '向老师请教'}
                ],
                'order': 9
            },
        ]
        for dq in default_questions:
            SurveyQuestion.objects.create(**dq, survey_type='habit', is_global=True)
        habit_question_qs = SurveyQuestion.objects.filter(survey_type='habit', is_global=True)

    questions: list[SurveyQuestion] = list(habit_question_qs)

    return success_response(
        data={
            'survey_id': HABIT_SURVEY_FIXED_ID,
            'title': '学习习惯调查问卷',
            'questions': [
                {
                    'question_id': q.id,
                    'text': q.text,
                    'options': q.options,
                    'type': q.question_type
                }
                for q in questions
            ]
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudent])
def submit_habit_survey(request):
    """
    提交学习习惯问卷答案
    POST /api/student/assessments/initial/habit
    
    注意：仅学生可以提交问卷
    """
    course_id = request.data.get('course_id')
    responses = request.data.get('responses', [])

    if not responses:
        return error_response(msg='缺少问卷回答')

    user = _get_authenticated_user(request)

    try:
        if isinstance(responses, dict):
            response_list = [{'question_id': k, 'answer': v} for k, v in responses.items()]
        else:
            response_list = responses

        field_map = {}
        extra = {}

        for resp in response_list:
            q_id = resp.get('question_id')
            answer = resp.get('answer')

            try:
                question = SurveyQuestion.objects.get(id=q_id)
            except SurveyQuestion.DoesNotExist:
                continue

            text = str(question.text or '')
            answer_text = str(answer or '')

            if '形式' in text or '获取新知识' in text:
                field_map['preferred_resource'] = answer
            elif '效率最高' in text or '哪段时间' in text:
                field_map['preferred_study_time'] = answer
            elif '学习节奏' in text:
                field_map['study_pace'] = answer
            elif '花多少时间' in text or ('每天' in text and '时间' in text):
                field_map['daily_goal_minutes'] = int(answer_text) if answer_text.isdigit() else 60
            elif '每周' in text and '几天' in text:
                field_map['weekly_goal_days'] = int(answer_text) if answer_text.isdigit() else 5
            elif '复习频率' in text or '复习' in text:
                field_map['review_frequency'] = answer
            elif '学习风格' in text:
                field_map['learning_style'] = answer
            elif '挑战' in text:
                field_map['accept_challenge'] = (answer in ('yes', 'moderate'))
            elif '困难' in text:
                extra['difficulty_strategy'] = answer
            else:
                extra[f'q_{q_id}'] = answer

        all_prefs = {**field_map, **extra}

        with transaction.atomic():
            HabitPreference.objects.update_or_create(
                user=user,
                defaults={
                    'preferred_resource': field_map.get('preferred_resource', 'video'),
                    'preferred_study_time': field_map.get('preferred_study_time', 'evening'),
                    'study_pace': field_map.get('study_pace', 'moderate'),
                    'study_duration': {'30': 'short', '60': 'medium'}.get(
                        str(field_map.get('daily_goal_minutes', 60)), 'long'
                    ),
                    'review_frequency': field_map.get('review_frequency', 'weekly'),
                    'learning_style': field_map.get('learning_style', 'visual'),
                    'accept_challenge': field_map.get('accept_challenge', True),
                    'daily_goal_minutes': field_map.get('daily_goal_minutes', 60),
                    'weekly_goal_days': field_map.get('weekly_goal_days', 5),
                    'preferences': all_prefs,
                }
            )

            if course_id:
                status, _ = AssessmentStatus.objects.get_or_create(
                    user=user,
                    course_id=course_id
                )
                status.habit_done = True
                status.save()
            else:
                AssessmentStatus.objects.filter(user=user).update(habit_done=True)
                from courses.models import Enrollment

                enrolled_course_ids = set(
                    Enrollment.objects.filter(user=user)
                    .values_list('class_obj__class_courses__course_id', flat=True)
                )
                existing_ids = set(
                    AssessmentStatus.objects.filter(user=user)
                    .values_list('course_id', flat=True)
                )

                for cid in enrolled_course_ids - existing_ids:
                    if cid:
                        AssessmentStatus.objects.create(user=user, course_id=cid, habit_done=True)

        return success_response(
            data={
                'preferences': all_prefs,
                'completed': True
            },
            msg='问卷提交成功'
        )
    except Exception as e:
        logger.exception('习惯问卷提交失败: %s', e)
        return error_response(msg=f'问卷提交失败: {str(e)}', code=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessment_status(request):
    """
    获取用户的初始评测完成状态
    GET /api/assessments/status
    
    业务规则：
    - 新注册学生用户需要先完成能力评测和习惯问卷（全局，不绑定课程）
    - 加入新课程后需要完成该课程的知识评测
    - 知识评测完成后生成该课程的学习者画像
    
    返回：
    - global_assessment_done: 全局评测（能力+习惯）是否完成
    - ability_done: 能力评测是否完成
    - habit_done: 习惯问卷是否完成  
    - courses: 各课程的知识评测状态
    """
    user = _get_authenticated_user(request)
    course_id = request.query_params.get('course_id')

    has_ability = AbilityScore.objects.filter(user=user).exists()
    has_habit = AssessmentStatus.objects.filter(user=user, habit_done=True).exists()

    result: dict[str, object] = {
        'user_id': user.id,
        'global_assessment_done': has_ability and has_habit,
        'ability_done': has_ability,
        'ability_completed': has_ability,
        'habit_done': has_habit,
        'habit_completed': has_habit,
        'knowledge_done': False,
        'knowledge_completed': False,
        'courses': [],
        'next_step': None,
    }

    if not has_ability:
        result['next_step'] = 'ability'
        result['next_step_msg'] = '请先完成学习能力评测'
    elif not has_habit:
        result['next_step'] = 'habit'
        result['next_step_msg'] = '请完成学习偏好问卷'

    if course_id:
        status = AssessmentStatus.objects.filter(
            user=user,
            course_id=course_id
        ).first()
        knowledge_done = status.knowledge_done if status else False

        from knowledge.models import ProfileSummary

        profile_exists = ProfileSummary.objects.filter(
            user=user, course_id=course_id
        ).exists()

        course_status = {
            'course_id': int(course_id),
            'knowledge_done': knowledge_done,
            'profile_generated': profile_exists
        }
        result['courses'].append(course_status)
        result['knowledge_done'] = knowledge_done
        result['knowledge_completed'] = knowledge_done

        if result['global_assessment_done'] and not knowledge_done:
            result['next_step'] = 'knowledge'
            result['next_step_msg'] = '请完成本课程的知识评测'
        elif result['global_assessment_done'] and knowledge_done and not profile_exists:
            result['next_step'] = 'generate_profile'
            result['next_step_msg'] = '正在生成学习者画像...'
    else:
        statuses = AssessmentStatus.objects.filter(user=user)
        from knowledge.models import ProfileSummary

        for status in statuses:
            profile_exists = ProfileSummary.objects.filter(
                user=user, course_id=status.course_id
            ).exists()
            result['courses'].append({
                'course_id': status.course_id,
                'knowledge_done': status.knowledge_done,
                'profile_generated': profile_exists
            })
        if statuses.exists():
            result['knowledge_done'] = all(s.knowledge_done for s in statuses)
            result['knowledge_completed'] = result['knowledge_done']

    return success_response(data=result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_course_profile(request):
    """
    为指定课程生成学习者画像
    POST /api/assessments/profile/generate
    
    请求参数：
    - course_id: 课程ID（必填）
    
    说明：
    在学生完成初始评测（能力评测+习惯问卷+知识评测）后调用，
    为该课程生成独立的学习者画像。
    """
    user = _get_authenticated_user(request)
    course_id = request.data.get('course_id')

    if not course_id:
        return error_response(msg='缺少课程ID')

    from courses.models import Course

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)

    has_ability = AbilityScore.objects.filter(user=user).exists()
    has_habit = AssessmentStatus.objects.filter(user=user, habit_done=True).exists()

    if not has_ability or not has_habit:
        return error_response(
            msg='请先完成学习能力评测和学习偏好问卷',
        )

    from users.services import get_learner_profile_service

    profile_service = get_learner_profile_service(user)
    result = profile_service.generate_profile_for_course(course_id)

    if result.get('success'):
        return success_response(
            data={
                'course_id': course_id,
                'course_name': course.name,
                'summary': result.get('summary', ''),
                'weakness': result.get('weakness', ''),
                'suggestion': result.get('suggestion', '')
            },
            msg='学习者画像生成成功'
        )
    else:
        return error_response(
            msg=f"画像生成失败: {result.get('error', '未知错误')}",
            code=500
        )
