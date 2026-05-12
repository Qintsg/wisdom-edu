#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 工具共享路径与论文元数据常量。"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MEFKT_MODEL_PATH = BASE_DIR / "models" / "MEFKT" / "mefkt_model.pt"
MEFKT_META_PATH = BASE_DIR / "models" / "MEFKT" / "mefkt_model.meta.json"
MEFKT_PUBLIC_BASELINE_DIR = BASE_DIR / "models" / "MEFKT" / "public_baselines"
PAPER_TITLE = "融合多视角习题表征与遗忘机制的深度知识追踪"
PAPER_DOI = "10.11896/jsjkx.250700092"
RUNTIME_SCHEMA = "question_online_v1"
