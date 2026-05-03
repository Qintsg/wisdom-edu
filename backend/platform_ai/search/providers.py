"""外部学习资源检索适配层。"""

from __future__ import annotations

from functools import lru_cache

from ai_services.services.web_search_service import search_learning_resources


# 维护意图：统一外部检索入口。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExternalSearchProvider:
    """
    统一外部检索入口。

    当前仍复用现有网页搜索服务，但把调用点集中到一层，
    便于后续替换为更稳定的 provider、缓存和重排策略。
    """

    # 维护意图：检索与指定知识点相关的外部学习资源
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @lru_cache(maxsize=256)
    def search_learning_resources(
        self,
        point_name: str,
        course_name: str | None = None,
        count: int = 5,
    ) -> list[dict]:
        """检索与指定知识点相关的外部学习资源。"""

        return search_learning_resources(
            point_name=point_name,
            course_name=course_name,
            count=count,
        )


external_search_provider = ExternalSearchProvider()

