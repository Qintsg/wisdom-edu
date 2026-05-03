from __future__ import annotations

import json
from typing import Any


# 维护意图：构造画像分析的课程上下文段落
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_course_context(
    course_name: str | None,
    grade_level: str | None,
) -> str:
    """构造画像分析的课程上下文段落。"""
    if not course_name and not grade_level:
        return ""

    parts: list[str] = []
    if course_name:
        parts.append(f"课程：{course_name}")
    if grade_level:
        parts.append(f"学段：{grade_level}")
    return "\n## 课程信息\n" + "\n".join(f"- {part}" for part in parts) + "\n"


# 维护意图：将知识点掌握度列表压缩成适合 prompt 的行文本
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def format_mastery_lines(mastery_data: list[dict[str, Any]]) -> str:
    """将知识点掌握度列表压缩成适合 prompt 的行文本。"""
    return ", ".join(
        [
            f"{item.get('point_name', '未知')}({item.get('category', '')}): {float(item.get('mastery_rate') or 0) * 100:.0f}%"
            for item in mastery_data
        ]
    )


# 维护意图：汇总掌握度统计信息
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def summarize_mastery_distribution(mastery_data: list[dict[str, Any]]) -> tuple[int, float, int, int]:
    """汇总掌握度统计信息。"""
    total_points = len(mastery_data)
    if total_points <= 0:
        return 0, 0.0, 0, 0

    avg_mastery = (
        sum(float(item.get("mastery_rate") or 0) for item in mastery_data)
        / total_points
        * 100
    )
    weak_count = sum(1 for item in mastery_data if float(item.get("mastery_rate") or 0) < 0.6)
    strong_count = sum(1 for item in mastery_data if float(item.get("mastery_rate") or 0) >= 0.8)
    return total_points, avg_mastery, weak_count, strong_count


# 维护意图：识别薄弱知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def identify_weaknesses(mastery_data: list[dict[str, Any]]) -> list[str]:
    """识别薄弱知识点。"""
    return [
        item.get("point_name", "未知")
        for item in mastery_data
        if float(item.get("mastery_rate") or 0) < 0.6
    ][:3]


# 维护意图：识别优势知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def identify_strengths(mastery_data: list[dict[str, Any]]) -> list[str]:
    """识别优势知识点。"""
    return [
        item.get("point_name", "未知")
        for item in mastery_data
        if float(item.get("mastery_rate") or 0) >= 0.8
    ][:3]


# 维护意图：构造学习画像分析 prompt
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_prompt(
    *,
    mastery_data: list[dict[str, Any]],
    ability_data: dict[str, Any] | None,
    habit_data: dict[str, Any] | None,
    course_name: str | None,
    grade_level: str | None,
    kt_predictions: dict[str, Any] | None,
) -> str:
    """构造学习画像分析 prompt。"""
    total_points, avg_mastery, weak_count, strong_count = summarize_mastery_distribution(mastery_data)
    return f"""# 任务
基于学生的多维度学习数据，生成个性化学习画像分析报告。

# 输入数据
{build_profile_course_context(course_name, grade_level)}## 知识掌握情况（共{total_points}个知识点）
- 各知识点掌握率：{format_mastery_lines(mastery_data)}
- 整体平均掌握率：{avg_mastery:.1f}%
- 薄弱知识点数量：{weak_count}个（低于60%）
- 优势知识点数量：{strong_count}个（高于80%）

## 能力维度评分
{json.dumps(ability_data, ensure_ascii=False) if ability_data else "暂无能力测评数据"}

## 学习偏好特征
{json.dumps(habit_data, ensure_ascii=False) if habit_data else "暂无学习偏好数据"}

## 知识追踪模型预测
{json.dumps(kt_predictions, ensure_ascii=False, indent=2) if kt_predictions else "暂无KT模型预测数据（掌握度基于统计方法估算）"}

# JSON输出格式
{{
    "summary": "综合评价摘要，包含学习状态定性描述和核心特点（80-120字）",
    "weakness": ["需要重点加强的薄弱知识点或能力短板，最多3项"],
    "strength": ["学习优势和突出表现，最多3项"],
    "suggestion": "针对性的学习建议，包含具体的学习策略、资源推荐和时间规划（150-250字）"
}}

# 示例输出
{{
    "summary": "你在函数与递归方面掌握扎实（85%），但循环结构（42%）和数组操作（38%）较薄弱，整体处于中等偏上水平，需要针对性强化基础控制结构。",
    "weakness": ["循环结构的嵌套使用和边界条件处理", "数组的动态操作与遍历技巧"],
    "strength": ["函数定义与调用理解透彻", "递归思维和问题分解能力突出"],
    "suggestion": "建议先用2天时间集中复习循环结构，重点练习while/for循环的6种经典模式（如累加、查找、排序），每天完成5道练习题。然后用1天学习数组遍历和操作，配合可视化工具理解内存变化。最后做1套综合题检验效果。利用你擅长的函数思维，尝试将循环逻辑封装为函数来加深理解。"
}}

# 分析原则
1. 评价要客观公正，既肯定进步也指出不足
2. 建议要具体可执行，避免空泛的描述
3. 考虑学生的学习偏好，推荐适合的学习方式
4. 薄弱点和优势点要精准对应具体知识点"""


# 维护意图：构造学习画像分析降级返回
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_profile_fallback(mastery_data: list[dict[str, Any]]) -> dict[str, Any]:
    """构造学习画像分析降级返回。"""
    return {
        "summary": "基于你的测评数据，你在核心概念理解方面表现良好，但在应用能力上有提升空间。",
        "weakness": identify_weaknesses(mastery_data),
        "strength": identify_strengths(mastery_data),
        "suggestion": "建议多做练习题，加强实践应用能力。针对薄弱知识点进行专项突破。",
    }


# 维护意图：生成路径规划所需的掌握度摘要
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def summarize_path_strengths_and_weaknesses(
    mastery_data: list[dict[str, Any]],
) -> tuple[str, list[str], list[str]]:
    """生成路径规划所需的掌握度摘要。"""
    mastery_text = ", ".join(
        [
            f"{item.get('point_name', '未知')}: {float(item.get('mastery_rate') or 0) * 100:.0f}%"
            for item in mastery_data
        ]
    )
    weak_points = [
        item.get("point_name") or "未知知识点"
        for item in mastery_data
        if float(item.get("mastery_rate") or 0) < 0.6
    ]
    strong_points = [
        item.get("point_name") or "未知知识点"
        for item in mastery_data
        if float(item.get("mastery_rate") or 0) >= 0.8
    ]
    return mastery_text, weak_points, strong_points


# 维护意图：格式化路径规划约束说明
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_path_constraints_text(constraints: dict[str, Any] | None) -> str:
    """格式化路径规划约束说明。"""
    if not constraints:
        return "无特殊约束，按常规进度安排"
    if not constraints.get("refresh_mode"):
        return json.dumps(constraints, ensure_ascii=False)

    parts: list[str] = []
    completed = constraints.get("completed_nodes", [])
    if completed:
        completed_text = ", ".join(
            [
                f"{item['name']}({item['status']}/{item['mastery']})"
                for item in completed[:15]
            ]
        )
        parts.append(
            f"已完成/跳过的节点（共{len(completed)}个，已保留，不要重复规划）：{completed_text}"
        )
    parts.append(f"剩余待规划知识点数：{constraints.get('remaining_count', '?')}")
    parts.append(
        f"KT答题历史：{constraints.get('kt_answer_count', 0)}条，预测维度：{constraints.get('kt_prediction_count', 0)}"
    )
    if constraints.get("ability_scores"):
        score_text = ", ".join(
            [f"{key}: {value}" for key, value in constraints["ability_scores"].items()]
        )
        parts.append(f"能力评测（C-WAIS）：{score_text}")
    if constraints.get("learning_preferences"):
        preferences = constraints["learning_preferences"]
        parts.append(
            "学习偏好："
            f"资源类型={preferences.get('preferred_resource', '未知')}, "
            f"时间段={preferences.get('preferred_study_time', '未知')}, "
            f"节奏={preferences.get('study_pace', 'moderate')}"
        )
    if constraints.get("learner_profile"):
        parts.append(f"学习画像摘要：\n{constraints['learner_profile']}")
    return "\n".join(f"- {part}" for part in parts)


# 维护意图：构造学习路径规划 prompt
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_path_prompt(
    *,
    mastery_data: list[dict[str, Any]],
    target: str | None,
    constraints: dict[str, Any] | None,
    course_name: str | None,
    max_nodes: int,
) -> str:
    """构造学习路径规划 prompt。"""
    mastery_text, weak_points, strong_points = summarize_path_strengths_and_weaknesses(mastery_data)
    course_context = f"\n## 课程信息\n- 课程名称：{course_name}" if course_name else ""
    constraints_text = build_path_constraints_text(constraints)
    return f"""# 任务
基于学生的知识掌握情况，设计一条循序渐进的个性化学习路径（最多{max_nodes}个节点）。

# 学生当前状态{course_context}
## 知识点掌握详情
{mastery_text}

## 分析概要
- 薄弱知识点（<60%）：{", ".join(weak_points) if weak_points else "无明显薄弱点"}
- 优势知识点（≥80%）：{", ".join(strong_points) if strong_points else "暂无突出优势"}

## 学习目标
{target or "全面掌握课程核心知识，达到80%以上的整体掌握率"}

## 约束条件
{constraints_text}

# 规划原则
1. 先修原则：前置知识先学
2. 优先级原则：薄弱知识点优先
3. 递进原则：由浅入深
4. 巩固原则：适时安排复习

# JSON输出格式
{{
    "reason": "路径规划的核心思路和依据说明（80-120字）",
    "nodes": [
        {{
            "title": "学习节点标题",
            "goal": "该节点的具体学习目标，可量化",
            "priority": "high/medium/low",
            "estimated_hours": 2,
            "prerequisites": ["前置知识点名称"]
        }}
    ]
}}"""


# 维护意图：构造学习路径规划降级返回
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_path_fallback(mastery_data: list[dict[str, Any]]) -> dict[str, Any]:
    """构造学习路径规划降级返回。"""
    weak_point_list = [
        item
        for item in mastery_data
        if float(item.get("mastery_rate") or 0) < 0.6
    ]
    return {
        "reason": "基于你的学习画像，系统为你定制了循序渐进的学习路径，优先强化薄弱知识点，同时巩固已有优势。",
        "nodes": [
            {
                "title": f"{item.get('point_name', '基础知识')}强化",
                "goal": f"掌握{item.get('point_name', '相关知识')}的核心概念，达到70%以上掌握率",
                "priority": "high" if float(item.get("mastery_rate") or 0) < 0.4 else "medium",
                "estimated_hours": 2,
                "prerequisites": [],
            }
            for item in weak_point_list[:5]
        ]
        or [
            {
                "title": "综合提升",
                "goal": "巩固已学知识，提升应用能力",
                "priority": "medium",
                "estimated_hours": 3,
                "prerequisites": [],
            }
        ],
    }


# 维护意图：根据掌握度返回阶段标签和描述
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_learning_stage(student_mastery: float | None) -> tuple[str, str]:
    """根据掌握度返回阶段标签和描述。"""
    if student_mastery is None:
        return "初学", "刚开始学习该知识点"
    if student_mastery < 0.4:
        return "入门", "需要从基础概念开始学习"
    if student_mastery < 0.6:
        return "巩固", "需要加强理解和练习"
    if student_mastery < 0.8:
        return "提高", "可以进行进阶学习和应用"
    return "精通", "可以挑战高级内容和拓展知识"


# 维护意图：构造资源推荐理由 prompt
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_resource_reason_prompt(
    *,
    resource_info: dict[str, Any],
    student_mastery: float | None,
    point_name: str | None,
    course_name: str | None,
) -> str:
    """构造资源推荐理由 prompt。"""
    stage, stage_description = resolve_learning_stage(student_mastery)
    course_context = f"\n- 所属课程：{course_name}" if course_name else ""
    return f"""# 任务
为学生解释推荐此学习资源的原因，评估资源与学生当前学习状态的匹配度。

# 推荐资源信息
- 资源名称：{resource_info.get("title", "未知资源")}
- 资源类型：{resource_info.get("type", "未知类型")}
- 资源描述：{resource_info.get("description", "无描述")}

# 学生学习状态
- 相关知识点：{point_name or "通用知识"}{course_context}
- 当前掌握度：{f"{student_mastery * 100:.0f}%" if student_mastery is not None else "未评测"}
- 学习阶段：{stage}（{stage_description}）

# JSON输出格式
{{
    "reason": "个性化推荐理由，说明资源与学生状态的匹配点（40-60字）",
    "relevance_score": "<float, 0-1之间的匹配度评分，根据学生阶段和资源特点动态评估>",
    "learning_tips": "使用该资源的学习建议（30-50字）"
}}"""


# 维护意图：构造资源推荐理由降级返回
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_resource_reason_fallback(
    *,
    resource_info: dict[str, Any],
    student_mastery: float | None,
    point_name: str | None,
) -> dict[str, Any]:
    """构造资源推荐理由降级返回。"""
    stage, _ = resolve_learning_stage(student_mastery)
    relevance = (
        0.85
        if student_mastery is None
        else max(0.6, min(0.95, 0.9 - abs(student_mastery - 0.5)))
    )
    return {
        "reason": f"这个{resource_info.get('type', '资源')}能够帮助你更好地理解{point_name or '相关概念'}，适合当前{stage}阶段学习。",
        "relevance_score": round(relevance, 2),
        "learning_tips": "建议结合笔记进行学习，完成后进行相关练习巩固。",
    }
