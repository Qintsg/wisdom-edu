"""外部学习资源检索适配层。"""

from __future__ import annotations

from functools import lru_cache

from platform_ai.mcp.resources import resource_mcp_service


class ExternalSearchProvider:
    """
    统一外部检索入口。

    当前统一复用学习资源 MCP 的 Tavily 外部搜索能力，避免新调用点绕回
    旧的网页搜索抓取逻辑。
    """

    @lru_cache(maxsize=256)
    def search_learning_resources(
        self,
        point_name: str,
        course_name: str | None = None,
        count: int = 5,
    ) -> list[dict]:
        """检索与指定知识点相关的外部学习资源。"""

        candidates = resource_mcp_service.search_external_resources(
            point_name=point_name,
            student_mastery=None,
            existing_titles=[],
            course_name=course_name,
            count=count,
        )
        return [
            {
                "title": candidate.title,
                "url": candidate.url,
                "snippet": candidate.snippet,
                "source": candidate.source,
                "type": candidate.resource_type,
                "provider": candidate.provider,
            }
            for candidate in candidates[:count]
        ]


external_search_provider = ExternalSearchProvider()

