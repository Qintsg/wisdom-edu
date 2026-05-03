"""
知识追踪统计工具混入模块。

本模块保留 KT 服务原有统计回退、默认预测与输入整理逻辑，
供主服务类以 mixin 方式复用，避免服务入口文件继续膨胀。
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional


# 维护意图：提供 KT 预测结果整理与内置统计算法
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KTPredictionStatsMixin:
    """提供 KT 预测结果整理与内置统计算法。"""

    # 维护意图：为所有预测模式补齐统一元数据
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _attach_prediction_metadata(
        self,
        result: Optional[Dict[str, Any]],
        answer_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """为所有预测模式补齐统一元数据。"""
        payload = dict(result or {})
        payload.setdefault("predictions", {})
        payload.setdefault("confidence", 0.0)
        payload.setdefault("model_type", "unknown")
        payload["answer_count"] = len(answer_history or [])
        payload["knowledge_point_count"] = len(
            {
                record.get("knowledge_point_id")
                for record in (answer_history or [])
                if record.get("knowledge_point_id")
            }
        )
        return payload

    # 维护意图：根据样本量和覆盖面估计统计回退的可信度
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _estimate_stat_confidence(
        self,
        answer_history: List[Dict[str, Any]],
        floor: float = 0.45,
        ceiling: float = 0.88,
    ) -> float:
        """根据样本量和覆盖面估计统计回退的可信度。"""
        total_answers = len(answer_history or [])
        unique_points = len(
            {
                record.get("knowledge_point_id")
                for record in (answer_history or [])
                if record.get("knowledge_point_id")
            }
        )
        if total_answers <= 0:
            return 0.0

        sample_factor = min(total_answers / 18.0, 1.0)
        coverage_factor = min(unique_points / 6.0, 1.0)
        confidence = floor + sample_factor * 0.28 + coverage_factor * 0.1
        return round(min(ceiling, confidence), 3)

    # 维护意图：从模型结果中提取可参与融合的知识点掌握度字典
    # 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    @staticmethod
    def _extract_prediction_map(
        result: Optional[Dict[str, Any]],
    ) -> Dict[int, float]:
        """从模型结果中提取可参与融合的知识点掌握度字典。"""
        if not isinstance(result, dict):
            return {}

        raw_predictions = result.get("predictions")
        if not isinstance(raw_predictions, dict):
            return {}

        normalized_predictions: Dict[int, float] = {}
        for raw_point_id, raw_mastery in raw_predictions.items():
            try:
                normalized_predictions[int(raw_point_id)] = round(float(raw_mastery), 4)
            except (TypeError, ValueError):
                continue

        return normalized_predictions

    # 维护意图：将批量请求中的标识值安全转换为整数
    # 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    @staticmethod
    def _coerce_int_identifier(value: object, default: int = 0) -> int:
        """将批量请求中的标识值安全转换为整数。"""
        if isinstance(value, bool):
            return default

        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # 维护意图：基于答题历史计算知识点掌握度。
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _calculate_point_mastery(
        self,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[int, float]:
        """
        基于答题历史计算知识点掌握度。

        使用加权平均算法，近期答题权重更高；缺失目标知识点时返回低置信默认值。
        """
        point_stats = defaultdict(
            lambda: {
                "correct": 0,
                "total": 0,
                "weighted_sum": 0.0,
                "weight_total": 0.0,
                "recent_correct": 0,
                "recent_total": 0,
            }
        )

        answer_count = len(answer_history)
        decay_factor = 0.9
        prior_mean = 0.25
        prior_strength = 4.0

        for index, record in enumerate(answer_history):
            point_id = record.get("knowledge_point_id", 0)
            correct = record.get("correct", 0)
            if not point_id:
                continue

            weight = decay_factor ** (answer_count - 1 - index)
            point_stats[point_id]["total"] += 1
            point_stats[point_id]["correct"] += correct
            point_stats[point_id]["weighted_sum"] += correct * weight
            point_stats[point_id]["weight_total"] += weight
            if index >= max(0, answer_count - 6):
                point_stats[point_id]["recent_correct"] += correct
                point_stats[point_id]["recent_total"] += 1

        predictions = {}
        for point_id, stats in point_stats.items():
            if stats["total"] <= 0:
                predictions[point_id] = round(prior_mean, 4)
                continue

            weighted_accuracy = (
                stats["weighted_sum"] + prior_mean * prior_strength
            ) / (stats["weight_total"] + prior_strength)
            simple_accuracy = stats["correct"] / stats["total"]
            recent_accuracy = (
                stats["recent_correct"] / stats["recent_total"]
                if stats["recent_total"] > 0
                else simple_accuracy
            )
            sample_factor = min(stats["total"] / 6.0, 1.0)
            blended = (
                weighted_accuracy * 0.55
                + simple_accuracy * 0.25
                + recent_accuracy * 0.20
            )
            mastery = prior_mean * (1 - sample_factor) + blended * sample_factor
            predictions[point_id] = round(max(0.0, min(0.9, mastery)), 4)

        if knowledge_points:
            for point_id in knowledge_points:
                if point_id not in predictions:
                    predictions[point_id] = round(prior_mean, 4)

        return predictions

    # 维护意图：准备模型输入数据，保留历史融合模式兼容格式
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @staticmethod
    def _prepare_input_data(
        answer_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """准备模型输入数据，保留历史融合模式兼容格式。"""
        num_questions = len(answer_history)
        question_ids = [answer.get("question_id", 0) for answer in answer_history]
        correct_flags = [answer.get("correct", 0) for answer in answer_history]
        knowledge_point_ids = [
            answer.get("knowledge_point_id", 0) for answer in answer_history
        ]
        timestamps = [answer.get("timestamp") for answer in answer_history]

        return {
            "num_questions": num_questions,
            "question_ids": question_ids,
            "correct_flags": correct_flags,
            "knowledge_point_ids": knowledge_point_ids,
            "timestamps": timestamps,
        }

    # 维护意图：返回无答题记录时的默认预测结果
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _get_default_prediction(
        self, knowledge_points: List[int] = None
    ) -> Dict[str, Any]:
        """返回无答题记录时的默认预测结果。"""
        predictions = {}
        if knowledge_points:
            for point_id in knowledge_points:
                predictions[point_id] = 0.25

        return {
            "predictions": predictions,
            "confidence": 0.0,
            "model_type": "default",
            "analysis": "无答题记录，返回默认预测值",
        }
