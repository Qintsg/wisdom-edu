"""Teacher-side request and response contract normalization helpers."""

from __future__ import annotations

from typing import Any


def first_present(data: Any, *keys: str, default: Any = None) -> Any:
    """Return the first non-empty value from a request-like mapping."""
    for key in keys:
        if key not in data:
            continue
        value = data.get(key)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return default


def normalize_course_payload(data: Any) -> dict[str, Any]:
    """Accept legacy and canonical teacher course payload keys."""
    payload = {
        "name": first_present(data, "name", "course_name"),
        "description": first_present(data, "description", "course_description", default=""),
        "term": first_present(data, "term", default=""),
        "is_public": first_present(data, "is_public", default=True),
        "initial_assessment_count": first_present(
            data,
            "initial_assessment_count",
            default=10,
        ),
    }
    if "course_cover" in data:
        payload["course_cover"] = data.get("course_cover")
    return payload


def normalize_class_payload(data: Any) -> dict[str, Any]:
    """Accept legacy and canonical teacher class payload keys."""
    return {
        "name": first_present(data, "name", "class_name"),
        "description": first_present(data, "description", "class_description", default=""),
        "semester": first_present(data, "semester", "term", default=""),
        "course_id": first_present(data, "course_id"),
    }


def normalize_exam_payload(data: Any) -> dict[str, Any]:
    """Accept legacy and canonical teacher exam payload keys."""
    question_ids = first_present(data, "questions", "question_ids", default=[])
    return {
        "course_id": first_present(data, "course_id"),
        "title": first_present(data, "title", "exam_name"),
        "description": first_present(data, "description", default=""),
        "questions": question_ids or [],
        "total_score": first_present(data, "total_score", default=100),
        "pass_score": first_present(data, "pass_score", default=60),
        "duration": first_present(data, "duration", default=60),
        "start_time": first_present(data, "start_time"),
        "end_time": first_present(data, "end_time"),
        "target_class": first_present(data, "target_class", "class_id"),
        "exam_type": first_present(data, "exam_type", "type", default="chapter"),
    }


def normalize_question_point_ids(data: Any) -> list[int]:
    """Accept both `points` and `knowledge_point_ids` request fields."""
    raw = first_present(data, "knowledge_point_ids", "points", default=[])
    if raw in (None, ""):
        return []
    if isinstance(raw, (list, tuple)):
        return [int(item) for item in raw]
    return [int(raw)]
