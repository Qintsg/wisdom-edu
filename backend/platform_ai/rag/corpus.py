"""GraphRAG 索引构建兼容入口。"""

from __future__ import annotations

from .corpus_builder import build_course_graph_payload
from .corpus_storage import delete_course_index, get_index_path, load_course_index, save_course_index
from .corpus_types import CorpusDocument
from .corpus_utils import tokenize


def build_course_graph_index(course_id: int) -> dict:
    """Build a native GraphRAG index from course graph, resources, and questions."""
    return build_course_graph_payload(course_id)


def build_course_corpus(course_id: int) -> list[CorpusDocument]:
    """Build a backwards-compatible corpus list from the GraphRAG index."""
    payload = build_course_graph_index(course_id)
    return [CorpusDocument(**document) for document in payload.get("documents", [])]


__all__ = [
    "build_course_graph_index",
    "build_course_corpus",
    "delete_course_index",
    "get_index_path",
    "load_course_index",
    "save_course_index",
    "tokenize",
]
