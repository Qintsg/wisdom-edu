"""教师查看学生画像接口的查询与组装 helper。"""

from __future__ import annotations

from assessments.models import AbilityScore, AnswerHistory, ProfileHistory
from common.responses import error_response, forbidden_response
from courses.models import ClassCourse, Enrollment
from knowledge.models import KnowledgeMastery

from .models import HabitPreference, User


# 维护意图：读取学生用户，未命中时返回标准错误响应
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_student_for_teacher_profile(user_id: int):
    """读取学生用户，未命中时返回标准错误响应。"""
    try:
        return User.objects.get(id=user_id), None
    except User.DoesNotExist:
        return None, error_response(msg="学生不存在", code=404)


# 维护意图：解析画像课程 ID，缺省时使用学生首个入班课程
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_profile_course_id(student: User, requested_course_id: object):
    """解析画像课程 ID，缺省时使用学生首个入班课程。"""
    if requested_course_id:
        return requested_course_id, None

    first_enrollment = (
        Enrollment.objects.filter(user=student)
        .select_related("class_obj")
        .first()
    )
    if first_enrollment is None:
        return None, error_response(msg="缺少课程ID且该学生暂无已加入的课程")

    first_class_course = ClassCourse.objects.filter(
        class_obj=first_enrollment.class_obj
    ).first()
    if first_class_course is None:
        return None, error_response(msg="缺少课程ID且该学生暂无已加入的课程")
    return first_class_course.course_id, None


# 维护意图：教师只能查看自己班级中对应课程的学生画像
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def ensure_teacher_can_view_student(request_user: User, student: User, course_id: object):
    """教师只能查看自己班级中对应课程的学生画像。"""
    if request_user.role != "teacher":
        return None

    has_access = Enrollment.objects.filter(
        user=student,
        class_obj__teacher=request_user,
        class_obj__class_courses__course_id=course_id,
    ).exists()
    if has_access:
        return None
    return forbidden_response(msg="该学生不在您的班级中")


# 维护意图：组装教师端学生画像详情响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_student_profile_payload(student: User, course_id: object) -> dict[str, object]:
    """组装教师端学生画像详情响应。"""
    return {
        "user_id": student.id,
        "username": student.username,
        "real_name": student.real_name,
        "student_id": student.student_id,
        "course_id": course_id,
        "knowledge_mastery": _build_mastery_list(student, course_id),
        "ability_scores": _build_ability_scores(student, course_id),
        "habit_preferences": _build_habit_preferences(student),
        "answer_stats": _build_answer_stats(student, course_id),
        "profile_history": _build_profile_history(student, course_id),
    }


# 维护意图：读取知识点掌握度列表
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_mastery_list(student: User, course_id: object) -> list[dict[str, object]]:
    """读取知识点掌握度列表。"""
    mastery_records = KnowledgeMastery.objects.filter(
        user=student,
        course_id=course_id,
    ).select_related("knowledge_point")
    return [
        {
            "point_id": mastery.knowledge_point_id,
            "point_name": mastery.knowledge_point.name,
            "mastery_rate": float(mastery.mastery_rate),
            "updated_at": mastery.updated_at.isoformat(),
        }
        for mastery in mastery_records
    ]


# 维护意图：读取能力评分字典，异常结构按空字典处理
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_ability_scores(student: User, course_id: object) -> dict[str, object]:
    """读取能力评分字典，异常结构按空字典处理。"""
    ability_score = AbilityScore.objects.filter(user=student, course_id=course_id).first()
    if ability_score and isinstance(ability_score.scores, dict):
        return ability_score.scores
    return {}


# 维护意图：读取学生学习偏好
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_habit_preferences(student: User) -> dict[str, object]:
    """读取学生学习偏好。"""
    habit_preference = HabitPreference.objects.filter(user=student).first()
    if habit_preference is None:
        return {}
    return {
        "preferred_resource": habit_preference.preferred_resource,
        "preferred_study_time": habit_preference.preferred_study_time,
        "study_pace": habit_preference.study_pace,
        "study_duration": habit_preference.study_duration,
        "review_frequency": habit_preference.review_frequency,
        "learning_style": habit_preference.learning_style,
    }


# 维护意图：读取最近画像历史
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_profile_history(student: User, course_id: object) -> list[dict[str, object]]:
    """读取最近画像历史。"""
    profile_history = ProfileHistory.objects.filter(
        user=student,
        course_id=course_id,
    ).order_by("-created_at")[:10]
    return [
        {
            "id": history.id,
            "update_reason": history.update_reason,
            "average_mastery": _average_history_mastery(history.knowledge_mastery),
            "created_at": history.created_at.isoformat(),
        }
        for history in profile_history
    ]


# 维护意图：计算画像历史中的平均掌握度
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _average_history_mastery(knowledge_mastery: object) -> float:
    """计算画像历史中的平均掌握度。"""
    if not isinstance(knowledge_mastery, dict) or not knowledge_mastery:
        return 0
    return sum(knowledge_mastery.values()) / len(knowledge_mastery)


# 维护意图：统计学生在课程内的答题正确率
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_answer_stats(student: User, course_id: object) -> dict[str, object]:
    """统计学生在课程内的答题正确率。"""
    answer_records = AnswerHistory.objects.filter(user=student, course_id=course_id)
    total_answers = answer_records.count()
    correct_answers = answer_records.filter(is_correct=True).count()
    return {
        "total": total_answers,
        "correct": correct_answers,
        "accuracy": round(correct_answers / total_answers * 100, 1)
        if total_answers > 0
        else 0,
    }


# 维护意图：刷新学生画像并返回标准响应数据或错误响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_refresh_payload(student: User, course_id: object):
    """刷新学生画像并返回标准响应数据或错误响应。"""
    from users.services import get_learner_profile_service

    profile_service = get_learner_profile_service(student)
    result = profile_service.generate_profile_for_course(course_id, force_refresh=True)
    if result.get("success"):
        return {
            "summary": result.get("summary", ""),
            "weakness": result.get("weakness", ""),
            "suggestion": result.get("suggestion", ""),
        }, None
    return None, error_response(
        msg=f"画像刷新失败: {result.get('error', '未知错误')}",
        code=500,
    )
