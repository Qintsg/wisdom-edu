"""GraphRAG service for the student AI assistant."""

from __future__ import annotations

from platform_ai.llm import llm_facade
from platform_ai.rag import student_learning_rag
from platform_ai.rag.runtime import student_graphrag_runtime
from .student_graph_rag_support import answer_graph_question, search_graph_points


# 维护意图：Provide graph search and graph-grounded Q&A capabilities
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentGraphRAGService:
    """Provide graph search and graph-grounded Q&A capabilities."""

    # 维护意图：Search knowledge points within the current course graph
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def search_points(self, *, user, course_id: int, query: str, limit: int = 8) -> dict[str, object]:
        """Search knowledge points within the current course graph."""
        return search_graph_points(user=user, course_id=course_id, query=query, limit=limit)

    # 维护意图：Run GraphRAG question answering under the current course context
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def ask(self, *, user, course_id: int, question: str, point_id: int | None = None) -> dict[str, object]:
        """Run GraphRAG question answering under the current course context."""
        return answer_graph_question(user=user, course_id=course_id, question=question, point_id=point_id)


student_graph_rag_service = StudentGraphRAGService()
