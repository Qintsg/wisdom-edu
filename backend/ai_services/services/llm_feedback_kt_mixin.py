from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from common.logging_utils import build_log_message
from .llm_feedback_kt_support import (
    FeedbackReportInput,
    KTAnalysisInput,
    build_feedback_report_fallback,
    build_feedback_report_prompt,
    build_kt_analysis_fallback,
    build_kt_analysis_prompt,
)


logger = logging.getLogger(__name__)


class LLMFeedbackKTMixin:
    """作业反馈报告与知识追踪结果解释能力。"""

    def generate_feedback_report(
        self,
        exam_info: Mapping[str, object],
        score: float,
        total_score: float,
        mistakes: Sequence[Mapping[str, object]],
        kt_predictions: Mapping[object, object] | None = None,
    ) -> dict[str, object]:
        """
        生成考试反馈报告

        Args:
            exam_info: 考试信息
            score: 得分
            total_score: 总分
            mistakes: 错题列表
            kt_predictions: KT模型预测的知识点掌握度 {kp_id: mastery_rate}

        Returns:
            反馈报告
        """
        report_input = FeedbackReportInput(
            exam_info=exam_info,
            score=score,
            total_score=total_score,
            mistakes=mistakes,
            kt_predictions=kt_predictions,
        )
        fallback = build_feedback_report_fallback(report_input)

        from common.config import AppConfig

        if not AppConfig.ai_feedback_enabled():
            logger.debug(
                build_log_message(
                    "llm.feedback.disabled",
                    provider=self.provider_name,
                    model=self.model_name,
                )
            )
            return fallback

        return self._call_with_fallback(
            build_feedback_report_prompt(report_input),
            "feedback_report",
            fallback,
        )

    def analyze_knowledge_tracing_result(
        self,
        kt_result: Mapping[str, object],
        answer_history: Sequence[Mapping[str, object]] | None = None,
        course_name: str | None = None,
        point_name_map: Mapping[int, str] | None = None,
    ) -> dict[str, object]:
        """
        分析知识追踪结果，生成学习洞察报告

        基于 DKT 知识追踪模型的预测结果，生成深度学习分析报告。

        Args:
            kt_result: 知识追踪服务返回的预测结果字典
            answer_history: 答题历史记录列表
            course_name: 课程名称
            point_name_map: 知识点ID到名称的映射 {id: name}，用于将数字ID转换为可读名称

        Returns:
            dict: 包含学习洞察、趋势分析和改进建议的报告
        """
        analysis_input = KTAnalysisInput(
            kt_result=kt_result,
            answer_history=answer_history,
            course_name=course_name,
            point_name_map=point_name_map,
        )
        return self._call_with_fallback(
            build_kt_analysis_prompt(analysis_input),
            "kt_analysis",
            build_kt_analysis_fallback(analysis_input),
        )
