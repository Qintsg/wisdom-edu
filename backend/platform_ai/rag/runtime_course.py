from __future__ import annotations

from platform_ai.rag.runtime_graph_query_mixin import CourseGraphRAGQueryMixin
from platform_ai.rag.runtime_materialization_mixin import CourseGraphRAGMaterializationMixin
from platform_ai.rag.runtime_search_mixin import CourseGraphRAGSearchMixin


class CourseGraphRAGRuntime(
    CourseGraphRAGMaterializationMixin,
    CourseGraphRAGSearchMixin,
    CourseGraphRAGQueryMixin,
):
    """统一管理课程级 GraphRAG 物化、检索与图查询。"""
