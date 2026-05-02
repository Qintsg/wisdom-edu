#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""KT 合成学习轨迹画像辅助工具。"""

from __future__ import annotations

from collections import defaultdict
import math
from random import Random
from typing import Any


def clamp_value(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """将数值限制在给定区间内。"""
    return max(lower, min(upper, value))


def sigmoid(logit: float) -> float:
    """稳定版 sigmoid。"""
    bounded_logit = clamp_value(logit, -12.0, 12.0)
    return 1 / (1 + math.exp(-bounded_logit))


def mean_or_default(values, default: float = 0.0) -> float:
    """计算均值，空序列时返回默认值。"""
    normalized_values = list(values)
    if not normalized_values:
        return default
    return sum(normalized_values) / len(normalized_values)


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


def apply_session_gap_decay(
    *,
    mastery: dict[int, float],
    attempts: dict[int, int],
    last_seen: dict[int, int],
    profile: dict[str, float | str | int],
    kp_profiles: dict[int, dict[str, Any]],
    step: int,
    gap_scale: float,
    review_queue: dict[int, float],
) -> None:
    """新会话开始时，对已学知识点施加遗忘衰减。"""
    for kp_id, current_mastery in list(mastery.items()):
        if attempts[kp_id] <= 0:
            continue
        age = max(step - last_seen.get(kp_id, step), 1)
        decay = float(profile["forgetting_rate"]) * gap_scale * min(age / 8, 1.6)
        decay *= 1.1 - float(kp_profiles[kp_id]["stability"]) * 0.45
        mastery[kp_id] = clamp_value(current_mastery - decay, 0.02, 0.98)
        if mastery[kp_id] < 0.55 and attempts[kp_id] > 0:
            review_queue[kp_id] += 0.1


def build_sampling_weights(
    *,
    kp_ids: list[int],
    kp_profiles: dict[int, dict[str, Any]],
    mastery: dict[int, float],
    attempts: dict[int, int],
    review_queue: dict[int, float],
    profile: dict[str, float | str | int],
    focus_kp: int,
    recent_wrong: dict[int, int],
) -> list[float]:
    """为当前时间步计算知识点采样权重。"""
    weights: list[float] = []
    for kp_id in kp_ids:
        kp_profile = kp_profiles[kp_id]
        prereq_mastery = mean_or_default(
            (mastery.get(pre, 0.25 + float(profile["base_ability"]) * 0.25) for pre in kp_profile["prereqs"]),
            default=0.92,
        )
        unlocked = prereq_mastery >= 0.45 or attempts[kp_id] > 0 or not kp_profile["prereqs"]
        weight = 0.05 + (1 - mastery[kp_id]) * 0.75 + min(review_queue[kp_id], 1.8) * float(profile["review_bias"])
        if attempts[kp_id] == 0:
            weight += 0.32 if unlocked else 0.03
        else:
            weight += min(attempts[kp_id], 4) * 0.02
        if kp_id == focus_kp:
            weight *= 1.9 + float(profile["focus_bias"]) * 0.25
        elif kp_profiles[focus_kp]["chapter"] and kp_profile["chapter"] == kp_profiles[focus_kp]["chapter"]:
            weight *= 1.35
        elif kp_id in kp_profiles[focus_kp]["prereqs"] or kp_id in kp_profiles[focus_kp]["children"]:
            weight *= 1.2
        if not unlocked:
            weight *= 0.22
        if recent_wrong[kp_id] > 0:
            weight *= 1.25 + min(recent_wrong[kp_id], 2) * 0.1
        if attempts[kp_id] > 0 and mastery[kp_id] > 0.78:
            weight *= 0.65
        weights.append(max(weight, 0.001))
    return weights


def choose_focus_kp(
    *,
    kp_profiles: dict[int, dict[str, Any]],
    mastery: dict[int, float],
    attempts: dict[int, int],
    review_queue: dict[int, float],
    profile: dict[str, float | str | int],
    rng: Random,
) -> int:
    """根据先修掌握、复习队列和学生画像选择当前学习焦点。"""
    candidates: list[int] = []
    weights: list[float] = []
    for kp_id, kp_profile in kp_profiles.items():
        prereq_mastery = mean_or_default(
            (mastery.get(pre, 0.25 + float(profile["base_ability"]) * 0.25) for pre in kp_profile["prereqs"]),
            default=0.9,
        )
        unlocked = prereq_mastery >= 0.45 or attempts.get(kp_id, 0) > 0 or not kp_profile["prereqs"]
        if not unlocked and attempts.get(kp_id, 0) == 0:
            continue
        weight = 0.1 + (1 - mastery.get(kp_id, 0.25)) * 1.2 + review_queue.get(kp_id, 0.0) * 0.5
        if attempts.get(kp_id, 0) == 0:
            weight += 0.3
        candidates.append(kp_id)
        weights.append(weight)
    if not candidates:
        return rng.choice(list(kp_profiles.keys()))
    return rng.choices(candidates, weights=weights, k=1)[0]


def compute_interaction_outcome(
    *,
    kp_id: int,
    kp_profiles: dict[int, dict[str, Any]],
    mastery: dict[int, float],
    review_queue: dict[int, float],
    recent_wrong: dict[int, int],
    last_results: list[int],
    profile: dict[str, float | str | int],
    focus_kp: int,
    session_progress: float,
    rng: Random,
) -> tuple[int, float, float]:
    """计算当前知识点作答是否正确及其先修掌握度、增益。"""
    kp_profile = kp_profiles[kp_id]
    prereq_mastery = mean_or_default(
        (mastery.get(pre, 0.25 + float(profile["base_ability"]) * 0.25) for pre in kp_profile["prereqs"]),
        default=0.95,
    )
    challenge_shift = rng.gauss(0, 0.06)
    if session_progress > 0.55 and mastery[kp_id] > 0.55:
        challenge_shift += 0.03
    elif session_progress < 0.25:
        challenge_shift -= 0.02
    item_difficulty = clamp_value(float(kp_profile["difficulty"]) + challenge_shift, 0.15, 0.96)
    recent_momentum = (mean_or_default(last_results[-4:], default=0.5) - 0.5) * 0.45
    fatigue_penalty = float(profile["fatigue_sensitivity"]) * session_progress * (0.8 + item_difficulty)
    review_bonus = 0.06 if review_queue[kp_id] > 0.45 else 0.0
    focus_bonus = 0.08 if kp_id == focus_kp else 0.0
    struggle_penalty = min(recent_wrong[kp_id], 3) * 0.05
    readiness_penalty = max(0.0, 0.52 - prereq_mastery) * 0.9
    latent_mastery = mastery[kp_id] * 0.58 + float(profile["base_ability"]) * 0.22 + prereq_mastery * 0.2
    base_prob = sigmoid(
        (latent_mastery - item_difficulty) * 5.4
        + review_bonus
        + focus_bonus
        + recent_momentum
        - fatigue_penalty
        - struggle_penalty
        - readiness_penalty
    )
    correct_prob = float(profile["guess_rate"]) + (1 - float(profile["guess_rate"]) - float(profile["slip_rate"])) * base_prob
    correct = 1 if rng.random() < clamp_value(correct_prob, 0.02, 0.98) else 0
    gain = float(profile["learning_rate"]) * (0.45 + item_difficulty * 0.65)
    return correct, prereq_mastery, gain


def update_mastery_after_interaction(
    *,
    kp_id: int,
    correct: int,
    prereq_mastery: float,
    gain: float,
    mastery: dict[int, float],
    review_queue: dict[int, float],
    recent_wrong: dict[int, int],
    kp_profiles: dict[int, dict[str, Any]],
    profile: dict[str, float | str | int],
) -> None:
    """根据作答结果更新掌握度、复习队列和最近错误统计。"""
    if correct:
        mastery[kp_id] = clamp_value(
            mastery[kp_id] + gain * (1 - mastery[kp_id]) * (0.72 + prereq_mastery * 0.18),
            0.02,
            0.995,
        )
        review_queue[kp_id] = max(review_queue[kp_id] * 0.45 - 0.08, 0.0)
        recent_wrong[kp_id] = 0
    else:
        mastery[kp_id] = clamp_value(
            mastery[kp_id] - 0.02 * (1 - float(profile["persistence"])) + gain * 0.22,
            0.01,
            0.96,
        )
        review_queue[kp_id] += 0.65
        recent_wrong[kp_id] += 1
        for prereq_id in kp_profiles[kp_id]["prereqs"]:
            review_queue[prereq_id] += 0.18

    for child_kp in kp_profiles[kp_id]["children"]:
        mastery[child_kp] = clamp_value(
            mastery[child_kp] + (0.012 if correct else -0.004) * prereq_mastery,
            0.01,
            0.96,
        )


def sample_sequence_length(
    *,
    min_seq: int,
    max_seq: int,
    profile: dict[str, float | str | int],
    rng: Random,
) -> int:
    """根据学生画像采样序列长度。"""
    preferred_length = rng.triangular(
        min_seq,
        max_seq,
        min(max_seq, min_seq + (max_seq - min_seq) * 0.42),
    )
    if profile["archetype"] == "advanced":
        preferred_length += rng.uniform(3, 10)
    elif profile["archetype"] == "struggling":
        preferred_length -= rng.uniform(0, 6)
    return max(min_seq, min(max_seq, int(round(preferred_length))))
