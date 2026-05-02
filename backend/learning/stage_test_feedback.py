"""阶段测试反馈报告生成与兜底规整。"""

from __future__ import annotations

import logging

from common.logging_utils import build_log_message
from learning.models import PathNode
from learning.stage_test_models import StageTestEvaluation, TOTAL_SCORE
from users.models import User


logger = logging.getLogger(__name__)


def build_feedback_report(
    node: PathNode,
    user: User,
    evaluation: StageTestEvaluation,
) -> dict[str, object]:
    """调用 LLM 生成阶段测试反馈，失败时返回本地兜底报告。"""
    try:
        from ai_services.services import llm_service as _llm

        llm_feedback = _llm.generate_feedback_report(
            exam_info={"title": node.title, "type": "阶段测试"},
            score=evaluation.score,
            total_score=TOTAL_SCORE,
            mistakes=evaluation.detailed_mistakes,
        )
        return _normalize_feedback_report(llm_feedback)
    except Exception as exc:
        logger.error(
            build_log_message(
                "llm.stage_test.fail",
                user_id=user.id,
                node_id=node.id,
                error=exc,
            )
        )
        return fallback_feedback_report(evaluation.point_stats)


def _normalize_feedback_report(llm_feedback: dict[str, object]) -> dict[str, object]:
    """规整 LLM 反馈字段，保持前端响应结构稳定。"""
    summary = llm_feedback.get("summary", "")
    if not summary and isinstance(llm_feedback.get("analysis"), str):
        summary = llm_feedback.get("analysis", "")
    feedback_report = {
        "summary": summary,
        "analysis": llm_feedback.get("analysis", "")
        if isinstance(llm_feedback.get("analysis"), str)
        else "",
        "knowledge_gaps": llm_feedback.get("knowledge_gaps", [])
        if isinstance(llm_feedback.get("knowledge_gaps"), list)
        else [],
        "recommendations": llm_feedback.get("recommendations", [])
        if isinstance(llm_feedback.get("recommendations"), list)
        else [],
        "next_tasks": llm_feedback.get("next_tasks", [])
        if isinstance(llm_feedback.get("next_tasks"), list)
        else [],
        "conclusion": llm_feedback.get("conclusion", "")
        or llm_feedback.get("encouragement", ""),
    }
    if feedback_report["analysis"] == feedback_report["summary"]:
        feedback_report["analysis"] = ""
    return feedback_report


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
