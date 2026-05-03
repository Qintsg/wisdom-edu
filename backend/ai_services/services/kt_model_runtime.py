"""
知识追踪模型运行混入模块。

本模块封装课程知识点加载和 MEFKT 运行时调用，
主服务类只负责配置与公开入口。
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from common.logging_utils import build_log_message


logger = logging.getLogger("ai_services.services.kt_service")


# 维护意图：提供本地模型推理、自动加载与可恢复异常降级
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KTModelRuntimeMixin:
    """提供本地模型推理、自动加载与可恢复异常降级。"""

    # 维护意图：加载课程知识点列表，供无历史记录时生成默认预测
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _load_course_knowledge_point_ids(self, course_id: int) -> List[int]:
        """加载课程知识点列表，供无历史记录时生成默认预测。"""
        if not course_id:
            return []

        try:
            from knowledge.models import KnowledgePoint

            return [
                int(point_id)
                for point_id in KnowledgePoint.objects.filter(course_id=course_id)
                .order_by("id")
                .values_list("id", flat=True)
            ]
        except Exception as error:
            logger.warning(
                build_log_message(
                    "kt.course_points.load_fail",
                    course_id=course_id,
                    error=error,
                )
            )
            return []

    # 维护意图：执行单个模型预测，并在可恢复的模型异常下返回空结果
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _run_model_prediction(
        self,
        model_type: str,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Optional[Dict[str, Any]]:
        """执行单个模型预测，并在可恢复的模型异常下返回空结果。"""
        predict_methods: Dict[
            str,
            Callable[[int, List[Dict[str, Any]], Optional[List[int]]], Dict[str, Any]],
        ] = {
            "mefkt": self._predict_with_mefkt,
        }
        predict_method = predict_methods.get(model_type)
        if predict_method is None:
            return None

        try:
            return predict_method(course_id, answer_history, knowledge_points)
        except (
            ImportError,
            NameError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            logger.warning(
                build_log_message(
                    "kt.model.predict_fail", model_type=model_type, error=error
                )
            )
            return None

    # 维护意图：优先使用 MEFKT 本地模型预测，失败时退回统计算法
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _predict_with_mefkt(
        self,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """优先使用 MEFKT 本地模型预测，失败时退回统计算法。"""
        answer_count = len(answer_history)

        try:
            from ai_services.services.mefkt_inference import (
                auto_load_model,
                mefkt_predictor,
            )

            if not mefkt_predictor.is_loaded:
                auto_load_model()

            if mefkt_predictor.is_loaded:
                result = mefkt_predictor.predict(
                    answer_history,
                    knowledge_points,
                    course_id=course_id,
                )
                logger.debug(
                    build_log_message(
                        "kt.mefkt.inference_ok",
                        answer_count=answer_count,
                        prediction_count=len(result.get("predictions", {})),
                    )
                )
                return result
            logger.debug("MEFKT 模型未加载，使用统计算法降级")
        except (
            ImportError,
            NameError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            logger.warning(
                build_log_message(
                    "kt.mefkt.inference_fail", answer_count=answer_count, error=error
                )
            )

        predictions = self._calculate_point_mastery(answer_history, knowledge_points)
        return {
            "predictions": predictions,
            "confidence": self._estimate_stat_confidence(
                answer_history, floor=0.4, ceiling=0.84
            ),
            "model_type": "mefkt",
            "analysis": f"MEFKT降级：基于{answer_count}条答题记录的统计推断",
        }
