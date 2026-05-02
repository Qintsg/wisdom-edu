"""GraphRAG corpus tokenization and entity helper functions。"""

from __future__ import annotations

from collections import Counter
from hashlib import md5
import re

from knowledge.models import Resource

TOKEN_PATTERN = re.compile(r"[\u4e00-\u9fff]{1,}|[a-zA-Z0-9_]+")
STOP_TOKENS = {
    "知识点",
    "课程",
    "资源",
    "题目",
    "学习",
    "关联",
    "当前",
    "point",
    "resource",
    "question",
}


def tokenize(text: str) -> set[str]:
    """Extract normalized Chinese and alphanumeric search tokens from text."""
    if not text:
        return set()
    return {token.lower() for token in TOKEN_PATTERN.findall(str(text)) if token.strip()}


def _safe_resource_url(resource: Resource) -> str:
    """Return a stable URL for a resource entity."""
    if resource.url:
        return resource.url
    if resource.file:
        try:
            return resource.file.url
        except ValueError:
            return ""
    return ""


def _top_themes(texts: list[str], limit: int = 6) -> list[str]:
    """Extract a compact list of community themes from entity texts."""
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(token for token in tokenize(text) if token not in STOP_TOKENS and len(token) > 1)
    return [token for token, _ in counter.most_common(limit)]


def _chapter_entity_id(chapter_name: str) -> str:
    """Build a deterministic chapter entity id."""
    normalized = chapter_name.strip() or "未分章"
    return f"chapter:{md5(normalized.encode('utf-8')).hexdigest()[:16]}"
