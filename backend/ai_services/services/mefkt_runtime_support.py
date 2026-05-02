#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 题目级在线运行时兼容导出。"""

from __future__ import annotations

from ai_services.services.mefkt_runtime_features import (
    prepare_question_features,
)
from ai_services.services.mefkt_runtime_graph import build_graph_statistics
from ai_services.services.mefkt_runtime_rows import build_runtime_feature_rows
from ai_services.services.mefkt_runtime_sources import (
    build_feature_sources,
    load_runtime_source_data,
)
from ai_services.services.mefkt_runtime_types import (
    GraphStatisticsBundle,
    QuestionFeaturePreparation,
    QuestionFeatureScales,
    RuntimeFeatureSources,
    RuntimeSourceData,
)

# 旧运行时仍从 support 导入私有名；这里保留别名，避免扩大调用方改动面。
_build_feature_sources = build_feature_sources

__all__ = [
    "GraphStatisticsBundle",
    "QuestionFeaturePreparation",
    "QuestionFeatureScales",
    "RuntimeFeatureSources",
    "RuntimeSourceData",
    "_build_feature_sources",
    "build_feature_sources",
    "build_graph_statistics",
    "build_runtime_feature_rows",
    "load_runtime_source_data",
    "prepare_question_features",
]
