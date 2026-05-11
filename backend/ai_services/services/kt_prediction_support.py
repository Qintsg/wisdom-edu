"""KT prediction result helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


MEFKT_MODEL_TYPES = frozenset({"mefkt_real", "mefkt_question_online"})


# 维护意图：判断 KT 输出是否来自真实 MEFKT 推理，而不是统计或默认回退。
# 边界说明：只有真实 MEFKT 输出可用于推断未直接测到的课程知识点。
# 风险说明：新增模型类型时需同步这里，避免把回退结果误当成模型推断。
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


# 维护意图：提取已有答题证据覆盖到的知识点 ID。
# 边界说明：用于限制统计回退结果，真实 MEFKT 推断不受该集合限制。
# 风险说明：输入记录来自多条链路，标识转换失败时必须跳过而不是中断。
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


# 维护意图：将 KT 原始 predictions 规整为 int -> float 字典。
# 边界说明：调用方只处理已经转换成功的条目，异常条目静默跳过。
# 风险说明：不要在这里裁剪值域，具体上下限由业务写回点决定。
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
