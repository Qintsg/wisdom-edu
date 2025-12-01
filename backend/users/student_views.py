"""
用户模块 - 学生画像接口

包含：画像查看、习惯偏好更新、画像刷新、历史对比、导出
"""

from typing import TypedDict

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from assessments.models import AbilityScore
from common.responses import error_response, success_response
from knowledge.models import KnowledgeMastery, ProfileSummary

from .models import HabitPreference
from .serializers import HabitPreferenceSerializer


class ProfileSnapshotPayload(TypedDict):
    """画像历史快照的序列化结构。"""

    summary: str
    weakness: str
    suggestion: str
    generated_at: str | None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    获取学习者画像
    GET /api/profile
    """
    user = request.user
    course_id = request.query_params.get('course_id')

    mastery_qs = KnowledgeMastery.objects.filter(user=user)
    if course_id:
        mastery_qs = mastery_qs.filter(course_id=course_id)

    knowledge_mastery = [
        {
            'point_id': mastery.knowledge_point_id,
            'point_name': mastery.knowledge_point.name,
            'mastery_rate': float(mastery.mastery_rate) if mastery.mastery_rate else 0,
            'updated_at': mastery.updated_at.isoformat() if mastery.updated_at else None,
        }
        for mastery in mastery_qs.select_related('knowledge_point')
    ]

    # 课程维度优先，缺失时回退到全局能力评估。
    ability_qs = AbilityScore.objects.filter(user=user)
    if course_id:
        course_ability = ability_qs.filter(course_id=course_id).first()
        ability_score = course_ability or ability_qs.first()
    else:
        ability_score = ability_qs.first()
    ability_scores = (
        ability_score.scores
        if ability_score and isinstance(ability_score.scores, dict)
        else {}
    )

    habit_pref = HabitPreference.objects.filter(user=user).first()
    habit_preferences = {}
    if habit_pref:
        habit_preferences = {
            'preferred_resource': habit_pref.preferred_resource,
            'preferred_study_time': habit_pref.preferred_study_time,
            'study_pace': habit_pref.study_pace,
            'study_duration': habit_pref.study_duration,
            'review_frequency': habit_pref.review_frequency,
            'learning_style': habit_pref.learning_style,
            'accept_challenge': habit_pref.accept_challenge,
            'daily_goal_minutes': habit_pref.daily_goal_minutes,
            'weekly_goal_days': habit_pref.weekly_goal_days,
            **(habit_pref.preferences if isinstance(habit_pref.preferences, dict) else {}),
        }

    # 生成学习者标签
    learner_tags = []
    if ability_scores:
        try:
            sorted_abilities = sorted(
                ability_scores.items(),
                key=lambda item: float(item[1]) if item[1] is not None else 0,
                reverse=True,
            )
        except (TypeError, ValueError):
            sorted_abilities = []
        ability_name_map = {
            # C-WAIS 维度
            '言语理解': '言语型', '知觉推理': '推理型',
            '工作记忆': '记忆型', '处理速度': '高效型',
            # 旧维度兼容
            'logical_reasoning': '逻辑型', 'memory': '记忆型', 'analysis': '分析型',
            'innovation': '创新型', 'comprehension': '理解型', 'application': '实践型',
        }
        if sorted_abilities:
            top_key = sorted_abilities[0][0]
            learner_tags.append(ability_name_map.get(top_key, '全能型') + '学习者')
    if habit_pref:
        if habit_pref.preferred_resource == 'video':
            learner_tags.append('视觉型')
        elif habit_pref.preferred_resource in ('text', 'document'):
            learner_tags.append('阅读型')
        elif habit_pref.preferred_resource == 'exercise':
            learner_tags.append('实践型')
        preferred_time = habit_pref.preferred_study_time
        if preferred_time == 'evening':
            learner_tags.append('晚间学习')
        elif preferred_time:
            learner_tags.append('日间学习')
        pace = habit_pref.study_pace
        if pace:
            learner_tags.append(
                {
                    'fast': '快节奏',
                    'moderate': '中节奏',
                    'slow': '慢节奏',
                    'adaptive': '自适应',
                }.get(pace, '中节奏')
            )

    summary_qs = ProfileSummary.objects.filter(user=user)
    if course_id:
        summary_qs = summary_qs.filter(course_id=course_id)
    summary = summary_qs.first()
    profile_summary = summary.summary or '' if summary else ''
    weakness = summary.weakness or '' if summary else ''
    suggestion = summary.suggestion or '' if summary else ''
    strength = ''
    if summary:
        strength = getattr(summary, 'strength', '') or ''
    last_update = summary.generated_at if summary else timezone.now()

    # 补充空数据提示
    if not knowledge_mastery and not ability_scores and not habit_preferences:
        profile_summary = profile_summary or '你还没有完成任何评测，请先完成初始评测以生成学习者画像。'

    # 按掌握度升序排序（薄弱项优先）
    knowledge_mastery.sort(key=lambda item: item['mastery_rate'])

    return success_response(
        data={
            'knowledge_mastery': knowledge_mastery,
            'ability_scores': ability_scores,
            'habit_preferences': habit_preferences,
            'learner_tags': learner_tags,
            'profile_summary': profile_summary,
            'weakness': weakness,
            'suggestion': suggestion,
            'strength': strength,
            'last_update': last_update.isoformat(),
        }
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_habit_preference(request):
    """
    更新学习习惯偏好
    PUT /api/profile/habit
    """
    habit_pref, _ = HabitPreference.objects.get_or_create(user=request.user)
    serializer = HabitPreferenceSerializer(habit_pref, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response(
            data=serializer.data,
            msg='学习偏好已更新',
        )
    return error_response(msg=str(serializer.errors), code=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_student_profile(request):
    """
    手动更新学生画像（主动刷新）
    PUT /api/student/profile/update

    调用KT服务细化掌握度 + LLM服务生成AI画像分析

    请求参数：
    - course_id: 课程ID（必填）
    """
    course_id = request.data.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID', code=400)

    from users.services import get_learner_profile_service

    profile_service = get_learner_profile_service(request.user)
    result = profile_service.generate_profile_for_course(course_id, force_refresh=True)
    if not result.get('success'):
        return error_response(
            msg=f"画像刷新失败: {result.get('error', '未知错误')}",
            code=500,
        )
    return success_response(
        data={
            'course_id': course_id,
            'summary': result.get('summary', ''),
            'weakness': result.get('weakness', ''),
            'suggestion': result.get('suggestion', ''),
            'strength': result.get('strength', []),
            'kt_enhanced': result.get('kt_enhanced', False),
        },
        msg='画像刷新成功（已调用AI分析）',
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_history(request):
    """
    获取画像历史（趋势对比）
    GET /api/profile/history

    查询参数：
    - course_id: 课程ID（必填）
    - limit: 返回记录数（默认10）
    """
    from assessments.models import ProfileHistory

    course_id = request.query_params.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID', code=400)

    try:
        limit = min(max(1, int(request.query_params.get('limit', 10))), 100)
    except (ValueError, TypeError):
        limit = 10

    history = ProfileHistory.objects.filter(
        user=request.user,
        course_id=course_id,
    ).order_by('-created_at')[:limit]
    history_list = [
        {
            'id': profile_history.id,
            'knowledge_mastery': profile_history.knowledge_mastery,
            'ability_scores': profile_history.ability_scores,
            'update_reason': profile_history.update_reason,
            'created_at': profile_history.created_at.isoformat(),
        }
        for profile_history in history
    ]
    return success_response(data={
        'course_id': course_id,
        'history': history_list,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_compare(request):
    """
    对比不同时间的学习画像
    GET /api/student/profile/compare

    查询参数：
    - date1: 第一个时间点 (YYYY-MM-DD)
    - date2: 第二个时间点 (YYYY-MM-DD)
    """
    date1 = request.query_params.get('date1')
    date2 = request.query_params.get('date2')
    if not date1 or not date2:
        return error_response(msg='请提供两个比较日期', code=400)

    history = ProfileSummary.objects.filter(user=request.user).order_by('generated_at')
    snapshot1 = history.filter(generated_at__date__lte=date1).last()
    snapshot2 = history.filter(generated_at__date__lte=date2).last()

    def snapshot_data(summary_record: ProfileSummary | None) -> ProfileSnapshotPayload | None:
        """将画像摘要对象转换为可序列化的快照数据。"""
        if summary_record is None:
            return None
        return {
            'summary': summary_record.summary,
            'weakness': summary_record.weakness,
            'suggestion': summary_record.suggestion,
            'generated_at': summary_record.generated_at.isoformat() if summary_record.generated_at else None,
        }

    return success_response(
        data={
            'date1': date1,
            'date2': date2,
            'snapshot1': snapshot_data(snapshot1),
            'snapshot2': snapshot_data(snapshot2),
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def profile_export(request):
    """
    导出学习画像为 JSON（简版，PDF 需集成额外库）
    POST /api/student/profile/export
    """
    import json as json_mod

    from django.http import HttpResponse

    user = request.user
    mastery_qs = KnowledgeMastery.objects.filter(user=user).select_related('knowledge_point')
    mastery_list = [
        {
            'knowledge_point': mastery.knowledge_point.name if mastery.knowledge_point else '',
            'mastery_rate': float(mastery.mastery_rate),
        }
        for mastery in mastery_qs
    ]
    ability = AbilityScore.objects.filter(user=user).first()
    habit_pref = HabitPreference.objects.filter(user=user).first()

    profile_data = {
        'user': user.username,
        'real_name': user.real_name,
        'knowledge_mastery': mastery_list,
        'ability_scores': ability.scores if ability else {},
        'habit_preferences': HabitPreferenceSerializer(habit_pref).data if habit_pref else {},
    }
    response = HttpResponse(
        json_mod.dumps(profile_data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8',
    )
    response['Content-Disposition'] = f'attachment; filename="profile_{user.username}.json"'
    return response
