from __future__ import annotations


# 维护意图：Resolve runtime.neo4j_service lazily so existing test patches keep working
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class RuntimeNeo4jServiceProxy:
    """Resolve runtime.neo4j_service lazily so existing test patches keep working."""

    def __getattr__(self, name: str):
        from platform_ai.rag import runtime as runtime_module

        return getattr(runtime_module.neo4j_service, name)


neo4j_service = RuntimeNeo4jServiceProxy()


# 维护意图：Instantiate the facade class from platform_ai.rag.runtime lazily
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def FacadeGraphRAGLLM():
    """Instantiate the facade class from platform_ai.rag.runtime lazily."""
    from platform_ai.rag import runtime as runtime_module

    return runtime_module.FacadeGraphRAGLLM()
