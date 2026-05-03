"""学生端 GraphRAG mixin 的动态依赖入口。"""
from __future__ import annotations


# 维护意图：通过 facade 模块读取依赖，保留测试 patch 路径兼容
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentRAGDependenciesMixin:
    """通过 facade 模块读取依赖，保留测试 patch 路径兼容。"""

    # 维护意图：读取 platform_ai.rag.student.student_graphrag_runtime
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _runtime(self):
        """读取 platform_ai.rag.student.student_graphrag_runtime。"""
        from . import student as student_module
        return student_module.student_graphrag_runtime

    # 维护意图：读取 platform_ai.rag.student.llm_facade
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _llm_facade(self):
        """读取 platform_ai.rag.student.llm_facade。"""
        from . import student as student_module
        return student_module.llm_facade

    # 维护意图：读取 platform_ai.rag.student.resource_mcp_service
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _resource_mcp_service(self):
        """读取 platform_ai.rag.student.resource_mcp_service。"""
        from . import student as student_module
        return student_module.resource_mcp_service
