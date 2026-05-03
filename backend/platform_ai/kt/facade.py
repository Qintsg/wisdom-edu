"""知识追踪门面。"""

from __future__ import annotations

from ai_services.services.kt_service import kt_service

from .datasets import DEFAULT_PUBLIC_DATASET, list_public_datasets


# 维护意图：对外暴露稳定的知识追踪接口，内部仍复用现有 KT 服务
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeTracingFacade:
    """对外暴露稳定的知识追踪接口，内部仍复用现有 KT 服务。"""

    # 维护意图：Delegate single-student mastery prediction to the shared KT service
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @staticmethod
    def predict_mastery(*args, **kwargs):
        """Delegate single-student mastery prediction to the shared KT service."""
        return kt_service.predict_mastery(*args, **kwargs)

    # 维护意图：Delegate batch mastery prediction to the shared KT service
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @staticmethod
    def batch_predict(*args, **kwargs):
        """Delegate batch mastery prediction to the shared KT service."""
        return kt_service.batch_predict(*args, **kwargs)

    # 维护意图：Delegate recommendation generation to the shared KT service
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_learning_recommendations(*args, **kwargs):
        """Delegate recommendation generation to the shared KT service."""
        return kt_service.get_learning_recommendations(*args, **kwargs)

    # 维护意图：Return KT model metadata enriched with the bundled public dataset catalog
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_model_info() -> dict:
        """Return KT model metadata enriched with the bundled public dataset catalog."""
        info = kt_service.get_model_info()
        info["default_public_dataset"] = DEFAULT_PUBLIC_DATASET
        info["public_datasets"] = list_public_datasets()
        return info


knowledge_tracing_facade = KnowledgeTracingFacade()

