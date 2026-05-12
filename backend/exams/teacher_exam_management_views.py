"""教师端考试管理视图。"""

from django.db import models, transaction
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from courses.models import Class, Course
from assessments.models import Question

from .models import Exam, ExamQuestion, ExamSubmission
from .score_policy import sync_exam_totals
from .serializers import ExamCreateSerializer
from .teacher_helpers import (
    _build_exam_question_rows,
    _ensure_teacher_exam_access,
    _get_exam_or_404,
    _get_owned_exam_or_404,
    _parse_pagination,
    _validate_exam_scores,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_manage_list(request):
    """教师获取考试列表。"""
    course_id = request.query_params.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID')

    exams = Exam.objects.filter(
        course_id=course_id,
        created_by=request.user,
    ).order_by('-created_at')

    page, page_size = _parse_pagination(request.query_params)
    total = exams.count()
    exams_page = exams[(page - 1) * page_size: page * page_size]

    return success_response(data={
        'total': total,
        'exams': [
            {
                'exam_id': exam.id,
                'title': exam.title,
                'type': exam.exam_type,
                'status': exam.status,
                'total_score': float(exam.total_score),
                'pass_score': float(exam.pass_score),
                'duration': exam.duration,
                'description': exam.description or '',
                'target_class': exam.target_class_id,
                'question_ids': list(ExamQuestion.objects.filter(exam=exam).values_list('question_id', flat=True)),
                'created_at': exam.created_at.isoformat(),
            }
            for exam in exams_page
        ],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_create(request):
    """创建考试。"""
    serializer = ExamCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(msg=str(serializer.errors))

    data = serializer.validated_data
    try:
        _validate_exam_scores(
            data.get('total_score', 100),
            data.get('pass_score', 60),
        )
    except ValueError as error:
        return error_response(msg=str(error))

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
            status='draft',
        )

        questions = Question.objects.filter(id__in=question_ids)
        ExamQuestion.objects.bulk_create(_build_exam_question_rows(exam, questions))
        sync_exam_totals(exam)

    return success_response(data={
        'exam_id': exam.id,
        'title': exam.title,
    }, msg='作业创建成功')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_publish(request, exam_id):
    """发布考试。"""
    exam, exam_error = _get_owned_exam_or_404(request.user, exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    class_id = request.data.get('class_id')
    if class_id:
        try:
            exam.target_class = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            pass

    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    if start_time:
        exam.start_time = parse_datetime(start_time) or start_time
    if end_time:
        exam.end_time = parse_datetime(end_time) or end_time

    exam.status = 'published'
    exam.save()

    return success_response(data={
        'exam_id': exam.id,
        'status': 'published',
    }, msg='作业已发布')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_teacher_detail(request, exam_id):
    """获取考试详情（教师端）。"""
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
        'question_id': exam_question.question.id,
        'content': exam_question.question.content,
        'type': exam_question.question.question_type,
        'question_type': exam_question.question.question_type,
        'options': exam_question.question.options,
        'correct_answer': exam_question.question.answer.get('answer', exam_question.question.answer) if isinstance(exam_question.question.answer, dict) else exam_question.question.answer,
        'score': exam_question.score,
        'order': exam_question.order,
    } for exam_question in exam_questions.order_by('order')]

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
            'avg_score': round(float(avg_score), 2),
        },
        'created_at': exam.created_at.isoformat(),
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_update(request, exam_id):
    """更新考试信息（教师端）。"""
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

    candidate_total = request.data.get('total_score', exam.total_score)
    candidate_pass = request.data.get('pass_score', exam.pass_score)
    try:
        _validate_exam_scores(candidate_total, candidate_pass)
    except ValueError as error:
        return error_response(msg=str(error))

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
        target_class_id = request.data['target_class']
        if target_class_id:
            try:
                exam.target_class = Class.objects.get(id=target_class_id)
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
        'updated_fields': updated,
    }, msg='作业信息已更新')


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_delete(request, exam_id):
    """删除考试（教师端）。"""
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
    """取消发布考试（教师端）。"""
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


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_exam_add_questions(request, exam_id):
    """向考试添加题目。"""
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
    for question_id in question_ids:
        if question_id not in existing:
            question = Question.objects.filter(id=question_id).first()
            if question is not None:
                questions_to_add.append(question)
                added.append(question_id)

    if added:
        ExamQuestion.objects.bulk_create(
            _build_exam_question_rows(exam, questions_to_add, start_order=max_order + 1)
        )
        sync_exam_totals(exam)

    return success_response(data={'added_count': len(added)}, msg=f'已添加 {len(added)} 道题目')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_exam_remove_questions(request, exam_id):
    """从考试移除题目。"""
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


__all__ = [
    'exam_create',
    'exam_delete',
    'exam_manage_list',
    'exam_publish',
    'exam_teacher_detail',
    'exam_unpublish',
    'exam_update',
    'teacher_exam_add_questions',
    'teacher_exam_remove_questions',
]
