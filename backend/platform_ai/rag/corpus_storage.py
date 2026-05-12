"""GraphRAG corpus persistence helpers。"""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings


def get_index_path(course_id: int) -> Path:
    """Return the runtime path used for the persisted course GraphRAG index."""
    return Path(settings.BASE_DIR) / "runtime_logs" / "rag" / f"course_{course_id}.json"


def save_course_index(course_id: int, payload: dict) -> Path:
    """Persist the generated GraphRAG index."""
    index_path = get_index_path(course_id)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return index_path


def load_course_index(course_id: int) -> dict:
    """Load a previously materialized GraphRAG index, if available."""
    index_path = get_index_path(course_id)
    if not index_path.exists():
        return {}
    return json.loads(index_path.read_text(encoding="utf-8"))


def delete_course_index(course_id: int) -> bool:
    """Delete the persisted GraphRAG index for a single course when present."""
    index_path = get_index_path(course_id)
    if not index_path.exists():
        return False
    index_path.unlink()
    return True
