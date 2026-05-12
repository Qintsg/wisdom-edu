#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""KT 合成轨迹的数值辅助函数。"""

from __future__ import annotations

import math
from collections.abc import Iterable


def clamp_value(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """将数值限制在给定区间内。"""
    return max(lower, min(upper, value))


def sigmoid(logit: float) -> float:
    """稳定版 sigmoid。"""
    bounded_logit = clamp_value(logit, -12.0, 12.0)
    return 1 / (1 + math.exp(-bounded_logit))


def mean_or_default(values: Iterable[float], default: float = 0.0) -> float:
    """计算均值，空序列时返回默认值。"""
    normalized_values = list(values)
    if not normalized_values:
        return default
    return sum(normalized_values) / len(normalized_values)


__all__ = ["clamp_value", "mean_or_default", "sigmoid"]
