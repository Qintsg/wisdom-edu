"""
LLM服务模块 - 使用LangChain框架封装大模型调用

支持的模型：
- DeepSeek (deepseek-v4-flash, deepseek-chat, deepseek-reasoner)
- 通义千问 (qwen-plus, qwen-turbo, qwen-max)

使用示例:
    from ai_services.services import llm_service

    result = llm_service.analyze_profile(user_data)
"""

import time
from dataclasses import dataclass
from importlib import import_module
import logging
import json
import os
import re
from typing import Dict, Any, Optional, List, TypedDict
from urllib.parse import urlparse
from django.conf import settings
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


class ModelProviderConfig(TypedDict, total=False):
    """Describe the provider-level settings used to initialize the LLM client."""

    display_name: str
    base_url: str
    models: list[str]
    env_keys: list[str]
    base_url_env_keys: list[str]
    model_prefixes: list[str]
    api_format: str


@dataclass(frozen=True)
class LLMExecutionPolicy:
    """Describe call-specific latency budgets and prompt shaping rules."""

    request_timeout_seconds: int
    max_retries: int
    max_attempts: int
    allow_repair: bool
    max_prompt_chars: int


class LLMService:
    """
    大语言模型服务类

    使用LangChain框架进行LLM调用，支持多种国产大模型。
    当未配置API密钥时，自动使用Mock响应。
    """

    # 支持的模型配置。当前统一走 OpenAI 兼容接口，因此只要提供方具备兼容
    # base_url + api_key + model 的调用方式，就可以接入 LangChain ChatOpenAI。
    MODEL_CONFIGS: dict[str, ModelProviderConfig] = {
        "qwen": {
            "display_name": "通义千问",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": [
                "qwen3.6-plus",
                "qwen3.5-plus",
                "qwen-plus",
                "qwen-plus-latest",
                "qwen-max",
                "qwen-flash",
                "qwen-turbo",
                "qwen3-coder-plus",
                "qwq-plus",
            ],
            "env_keys": ["DASHSCOPE_API_KEY", "LLM_API_KEY"],
            "base_url_env_keys": ["QWEN_BASE_URL"],
            "model_prefixes": ["qwen", "qwq"],
            "api_format": "openai-compatible",
        },
        "deepseek": {
            "display_name": "DeepSeek",
            "base_url": "https://api.deepseek.com",
            "models": [
                "deepseek-v4-flash",
                "deepseek-chat",
                "deepseek-reasoner",
                "deepseek-coder",
            ],
            "env_keys": ["DEEPSEEK_API_KEY", "LLM_API_KEY"],
            "base_url_env_keys": ["DEEPSEEK_BASE_URL"],
            "model_prefixes": ["deepseek"],
            "api_format": "openai-compatible",
        },
        "doubao": {
            "display_name": "豆包 / ModelArk",
            "base_url": "https://ark.ap-southeast.bytepluses.com/api/v3",
            "models": [
                "doubao-seed-1.6",
                "doubao-seed-1.6-thinking",
                "ByteDance-Seed-1.8",
            ],
            "env_keys": ["ARK_API_KEY", "DOUBAO_API_KEY", "LLM_API_KEY"],
            "base_url_env_keys": ["DOUBAO_BASE_URL"],
            "model_prefixes": ["doubao", "seed", "ark"],
            "api_format": "openai-compatible",
        },
        "zhipu": {
            "display_name": "智谱 / GLM",
            "base_url": "https://open.bigmodel.cn/api/paas/v4/",
            "models": ["glm-5", "glm-4.7", "glm-4.6", "glm-4.6v"],
            "env_keys": ["ZAI_API_KEY", "ZHIPU_API_KEY", "LLM_API_KEY"],
            "base_url_env_keys": ["ZHIPU_BASE_URL"],
            "model_prefixes": ["glm", "zhipu"],
            "api_format": "openai-compatible",
        },
        "kimi": {
            "display_name": "Kimi / Moonshot",
            "base_url": "https://api.moonshot.ai/v1",
            "models": [
                "kimi-k2.5",
                "kimi-k2-thinking",
                "moonshot-v1-8k",
                "moonshot-v1-32k",
                "moonshot-v1-128k",
                "moonshot-v1-auto",
            ],
            "env_keys": ["MOONSHOT_API_KEY", "KIMI_API_KEY", "LLM_API_KEY"],
            "base_url_env_keys": ["KIMI_BASE_URL"],
            "model_prefixes": ["kimi", "moonshot"],
            "api_format": "openai-compatible",
        },
        "custom": {
            "display_name": "自定义兼容服务",
            "base_url": "",
            "models": [],
            "env_keys": ["CUSTOM_LLM_API_KEY", "LLM_API_KEY"],
            "base_url_env_keys": ["CUSTOM_LLM_BASE_URL"],
            "model_prefixes": ["custom"],
            "api_format": "openai-compatible",
        },
    }

    SUPPORTED_API_FORMATS = {
        "openai",
        "openai-compatible",
        "openai_compatible",
        "chat-completions",
    }

    AGENT_ENABLED_CALL_TYPES = frozenset({
        "agent_planning",
        "agent_orchestration",
    })

    FAST_FAIL_CALL_TYPES = frozenset({
        "path_planning",
        "node_intro",
        "resource_reason",
        "feedback_report",
        "internal_resources",
        "external_resources",
        "kt_analysis",
        "question_selection",
        "chat",
    })

    GATEWAY_SAFE_TIMEOUT_SECONDS = 25
    DEFAULT_MAX_PROMPT_CHARS = 16000
    GRAPH_RAG_MAX_PROMPT_CHARS = 6000
    LATENCY_SAFE_MAX_PROMPT_CHARS = 7000
    PROMPT_TRUNCATION_NOTICE = (
        "\n\n[上下文过长，系统已自动截断部分中间证据以保障响应时延]\n\n"
    )

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

    @staticmethod
    def _format_input_data(
        data: Dict[str, Any], data_type: str = "general"
    ) -> str:
        """
        格式化输入数据为结构化文本

        Args:
            data: 输入数据字典
            data_type: 数据类型（用于选择格式化策略）

        Returns:
            格式化后的文本
        """
        if not data:
            return "无数据"

        if isinstance(data, dict):
            formatted_lines = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    formatted_lines.append(
                        f"- {key}: {json.dumps(value, ensure_ascii=False)}"
                    )
                else:
                    formatted_lines.append(f"- {key}: {value}")
            return "\n".join(formatted_lines)

        return str(data)

    @staticmethod
    def _strip_reasoning_blocks(content: str) -> str:
        """移除兼容网关可能返回的 <think> 推理片段，保留最终答案。"""
        if not content:
            return ""
        return re.sub(
            r"<think>[\s\S]*?</think>",
            "",
            str(content),
            flags=re.IGNORECASE,
        ).strip()

    @staticmethod
    def _parse_json_response(content: str) -> Dict[str, Any]:
        """
        安全解析LLM返回的JSON响应

        处理各种可能的格式问题：
        1. 纯JSON
        2. 带有markdown代码块的JSON
        3. 带有额外文本的JSON

        Args:
            content: LLM返回的原始内容

        Returns:
            解析后的字典
        """
        content = LLMService._strip_reasoning_blocks(content)

        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从markdown代码块中提取JSON
        json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(json_pattern, content)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # 尝试查找JSON对象
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

        # 无法解析时保留原始内容，便于后续降级或修复。
        return {"content": content, "parse_error": True}

    @staticmethod
    def _coerce_message_text(content: str | List[Any] | None) -> str:
        """Normalize LangChain message content into a single text string."""
        if isinstance(content, str):
            return LLMService._strip_reasoning_blocks(content)
        if isinstance(content, list):
            message_text = "\n".join(
                item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
                for item in content
                if item is not None
            )
            return LLMService._strip_reasoning_blocks(message_text)
        return ""

    def _repair_json_response(
        self, llm, raw_content: str, fallback_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """要求模型将原始内容修复为可直接解析的合法 JSON。"""
        from langchain_core.messages import HumanMessage, SystemMessage

        schema_hint = json.dumps(fallback_response, ensure_ascii=False)
        repair_prompt = (
            "Please rewrite the following content as complete, valid JSON that can be parsed "
            "directly by json.loads(). Do not add explanations and do not omit any existing information.\n\n"
            f"Target schema example: {schema_hint}\n\n"
            f"Original content:\n{raw_content}"
        )
        repaired = llm.invoke(
            [
                SystemMessage(
                    content="You are a JSON repair assistant. Output valid JSON only."
                ),
                HumanMessage(content=repair_prompt),
            ]
        )
        return self._parse_json_response(self._coerce_message_text(repaired.content))

    @staticmethod
    def _merge_missing_fields(
        result: Dict[str, Any], fallback_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """仅补齐缺失的顶层字段，不覆盖模型已经生成的内容。"""
        merged = dict(result)
        for key, value in (fallback_response or {}).items():
            if key not in merged or merged[key] is None:
                merged[key] = value
        return merged

    def _call_with_fallback(
        self,
        prompt: str,
        call_type: str,
        fallback_response: Dict[str, Any],
        temperature: float = None,
        extra_body_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        调用 LLM，并在所有结构化输出尝试都失败后才降级。
        """
        start_time = time.time()
        execution_policy = self._resolve_execution_policy(call_type)
        prepared_prompt = self._truncate_prompt(
            prompt,
            execution_policy.max_prompt_chars,
        )
        if len(prepared_prompt) != len(str(prompt or "").strip()):
            logger.info(
                build_log_message(
                    "llm.prompt.truncated",
                    call_type=call_type,
                    original_chars=len(str(prompt or "")),
                    kept_chars=len(prepared_prompt),
                )
            )

        agent_service = (
            self._get_agent_service()
            if self._should_use_agent_service(call_type)
            else None
        )
        if agent_service and agent_service.is_available:
            agent_result = agent_service.invoke_json(
                call_type=call_type,
                prompt=prepared_prompt,
                fallback_response=fallback_response,
            )
            if agent_result and agent_result != fallback_response:
                duration_ms = int((time.time() - start_time) * 1000)
                # 写入日志记录
                logger.debug(
                    build_log_message(
                        "llm.agent.success",
                        call_type=call_type,
                        duration_ms=duration_ms,
                        model=self.model_name,
                    )
                )
                return self._post_process_response(
                    self._merge_missing_fields(agent_result, fallback_response),
                    call_type,
                )
        elif self.is_available:
            logger.debug(
                build_log_message(
                    "llm.agent.skipped",
                    call_type=call_type,
                    reason="non_agent_call_type",
                )
            )

        llm = self._get_llm_for_policy(execution_policy, extra_body_overrides)
        if llm is None:
            # 写入日志记录
            logger.debug(
                build_log_message(
                    "llm.call.fallback", call_type=call_type, reason="model_unavailable"
                )
            )
            return fallback_response

        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            system_content = """You are the AI analysis engine for an adaptive learning system.

# Output rules
1. Output valid JSON only.
2. The response must be directly parseable by json.loads().
3. Use natural language descriptions instead of internal IDs.
4. Keep recommendations concrete, complete, and actionable.
5. If information is limited, still return the full JSON structure with the best available content."""

            original_temp = None
            if temperature is not None and hasattr(llm, "temperature"):
                original_temp = llm.temperature
                llm.temperature = temperature

            last_raw_content = ""
            for attempt in range(execution_policy.max_attempts):
                current_prompt = prepared_prompt
                if attempt == 1:
                    current_prompt += "\n\nPlease output the complete JSON again. Ensure all fields are present and no content is omitted."

                response = llm.invoke(
                    [
                        SystemMessage(content=system_content),
                        HumanMessage(content=current_prompt),
                    ]
                )
                last_raw_content = self._coerce_message_text(response.content)
                result = self._parse_json_response(last_raw_content)
                if not result.get("parse_error"):
                    duration_ms = int((time.time() - start_time) * 1000)
                    # 写入日志记录
                    logger.debug(
                        build_log_message(
                            "llm.call.success",
                            call_type=call_type,
                            attempt=attempt + 1,
                            duration_ms=duration_ms,
                            model=self.model_name,
                        )
                    )
                    result = self._merge_missing_fields(result, fallback_response)
                    result = self._post_process_response(result, call_type)
                    if original_temp is not None:
                        llm.temperature = original_temp
                    return result

                if execution_policy.allow_repair:
                    repaired = self._repair_json_response(
                        llm, last_raw_content, fallback_response
                    )
                    if not repaired.get("parse_error"):
                        duration_ms = int((time.time() - start_time) * 1000)
                        # 写入日志记录
                        logger.debug(
                            build_log_message(
                                "llm.call.repaired",
                                call_type=call_type,
                                attempt=attempt + 1,
                                duration_ms=duration_ms,
                                model=self.model_name,
                            )
                        )
                        repaired = self._merge_missing_fields(repaired, fallback_response)
                        repaired = self._post_process_response(repaired, call_type)
                        if original_temp is not None:
                            llm.temperature = original_temp
                        return repaired

            if original_temp is not None:
                llm.temperature = original_temp
            # 写入日志记录
            logger.warning(
                build_log_message(
                    "llm.call.parse_fail",
                    call_type=call_type,
                    raw=last_raw_content[:300],
                )
            )
            return fallback_response

        except Exception as e:
            # 写入日志记录
            logger.error(
                build_log_message(
                    "llm.call.fail", call_type=call_type, model=self.model_name, error=e
                )
            )
            return fallback_response

    def call_with_fallback(
        self,
        prompt: str,
        call_type: str,
        fallback_response: Dict[str, Any],
        temperature: float = None,
        extra_body_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """通过公共入口执行带降级保护的 LLM 调用。"""
        return self._call_with_fallback(
            prompt=prompt,
            call_type=call_type,
            fallback_response=fallback_response,
            temperature=temperature,
            extra_body_overrides=extra_body_overrides,
        )

    _FIELD_MAX_LEN = {}

    @staticmethod
    def _post_process_response(
        result: Dict[str, Any], call_type: str
    ) -> Dict[str, Any]:
        """Light cleanup only; do not truncate model content."""
        _ = call_type
        cleaned = {}
        for key, value in (result or {}).items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            elif isinstance(value, list):
                normalized_list = []
                for item in value:
                    if isinstance(item, str):
                        item = item.strip()
                        if item:
                            normalized_list.append(item)
                    elif item is not None:
                        normalized_list.append(item)
                cleaned[key] = normalized_list
            else:
                cleaned[key] = value
        return cleaned

    def analyze_profile(
        self,
        mastery_data: List[Dict],
        ability_data: Dict = None,
        habit_data: Dict = None,
        course_name: str = None,
        grade_level: str = None,
        kt_predictions: Dict = None,
    ) -> Dict[str, Any]:
        """
        分析学习者画像

        Args:
            mastery_data: 知识掌握度数据列表
            ability_data: 能力评分数据
            habit_data: 学习习惯数据
            course_name: 课程名称（可选，用于生成学科针对性建议）
            grade_level: 学段/年级（可选）
            kt_predictions: KT模型预测的知识点掌握度 {kp_name: mastery_rate}

        Returns:
            画像分析结果，包含summary, weakness, strength, suggestion
        """
        mastery_str = ", ".join(
            [
                f"{m.get('point_name', '未知')}({m.get('category', '')}): {float(m.get('mastery_rate') or 0) * 100:.0f}%"
                for m in mastery_data
            ]
        )

        total_points = len(mastery_data)
        if total_points > 0:
            avg_mastery = (
                sum(float(m.get("mastery_rate") or 0) for m in mastery_data)
                / total_points
                * 100
            )
            weak_count = sum(
                1 for m in mastery_data if float(m.get("mastery_rate") or 0) < 0.6
            )
            strong_count = sum(
                1 for m in mastery_data if float(m.get("mastery_rate") or 0) >= 0.8
            )
        else:
            avg_mastery, weak_count, strong_count = 0, 0, 0

        # 构建优化的提示词
        course_ctx = ""
        if course_name or grade_level:
            parts = []
            if course_name:
                parts.append(f"课程：{course_name}")
            if grade_level:
                parts.append(f"学段：{grade_level}")
            course_ctx = "\n## 课程信息\n" + "\n".join(f"- {p}" for p in parts) + "\n"

        prompt = f"""# 任务
基于学生的多维度学习数据，生成个性化学习画像分析报告。

# 输入数据
{course_ctx}## 知识掌握情况（共{total_points}个知识点）
- 各知识点掌握率：{mastery_str}
- 整体平均掌握率：{avg_mastery:.1f}%
- 薄弱知识点数量：{weak_count}个（低于60%）
- 优势知识点数量：{strong_count}个（高于80%）

## 能力维度评分
{json.dumps(ability_data, ensure_ascii=False) if ability_data else "暂无能力测评数据"}

## 学习偏好特征
{json.dumps(habit_data, ensure_ascii=False) if habit_data else "暂无学习偏好数据"}

## 知识追踪模型预测
{json.dumps(kt_predictions, ensure_ascii=False, indent=2) if kt_predictions else "暂无KT模型预测数据（掌握度基于统计方法估算）"}

# JSON输出格式
{{
    "summary": "综合评价摘要，包含学习状态定性描述和核心特点（80-120字）",
    "weakness": ["需要重点加强的薄弱知识点或能力短板，最多3项"],
    "strength": ["学习优势和突出表现，最多3项"],
    "suggestion": "针对性的学习建议，包含具体的学习策略、资源推荐和时间规划（150-250字）"
}}

# 示例输出
{{
    "summary": "你在函数与递归方面掌握扎实（85%），但循环结构（42%）和数组操作（38%）较薄弱，整体处于中等偏上水平，需要针对性强化基础控制结构。",
    "weakness": ["循环结构的嵌套使用和边界条件处理", "数组的动态操作与遍历技巧"],
    "strength": ["函数定义与调用理解透彻", "递归思维和问题分解能力突出"],
    "suggestion": "建议先用2天时间集中复习循环结构，重点练习while/for循环的6种经典模式（如累加、查找、排序），每天完成5道练习题。然后用1天学习数组遍历和操作，配合可视化工具理解内存变化。最后做1套综合题检验效果。利用你擅长的函数思维，尝试将循环逻辑封装为函数来加深理解。"
}}

# 分析原则
1. 评价要客观公正，既肯定进步也指出不足
2. 建议要具体可执行，避免空泛的描述
3. 考虑学生的学习偏好，推荐适合的学习方式
4. 薄弱点和优势点要精准对应具体知识点"""

        # 构建降级响应
        fallback = {
            "summary": "基于你的测评数据，你在核心概念理解方面表现良好，但在应用能力上有提升空间。",
            "weakness": self._identify_weakness(mastery_data),
            "strength": self._identify_strength(mastery_data),
            "suggestion": "建议多做练习题，加强实践应用能力。针对薄弱知识点进行专项突破。",
        }

        return self._call_with_fallback(prompt, "profile_analysis", fallback)

    def plan_learning_path(
        self,
        mastery_data: List[Dict],
        target: str = None,
        constraints: Dict = None,
        course_name: str = None,
        max_nodes: int = None,
    ) -> Dict[str, Any]:
        """
        规划学习路径

        Args:
            mastery_data: 知识掌握度数据
            target: 学习目标
            constraints: 约束条件
            course_name: 课程名称（可选，提供领域上下文）
            max_nodes: 最大节点数（可选，默认从配置读取）

        Returns:
            路径规划结果
        """
        # 从配置读取节点上限
        if max_nodes is None:
            from common.config import AppConfig

            max_nodes = AppConfig.max_path_nodes()

        # 分析掌握度数据
        mastery_str = ", ".join(
            [
                f"{m.get('point_name', '未知')}: {float(m.get('mastery_rate') or 0) * 100:.0f}%"
                for m in mastery_data
            ]
        )

        # 识别薄弱和强势知识点
        weak_points = [
            m.get("point_name") or "未知知识点"
            for m in mastery_data
            if float(m.get("mastery_rate") or 0) < 0.6
        ]
        strong_points = [
            m.get("point_name") or "未知知识点"
            for m in mastery_data
            if float(m.get("mastery_rate") or 0) >= 0.8
        ]

        # 构建优化的提示词
        course_ctx = f"\n## 课程信息\n- 课程名称：{course_name}" if course_name else ""

        # 增量刷新模式：展开已完成进度和学习画像
        constraints_text = ""
        if constraints:
            if constraints.get("refresh_mode"):
                parts = []
                completed = constraints.get("completed_nodes", [])
                if completed:
                    comp_str = ", ".join(
                        [
                            f"{c['name']}({c['status']}/{c['mastery']})"
                            for c in completed[:15]
                        ]
                    )
                    parts.append(
                        f"已完成/跳过的节点（共{len(completed)}个，已保留，不要重复规划）：{comp_str}"
                    )
                parts.append(
                    f"剩余待规划知识点数：{constraints.get('remaining_count', '?')}"
                )
                parts.append(
                    f"KT答题历史：{constraints.get('kt_answer_count', 0)}条，预测维度：{constraints.get('kt_prediction_count', 0)}"
                )
                if constraints.get("ability_scores"):
                    score_str = ", ".join(
                        [f"{k}: {v}" for k, v in constraints["ability_scores"].items()]
                    )
                    parts.append(f"能力评测（C-WAIS）：{score_str}")
                if constraints.get("learning_preferences"):
                    pref = constraints["learning_preferences"]
                    parts.append(
                        f"学习偏好：资源类型={pref.get('preferred_resource', '未知')}, 时间段={pref.get('preferred_study_time', '未知')}, 节奏={pref.get('study_pace', 'moderate')}"
                    )
                if constraints.get("learner_profile"):
                    parts.append(f"学习画像摘要：\n{constraints['learner_profile']}")
                constraints_text = "\n".join(f"- {p}" for p in parts)
            else:
                constraints_text = json.dumps(constraints, ensure_ascii=False)
        else:
            constraints_text = "无特殊约束，按常规进度安排"

        prompt = f"""# 任务
基于学生的知识掌握情况，设计一条循序渐进的个性化学习路径（最多{max_nodes}个节点）。

# 学生当前状态{course_ctx}
## 知识点掌握详情
{mastery_str}

## 分析概要
- 薄弱知识点（<60%）：{", ".join(weak_points) if weak_points else "无明显薄弱点"}
- 优势知识点（≥80%）：{", ".join(strong_points) if strong_points else "暂无突出优势"}

## 学习目标
{target or "全面掌握课程核心知识，达到80%以上的整体掌握率"}

## 约束条件
{constraints_text}

# 规划原则
1. 先修原则：前置知识先学
2. 优先级原则：薄弱知识点优先
3. 递进原则：由浅入深
4. 巩固原则：适时安排复习

# JSON输出格式
{{
    "reason": "路径规划的核心思路和依据说明（80-120字）",
    "nodes": [
        {{
            "title": "学习节点标题",
            "goal": "该节点的具体学习目标，可量化",
            "priority": "high/medium/low",
            "estimated_hours": 2,
            "prerequisites": ["前置知识点名称"]
        }}
    ]
}}"""

        # 基于掌握度生成降级响应
        weak_point_list = [
            m for m in mastery_data if float(m.get("mastery_rate") or 0) < 0.6
        ]

        fallback = {
            "reason": "基于你的学习画像，系统为你定制了循序渐进的学习路径，优先强化薄弱知识点，同时巩固已有优势。",
            "nodes": [
                {
                    "title": f"{p.get('point_name', '基础知识')}强化",
                    "goal": f"掌握{p.get('point_name', '相关知识')}的核心概念，达到70%以上掌握率",
                    "priority": "high"
                    if float(p.get("mastery_rate") or 0) < 0.4
                    else "medium",
                    "estimated_hours": 2,
                    "prerequisites": [],
                }
                for p in weak_point_list[:5]
            ]
            or [
                {
                    "title": "综合提升",
                    "goal": "巩固已学知识，提升应用能力",
                    "priority": "medium",
                    "estimated_hours": 3,
                    "prerequisites": [],
                }
            ],
        }

        return self._call_with_fallback(prompt, "path_planning", fallback)

    def generate_resource_reason(
        self,
        resource_info: Dict,
        student_mastery: float = None,
        point_name: str = None,
        course_name: str = None,
    ) -> Dict[str, Any]:
        """
        生成资源推荐理由

        Args:
            resource_info: 资源信息
            student_mastery: 学生对相关知识点的掌握度
            point_name: 知识点名称
            course_name: 课程名称（可选，提供领域上下文）

        Returns:
            推荐理由
        """
        # 确定学习阶段
        if student_mastery is None:
            stage = "初学"
            stage_desc = "刚开始学习该知识点"
        elif student_mastery < 0.4:
            stage = "入门"
            stage_desc = "需要从基础概念开始学习"
        elif student_mastery < 0.6:
            stage = "巩固"
            stage_desc = "需要加强理解和练习"
        elif student_mastery < 0.8:
            stage = "提高"
            stage_desc = "可以进行进阶学习和应用"
        else:
            stage = "精通"
            stage_desc = "可以挑战高级内容和拓展知识"

        course_ctx = f"\n- 所属课程：{course_name}" if course_name else ""

        prompt = f"""# 任务
为学生解释推荐此学习资源的原因，评估资源与学生当前学习状态的匹配度。

# 推荐资源信息
- 资源名称：{resource_info.get("title", "未知资源")}
- 资源类型：{resource_info.get("type", "未知类型")}
- 资源描述：{resource_info.get("description", "无描述")}

# 学生学习状态
- 相关知识点：{point_name or "通用知识"}{course_ctx}
- 当前掌握度：{f"{student_mastery * 100:.0f}%" if student_mastery is not None else "未评测"}
- 学习阶段：{stage}（{stage_desc}）

# JSON输出格式
{{
    "reason": "个性化推荐理由，说明资源与学生状态的匹配点（40-60字）",
    "relevance_score": "<float, 0-1之间的匹配度评分，根据学生阶段和资源特点动态评估>",
    "learning_tips": "使用该资源的学习建议（30-50字）"
}}"""

        # 构建降级响应
        relevance = (
            0.85
            if student_mastery is None
            else max(0.6, min(0.95, 0.9 - abs(student_mastery - 0.5)))
        )
        fallback = {
            "reason": f"这个{resource_info.get('type', '资源')}能够帮助你更好地理解{point_name or '相关概念'}，适合当前{stage}阶段学习。",
            "relevance_score": round(relevance, 2),
            "learning_tips": "建议结合笔记进行学习，完成后进行相关练习巩固。",
        }

        return self._call_with_fallback(
            prompt, "resource_reason", fallback, temperature=0.5
        )

    def recommend_external_resources(
        self,
        point_name: str,
        student_mastery: float = None,
        existing_titles: List[str] = None,
        course_name: str = None,
        search_results: List[Dict[str, Any]] = None,
        count: int = 3,
    ) -> Dict[str, Any]:
        """
        根据知识点和学生掌握度，推荐外部学习资源（网站、视频、文章等）

        Args:
            point_name: 知识点名称
            student_mastery: 学生掌握度 0-1
            existing_titles: 已有内部资源标题列表（避免重复）
            course_name: 所属课程名称（提供领域上下文）
            count: 推荐数量（最少返回数）

        Returns:
            包含 resources 列表的字典
        """
        # 确定学习阶段
        if student_mastery is None:
            stage = "初学"
        elif student_mastery < 0.4:
            stage = "入门"
        elif student_mastery < 0.6:
            stage = "巩固"
        elif student_mastery < 0.8:
            stage = "提高"
        else:
            stage = "精通"

        existing_str = ""
        if existing_titles:
            existing_str = (
                f"\n已有课内资源（请勿推荐相同内容）：{', '.join(existing_titles[:5])}"
            )

        course_ctx = f"所属课程：{course_name}\n" if course_name else ""

        _ = search_results

        prompt = f"""# 任务
请直接使用 DeepSeek / 当前模型提供方的原生联网搜索能力，为正在学习「{point_name}」的学生推荐 {count} 个优质外部学习资源。

# 学生信息
- 知识点：{point_name}
- 掌握度：{f"{student_mastery * 100:.0f}%" if student_mastery is not None else "未评测"}
- 学习阶段：{stage}
{course_ctx}{existing_str}

# 重要要求
1. 必须由模型直接联网获取真实存在、可正常访问的资源 URL，禁止使用后端预检索候选列表
2. 资源难度应匹配学生当前{stage}阶段
3. 至少返回 {count} 个资源
4. 优先推荐以下知名平台的资源：
   - 视频类：B站(bilibili.com)、中国大学MOOC(icourse163.com)、网易公开课
   - 文档类：菜鸟教程(runoob.com)、W3Cschool、官方技术文档
   - 英文经典：Coursera、Khan Academy、官方文档(如Apache/Spark官网)
5. 每个资源需说明推荐理由，理由要具体到知识点内容
6. URL格式要完整（以 http:// 或 https:// 开头）
7. 不要返回搜索结果页 URL，优先返回具体课程、视频、文章或文档页面

# JSON输出格式
{{
    "resources": [
        {{
            "title": "资源标题（准确描述资源内容）",
            "url": "完整的资源URL",
            "type": "video/document/link/exercise",
            "reason": "推荐理由，说明与知识点的关联（30-50字）"
        }}
    ]
}}"""

        # Fallback: 根据领域生成通用平台链接
        fallback_resources = []
        # 替换字符串内容
        search_kw = point_name.replace(" ", "+")
        fallback_templates = [
            {
                "title": f"{point_name} - B站视频教程",
                "url": f"https://search.bilibili.com/all?keyword={search_kw}",
                "type": "video",
            },
            {
                "title": f"{point_name} - 中国大学MOOC",
                "url": f"https://www.icourse163.org/search.htm?search={search_kw}",
                "type": "video",
            },
            {
                "title": f"{point_name} - 菜鸟教程",
                "url": f"https://www.runoob.com/",
                "type": "document",
            },
        ]
        for i, tmpl in enumerate(fallback_templates[:count]):
            fallback_resources.append(
                {
                    **tmpl,
                    "reason": f"该平台有丰富的{point_name}学习内容，适合{stage}阶段。",
                }
            )

        fallback = {"resources": fallback_resources}

        result = self._call_with_fallback(
            prompt,
            "external_resources",
            fallback,
            temperature=0.7,
            extra_body_overrides={"enable_search": True},
        )
        # 规范 resources 字段为列表格式。
        if "resources" not in result or not isinstance(result.get("resources"), list):
            result = fallback
        # 过滤掉无URL的资源
        result["resources"] = [r for r in result["resources"] if r.get("url")]
        # 不足时用fallback补充
        if len(result["resources"]) < count:
            used_urls = {r.get("url") for r in result["resources"]}
            for fb in fallback_resources:
                if fb["url"] not in used_urls:
                    result["resources"].append(
                        {**fb, "reason": f"推荐学习{point_name}相关内容。"}
                    )
                if len(result["resources"]) >= count:
                    break
        return result

    def generate_feedback_report(
        self,
        exam_info: Dict,
        score: float,
        total_score: float,
        mistakes: List[Dict],
        kt_predictions: Dict = None,
    ) -> Dict[str, Any]:
        """
        生成考试反馈报告

        Args:
            exam_info: 考试信息
            score: 得分
            total_score: 总分
            mistakes: 错题列表
            kt_predictions: KT模型预测的知识点掌握度 {kp_id: mastery_rate}

        Returns:
            反馈报告
        """
        accuracy = score / total_score if total_score > 0 else 0

        # 分析错题涉及的知识点（丰富上下文数据）
        mistake_points = []
        for m in mistakes[:5]:  # 取前5个错题分析
            point = {
                "question_text": m.get("question_text", ""),
                "knowledge_point": m.get("knowledge_point_name", ""),
                "student_answer": m.get("student_answer", ""),
                "correct_answer": m.get("correct_answer", ""),
                "analysis": m.get("analysis", ""),
            }
            mistake_points.append({k: v for k, v in point.items() if v})

        # 确定表现等级
        if accuracy >= 0.9:
            level = "优秀"
            level_desc = "你的表现非常出色，已经很好地掌握了本次作业涉及的知识点"
        elif accuracy >= 0.8:
            level = "良好"
            level_desc = "你的表现良好，大部分知识点已经掌握"
        elif accuracy >= 0.7:
            level = "中等"
            level_desc = "你基本掌握了课程内容，但仍有提升空间"
        elif accuracy >= 0.6:
            level = "及格"
            level_desc = "你已达到本次作业的基本要求，但仍需加强对部分知识点的理解"
        else:
            level = "待提高"
            level_desc = "你需要加强基础知识的学习"

        prompt = f"""# 任务
基于学生的作业表现，生成鼓励性、有针对性的学习反馈报告。

# 作业信息
- 作业名称：{exam_info.get("title", "未知作业")}
- 作业类型：{exam_info.get("type", "课程作业")}
- 总分：{total_score}分 / 学生得分：{score}分 / 正确率：{accuracy * 100:.1f}%
- 表现等级：{level}（{level_desc}）
- 错题数量：{len(mistakes)}题

# 错题详情
{json.dumps(mistake_points, ensure_ascii=False, indent=2) if mistake_points else "无错题数据"}

# 知识追踪分析
{json.dumps(kt_predictions, ensure_ascii=False, indent=2) if kt_predictions else "暂无KT模型预测数据"}

# JSON输出格式
{{
    "summary": "一句话摘要，先概括结果再点出最关键的改进方向（40-70字）",
    "analysis": "表现分析，包含整体评价、亮点和不足（80-120字）",
    "knowledge_gaps": ["需要加强的知识点或能力缺口，最多3项"],
    "recommendations": ["具体的改进建议，可操作性强，最多3项"],
    "next_tasks": ["下一步学习任务，包含具体行动，最多3项"],
    "encouragement": "鼓励性话语，激发学习动力（30-50字）"
}}

# 反馈原则
1. 先肯定进步，再指出不足
2. 建议要具体、可执行
3. 根据表现等级调整建议的难度"""

        # 根据正确率生成降级分析
        if accuracy >= 0.9:
            analysis = f"{level_desc}！继续保持，可以挑战更高难度的内容，拓展知识广度。"
            recommendations = ["尝试更高难度的拓展题目", "帮助同学解答问题，巩固理解"]
            next_tasks = ["学习进阶知识点", "参与课程讨论和实践项目"]
        elif accuracy >= 0.7:
            analysis = f"{level_desc}。建议针对错题涉及的知识点进行专项复习。"
            recommendations = [
                "复习错题涉及的知识点",
                "多做同类型练习题",
                "整理错题笔记",
            ]
            next_tasks = ["完成针对性强化练习", "重做本次作业的错题"]
        elif accuracy >= 0.6:
            analysis = f"{level_desc}。需要系统复习课程内容，加强基础知识的理解。"
            recommendations = [
                "系统复习课程重点内容",
                "观看知识点讲解视频",
                "做基础练习题",
            ]
            next_tasks = ["重新学习薄弱知识点", "制定复习计划并执行"]
        else:
            analysis = f"{level_desc}。建议从基础概念开始重新学习，循序渐进地掌握知识。"
            recommendations = [
                "从基础概念开始学习",
                "多次观看教学视频",
                "寻求老师或同学帮助",
            ]
            next_tasks = [
                "制定详细学习计划",
                "从最基础的内容开始复习",
                "每日进行适量练习",
            ]
        summary = f"{exam_info.get('title', '本次作业')}得分{score}/{total_score}，正确率{accuracy * 100:.1f}%，{level_desc}。"

        fallback = {
            "summary": summary,
            "analysis": analysis,
            "knowledge_gaps": [
                m.get("analysis", "相关知识点")[:20] for m in mistakes[:3]
            ]
            if mistakes
            else [],
            "recommendations": recommendations,
            "next_tasks": next_tasks,
            "encouragement": "学习是一个渐进的过程，每一次努力都是进步。相信自己，持续学习一定会有收获！",
        }

        from common.config import AppConfig

        if not AppConfig.ai_feedback_enabled():
            logger.debug(
                build_log_message(
                    "llm.feedback.disabled",
                    provider=self.provider_name,
                    model=self.model_name,
                )
            )
            return fallback

        return self._call_with_fallback(prompt, "feedback_report", fallback)

    def analyze_knowledge_tracing_result(
        self,
        kt_result: Dict[str, Any],
        answer_history: List[Dict] = None,
        course_name: str = None,
        point_name_map: Dict[int, str] = None,
    ) -> Dict[str, Any]:
        """
        分析知识追踪结果，生成学习洞察报告

        基于 DKT 知识追踪模型的预测结果，生成深度学习分析报告。

        Args:
            kt_result: 知识追踪服务返回的预测结果字典
            answer_history: 答题历史记录列表
            course_name: 课程名称
            point_name_map: 知识点ID到名称的映射 {id: name}，用于将数字ID转换为可读名称

        Returns:
            dict: 包含学习洞察、趋势分析和改进建议的报告
        """
        predictions = kt_result.get("predictions", {})
        model_type = kt_result.get("model_type", "unknown")
        confidence = kt_result.get("confidence", 0)
        active_models = kt_result.get("active_models", [])

        # 将知识点ID映射为名称（如有映射表）
        _name = point_name_map or {}
        weak_points = {k: v for k, v in predictions.items() if v < 0.6}
        strong_points = {k: v for k, v in predictions.items() if v >= 0.8}

        named_predictions = {
            _name.get(int(k) if isinstance(k, (int, float)) else k, f"知识点{k}"): v
            for k, v in predictions.items()
        }
        named_weak = {
            _name.get(int(k) if isinstance(k, (int, float)) else k, f"知识点{k}"): v
            for k, v in weak_points.items()
        }

        # 统计分析
        if predictions:
            # 提取字段值
            avg_mastery = sum(predictions.values()) / len(predictions)
        else:
            avg_mastery = 0

        # 答题趋势分析
        if answer_history:
            total_questions = len(answer_history)
            correct_count = sum(1 for a in answer_history if a.get("correct", 0) == 1)
            recent_accuracy = (
                correct_count / total_questions if total_questions > 0 else 0
            )
        else:
            total_questions = 0
            recent_accuracy = 0

        prompt = f"""# 任务
基于知识追踪模型的预测结果，生成学习洞察报告。

# 知识追踪预测结果
- 使用模型：{", ".join([m.upper() for m in active_models]) if active_models else model_type.upper()}
- 预测置信度：{confidence * 100:.1f}%
- 课程：{course_name or "未知课程"}

## 各知识点预测掌握率
{json.dumps(named_predictions, ensure_ascii=False, indent=2)}

## 统计概要
- 总知识点数：{len(predictions)} / 平均掌握率：{avg_mastery * 100:.1f}%
- 薄弱知识点（<60%）：{len(weak_points)}个 / 优势知识点（≥80%）：{len(strong_points)}个
- 答题记录数：{total_questions} / 近期正确率：{recent_accuracy * 100:.1f}%

# JSON输出格式
{{
    "insight_summary": "学习状态核心洞察，基于模型预测的关键发现（60-100字）",
    "mastery_trend": "掌握度变化趋势分析和预判（40-60字）",
    "weak_point_analysis": ["薄弱知识点深度分析，说明可能原因，最多3项"],
    "improvement_strategy": ["针对性提升策略，具体可执行，最多3项"],
    "model_confidence_note": "关于预测置信度的解读和使用建议（30-50字）"
}}"""

        # 构建降级响应
        weak_analysis = []
        for point_id, mastery in list(weak_points.items())[:3]:
            name = _name.get(
                int(point_id) if isinstance(point_id, (int, float)) else point_id,
                f"知识点{point_id}",
            )
            weak_analysis.append(f"{name}掌握率仅{mastery * 100:.0f}%，需重点关注")

        improvement = [
            "针对薄弱知识点进行专项练习",
            "增加相关知识点的学习时间",
            "结合视频和文档多维度学习",
        ]

        fallback = {
            "insight_summary": f"基于{model_type.upper()}模型分析，你的整体掌握率为{avg_mastery * 100:.1f}%，有{len(weak_points)}个知识点需要加强。",
            "mastery_trend": "建议持续进行练习，关注薄弱知识点的掌握情况变化。",
            "weak_point_analysis": weak_analysis
            if weak_analysis
            else ["暂无明显薄弱知识点"],
            "improvement_strategy": improvement,
            "model_confidence_note": f"预测置信度{confidence * 100:.0f}%，结果可作为学习规划参考。",
        }

        return self._call_with_fallback(prompt, "kt_analysis", fallback)

    @staticmethod
    def _identify_weakness(mastery_data: List[Dict]) -> List[str]:
        """识别薄弱知识点"""
        return [
            m.get("point_name", "未知")
            for m in mastery_data
            if float(m.get("mastery_rate") or 0) < 0.6
        ][:3]

    @staticmethod
    def _identify_strength(mastery_data: List[Dict]) -> List[str]:
        """识别优势知识点"""
        return [
            m.get("point_name", "未知")
            for m in mastery_data
            if float(m.get("mastery_rate") or 0) >= 0.8
        ][:3]

    def recommend_internal_resources(
        self,
        point_name: str,
        student_mastery: float = None,
        available_resources: List[Dict] = None,
        course_name: str = None,
        count: int = 2,
    ) -> Dict[str, Any]:
        """
        从课程内部资源库中，由LLM选出最匹配当前知识点和学生掌握度的资源

        Args:
            point_name: 知识点名称
            student_mastery: 学生掌握度 0-1
            available_resources: 候选内部资源列表 [{'id','title','type','description','chapter'}]
            course_name: 课程名称
            count: 推荐数量（最少返回数）

        Returns:
            {'resources': [{'id': int, 'reason': str, 'learning_tips': str}]}
        """
        if not available_resources:
            return {"resources": []}

        # 确定学习阶段
        if student_mastery is None:
            stage = "初学"
        elif student_mastery < 0.4:
            stage = "入门"
        elif student_mastery < 0.6:
            stage = "巩固"
        elif student_mastery < 0.8:
            stage = "提高"
        else:
            stage = "精通"

        # 构建候选资源文本
        candidate_text = "\n".join(
            [
                f"  - ID:{r['id']} | 类型:{r.get('type', '未知')} | 标题:{r.get('title', '无标题')} | 描述:{r.get('description', '')[:60]} | 章节:{r.get('chapter', '')}"
                for r in available_resources[:40]
            ]
        )

        course_ctx = f"所属课程：{course_name}\n" if course_name else ""

        prompt = f"""# 任务
从课程内部资源库中，选出最适合学生当前学习状态的 {count} 个学习资源。

# 学生信息
- 正在学习的知识点：{point_name}
- 当前掌握度：{f"{student_mastery * 100:.0f}%" if student_mastery is not None else "未评测"}
- 学习阶段：{stage}
{course_ctx}
# 候选内部资源
{candidate_text}

# 选择原则
1. 优先选择与知识点「{point_name}」内容最相关的资源
2. 资源类型多样化（如PPT+视频组合优于两个PPT）
3. 难度匹配学生当前{stage}阶段（入门选基础、精通选进阶）
4. 至少选出 {count} 个资源，如果高度相关的不足则放宽相关性
5. 每种资源类型（PPT/视频/电子教材）最多选1个

# JSON输出格式
{{
    "resources": [
        {{
            "id": "<int, 选中资源的ID>",
            "reason": "推荐理由（30-50字，说明该资源与知识点的关联性）",
            "learning_tips": "使用该资源的学习建议（20-40字）"
        }}
    ]
}}"""

        # Fallback: 简单按标题模糊匹配
        fallback_resources = []
        # 优先匹配标题包含知识点名的
        for r in available_resources:
            title = r.get("title", "")
            if point_name in title or any(kw in title for kw in point_name.split("与")):
                fallback_resources.append(
                    {
                        "id": r["id"],
                        "reason": f"该资源与「{point_name}」相关，适合{stage}阶段学习。",
                        "learning_tips": "建议结合笔记进行学习。",
                    }
                )
            if len(fallback_resources) >= count:
                break
        # 不足则补充其他资源
        if len(fallback_resources) < count:
            used_ids = {r["id"] for r in fallback_resources}
            for r in available_resources:
                if r["id"] not in used_ids:
                    fallback_resources.append(
                        {
                            "id": r["id"],
                            "reason": f"推荐学习此{r.get('type', '资源')}以加深理解。",
                            "learning_tips": "建议配合其他资源一起学习。",
                        }
                    )
                if len(fallback_resources) >= count:
                    break

        fallback = {"resources": fallback_resources}
        result = self._call_with_fallback(
            prompt, "internal_resources", fallback, temperature=0.3
        )

        if "resources" not in result or not isinstance(result.get("resources"), list):
            result = fallback
        return result

    def select_stage_test_questions(
        self, candidates: List[Dict], kp_names: List[str], count: int = 10
    ) -> Optional[List[int]]:
        """
        LLM智能选择阶段测试题目

        从候选题目中挑选最能检验知识点掌握程度的题目。

        Args:
            candidates: 候选题目列表 [{'id': int, 'content': str, 'type': str, 'difficulty': str}]
            kp_names: 本次测试涉及的知识点名称列表
            count: 需要选出的题目数量

        Returns:
            选中题目的ID列表，失败时返回None
        """
        if not candidates:
            return None

        candidate_text = "\n".join(
            [
                f"  - ID:{c['id']} | 类型:{c['type']} | 难度:{c['difficulty']} | 题干:{c['content']}"
                for c in candidates[:30]  # 限制输入长度
            ]
        )

        prompt = f"""# 任务
从以下候选题目中选出最适合用于阶段测试的 {count} 道题目。

# 测试覆盖的知识点
{", ".join(kp_names)}

# 候选题目
{candidate_text}

# 选题原则
1. 覆盖尽可能多的知识点
2. 难度均衡分布（易/中/难合理搭配）
3. 题型多样化（单选/多选/判断搭配）
4. 避免重复或相似的题目

# JSON输出格式
{{
    "selected_ids": [所选题目的ID列表，整数数组],
    "reason": "选题理由简述（30字以内）"
}}"""

        fallback = {
            "selected_ids": [c["id"] for c in candidates[:count]],
            "reason": "按默认顺序选取",
        }

        result = self._call_with_fallback(
            prompt, "question_selection", fallback, temperature=0.2
        )
        ids = result.get("selected_ids")
        if isinstance(ids, list) and ids:
            return [int(i) for i in ids]
        return None


# 创建默认实例
llm_service = LLMService()
