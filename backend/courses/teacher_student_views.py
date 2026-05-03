"""教师端班级学生管理与学生画像视图。"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, forbidden_response, success_response

from .models import Class, Enrollment


# 维护意图：获取班级学生列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_students(request, class_id):
    """获取班级学生列表。"""
    user = request.user
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权查看此班级的学生")

    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")
    students = [{"user_id": enrollment.user.id, "username": enrollment.user.username, "real_name": enrollment.user.real_name, "student_id": enrollment.user.student_id, "email": enrollment.user.email, "role": enrollment.role, "enrolled_at": enrollment.enrolled_at.isoformat()} for enrollment in enrollments]
    course_name = class_obj.course.name if class_obj.course else None
    return success_response(data={"class_id": class_id, "class_name": class_obj.name, "course_name": course_name, "total": len(students), "students": students})


# 维护意图：从班级中移除学生
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def remove_student_from_class(request, class_id, user_id):
    """从班级中移除学生。"""
    user = request.user
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权管理此班级")
    try:
        enrollment = Enrollment.objects.get(class_obj=class_obj, user_id=user_id)
    except Enrollment.DoesNotExist:
        return error_response(msg="该学生不在此班级中", code=404)
    enrollment.delete()
    return success_response(msg="学生已从班级中移除")


# 维护意图：获取班级学生画像列表
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def get_class_student_profiles(request, class_id):
    """获取班级学生画像列表。"""
    from assessments.models import AbilityScore
    from knowledge.models import KnowledgeMastery
    from users.models import HabitPreference

    user = request.user
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权查看此班级的学生画像")

    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")
    course = class_obj.course
    student_ids = [enrollment.user_id for enrollment in enrollments]
    ability_by_user = {}
    for ability in AbilityScore.objects.filter(user_id__in=student_ids):
        if ability.user_id not in ability_by_user:
            ability_by_user[ability.user_id] = ability
    habit_by_user = {}
    for habit in HabitPreference.objects.filter(user_id__in=student_ids):
        if habit.user_id not in habit_by_user:
            habit_by_user[habit.user_id] = habit
    mastery_by_user = {}
    if course:
        for mastery in KnowledgeMastery.objects.filter(user_id__in=student_ids, course=course).select_related("knowledge_point"):
            mastery_by_user.setdefault(mastery.user_id, []).append({"point_name": mastery.knowledge_point.name, "mastery_rate": float(mastery.mastery_rate)})

    profiles = []
    for enrollment in enrollments:
        student = enrollment.user
        ability_score = ability_by_user.get(student.id)
        habit = habit_by_user.get(student.id)
        profiles.append({
            "user_id": student.id,
            "username": student.username,
            "real_name": student.real_name,
            "ability_score": {"logical_reasoning": ability_score.logical_reasoning, "memory": ability_score.memory, "innovation": ability_score.innovation} if ability_score is not None else None,
            "habit_preference": {"preferred_resource": habit.preferred_resource, "preferred_study_time": habit.preferred_study_time, "study_pace": habit.study_pace} if habit is not None else None,
            "knowledge_mastery": mastery_by_user.get(student.id, [])[:10],
        })
    return success_response(data={"class_id": class_id, "class_name": class_obj.name, "profiles": profiles})
