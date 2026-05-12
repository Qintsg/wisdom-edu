"""KT prediction result helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


MEFKT_MODEL_TYPES = frozenset({"mefkt_real", "mefkt_question_online"})


def is_mefkt_prediction(result: Mapping[str, object] | None) -> bool:
    """判断 KT 输出是否来自真实 MEFKT 推理。"""
    if not isinstance(result, Mapping):
        return False
    model_type = str(result.get("model_type") or "")
    if model_type in MEFKT_MODEL_TYPES:
        return True
    if model_type not in {"fusion", "ensemble"}:
        return False

    model_results = result.get("model_results")
    if not isinstance(model_results, Mapping):
        return False
    child_results = [
        child_result
        for child_result in model_results.values()
        if isinstance(child_result, Mapping)
    ]
    return bool(child_results) and all(is_mefkt_prediction(child) for child in child_results)


def answered_point_ids(answer_history: Iterable[Mapping[str, object]]) -> set[int]:
    """提取已有答题证据覆盖到的知识点 ID。"""
    point_ids: set[int] = set()
    for record in answer_history:
        point_id_raw = record.get("knowledge_point_id")
        if point_id_raw is None:
            continue
        try:
            point_ids.add(int(point_id_raw))
        except (TypeError, ValueError):
            continue
    return point_ids


def normalize_prediction_map(raw_predictions: object) -> dict[int, float]:
    """将 KT 原始 predictions 规整为 int -> float 字典。"""
    if not isinstance(raw_predictions, Mapping):
        return {}
    prediction_map: dict[int, float] = {}
    for point_id_raw, mastery_raw in raw_predictions.items():
        try:
            prediction_map[int(point_id_raw)] = float(mastery_raw)
        except (TypeError, ValueError):
            continue
    return prediction_map


__all__ = [
    "MEFKT_MODEL_TYPES",
    "answered_point_ids",
    "is_mefkt_prediction",
    "normalize_prediction_map",
]
