"""DKT 推理辅助工具。"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_backend_path(path_value: str | None) -> Path | None:
    """将环境变量中的模型路径统一解析为后端根目录下的绝对路径。"""
    if path_value is None:
        return None
    normalized = str(path_value).strip()
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (BACKEND_ROOT / candidate).resolve()


def resolve_metadata_path(model_path: Path, metadata_path: str | None) -> Path:
    """解析元数据路径，空白输入回退到模型旁的默认 metadata 文件。"""
    resolved = resolve_backend_path(metadata_path)
    if resolved is not None:
        return resolved
    return model_path.with_suffix(".meta.json")


def coerce_optional_int(value: object) -> int | None:
    """将动态字典中的值安全转换为整数。"""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class CourseSlotBundle:
    """课程知识点/题目到公共槽位的稳定映射。"""

    question_to_slot: dict[int, int]
    point_to_slots: dict[int, list[int]]
    representative_slot: dict[int, int]


def load_global_kp_mapping() -> tuple[dict[int, int], list[int]]:
    """使用训练时一致的全局知识点顺序映射知识点索引。"""
    from knowledge.models import KnowledgePoint

    ordered_ids = list(KnowledgePoint.objects.order_by("id").values_list("id", flat=True))
    return {kp_id: idx for idx, kp_id in enumerate(ordered_ids)}, ordered_ids


def stable_slot_index(parts: list[str], slot_count: int) -> int:
    """为课程题目构建稳定的公开槽位索引。"""
    payload = "|".join(parts).encode("utf-8")
    digest = hashlib.md5(payload).hexdigest()
    return int(digest[:12], 16) % max(slot_count, 1)


def build_public_slot_bundle(*, course_id: int, slot_count: int) -> CourseSlotBundle:
    """为课程构建稳定的公共槽位映射。"""
    from assessments.models import Question
    from knowledge.models import KnowledgePoint

    question_to_slot: dict[int, int] = {}
    point_to_slots: dict[int, list[int]] = {}
    questions = list(
        Question.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    for question in questions:
        point_ids = [str(point_id) for point_id in question.knowledge_points.values_list("id", flat=True)]
        slot_index = stable_slot_index(
            [
                str(question.question_type or "unknown"),
                str(question.difficulty or "medium"),
                str(question.chapter or ""),
                ",".join(sorted(point_ids)[:4]),
                str(len(question.content or "")),
            ],
            slot_count,
        )
        question_to_slot[int(question.id)] = slot_index
        for point_id in point_ids:
            point_to_slots.setdefault(int(point_id), []).append(slot_index)

    for point_id in KnowledgePoint.objects.filter(course_id=course_id).values_list("id", flat=True):
        current_point_id = int(point_id)
        if current_point_id not in point_to_slots:
            point_to_slots[current_point_id] = [
                stable_slot_index(["kp", str(course_id), str(current_point_id)], slot_count)
            ]

    representative_slot = {point_id: slots[0] for point_id, slots in point_to_slots.items() if slots}
    return CourseSlotBundle(
        question_to_slot=question_to_slot,
        point_to_slots=point_to_slots,
        representative_slot=representative_slot,
    )


def collect_legacy_target_kp_ids(answer_history: list[dict[str, Any]], knowledge_point_ids: list[int] | None) -> set[int]:
    """收集旧版推理需要输出的目标知识点 ID。"""
    target_kp_ids: set[int] = set()
    for record in answer_history:
        current_kp_id = coerce_optional_int(record.get("knowledge_point_id"))
        if current_kp_id is not None:
            target_kp_ids.add(current_kp_id)
    if knowledge_point_ids:
        target_kp_ids.update(int(kp_id) for kp_id in knowledge_point_ids)
    return target_kp_ids


def build_legacy_input_sequence(
    *,
    answer_history: list[dict[str, Any]],
    kp_to_idx: dict[int, int],
    q_size: int,
) -> Any:
    """构造旧版知识点维度 DKT 输入序列。"""
    import numpy as np

    sequence_length = len(answer_history)
    input_seq = np.zeros((1, sequence_length, 2 * q_size), dtype=np.float32)
    for time_index, record in enumerate(answer_history):
        current_kp_id = coerce_optional_int(record.get("knowledge_point_id"))
        if current_kp_id is None:
            continue
        idx = kp_to_idx.get(current_kp_id)
        if idx is None or idx >= q_size:
            continue
        is_correct = coerce_optional_int(record.get("correct")) == 1
        input_seq[0, time_index, idx if is_correct else q_size + idx] = 1.0
    return input_seq


def collect_public_slot_target_kp_ids(
    *,
    answer_history: list[dict[str, Any]],
    bundle: CourseSlotBundle,
    explicit_point_ids: list[int] | None,
) -> set[int]:
    """收集公开槽位适配模式需要输出的目标知识点 ID。"""
    target_kp_ids = {int(kp_id) for kp_id in (explicit_point_ids or [])}
    for record in answer_history:
        current_kp_id = coerce_optional_int(record.get("knowledge_point_id"))
        if current_kp_id is not None:
            target_kp_ids.add(current_kp_id)
        current_question_id = coerce_optional_int(record.get("question_id"))
        if current_question_id is None:
            continue
        question_slot = bundle.question_to_slot.get(current_question_id)
        if question_slot is None:
            continue
        for point_id, slots in bundle.point_to_slots.items():
            if question_slot in slots:
                target_kp_ids.add(int(point_id))
    if not target_kp_ids:
        target_kp_ids.update(bundle.point_to_slots.keys())
    return target_kp_ids


def build_public_slot_input_sequence(
    *,
    answer_history: list[dict[str, Any]],
    bundle: CourseSlotBundle,
    q_size: int,
) -> tuple[Any, int, set[int]]:
    """构造公开槽位适配模式输入序列。"""
    import numpy as np

    sequence_length = len(answer_history)
    input_seq = np.zeros((1, sequence_length, 2 * q_size), dtype=np.float32)
    recognized_count = 0
    used_slots: set[int] = set()
    for time_index, record in enumerate(answer_history):
        slot_index = None
        current_question_id = coerce_optional_int(record.get("question_id"))
        if current_question_id is not None:
            slot_index = bundle.question_to_slot.get(current_question_id)
        if slot_index is None:
            current_point_id = coerce_optional_int(record.get("knowledge_point_id"))
            if current_point_id is not None:
                slot_index = bundle.representative_slot.get(current_point_id)
        if slot_index is None:
            continue
        recognized_count += 1
        used_slots.add(int(slot_index))
        correct = 1 if coerce_optional_int(record.get("correct")) == 1 else 0
        input_seq[0, time_index, slot_index if correct else q_size + slot_index] = 1.0
    return input_seq, recognized_count, used_slots
