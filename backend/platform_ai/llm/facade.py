"""LLM 门面层。"""

from __future__ import annotations

from functools import lru_cache

from ai_services.services.llm_service import LLMService


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    """返回缓存后的底层 LLM 服务实例。"""
    return LLMService()


class LLMFacade:
    """对编排层暴露稳定的 LLM 能力，底层由 agent-backed LLMService 承载。"""

    @property
    def service(self) -> LLMService:
        """返回缓存后的底层 LLM 服务实例。"""
        return get_llm_service()

    @property
    def is_available(self) -> bool:
        """返回当前 LLM 能力是否可用。"""
        return self.service.is_available

    def analyze_profile(self, *args, **kwargs):
        """分析学习者画像并生成结构化结论。"""
        return self.service.analyze_profile(*args, **kwargs)

    def plan_learning_path(self, *args, **kwargs):
        """规划个性化学习路径。"""
        return self.service.plan_learning_path(*args, **kwargs)

    def generate_resource_reason(self, *args, **kwargs):
        """生成资源推荐理由说明。"""
        return self.service.generate_resource_reason(*args, **kwargs)

    def generate_feedback_report(self, *args, **kwargs):
        """生成考试或阶段反馈报告。"""
        return self.service.generate_feedback_report(*args, **kwargs)

    def recommend_internal_resources(self, *args, **kwargs):
        """推荐站内学习资源。"""
        return self.service.recommend_internal_resources(*args, **kwargs)

    def recommend_external_resources(self, *args, **kwargs):
        """推荐站外学习资源。"""
        return self.service.recommend_external_resources(*args, **kwargs)

    def call_with_fallback(self, *args, **kwargs):
        """通过公共入口执行带降级保护的 LLM 调用。"""
        return self.service.call_with_fallback(*args, **kwargs)


llm_facade = LLMFacade()
