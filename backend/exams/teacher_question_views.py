"""教师端题库管理视图。"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from courses.models import Course
from assessments.models import Question

from .teacher_helpers import _parse_pagination


# 维护意图：获取题库列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_list(request):
    """获取题库列表。"""
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
                'id': question.id,
                'content': question.content[:100] + '...' if len(question.content) > 100 else question.content,
                'question_type': question.question_type,
                'difficulty': question.difficulty,
                'score': float(question.score),
                'suggested_score': float(question.suggested_score) if question.suggested_score else None,
                'chapter': question.chapter,
                'is_visible': question.is_visible,
                'for_initial_assessment': question.for_initial_assessment,
                'knowledge_points': list(question.knowledge_points.values('id', 'name')),
            }
            for question in questions
        ],
    })


# 维护意图：创建题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_create(request):
    """创建题目。"""
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
        created_by=request.user,
    )

    knowledge_point_ids = data.get('knowledge_point_ids', [])
    if knowledge_point_ids:
        from knowledge.models import KnowledgePoint

        knowledge_points = KnowledgePoint.objects.filter(id__in=knowledge_point_ids, course=course)
        question.knowledge_points.set(knowledge_points)

    return success_response(data={
        'question_id': question.id,
    }, msg='题目创建成功')


# 维护意图：更新题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_update(request, question_id):
    """更新题目。"""
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

        knowledge_points = KnowledgePoint.objects.filter(id__in=data['knowledge_point_ids'], course=question.course)
        question.knowledge_points.set(knowledge_points)

    return success_response(data={
        'question_id': question.id,
    }, msg='题目更新成功')


# 维护意图：删除题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_delete(request, question_id):
    """删除题目。"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg='题目不存在', code=404)

    if question.created_by != request.user and request.user.role != 'admin' and not request.user.is_superuser:
        return error_response(msg='无权删除此题目', code=403)

    question.delete()

    return success_response(msg='题目已删除')


__all__ = [
    'question_create',
    'question_delete',
    'question_list',
    'question_update',
]
