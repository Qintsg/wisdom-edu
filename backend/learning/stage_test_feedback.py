"""阶段测试反馈报告生成与兜底规整。"""

from __future__ import annotations

import logging

from common.logging_utils import build_log_message
from learning.models import PathNode
from learning.stage_test_models import StageTestEvaluation, TOTAL_SCORE
from users.models import User


logger = logging.getLogger(__name__)


# 维护意图：调用 LLM 生成阶段测试反馈，失败时返回本地兜底报告
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_feedback_report(
    node: PathNode,
    user: User,
    evaluation: StageTestEvaluation,
) -> dict[str, object]:
    """调用 LLM 生成阶段测试反馈，失败时返回本地兜底报告。"""
    try:
        from ai_services.services import llm_service

        # 阶段测试反馈属于智能增强链路，LLM 不可用时必须保留本地报告。
        llm_feedback = llm_service.generate_feedback_report(
            exam_info={"title": node.title, "type": "阶段测试"},
            score=evaluation.score,
            total_score=TOTAL_SCORE,
            mistakes=evaluation.detailed_mistakes,
        )
        return normalize_feedback_report(llm_feedback)
    except (ImportError, RuntimeError, TypeError, ValueError) as exc:
        logger.error(
            build_log_message(
                "llm.stage_test.fail",
                user_id=user.id,
                node_id=node.id,
                error=exc,
            )
        )
        return fallback_feedback_report(evaluation.point_stats)


# 维护意图：规整 LLM 反馈字段，保持前端响应结构稳定
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_feedback_report(llm_feedback: dict[str, object]) -> dict[str, object]:
    """规整 LLM 反馈字段，保持前端响应结构稳定。"""
    summary = llm_field(llm_feedback, "summary", "")
    analysis_value = llm_field(llm_feedback, "analysis", "")
    knowledge_gaps = llm_field(llm_feedback, "knowledge_gaps", [])
    recommendations = llm_field(llm_feedback, "recommendations", [])
    next_tasks = llm_field(llm_feedback, "next_tasks", [])
    conclusion = llm_field(llm_feedback, "conclusion", "") or llm_field(llm_feedback, "encouragement", "")
    if not summary and isinstance(analysis_value, str):
        summary = analysis_value
    feedback_report = {
        "summary": summary,
        "analysis": analysis_value if isinstance(analysis_value, str) else "",
        "knowledge_gaps": knowledge_gaps if isinstance(knowledge_gaps, list) else [],
        "recommendations": recommendations if isinstance(recommendations, list) else [],
        "next_tasks": next_tasks if isinstance(next_tasks, list) else [],
        "conclusion": conclusion,
    }
    if feedback_report["analysis"] == feedback_report["summary"]:
        feedback_report["analysis"] = ""
    return feedback_report


# 维护意图：读取 LLM 字段并集中表达默认值，避免字段缺失影响报告结构
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def llm_field(llm_feedback: dict[str, object], field_name: str, default_value: object) -> object:
    """读取 LLM 字段并集中表达默认值，避免字段缺失影响报告结构。"""
    return llm_feedback.get(field_name, default_value)


# 维护意图：LLM 失败时返回稳定的阶段测试反馈
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def fallback_feedback_report(
    point_stats: dict[int, dict[str, object]],
) -> dict[str, object]:
    """LLM 失败时返回稳定的阶段测试反馈。"""
    return {
        "summary": "系统已根据你的答题情况生成阶段测试结果，建议结合错题和薄弱知识点继续巩固。",
        "analysis": "系统已根据你的答题情况生成阶段测试结果，建议结合错题和薄弱知识点继续巩固。",
        "knowledge_gaps": [stats["name"] for _, stats in list(point_stats.items())[:3]],
        "recommendations": [
            "复习错题涉及知识点",
            "结合学习资源再次梳理重点概念",
            "完成后重新尝试阶段测试",
        ],
        "next_tasks": ["回顾当前阶段对应的学习节点", "重做错题并记录原因"],
        "conclusion": "继续保持，修正薄弱点后你的成绩会更稳！",
    }
