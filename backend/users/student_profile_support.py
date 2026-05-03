"""学生画像接口的数据查询与响应组装。"""

from __future__ import annotations

import json
from typing import TypedDict

from django.http import HttpResponse
from django.utils import timezone

from assessments.models import AbilityScore, ProfileHistory
from knowledge.models import KnowledgeMastery, ProfileSummary
from users.models import HabitPreference, User
from users.serializers import HabitPreferenceSerializer


# 维护意图：画像历史快照的序列化结构
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ProfileSnapshotPayload(TypedDict):
    """画像历史快照的序列化结构。"""

    summary: str
    weakness: str
    suggestion: str
    generated_at: str | None


# 维护意图：组装学生端学习者画像响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_student_profile_payload(user: User, course_id: object | None) -> dict[str, object]:
    """组装学生端学习者画像响应。"""
    knowledge_mastery = build_knowledge_mastery_payload(user, course_id)
    ability_scores = build_ability_scores(user, course_id)
    habit_preference = HabitPreference.objects.filter(user=user).first()
    habit_preferences = build_habit_preferences(habit_preference)
    profile_summary = build_profile_summary_payload(user, course_id)
    if not knowledge_mastery and not ability_scores and not habit_preferences:
        profile_summary["profile_summary"] = (
            profile_summary["profile_summary"]
            or "你还没有完成任何评测，请先完成初始评测以生成学习者画像。"
        )

    knowledge_mastery.sort(key=lambda item: item["mastery_rate"])
    return {
        "knowledge_mastery": knowledge_mastery,
        "ability_scores": ability_scores,
        "habit_preferences": habit_preferences,
        "learner_tags": build_learner_tags(ability_scores, habit_preference),
        **profile_summary,
    }


# 维护意图：读取并序列化学生知识点掌握度
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_knowledge_mastery_payload(user: User, course_id: object | None) -> list[dict[str, object]]:
    """读取并序列化学生知识点掌握度。"""
    mastery_records = KnowledgeMastery.objects.filter(user=user)
    if course_id:
        mastery_records = mastery_records.filter(course_id=course_id)
    return [
        {
            "point_id": mastery.knowledge_point_id,
            "point_name": mastery.knowledge_point.name,
            "mastery_rate": float(mastery.mastery_rate) if mastery.mastery_rate else 0,
            "updated_at": mastery.updated_at.isoformat() if mastery.updated_at else None,
        }
        for mastery in mastery_records.select_related("knowledge_point")
    ]


# 维护意图：课程维度优先读取能力评分，缺失时回退全局能力评估
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_ability_scores(user: User, course_id: object | None) -> dict[str, object]:
    """课程维度优先读取能力评分，缺失时回退全局能力评估。"""
    ability_records = AbilityScore.objects.filter(user=user)
    if course_id:
        course_ability = ability_records.filter(course_id=course_id).first()
        ability_score = course_ability or ability_records.first()
    else:
        ability_score = ability_records.first()
    if ability_score and isinstance(ability_score.scores, dict):
        return ability_score.scores
    return {}


# 维护意图：序列化学习习惯偏好，兼容扩展 preferences 字段
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_habit_preferences(habit_preference: HabitPreference | None) -> dict[str, object]:
    """序列化学习习惯偏好，兼容扩展 preferences 字段。"""
    if habit_preference is None:
        return {}
    return {
        "preferred_resource": habit_preference.preferred_resource,
        "preferred_study_time": habit_preference.preferred_study_time,
        "study_pace": habit_preference.study_pace,
        "study_duration": habit_preference.study_duration,
        "review_frequency": habit_preference.review_frequency,
        "learning_style": habit_preference.learning_style,
        "accept_challenge": habit_preference.accept_challenge,
        "daily_goal_minutes": habit_preference.daily_goal_minutes,
        "weekly_goal_days": habit_preference.weekly_goal_days,
        **(habit_preference.preferences if isinstance(habit_preference.preferences, dict) else {}),
    }


# 维护意图：根据能力评分和学习偏好生成学习者标签
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_learner_tags(
    ability_scores: dict[str, object],
    habit_preference: HabitPreference | None,
) -> list[str]:
    """根据能力评分和学习偏好生成学习者标签。"""
    learner_tags = ability_tags(ability_scores)
    if habit_preference is None:
        return learner_tags
    learner_tags.extend(habit_resource_tags(habit_preference))
    learner_tags.extend(habit_time_and_pace_tags(habit_preference))
    return learner_tags


# 维护意图：根据最高能力维度生成学习者标签
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def ability_tags(ability_scores: dict[str, object]) -> list[str]:
    """根据最高能力维度生成学习者标签。"""
    if not ability_scores:
        return []
    try:
        sorted_abilities = sorted(
            ability_scores.items(),
            key=lambda item: float(item[1]) if item[1] is not None else 0,
            reverse=True,
        )
    except (TypeError, ValueError):
        return []
    if not sorted_abilities:
        return []
    ability_name_map = {
        "言语理解": "言语型",
        "知觉推理": "推理型",
        "工作记忆": "记忆型",
        "处理速度": "高效型",
        "logical_reasoning": "逻辑型",
        "memory": "记忆型",
        "analysis": "分析型",
        "innovation": "创新型",
        "comprehension": "理解型",
        "application": "实践型",
    }
    top_key = sorted_abilities[0][0]
    return [ability_name_map.get(top_key, "全能型") + "学习者"]


# 维护意图：根据资源偏好生成标签
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def habit_resource_tags(habit_preference: HabitPreference) -> list[str]:
    """根据资源偏好生成标签。"""
    if habit_preference.preferred_resource == "video":
        return ["视觉型"]
    if habit_preference.preferred_resource in ("text", "document"):
        return ["阅读型"]
    if habit_preference.preferred_resource == "exercise":
        return ["实践型"]
    return []


# 维护意图：根据学习时间与节奏生成标签
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def habit_time_and_pace_tags(habit_preference: HabitPreference) -> list[str]:
    """根据学习时间与节奏生成标签。"""
    learner_tags: list[str] = []
    if habit_preference.preferred_study_time == "evening":
        learner_tags.append("晚间学习")
    elif habit_preference.preferred_study_time:
        learner_tags.append("日间学习")
    if habit_preference.study_pace:
        learner_tags.append(
            {
                "fast": "快节奏",
                "moderate": "中节奏",
                "slow": "慢节奏",
                "adaptive": "自适应",
            }.get(habit_preference.study_pace, "中节奏")
        )
    return learner_tags


# 维护意图：读取学生画像摘要，并补齐空值
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_summary_payload(user: User, course_id: object | None) -> dict[str, object]:
    """读取学生画像摘要，并补齐空值。"""
    summary_records = ProfileSummary.objects.filter(user=user)
    if course_id:
        summary_records = summary_records.filter(course_id=course_id)
    summary = summary_records.first()
    return {
        "profile_summary": summary.summary or "" if summary else "",
        "weakness": summary.weakness or "" if summary else "",
        "suggestion": summary.suggestion or "" if summary else "",
        "strength": getattr(summary, "strength", "") or "" if summary else "",
        "last_update": (summary.generated_at if summary else timezone.now()).isoformat(),
    }


# 维护意图：刷新学生画像，返回成功载荷或错误信息
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_refresh_payload(user: User, course_id: object) -> tuple[dict[str, object] | None, str | None]:
    """刷新学生画像，返回成功载荷或错误信息。"""
    from users.services import get_learner_profile_service

    profile_service = get_learner_profile_service(user)
    result = profile_service.generate_profile_for_course(course_id, force_refresh=True)
    if result.get("success"):
        return {
            "course_id": course_id,
            "summary": result.get("summary", ""),
            "weakness": result.get("weakness", ""),
            "suggestion": result.get("suggestion", ""),
            "strength": result.get("strength", []),
            "kt_enhanced": result.get("kt_enhanced", False),
        }, None
    return None, str(result.get("error", "未知错误"))


# 维护意图：解析画像历史条数限制
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_profile_history_limit(raw_limit: object) -> int:
    """解析画像历史条数限制。"""
    try:
        return min(max(1, int(raw_limit or 10)), 100)
    except (ValueError, TypeError):
        return 10


# 维护意图：读取画像历史列表
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_history_payload(user: User, course_id: object, limit: int) -> list[dict[str, object]]:
    """读取画像历史列表。"""
    history = ProfileHistory.objects.filter(
        user=user,
        course_id=course_id,
    ).order_by("-created_at")[:limit]
    return [
        {
            "id": profile_history.id,
            "knowledge_mastery": profile_history.knowledge_mastery,
            "ability_scores": profile_history.ability_scores,
            "update_reason": profile_history.update_reason,
            "created_at": profile_history.created_at.isoformat(),
        }
        for profile_history in history
    ]


# 维护意图：将画像摘要对象转换为可序列化的快照数据
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def snapshot_profile_summary(summary_record: ProfileSummary | None) -> ProfileSnapshotPayload | None:
    """将画像摘要对象转换为可序列化的快照数据。"""
    if summary_record is None:
        return None
    return {
        "summary": summary_record.summary,
        "weakness": summary_record.weakness,
        "suggestion": summary_record.suggestion,
        "generated_at": summary_record.generated_at.isoformat() if summary_record.generated_at else None,
    }


# 维护意图：导出学习画像 JSON 响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_export_response(user: User) -> HttpResponse:
    """导出学习画像 JSON 响应。"""
    profile_data = {
        "user": user.username,
        "real_name": user.real_name,
        "knowledge_mastery": build_export_mastery_list(user),
        "ability_scores": build_export_ability_scores(user),
        "habit_preferences": build_export_habit_preferences(user),
    }
    response = HttpResponse(
        json.dumps(profile_data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="profile_{user.username}.json"'
    return response


# 维护意图：构造导出文件中的知识点掌握度列表
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_export_mastery_list(user: User) -> list[dict[str, object]]:
    """构造导出文件中的知识点掌握度列表。"""
    mastery_records = KnowledgeMastery.objects.filter(user=user).select_related("knowledge_point")
    return [
        {
            "knowledge_point": mastery.knowledge_point.name if mastery.knowledge_point else "",
            "mastery_rate": float(mastery.mastery_rate),
        }
        for mastery in mastery_records
    ]


# 维护意图：读取导出文件中的能力评分
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_export_ability_scores(user: User) -> dict[str, object]:
    """读取导出文件中的能力评分。"""
    ability = AbilityScore.objects.filter(user=user).first()
    return ability.scores if ability else {}


# 维护意图：读取导出文件中的学习偏好
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_export_habit_preferences(user: User) -> dict[str, object]:
    """读取导出文件中的学习偏好。"""
    habit_preference = HabitPreference.objects.filter(user=user).first()
    return HabitPreferenceSerializer(habit_preference).data if habit_preference else {}
