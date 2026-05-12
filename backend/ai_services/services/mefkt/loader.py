#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 模型自动加载辅助。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Mapping, Protocol

logger = logging.getLogger(__name__)


class MEFKTLoaderProtocol(Protocol):
    """自动加载所需的预测器接口。"""

    def load_model(self, model_path: str, metadata_path: str | None = None) -> bool:
        """加载模型。"""


def auto_load_mefkt_model(
    predictor: MEFKTLoaderProtocol,
    backend_root: Path,
    environ: Mapping[str, str],
) -> bool:
    """从环境变量或默认路径加载 MEFKT 模型。"""
    model_path = environ.get("KT_MEFKT_MODEL_PATH", "").strip()
    metadata_path = environ.get("KT_MEFKT_META_PATH", "").strip()
    if not model_path:
        default_model_path = backend_root / "models" / "MEFKT" / "mefkt_model.pt"
        if not default_model_path.exists():
            logger.debug("未配置 KT_MEFKT_MODEL_PATH 且默认模型不存在，跳过自动加载")
            return False
        model_path = str(default_model_path)
    effective_metadata_path = metadata_path if metadata_path else None
    return predictor.load_model(model_path=model_path, metadata_path=effective_metadata_path)
