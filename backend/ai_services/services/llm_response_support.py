"""LLM 结构化响应解析与清洗工具。"""

from __future__ import annotations

import json
import re
from typing import Any


# 维护意图：格式化输入数据为结构化文本
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def format_input_data(data: dict[str, Any], data_type: str = "general") -> str:
    """格式化输入数据为结构化文本。"""
    _ = data_type
    if not data:
        return "无数据"

    if isinstance(data, dict):
        formatted_lines = []
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                formatted_lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                formatted_lines.append(f"- {key}: {value}")
        return "\n".join(formatted_lines)
    return str(data)


# 维护意图：移除兼容网关可能返回的 <think> 推理片段，保留最终答案
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def strip_reasoning_blocks(content: str) -> str:
    """移除兼容网关可能返回的 <think> 推理片段，保留最终答案。"""
    if not content:
        return ""
    return re.sub(
        r"<think>[\s\S]*?</think>",
        "",
        str(content),
        flags=re.IGNORECASE,
    ).strip()


# 维护意图：安全解析 LLM 返回的 JSON 响应
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_json_response(content: str) -> dict[str, Any]:
    """安全解析 LLM 返回的 JSON 响应。"""
    normalized_content = strip_reasoning_blocks(content)
    direct_result = parse_json_object(normalized_content)
    if direct_result is not None:
        return direct_result

    fenced_result = parse_fenced_json(normalized_content)
    if fenced_result is not None:
        return fenced_result

    embedded_result = parse_embedded_json(normalized_content)
    if embedded_result is not None:
        return embedded_result
    return {"content": normalized_content, "parse_error": True}


# 维护意图：尝试直接解析 JSON 对象
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_json_object(content: str) -> dict[str, Any] | None:
    """尝试直接解析 JSON 对象。"""
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        return None
    return result if isinstance(result, dict) else {"content": result}


# 维护意图：从 Markdown 代码块中提取 JSON
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_fenced_json(content: str) -> dict[str, Any] | None:
    """从 Markdown 代码块中提取 JSON。"""
    json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    for match in re.findall(json_pattern, content):
        result = parse_json_object(match.strip())
        if result is not None:
            return result
    return None


# 维护意图：从混合文本中截取首尾大括号之间的 JSON
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_embedded_json(content: str) -> dict[str, Any] | None:
    """从混合文本中截取首尾大括号之间的 JSON。"""
    start = content.find("{")
    end = content.rfind("}") + 1
    if start == -1 or end <= start:
        return None
    return parse_json_object(content[start:end])


# 维护意图：Normalize LangChain message content into a single text string
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def coerce_message_text(content: str | list[Any] | None) -> str:
    """Normalize LangChain message content into a single text string."""
    if isinstance(content, str):
        return strip_reasoning_blocks(content)
    if isinstance(content, list):
        message_text = "\n".join(
            item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
            for item in content
            if item is not None
        )
        return strip_reasoning_blocks(message_text)
    return ""


# 维护意图：为后续重试补充更明确的 JSON 约束提示
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_retry_prompt(prepared_prompt: str, attempt_index: int) -> str:
    """为后续重试补充更明确的 JSON 约束提示。"""
    if attempt_index != 1:
        return prepared_prompt
    return (
        prepared_prompt
        + "\n\nPlease output the complete JSON again. Ensure all fields are present and no content is omitted."
    )


# 维护意图：仅补齐缺失的顶层字段，不覆盖模型已经生成的内容
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def merge_missing_fields(result: dict[str, Any], fallback_response: dict[str, Any]) -> dict[str, Any]:
    """仅补齐缺失的顶层字段，不覆盖模型已经生成的内容。"""
    merged = dict(result)
    for key, value in (fallback_response or {}).items():
        if key not in merged or merged[key] is None:
            merged[key] = value
    return merged


# 维护意图：执行轻量响应清洗，不截断模型内容
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def post_process_response(result: dict[str, Any], call_type: str) -> dict[str, Any]:
    """执行轻量响应清洗，不截断模型内容。"""
    _ = call_type
    return {
        key: clean_response_value(value)
        for key, value in (result or {}).items()
    }


# 维护意图：清洗单个响应字段值
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clean_response_value(value: Any) -> Any:
    """清洗单个响应字段值。"""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return clean_response_list(value)
    return value


# 维护意图：清洗列表字段，删除空字符串并保留非空项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clean_response_list(items: list[Any]) -> list[Any]:
    """清洗列表字段，删除空字符串并保留非空项。"""
    normalized_list = []
    for item in items:
        if isinstance(item, str):
            normalized_item = item.strip()
            if normalized_item:
                normalized_list.append(normalized_item)
        elif item is not None:
            normalized_list.append(item)
    return normalized_list
