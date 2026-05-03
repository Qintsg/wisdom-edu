#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""KT 合成轨迹的采样与交互更新辅助函数。"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any

from tools.kt_synthetic_math import clamp_value, mean_or_default, sigmoid


StudentProfile = dict[str, float | str | int]
KnowledgePointProfiles = dict[int, dict[str, Any]]


# 维护意图：合成学生在模拟过程中的动态状态
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class SyntheticState:
    """合成学生在模拟过程中的动态状态。"""

    mastery: dict[int, float]
    attempts: dict[int, int]
    review_queue: dict[int, float]
    recent_wrong: dict[int, int]


# 维护意图：合成轨迹的静态学习上下文
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class SyntheticLearningContext:
    """合成轨迹的静态学习上下文。"""

    kp_profiles: KnowledgePointProfiles
    profile: StudentProfile


# 维护意图：单步知识点采样所需上下文
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class SamplingContext:
    """单步知识点采样所需上下文。"""

    learning: SyntheticLearningContext
    state: SyntheticState
    focus_kp: int


# 维护意图：当前交互步骤的局部上下文
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class InteractionStep:
    """当前交互步骤的局部上下文。"""

    kp_id: int
    focus_kp: int
    session_progress: float
    last_results: list[int]


# 维护意图：单次作答交互的模拟结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class InteractionOutcome:
    """单次作答交互的模拟结果。"""

    correct: int
    prereq_mastery: float
    gain: float


# 维护意图：新会话开始时，对已学知识点施加遗忘衰减
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_session_gap_decay(
    *,
    state: SyntheticState,
    last_seen: dict[int, int],
    learning: SyntheticLearningContext,
    step: int,
    gap_scale: float,
) -> None:
    """新会话开始时，对已学知识点施加遗忘衰减。"""
    for kp_id, current_mastery in list(state.mastery.items()):
        if state.attempts[kp_id] <= 0:
            continue
        age = max(step - last_seen.get(kp_id, step), 1)
        decay = float(learning.profile["forgetting_rate"]) * gap_scale * min(age / 8, 1.6)
        decay *= 1.1 - float(learning.kp_profiles[kp_id]["stability"]) * 0.45
        state.mastery[kp_id] = clamp_value(current_mastery - decay, 0.02, 0.98)
        if state.mastery[kp_id] < 0.55 and state.attempts[kp_id] > 0:
            state.review_queue[kp_id] += 0.1


# 维护意图：计算先修知识点的平均掌握度
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def prerequisite_mastery(
    prereq_ids: list[int],
    state: SyntheticState,
    profile: StudentProfile,
    default: float,
) -> float:
    """计算先修知识点的平均掌握度。"""
    base_fallback = 0.25 + float(profile["base_ability"]) * 0.25
    return mean_or_default(
        (state.mastery.get(pre, base_fallback) for pre in prereq_ids),
        default=default,
    )


# 维护意图：判断知识点是否可被当前学生采样
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def is_kp_unlocked(
    kp_profile: dict[str, Any],
    state: SyntheticState,
    prereq_mastery_value: float,
    kp_id: int,
) -> bool:
    """判断知识点是否可被当前学生采样。"""
    return (
        prereq_mastery_value >= 0.45
        or state.attempts[kp_id] > 0
        or not kp_profile["prereqs"]
    )


# 维护意图：计算不含焦点和结构关系的基础采样权重
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def base_sampling_weight(
    kp_id: int,
    state: SyntheticState,
    profile: StudentProfile,
) -> float:
    """计算不含焦点和结构关系的基础采样权重。"""
    return (
        0.05
        + (1 - state.mastery[kp_id]) * 0.75
        + min(state.review_queue[kp_id], 1.8) * float(profile["review_bias"])
    )


# 维护意图：根据是否首练和解锁状态调整采样权重
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_attempt_weight(weight: float, kp_id: int, state: SyntheticState, unlocked: bool) -> float:
    """根据是否首练和解锁状态调整采样权重。"""
    if state.attempts[kp_id] == 0:
        return weight + (0.32 if unlocked else 0.03)
    return weight + min(state.attempts[kp_id], 4) * 0.02


# 维护意图：根据当前学习焦点和图谱邻接关系调整权重
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_focus_weight(
    weight: float,
    kp_id: int,
    context: SamplingContext,
) -> float:
    """根据当前学习焦点和图谱邻接关系调整权重。"""
    kp_profiles = context.learning.kp_profiles
    kp_profile = kp_profiles[kp_id]
    focus_profile = kp_profiles[context.focus_kp]
    if kp_id == context.focus_kp:
        return weight * (1.9 + float(context.learning.profile["focus_bias"]) * 0.25)
    if focus_profile["chapter"] and kp_profile["chapter"] == focus_profile["chapter"]:
        return weight * 1.35
    if kp_id in focus_profile["prereqs"] or kp_id in focus_profile["children"]:
        return weight * 1.2
    return weight


# 维护意图：根据最近错误、已掌握状态和锁定状态做最终权重调整
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_recent_state_weight(
    weight: float,
    kp_id: int,
    state: SyntheticState,
    unlocked: bool,
) -> float:
    """根据最近错误、已掌握状态和锁定状态做最终权重调整。"""
    adjusted_weight = weight * (0.22 if not unlocked else 1.0)
    if state.recent_wrong[kp_id] > 0:
        adjusted_weight *= 1.25 + min(state.recent_wrong[kp_id], 2) * 0.1
    if state.attempts[kp_id] > 0 and state.mastery[kp_id] > 0.78:
        adjusted_weight *= 0.65
    return max(adjusted_weight, 0.001)


# 维护意图：计算单个知识点在当前时间步的采样权重
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_single_sampling_weight(kp_id: int, context: SamplingContext) -> float:
    """计算单个知识点在当前时间步的采样权重。"""
    state = context.state
    profile = context.learning.profile
    kp_profile = context.learning.kp_profiles[kp_id]
    prereq_mastery_value = prerequisite_mastery(
        kp_profile["prereqs"],
        state,
        profile,
        default=0.92,
    )
    unlocked = is_kp_unlocked(kp_profile, state, prereq_mastery_value, kp_id)
    weight = base_sampling_weight(kp_id, state, profile)
    weight = apply_attempt_weight(weight, kp_id, state, unlocked)
    weight = apply_focus_weight(weight, kp_id, context)
    return apply_recent_state_weight(weight, kp_id, state, unlocked)


# 维护意图：为当前时间步计算知识点采样权重
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_sampling_weights(kp_ids: list[int], context: SamplingContext) -> list[float]:
    """为当前时间步计算知识点采样权重。"""
    return [build_single_sampling_weight(kp_id, context) for kp_id in kp_ids]


# 维护意图：计算学习焦点候选权重，未解锁且未练习的知识点返回 None
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_focus_candidate_weight(
    kp_id: int,
    kp_profile: dict[str, Any],
    learning: SyntheticLearningContext,
    state: SyntheticState,
) -> float | None:
    """计算学习焦点候选权重，未解锁且未练习的知识点返回 None。"""
    prereq_mastery_value = prerequisite_mastery(
        kp_profile["prereqs"],
        state,
        learning.profile,
        default=0.9,
    )
    unlocked = prereq_mastery_value >= 0.45 or state.attempts.get(kp_id, 0) > 0 or not kp_profile["prereqs"]
    if not unlocked and state.attempts.get(kp_id, 0) == 0:
        return None
    weight = 0.1 + (1 - state.mastery.get(kp_id, 0.25)) * 1.2 + state.review_queue.get(kp_id, 0.0) * 0.5
    return weight + (0.3 if state.attempts.get(kp_id, 0) == 0 else 0.0)


# 维护意图：根据先修掌握、复习队列和学生画像选择当前学习焦点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def choose_focus_kp(
    learning: SyntheticLearningContext,
    state: SyntheticState,
    rng: Random,
) -> int:
    """根据先修掌握、复习队列和学生画像选择当前学习焦点。"""
    candidates: list[int] = []
    weights: list[float] = []
    for kp_id, kp_profile in learning.kp_profiles.items():
        weight = build_focus_candidate_weight(kp_id, kp_profile, learning, state)
        if weight is None:
            continue
        candidates.append(kp_id)
        weights.append(weight)
    if not candidates:
        return rng.choice(list(learning.kp_profiles.keys()))
    return rng.choices(candidates, weights=weights, k=1)[0]


# 维护意图：计算当前知识点作答是否正确及其先修掌握度、增益
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def compute_interaction_outcome(
    step: InteractionStep,
    learning: SyntheticLearningContext,
    state: SyntheticState,
    rng: Random,
) -> InteractionOutcome:
    """计算当前知识点作答是否正确及其先修掌握度、增益。"""
    kp_profile = learning.kp_profiles[step.kp_id]
    prereq_mastery_value = prerequisite_mastery(
        kp_profile["prereqs"],
        state,
        learning.profile,
        default=0.95,
    )
    item_difficulty = adjusted_item_difficulty(step, learning, state, rng)
    correct_probability = compute_correct_probability(
        step,
        learning,
        state,
        prereq_mastery_value,
        item_difficulty,
    )
    correct = 1 if rng.random() < clamp_value(correct_probability, 0.02, 0.98) else 0
    gain = float(learning.profile["learning_rate"]) * (0.45 + item_difficulty * 0.65)
    return InteractionOutcome(correct=correct, prereq_mastery=prereq_mastery_value, gain=gain)


# 维护意图：根据会话进度和当前掌握度微调题目难度
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def adjusted_item_difficulty(
    step: InteractionStep,
    learning: SyntheticLearningContext,
    state: SyntheticState,
    rng: Random,
) -> float:
    """根据会话进度和当前掌握度微调题目难度。"""
    challenge_shift = rng.gauss(0, 0.06)
    if step.session_progress > 0.55 and state.mastery[step.kp_id] > 0.55:
        challenge_shift += 0.03
    elif step.session_progress < 0.25:
        challenge_shift -= 0.02
    raw_difficulty = float(learning.kp_profiles[step.kp_id]["difficulty"])
    return clamp_value(raw_difficulty + challenge_shift, 0.15, 0.96)


# 维护意图：综合掌握度、先修、疲劳和错题状态计算正确概率
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def compute_correct_probability(
    step: InteractionStep,
    learning: SyntheticLearningContext,
    state: SyntheticState,
    prereq_mastery_value: float,
    item_difficulty: float,
) -> float:
    """综合掌握度、先修、疲劳和错题状态计算正确概率。"""
    recent_momentum = (mean_or_default(step.last_results[-4:], default=0.5) - 0.5) * 0.45
    fatigue_penalty = float(learning.profile["fatigue_sensitivity"]) * step.session_progress * (0.8 + item_difficulty)
    review_bonus = 0.06 if state.review_queue[step.kp_id] > 0.45 else 0.0
    focus_bonus = 0.08 if step.kp_id == step.focus_kp else 0.0
    struggle_penalty = min(state.recent_wrong[step.kp_id], 3) * 0.05
    readiness_penalty = max(0.0, 0.52 - prereq_mastery_value) * 0.9
    latent_mastery = (
        state.mastery[step.kp_id] * 0.58
        + float(learning.profile["base_ability"]) * 0.22
        + prereq_mastery_value * 0.2
    )
    base_prob = sigmoid(
        (latent_mastery - item_difficulty) * 5.4
        + review_bonus
        + focus_bonus
        + recent_momentum
        - fatigue_penalty
        - struggle_penalty
        - readiness_penalty
    )
    return float(learning.profile["guess_rate"]) + (
        1 - float(learning.profile["guess_rate"]) - float(learning.profile["slip_rate"])
    ) * base_prob


# 维护意图：根据作答结果更新掌握度、复习队列和最近错误统计
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_mastery_after_interaction(
    kp_id: int,
    outcome: InteractionOutcome,
    learning: SyntheticLearningContext,
    state: SyntheticState,
) -> None:
    """根据作答结果更新掌握度、复习队列和最近错误统计。"""
    if outcome.correct:
        apply_correct_interaction(kp_id, outcome, state)
    else:
        apply_wrong_interaction(kp_id, outcome, learning, state)
    update_child_mastery(kp_id, outcome, learning, state)


# 维护意图：应用答对后的掌握度和复习状态变化
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_correct_interaction(
    kp_id: int,
    outcome: InteractionOutcome,
    state: SyntheticState,
) -> None:
    """应用答对后的掌握度和复习状态变化。"""
    state.mastery[kp_id] = clamp_value(
        state.mastery[kp_id] + outcome.gain * (1 - state.mastery[kp_id]) * (0.72 + outcome.prereq_mastery * 0.18),
        0.02,
        0.995,
    )
    state.review_queue[kp_id] = max(state.review_queue[kp_id] * 0.45 - 0.08, 0.0)
    state.recent_wrong[kp_id] = 0


# 维护意图：应用答错后的掌握度、复习队列和先修复习变化
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_wrong_interaction(
    kp_id: int,
    outcome: InteractionOutcome,
    learning: SyntheticLearningContext,
    state: SyntheticState,
) -> None:
    """应用答错后的掌握度、复习队列和先修复习变化。"""
    state.mastery[kp_id] = clamp_value(
        state.mastery[kp_id] - 0.02 * (1 - float(learning.profile["persistence"])) + outcome.gain * 0.22,
        0.01,
        0.96,
    )
    state.review_queue[kp_id] += 0.65
    state.recent_wrong[kp_id] += 1
    for prereq_id in learning.kp_profiles[kp_id]["prereqs"]:
        state.review_queue[prereq_id] += 0.18


# 维护意图：根据当前知识点作答结果对后继知识点施加轻量迁移影响
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_child_mastery(
    kp_id: int,
    outcome: InteractionOutcome,
    learning: SyntheticLearningContext,
    state: SyntheticState,
) -> None:
    """根据当前知识点作答结果对后继知识点施加轻量迁移影响。"""
    for child_kp in learning.kp_profiles[kp_id]["children"]:
        state.mastery[child_kp] = clamp_value(
            state.mastery[child_kp] + (0.012 if outcome.correct else -0.004) * outcome.prereq_mastery,
            0.01,
            0.96,
        )


# 维护意图：根据学生画像采样序列长度
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


__all__ = [
    "InteractionOutcome",
    "InteractionStep",
    "SamplingContext",
    "SyntheticLearningContext",
    "SyntheticState",
    "apply_session_gap_decay",
    "build_sampling_weights",
    "choose_focus_kp",
    "compute_interaction_outcome",
    "sample_sequence_length",
    "update_mastery_after_interaction",
]
