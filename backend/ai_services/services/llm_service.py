"""
LLM服务模块 - 使用LangChain框架封装大模型调用

支持的模型：
- DeepSeek (deepseek-v4-flash, deepseek-chat, deepseek-reasoner)
- 通义千问 (qwen-plus, qwen-turbo, qwen-max)

使用示例:
    from ai_services.services import llm_service

    result = llm_service.analyze_profile(user_data)
"""

from __future__ import annotations

from importlib import import_module
import logging
import json
import os
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from django.conf import settings

from ai_services.services.llm_feedback_kt_mixin import LLMFeedbackKTMixin
from ai_services.services.llm_profile_path_mixin import LLMProfilePathMixin
from ai_services.services.llm_provider_config import (
    AGENT_ENABLED_CALL_TYPES,
    DEFAULT_MAX_PROMPT_CHARS,
    FAST_FAIL_CALL_TYPES,
    GATEWAY_SAFE_TIMEOUT_SECONDS,
    GRAPH_RAG_MAX_PROMPT_CHARS,
    LATENCY_SAFE_MAX_PROMPT_CHARS,
    LLMExecutionPolicy,
    MODEL_CONFIGS as MODEL_PROVIDER_CONFIGS,
    ModelProviderConfig,
    PROMPT_TRUNCATION_NOTICE,
    SUPPORTED_API_FORMATS,
)
from ai_services.services.llm_resource_mixin import LLMResourceMixin
from ai_services.services.llm_response_mixin import LLMResponseMixin
from common.logging_utils import build_log_message

logger = logging.getLogger(__name__)


def _read_runtime_setting(name: str) -> str:
    """Read a string setting from Django settings first, then environment variables."""
    raw_value = getattr(settings, name, "")
    if isinstance(raw_value, str) and raw_value.strip():
        return raw_value.strip()
    return os.getenv(name, "").strip()


def resolve_llm_proxy_for_base_url(base_url: str) -> str:
    """Resolve the most suitable proxy for the current LLM gateway URL."""
    normalized_base_url = (base_url or "").strip()
    parsed_scheme = urlparse(normalized_base_url).scheme.lower()
    http_proxy = _read_runtime_setting("LLM_HTTP_PROXY") or _read_runtime_setting("HTTP_PROXY")
    https_proxy = _read_runtime_setting("LLM_HTTPS_PROXY") or _read_runtime_setting("HTTPS_PROXY")
    if parsed_scheme == "http":
        return http_proxy or https_proxy
    return https_proxy or http_proxy


class LLMService(LLMProfilePathMixin, LLMResourceMixin, LLMFeedbackKTMixin, LLMResponseMixin):
    """
    大语言模型服务类。

    使用 LangChain 框架进行 LLM 调用，支持多种国产大模型。
    当未配置 API 密钥时，自动使用 Mock 响应。
    """

    MODEL_CONFIGS: dict[str, ModelProviderConfig] = MODEL_PROVIDER_CONFIGS
    SUPPORTED_API_FORMATS = SUPPORTED_API_FORMATS
    AGENT_ENABLED_CALL_TYPES = AGENT_ENABLED_CALL_TYPES
    FAST_FAIL_CALL_TYPES = FAST_FAIL_CALL_TYPES
    GATEWAY_SAFE_TIMEOUT_SECONDS = GATEWAY_SAFE_TIMEOUT_SECONDS
    DEFAULT_MAX_PROMPT_CHARS = DEFAULT_MAX_PROMPT_CHARS
    GRAPH_RAG_MAX_PROMPT_CHARS = GRAPH_RAG_MAX_PROMPT_CHARS
    LATENCY_SAFE_MAX_PROMPT_CHARS = LATENCY_SAFE_MAX_PROMPT_CHARS
    PROMPT_TRUNCATION_NOTICE = PROMPT_TRUNCATION_NOTICE
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.3):
        """
        初始化LLM服务

        Args:
            model_name: 模型名称，默认使用settings中配置的LLM_MODEL
            temperature: 生成温度，0-1之间，越高越随机
        """
        # 读取默认模型配置，并收窄为稳定的字符串模型名。
        configured_model = getattr(settings, "LLM_MODEL", "deepseek-v4-flash")
        if model_name:
            self.model_name = model_name
        elif isinstance(configured_model, str):
            self.model_name = configured_model
        else:
            self.model_name = "deepseek-v4-flash"
        self.temperature = temperature
        self._llm = None
        self._api_key = None
        self._base_url = None
        self._provider = ""
        self._api_format = getattr(settings, "LLM_API_FORMAT", "openai-compatible")
        self._request_timeout = int(getattr(settings, "LLM_REQUEST_TIMEOUT", 120) or 120)
        self._max_retries = int(getattr(settings, "LLM_MAX_RETRIES", 2) or 2)
        self._agent_service = None
        self._proxy_url = ""
        self._reasoning_enabled = bool(getattr(settings, "LLM_REASONING_ENABLED", False))
        self._reasoning_effort = str(
            getattr(settings, "LLM_REASONING_EFFORT", "") or ""
        ).strip().lower()
        self._extra_body: dict[str, Any] = {}

        # 确定模型提供商和API配置
        self._detect_provider()
        self._extra_body = self._resolve_extra_body()

    @property
    def provider_name(self) -> str:
        """返回解析后的提供方标识。"""
        return self._provider or "deepseek"

    @property
    def resolved_api_key(self) -> str:
        """返回当前实例解析后的 API Key。"""
        return self._api_key or ""

    @property
    def resolved_base_url(self) -> str:
        """返回当前实例解析后的 Base URL。"""
        return self._base_url or ""

    @property
    def api_format(self) -> str:
        """返回当前实例使用的接口格式描述。"""
        return self._api_format or "openai-compatible"

    @staticmethod
    def _read_setting(name: str) -> str:
        """优先读取 Django settings，再回退到环境变量。"""
        return _read_runtime_setting(name)

    @property
    def resolved_proxy_url(self) -> str:
        """返回当前网关将使用的代理地址。"""
        return self._proxy_url or ""

    @property
    def resolved_extra_body(self) -> dict[str, Any]:
        """返回透传给 OpenAI 兼容网关的额外请求体。"""
        return dict(self._extra_body)

    @classmethod
    def _normalize_provider_name(cls, provider_name: str) -> str:
        """标准化提供方名称，兼容常见别名。"""
        normalized_name = provider_name.strip().lower()
        alias_map = {
            "aliyun": "qwen",
            "dashscope": "qwen",
            "tongyi": "qwen",
            "ark": "doubao",
            "byteplus": "doubao",
            "byteplus-modelark": "doubao",
            "glm": "zhipu",
            "bigmodel": "zhipu",
            "moonshot": "kimi",
            "openai-compatible": "custom",
        }
        return alias_map.get(normalized_name, normalized_name)

    @classmethod
    def _provider_from_model_name(cls, model_name: str) -> str | None:
        """根据模型名前缀反推提供方。"""
        normalized_model = model_name.strip().lower()
        for provider_name, provider_config in cls.MODEL_CONFIGS.items():
            model_prefixes = provider_config.get("model_prefixes", [])
            if any(normalized_model.startswith(prefix) for prefix in model_prefixes):
                return provider_name
        return None

    @classmethod
    def _first_non_empty_setting(cls, keys: list[str]) -> str:
        """从候选设置键中返回第一个非空值。"""
        for key in keys:
            resolved_value = cls._read_setting(key)
            if resolved_value:
                return resolved_value
        return ""

    def _detect_provider(self):
        """
        检测模型提供商并设置API配置

        优先尊重显式的 LLM_PROVIDER，再回退到模型名前缀匹配。
        所有当前支持的提供方都通过 OpenAI 兼容接口接入。
        """
        explicit_provider = self._normalize_provider_name(
            self._read_setting("LLM_PROVIDER")
        )
        detected_provider = None
        if explicit_provider and explicit_provider not in {"auto", "default"}:
            detected_provider = explicit_provider
        else:
            detected_provider = self._provider_from_model_name(self.model_name)

        if detected_provider not in self.MODEL_CONFIGS:
            has_custom_gateway = bool(
                self._read_setting("LLM_API_KEY") or self._read_setting("CUSTOM_LLM_API_KEY")
            ) and bool(
                self._read_setting("LLM_BASE_URL") or self._read_setting("CUSTOM_LLM_BASE_URL")
            )
            detected_provider = "custom" if has_custom_gateway else "deepseek"

        provider_config = self.MODEL_CONFIGS[detected_provider]
        self._provider = detected_provider
        self._api_key = self._first_non_empty_setting(provider_config.get("env_keys", []))

        shared_base_url = self._read_setting("LLM_BASE_URL")
        provider_base_url = self._first_non_empty_setting(
            provider_config.get("base_url_env_keys", [])
        )
        self._base_url = shared_base_url or provider_base_url or provider_config.get("base_url", "")
        self._proxy_url = resolve_llm_proxy_for_base_url(self._base_url)

        configured_api_format = self._read_setting("LLM_API_FORMAT")
        self._api_format = configured_api_format or provider_config.get("api_format", "openai-compatible")

        logger.debug(
            build_log_message(
                "llm.provider.detected",
                provider=self._provider,
                model=self.model_name,
                api_format=self._api_format,
                base_url=self._base_url,
            )
        )

    def _resolve_extra_body(self) -> dict[str, Any]:
        """构造 OpenAI 兼容请求额外参数，默认明确关闭思考模式。"""
        configured_extra_body = getattr(settings, "LLM_EXTRA_BODY", {}) or {}
        extra_body = (
            dict(configured_extra_body)
            if isinstance(configured_extra_body, dict)
            else {}
        )
        if not self._reasoning_enabled:
            model_name = self.model_name.strip().lower()
            reasoning_sensitive = (
                self.provider_name in {"qwen", "deepseek", "custom"}
                or "thinking" in model_name
                or "reasoner" in model_name
                or "deepseek-v4" in model_name
            )
            if reasoning_sensitive:
                extra_body.setdefault("enable_thinking", False)
        return extra_body

    @staticmethod
    def _clamp_positive_int(value: int, minimum: int = 1) -> int:
        """Clamp integer settings to a positive lower bound."""
        return max(minimum, int(value))

    @classmethod
    def _truncate_prompt(cls, prompt: str, max_prompt_chars: int) -> str:
        """Trim oversized prompts while preserving both instructions and output schema."""
        normalized_prompt = str(prompt or "").strip()
        if max_prompt_chars <= 0 or len(normalized_prompt) <= max_prompt_chars:
            return normalized_prompt

        marker = cls.PROMPT_TRUNCATION_NOTICE
        if max_prompt_chars <= len(marker) + 64:
            return normalized_prompt[:max_prompt_chars]

        usable_chars = max_prompt_chars - len(marker)
        head_chars = int(usable_chars * 0.6)
        tail_chars = usable_chars - head_chars
        return (
            f"{normalized_prompt[:head_chars].rstrip()}"
            f"{marker}"
            f"{normalized_prompt[-tail_chars:].lstrip()}"
        )

    def _resolve_execution_policy(self, call_type: str) -> LLMExecutionPolicy:
        """Resolve a call-specific timeout and prompt budget policy."""
        normalized_call_type = (call_type or "").strip().lower()
        default_timeout = self._clamp_positive_int(self._request_timeout, minimum=5)
        default_retries = max(0, int(self._max_retries))

        if normalized_call_type.startswith("graph_rag_"):
            safe_timeout = min(default_timeout, self.GATEWAY_SAFE_TIMEOUT_SECONDS)
            return LLMExecutionPolicy(
                request_timeout_seconds=self._clamp_positive_int(safe_timeout, minimum=5),
                max_retries=0,
                max_attempts=1,
                allow_repair=False,
                max_prompt_chars=self.GRAPH_RAG_MAX_PROMPT_CHARS,
            )

        if normalized_call_type in self.FAST_FAIL_CALL_TYPES:
            safe_timeout = min(default_timeout, self.GATEWAY_SAFE_TIMEOUT_SECONDS)
            return LLMExecutionPolicy(
                request_timeout_seconds=self._clamp_positive_int(safe_timeout, minimum=5),
                max_retries=0,
                max_attempts=1,
                allow_repair=False,
                max_prompt_chars=self.LATENCY_SAFE_MAX_PROMPT_CHARS,
            )

        return LLMExecutionPolicy(
            request_timeout_seconds=default_timeout,
            max_retries=default_retries,
            max_attempts=2,
            allow_repair=True,
            max_prompt_chars=self.DEFAULT_MAX_PROMPT_CHARS,
        )

    @property
    def is_available(self) -> bool:
        """检查LLM服务是否可用"""
        return bool(self._api_key)

    def _create_llm_client(
        self,
        request_timeout: int,
        max_retries: int,
        extra_body_overrides: Optional[Dict[str, Any]] = None,
    ):
        """Instantiate a ChatOpenAI client with the supplied latency budget."""
        normalized_format = self.api_format.replace("_", "-").lower()
        if normalized_format not in self.SUPPORTED_API_FORMATS:
            logger.warning(
                build_log_message(
                    "llm.client.unsupported_format",
                    api_format=self.api_format,
                    provider=self.provider_name,
                    model=self.model_name,
                )
            )
            return None

        chat_openai_module = import_module("langchain_openai")
        chat_openai_class = getattr(chat_openai_module, "ChatOpenAI")
        client_kwargs = {
            "model": self.model_name,
            "temperature": self.temperature,
            "api_key": self._api_key,
            "base_url": self._base_url,
            "openai_proxy": self._proxy_url or None,
            "request_timeout": self._clamp_positive_int(request_timeout, minimum=5),
            "max_retries": max(0, int(max_retries)),
        }
        extra_body = dict(self._extra_body or {})
        if extra_body_overrides:
            extra_body.update(extra_body_overrides)
        if extra_body:
            client_kwargs["extra_body"] = extra_body
        if self._reasoning_enabled and self._reasoning_effort:
            client_kwargs["reasoning_effort"] = self._reasoning_effort
        return chat_openai_class(**client_kwargs)

    def _get_llm(self):
        """
        延迟初始化LLM实例

        使用 langchain_openai.ChatOpenAI 作为兼容协议客户端，
        仅承载通义千问与 DeepSeek 的聊天调用。
        """
        if self._llm is None and self.is_available:
            try:
                self._llm = self._create_llm_client(
                    request_timeout=self._request_timeout,
                    max_retries=self._max_retries,
                )
                # 写入日志记录
                if self._llm is not None:
                    logger.debug(
                        build_log_message(
                            "llm.client.ready",
                            model=self.model_name,
                            base_url=self._base_url,
                        )
                    )
            except ImportError:
                # 写入日志记录
                logger.warning(
                    build_log_message(
                        "llm.client.import_error", detail="langchain_openai 未安装"
                    )
                )
            except Exception as e:
                # 写入日志记录
                logger.error(
                    build_log_message(
                        "llm.client.init_fail", model=self.model_name, error=e
                    )
                )

        return self._llm

    def _get_llm_for_policy(
        self,
        policy: LLMExecutionPolicy,
        extra_body_overrides: Optional[Dict[str, Any]] = None,
    ):
        """Return a cached or one-off chat client that matches the execution policy."""
        if not self.is_available:
            return None

        uses_default_budget = (
            policy.request_timeout_seconds == self._clamp_positive_int(self._request_timeout, minimum=5)
            and policy.max_retries == max(0, int(self._max_retries))
        )
        if uses_default_budget and not extra_body_overrides:
            return self._get_llm()

        try:
            return self._create_llm_client(
                request_timeout=policy.request_timeout_seconds,
                max_retries=policy.max_retries,
                extra_body_overrides=extra_body_overrides,
            )
        except ImportError:
            logger.warning(
                build_log_message(
                    "llm.client.import_error",
                    detail="langchain_openai 未安装",
                )
            )
            return None
        except Exception as error:
            logger.error(
                build_log_message(
                    "llm.client.init_fail",
                    model=self.model_name,
                    error=error,
                    timeout_seconds=policy.request_timeout_seconds,
                    max_retries=policy.max_retries,
                )
            )
            return None

    def _get_agent_service(self):
        """Lazily build the LangChain agent orchestration layer."""
        if self._agent_service is None and self.is_available:
            from platform_ai.llm.agent import get_agent_service

            self._agent_service = get_agent_service(
                model_name=self.model_name,
                api_key=self._api_key,
                base_url=self._base_url,
                api_format=self.api_format,
                temperature=self.temperature,
                request_timeout=self._request_timeout,
                max_retries=self._max_retries,
                proxy_url=self._proxy_url,
                reasoning_enabled=self._reasoning_enabled,
                reasoning_effort=self._reasoning_effort,
                extra_body_json=json.dumps(
                    self._extra_body,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        return self._agent_service

    @classmethod
    def _should_use_agent_service(cls, call_type: str) -> bool:
        """仅对显式 agent 任务启用编排层，避免常规调用产生递归开销。"""
        normalized_call_type = (call_type or "").strip().lower()
        if not normalized_call_type:
            return False
        if normalized_call_type.startswith("graph_rag_"):
            return False
        return (
            normalized_call_type in cls.AGENT_ENABLED_CALL_TYPES
            or normalized_call_type.startswith("agent_")
        )


# 创建默认实例
llm_service = LLMService()
