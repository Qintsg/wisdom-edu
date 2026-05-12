"""学生学习资源推荐的 MCP 工具适配层。

该模块把项目内课程资源检索和 Tavily 外部网页搜索收束成稳定服务。
调用方仍只消费结构化资源列表，避免在视图层或 RAG 编排层直接散落
外部服务细节。
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
import logging
import re
from urllib.parse import urlparse

from django.conf import settings
import requests

from knowledge.models import KnowledgePoint, Resource
from learning.models import PathNode
from platform_ai.rag.resource_utils import (
    normalize_resource_match_text as _normalize_match_text,
    resource_rank_key as _resource_rank_key,
    safe_resource_url as _safe_resource_url,
    score_resource_point_match as _score_resource_point_match,
)


logger = logging.getLogger(__name__)

WHITESPACE_PATTERN = re.compile(r"\s+")
EXTERNAL_REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def _coerce_text(value: object) -> str:
    """将外部 JSON 或模型字段规整为单行文本。"""

    return WHITESPACE_PATTERN.sub(" ", str(value or "")).strip()


def _resource_id(resource: Resource) -> int:
    """读取资源主键，兼容测试中的轻量对象。"""

    try:
        return int(getattr(resource, "id", 0) or 0)
    except (TypeError, ValueError):
        return 0


def _mastery_stage(student_mastery: float | None) -> str:
    """将掌握度映射为资源难度阶段。"""

    if student_mastery is None:
        return "初学"
    if student_mastery < 0.4:
        return "入门"
    if student_mastery < 0.6:
        return "巩固"
    if student_mastery < 0.8:
        return "提高"
    return "拓展"


def _is_valid_http_url(url: str) -> bool:
    """过滤空 URL、搜索页锚点和非 HTTP 协议。"""

    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _domain_from_url(url: str) -> str:
    """提取资源来源域名。"""

    return urlparse(url).netloc.lower().removeprefix("www.")


def _guess_resource_type(url: str, title: str = "") -> str:
    """根据域名和标题粗略判断外部资源类型。"""

    host = _domain_from_url(url)
    title_text = _coerce_text(title).lower()
    if any(domain in host for domain in ("bilibili.com", "youtube.com", "icourse163.org", "coursera.org")):
        return "video"
    if any(domain in host for domain in ("docs.", "developer.", "runoob.com", "w3school", "mozilla.org")):
        return "document"
    if "exercise" in title_text or "练习" in title_text or "题" in title_text:
        return "exercise"
    return "link"


def _truncate_text(value: str, limit: int = 360) -> str:
    """限制摘要长度，避免把整页正文带入 API 响应。"""

    text = _coerce_text(value)
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


@dataclass(frozen=True)
class InternalResourceCandidate:
    """项目内资源 MCP 检索结果。"""

    resource: Resource
    score: int
    source: str

    @property
    def resource_id(self) -> int:
        """返回资源主键。"""

        return _resource_id(self.resource)


@dataclass(frozen=True)
class ExternalResourceCandidate:
    """Tavily MCP 外部资源结果。"""

    title: str
    url: str
    resource_type: str
    source: str
    provider: str
    snippet: str
    reason: str
    learning_tips: str

    def to_response(self) -> dict[str, object]:
        """转换为学生端资源推荐 API 的响应结构。"""

        external_id = sha1(self.url.encode("utf-8")).hexdigest()[:16]
        return {
            "resource_id": f"external:mcp:{external_id}",
            "title": self.title,
            "url": self.url,
            "type": self.resource_type,
            "description": self.snippet,
            "recommended_reason": self.reason,
            "learning_tips": self.learning_tips,
            "source": self.source,
            "provider": self.provider,
            "is_internal": False,
            "completed": False,
            "required": False,
        }


class LearningResourceMCPService:
    """学习资源 MCP 编排服务。"""

    def __init__(self, session: requests.Session | None = None) -> None:
        """初始化 HTTP 会话，便于测试替换外部请求。"""

        self.session = session or requests.Session()

    def search_internal_resources(
        self,
        *,
        node: PathNode,
        point: KnowledgePoint,
        mastery_value: float | None,
        limit: int = 12,
    ) -> list[InternalResourceCandidate]:
        """搜索项目内课程、节点和知识点绑定资源。"""

        if limit <= 0:
            return []

        candidate_resources: dict[int, Resource] = {}
        resource_scores: dict[int, int] = {}
        resource_sources: dict[int, str] = {}

        for bound_resource in node.resources.filter(is_visible=True).order_by("sort_order", "id"):
            resource_id = _resource_id(bound_resource)
            if resource_id <= 0:
                continue
            candidate_resources[resource_id] = bound_resource
            resource_scores[resource_id] = max(resource_scores.get(resource_id, 0), 1000)
            resource_sources[resource_id] = "path_node"

        for linked_resource in Resource.objects.filter(knowledge_points=point, is_visible=True).order_by("sort_order", "id"):
            resource_id = _resource_id(linked_resource)
            if resource_id <= 0:
                continue
            candidate_resources.setdefault(resource_id, linked_resource)
            resource_scores[resource_id] = max(resource_scores.get(resource_id, 0), 900)
            resource_sources.setdefault(resource_id, "knowledge_point")

        unmatched_course_resources: list[Resource] = []
        course = getattr(getattr(node, "path", None), "course", None)
        for course_resource in list(Resource.objects.filter(course=course, is_visible=True).order_by("sort_order", "id")[:80]):
            resource_id = _resource_id(course_resource)
            if resource_id <= 0 or resource_id in candidate_resources:
                continue
            match_score = _score_resource_point_match(course_resource, point)
            if match_score > 0:
                candidate_resources[resource_id] = course_resource
                resource_scores[resource_id] = match_score
                resource_sources[resource_id] = "course_text_match"
            elif len(unmatched_course_resources) < limit:
                unmatched_course_resources.append(course_resource)

        if not candidate_resources:
            for course_resource in unmatched_course_resources:
                resource_id = _resource_id(course_resource)
                if resource_id <= 0:
                    continue
                candidate_resources[resource_id] = course_resource
                resource_scores[resource_id] = 1
                resource_sources[resource_id] = "course_fallback"

        ordered_resources = sorted(
            candidate_resources.values(),
            key=lambda resource: (
                -resource_scores.get(_resource_id(resource), 0),
                *_resource_rank_key(resource, mastery_value),
            ),
        )
        return [
            InternalResourceCandidate(
                resource=resource,
                score=resource_scores.get(_resource_id(resource), 0),
                source=resource_sources.get(_resource_id(resource), "course"),
            )
            for resource in ordered_resources[:limit]
        ]

    def search_external_resources(
        self,
        *,
        point_name: str,
        student_mastery: float | None,
        existing_titles: list[str],
        course_name: str | None,
        count: int,
    ) -> list[ExternalResourceCandidate]:
        """使用 Tavily 搜索外部学习资源。"""

        if count <= 0 or not self._external_search_enabled():
            return []

        return self._search_with_tavily(
            point_name=point_name,
            student_mastery=student_mastery,
            existing_titles=existing_titles,
            course_name=course_name,
            count=count,
        )

    def _external_search_enabled(self) -> bool:
        """判断外部 MCP 搜索是否具备必要配置。"""

        return bool(
            getattr(settings, "RESOURCE_MCP_ENABLED", True)
            and _coerce_text(getattr(settings, "TAVILY_API_KEY", ""))
        )

    def _build_search_query(
        self,
        *,
        point_name: str,
        student_mastery: float | None,
        course_name: str | None,
    ) -> str:
        """构造面向学习资源的 Tavily 查询。"""

        stage = _mastery_stage(student_mastery)
        course_prefix = f"{course_name} " if course_name else ""
        return f"{course_prefix}{point_name} {stage} 学习资源 教程 示例 官方文档"

    def _search_with_tavily(
        self,
        *,
        point_name: str,
        student_mastery: float | None,
        existing_titles: list[str],
        course_name: str | None,
        count: int,
    ) -> list[ExternalResourceCandidate]:
        """调用 Tavily Search API 返回候选资源。"""

        query = self._build_search_query(
            point_name=point_name,
            student_mastery=student_mastery,
            course_name=course_name,
        )
        max_results = max(count, int(getattr(settings, "TAVILY_MAX_RESULTS", max(6, count * 2))))
        payload = {
            "query": query,
            "search_depth": _coerce_text(getattr(settings, "TAVILY_SEARCH_DEPTH", "basic")) or "basic",
            "max_results": min(max_results, 20),
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
        }
        headers = {
            **EXTERNAL_REQUEST_HEADERS,
            "Authorization": f"Bearer {_coerce_text(getattr(settings, 'TAVILY_API_KEY', ''))}",
        }

        try:
            response = self.session.post(
                _coerce_text(getattr(settings, "TAVILY_SEARCH_URL", "https://api.tavily.com/search"))
                or "https://api.tavily.com/search",
                headers=headers,
                json=payload,
                timeout=int(getattr(settings, "RESOURCE_MCP_TIMEOUT_SECONDS", 12)),
            )
            response.raise_for_status()
            response_payload = response.json()
        except Exception as exc:
            logger.warning("Tavily 学习资源搜索失败: point=%s error=%s", point_name, exc)
            return []

        raw_results = response_payload.get("results") if isinstance(response_payload, dict) else []
        if not isinstance(raw_results, list):
            return []

        seen_urls: set[str] = set()
        existing_title_set = {_normalize_match_text(title) for title in existing_titles if _coerce_text(title)}
        candidates: list[ExternalResourceCandidate] = []
        stage = _mastery_stage(student_mastery)
        for raw_item in raw_results:
            if not isinstance(raw_item, dict):
                continue
            title = _coerce_text(raw_item.get("title"))
            url = _coerce_text(raw_item.get("url"))
            if not title or not _is_valid_http_url(url):
                continue
            normalized_url = url.split("#", 1)[0]
            if normalized_url in seen_urls or _normalize_match_text(title) in existing_title_set:
                continue
            seen_urls.add(normalized_url)
            snippet = self._extract_tavily_snippet(raw_item)
            candidates.append(
                ExternalResourceCandidate(
                    title=title,
                    url=normalized_url,
                    resource_type=_guess_resource_type(normalized_url, title),
                    source=_domain_from_url(normalized_url),
                    provider="tavily",
                    snippet=snippet,
                    reason=f"Tavily 搜索命中该资源，内容与“{point_name}”相关，适合{stage}阶段补充学习。",
                    learning_tips="建议先完成课程内资源，再打开该外部资料对照示例复习。",
                )
            )
            if len(candidates) >= count:
                break
        return candidates

    def _extract_tavily_snippet(self, raw_item: dict[str, object]) -> str:
        """从 Tavily 响应中提取摘要。"""

        return _truncate_text(_coerce_text(raw_item.get("content") or raw_item.get("raw_content")))


resource_mcp_service = LearningResourceMCPService()
