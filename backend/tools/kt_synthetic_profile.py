#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""KT 合成轨迹的知识点画像辅助函数。"""

from __future__ import annotations

from collections import defaultdict
from random import Random
from typing import Any

from tools.kt_synthetic_math import clamp_value


def build_children_map(
    prereqs: dict[int, list[int]],
    kp_to_idx: dict[int, int],
) -> dict[int, list[int]]:
    """根据先修关系构造每个知识点的后继节点映射。"""
    children: dict[int, list[int]] = defaultdict(list)
    for post_kp, pre_list in prereqs.items():
        for pre_kp in pre_list:
            if pre_kp in kp_to_idx and post_kp in kp_to_idx:
                children[pre_kp].append(post_kp)
    return dict(children)


def calculate_kp_depth(
    current_kp_id: int,
    prereqs: dict[int, list[int]],
    kp_to_idx: dict[int, int],
    depth_cache: dict[int, int],
    trail: set[int] | None = None,
) -> int:
    """递归计算知识点在先修图中的深度。"""
    if current_kp_id in depth_cache:
        return depth_cache[current_kp_id]
    current_trail = trail or set()
    if current_kp_id in current_trail:
        return 0

    parents = [pre for pre in prereqs.get(current_kp_id, []) if pre in kp_to_idx]
    if not parents:
        depth_cache[current_kp_id] = 0
        return 0

    depth = 1 + max(
        calculate_kp_depth(
            parent,
            prereqs,
            kp_to_idx,
            depth_cache,
            current_trail | {current_kp_id},
        )
        for parent in parents
    )
    depth_cache[current_kp_id] = depth
    return depth


def compute_kp_difficulty(
    *,
    meta: dict[str, Any],
    depth: int,
    prereq_count: int,
    dependent_count: int,
    level: int,
    order: int,
    total_points: int,
) -> float:
    """综合元数据、题量和先修结构估计知识点难度。"""
    tags = set(meta.get("tags", []))
    q_stats = meta.get("question_stats", {})
    cognitive_bonus = {
        "remember": -0.02,
        "understand": 0.0,
        "apply": 0.05,
        "analyze": 0.08,
        "evaluate": 0.1,
        "create": 0.12,
    }
    category_bonus = {
        "factual": -0.03,
        "conceptual": 0.02,
        "procedural": 0.06,
        "metacognitive": 0.1,
    }

    difficulty = 0.26
    difficulty += min(depth, 4) * 0.07
    difficulty += min(prereq_count, 3) * 0.025
    difficulty += min(dependent_count, 4) * 0.015
    difficulty += min(level - 1, 5) * 0.035
    difficulty += cognitive_bonus.get(meta.get("cognitive_dimension", ""), 0.0)
    difficulty += category_bonus.get(meta.get("category", ""), 0.0)
    difficulty += q_stats.get("hard", 0) * 0.035
    difficulty += q_stats.get("medium", 0) * 0.012
    difficulty -= q_stats.get("easy", 0) * 0.01
    difficulty += min(order / max(total_points, 1), 1.0) * 0.05
    if "难点" in tags:
        difficulty += 0.06
    if "考点" in tags:
        difficulty += 0.03
    if "重点" in tags:
        difficulty += 0.02
    return clamp_value(difficulty, 0.18, 0.92)


def build_kp_profile(
    *,
    kp_id: int,
    kp_to_idx: dict[int, int],
    prereqs: dict[int, list[int]],
    children_map: dict[int, list[int]],
    kp_metadata: dict[int, dict[str, Any]],
    depth_cache: dict[int, int],
) -> dict[str, Any]:
    """构造单个知识点的画像条目。"""
    meta = kp_metadata.get(kp_id, {})
    prereq_ids = [pre for pre in prereqs.get(kp_id, []) if pre in kp_to_idx]
    children = children_map.get(kp_id, [])
    depth = calculate_kp_depth(kp_id, prereqs, kp_to_idx, depth_cache)
    level = max(1, int(meta.get("level") or 1))
    order = max(0, int(meta.get("order") or 0))
    q_stats = meta.get("question_stats", {})
    difficulty = compute_kp_difficulty(
        meta=meta,
        depth=depth,
        prereq_count=len(prereq_ids),
        dependent_count=len(children),
        level=level,
        order=order,
        total_points=len(kp_to_idx),
    )
    return {
        "difficulty": difficulty,
        "depth": depth,
        "chapter": meta.get("chapter", ""),
        "level": level,
        "order": order,
        "prereqs": prereq_ids,
        "children": children,
        "question_volume": q_stats.get("total", 0),
        "stability": clamp_value(
            0.35 + q_stats.get("total", 0) * 0.04 + len(prereq_ids) * 0.05,
            0.35,
            0.92,
        ),
    }


def initialize_mastery_levels(
    kp_profiles: dict[int, dict[str, Any]],
    profile: dict[str, float | str | int],
    rng: Random,
) -> dict[int, float]:
    """初始化学生对各知识点的掌握度。"""
    mastery: dict[int, float] = {}
    for kp_id, kp_profile in kp_profiles.items():
        prereq_boost = 0.04 * len(kp_profile["prereqs"])
        mastery[kp_id] = clamp_value(
            float(profile["base_ability"]) - float(kp_profile["difficulty"]) * 0.42 + prereq_boost + rng.gauss(0, 0.05),
            0.04,
            0.78,
        )
    return mastery


__all__ = [
    "build_children_map",
    "build_kp_profile",
    "calculate_kp_depth",
    "compute_kp_difficulty",
    "initialize_mastery_levels",
]
