"""知识追踪门面。"""

from __future__ import annotations

from ai_services.services.kt_service import kt_service

from .datasets import DEFAULT_PUBLIC_DATASET, list_public_datasets


class KnowledgeTracingFacade:
    """对外暴露稳定的知识追踪接口，内部仍复用现有 KT 服务。"""

    @staticmethod
    def predict_mastery(*args, **kwargs):
        """Delegate single-student mastery prediction to the shared KT service."""
        return kt_service.predict_mastery(*args, **kwargs)

    @staticmethod
    def batch_predict(*args, **kwargs):
        """Delegate batch mastery prediction to the shared KT service."""
        return kt_service.batch_predict(*args, **kwargs)

    @staticmethod
    def get_learning_recommendations(*args, **kwargs):
        """Delegate recommendation generation to the shared KT service."""
        return kt_service.get_learning_recommendations(*args, **kwargs)

    @staticmethod
    def get_model_info() -> dict:
        """Return KT model metadata enriched with the bundled public dataset catalog."""
        info = kt_service.get_model_info()
        info["default_public_dataset"] = DEFAULT_PUBLIC_DATASET
        info["public_datasets"] = list_public_datasets()
        return info


knowledge_tracing_facade = KnowledgeTracingFacade()

