"""
AI服务模块 - 视图

提供AI大模型服务相关的API端点
并承载画像分析、路径规划、学习建议等能力。
"""
from typing import cast
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from common.responses import success_response, error_response
from common.utils import check_answer, extract_answer_value
from common.logging_utils import build_log_message
from common.permissions import IsTeacherOrAdmin
from users.models import User, HabitPreference
from knowledge.models import KnowledgeMastery, KnowledgePoint, Resource, ProfileSummary
from courses.models import Course
from assessments.models import AbilityScore
from exams.models import Exam, ExamSubmission
from assessments.models import AssessmentStatus
from learning.path_rules import apply_prerequisite_caps, partition_points_for_path
from .models import LLMCallLog
from .services.llm_service import LLMService
from platform_ai.rag import student_learning_rag
import logging

logger = logging.getLogger(__name__)

llm_service = LLMService()


def _build_user_learning_context(user, course_id, include_study_pace=False):
    """统一收集能力评测与学习偏好上下文。"""
    ability = AbilityScore.objects.filter(user=user, course_id=course_id).first()
    ability_data = ability.scores if ability else None

    habit = HabitPreference.objects.filter(user=user).first()
    habit_data = None
    if habit:
        habit_data = {
            'preferred_resource': habit.preferred_resource,
            'preferred_study_time': habit.preferred_study_time,
        }
        if include_study_pace:
            habit_data['study_pace'] = getattr(habit, 'study_pace', 'moderate')

    return ability_data, habit_data


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_profile_analysis(request):
    """
    AI画像诊断。
    POST /api/ai/profile-analysis

    结合知识评测、能力评测与画像缓存结果返回 AI 分析。
    """
    course_id = request.data.get('course_id')
    refresh = request.data.get('refresh', False)

    if not course_id:
        return error_response(msg='缂哄皯璇剧▼ID', code=400)

    if not Course.objects.filter(id=course_id).exists():
        return error_response(msg='课程不存在', code=400)

    user = cast(User, request.user)

    # 评测门控：至少完成知识评测后才能获取 AI 画像分析。
    has_ability = AbilityScore.objects.filter(user=user).exists()
    assessment_status = AssessmentStatus.objects.filter(user=user, course_id=course_id).first()
    knowledge_done = assessment_status.knowledge_done if assessment_status else False
    if not has_ability or not knowledge_done:
        missing = []
        if not has_ability:
            missing.append('鑳藉姏璇勬祴')
        if not knowledge_done:
            missing.append('鐭ヨ瘑璇勬祴')
        return error_response(
            msg=f"请先完成{'和'.join(missing)}后再获取AI分析",
            code=400,
            data={'missing': missing, 'need_assessment': True}
        )

    # 检查是否已有画像，非刷新模式优先直接返回缓存结果。
    existing = ProfileSummary.objects.filter(
        user=user,
        course_id=course_id
    ).first()

    if existing and not refresh:
        return success_response(
            data={
                'summary': existing.summary,
                'weakness': existing.weakness,
                'suggestion': existing.suggestion,
                'generated_at': existing.generated_at.isoformat()
            }
        )

    from users.services import get_learner_profile_service
    profile_service = get_learner_profile_service(user)
    result = profile_service.generate_profile_for_course(course_id, force_refresh=refresh)

    if result.get('success'):
        return success_response(
            data={
                'summary': result.get('summary', ''),
                'weakness': result.get('weakness', ''),
                'suggestion': result.get('suggestion', ''),
                'strength': result.get('strength', []),
                'kt_enhanced': result.get('kt_enhanced', False),
                'generated_at': ProfileSummary.objects.filter(
                    user=user, course_id=course_id
                ).values_list('generated_at', flat=True).first()
            },
            msg='AI鐢诲儚鍒嗘瀽瀹屾垚'
        )

    return error_response(msg=f"画像分析失败: {result.get('error', '未知错误')}", code=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_path_planning(request):
    """
    AI路径规划
    POST /api/ai/path-planning
    
    集成KT服务 + LLM服务，结合能力评测和习惯问卷结果
    """
    course_id = request.data.get('course_id')
    target = request.data.get('target', '')
    constraints = request.data.get('constraints', {})

    if not course_id:
        return error_response(msg='缂哄皯璇剧▼ID', code=400)

    user = cast(User, request.user)

    mastery_records = KnowledgeMastery.objects.filter(
        user=user,
        course_id=course_id
    ).select_related('knowledge_point')

    mastery_data = [
        {
            'point_name': m.knowledge_point.name,
            'mastery_rate': float(m.mastery_rate)
        }
        for m in mastery_records
    ]

    ability_data, habit_data = _build_user_learning_context(user, course_id)

    enhanced_constraints = dict(constraints or {})
    if ability_data:
        enhanced_constraints['ability_scores'] = ability_data
    if habit_data:
        enhanced_constraints['learning_preferences'] = habit_data

    pending_points = [
        record.knowledge_point
        for record in sorted(mastery_records, key=lambda item: float(item.mastery_rate))
        if record.knowledge_point is not None
    ]
    if pending_points:
        rag_context = student_learning_rag.build_path_context(
            course_id=int(course_id),
            target=target or 'improve mastery',
            pending_points=pending_points,
        )
        enhanced_constraints['retrieved_context'] = rag_context['retrieved_context']
        enhanced_constraints['retrieved_sources'] = rag_context['retrieved_sources']

    try:
        response = llm_service.plan_learning_path(mastery_data, target, enhanced_constraints)
    except Exception as e:
        logger.exception('AI璺緞瑙勫垝澶辫触锛屼娇鐢ㄩ檷绾х瓥鐣? %s', e)
        ordered = sorted(mastery_data, key=lambda x: x.get('mastery_rate', 0))
        response = {
            'reason': '已按掌握度从低到高生成学习路径（降级模式）。',
            'nodes': [
                {
                    'title': item.get('point_name'),
                    'priority': 'high' if item.get('mastery_rate', 0) < 0.6 else 'normal'
                }
                for item in ordered
            ]
        }

    LLMCallLog.objects.create(
        user=user,
        call_type='path_planning',
        input_summary=(
            f"target: {target}, points: {len(mastery_data)}, ability: {bool(ability_data)}, "
            f"habit: {bool(habit_data)}, retrieved: {len(enhanced_constraints.get('retrieved_sources', []))}"
        ),
        output_summary=str(response)[:500],
        is_success=True
    )

    return success_response(
        data={
            'reason': response.get('reason', ''),
            'suggested_nodes': response.get('nodes', [])
        },
        msg='路径规划完成'
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_resource_reason(request):
    """
    AI 资源推荐理由生成。
    POST /api/ai/resource-reason

    学生可以自己调用（student_id可省略，默认为当前用户）
    """
    resource_id = request.data.get('resource_id')
    student_id = request.data.get('student_id') or request.user.id
    point_id = request.data.get('point_id')

    if not resource_id:
        return error_response(msg='缂哄皯resource_id鍙傛暟', code=400)

    try:
        resource = Resource.objects.get(id=resource_id)
        student = User.objects.get(id=student_id)
    except (Resource.DoesNotExist, User.DoesNotExist):
        return error_response(msg='资源或学生不存在', code=404)

    mastery = None
    point_name = None
    if point_id:
        mastery_obj = KnowledgeMastery.objects.filter(
            user=student,
            knowledge_point_id=point_id
        ).select_related('knowledge_point').first()
        if mastery_obj:
            mastery = float(mastery_obj.mastery_rate)
            point_name = mastery_obj.knowledge_point.name

    resource_info = {
        'title': resource.title,
        'type': resource.get_resource_type_display()
    }
    response = llm_service.generate_resource_reason(resource_info, mastery, point_name)

    LLMCallLog.objects.create(
        user=request.user,
        call_type='resource_reason',
        input_summary=f"resource: {resource_id}, student: {student_id}",
        output_summary=str(response)[:500],
        is_success=True
    )

    return success_response(
        data={
            'resource_id': resource_id,
            'student_id': student_id,
            'reason': response.get('reason', '璇ヨ祫婧愪笌瀛︾敓褰撳墠瀛︿範杩涘害鍖归厤'),
            'relevance_score': response.get('relevance_score', 0.8)
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def ai_feedback_report(request):
    """
    AI反馈报告生成
    POST /api/ai/feedback-report
    
    使用LangChain生成考试反馈报告
    """
    exam_id = request.data.get('exam_id')
    student_id = request.data.get('student_id')
    include_next_tasks = request.data.get('include_next_tasks', True)

    if not exam_id or not student_id:
        return error_response(msg='缺少必要参数', code=400)

    try:
        exam = Exam.objects.get(id=exam_id)
        student = User.objects.get(id=student_id)
        submission = ExamSubmission.objects.get(exam=exam, user=student)
    except (Exam.DoesNotExist, User.DoesNotExist, ExamSubmission.DoesNotExist):
        return error_response(msg='作业、学生或提交记录不存在', code=404)

    from exams.models import ExamQuestion
    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related(
        'question'
    ).prefetch_related('question__knowledge_points')

    mistakes = []
    answer_history_records = []
    for eq in exam_questions:
        q = eq.question
        student_answer = submission.answers.get(str(q.id)) if submission.answers else None
        correct_answer = extract_answer_value(q.answer)
        is_correct = check_answer(q.question_type, student_answer, q.answer)

        if not is_correct:
            mistakes.append({
                'question_id': q.id,
                'correct_answer': correct_answer,
                'student_answer': student_answer,
                'analysis': q.analysis or ''
            })
        for point in q.knowledge_points.all():
            answer_history_records.append({
                'question_id': q.id,
                'knowledge_point_id': point.id,
                'correct': 1 if is_correct else 0
            })

    kt_analysis = {}
    try:
        from .services.kt_service import kt_service as _kt
        if answer_history_records:
            kt_result = _kt.predict_mastery(
                user_id=student.id,
                course_id=exam.course_id,
                answer_history=answer_history_records
            )
            kt_analysis = {
                'predictions': kt_result.get('predictions', {}),
                'confidence': kt_result.get('confidence', 0)
            }
    except Exception as e:
        logger.warning(build_log_message('kt.teacher_feedback.fail', exam_id=exam_id, student_id=student_id, error=e))

    ability = AbilityScore.objects.filter(user=student, course_id=exam.course_id).first()
    ability_data = ability.scores if ability else None
    habit_data = None
    try:
        habit = student.habit_preference
        habit_data = {'preferred_resource': habit.preferred_resource, 'preferred_study_time': habit.preferred_study_time}
    except HabitPreference.DoesNotExist:
        pass

    exam_info = {
        'title': exam.title,
        'type': exam.exam_type if hasattr(exam, 'exam_type') else '课程作业'
    }
    response = llm_service.generate_feedback_report(
        exam_info,
        float(submission.score),
        float(exam.total_score),
        mistakes
    )

    LLMCallLog.objects.create(
        user=request.user,
        call_type='feedback_report',
        input_summary=f"exam: {exam_id}, student: {student_id}, mistakes: {len(mistakes)}, kt: {bool(kt_analysis)}",
        output_summary=str(response)[:500],
        is_success=True
    )

    result = {
        'exam_id': exam_id,
        'student_id': student_id,
        'analysis': response.get('analysis', ''),
        'knowledge_gaps': response.get('knowledge_gaps', []),
        'recommendations': response.get('recommendations', []),
        'encouragement': response.get('encouragement', ''),
        'kt_analysis': kt_analysis,
        'ability_context': ability_data,
        'habit_context': habit_data
    }

    if include_next_tasks:
        result['next_tasks'] = response.get('next_tasks', [])

    return success_response(data=result, msg='反馈报告生成完成')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_learning_advice(request):
    """
    AI学习建议
    POST /api/ai/learning-advice
    
    缁撳悎KT棰勬祴銆佽兘鍔涜瘎娴嬬粨鏋滃拰涔犳儻闂嵎鐢熸垚涓€у寲瀛︿範寤鸿
    """
    course_id = request.data.get('course_id')

    if not course_id:
        return error_response(msg='缂哄皯璇剧▼ID', code=400)

    user = cast(User, request.user)

    mastery_records = KnowledgeMastery.objects.filter(
        user=user, course_id=course_id
    ).select_related('knowledge_point')

    mastery_data = [
        {
            'point_name': m.knowledge_point.name,
            'point_id': m.knowledge_point_id,
            'mastery_rate': float(m.mastery_rate)
        }
        for m in mastery_records
    ]

    ability_data, habit_data = _build_user_learning_context(user, course_id)

    kt_insight = None
    try:
        from .services.kt_service import kt_service as _kt
        from assessments.models import AnswerHistory
        answer_records = AnswerHistory.objects.filter(
            user=user, course_id=course_id
        ).order_by('answered_at').values('question_id', 'knowledge_point_id', 'is_correct')
        if answer_records.exists():
            history = [
                {'question_id': r['question_id'], 'knowledge_point_id': r['knowledge_point_id'], 'correct': 1 if r['is_correct'] else 0}
                for r in answer_records if r['knowledge_point_id']
            ]
            kt_result = _kt.predict_mastery(user_id=user.id, course_id=course_id, answer_history=history)
            kt_insight = llm_service.analyze_knowledge_tracing_result(
                kt_result=kt_result,
                answer_history=history,
                course_name=str(Course.objects.filter(id=course_id).values_list('name', flat=True).first() or '')
            )
    except Exception as e:
        logger.warning(build_log_message('kt.learning_advice.fail', user_id=request.user.id, course_id=course_id, error=e))

    try:
        profile_result = llm_service.analyze_profile(mastery_data, ability_data, habit_data)
    except Exception as e:
        logger.warning(build_log_message('llm.learning_advice.fail', user_id=request.user.id, course_id=course_id, error=e))
        profile_result = {}

    advice = {
        'summary': profile_result.get('summary', ''),
        'weakness': profile_result.get('weakness', []),
        'strength': profile_result.get('strength', []),
        'suggestion': profile_result.get('suggestion', ''),
        'kt_insight': kt_insight,
        'ability_scores': ability_data,
        'habit_preferences': habit_data
    }

    LLMCallLog.objects.create(
        user=user,
        call_type='other',
        input_summary=f"learning_advice: course={course_id}, mastery={len(mastery_data)}",
        output_summary=str(advice)[:500],
        is_success=True
    )

    return success_response(data=advice, msg='AI学习建议生成完成')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_refresh_profile(request):
    """
    主动刷新学习画像。
    POST /api/ai/refresh-profile
    """
    course_id = request.data.get('course_id')
    if not course_id:
        return error_response(msg='缂哄皯璇剧▼ID', code=400)

    if not Course.objects.filter(id=course_id).exists():
        return error_response(msg='课程不存在', code=400)

    from users.services import get_learner_profile_service
    profile_service = get_learner_profile_service(cast(User, request.user))
    result = profile_service.generate_profile_for_course(course_id, force_refresh=True)

    if result.get('success'):
        return success_response(data={
            'summary': result.get('summary', ''),
            'weakness': result.get('weakness', ''),
            'suggestion': result.get('suggestion', ''),
            'strength': result.get('strength', []),
            'kt_enhanced': result.get('kt_enhanced', False)
        }, msg='画像已刷新')

    return error_response(msg=f"画像刷新失败: {result.get('error', '未知错误')}", code=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_refresh_learning_path(request):
    """
    涓诲姩鍒锋柊瀛︿範璺緞锛堜繚鐣欏凡瀹屾垚鑺傜偣锛孠T+鐢诲儚+LLM澧為噺閲嶅缓锛?
    POST /api/ai/refresh-learning-path

    娴佺▼锛?
    1. 璋冪敤KT鏈嶅姟鏇存柊鎺屾彙搴?
    2. 鏀堕泦瀛︿範鐢诲儚銆佽兘鍔涜瘎娴嬨€佷範鎯亸濂?
    3. 淇濈暀宸插畬鎴?璺宠繃鑺傜偣锛屽彧鍒犻櫎locked鑺傜偣
    4. 调用LLM（含画像/KT/已完成信息）规划剩余路径
    5. 鎸塋LM鎺掑簭+鎺屾彙搴﹀垱寤烘柊鑺傜偣锛堝涔?娴嬭瘎锛?
    6. 杩斿洖瀹屾暣璺緞 + 鎺屾彙搴?+ 鐢诲儚鎽樿
    """
    course_id = request.data.get('course_id')
    if not course_id:
        return error_response(msg='缂哄皯璇剧▼ID', code=400)

    user = request.user

    from learning.models import LearningPath, PathNode
    from courses.models import Course
    from common.config import AppConfig
    from assessments.models import AnswerHistory
    from knowledge.models import ProfileSummary

    path = LearningPath.objects.filter(user=user, course_id=course_id).first()
    if not path:
        return error_response(msg='学习路径不存在，请先完成初始评测', code=404)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)

    # ========== 1. 调用 KT 服务刷新掌握度 ==========
    kt_predictions = {}
    kt_answer_count = 0
    try:
        from .services.kt_service import kt_service as _kt
        answer_records = AnswerHistory.objects.filter(
            user=user, course_id=course_id
        ).order_by('answered_at').values('question_id', 'knowledge_point_id', 'is_correct')
        if answer_records.exists():
            history = [
                {'question_id': r['question_id'], 'knowledge_point_id': r['knowledge_point_id'], 'correct': 1 if r['is_correct'] else 0}
                for r in answer_records if r['knowledge_point_id']
            ]
            kt_answer_count = len(history)
            kt_result = _kt.predict_mastery(user_id=user.id, course_id=course_id, answer_history=history)
            kt_predictions = kt_result.get('predictions') or {}
            logger.info(
                'KT 服务调用成功(路径刷新): user=%s, answer_history=%s, predictions=%s',
                user.id,
                kt_answer_count,
                len(kt_predictions),
            )
            for kp_id, rate in kt_predictions.items():
                try:
                    KnowledgeMastery.objects.update_or_create(
                        user=user, course_id=course_id, knowledge_point_id=kp_id,
                        defaults={'mastery_rate': float(rate)}
                    )
                except Exception as e:
                    logger.warning('KT 掌握度更新失败: kp_id=%s, %s', kp_id, e)
    except Exception as e:
        logger.warning(f"学习路径刷新时KT更新失败: {e}")

    # ========== 2. 收集学习画像数据 ==========
    mastery_dict = {
        m.knowledge_point_id: float(m.mastery_rate)
        for m in KnowledgeMastery.objects.filter(user=user, course_id=course_id)
    }
    mastery_dict = apply_prerequisite_caps(mastery_dict, int(course_id), buffer=0.05)
    for kp_id, mastery_rate in mastery_dict.items():
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course_id=course_id,
            knowledge_point_id=kp_id,
            defaults={'mastery_rate': mastery_rate}
        )

    ability_data, habit_data = _build_user_learning_context(user, course_id, include_study_pace=True)

    profile_summary = ProfileSummary.objects.filter(
        user=user, course_id=course_id
    ).order_by('-generated_at').first()
    profile_text = ''
    if profile_summary:
        profile_text = (
            f"总体评价：{profile_summary.summary or '暂无'}\n"
            f"薄弱点：{profile_summary.weakness or '暂无'}\n"
            f"建议：{profile_summary.suggestion or '暂无'}"
        )

    # ========== 3. 保留已完成节点和当前上下文，仅重建未来段 ==========
    with transaction.atomic():
        preserved_statuses = ('completed', 'skipped')
        preserved_nodes = list(
            path.nodes.filter(status__in=preserved_statuses)
            .select_related('knowledge_point')
            .order_by('order_index')
        )
        context_node = (
            path.nodes.filter(status__in=('active', 'failed'))
            .select_related('knowledge_point')
            .order_by('order_index')
            .first()
        )
        if context_node and all(node.id != context_node.id for node in preserved_nodes):
            preserved_nodes.append(context_node)
            preserved_nodes.sort(key=lambda item: item.order_index)

        preserved_ids = {node.id for node in preserved_nodes}
        preserved_kp_ids = {n.knowledge_point_id for n in preserved_nodes if n.knowledge_point_id}
        removed_count = path.nodes.exclude(id__in=preserved_ids).count()

        # 收集已保留节点信息，供增量规划参考。
        completed_info = []
        for n in preserved_nodes:
            if n.knowledge_point:
                m_rate = mastery_dict.get(n.knowledge_point_id, 0)
                completed_info.append({
                    'name': n.knowledge_point.name,
                    'status': n.status,
                    'mastery': f'{m_rate*100:.0f}%'
                })

        # 删除未保留节点，仅重建当前节点之后的未来段。
        path.nodes.exclude(id__in=preserved_ids).delete()

        # ========== 4. 获取剩余知识点（含自动完成与待学习） ==========
        auto_completed_points, pending_points, _ = partition_points_for_path(
            int(course_id),
            mastery_dict,
            excluded_point_ids=preserved_kp_ids,
        )

        # ========== 5. 调用 LLM 规划剩余路径（含画像 / KT / 已完成信息） ==========
        max_nodes = AppConfig.max_path_nodes()
        test_interval = AppConfig.path_test_interval()
        remaining_quota = max(0, max_nodes - len(preserved_nodes))

        ai_reason = '已根据 KT 预测和 AI 分析，保留你的学习进度并重新规划了未完成部分。'
        try:
            from ai_services.services.llm_service import LLMService
            llm_svc = LLMService()

            # 构建待规划知识点的掌握度数据。
            remaining_mastery = [
                {'point_name': p.name, 'mastery_rate': float(mastery_dict.get(p.id, 0))}
                for p in pending_points
            ]

            # 构建增量规划约束。
            constraints: dict[str, object] = {
                'refresh_mode': True,
                'completed_nodes': completed_info,
                'completed_count': len(preserved_nodes),
                'remaining_count': len(remaining_mastery),
                'auto_completed_count': len(auto_completed_points),
                'kt_answer_count': kt_answer_count,
                'kt_prediction_count': len(kt_predictions),
            }
            if ability_data:
                constraints['ability_scores'] = ability_data
            if habit_data:
                constraints['learning_preferences'] = habit_data
            if profile_text:
                constraints['learner_profile'] = profile_text
            if pending_points:
                rag_context = student_learning_rag.build_path_context(
                    course_id=int(course_id),
                    target='refresh learning path',
                    pending_points=list(pending_points),
                )
                constraints['retrieved_context'] = rag_context['retrieved_context']
                constraints['retrieved_sources'] = rag_context['retrieved_sources']

            llm_result = llm_svc.plan_learning_path(
                remaining_mastery,
                target='基于当前学习进度，优先弥补薄弱知识点，循序渐进提升整体掌握率',
                constraints=constraints,
                course_name=course.name,
                max_nodes=remaining_quota
            )
            ai_reason = llm_result.get('reason') or ai_reason if isinstance(llm_result, dict) else ai_reason
        except Exception as e:
            logger.warning(build_log_message('llm.path_refresh.sort_fail', user_id=user.id, course_id=course_id, error=e))

        # ========== 6. 批量创建新节点（学习 + 测评） ==========
        max_order = max((n.order_index for n in preserved_nodes), default=-1)
        next_order = max_order + 1

        nodes_to_create = []
        node_resource_map = []
        study_batch = []
        order_idx = next_order

        auto_completed_quota = min(len(auto_completed_points), remaining_quota)
        for point in auto_completed_points[:auto_completed_quota]:
            nodes_to_create.append(PathNode(
                path=path,
                knowledge_point=point,
                title=f'{point.name}巩固',
                goal=f'{point.name} 已达到默认完成标准',
                criterion='掌握度已达到自动完成阈值，且前置知识点已满足要求',
                suggestion='该知识点已自动标记完成，如需复习可直接进入相关资源。',
                status='completed',
                order_index=order_idx,
                node_type='study',
                estimated_minutes=15
            ))
            node_resource_map.append(point)
            order_idx += 1

        pending_quota = max(0, remaining_quota - auto_completed_quota)
        for point in pending_points[:pending_quota]:
            mastery = mastery_dict.get(point.id, 0)
            nodes_to_create.append(PathNode(
                path=path,
                knowledge_point=point,
                title=f'{point.name}' + ('提升' if mastery > 0.5 else '基础'),
                goal=f'掌握{point.name}的核心概念及应用',
                criterion='完成全部学习资源与测验，正确率达到 80% 以上',
                suggestion=f'{"巩固" if mastery > 0.5 else "重点学习"} {point.name} 相关内容。',
                status='locked',
                order_index=order_idx,
                node_type='study',
                estimated_minutes=max(15, min(60, int(30 + (1 - mastery) * 30)))
            ))
            node_resource_map.append(point)
            study_batch.append(point)
            order_idx += 1

            if len(study_batch) >= test_interval:
                kp_name_list = [p.name for p in study_batch]
                if len(kp_name_list) > 3:
                    test_title = f"阶段测试：{'、'.join(kp_name_list[:3])}等{len(kp_name_list)}个知识点"
                else:
                    test_title = f"阶段测试：{'、'.join(kp_name_list)}"
                nodes_to_create.append(PathNode(
                    path=path,
                    knowledge_point=study_batch[-1],
                    title=test_title,
                    goal=f"检验{'、'.join(kp_name_list)}的掌握程度",
                    criterion='正确率达到 80% 视为通过',
                    suggestion='综合运用前几个知识点完成测试题。',
                    status='locked',
                    order_index=order_idx,
                    node_type='test',
                    estimated_minutes=15
                ))
                node_resource_map.append(None)
                study_batch = []
                order_idx += 1

        if nodes_to_create:
            created_nodes = PathNode.objects.bulk_create(nodes_to_create)
            for node, point in zip(created_nodes, node_resource_map):
                if point is not None:
                    resources = point.resources.filter(is_visible=True)[:5]
                    if resources:
                        node.resources.add(*list(resources))

        # 确保至少有一个 active 节点。
        if not path.nodes.filter(status='active').exists():
            first_locked = path.nodes.filter(status='locked').order_by('order_index').first()
            if first_locked:
                first_locked.status = 'active'
                first_locked.save(update_fields=['status'])

        path.is_dynamic = True
        path.ai_reason = ai_reason
        path.save(update_fields=['is_dynamic', 'ai_reason'])

    # ========== 7. 构建响应（含节点列表、掌握度、画像） ==========
    nodes = []
    for node in path.nodes.select_related('knowledge_point').prefetch_related('resources').order_by('order_index'):
        nodes.append({
            'node_id': node.id,
            'title': node.title,
            'goal': node.goal,
            'criterion': node.criterion,
            'status': node.status,
            'suggestion': node.suggestion,
            'node_type': node.node_type,
            'knowledge_point_id': node.knowledge_point_id,
            'knowledge_point_name': node.knowledge_point.name if node.knowledge_point else None,
            'tasks_count': len(node.resources.all()) + (1 if node.exam else 0)
        })

    # 掌握度数据（供前端展示）
    mastery_list = []
    for kp in KnowledgePoint.objects.filter(course_id=course_id, is_published=True).order_by('order'):
        mastery_list.append({
            'point_id': kp.id,
            'point_name': kp.name,
            'mastery_rate': round(mastery_dict.get(kp.id, 0), 4),
        })

    # 画像摘要
    profile_info = None
    if profile_summary:
        profile_info = {
            'summary': profile_summary.summary,
            'weakness': profile_summary.weakness,
            'suggestion': profile_summary.suggestion,
        }

    LLMCallLog.objects.create(
        user=user,
        call_type='path_planning',
        input_summary=f"refresh_path: course={course_id}, preserved={len(preserved_nodes)}, new={len(nodes_to_create)}",
        output_summary=f"total_nodes={len(nodes)}, ai_reason={ai_reason[:60]}",
        is_success=True
    )

    return success_response(
        data={
            'path_id': path.id,
            'nodes': nodes,
            'ai_reason': path.ai_reason,
            'dynamic': path.is_dynamic,
            'preserved_count': len(preserved_nodes),
            'new_count': len(nodes_to_create),
            'change_summary': {
                'preserved_completed': sum(1 for node in preserved_nodes if node.status == 'completed'),
                'preserved_context': 1 if context_node else 0,
                'removed_count': removed_count,
                'auto_completed_count': auto_completed_quota,
                'new_count': len(nodes_to_create),
                'current_node_id': context_node.id if context_node else None,
                'current_node_title': context_node.title if context_node else None,
            },
            'mastery': mastery_list,
            'profile': profile_info,
            'kt_info': {
                'answer_count': kt_answer_count,
                'prediction_count': len(kt_predictions),
            },
        },
        msg='学习路径已刷新'
    )


# ============ 鐭ヨ瘑杩借釜鏈嶅姟 ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def kt_predict(request):
    """
    鐭ヨ瘑杩借釜棰勬祴
    POST /api/ai/kt/predict
    
    使用深度学习知识追踪模型预测学生对各知识点的掌握程度
    """
    from .services.kt_service import kt_service

    course_id = request.data.get('course_id')
    answer_history = request.data.get('answer_history', [])
    knowledge_points = request.data.get('knowledge_points', [])

    if not course_id:
        return error_response(msg='缂哄皯璇剧▼ID', code=400)

    if not answer_history:
        return error_response(msg='缺少答题历史', code=400)

    user = request.user

    result = kt_service.predict_mastery(
        user_id=user.id,
        course_id=course_id,
        answer_history=answer_history,
        knowledge_points=knowledge_points if knowledge_points else None
    )

    return success_response(data=result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kt_model_info(request):
    """
    获取知识追踪模型信息
    GET /api/ai/kt/model-info
    """
    from .services.kt_service import kt_service

    model_info = kt_service.get_model_info()
    return success_response(data=model_info)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def kt_batch_predict(request):
    """
    鎵归噺鐭ヨ瘑杩借釜棰勬祴锛堟暀甯堢锛?
    POST /api/ai/kt/batch-predict
    """
    from .services.kt_service import kt_service

    user_histories = request.data.get('user_histories', [])

    if not user_histories:
        return error_response(msg='缂哄皯鐢ㄦ埛鍘嗗彶鏁版嵁', code=400)

    results = kt_service.batch_predict(user_histories)
    return success_response(data={'results': results})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def kt_recommendations(request):
    """
    鑾峰彇鍩轰簬鐭ヨ瘑杩借釜鐨勫涔犲缓璁?
    POST /api/ai/kt/recommendations
    """
    from .services.kt_service import kt_service

    course_id = request.data.get('course_id')
    predictions = request.data.get('predictions', {})
    threshold = request.data.get('threshold', 0.6)

    if not course_id or not predictions:
        return error_response(msg='缺少必要参数', code=400)

    user = request.user

    recommendations = kt_service.get_learning_recommendations(
        user_id=user.id,
        course_id=course_id,
        mastery_predictions=predictions,
        threshold=threshold
    )

    return success_response(data={'recommendations': recommendations})


# ============ AI 鎵╁睍鏈嶅姟 ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_key_points_reminder(request):
    """
    AI 鍏抽敭鐭ヨ瘑鐐规彁閱?
    POST /api/student/ai/key-points-reminder
    """
    from knowledge.models import KnowledgeMastery

    course_id = request.data.get('course_id')
    if not course_id:
        return error_response(msg='缂哄皯 course_id', code=400)

    weak_points = (
        KnowledgeMastery.objects.filter(
            user=request.user,
            course_id=course_id,
            mastery_rate__lt=0.6,
        )
        .select_related('knowledge_point')
        .order_by('mastery_rate')[:10]
    )

    reminders = [
        {
            'knowledge_point_id': m.knowledge_point_id,
            'name': m.knowledge_point.name if m.knowledge_point else '',
            'mastery_rate': float(m.mastery_rate),
            'suggestion': f'建议重新学习“{m.knowledge_point.name if m.knowledge_point else ""}”，当前掌握度仅 {float(m.mastery_rate) * 100:.0f}%。',
        }
        for m in weak_points
    ]

    return success_response(data={'reminders': reminders})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_time_scheduling(request):
    """
    AI 瀛︿範鏃堕棿瑙勫垝
    POST /api/student/ai/time-scheduling
    """
    from knowledge.models import KnowledgeMastery

    course_id = request.data.get('course_id')
    available_hours = request.data.get('available_hours', 2)

    if not course_id:
        return error_response(msg='缂哄皯 course_id', code=400)

    weak = KnowledgeMastery.objects.filter(
        user=request.user, course_id=course_id, mastery_rate__lt=0.7
    ).select_related('knowledge_point').order_by('mastery_rate')

    total_weight = sum(1 - float(m.mastery_rate) for m in weak) or 1

    schedule = []
    for m in weak[:8]:
        weight = 1 - float(m.mastery_rate)
        hours = round(available_hours * weight / total_weight, 1)
        schedule.append({
            'knowledge_point': m.knowledge_point.name if m.knowledge_point else '',
            'mastery_rate': float(m.mastery_rate),
            'suggested_hours': hours,
        })

    return success_response(data={
        'total_hours': available_hours,
        'schedule': schedule,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_analysis_compare(request):
    """
    瀵规瘮涓嶅悓鏃舵湡鐨?AI 鍒嗘瀽缁撴灉
    GET /api/student/ai/analysis-compare
    """
    from knowledge.models import ProfileSummary

    date1 = request.query_params.get('date1')
    date2 = request.query_params.get('date2')

    if not date1 or not date2:
        return error_response(msg='璇锋彁渚?date1 鍜?date2 鍙傛暟', code=400)

    history = ProfileSummary.objects.filter(user=request.user).order_by('generated_at')

    s1 = history.filter(generated_at__date__lte=date1).last()
    s2 = history.filter(generated_at__date__lte=date2).last()

    return success_response(data={
        'date1': date1,
        'snapshot1': {
            'summary': s1.summary,
            'weakness': s1.weakness,
            'suggestion': s1.suggestion,
            'generated_at': s1.generated_at,
        } if s1 else None,
        'date2': date2,
        'snapshot2': {
            'summary': s2.summary,
            'weakness': s2.weakness,
            'suggestion': s2.suggestion,
            'generated_at': s2.generated_at,
        } if s2 else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """
    AI瀛︿範瀵硅瘽
    POST /api/student/ai/chat
    
    与AI助手进行学习相关对话，支持基于知识点上下文的问答
    """
    message = request.data.get('message', '').strip()
    knowledge_point = request.data.get('knowledge_point', '')
    course_name = request.data.get('course_name', '')
    history = request.data.get('history', [])

    if not message:
        return error_response(msg='请输入问题', code=400)

    if len(message) > 2000:
        return error_response(msg='问题内容过长，请限制在1000字以内', code=400)

    try:
        from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

        llm = getattr(llm_service, '_get_llm')()
        if llm is None:
            return success_response(data={
                'reply': f'关于“{knowledge_point or "这个问题"}”，建议你先结合课程知识图谱和教材资源进行理解，再通过练习验证掌握情况。',
                'mock': True
            })

        context_parts = ['你是自适应学习系统的 AI 学习助手，负责回答学生的学习问题。']
        if course_name:
            context_parts.append(f'当前课程：{course_name}。')
        if knowledge_point:
            context_parts.append(f'当前学习的知识点：{knowledge_point}。')
        context_parts.append(
            '请用通俗易懂的语言回答，适当举例说明。'
            '如果涉及代码，请使用 markdown 代码块格式。'
            '回答要简洁实用，控制在 200 字以内。'
        )

        messages: list[BaseMessage] = [SystemMessage(content=''.join(context_parts))]

        for h in history[-12:]:
            if h.get('role') == 'user':
                messages.append(HumanMessage(content=h['content'][:500]))
            elif h.get('role') == 'assistant':
                messages.append(AIMessage(content=h['content'][:500]))

        messages.append(HumanMessage(content=message))

        response = llm.invoke(messages)

        LLMCallLog.objects.create(
            user=request.user,
            call_type='chat',
            input_summary=message[:200],
            output_summary=response.content[:200] if response.content else '',
            tokens_used=len(message) + len(response.content or ''),
            is_success=True
        )

        return success_response(data={
            'reply': response.content,
            'mock': False
        })
    except Exception as e:
        logger.error(build_log_message('llm.chat.fail', user_id=request.user.id, error=e))
        return success_response(data={
            'reply': '抱歉，AI 助手暂时无法回复。请稍后重试。',
            'error': True
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_node_intro(request):
    """
    AI鐭ヨ瘑鐐逛粙缁?
    POST /api/student/ai/node-intro
    
    涓哄綋鍓嶅涔犺妭鐐圭敓鎴怢LM鐭ヨ瘑鐐逛粙缁?
    """
    point_name = request.data.get('point_name', '').strip()
    course_name = request.data.get('course_name', '')

    if not point_name:
        return error_response(msg='缺少知识点名称', code=400)

    from django.core.cache import cache
    cache_key = f'node_intro:{request.user.id}:{hash(point_name)}'
    cached = cache.get(cache_key)
    if cached:
        return success_response(data=cached)

    try:
        prompt = f"""请为以下知识点生成一个简短的学习介绍。

课程：{course_name or '未指定'}
知识点：{point_name}

请按以下 JSON 格式输出：
{{
    "introduction": "知识点简介（2-3句话，通俗易懂）",
    "key_concepts": ["核心概念1", "核心概念2", "核心概念3"],
    "learning_tips": "学习建议（1-2句话）",
    "difficulty": "easy/medium/hard"
}}"""

        fallback = {
            'introduction': f'{point_name} 是本课程的重要知识点，建议结合课程资源进行理解。',
            'key_concepts': [point_name],
            'learning_tips': '建议先阅读教材，再通过练习巩固。',
            'difficulty': 'medium'
        }

        result = getattr(llm_service, '_call_with_fallback')(
            prompt=prompt,
            call_type='node_intro',
            fallback_response=fallback
        )

        cache.set(cache_key, result, 3600)

        return success_response(data=result)
    except Exception as e:
        logger.error(build_log_message('llm.node_intro.fail', user_id=request.user.id, point_name=point_name, error=e))
        return success_response(data={
            'introduction': f'{point_name} 是本课程的重要知识点，建议结合课程资源进行理解。',
            'key_concepts': [point_name],
            'learning_tips': '建议先阅读教材，再通过练习巩固。',
            'difficulty': 'medium'
        })

