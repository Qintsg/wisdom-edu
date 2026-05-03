from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

# 维护意图：Describe the provider-level settings used to initialize the LLM client
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ModelProviderConfig(TypedDict, total=False):
    """Describe the provider-level settings used to initialize the LLM client."""

    display_name: str
    base_url: str
    models: list[str]
    env_keys: list[str]
    base_url_env_keys: list[str]
    model_prefixes: list[str]
    api_format: str


# 维护意图：Describe call-specific latency budgets and prompt shaping rules
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class LLMExecutionPolicy:
    """Describe call-specific latency budgets and prompt shaping rules."""

    request_timeout_seconds: int
    max_retries: int
    max_attempts: int
    allow_repair: bool
    max_prompt_chars: int


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
