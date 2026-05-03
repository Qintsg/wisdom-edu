"""LangChain agent 消息对象的文本提取工具。"""
from __future__ import annotations


# 维护意图：从 agent 调用返回中提取最终消息文本
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_agent_message_text(messages: object) -> str:
    """从 agent 调用返回中提取最终消息文本。"""
    if not isinstance(messages, list) or not messages:
        return ""
    return extract_message_content(getattr(messages[-1], "content", "") or "")


# 维护意图：兼容普通字符串和 OpenAI 兼容内容块数组
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_message_content(content: object) -> str:
    """兼容普通字符串和 OpenAI 兼容内容块数组。"""
    if not isinstance(content, list):
        return str(content)
    parts = [extract_content_part_text(item) for item in content]
    return "\n".join(part for part in parts if part)


# 维护意图：提取单个内容块中的文本
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_content_part_text(item: object) -> str:
    """提取单个内容块中的文本。"""
    if isinstance(item, str):
        return item
    if isinstance(item, dict) and item.get("text"):
        return str(item["text"])
    return ""


__all__ = [
    "extract_agent_message_text",
    "extract_content_part_text",
    "extract_message_content",
]
