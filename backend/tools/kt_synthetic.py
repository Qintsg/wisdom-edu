#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""知识追踪合成学习轨迹画像辅助逻辑。"""

from __future__ import annotations

from collections import defaultdict
from random import Random
from typing import cast

from tools.kt_synthetic_support import (
    InteractionStep,
    SamplingContext,
    SyntheticLearningContext,
    SyntheticState,
    apply_session_gap_decay,
    build_children_map,
    build_kp_profile,
    build_sampling_weights,
    choose_focus_kp,
    clamp_value,
    compute_interaction_outcome,
    initialize_mastery_levels,
    mean_or_default,
    update_mastery_after_interaction,
)


StudentProfile = dict[str, float | int | str]
KnowledgePointProfile = dict[str, object]
SyntheticSequence = dict[str, object]


# 维护意图：限制概率、掌握度等连续特征，避免合成轨迹出现越界值
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """限制概率、掌握度等连续特征，避免合成轨迹出现越界值。"""
    return clamp_value(value, lower, upper)


# 维护意图：兼容历史测试入口的均值包装
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _mean(values: object, default: float = 0.0) -> float:
    """兼容历史测试入口的均值包装。"""
    return mean_or_default(values, default)


# 维护意图：构建知识点画像：难度、章节、邻接关系与学习稳定度
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_kp_profiles(
    kp_to_idx: dict[int, int],
    prereqs: dict[int, list[int]],
    kp_metadata: dict[int, dict[str, object]],
) -> tuple[dict[int, KnowledgePointProfile], dict[int, list[int]]]:
    """构建知识点画像：难度、章节、邻接关系与学习稳定度。"""
    children = build_children_map(prereqs, kp_to_idx)
    depth_cache: dict[int, int] = {}
    kp_profiles: dict[int, KnowledgePointProfile] = {}
    for kp_id in kp_to_idx:
        kp_profiles[kp_id] = build_kp_profile(
            kp_id=kp_id,
            kp_to_idx=kp_to_idx,
            prereqs=prereqs,
            children_map=children,
            kp_metadata=kp_metadata,
            depth_cache=depth_cache,
        )

    return kp_profiles, {
        kp_id: cast(list[int], kp_profiles[kp_id]["children"])
        for kp_id in kp_profiles
    }


# 维护意图：采样学生画像，让合成学生不再只有一个统一模板
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _sample_student_profile(rng: Random) -> StudentProfile:
    """采样学生画像，让合成学生不再只有一个统一模板。"""
    archetype = rng.choices(
        ["struggling", "steady", "advanced"],
        weights=[0.26, 0.52, 0.22],
        k=1,
    )[0]
    if archetype == "struggling":
        base_ability = _clamp(rng.betavariate(2.0, 4.2) * 0.9 + 0.02, 0.08, 0.72)
        learning_rate = 0.045 + rng.random() * 0.06
        forgetting_rate = 0.035 + rng.random() * 0.045
        slip_rate = 0.08 + rng.random() * 0.08
        guess_rate = 0.05 + rng.random() * 0.08
        review_bias = 0.5 + rng.random() * 0.35
        persistence = 0.42 + rng.random() * 0.22
    elif archetype == "advanced":
        base_ability = _clamp(rng.betavariate(4.2, 2.1) * 0.92 + 0.04, 0.38, 0.96)
        learning_rate = 0.065 + rng.random() * 0.08
        forgetting_rate = 0.012 + rng.random() * 0.025
        slip_rate = 0.02 + rng.random() * 0.05
        guess_rate = 0.02 + rng.random() * 0.04
        review_bias = 0.2 + rng.random() * 0.25
        persistence = 0.62 + rng.random() * 0.28
    else:
        base_ability = _clamp(rng.betavariate(3.0, 3.0) * 0.9 + 0.03, 0.18, 0.88)
        learning_rate = 0.055 + rng.random() * 0.07
        forgetting_rate = 0.02 + rng.random() * 0.035
        slip_rate = 0.04 + rng.random() * 0.06
        guess_rate = 0.03 + rng.random() * 0.05
        review_bias = 0.3 + rng.random() * 0.3
        persistence = 0.5 + rng.random() * 0.25

    return {
        "archetype": archetype,
        "base_ability": base_ability,
        "learning_rate": learning_rate,
        "forgetting_rate": forgetting_rate,
        "slip_rate": slip_rate,
        "guess_rate": guess_rate,
        "review_bias": review_bias,
        "focus_bias": 0.48 + rng.random() * 0.35,
        "fatigue_sensitivity": 0.04 + rng.random() * 0.11,
        "persistence": persistence,
        "session_span": rng.randint(6, 14),
    }


# 维护意图：根据先修掌握、复习队列和学生画像选择当前学习焦点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _choose_focus_kp(
    kp_profiles: dict[int, KnowledgePointProfile],
    state: SyntheticState,
    profile: StudentProfile,
    rng: Random,
) -> int:
    """根据先修掌握、复习队列和学生画像选择当前学习焦点。"""
    return choose_focus_kp(
        learning=SyntheticLearningContext(kp_profiles=kp_profiles, profile=profile),
        state=state,
        rng=rng,
    )


# 维护意图：模拟单个学生的答题轨迹，供 KT 相关回归测试构造稳定样本
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _simulate_student_sequence(
    kp_to_idx: dict[int, int],
    kp_profiles: dict[int, KnowledgePointProfile],
    children_map: dict[int, list[int]],
    rng: Random,
    seq_len: int,
    student_profile: StudentProfile | None = None,
) -> SyntheticSequence:
    """模拟单个学生的答题轨迹，供 KT 相关回归测试构造稳定样本。"""
    profile = student_profile or _sample_student_profile(rng)
    kp_ids = list(kp_profiles.keys())
    mastery = initialize_mastery_levels(kp_profiles, profile, rng)
    state = SyntheticState(
        mastery=mastery,
        attempts=defaultdict(int),
        review_queue=defaultdict(float),
        recent_wrong=defaultdict(int),
    )
    learning = SyntheticLearningContext(kp_profiles=kp_profiles, profile=profile)
    last_seen: dict[int, int] = {}
    last_results: list[int] = []

    kp_indices: list[str] = []
    correct_flags: list[str] = []
    focus_kp = _choose_focus_kp(
        kp_profiles,
        state,
        profile,
        rng,
    )
    session_remaining = 0
    session_count = 0

    for step in range(seq_len):
        session_span = max(int(profile["session_span"]), 1)
        if session_remaining <= 0:
            session_count += 1
            focus_kp = _choose_focus_kp(
                kp_profiles,
                state,
                profile,
                rng,
            )
            session_remaining = min(seq_len - step, max(4, int(rng.gauss(session_span, 2))))
            gap_scale = 1 + rng.random() * 1.2
            apply_session_gap_decay(
                state=state,
                last_seen=last_seen,
                learning=learning,
                step=step,
                gap_scale=gap_scale,
            )

        session_progress = 1 - (session_remaining / session_span)
        if rng.random() < 0.18:
            focus_kp = _choose_focus_kp(
                kp_profiles,
                state,
                profile,
                rng,
            )

        weights = build_sampling_weights(
            kp_ids,
            SamplingContext(learning=learning, state=state, focus_kp=focus_kp),
        )
        kp_id = rng.choices(kp_ids, weights=weights, k=1)[0]
        outcome = compute_interaction_outcome(
            InteractionStep(
                kp_id=kp_id,
                focus_kp=focus_kp,
                session_progress=session_progress,
                last_results=last_results,
            ),
            learning=learning,
            state=state,
            rng=rng,
        )
        update_mastery_after_interaction(
            kp_id,
            outcome,
            learning,
            state,
        )

        state.attempts[kp_id] += 1
        last_seen[kp_id] = step
        kp_indices.append(str(kp_to_idx[kp_id]))
        correct_flags.append(str(outcome.correct))
        last_results.append(outcome.correct)
        session_remaining -= 1

    unique_kps = len(set(kp_indices))
    accuracy = sum(int(flag) for flag in correct_flags) / max(len(correct_flags), 1)
    return {
        "kp_indices": kp_indices,
        "correct_flags": correct_flags,
        "accuracy": accuracy,
        "revisit_ratio": 1 - unique_kps / max(len(kp_indices), 1),
        "unique_kps": unique_kps,
        "sessions": session_count,
        "profile": profile,
    }


__all__ = [
    "_build_kp_profiles",
    "_simulate_student_sequence",
]
