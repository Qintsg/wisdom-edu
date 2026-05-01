"""LangChain agent orchestration for structured LLM tasks."""

from __future__ import annotations

from functools import lru_cache
import json
import logging
import re

from django.conf import settings

from courses.models import Course
from knowledge.models import KnowledgePoint, KnowledgeMastery

logger = logging.getLogger(__name__)

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _parse_json_payload(content: str) -> dict:
    """Best-effort JSON extraction for agent replies that contain extra wrapping."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Some providers wrap valid JSON in markdown fences even when instructed not
    # to, so inspect fenced blocks before falling back to brace slicing.
    for match in JSON_BLOCK_RE.findall(content or ""):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    start = (content or "").find("{")
    end = (content or "").rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}


def _trim_graph_sources(raw_sources: object, limit: int = 4) -> list[dict[str, object]]:
    """Normalize GraphRAG sources into a compact JSON-safe payload for agent tools."""
    if not isinstance(raw_sources, list):
        return []

    normalized_sources: list[dict[str, object]] = []
    for item in raw_sources:
        if not isinstance(item, dict):
            continue
        normalized_sources.append(
            {
                "id": str(item.get("id", "")).strip(),
                "title": str(item.get("title", "")).strip() or "课程证据",
                "kind": str(item.get("kind", "")).strip() or "document",
                "excerpt": str(item.get("excerpt", "")).strip(),
                "query_mode": str(item.get("query_mode", "")).strip(),
                "retrieval_source": str(item.get("retrieval_source", "")).strip(),
            }
        )
        if len(normalized_sources) >= limit:
            break
    return normalized_sources


def _build_point_graphrag_payload(course_id: int, point: KnowledgePoint) -> dict[str, object]:
    """Fetch a compact GraphRAG summary for a single knowledge point."""
    try:
        from platform_ai.rag.student import student_learning_rag

        payload = student_learning_rag.build_point_support_payload(
            course_id=course_id,
            point=point,
        )
    except Exception as exc:
        logger.warning(
            "LangChain agent point GraphRAG support failed: course=%s point=%s error=%s",
            course_id,
            point.id,
            exc,
        )
        return {}

    generated_summary = str(payload.get("summary", "")).strip()
    if not generated_summary and not payload.get("sources"):
        return {}

    return {
        "summary": generated_summary,
        "mode": str(payload.get("mode", "")).strip() or "graph_rag",
        "sources": _trim_graph_sources(payload.get("sources"), limit=3),
    }


def _build_course_graphrag_payload(
    *,
    course_id: int,
    query: str,
    point_id: int | None = None,
    limit: int = 4,
) -> dict[str, object]:
    """Query GraphRAG on demand so the agent can ground course-specific answers."""
    normalized_query = query.strip()
    point_name = ""
    if point_id:
        point = KnowledgePoint.objects.filter(id=point_id, course_id=course_id).first()
        if point:
            point_name = point.name

    if not normalized_query:
        return {
            "course_id": course_id,
            "point_id": point_id,
            "point_name": point_name,
            "query": "",
            "mode": "",
            "query_modes": [],
            "tools_selected": [],
            "generated_cypher": "",
            "context": "",
            "sources": [],
            "matched_point_ids": [],
        }

    try:
        from platform_ai.rag.runtime import student_graphrag_runtime

        payload = student_graphrag_runtime.query_graph(
            course_id=course_id,
            query=normalized_query,
            focus_point_id=point_id,
            focus_point_name=point_name,
            limit=max(limit, 3),
        )
    except Exception as exc:
        logger.warning(
            "LangChain agent course GraphRAG query failed: course=%s point=%s error=%s",
            course_id,
            point_id,
            exc,
        )
        payload = {}

    raw_modes = payload.get("query_modes") if isinstance(payload, dict) else []
    raw_tools = payload.get("tools_selected") if isinstance(payload, dict) else []
    raw_points = payload.get("matched_point_ids") if isinstance(payload, dict) else []
    return {
        "course_id": course_id,
        "point_id": point_id,
        "point_name": point_name,
        "query": normalized_query,
        "mode": str(payload.get("mode", "")).strip() if isinstance(payload, dict) else "",
        "query_modes": [
            str(mode).strip()
            for mode in raw_modes
            if str(mode).strip()
        ]
        if isinstance(raw_modes, list)
        else [],
        "tools_selected": [
            str(tool_name).strip()
            for tool_name in raw_tools
            if str(tool_name).strip()
        ]
        if isinstance(raw_tools, list)
        else [],
        "generated_cypher": (
            str(payload.get("generated_cypher", "")).strip()
            if isinstance(payload, dict)
            else ""
        ),
        "context": str(payload.get("context", "")).strip() if isinstance(payload, dict) else "",
        "sources": _trim_graph_sources(
            payload.get("sources") if isinstance(payload, dict) else [],
            limit=limit,
        ),
        "matched_point_ids": [
            point_pk
            for point_pk in raw_points
            if isinstance(point_pk, int) and point_pk > 0
        ]
        if isinstance(raw_points, list)
        else [],
    }


class LangChainAgentService:
    """Thin agent wrapper used by legacy LLMService for structured outputs."""

    SUPPORTED_API_FORMATS = {
        "openai",
        "openai-compatible",
        "openai_compatible",
        "chat-completions",
    }

    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str,
        api_format: str = "openai-compatible",
        temperature: float = 0.3,
        request_timeout: int = 120,
        max_retries: int = 2,
        proxy_url: str = "",
        reasoning_enabled: bool = False,
        reasoning_effort: str = "",
        extra_body: dict[str, object] | None = None,
    ):
        """Store model connection settings and defer heavy LangChain setup."""
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.api_format = api_format
        self.temperature = temperature
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.proxy_url = proxy_url
        self.reasoning_enabled = reasoning_enabled
        self.reasoning_effort = reasoning_effort
        self.extra_body = dict(extra_body or {})
        self._model = None
        self._agent = None

    @property
    def is_available(self) -> bool:
        """Return whether provider credentials are available for agent invocation."""
        return bool(self.api_key)

    def _get_model(self):
        """Instantiate the compatible chat client lazily for the configured provider."""
        if self._model is not None or not self.is_available:
            return self._model
        try:
            normalized_format = self.api_format.replace("_", "-").lower()
            if normalized_format not in self.SUPPORTED_API_FORMATS:
                logger.warning(
                    "LangChain agent model format unsupported: format=%s model=%s",
                    self.api_format,
                    self.model_name,
                )
                return None

            from langchain_openai import ChatOpenAI

            model_kwargs = {
                "model": self.model_name,
                "temperature": self.temperature,
                "api_key": self.api_key,
                "base_url": self.base_url,
                "openai_proxy": self.proxy_url or None,
                "request_timeout": self.request_timeout,
                "max_retries": self.max_retries,
            }
            if self.extra_body:
                model_kwargs["extra_body"] = self.extra_body
            if self.reasoning_enabled and self.reasoning_effort:
                model_kwargs["reasoning_effort"] = self.reasoning_effort
            self._model = ChatOpenAI(**model_kwargs)
        except Exception as exc:
            logger.warning("LangChain agent model init failed: %s", exc)
            self._model = None
        return self._model

    def _get_tools(self):
        """Create the minimal grounding tools exposed to the agent runtime."""
        try:
            from langchain.tools import tool
        except Exception as exc:
            logger.warning("LangChain tools import failed: %s", exc)
            return []

        @tool
        def lookup_course_context(course_id: int, point_id: int | None = None) -> str:
            """Look up course and optional knowledge point context."""
            course = Course.objects.filter(id=course_id).first()
            if not course:
                return "课程不存在"
            if not point_id:
                return json.dumps(
                    {"course_id": course.id, "course_name": course.name},
                    ensure_ascii=False,
                )

            point = KnowledgePoint.objects.filter(id=point_id, course_id=course_id).first()
            if not point:
                return json.dumps(
                    {"course_id": course.id, "course_name": course.name, "point_missing": True},
                    ensure_ascii=False,
                )
            payload = {
                "course_id": course.id,
                "course_name": course.name,
                "point_id": point.id,
                "point_name": point.name,
                "description": point.description or "",
                "chapter": point.chapter or "",
            }
            graph_support = _build_point_graphrag_payload(course_id=course_id, point=point)
            if graph_support:
                payload["graph_rag"] = graph_support
            return json.dumps(payload, ensure_ascii=False)

        @tool
        def query_course_graphrag(
            course_id: int,
            query: str,
            point_id: int | None = None,
            limit: int = 4,
        ) -> str:
            """Retrieve GraphRAG evidence for a course or knowledge-point question."""
            payload = _build_course_graphrag_payload(
                course_id=course_id,
                query=query,
                point_id=point_id,
                limit=limit,
            )
            return json.dumps(payload, ensure_ascii=False)

        @tool
        def summarize_mastery(user_id: int, course_id: int) -> str:
            """Summarize learner mastery for a course."""
            rows = list(
                KnowledgeMastery.objects.filter(user_id=user_id, course_id=course_id)
                .select_related("knowledge_point")
                .order_by("mastery_rate")[:12]
            )
            payload = [
                {
                    "point_id": row.knowledge_point_id,
                    "point_name": row.knowledge_point.name if row.knowledge_point else "",
                    "mastery_rate": float(row.mastery_rate),
                }
                for row in rows
            ]
            return json.dumps(payload, ensure_ascii=False)

        return [
            lookup_course_context,
            query_course_graphrag,
            summarize_mastery,
        ]

    def _get_agent(self):
        """Build and cache the LangChain agent instance on first successful use."""
        if self._agent is not None or not self.is_available:
            return self._agent
        model = self._get_model()
        if model is None:
            return None
        try:
            from langchain.agents import create_agent

            self._agent = create_agent(
                model=model,
                tools=self._get_tools(),
                system_prompt=(
                    "You are an educational AI agent. "
                    "For course-scoped or knowledge-point questions, query GraphRAG evidence before answering. "
                    "For external learning resources, rely on provider-native web access when available instead of local search tools. "
                    "Use tools only when they materially improve factual grounding. "
                    "Always return valid JSON only."
                ),
            )
        except Exception as exc:
            logger.warning("LangChain agent init failed: %s", exc)
            self._agent = None
        return self._agent

    def invoke_json(self, *, call_type: str, prompt: str, fallback_response: dict) -> dict:
        """Invoke the agent and coerce its final answer into the expected JSON shape."""
        agent = self._get_agent()
        if agent is None:
            return fallback_response

        user_prompt = (
            f"任务类型：{call_type}\n"
            "请严格输出合法 JSON，不要输出解释、代码块标题或额外文本。\n"
            f"目标返回结构示例：{json.dumps(fallback_response, ensure_ascii=False)}\n\n"
            f"{prompt}"
        )
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})
            messages = result.get("messages", []) if isinstance(result, dict) else []
            content = ""
            if messages:
                last_message = messages[-1]
                # LangChain message content can be a string or a list of content
                # parts depending on provider adapters and tool execution traces.
                content = getattr(last_message, "content", "") or ""
                if isinstance(content, list):
                    parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("text"):
                            parts.append(item["text"])
                        elif isinstance(item, str):
                            parts.append(item)
                    content = "\n".join(parts)
            parsed = _parse_json_payload(content)
            return parsed or fallback_response
        except Exception as exc:
            logger.warning("LangChain agent invoke failed for %s: %s", call_type, exc)
            return fallback_response


@lru_cache(maxsize=8)
def get_agent_service(
    model_name: str,
    api_key: str,
    base_url: str,
    api_format: str = "openai-compatible",
    temperature: float = 0.3,
    request_timeout: int = 120,
    max_retries: int = 2,
    proxy_url: str = "",
    reasoning_enabled: bool = False,
    reasoning_effort: str = "",
    extra_body_json: str = "{}",
) -> LangChainAgentService:
    """Reuse a small pool of agent service instances per provider configuration."""
    try:
        parsed_extra_body = json.loads(extra_body_json or "{}")
    except json.JSONDecodeError:
        parsed_extra_body = {}
    extra_body = parsed_extra_body if isinstance(parsed_extra_body, dict) else {}
    return LangChainAgentService(
        model_name=model_name,
        api_key=api_key,
        base_url=base_url,
        api_format=api_format,
        temperature=temperature,
        request_timeout=request_timeout,
        max_retries=max_retries,
        proxy_url=proxy_url,
        reasoning_enabled=reasoning_enabled,
        reasoning_effort=reasoning_effort,
        extra_body=extra_body,
    )


def get_default_agent_service() -> LangChainAgentService:
    """Resolve the default provider credentials from Django settings."""
    from ai_services.services.llm_service import LLMService, resolve_llm_proxy_for_base_url

    llm_service = LLMService()
    return get_agent_service(
        model_name=llm_service.model_name,
        api_key=llm_service.resolved_api_key,
        base_url=llm_service.resolved_base_url,
        api_format=llm_service.api_format,
        temperature=llm_service.temperature,
        request_timeout=int(getattr(settings, "LLM_REQUEST_TIMEOUT", 120) or 120),
        max_retries=int(getattr(settings, "LLM_MAX_RETRIES", 2) or 2),
        proxy_url=resolve_llm_proxy_for_base_url(llm_service.resolved_base_url),
        reasoning_enabled=bool(getattr(settings, "LLM_REASONING_ENABLED", False)),
        reasoning_effort=str(getattr(settings, "LLM_REASONING_EFFORT", "") or ""),
        extra_body_json=json.dumps(
            llm_service.resolved_extra_body,
            ensure_ascii=False,
            sort_keys=True,
        ),
    )
