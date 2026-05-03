from __future__ import annotations

from platform_ai.rag.runtime_graph_query_mixin import CourseGraphRAGQueryMixin
from platform_ai.rag.runtime_materialization_mixin import CourseGraphRAGMaterializationMixin
from platform_ai.rag.runtime_search_mixin import CourseGraphRAGSearchMixin


# 维护意图：统一管理课程级 GraphRAG 物化、检索与图查询
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class CourseGraphRAGRuntime(
    CourseGraphRAGMaterializationMixin,
    CourseGraphRAGSearchMixin,
    CourseGraphRAGQueryMixin,
):
    """统一管理课程级 GraphRAG 物化、检索与图查询。"""
