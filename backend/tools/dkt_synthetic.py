#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""DKT 合成学习轨迹生成逻辑。"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from pathlib import Path

from tools.dkt_data_access import _get_kp_mapping, _get_kp_metadata, _get_kp_prerequisites
from tools.dkt_paths import DEFAULT_TRAINING_DATA_PATH
from tools.dkt_synthetic_support import (
    build_children_map,
    build_kp_profile,
    build_sampling_weights,
    calculate_kp_depth,
    clamp_value,
    choose_focus_kp,
    compute_interaction_outcome,
    initialize_mastery_levels,
    mean_or_default,
    sample_sequence_length,
    sigmoid,
    update_mastery_after_interaction,
    apply_session_gap_decay,
)


def _clamp(value, lower=0.0, upper=1.0):
    return clamp_value(value, lower, upper)


def _sigmoid(logit):
    return sigmoid(logit)


def _mean(values, default=0.0):
    return mean_or_default(values, default)


def _build_kp_profiles(kp_to_idx, prereqs, kp_metadata):
    """构建知识点画像：难度、章节、邻接关系与学习稳定度。"""
    children = build_children_map(prereqs, kp_to_idx)
    depth_cache = {}
    kp_profiles = {}
    for kp_id in kp_to_idx:
        kp_profiles[kp_id] = build_kp_profile(
            kp_id=kp_id,
            kp_to_idx=kp_to_idx,
            prereqs=prereqs,
            children_map=children,
            kp_metadata=kp_metadata,
            depth_cache=depth_cache,
        )

    return kp_profiles, {kp_id: kp_profiles[kp_id]["children"] for kp_id in kp_profiles}


def _sample_student_profile(rng):
    """采样学生画像，让合成学生不再只有一个统一模板。"""
    archetype = rng.choices(["struggling", "steady", "advanced"], weights=[0.26, 0.52, 0.22], k=1)[0]
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


def _choose_focus_kp(kp_profiles, mastery, attempts, review_queue, profile, rng):
    """根据先修掌握、复习队列和学生画像选择当前学习焦点。"""
    return choose_focus_kp(
        kp_profiles=kp_profiles,
        mastery=mastery,
        attempts=attempts,
        review_queue=review_queue,
        profile=profile,
        rng=rng,
    )


def _simulate_student_sequence(kp_to_idx, kp_profiles, children_map, rng, seq_len, student_profile=None):
    """模拟单个学生的答题轨迹。"""
    profile = student_profile or _sample_student_profile(rng)
    kp_ids = list(kp_profiles.keys())
    mastery = initialize_mastery_levels(kp_profiles, profile, rng)
    attempts = defaultdict(int)
    recent_wrong = defaultdict(int)
    review_queue = defaultdict(float)
    last_seen = {}
    last_results = []

    kp_indices = []
    correct_flags = []
    focus_kp = _choose_focus_kp(kp_profiles, mastery, attempts, review_queue, profile, rng)
    session_remaining = 0
    session_count = 0

    for step in range(seq_len):
        if session_remaining <= 0:
            session_count += 1
            focus_kp = _choose_focus_kp(kp_profiles, mastery, attempts, review_queue, profile, rng)
            session_remaining = min(seq_len - step, max(4, int(rng.gauss(profile["session_span"], 2))))
            gap_scale = 1 + rng.random() * 1.2
            apply_session_gap_decay(
                mastery=mastery,
                attempts=attempts,
                last_seen=last_seen,
                profile=profile,
                kp_profiles=kp_profiles,
                step=step,
                gap_scale=gap_scale,
                review_queue=review_queue,
            )

        session_progress = 1 - (session_remaining / max(profile["session_span"], 1))
        if rng.random() < 0.18:
            focus_kp = _choose_focus_kp(kp_profiles, mastery, attempts, review_queue, profile, rng)

        weights = build_sampling_weights(
            kp_ids=kp_ids,
            kp_profiles=kp_profiles,
            mastery=mastery,
            attempts=attempts,
            review_queue=review_queue,
            profile=profile,
            focus_kp=focus_kp,
            recent_wrong=recent_wrong,
        )
        kp_id = rng.choices(kp_ids, weights=weights, k=1)[0]
        correct, prereq_mastery, gain = compute_interaction_outcome(
            kp_id=kp_id,
            kp_profiles=kp_profiles,
            mastery=mastery,
            review_queue=review_queue,
            recent_wrong=recent_wrong,
            last_results=last_results,
            profile=profile,
            focus_kp=focus_kp,
            session_progress=session_progress,
            rng=rng,
        )
        update_mastery_after_interaction(
            kp_id=kp_id,
            correct=correct,
            prereq_mastery=prereq_mastery,
            gain=gain,
            mastery=mastery,
            review_queue=review_queue,
            recent_wrong=recent_wrong,
            kp_profiles=kp_profiles,
            profile=profile,
        )

        attempts[kp_id] += 1
        last_seen[kp_id] = step
        kp_indices.append(str(kp_to_idx[kp_id]))
        correct_flags.append(str(correct))
        last_results.append(correct)
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


def generate_synthetic_data(course_id=None, num_students=200, min_seq=10, max_seq=80, output_path=None, seed=None):
    """生成带学生画像、先修关系与复习效应的 DKT 合成训练数据。"""
    kp_to_idx, _ = _get_kp_mapping(course_id)
    q_size = len(kp_to_idx)
    if q_size == 0:
        print("[错误] 没有知识点数据，无法生成合成数据")
        return None, 0, 0

    rng = random.Random(seed)
    prereqs = _get_kp_prerequisites(course_id)
    kp_metadata = _get_kp_metadata(course_id)
    kp_profiles, children_map = _build_kp_profiles(kp_to_idx, prereqs, kp_metadata)

    if output_path is None:
        output_path = str(DEFAULT_TRAINING_DATA_PATH)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    total_records = 0
    accuracy_stats = []
    revisit_stats = []
    session_stats = []
    with open(output_path, "w", encoding="utf-8") as handle:
        for _ in range(num_students):
            profile = _sample_student_profile(rng)
            seq_len = sample_sequence_length(
                min_seq=min_seq,
                max_seq=max_seq,
                profile=profile,
                rng=rng,
            )
            student_seq = _simulate_student_sequence(kp_to_idx, kp_profiles, children_map, rng, seq_len, profile)
            accuracy_stats.append(student_seq["accuracy"])
            revisit_stats.append(student_seq["revisit_ratio"])
            session_stats.append(student_seq["sessions"])
            total_records += seq_len
            handle.write(f"{seq_len}\n")
            handle.write(f"{','.join(student_seq['kp_indices'])}\n")
            handle.write(f"{','.join(student_seq['correct_flags'])}\n")

    avg_accuracy = _mean(accuracy_stats, default=0.0)
    avg_revisit = _mean(revisit_stats, default=0.0)
    avg_sessions = _mean(session_stats, default=0.0)
    print(
        f"[合成数据] {num_students} 个虚拟学生, {total_records} 条记录, {q_size} 个知识点 → {output_path} "
        f"(平均正确率={avg_accuracy:.2%}, 平均复习占比={avg_revisit:.2%}, 平均会话数={avg_sessions:.1f})"
    )
    return output_path, num_students, total_records
