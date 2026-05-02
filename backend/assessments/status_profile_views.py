"""
测评状态与课程画像生成视图。

聚合初始测评完成状态，并暴露课程学习者画像生成入口。
"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.responses import error_response, success_response

from .assessment_helpers import get_authenticated_user
from .models import AbilityScore, AssessmentStatus


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessment_status(request: Request) -> Response:
    """
    获取用户的初始评测完成状态。
    GET /api/assessments/status
    """
    user = get_authenticated_user(request)
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
        status = AssessmentStatus.objects.filter(user=user, course_id=course_id).first()
        knowledge_done = status.knowledge_done if status else False

        from knowledge.models import ProfileSummary
        profile_exists = ProfileSummary.objects.filter(user=user, course_id=course_id).exists()

        result['courses'].append({
            'course_id': int(course_id),
            'knowledge_done': knowledge_done,
            'profile_generated': profile_exists,
        })
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
            profile_exists = ProfileSummary.objects.filter(user=user, course_id=status.course_id).exists()
            result['courses'].append({
                'course_id': status.course_id,
                'knowledge_done': status.knowledge_done,
                'profile_generated': profile_exists,
            })
        if statuses.exists():
            result['knowledge_done'] = all(status.knowledge_done for status in statuses)
            result['knowledge_completed'] = result['knowledge_done']

    return success_response(data=result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_course_profile(request: Request) -> Response:
    """
    为指定课程生成学习者画像。
    POST /api/assessments/profile/generate
    """
    user = get_authenticated_user(request)
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
        return error_response(msg='请先完成学习能力评测和学习偏好问卷')

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
                'suggestion': result.get('suggestion', ''),
            },
            msg='学习者画像生成成功',
        )
    return error_response(msg=f"画像生成失败: {result.get('error', '未知错误')}", code=500)
