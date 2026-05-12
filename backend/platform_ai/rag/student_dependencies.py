"""学生端 GraphRAG mixin 的动态依赖入口。"""
from __future__ import annotations


class StudentRAGDependenciesMixin:
    """通过 facade 模块读取依赖，保留测试 patch 路径兼容。"""

    def _runtime(self):
        """读取 platform_ai.rag.student.student_graphrag_runtime。"""
        from . import student as student_module
        return student_module.student_graphrag_runtime

    def _llm_facade(self):
        """读取 platform_ai.rag.student.llm_facade。"""
        from . import student as student_module
        return student_module.llm_facade

    def _resource_mcp_service(self):
        """读取 platform_ai.rag.student.resource_mcp_service。"""
        from . import student as student_module
        return student_module.resource_mcp_service
