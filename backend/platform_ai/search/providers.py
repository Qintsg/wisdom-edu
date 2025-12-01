"""外部学习资源检索适配层。"""

from __future__ import annotations

from functools import lru_cache

from ai_services.services.web_search_service import search_learning_resources


class ExternalSearchProvider:
    """
    统一外部检索入口。

    当前仍复用现有网页搜索服务，但把调用点集中到一层，
    便于后续替换为更稳定的 provider、缓存和重排策略。
    """

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

