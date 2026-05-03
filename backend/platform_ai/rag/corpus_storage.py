"""GraphRAG corpus persistence helpers。"""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings


# 维护意图：Return the runtime path used for the persisted course GraphRAG index
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_index_path(course_id: int) -> Path:
    """Return the runtime path used for the persisted course GraphRAG index."""
    return Path(settings.BASE_DIR) / "runtime_logs" / "rag" / f"course_{course_id}.json"


# 维护意图：Persist the generated GraphRAG index
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def save_course_index(course_id: int, payload: dict) -> Path:
    """Persist the generated GraphRAG index."""
    index_path = get_index_path(course_id)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return index_path


# 维护意图：Load a previously materialized GraphRAG index, if available
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_course_index(course_id: int) -> dict:
    """Load a previously materialized GraphRAG index, if available."""
    index_path = get_index_path(course_id)
    if not index_path.exists():
        return {}
    return json.loads(index_path.read_text(encoding="utf-8"))


# 维护意图：Delete the persisted GraphRAG index for a single course when present
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def delete_course_index(course_id: int) -> bool:
    """Delete the persisted GraphRAG index for a single course when present."""
    index_path = get_index_path(course_id)
    if not index_path.exists():
        return False
    index_path.unlink()
    return True
