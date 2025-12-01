"""
考试模块 - 教师接口

包含：考试管理、试题管理、成绩分析、导出
"""
import codecs
from collections.abc import Iterable, Mapping
import csv
import logging
from decimal import Decimal, InvalidOperation
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models, transaction
from django.http import HttpResponse

from common.responses import success_response, error_response, forbidden_response
from common.permissions import IsTeacherOrAdmin
from courses.models import Class, Course
from users.models import User
from .models import Exam, ExamQuestion, ExamSubmission
from .score_policy import sync_exam_totals
from .serializers import ExamCreateSerializer
from assessments.models import Question

logger = logging.getLogger(__name__)
UTF8_BOM = codecs.BOM_UTF8.decode('utf-8')


def _validate_exam_scores(total_score, pass_score):
    """校验总分与及格分关系。"""
    try:
        total_val = Decimal(str(total_score))
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError('总分格式错误')

    try:
        pass_val = Decimal(str(pass_score))
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError('及格分格式错误')

    if total_val <= 0:
        raise ValueError('总分必须大于0')
    if pass_val <= 0:
        raise ValueError('及格分必须大于0')
    if pass_val > total_val:
        raise ValueError('及格分不能大于总分')


def _parse_pagination(
    query_params: Mapping[str, object],
    *,
    size_key: str = 'page_size',
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    """安全解析分页参数。"""

    try:
        page = max(1, int(query_params.get('page', 1)))
        page_size = min(max(1, int(query_params.get(size_key, default_size))), max_size)
    except (ValueError, TypeError):
        return 1, default_size
    return page, page_size


def _normalize_choice_answer_set(answer_value: object) -> set[str]:
    """将多选答案规整成可比较的字符串集合。"""

    resolved_answer = answer_value.get('answer', answer_value) if isinstance(answer_value, Mapping) else answer_value
    if isinstance(resolved_answer, Iterable) and not isinstance(resolved_answer, (str, bytes, Mapping)):
        return {
            str(item).strip().lower()
            for item in resolved_answer
            if str(item).strip()
        }
    normalized_text = str(resolved_answer).strip().lower()
    return {normalized_text} if normalized_text else set()


def _get_exam_or_404(exam_id: int) -> tuple[Exam | None, Response | None]:
    """按 ID 获取考试，不存在时返回标准错误响应。"""

    try:
        return Exam.objects.get(id=exam_id), None
    except Exam.DoesNotExist:
        return None, error_response(msg='作业不存在', code=404)


def _get_owned_exam_or_404(user: User, exam_id: int) -> tuple[Exam | None, Response | None]:
    """获取当前教师创建的考试，不存在时返回标准错误响应。"""

    try:
        return Exam.objects.get(id=exam_id, created_by=user), None
    except Exam.DoesNotExist:
        return None, error_response(msg='作业不存在', code=404)


def _get_teacher_course_ids(user: User) -> set[int]:
    """获取教师可管理的课程 ID 集合。"""

    return set(Class.objects.filter(teacher=user).values_list('course_id', flat=True))


def _ensure_teacher_exam_access(
    user: User,
    exam: Exam,
    *,
    deny_message: str,
    allow_creator_bypass: bool = True,
) -> Response | None:
    """校验教师是否可访问指定考试。"""

    if user.role != 'teacher':
        return None
    if allow_creator_bypass and exam.created_by_id == user.id:
        return None
    if exam.course_id in _get_teacher_course_ids(user):
        return None
    return forbidden_response(msg=deny_message)


def _build_exam_question_rows(
    exam: Exam,
    questions: Iterable[Question],
    *,
    start_order: int = 0,
) -> list[ExamQuestion]:
    """按顺序构造考试题目关联记录。"""

    return [
        ExamQuestion(exam=exam, question=question, score=question.score, order=start_order + index)
        for index, question in enumerate(questions)
    ]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_manage_list(request):
    """
    教师获取考试列表
    GET /api/teacher/exams
    """
    course_id = request.query_params.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID')
    
    exams = Exam.objects.filter(
        course_id=course_id,
        created_by=request.user
    ).order_by('-created_at')
    
    page, page_size = _parse_pagination(request.query_params)
    
    total = exams.count()
    exams_page = exams[(page - 1) * page_size: page * page_size]
    
    return success_response(data={
        'total': total,
        'exams': [
            {
                'exam_id': e.id,
                'title': e.title,
                'type': e.exam_type,
                'status': e.status,
                'total_score': float(e.total_score),
                'pass_score': float(e.pass_score),
                'duration': e.duration,
                'description': e.description or '',
                'target_class': e.target_class_id,
                'question_ids': list(ExamQuestion.objects.filter(exam=e).values_list('question_id', flat=True)),
                'created_at': e.created_at.isoformat()
            }
            for e in exams_page
        ]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_create(request):
    """
    创建考试
    POST /api/teacher/exams/create
    """
    serializer = ExamCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(msg=str(serializer.errors))
    
    data = serializer.validated_data
    try:
        _validate_exam_scores(
            data.get('total_score', 100),
            data.get('pass_score', 60),
        )
    except ValueError as e:
        return error_response(msg=str(e))

    course_id = data['course_id']
    question_ids = data['questions']
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)
    
    with transaction.atomic():
        target_class_id = data.get('target_class')
        target_class_obj = None
        if target_class_id:
            try:
                target_class_obj = Class.objects.get(id=target_class_id)
            except Class.DoesNotExist:
                pass
        
        exam = Exam.objects.create(
            course=course,
            title=data['title'],
            description=data.get('description', ''),
            exam_type=data.get('exam_type', 'chapter'),
            total_score=0,
            pass_score=0,
            duration=data.get('duration', 60),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            target_class=target_class_obj,
            created_by=request.user,
            status='draft'
        )
        
        questions = Question.objects.filter(id__in=question_ids)
        ExamQuestion.objects.bulk_create(_build_exam_question_rows(exam, questions))
        sync_exam_totals(exam)
    
    return success_response(data={
        'exam_id': exam.id,
        'title': exam.title
    }, msg='作业创建成功')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_publish(request, exam_id):
    """
    发布考试
    POST /api/teacher/exams/{exam_id}/publish
    """
    exam, exam_error = _get_owned_exam_or_404(request.user, exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None
    
    class_id = request.data.get('class_id')
    if class_id:
        try:
            target_class = Class.objects.get(id=class_id)
            exam.target_class = target_class
        except Class.DoesNotExist:
            pass
    
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    if start_time:
        from django.utils.dateparse import parse_datetime
        exam.start_time = parse_datetime(start_time) or start_time
    if end_time:
        from django.utils.dateparse import parse_datetime as pd2
        exam.end_time = pd2(end_time) or end_time
    
    exam.status = 'published'
    exam.save()
    
    return success_response(data={
        'exam_id': exam.id,
        'status': 'published'
    }, msg='作业已发布')


# ========== 题库管理 ==========


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_list(request):
    """
    获取题库列表
    GET /api/teacher/questions
    """
    course_id = request.query_params.get('course_id')
    question_type = request.query_params.get('question_type')
    difficulty = request.query_params.get('difficulty')
    for_initial = request.query_params.get('for_initial_assessment')
    is_visible = request.query_params.get('is_visible')
    page, page_size = _parse_pagination(request.query_params)
    
    if not course_id:
        return error_response(msg='缺少课程ID')
    
    queryset = Question.objects.filter(course_id=course_id)
    
    if question_type:
        queryset = queryset.filter(question_type=question_type)
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)
    if for_initial is not None:
        queryset = queryset.filter(for_initial_assessment=for_initial.lower() == 'true')
    if is_visible is not None:
        queryset = queryset.filter(is_visible=is_visible.lower() == 'true')
    
    total = queryset.count()
    start = (page - 1) * page_size
    questions = queryset.prefetch_related('knowledge_points')[start:start + page_size]
    
    return success_response(data={
        'total': total,
        'page': page,
        'questions': [
            {
                'id': q.id,
                'content': q.content[:100] + '...' if len(q.content) > 100 else q.content,
                'question_type': q.question_type,
                'difficulty': q.difficulty,
                'score': float(q.score),
                'suggested_score': float(q.suggested_score) if q.suggested_score else None,
                'chapter': q.chapter,
                'is_visible': q.is_visible,
                'for_initial_assessment': q.for_initial_assessment,
                'knowledge_points': list(q.knowledge_points.values('id', 'name'))
            }
            for q in questions
        ]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_create(request):
    """
    创建题目
    POST /api/teacher/questions/create
    """
    data = request.data
    course_id = data.get('course_id')
    content = data.get('content')
    question_type = data.get('question_type')
    
    if not all([course_id, content, question_type]):
        return error_response(msg='缺少必填参数')
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)
    
    question = Question.objects.create(
        course=course,
        content=content,
        question_type=question_type,
        options=data.get('options', []),
        answer=data.get('answer', {}),
        analysis=data.get('analysis', ''),
        difficulty=data.get('difficulty', 'medium'),
        score=data.get('score', 1),
        is_visible=data.get('is_visible', True),
        for_initial_assessment=data.get('for_initial_assessment', False),
        created_by=request.user
    )
    
    knowledge_point_ids = data.get('knowledge_point_ids', [])
    if knowledge_point_ids:
        from knowledge.models import KnowledgePoint
        kps = KnowledgePoint.objects.filter(id__in=knowledge_point_ids, course=course)
        question.knowledge_points.set(kps)
    
    return success_response(data={
        'question_id': question.id
    }, msg='题目创建成功')


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_update(request, question_id):
    """
    更新题目
    PUT /api/teacher/questions/{question_id}
    """
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg='题目不存在', code=404)
    
    if question.created_by != request.user and request.user.role != 'admin' and not request.user.is_superuser:
        return error_response(msg='无权编辑此题目', code=403)
    
    data = request.data
    allowed_fields = ['content', 'question_type', 'options', 'answer', 'analysis', 
                      'difficulty', 'score', 'suggested_score', 'chapter',
                      'is_visible', 'for_initial_assessment']
    
    for field in allowed_fields:
        if field in data:
            setattr(question, field, data[field])
    
    question.save()
    
    if 'knowledge_point_ids' in data:
        from knowledge.models import KnowledgePoint
        kps = KnowledgePoint.objects.filter(id__in=data['knowledge_point_ids'], course=question.course)
        question.knowledge_points.set(kps)
    
    return success_response(data={
        'question_id': question.id
    }, msg='题目更新成功')


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_delete(request, question_id):
    """
    删除题目
    DELETE /api/teacher/questions/{question_id}
    """
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg='题目不存在', code=404)
    
    if question.created_by != request.user and request.user.role != 'admin' and not request.user.is_superuser:
        return error_response(msg='无权删除此题目', code=403)
    
    question.delete()
    
    return success_response(msg='题目已删除')


# ========== 初始评测 ==========


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_teacher_detail(request, exam_id):
    """
    获取考试详情（教师端）
    GET /api/teacher/exams/{exam_id}
    
    返回考试的完整信息，包括题目列表
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权查看此作业',
    )
    if permission_error is not None:
        return permission_error
    
    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question')
    questions = [{
        'question_id': eq.question.id,
        'content': eq.question.content,
        'type': eq.question.question_type,
        'question_type': eq.question.question_type,
        'options': eq.question.options,
        'correct_answer': eq.question.answer.get('answer', eq.question.answer) if isinstance(eq.question.answer, dict) else eq.question.answer,
        'score': eq.score,
        'order': eq.order
    } for eq in exam_questions.order_by('order')]
    
    submissions = ExamSubmission.objects.filter(exam=exam)
    submission_count = submissions.count()
    passed_count = submissions.filter(is_passed=True).count()
    avg_score = submissions.aggregate(avg=models.Avg('score'))['avg'] or 0
    
    return success_response(data={
        'exam_id': exam.id,
        'title': exam.title,
        'exam_type': exam.exam_type,
        'course_id': exam.course_id,
        'course_name': exam.course.name if exam.course else None,
        'duration': exam.duration,
        'total_score': float(exam.total_score),
        'pass_score': float(exam.pass_score),
        'is_published': exam.status == 'published',
        'status': exam.status,
        'start_time': exam.start_time.isoformat() if exam.start_time else None,
        'end_time': exam.end_time.isoformat() if exam.end_time else None,
        'questions': questions,
        'statistics': {
            'submission_count': submission_count,
            'passed_count': passed_count,
            'avg_score': round(float(avg_score), 2)
        },
        'created_at': exam.created_at.isoformat()
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_update(request, exam_id):
    """
    更新考试信息（教师端）
    PUT /api/teacher/exams/{exam_id}
    
    可更新字段：title, duration, pass_score, start_time, end_time
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权修改此作业',
        allow_creator_bypass=False,
    )
    if permission_error is not None:
        return permission_error
    
    if exam.status == 'published':
        allowed_fields = ['end_time']
    else:
        allowed_fields = ['title', 'description', 'exam_type', 'duration',
                          'pass_score', 'total_score', 'start_time', 'end_time']
    
    # 分值参数联动校验（防止出现 pass_score<=0 导致总是通过）
    candidate_total = request.data.get('total_score', exam.total_score)
    candidate_pass = request.data.get('pass_score', exam.pass_score)
    try:
        _validate_exam_scores(candidate_total, candidate_pass)
    except ValueError as e:
        return error_response(msg=str(e))

    updated = []
    for field in allowed_fields:
        if field in request.data:
            setattr(exam, field, request.data[field])
            updated.append(field)
    
    if exam.status != 'published' and 'questions' in request.data:
        question_ids = request.data['questions']
        if isinstance(question_ids, list):
            with transaction.atomic():
                ExamQuestion.objects.filter(exam=exam).delete()
                questions = Question.objects.filter(id__in=question_ids)
                ExamQuestion.objects.bulk_create(_build_exam_question_rows(exam, questions))
                updated.append('questions')
    
    if exam.status != 'published' and 'target_class' in request.data:
        tc_id = request.data['target_class']
        if tc_id:
            try:
                exam.target_class = Class.objects.get(id=tc_id)
                updated.append('target_class')
            except Class.DoesNotExist:
                pass
        else:
            exam.target_class = None
            updated.append('target_class')
    
    if updated:
        exam.save()
        if 'questions' in updated:
            sync_exam_totals(exam)
    
    return success_response(data={
        'exam_id': exam.id,
        'updated_fields': updated
    }, msg='作业信息已更新')


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_delete(request, exam_id):
    """
    删除考试（教师端）
    DELETE /api/teacher/exams/{exam_id}/delete
    
    已发布或有提交记录的考试不能删除
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权删除此作业',
    )
    if permission_error is not None:
        return permission_error
    
    if ExamSubmission.objects.filter(exam=exam).exists():
        return error_response(msg='作业已有提交记录，无法删除')
    
    if exam.status == 'published':
        return error_response(msg='已发布的作业无法删除，请先取消发布')
    
    exam_title = exam.title
    exam.delete()
    
    return success_response(msg=f'作业 "{exam_title}" 已删除')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_unpublish(request, exam_id):
    """
    取消发布考试（教师端）
    POST /api/teacher/exams/{exam_id}/unpublish
    
    已有提交记录的考试不能取消发布
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权操作此作业',
    )
    if permission_error is not None:
        return permission_error
    
    if exam.status != 'published':
        return error_response(msg='作业未发布')
    
    if ExamSubmission.objects.filter(exam=exam).exists():
        return error_response(msg='作业已有提交记录，无法取消发布')
    
    exam.status = 'draft'
    exam.save()
    
    return success_response(msg='作业已取消发布')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_results(request, exam_id):
    """
    获取考试成绩列表（教师端）
    GET /api/teacher/exams/{exam_id}/results
    
    查询参数：
    - page: 页码
    - size: 每页数量
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权查看此作业成绩',
    )
    if permission_error is not None:
        return permission_error

    page, size = _parse_pagination(request.query_params, size_key='size')
    
    submissions = ExamSubmission.objects.filter(exam=exam).select_related('user').order_by('-submitted_at')
    
    total = submissions.count()
    start = (page - 1) * size
    end = start + size
    submissions = submissions[start:end]
    
    results = [{
        'submission_id': s.id,
        'user_id': s.user.id,
        'username': s.user.username,
        'real_name': s.user.real_name or '',
        'score': float(s.score),
        'is_passed': s.is_passed,
        'submitted_at': s.submitted_at.isoformat()
    } for s in submissions]
    
    return success_response(data={
        'exam_id': exam_id,
        'exam_title': exam.title,
        'total': total,
        'page': page,
        'size': size,
        'results': results
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_student_detail(request, exam_id, student_id):
    """
    获取学生考试详情（教师端）
    GET /api/teacher/exams/{exam_id}/students/{student_id}
    
    返回学生的答题详情和成绩
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权查看此作业',
    )
    if permission_error is not None:
        return permission_error
    
    try:
        submission = ExamSubmission.objects.get(exam=exam, user_id=student_id)
    except ExamSubmission.DoesNotExist:
        return error_response(msg='学生未提交作业', code=404)
    
    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question')
    answers = submission.answers or {}
    
    question_details = []
    for eq in exam_questions.order_by('order'):
        q = eq.question
        student_answer = answers.get(str(q.id), '')
        correct_answer = q.answer.get('answer', q.answer) if isinstance(q.answer, dict) else q.answer
        
        if q.question_type in ['single_choice', 'true_false']:
            is_correct = student_answer == correct_answer
        elif q.question_type == 'multiple_choice':
            correct_set = _normalize_choice_answer_set(correct_answer)
            student_set = _normalize_choice_answer_set(student_answer)
            is_correct = correct_set == student_set
        else:
            is_correct = str(student_answer).strip().lower() == str(correct_answer).strip().lower()
        
        question_details.append({
            'question_id': q.id,
            'content': q.content,
            'question_type': q.question_type,
            'options': q.options,
            'correct_answer': correct_answer,
            'student_answer': student_answer,
            'is_correct': is_correct,
            'score': eq.score if is_correct else 0
        })
    
    return success_response(data={
        'exam_id': exam_id,
        'exam_title': exam.title,
        'student': {
            'user_id': submission.user.id,
            'username': submission.user.username,
            'real_name': submission.user.real_name or ''
        },
        'score': float(submission.score),
        'is_passed': submission.is_passed,
        'submitted_at': submission.submitted_at.isoformat(),
        'questions': question_details
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_analysis(request, exam_id):
    """
    获取考试统计分析（教师端）
    GET /api/teacher/exams/{exam_id}/analysis
    
    返回考试的整体统计和题目正确率分析
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权查看此作业',
    )
    if permission_error is not None:
        return permission_error
    
    submissions = ExamSubmission.objects.filter(exam=exam)
    
    total_submissions = submissions.count()
    if total_submissions == 0:
        return success_response(data={
            'exam_id': exam_id,
            'exam_title': exam.title,
            'total_submissions': 0,
            'message': '暂无提交记录'
        })
    
    passed_count = submissions.filter(is_passed=True).count()
    scores = list(submissions.values_list('score', flat=True))
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    score_distribution = {
        '0-59': 0,
        '60-69': 0,
        '70-79': 0,
        '80-89': 0,
        '90-100': 0
    }
    for score in scores:
        if score < 60:
            score_distribution['0-59'] += 1
        elif score < 70:
            score_distribution['60-69'] += 1
        elif score < 80:
            score_distribution['70-79'] += 1
        elif score < 90:
            score_distribution['80-89'] += 1
        else:
            score_distribution['90-100'] += 1
    
    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question')
    question_analysis = []
    
    for eq in exam_questions.order_by('order'):
        q = eq.question
        correct_count = 0
        correct_answer = q.answer.get('answer', q.answer) if isinstance(q.answer, dict) else q.answer
        for s in submissions:
            answers = s.answers or {}
            student_answer = answers.get(str(q.id))
            
            if q.question_type in ['single_choice', 'true_false']:
                if student_answer == correct_answer:
                    correct_count += 1
            elif q.question_type == 'multiple_choice':
                correct_set = _normalize_choice_answer_set(correct_answer)
                student_set = _normalize_choice_answer_set(student_answer)
                if correct_set == student_set:
                    correct_count += 1
            else:
                if student_answer is not None and str(student_answer).strip().lower() == str(correct_answer).strip().lower():
                    correct_count += 1
        
        accuracy = correct_count / total_submissions if total_submissions > 0 else 0
        question_analysis.append({
            'question_id': q.id,
            'content': q.content[:50] + '...' if len(q.content) > 50 else q.content,
            'accuracy': round(accuracy, 3),
            'correct_count': correct_count,
            'total_count': total_submissions
        })
    
    return success_response(data={
        'exam_id': exam_id,
        'exam_title': exam.title,
        'statistics': {
            'total_submissions': total_submissions,
            'passed_count': passed_count,
            'pass_rate': round(passed_count / total_submissions, 3),
            'avg_score': round(float(avg_score), 2),
            'max_score': float(max_score),
            'min_score': float(min_score)
        },
        'score_distribution': score_distribution,
        'question_analysis': question_analysis
    })


# ============ 学生端 — 考试扩展 ============


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_exam_export(request, exam_id):
    """
    导出考试成绩
    GET /api/teacher/exams/{exam_id}/export
    """
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权导出此作业成绩',
    )
    if permission_error is not None:
        return permission_error

    subs = ExamSubmission.objects.filter(exam=exam, score__gte=0).select_related('user')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="homework_{exam_id}_results.csv"'
    response.write(UTF8_BOM)

    writer = csv.writer(response)
    writer.writerow(['学生ID', '用户名', '姓名', '成绩', '提交时间'])

    for s in subs:
        writer.writerow([
            s.user.id,
            s.user.username,
            s.user.real_name or '',
            float(s.score),
            s.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if s.submitted_at else '',
        ])

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_exam_add_questions(request, exam_id):
    """
    向考试添加题目
    POST /api/teacher/exams/{exam_id}/questions/add
    """
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg='作业不存在', code=404)

    question_ids = request.data.get('question_ids', [])
    if not question_ids:
        return error_response(msg='请提供题目ID列表')

    existing = set(ExamQuestion.objects.filter(exam=exam).values_list('question_id', flat=True))
    max_order = ExamQuestion.objects.filter(exam=exam).aggregate(m=models.Max('order'))['m'] or 0

    added = []
    questions_to_add = []
    for qid in question_ids:
        if qid not in existing:
            question = Question.objects.filter(id=qid).first()
            if question is not None:
                questions_to_add.append(question)
                added.append(qid)

    if added:
        ExamQuestion.objects.bulk_create(
            _build_exam_question_rows(exam, questions_to_add, start_order=max_order + 1)
        )
        sync_exam_totals(exam)

    return success_response(data={'added_count': len(added)}, msg=f'已添加 {len(added)} 道题目')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_exam_remove_questions(request, exam_id):
    """
    从考试移除题目
    POST /api/teacher/exams/{exam_id}/questions/remove
    """
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg='作业不存在', code=404)

    question_ids = request.data.get('question_ids', [])
    if not question_ids:
        return error_response(msg='请提供题目ID列表')

    deleted_count, _ = ExamQuestion.objects.filter(exam=exam, question_id__in=question_ids).delete()
    if deleted_count:
        sync_exam_totals(exam)
    return success_response(data={'removed_count': deleted_count}, msg=f'已移除 {deleted_count} 道题目')
