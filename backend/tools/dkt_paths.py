#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""DKT 工具共享路径常量。"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_BASELINE_DIR = BASE_DIR / "models" / "DKT" / "public_baselines"
DEFAULT_TRAINING_DATA_PATH = BASE_DIR / "models" / "DKT" / "training_data.txt"
DEFAULT_RUNTIME_MODEL_PATH = BASE_DIR / "models" / "DKT" / "dkt_model.pt"
RUNTIME_METADATA_PATH = BASE_DIR / "models" / "DKT" / "dkt_model.meta.json"
