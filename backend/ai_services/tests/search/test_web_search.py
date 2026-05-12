"""Regression tests for AI-facing student and search services."""

from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from ai_services.services.search.web_search import (
    SEARCH_PROVIDERS,
    _search_with_provider,
    search_learning_resources,
)


class WebSearchServiceTests(SimpleTestCase):
    """Cover provider ordering and redirect filtering for resource search."""

    @patch("ai_services.services.search.web_search.requests.get")
    def test_search_with_baidu_should_resolve_redirect_and_filter_domain(
        self, mock_get
    ):
        """Baidu redirect links should resolve to the expected destination domain."""
        search_response = Mock()
        search_response.raise_for_status.return_value = None
        search_response.text = (
            "<html><body>"
            '<a href="https://www.baidu.com/link?url=demo123">大数据技术基础 - 菜鸟教程</a>'
            '<a href="https://www.baidu.com/link?url=other456">无关结果</a>'
            "</body></html>"
        )

        redirect_response = Mock()
        redirect_response.url = "https://www.runoob.com/hadoop/hadoop-tutorial.html"
        redirect_response.close.return_value = None

        other_redirect_response = Mock()
        other_redirect_response.url = "https://example.com/other"
        other_redirect_response.close.return_value = None

        mock_get.side_effect = [
            search_response,
            redirect_response,
            other_redirect_response,
        ]

        results = _search_with_provider(
            provider_name="baidu",
            query="大数据技术基础 site:runoob.com",
            expected_domain="runoob.com",
            max_results=3,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["url"], "https://www.runoob.com/hadoop/hadoop-tutorial.html"
        )
        self.assertIn("菜鸟教程", results[0]["title"])

    @patch(
        "ai_services.services.search.web_search._is_accessible_url", return_value=True
    )
    @patch("ai_services.services.search.web_search._search_with_provider")
    def test_search_learning_resources_should_use_configured_engines_in_order(
        self, mock_search_with_provider, _mock_accessible
    ):
        """Configured providers should be queried in priority order until one succeeds."""
        provider_calls = []
        configured_providers = [name for name, _ in SEARCH_PROVIDERS]
        primary_provider = configured_providers[0]
        fallback_provider = configured_providers[1]

        def side_effect(provider_name, query, expected_domain, max_results):
            """Return a single mocked hit only for the configured fallback provider."""
            # 显式消费关键字参数，保留真实调用签名并避免未使用形参告警。
            _ = (query, expected_domain, max_results)
            provider_calls.append(provider_name)
            if provider_name == primary_provider:
                return []
            if provider_name == fallback_provider:
                return [
                    {
                        "title": "大数据技术基础 - B站讲解",
                        "url": "https://www.bilibili.com/video/BV1demo",
                        "snippet": "示例摘要",
                    }
                ]
            return []

        mock_search_with_provider.side_effect = side_effect

        results = search_learning_resources(
            point_name="大数据技术基础",
            course_name="大数据技术与应用",
            count=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "bilibili.com")
        self.assertEqual(provider_calls[:2], [primary_provider, fallback_provider])
        self.assertEqual(set(provider_calls), {primary_provider, fallback_provider})
