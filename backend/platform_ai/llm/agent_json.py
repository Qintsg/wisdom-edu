"""LangChain agent 返回 JSON 的容错解析工具。"""
from __future__ import annotations

import json
import re
from collections.abc import Iterator


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


# 维护意图：从可能带解释文本或 Markdown 代码块的 agent 回复中提取 JSON 对象
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_json_payload(content: str) -> dict[str, object]:
    """从可能带解释文本或 Markdown 代码块的 agent 回复中提取 JSON 对象。"""
    for candidate in iter_json_candidates(content or ""):
        parsed = parse_json_candidate(candidate)
        if parsed is not None:
            return parsed
    return {}


# 维护意图：按可信度顺序产出可尝试解析的 JSON 文本片段
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def iter_json_candidates(content: str) -> Iterator[str]:
    """按可信度顺序产出可尝试解析的 JSON 文本片段。"""
    yield content
    yield from JSON_BLOCK_RE.findall(content)
    inline_candidate = extract_inline_json_candidate(content)
    if inline_candidate:
        yield inline_candidate


# 维护意图：截取回复中最外层花括号包裹的 JSON 片段
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_inline_json_candidate(content: str) -> str:
    """截取回复中最外层花括号包裹的 JSON 片段。"""
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end <= start:
        return ""
    return content[start : end + 1]


# 维护意图：解析单个候选片段，只接受对象型 JSON
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_json_candidate(candidate: str) -> dict[str, object] | None:
    """解析单个候选片段，只接受对象型 JSON。"""
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


__all__ = [
    "extract_inline_json_candidate",
    "iter_json_candidates",
    "parse_json_candidate",
    "parse_json_payload",
]
