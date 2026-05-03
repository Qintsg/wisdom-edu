"""
知识追踪服务模块 (Knowledge Tracing Service)

本模块保留 MEFKT 知识追踪服务的公开入口，具体运行时、预测策略与统计回退
拆分到相邻 mixin 模块中，保持旧导入路径与响应结构兼容。
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from common.logging_utils import build_log_message

from ai_services.services.kt_model_runtime import KTModelRuntimeMixin
from ai_services.services.kt_prediction_modes import KTPredictionModeMixin


logger = logging.getLogger(__name__)
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


MODEL_CONFIGS = {
    "mefkt": {
        "name": "Multi-view Exercise Fusion KT",
        "description": "融合结构视角、属性视角与遗忘机制的知识追踪模型，支持公开预训练 + 题目级在线部署",
        "paper_title": "融合多视角习题表征与遗忘机制的深度知识追踪",
        "paper_doi": "10.11896/jsjkx.250700092",
        "requires": ["torch", "numpy", "scikit-learn"],
        "default_weight": 1.0,
    },
}

DEFAULT_FUSION_WEIGHTS = {
    "mefkt": 1.0,
}


# 维护意图：将配置中的相对模型路径统一解析为后端根目录下的绝对路径
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
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


# 维护意图：知识追踪服务类。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeTracingService(KTModelRuntimeMixin, KTPredictionModeMixin):
    """
    知识追踪服务类。

    提供基于 MEFKT 的知识追踪能力，并在模型不可用时自动降级到
    内置统计预测，避免学习、测评和画像链路因模型文件缺失而中断。
    """

    MODEL_CONFIGS = MODEL_CONFIGS
    DEFAULT_FUSION_WEIGHTS = DEFAULT_FUSION_WEIGHTS

    def __init__(
        self,
        model_paths: Dict[str, str] = None,
        fusion_weights: Dict[str, float] = None,
        use_gpu: bool = False,
        prediction_mode: str = None,
        enabled_models: List[str] = None,
    ):
        """初始化知识追踪服务和预测模式配置。"""
        default_mefkt_model_root = BACKEND_ROOT / "models" / "MEFKT"
        raw_model_paths = model_paths or {
            "mefkt": os.getenv(
                "KT_MEFKT_MODEL_PATH", str(default_mefkt_model_root / "mefkt_model.pt")
            ),
        }
        self.model_paths = {
            model_type: _resolve_backend_path(model_path)
            for model_type, model_path in raw_model_paths.items()
            if model_type in self.MODEL_CONFIGS
        }

        self.fusion_weights = fusion_weights or self._load_fusion_weights()
        self._normalize_weights()

        self.use_gpu = use_gpu and os.getenv("KT_USE_GPU", "false").lower() == "true"

        valid_modes = ["fusion", "single", "ensemble"]
        env_mode = os.getenv("KT_PREDICTION_MODE", "fusion").lower()
        self.prediction_mode = prediction_mode or (
            env_mode if env_mode in valid_modes else "fusion"
        )

        configured_models = self._resolve_enabled_models(enabled_models)
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

    # 维护意图：解析启用模型列表，并保证至少返回一个有效模型
    # 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def _resolve_enabled_models(self, enabled_models: List[str] = None) -> List[str]:
        """解析启用模型列表，并保证至少返回一个有效模型。"""
        if enabled_models is not None:
            configured_models = [
                model.lower()
                for model in enabled_models
                if model.lower() in self.MODEL_CONFIGS
            ]
        else:
            env_models = os.getenv("KT_ENABLED_MODELS", "")
            if env_models:
                configured_models = [
                    model.strip().lower()
                    for model in env_models.split(",")
                    if model.strip().lower() in self.MODEL_CONFIGS
                ]
            else:
                configured_models = ["mefkt"]

        if not configured_models:
            configured_models = ["mefkt"]
        return configured_models

    # 维护意图：从环境变量加载融合权重，配置无效时使用默认权重
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _load_fusion_weights(self) -> Dict[str, float]:
        """从环境变量加载融合权重，配置无效时使用默认权重。"""
        try:
            weights_str = os.getenv("KT_FUSION_WEIGHTS", "")
            if weights_str:
                weights = json.loads(weights_str)
                return {
                    key: value
                    for key, value in weights.items()
                    if key in self.MODEL_CONFIGS
                }
        except json.JSONDecodeError:
            logger.warning(
                build_log_message(
                    "kt.weights.invalid", detail="融合权重配置格式错误，使用默认权重"
                )
            )
        return self.DEFAULT_FUSION_WEIGHTS.copy()

    # 维护意图：归一化融合权重，避免权重和异常影响融合预测
    # 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def _normalize_weights(self) -> None:
        """归一化融合权重，避免权重和异常影响融合预测。"""
        self.fusion_weights = {
            key: value
            for key, value in self.fusion_weights.items()
            if key in self.MODEL_CONFIGS
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

    # 维护意图：检查服务是否可用；内置降级算法始终可用
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def is_available(self) -> bool:
        """检查服务是否可用；内置降级算法始终可用。"""
        if self._is_available is not None:
            return self._is_available

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

        logger.info(
            build_log_message(
                "kt.service.degraded",
                detail="未发现本地模型，当前仅能使用内置降级算法",
            )
        )
        self._is_available = True
        return self._is_available

    # 维护意图：获取各 KT 模型配置、运行时状态和当前预测模式
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_model_info(self) -> Dict[str, Any]:
        """获取各 KT 模型配置、运行时状态和当前预测模式。"""
        models_info = {}
        for model_type, config in self.MODEL_CONFIGS.items():
            model_path = self.model_paths.get(model_type, "")
            is_enabled = model_type in self.enabled_models
            runtime_info = self._load_runtime_info(model_type)
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
            "fusion_mode": self.prediction_mode == "fusion",
            "fusion_weights": self.fusion_weights,
            "models": models_info,
            "is_available": self.is_available,
            "use_gpu": self.use_gpu,
        }

    # 维护意图：按模型类型读取运行时状态，导入失败时保持空值兼容
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _load_runtime_info(self, model_type: str) -> Dict[str, Any] | None:
        """按模型类型读取运行时状态，导入失败时保持空值兼容。"""
        if model_type == "mefkt":
            try:
                from ai_services.services.mefkt_inference import mefkt_predictor

                return mefkt_predictor.get_info()
            except ImportError:
                return None
        return None


kt_service = KnowledgeTracingService()


__all__ = [
    "KnowledgeTracingService",
    "kt_service",
    "_resolve_backend_path",
]
