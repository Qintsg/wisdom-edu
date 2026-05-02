"""LangChain agent orchestration for structured LLM tasks."""

from __future__ import annotations

from functools import lru_cache
import json
import logging

from django.conf import settings

from knowledge.models import KnowledgeMastery
from platform_ai.llm.agent_support import (
    build_course_graphrag_payload,
    build_lookup_course_context_payload,
    extract_agent_message_text,
    parse_json_payload,
)

logger = logging.getLogger(__name__)


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
            payload = build_lookup_course_context_payload(course_id, point_id)
            if payload.get("message") == "课程不存在":
                return "课程不存在"
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
            parsed = parse_json_payload(extract_agent_message_text(messages))
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
