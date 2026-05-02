from __future__ import annotations


class RuntimeNeo4jServiceProxy:
    """Resolve runtime.neo4j_service lazily so existing test patches keep working."""

    def __getattr__(self, name: str):
        from platform_ai.rag import runtime as runtime_module

        return getattr(runtime_module.neo4j_service, name)


neo4j_service = RuntimeNeo4jServiceProxy()


def FacadeGraphRAGLLM():
    """Instantiate the facade class from platform_ai.rag.runtime lazily."""
    from platform_ai.rag import runtime as runtime_module

    return runtime_module.FacadeGraphRAGLLM()
