"""知识追踪领域能力。"""

from .datasets import DEFAULT_PUBLIC_DATASET, list_public_datasets


def __getattr__(name: str) -> object:
    """按需加载依赖 Django settings 的 KT 门面，避免数据集工具产生副作用。"""
    if name == "knowledge_tracing_facade":
        from .facade import knowledge_tracing_facade

        return knowledge_tracing_facade
    raise AttributeError(f"module 'platform_ai.kt' has no attribute {name!r}")

__all__ = [
    "DEFAULT_PUBLIC_DATASET",
    "knowledge_tracing_facade",
    "list_public_datasets",
]

