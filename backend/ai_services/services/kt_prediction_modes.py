"""
知识追踪预测模式混入模块。

本模块封装 single / ensemble / fusion / builtin 预测策略，
保持公开响应结构不变。
"""

import logging
from typing import Any, Dict, List, Optional

from common.logging_utils import build_log_message

from ai_services.services.kt_prediction_stats import KTPredictionStatsMixin


logger = logging.getLogger("ai_services.services.kt_service")


class KTPredictionModeMixin(KTPredictionStatsMixin):
    """提供 KT 公开预测入口、融合策略与学习建议生成。"""

    def predict_mastery(
        self,
        user_id: int,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: List[int] = None,
    ) -> Dict[str, Any]:
        """根据配置模式预测学生对知识点的掌握程度。"""
        if not answer_history:
            logger.warning(
                build_log_message(
                    "kt.predict.no_history", user_id=user_id, course_id=course_id
                )
            )
            resolved_points = knowledge_points or self._load_course_knowledge_point_ids(
                course_id
            )
            default_result = self._get_default_prediction(resolved_points)
            if resolved_points and not knowledge_points:
                default_result["analysis"] = "无答题记录，返回课程知识点默认预测值"
            elif not default_result.get("predictions"):
                default_result["analysis"] = "无答题记录，且当前课程暂无可预测知识点"
            return self._attach_prediction_metadata(default_result, answer_history)

        try:
            if self.prediction_mode == "single":
                result = self._single_model_predict(
                    user_id, course_id, answer_history, knowledge_points
                )
            elif self.prediction_mode == "ensemble":
                result = self._ensemble_predict(
                    user_id, course_id, answer_history, knowledge_points
                )
            else:
                result = self._fusion_predict(
                    user_id, course_id, answer_history, knowledge_points
                )
            return self._attach_prediction_metadata(result, answer_history)
        except Exception as error:
            logger.error(
                build_log_message(
                    "kt.predict.fail", user_id=user_id, course_id=course_id, error=error
                )
            )
            result = self._builtin_prediction(
                user_id, course_id, answer_history, knowledge_points
            )
            return self._attach_prediction_metadata(result, answer_history)

    def _single_model_predict(
        self,
        _user_id: int,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """仅使用一个启用模型预测，模型不可用时降级到内置算法。"""
        if not self.enabled_models:
            return self._builtin_prediction(
                _user_id, course_id, answer_history, knowledge_points
            )

        model_type = self.enabled_models[0]
        num_questions = len(answer_history)
        result = self._run_model_prediction(
            model_type=model_type,
            course_id=course_id,
            answer_history=answer_history,
            knowledge_points=knowledge_points,
        )
        if result is not None:
            result["prediction_mode"] = "single"
            result["active_models"] = [model_type]
            result["analysis"] = (
                f"使用{model_type.upper()}模型分析了{num_questions}次答题记录"
            )
            return result

        return self._builtin_prediction(
            _user_id, course_id, answer_history, knowledge_points
        )

    def _ensemble_predict(
        self,
        _user_id: int,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """调用所有启用模型并返回各模型独立结果，不做融合。"""
        model_results = {}
        num_questions = len(answer_history)

        for model_type in self.enabled_models:
            model_results[model_type] = self._run_model_prediction(
                model_type=model_type,
                course_id=course_id,
                answer_history=answer_history,
                knowledge_points=knowledge_points,
            )

        active_models = [key for key, value in model_results.items() if value is not None]
        valid_models = [model for model in model_results.values() if model is not None]
        if valid_models:
            avg_confidence = sum(
                model.get("confidence", 0.6) for model in valid_models
            ) / len(valid_models)
        else:
            avg_confidence = 0.5

        main_predictions = {}
        for model_type in active_models:
            if model_results[model_type]:
                main_predictions = self._extract_prediction_map(
                    model_results[model_type]
                )
                break

        model_names = (
            ", ".join([str(model).upper() for model in active_models])
            if active_models
            else "无"
        )

        return {
            "predictions": main_predictions,
            "model_results": {
                key: value for key, value in model_results.items() if value is not None
            },
            "confidence": round(avg_confidence, 3),
            "model_type": "ensemble",
            "prediction_mode": "ensemble",
            "active_models": active_models,
            "analysis": f"集成{len(active_models)}个模型（{model_names}）分析了{num_questions}次答题记录（各模型独立预测）",
        }

    def _fusion_predict(
        self,
        _user_id: int,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """调用所有启用模型，并按配置权重融合预测结果。"""
        model_results = {}
        num_questions = len(answer_history)

        for model_type in self.enabled_models:
            model_results[model_type] = self._run_model_prediction(
                model_type=model_type,
                course_id=course_id,
                answer_history=answer_history,
                knowledge_points=knowledge_points,
            )

        fused_predictions = self._fuse_predictions(model_results)
        valid_models = [model for model in model_results.values() if model is not None]
        if valid_models:
            avg_confidence = sum(
                model.get("confidence", 0.6) for model in valid_models
            ) / len(valid_models)
        else:
            avg_confidence = 0.5

        active_models = [key for key, value in model_results.items() if value is not None]
        model_names = (
            ", ".join([str(model).upper() for model in active_models])
            if active_models
            else "无"
        )

        return {
            "predictions": fused_predictions,
            "model_results": {
                key: value for key, value in model_results.items() if value is not None
            },
            "fusion_weights": self.fusion_weights,
            "confidence": round(avg_confidence, 3),
            "model_type": "fusion",
            "prediction_mode": "fusion",
            "active_models": active_models,
            "analysis": f"融合{len(active_models)}个模型（{model_names}）分析了{num_questions}次答题记录",
        }

    def _fuse_predictions(
        self, model_results: Dict[str, Optional[Dict[str, Any]]]
    ) -> Dict[int, float]:
        """使用加权平均融合各模型的知识点预测结果。"""
        all_points = set()
        for result in model_results.values():
            all_points.update(self._extract_prediction_map(result).keys())

        fused = {}
        for point_id in all_points:
            weighted_sum = 0.0
            weight_sum = 0.0

            for model_type, result in model_results.items():
                predictions = self._extract_prediction_map(result)
                if point_id in predictions:
                    weight = self.fusion_weights.get(model_type, 0)
                    weighted_sum += predictions[point_id] * weight
                    weight_sum += weight

            if weight_sum > 0:
                fused[point_id] = round(weighted_sum / weight_sum, 4)
            else:
                fused[point_id] = 0.5

        return fused

    def _builtin_prediction(
        self,
        _user_id: int,
        _course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """使用内置统计算法进行掌握度预测。"""
        predictions = self._calculate_point_mastery(answer_history, knowledge_points)
        return {
            "predictions": predictions,
            "confidence": self._estimate_stat_confidence(
                answer_history, floor=0.35, ceiling=0.76
            ),
            "model_type": "builtin",
            "analysis": "使用内置统计算法进行掌握度分析",
        }

    def batch_predict(
        self, user_histories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量预测多个用户的掌握度。"""
        results = []
        for user_data in user_histories:
            user_id = self._coerce_int_identifier(user_data.get("user_id"))
            course_id = self._coerce_int_identifier(user_data.get("course_id"))
            answer_history = user_data.get("answer_history", [])
            knowledge_points = user_data.get("knowledge_points")
            result = self.predict_mastery(
                user_id=user_id,
                course_id=course_id,
                answer_history=answer_history if isinstance(answer_history, list) else [],
                knowledge_points=knowledge_points if isinstance(knowledge_points, list) else None,
            )
            result["user_id"] = user_id
            results.append(result)

        return results

    def get_learning_recommendations(
        self,
        _user_id: int,
        _course_id: int,
        mastery_predictions: Dict[int, float],
        threshold: float = 0.6,
    ) -> List[Dict[str, Any]]:
        """基于掌握度预测生成学习建议列表。"""
        recommendations = []
        weak_points = [
            (point_id, mastery)
            for point_id, mastery in mastery_predictions.items()
            if mastery < threshold
        ]

        weak_points.sort(key=lambda pair: pair[1])

        for point_id, mastery in weak_points:
            priority = "high" if mastery < 0.4 else "medium"
            recommendations.append(
                {
                    "knowledge_point_id": point_id,
                    "current_mastery": mastery,
                    "target_mastery": threshold,
                    "priority": priority,
                    "suggestion": f"建议加强学习，当前掌握度 {mastery * 100:.1f}%",
                }
            )

        return recommendations
