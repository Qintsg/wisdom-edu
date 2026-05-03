"""
轻量级联网搜索服务

用于为学习资源推荐提供真实网页检索结果，避免 LLM 直接臆造链接。
"""

from __future__ import annotations

import html
import logging
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, unquote, urlparse

import requests

logger = logging.getLogger(__name__)


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

ALLOWED_DOMAINS = [
    ("bilibili.com", "video"),
    ("icourse163.org", "video"),
    ("runoob.com", "document"),
    ("w3schools.com", "document"),
    ("developer.mozilla.org", "document"),
    ("docs.python.org", "document"),
]

SEARCH_PROVIDERS: List[Tuple[str, str]] = [
    ("baidu", "https://www.baidu.com/s?wd={query}"),
    ("bing", "https://www.bing.com/search?q={query}&setlang=zh-cn"),
]

ANCHOR_PATTERN = re.compile(
    r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL
)
TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")
SEARCH_ENGINE_HOST_KEYWORDS = ("baidu.com", "bing.com")


# 维护意图：clean html text
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _clean_html_text(value: str) -> str:
    if not value:
        return ""
    text = TAG_PATTERN.sub(" ", value)
    text = html.unescape(text)
    return WHITESPACE_PATTERN.sub(" ", text).strip()


# 维护意图：normalize candidate url
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _normalize_candidate_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    if raw_url.startswith("//"):
        return f"https:{raw_url}"
    return html.unescape(unquote(raw_url)).strip()


# 维护意图：guess resource type
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _guess_resource_type(url: str, fallback: str = "link") -> str:
    host = urlparse(url).netloc.lower()
    if "bilibili.com" in host or "icourse163.org" in host:
        return "video"
    if any(
        domain in host
        for domain in ["runoob.com", "w3schools.com", "mozilla.org", "python.org"]
    ):
        return "document"
    return fallback


# 维护意图：is accessible url
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _is_accessible_url(url: str, timeout: int = 5) -> bool:
    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
            stream=True,
        )
        ok = response.status_code < 400
        response.close()
        return ok
    except Exception as exc:
        logger.debug("URL 可达性检查失败: %s, %s", url, exc)
        return False


# 维护意图：is search engine url
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _is_search_engine_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(keyword in host for keyword in SEARCH_ENGINE_HOST_KEYWORDS)


# 维护意图：matches expected domain
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _matches_expected_domain(url: str, expected_domain: str) -> bool:
    host = urlparse(url).netloc.lower()
    normalized = expected_domain.lower()
    return host == normalized or host.endswith(f".{normalized}")


# 维护意图：resolve result url
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _resolve_result_url(raw_url: str, timeout: int = 8) -> str:
    normalized = _normalize_candidate_url(raw_url)
    if not normalized:
        return ""

    parsed = urlparse(normalized)
    if parsed.scheme not in ("http", "https"):
        return ""

    if not _is_search_engine_url(normalized):
        return normalized

    try:
        response = requests.get(
            normalized,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
            stream=True,
        )
        final_url = response.url or normalized
        response.close()
        if (
            final_url
            and urlparse(final_url).scheme in ("http", "https")
            and not _is_search_engine_url(final_url)
        ):
            return final_url
    except Exception as exc:
        logger.debug("搜索结果跳转解析失败: %s, %s", normalized, exc)

    return normalized


# 维护意图：search with provider
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _search_with_provider(
    provider_name: str,
    query: str,
    expected_domain: str,
    max_results: int = 5,
) -> List[Dict[str, str]]:
    provider_map = {name: template for name, template in SEARCH_PROVIDERS}
    if provider_name not in provider_map:
        raise ValueError(f"未知搜索源: {provider_name}")

    search_url = provider_map[provider_name].format(query=quote_plus(query))
    response = requests.get(search_url, headers=DEFAULT_HEADERS, timeout=12)
    response.raise_for_status()
    body = response.text

    results: List[Dict[str, str]] = []
    seen_urls = set()
    for match in ANCHOR_PATTERN.finditer(body):
        title = _clean_html_text(match.group(2))
        raw_url = _normalize_candidate_url(match.group(1))
        if not title or not raw_url:
            continue
        if len(title) < 4:
            continue
        if raw_url.startswith("#") or raw_url.lower().startswith("javascript:"):
            continue

        resolved_url = _resolve_result_url(raw_url)
        if not resolved_url:
            continue
        if not _matches_expected_domain(resolved_url, expected_domain):
            continue

        normalized_url = resolved_url.split("#")[0]
        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        results.append(
            {
                "title": title,
                "url": normalized_url,
                "snippet": "",
            }
        )
        if len(results) >= max_results:
            break

    return results


# 维护意图：搜索与知识点相关的真实外部学习资源。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def search_learning_resources(
    point_name: str, course_name: Optional[str] = None, count: int = 8
) -> List[Dict[str, str]]:
    """
    搜索与知识点相关的真实外部学习资源。

    返回的数据结构：
    [
        {
            'title': '资源标题',
            'url': 'https://...',
            'snippet': '摘要',
            'source': 'bilibili.com',
            'type': 'video'
        }
    ]
    """
    search_prefix = f"{course_name} {point_name}".strip()
    seen_urls = set()
    results: List[Dict[str, str]] = []

    for domain, resource_type in ALLOWED_DOMAINS:
        query = f"{search_prefix} site:{domain}"
        domain_results: List[Dict[str, str]] = []
        for provider_name, _ in SEARCH_PROVIDERS:
            try:
                domain_results = _search_with_provider(
                    provider_name=provider_name,
                    query=query,
                    expected_domain=domain,
                    max_results=3,
                )
            except Exception as exc:
                logger.warning(
                    "外部资源搜索失败: engine=%s, query=%s, error=%s",
                    provider_name,
                    query,
                    exc,
                )
                continue

            if domain_results:
                break

        for item in domain_results:
            normalized_url = item["url"].split("#")[0]
            if normalized_url in seen_urls:
                continue
            if not _is_accessible_url(normalized_url):
                continue

            seen_urls.add(normalized_url)
            results.append(
                {
                    "title": item["title"],
                    "url": normalized_url,
                    "snippet": item.get("snippet", ""),
                    "source": domain,
                    "type": _guess_resource_type(normalized_url, resource_type),
                }
            )
            if len(results) >= count:
                return results

    if results:
        return results

    query = quote_plus(search_prefix)
    fallback_results = [
        {
            "title": f"Bilibili 搜索：{point_name}",
            "url": f"https://search.bilibili.com/all?keyword={query}",
            "snippet": f"在 Bilibili 中检索“{search_prefix}”的相关讲解视频。",
            "source": "bilibili.com",
            "type": "video",
        },
        {
            "title": f"Bing 搜索：{point_name}",
            "url": f"https://www.bing.com/search?q={query}",
            "snippet": f"在 Bing 中检索“{search_prefix}”的公开课程资料与讲解文章。",
            "source": "bing.com",
            "type": "document",
        },
    ]
    return fallback_results[:count]

    return results
