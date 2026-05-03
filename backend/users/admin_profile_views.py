"""用户模块 - 管理员学生画像接口。"""

from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from assessments.models import AbilityScore, AnswerHistory
from common.permissions import IsAdmin
from common.responses import error_response, success_response
from courses.models import Enrollment
from knowledge.models import KnowledgeMastery
from .admin_helpers import _parse_pagination
from .models import HabitPreference, User
from .serializers import HabitPreferenceSerializer


# 维护意图：管理员查看所有学生画像
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_get_all_student_profiles(request):
    """管理员查看所有学生画像。"""
    course_id = request.query_params.get('course_id')
    user_id = request.query_params.get('user_id')
    page, page_size = _parse_pagination(request.query_params)

    students = User.objects.filter(id=user_id, role='student') if user_id else User.objects.filter(role='student')
    total = students.count()
    students = list(students[(page - 1) * page_size : page * page_size])
    student_ids = [student.id for student in students]

    mastery_qs = KnowledgeMastery.objects.filter(user_id__in=student_ids)
    if course_id:
        mastery_qs = mastery_qs.filter(course_id=course_id)
    mastery_by_user = {}
    for mastery in mastery_qs:
        mastery_by_user.setdefault(mastery.user_id, []).append(float(mastery.mastery_rate))

    ability_qs = AbilityScore.objects.filter(user_id__in=student_ids)
    if course_id:
        ability_qs = ability_qs.filter(course_id=course_id)
    ability_by_user = {}
    for ability in ability_qs:
        if ability.user_id not in ability_by_user:
            ability_by_user[ability.user_id] = ability

    enrollment_counts = dict(
        Enrollment.objects.filter(user_id__in=student_ids)
        .values('user_id')
        .annotate(cnt=models.Count('id'))
        .values_list('user_id', 'cnt')
    )

    profiles = []
    for student in students:
        rates = mastery_by_user.get(student.id, [])
        average_mastery = sum(rates) / len(rates) if rates else 0
        ability_score = ability_by_user.get(student.id)
        ability_scores = ability_score.scores if ability_score else None
        profiles.append({
            'user_id': student.id,
            'username': student.username,
            'real_name': student.real_name,
            'student_id': student.student_id,
            'average_mastery': round(average_mastery, 2),
            'ability_scores': ability_scores if isinstance(ability_scores, dict) else {},
            'courses_enrolled': enrollment_counts.get(student.id, 0),
        })

    return success_response(data={'total': total, 'page': page, 'page_size': page_size, 'profiles': profiles})


# 维护意图：获取指定学生画像详情（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_student_profile_detail(request, student_id):
    """获取指定学生画像详情（管理员）。"""
    try:
        student = User.objects.get(id=student_id, role='student')
    except User.DoesNotExist:
        return error_response(msg='学生不存在', code=404)

    course_id = request.query_params.get('course_id')
    mastery_qs = KnowledgeMastery.objects.filter(user=student).select_related('knowledge_point')
    if course_id:
        mastery_qs = mastery_qs.filter(course_id=course_id)
    mastery_list = [
        {
            'knowledge_point_id': mastery.knowledge_point_id,
            'knowledge_point_name': mastery.knowledge_point.name if mastery.knowledge_point else '',
            'mastery_rate': float(mastery.mastery_rate),
        }
        for mastery in mastery_qs
    ]

    ability_qs = AbilityScore.objects.filter(user=student)
    if course_id:
        ability_qs = ability_qs.filter(course_id=course_id)
    ability = ability_qs.first()
    habit_pref = HabitPreference.objects.filter(user=student).first()
    total_answers = AnswerHistory.objects.filter(user=student).count()
    correct_answers = AnswerHistory.objects.filter(user=student, is_correct=True).count()

    return success_response(data={
        'user_id': student.id,
        'username': student.username,
        'real_name': student.real_name,
        'student_id': student.student_id,
        'knowledge_mastery': mastery_list,
        'ability_scores': ability.scores if ability else {},
        'habit_preferences': HabitPreferenceSerializer(habit_pref).data if habit_pref else {},
        'answer_stats': {
            'total': total_answers,
            'correct': correct_answers,
            'accuracy': round(correct_answers / total_answers * 100, 1) if total_answers > 0 else 0,
        },
    })
