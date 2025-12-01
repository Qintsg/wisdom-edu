"""
知识追踪服务模块 (Knowledge Tracing Service)

本模块封装了 DKT / MEFKT 深度知识追踪模型，支持多种预测模式：
- fusion: 融合模式（支持 DKT 与 MEFKT）
- single: 单模型模式
- ensemble: 集成模式

模型架构: RNN(tanh) → Linear → Sigmoid
模型来源: https://github.com/pydaxing/Deep-Knowledge-Tracing-DKT-Pytorch

使用示例:
    from ai_services.services import kt_service

    predictions = kt_service.predict_mastery(
        user_id=1,
        course_id=1,
        answer_history=[
            {'question_id': 1, 'correct': 1, 'knowledge_point_id': 10},
            {'question_id': 2, 'correct': 0, 'knowledge_point_id': 11}
        ]
    )
    返回结果示例:
        {
            'predictions': {10: 0.75, 11: 0.35},
            'confidence': 0.85,
            'model_type': 'dkt' | 'mefkt' | 'fusion' | 'builtin',
            'analysis': '...'
        }

作者: 自适应学习系统团队
"""

import logging
import os
import json
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
from common.logging_utils import build_log_message

logger = logging.getLogger(__name__)
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_backend_path(path_value: str | None) -> str:
    """将配置中的相对模型路径统一解析为后端根目录下的绝对路径。"""
    if path_value is None:
        return ""
    normalized = str(path_value).strip()
    if not normalized:
        return ""
    candidate = Path(normalized)
    if candidate.is_absolute():
        return str(candidate)
    return str((BACKEND_ROOT / candidate).resolve())


class KnowledgeTracingService:
    """
    知识追踪服务类

    提供基于深度学习的知识追踪能力，用于预测学生对知识点的掌握程度。
    当前支持 DKT 与 MEFKT 模型，保留多模型融合框架以便未来扩展。

    属性:
        fusion_weights: 模型融合权重 {'dkt': 1.0, 'mefkt': 0.0}
        model_paths: 各模型文件路径
        is_available: 服务是否可用
    """

    MODEL_CONFIGS = {
        "dkt": {
            "name": "Deep Knowledge Tracing",
            "description": "基于RNN(tanh)的深度知识追踪模型，支持本地推理",
            "github": "https://github.com/pydaxing/Deep-Knowledge-Tracing-DKT-Pytorch",
            "input_format": "三行格式：答题数/题目编号/答题结果(0或1)",
            "requires": ["torch", "numpy"],
            "default_weight": 0.5,
        },
        "mefkt": {
            "name": "Multi-view Exercise Fusion KT",
            "description": "融合结构视角、属性视角与遗忘机制的知识追踪模型，支持公开预训练 + 题目级在线部署",
            "paper_title": "融合多视角习题表征与遗忘机制的深度知识追踪",
            "paper_doi": "10.11896/jsjkx.250700092",
            "requires": ["torch", "numpy", "scikit-learn"],
            "default_weight": 0.5,
        },
    }

    DEFAULT_FUSION_WEIGHTS = {
        "dkt": 0.5,
        "mefkt": 0.5,
    }

    def __init__(
        self,
        model_paths: Dict[str, str] = None,
        fusion_weights: Dict[str, float] = None,
        use_gpu: bool = False,
        prediction_mode: str = None,
        enabled_models: List[str] = None,
    ):
        """
        初始化知识追踪服务

        支持三种预测模式：
        - 'fusion': 融合模式，同时使用多个模型并加权融合结果（默认）
        - 'single': 单模型模式，仅使用指定的单个模型
        - 'ensemble': 集成模式，使用多个模型但不融合，返回各模型独立结果

        注意：在单模型模式下，如果提供了多个模型，服务将只使用列表中的第一个模型，
        并记录警告日志。其他模型配置会被忽略但不会抛出异常。

        Args:
            model_paths: 各模型的文件路径 {'dkt': '/path/to/dkt'}
            fusion_weights: 融合权重 {'dkt': 1.0}，权重总和应为1.0
            use_gpu: 是否使用GPU加速
            prediction_mode: 预测模式，可选 'fusion'（融合）, 'single'（单模型）, 'ensemble'（集成）
            enabled_models: 启用的模型列表，如 ['dkt']。为None时启用默认有效模型。
                           单模型模式下仅使用第一个模型。
        """
        default_dkt_model_root = Path(__file__).resolve().parent.parent.parent / "models" / "DKT"
        default_mefkt_model_root = Path(__file__).resolve().parent.parent.parent / "models" / "MEFKT"
        raw_model_paths = model_paths or {
            "dkt": os.getenv("KT_DKT_MODEL_PATH", str(default_dkt_model_root / "dkt_model.pt")),
            "mefkt": os.getenv("KT_MEFKT_MODEL_PATH", str(default_mefkt_model_root / "mefkt_model.pt")),
        }
        self.model_paths = {
            model_type: _resolve_backend_path(model_path)
            for model_type, model_path in raw_model_paths.items()
        }

        self.fusion_weights = fusion_weights or self._load_fusion_weights()
        self._normalize_weights()

        self.use_gpu = use_gpu and os.getenv("KT_USE_GPU", "false").lower() == "true"

        valid_modes = ["fusion", "single", "ensemble"]
        env_mode = os.getenv("KT_PREDICTION_MODE", "fusion").lower()
        self.prediction_mode = prediction_mode or (
            env_mode if env_mode in valid_modes else "fusion"
        )

        if enabled_models is not None:
            configured_models = [
                m.lower() for m in enabled_models if m.lower() in self.MODEL_CONFIGS
            ]
        else:
            env_models = os.getenv("KT_ENABLED_MODELS", "")
            if env_models:
                configured_models = [
                    m.strip().lower()
                    for m in env_models.split(",")
                    if m.strip().lower() in self.MODEL_CONFIGS
                ]
            else:
                configured_models = ["dkt", "mefkt"]

        # 若过滤后为空，回退到默认有效模型
        if not configured_models:
            configured_models = ["dkt"]

        # 单模型模式下，确保只有一个模型被启用
        # 保存原始配置以供调试参考
        self._configured_models = configured_models.copy()
        if self.prediction_mode == "single" and len(configured_models) > 1:
            self.enabled_models = [configured_models[0]]
            logger.warning(
                build_log_message(
                    "kt.mode.single_truncated",
                    selected_model=self.enabled_models[0],
                    configured_models=configured_models,
                )
            )
        else:
            self.enabled_models = configured_models

        self._models = {}
        self._is_available = None

        mode_name = {"fusion": "融合", "single": "单模型", "ensemble": "集成"}.get(
            self.prediction_mode, "融合"
        )
        logger.debug(
            build_log_message(
                "kt.service.ready",
                prediction_mode=mode_name,
                enabled_models=self.enabled_models,
                fusion_weights=self.fusion_weights,
            )
        )

    def _load_fusion_weights(self) -> Dict[str, float]:
        """
        从环境变量加载融合权重

        Returns:
            融合权重字典
        """
        try:
            weights_str = os.getenv("KT_FUSION_WEIGHTS", "")
            if weights_str:
                weights = json.loads(weights_str)
                # 过滤掉已下线的模型权重
                return {k: v for k, v in weights.items() if k in self.MODEL_CONFIGS}
        except json.JSONDecodeError:
            logger.warning(
                build_log_message(
                    "kt.weights.invalid", detail="融合权重配置格式错误，使用默认权重"
                )
            )
        return self.DEFAULT_FUSION_WEIGHTS.copy()

    def _normalize_weights(self):
        """
        归一化融合权重，确保总和为1.0

        如果权重总和为0，使用默认权重
        """
        self.fusion_weights = {
            k: v for k, v in self.fusion_weights.items() if k in self.MODEL_CONFIGS
        }
        total = sum(self.fusion_weights.values())
        if total == 0:
            self.fusion_weights = self.DEFAULT_FUSION_WEIGHTS.copy()
            logger.warning(
                build_log_message(
                    "kt.weights.zero_total", detail="融合权重总和为 0，已重置为默认权重"
                )
            )
        elif abs(total - 1.0) > 0.001:
            for model in self.fusion_weights:
                self.fusion_weights[model] /= total
            logger.debug(
                build_log_message(
                    "kt.weights.normalized", fusion_weights=self.fusion_weights
                )
            )

    @property
    def is_available(self) -> bool:
        """
        检查服务是否可用

        返回True如果：
        1. 本地至少有一个模型文件存在
        2. 内置降级算法（始终可用）

        Returns:
            bool: 服务是否可用
        """
        if self._is_available is not None:
            return self._is_available

        # 检查本地模型（任意一个存在即可）
        local_model_available = False
        for model_type, model_path in self.model_paths.items():
            if model_path and Path(model_path).exists():
                local_model_available = True
                logger.debug(
                    build_log_message(
                        "kt.local.available",
                        model_type=model_type,
                        model_path=model_path,
                    )
                )

        if local_model_available:
            self._is_available = True
            return self._is_available

        # 使用内置算法（降级方案，始终可用）
        logger.info(
            build_log_message(
                "kt.service.degraded",
                detail="未发现本地模型，当前仅能使用内置降级算法",
            )
        )
        self._is_available = True
        return self._is_available

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取所有模型的信息

        Returns:
            dict: 各模型配置和状态信息，包括预测模式和启用的模型
        """
        models_info = {}
        for model_type, config in self.MODEL_CONFIGS.items():
            model_path = self.model_paths.get(model_type, "")
            is_enabled = model_type in self.enabled_models
            runtime_info = None
            if model_type == "dkt":
                try:
                    from ai_services.services.dkt_inference import dkt_predictor

                    runtime_info = dkt_predictor.get_info()
                except ImportError:
                    runtime_info = None
            elif model_type == "mefkt":
                try:
                    from ai_services.services.mefkt_inference import mefkt_predictor

                    runtime_info = mefkt_predictor.get_info()
                except ImportError:
                    runtime_info = None
            models_info[model_type] = {
                "name": config.get("name", "未知"),
                "description": config.get("description", ""),
                "github": config.get("github", ""),
                "paper_title": config.get("paper_title"),
                "paper_doi": config.get("paper_doi"),
                "weight": self.fusion_weights.get(model_type, 0),
                "model_path": model_path if model_path else None,
                "is_local_available": bool(model_path and Path(model_path).exists()),
                "is_enabled": is_enabled,
                "runtime_info": runtime_info,
            }

        mode_names = {
            "fusion": "融合模式",
            "single": "单模型模式",
            "ensemble": "集成模式",
        }

        return {
            "prediction_mode": self.prediction_mode,
            "prediction_mode_name": mode_names.get(self.prediction_mode, "融合模式"),
            "enabled_models": self.enabled_models,
            "fusion_mode": self.prediction_mode == "fusion",  # 向后兼容
            "fusion_weights": self.fusion_weights,
            "models": models_info,
            "is_available": self.is_available,
            "use_gpu": self.use_gpu,
        }

    def predict_mastery(
        self,
        user_id: int,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: List[int] = None,
    ) -> Dict[str, Any]:
        """
        预测学生对知识点的掌握程度

        根据配置的预测模式（fusion/single/ensemble）使用不同策略进行预测。

        Args:
            user_id: 用户ID
            course_id: 课程ID
            answer_history: 答题历史列表，每项包含:
                - question_id: 题目ID
                - correct: 是否正确 (0或1)
                - timestamp: 答题时间（可选）
                - knowledge_point_id: 知识点ID（可选）
            knowledge_points: 需要预测的知识点ID列表（可选）

        Returns:
            dict: 预测结果，包含:
                - predictions: 各知识点掌握率 {point_id: mastery_rate}
                - model_results: 各模型单独的预测结果（融合/集成模式）
                - fusion_weights: 使用的融合权重（融合模式）
                - confidence: 预测置信度
                - model_type: 使用的模型类型
                - prediction_mode: 预测模式
                - analysis: 分析说明
        """
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
                return self._attach_prediction_metadata(result, answer_history)
            elif self.prediction_mode == "ensemble":
                result = self._ensemble_predict(
                    user_id, course_id, answer_history, knowledge_points
                )
                return self._attach_prediction_metadata(result, answer_history)
            else:  # 默认融合模式
                result = self._fusion_predict(
                    user_id, course_id, answer_history, knowledge_points
                )
                return self._attach_prediction_metadata(result, answer_history)
        except Exception as e:
            logger.error(
                build_log_message(
                    "kt.predict.fail", user_id=user_id, course_id=course_id, error=e
                )
            )
            # 降级到内置算法
            result = self._builtin_prediction(
                user_id, course_id, answer_history, knowledge_points
            )
            return self._attach_prediction_metadata(result, answer_history)

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
            "dkt": self._predict_with_dkt,
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

    @staticmethod
    def _coerce_int_identifier(value: object, default: int = 0) -> int:
        """将批量请求中的标识值安全转换为整数。"""
        if isinstance(value, bool):
            return default

        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _single_model_predict(
        self,
        _user_id: int,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        单模型预测

        仅使用一个启用的模型进行预测。

        Args:
            user_id: 用户ID
            course_id: 课程ID
            answer_history: 答题历史
            knowledge_points: 知识点列表

        Returns:
            预测结果
        """
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

        # 回退到内置算法
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
        """
        集成预测（不融合）

        调用所有启用的模型进行预测，返回各模型独立结果，不进行融合。

        Args:
            user_id: 用户ID
            course_id: 课程ID
            answer_history: 答题历史
            knowledge_points: 知识点列表

        Returns:
            各模型的独立预测结果
        """
        model_results = {}
        num_questions = len(answer_history)

        # 仅调用启用的模型
        for model_type in self.enabled_models:
            model_results[model_type] = self._run_model_prediction(
                model_type=model_type,
                course_id=course_id,
                answer_history=answer_history,
                knowledge_points=knowledge_points,
            )

        # 有效模型
        active_models = [k for k, v in model_results.items() if v is not None]

        # 计算平均置信度
        valid_models = [m for m in model_results.values() if m is not None]
        if valid_models:
            avg_confidence = sum(m.get("confidence", 0.6) for m in valid_models) / len(
                valid_models
            )
        else:
            avg_confidence = 0.5

        # 使用第一个有效模型的预测作为主结果（集成模式不融合）
        main_predictions = {}
        for model_type in active_models:
            if model_results[model_type]:
                main_predictions = self._extract_prediction_map(
                    model_results[model_type]
                )
                break

        model_names = (
            ", ".join([str(m).upper() for m in active_models])
            if active_models
            else "无"
        )

        return {
            "predictions": main_predictions,
            "model_results": {k: v for k, v in model_results.items() if v is not None},
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
        """
        融合多个模型的预测结果

        调用所有启用的模型，按权重融合预测结果。

        Args:
            user_id: 用户ID
            course_id: 课程ID
            answer_history: 答题历史
            knowledge_points: 知识点列表

        Returns:
            融合预测结果
        """
        model_results = {}
        num_questions = len(answer_history)

        # 仅调用启用的模型
        for model_type in self.enabled_models:
            model_results[model_type] = self._run_model_prediction(
                model_type=model_type,
                course_id=course_id,
                answer_history=answer_history,
                knowledge_points=knowledge_points,
            )

        # 融合预测结果
        fused_predictions = self._fuse_predictions(model_results)

        # 计算融合置信度（安全处理空列表情况）
        valid_models = [m for m in model_results.values() if m is not None]
        if valid_models:
            avg_confidence = sum(m.get("confidence", 0.6) for m in valid_models) / len(
                valid_models
            )
        else:
            avg_confidence = 0.5

        # 生成分析说明
        active_models = [k for k, v in model_results.items() if v is not None]

        # 生成模型名称列表（确保都是字符串）
        model_names = (
            ", ".join([str(m).upper() for m in active_models])
            if active_models
            else "无"
        )

        return {
            "predictions": fused_predictions,
            "model_results": {k: v for k, v in model_results.items() if v is not None},
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
        """
        融合多个模型的预测结果

        使用加权平均融合各模型的预测结果。

        Args:
            model_results: 各模型的预测结果

        Returns:
            融合后的知识点掌握度
        """
        # 收集所有知识点
        all_points = set()
        for result in model_results.values():
            all_points.update(self._extract_prediction_map(result).keys())

        # 加权融合
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
                fused[point_id] = 0.5  # 默认值

        return fused

    def _predict_with_dkt(
        self,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        使用DKT模型进行预测

        优先使用本地 DKT 神经网络模型推理，若模型未加载则降级到统计算法。

        Args:
            answer_history: 答题历史
            knowledge_points: 知识点列表

        Returns:
            预测结果
        """
        num_questions = len(answer_history)

        # 尝试使用真实 DKT 模型
        try:
            from ai_services.services.dkt_inference import (
                dkt_predictor,
                auto_load_model,
            )

            # 如果模型未加载，尝试自动加载
            if not dkt_predictor.is_loaded:
                auto_load_model()

            if dkt_predictor.is_loaded:
                result = dkt_predictor.predict(
                    answer_history,
                    knowledge_points,
                    course_id=course_id,
                )
                logger.debug(
                    build_log_message(
                        "kt.dkt.inference_ok",
                        answer_count=num_questions,
                        prediction_count=len(result.get("predictions", {})),
                    )
                )
                return result
            else:
                logger.debug("DKT 模型未加载，使用统计算法降级")
        except (
            ImportError,
            NameError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:
            logger.warning(
                build_log_message(
                    "kt.dkt.inference_fail", answer_count=num_questions, error=e
                )
            )

        # 降级: 使用内置统计算法
        predictions = self._calculate_point_mastery(answer_history, knowledge_points)

        return {
            "predictions": predictions,
            "confidence": self._estimate_stat_confidence(
                answer_history, floor=0.42, ceiling=0.82
            ),
            "model_type": "dkt",
            "analysis": f"DKT降级：基于{num_questions}条答题记录的统计推断",
        }

    def _predict_with_mefkt(
        self,
        course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        使用 MEFKT 模型进行预测。

        优先调用本地训练好的 MEFKT 检查点；若未加载成功，
        则回退到当前服务已有的统计算法，保证 KT 接口稳定。

        Args:
            answer_history: 答题历史
            knowledge_points: 目标知识点列表

        Returns:
            预测结果
        """
        answer_count = len(answer_history)

        # 尝试使用真实 MEFKT 模型
        try:
            from ai_services.services.mefkt_inference import (
                auto_load_model,
                mefkt_predictor,
            )

            # 如果模型未加载，尝试自动加载
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
            else:
                logger.debug("MEFKT 模型未加载，使用统计算法降级")
        except (
            ImportError,
            NameError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:
            logger.warning(
                build_log_message(
                    "kt.mefkt.inference_fail", answer_count=answer_count, error=e
                )
            )

        # 降级: 使用内置统计算法
        predictions = self._calculate_point_mastery(answer_history, knowledge_points)

        return {
            "predictions": predictions,
            "confidence": self._estimate_stat_confidence(
                answer_history, floor=0.4, ceiling=0.84
            ),
            "model_type": "mefkt",
            "analysis": f"MEFKT降级：基于{answer_count}条答题记录的统计推断",
        }

    def _builtin_prediction(
        self,
        _user_id: int,
        _course_id: int,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        使用内置算法进行掌握度预测（降级方案）

        基于加权平均和指数衰减的简单算法：
        1. 按知识点分组统计正确率
        2. 近期答题权重更高（指数衰减）
        3. 考虑题目难度因素

        Args:
            user_id: 用户ID
            course_id: 课程ID
            answer_history: 答题历史
            knowledge_points: 知识点列表

        Returns:
            预测结果
        """
        predictions = self._calculate_point_mastery(answer_history, knowledge_points)

        return {
            "predictions": predictions,
            "confidence": self._estimate_stat_confidence(
                answer_history, floor=0.35, ceiling=0.76
            ),
            "model_type": "builtin",
            "analysis": "使用内置统计算法进行掌握度分析",
        }

    def _calculate_point_mastery(
        self,
        answer_history: List[Dict[str, Any]],
        knowledge_points: Optional[List[int]] = None,
    ) -> Dict[int, float]:
        """
        基于答题历史计算知识点掌握度

        使用加权平均算法，近期答题权重更高

        Args:
            answer_history: 答题历史
            knowledge_points: 知识点列表

        Returns:
            知识点掌握度字典 {point_id: mastery_rate}
        """
        from collections import defaultdict

        # 按知识点分组
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

        # 计算指数衰减权重（最近的答题权重最高）
        n = len(answer_history)
        decay_factor = 0.9
        prior_mean = 0.25
        prior_strength = 4.0

        for i, record in enumerate(answer_history):
            point_id = record.get("knowledge_point_id", 0)
            correct = record.get("correct", 0)
            if not point_id:
                continue

            # 计算权重（最近的记录权重最高）
            weight = decay_factor ** (n - 1 - i)

            point_stats[point_id]["total"] += 1
            point_stats[point_id]["correct"] += correct
            point_stats[point_id]["weighted_sum"] += correct * weight
            point_stats[point_id]["weight_total"] += weight
            if i >= max(0, n - 6):
                point_stats[point_id]["recent_correct"] += correct
                point_stats[point_id]["recent_total"] += 1

        # 计算加权平均掌握度
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

        # 如果指定了知识点列表，确保所有知识点都有预测值
        if knowledge_points:
            for point_id in knowledge_points:
                if point_id not in predictions:
                    predictions[point_id] = round(prior_mean, 4)

        return predictions

    @staticmethod
    def _prepare_input_data(
        answer_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        准备模型输入数据（融合模式）

        为所有模型准备统一的输入数据格式

        Args:
            answer_history: 答题历史

        Returns:
            转换后的数据，包含所有模型需要的格式
        """
        num_questions = len(answer_history)
        question_ids = [a.get("question_id", 0) for a in answer_history]
        correct_flags = [a.get("correct", 0) for a in answer_history]
        knowledge_point_ids = [a.get("knowledge_point_id", 0) for a in answer_history]
        timestamps = [a.get("timestamp") for a in answer_history]

        return {
            "num_questions": num_questions,
            "question_ids": question_ids,
            "correct_flags": correct_flags,
            "knowledge_point_ids": knowledge_point_ids,
            "timestamps": timestamps,
            # 各模型特定格式
            "dkt_format": {
                "num_questions": num_questions,
                "question_ids": question_ids,
                "correct_flags": correct_flags,
            },
        }

    def _get_default_prediction(
        self, knowledge_points: List[int] = None
    ) -> Dict[str, Any]:
        """
        返回默认预测结果（无数据时）

        Args:
            knowledge_points: 知识点列表

        Returns:
            默认预测结果
        """
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

    def batch_predict(
        self, user_histories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        批量预测多个用户的掌握度

        Args:
            user_histories: 用户历史列表，每项包含:
                - user_id: 用户ID
                - course_id: 课程ID
                - answer_history: 答题历史
                - knowledge_points: 知识点列表（可选）

        Returns:
            预测结果列表
        """
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
        """
        基于掌握度预测生成学习建议

        Args:
            user_id: 用户ID
            course_id: 课程ID
            mastery_predictions: 知识点掌握度预测
            threshold: 掌握度阈值（低于此值需要加强学习）

        Returns:
            学习建议列表
        """
        recommendations = []

        # 筛选出需要加强的知识点
        weak_points = [
            (point_id, mastery)
            for point_id, mastery in mastery_predictions.items()
            if mastery < threshold
        ]

        # 按掌握度排序（最弱的优先）
        weak_points.sort(key=lambda x: x[1])

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


# 创建默认服务实例
kt_service = KnowledgeTracingService()
