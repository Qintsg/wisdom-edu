"""AI、图谱与外部资源相关 Django settings 装载。"""

from __future__ import annotations

from collections.abc import Callable
import logging
import os


ConfigValue = Callable[[str, str, str], str]
ConfigInt = Callable[[str, str, int], int]
EnvConfigBool = Callable[[str, str, str, bool], bool]
ConfigJsonDict = Callable[[str, str, str], dict[str, object]]


# 维护意图：读取环境变量优先的整数配置
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _int_setting(
    env_name: str,
    section: str,
    key: str,
    default: int,
    config_int: ConfigInt,
) -> int:
    """读取环境变量优先的整数配置。"""
    value = config_int(section, key, default)
    raw_env_value = os.getenv(env_name, "").strip()
    if raw_env_value.isdigit():
        return int(raw_env_value)
    return value


# 维护意图：加载 AI、Neo4j、GraphRAG 与资源 MCP settings。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_ai_settings(
    config_value: ConfigValue,
    config_int: ConfigInt,
    env_config_bool: EnvConfigBool,
    config_json_dict: ConfigJsonDict,
    debug: bool,
) -> dict[str, object]:
    """
    加载 AI、Neo4j、GraphRAG 与资源 MCP settings。

    :return: 可合并进 Django settings 模块 globals 的变量字典。
    """
    settings_values = _load_graph_and_resource_settings(
        config_value,
        config_int,
        env_config_bool,
    )
    settings_values.update(
        _load_llm_settings(
            config_value,
            config_int,
            env_config_bool,
            config_json_dict,
            debug,
        )
    )
    return settings_values


# 维护意图：加载 Neo4j、GraphRAG 和资源 MCP settings
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _load_graph_and_resource_settings(
    config_value: ConfigValue,
    config_int: ConfigInt,
    env_config_bool: EnvConfigBool,
) -> dict[str, object]:
    """加载 Neo4j、GraphRAG 和资源 MCP settings。"""
    return {
        "NEO4J_BOLT_URL": os.getenv("NEO4J_BOLT_URL", "bolt://localhost:7687"),
        "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME", "neo4j"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD", "password"),
        "GRAPHRAG_EMBEDDER_PROVIDER": os.getenv(
            "GRAPHRAG_EMBEDDER_PROVIDER",
            config_value("graphrag", "embedder_provider", "hash"),
        ).strip() or "hash",
        "GRAPHRAG_SENTENCE_MODEL": os.getenv(
            "GRAPHRAG_SENTENCE_MODEL",
            config_value(
                "graphrag",
                "sentence_model",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            ),
        ).strip() or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "GRAPHRAG_VECTOR_DIMENSION": _int_setting(
            "GRAPHRAG_VECTOR_DIMENSION",
            "graphrag",
            "vector_dimension",
            256,
            config_int,
        ),
        "GRAPHRAG_QDRANT_PATH": os.getenv(
            "GRAPHRAG_QDRANT_PATH",
            config_value("graphrag", "qdrant_path", "runtime_logs/rag/qdrant"),
        ).strip() or "runtime_logs/rag/qdrant",
        "RESOURCE_MCP_ENABLED": env_config_bool(
            "RESOURCE_MCP_ENABLED", "resource_mcp", "enabled", True
        ),
        "RESOURCE_MCP_EXA_ENABLED": env_config_bool(
            "RESOURCE_MCP_EXA_ENABLED", "resource_mcp", "exa_enabled", True
        ),
        "RESOURCE_MCP_FIRECRAWL_ENABLED": env_config_bool(
            "RESOURCE_MCP_FIRECRAWL_ENABLED", "resource_mcp", "firecrawl_enabled", True
        ),
        "RESOURCE_MCP_TIMEOUT_SECONDS": _int_setting(
            "RESOURCE_MCP_TIMEOUT_SECONDS", "resource_mcp", "timeout_seconds", 12, config_int
        ),
        "RESOURCE_MCP_FIRECRAWL_LIMIT": _int_setting(
            "RESOURCE_MCP_FIRECRAWL_LIMIT", "resource_mcp", "firecrawl_limit", 2, config_int
        ),
        "EXA_API_KEY": os.getenv("EXA_API_KEY", ""),
        "EXA_SEARCH_URL": os.getenv("EXA_SEARCH_URL", "https://api.exa.ai/search"),
        "EXA_SEARCH_TYPE": os.getenv(
            "EXA_SEARCH_TYPE", config_value("resource_mcp", "exa_search_type", "neural")
        ),
        "EXA_MAX_RESULTS": _int_setting(
            "EXA_MAX_RESULTS", "resource_mcp", "exa_max_results", 8, config_int
        ),
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", ""),
        "FIRECRAWL_SCRAPE_URL": os.getenv(
            "FIRECRAWL_SCRAPE_URL", "https://api.firecrawl.dev/v1/scrape"
        ),
        "FIRECRAWL_TIMEOUT_MILLISECONDS": _int_setting(
            "FIRECRAWL_TIMEOUT_MILLISECONDS",
            "resource_mcp",
            "firecrawl_timeout_milliseconds",
            15000,
            config_int,
        ),
    }


# 维护意图：加载 LLM provider、代理、重试和密钥 settings
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _load_llm_settings(
    config_value: ConfigValue,
    config_int: ConfigInt,
    env_config_bool: EnvConfigBool,
    config_json_dict: ConfigJsonDict,
    debug: bool,
) -> dict[str, object]:
    """加载 LLM provider、代理、重试和密钥 settings。"""
    values: dict[str, object] = {
        "LLM_PROVIDER": os.getenv(
            "LLM_PROVIDER", config_value("llm", "provider", "deepseek")
        ).strip().lower() or "deepseek",
        "LLM_MODEL": os.getenv(
            "LLM_MODEL", config_value("llm", "model", "deepseek-v4-flash")
        ).strip() or "deepseek-v4-flash",
        "LLM_API_FORMAT": os.getenv(
            "LLM_API_FORMAT", config_value("llm", "api_format", "openai-compatible")
        ).strip().lower() or "openai-compatible",
        "LLM_REQUEST_TIMEOUT": _int_setting(
            "LLM_REQUEST_TIMEOUT",
            "llm",
            "request_timeout_seconds",
            config_int("ai_services", "api_timeout", 120),
            config_int,
        ),
        "LLM_MAX_RETRIES": _int_setting(
            "LLM_MAX_RETRIES", "llm", "max_retries", 2, config_int
        ),
        "LLM_BASE_URL": os.getenv(
            "LLM_BASE_URL", config_value("llm", "base_url", "")
        ).strip(),
        "LLM_REASONING_ENABLED": env_config_bool(
            "LLM_REASONING_ENABLED", "llm", "reasoning_enabled", False
        ),
        "LLM_REASONING_EFFORT": os.getenv(
            "LLM_REASONING_EFFORT", config_value("llm", "reasoning_effort", "")
        ).strip().lower(),
        "LLM_EXTRA_BODY": config_json_dict("LLM_EXTRA_BODY_JSON", "llm", "extra_body_json"),
        "LLM_HTTP_PROXY": os.getenv("LLM_HTTP_PROXY", os.getenv("HTTP_PROXY", "")).strip(),
        "LLM_HTTPS_PROXY": os.getenv("LLM_HTTPS_PROXY", os.getenv("HTTPS_PROXY", "")).strip(),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "CUSTOM_LLM_API_KEY": os.getenv("CUSTOM_LLM_API_KEY", ""),
        "CUSTOM_LLM_BASE_URL": os.getenv("CUSTOM_LLM_BASE_URL", ""),
        "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY", ""),
        "QWEN_BASE_URL": os.getenv("QWEN_BASE_URL", ""),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
        "DEEPSEEK_BASE_URL": os.getenv("DEEPSEEK_BASE_URL", ""),
        "ARK_API_KEY": os.getenv("ARK_API_KEY", ""),
        "ZAI_API_KEY": os.getenv("ZAI_API_KEY", ""),
        "ZAI_BASE_URL": os.getenv("ZAI_BASE_URL", ""),
        "MOONSHOT_API_KEY": os.getenv("MOONSHOT_API_KEY", ""),
        "MOONSHOT_BASE_URL": os.getenv("MOONSHOT_BASE_URL", ""),
    }
    values["DOUBAO_API_KEY"] = os.getenv("DOUBAO_API_KEY", str(values["ARK_API_KEY"]))
    values["DOUBAO_BASE_URL"] = os.getenv("DOUBAO_BASE_URL", "")
    values["ZHIPU_API_KEY"] = os.getenv("ZHIPU_API_KEY", str(values["ZAI_API_KEY"]))
    values["ZHIPU_BASE_URL"] = os.getenv("ZHIPU_BASE_URL", "")
    values["KIMI_API_KEY"] = os.getenv("KIMI_API_KEY", str(values["MOONSHOT_API_KEY"]))
    values["KIMI_BASE_URL"] = os.getenv("KIMI_BASE_URL", "")

    llm_key = (
        values["LLM_API_KEY"]
        or values["CUSTOM_LLM_API_KEY"]
        or values["DASHSCOPE_API_KEY"]
        or values["DEEPSEEK_API_KEY"]
        or values["ARK_API_KEY"]
        or values["DOUBAO_API_KEY"]
        or values["ZAI_API_KEY"]
        or values["ZHIPU_API_KEY"]
        or values["MOONSHOT_API_KEY"]
        or values["KIMI_API_KEY"]
    )
    if not debug and not llm_key:
        logging.warning("未配置LLM API密钥，AI功能将使用Mock响应。")
        logging.warning(
            "请设置 LLM_API_KEY，或配置 DASHSCOPE_API_KEY / DEEPSEEK_API_KEY / ARK_API_KEY / ZAI_API_KEY / MOONSHOT_API_KEY。"
        )

    return values
