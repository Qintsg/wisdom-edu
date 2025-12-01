"""
用户模块 - 教师接口

包含：教师查看学生画像详情、教师刷新学生画像
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import success_response, error_response, forbidden_response
from courses.models import Enrollment, ClassCourse
from knowledge.models import KnowledgeMastery
from assessments.models import AbilityScore
from .models import User, HabitPreference


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_profile_detail(request, user_id):
    """
    获取单个学生的详细画像（教师/管理员）
    GET /api/teacher/students/{user_id}/profile
    
    查询参数：
    - course_id: 课程ID（可选，缺省时自动获取学生第一个课程）
    """
    user = request.user
    
    if user.role not in ['teacher', 'admin']:
        return forbidden_response(msg='无权查看学生画像')
    
    try:
        student = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return error_response(msg='学生不存在', code=404)
    
    course_id = request.query_params.get('course_id')
    if not course_id:
        first_enrollment = Enrollment.objects.filter(user=student).select_related('class_obj').first()
        if first_enrollment:
            first_cc = ClassCourse.objects.filter(class_obj=first_enrollment.class_obj).first()
            if first_cc:
                course_id = first_cc.course_id
        if not course_id:
            return error_response(msg='缺少课程ID且该学生暂无已加入的课程')
    
    # 教师验证：该学生是否在自己的班级中
    if user.role == 'teacher':
        has_access = Enrollment.objects.filter(
            user=student,
            class_obj__teacher=user,
            class_obj__class_courses__course_id=course_id
        ).exists()
        if not has_access:
            return forbidden_response(msg='该学生不在您的班级中')
    
    mastery_records = KnowledgeMastery.objects.filter(
        user=student, course_id=course_id
    ).select_related('knowledge_point')
    
    mastery_list = [
        {
            'point_id': m.knowledge_point_id,
            'point_name': m.knowledge_point.name,
            'mastery_rate': float(m.mastery_rate),
            'updated_at': m.updated_at.isoformat()
        }
        for m in mastery_records
    ]
    
    ability_score = AbilityScore.objects.filter(
        user=student, course_id=course_id
    ).first()
    # 类型检查
    ability_scores = ability_score.scores if (ability_score and isinstance(ability_score.scores, dict)) else {}

    habit_pref = HabitPreference.objects.filter(user=student).first()

    from assessments.models import ProfileHistory
    profile_history = ProfileHistory.objects.filter(
        user=student, course_id=course_id
    ).order_by('-created_at')[:10]
    
    history_list = [
        {
            'id': ph.id,
            'update_reason': ph.update_reason,
            'average_mastery': sum(ph.knowledge_mastery.values()) / len(ph.knowledge_mastery) if ph.knowledge_mastery else 0,
            'created_at': ph.created_at.isoformat()
        }
        for ph in profile_history
    ]

    from assessments.models import AnswerHistory
    answer_stats = AnswerHistory.objects.filter(
        user=student, course_id=course_id
    )
    total_answers = answer_stats.count()
    correct_answers = answer_stats.filter(is_correct=True).count()
    
    return success_response(data={
        'user_id': student.id,
        'username': student.username,
        'real_name': student.real_name,
        'student_id': student.student_id,
        'course_id': course_id,
        'knowledge_mastery': mastery_list,
        'ability_scores': ability_scores,
        'habit_preferences': {
            'preferred_resource': habit_pref.preferred_resource if habit_pref else None,
            'preferred_study_time': habit_pref.preferred_study_time if habit_pref else None,
            'study_pace': habit_pref.study_pace if habit_pref else None,
            'study_duration': habit_pref.study_duration if habit_pref else None,
            'review_frequency': habit_pref.review_frequency if habit_pref else None,
            'learning_style': habit_pref.learning_style if habit_pref else None
        } if habit_pref else {},
        'answer_stats': {
            'total': total_answers,
            'correct': correct_answers,
            'accuracy': round(correct_answers / total_answers * 100, 1) if total_answers > 0 else 0
        },
        'profile_history': history_list
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def teacher_refresh_student_profile(request, user_id):
    """
    教师主动刷新学生画像（调用KT+LLM服务）
    POST /api/teacher/students/{user_id}/refresh-profile
    """
    user = request.user
    if user.role not in ['teacher', 'admin']:
        return forbidden_response(msg='无权操作')

    course_id = request.data.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID')

    try:
        student = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return error_response(msg='学生不存在', code=404)

    from users.services import get_learner_profile_service
    profile_service = get_learner_profile_service(student)
    result = profile_service.generate_profile_for_course(course_id, force_refresh=True)

    if result.get('success'):
        return success_response(data={
            'summary': result.get('summary', ''),
            'weakness': result.get('weakness', ''),
            'suggestion': result.get('suggestion', ''),
        }, msg='学生画像已刷新')
    else:
        return error_response(msg=f"画像刷新失败: {result.get('error', '未知错误')}", code=500)
