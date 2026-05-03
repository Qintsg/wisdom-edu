"""学生端 GraphRAG 共享工具与数据结构。"""
from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Sequence
from dataclasses import dataclass
from typing import TypeAlias, TypeVar

from knowledge.models import Resource

from .resource_utils import safe_resource_url as _safe_url


SourceList: TypeAlias = list[dict[str, object]]
InputItem = TypeVar("InputItem")
NormalizedItem = TypeVar("NormalizedItem", bound=Hashable)


# 维护意图：将未知输入稳健转换为整数
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def to_int(value: object, default: int = 0) -> int:
    """将未知输入稳健转换为整数。"""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


# 维护意图：将未知输入稳健转换为浮点数
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def to_float(value: object, default: float = 0.0) -> float:
    """将未知输入稳健转换为浮点数。"""
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


# 维护意图：以类型安全方式读取 Django 模型主键
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def model_pk(instance: object) -> int:
    """以类型安全方式读取 Django 模型主键。"""
    return to_int(getattr(instance, "id", 0))


# 维护意图：按归一化结果去重并保留原始顺序
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def ordered_unique(
    items: Iterable[InputItem],
    normalize: Callable[[InputItem], NormalizedItem | None],
) -> list[NormalizedItem]:
    """按归一化结果去重并保留原始顺序。"""
    seen: set[NormalizedItem] = set()
    ordered: list[NormalizedItem] = []
    for item in items:
        normalized = normalize(item)
        if normalized is None or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


# 维护意图：将字符串规整为可去重的非空值
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_nonempty_string(item: str) -> str | None:
    """将字符串规整为可去重的非空值。"""
    normalized = item.strip()
    return normalized or None


# 维护意图：过滤非正整数，避免无效主键进入结果
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_positive_int(item: int) -> int | None:
    """过滤非正整数，避免无效主键进入结果。"""
    if item <= 0:
        return None
    return item


# 维护意图：从上下文包中安全提取 source 列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bundle_sources(bundle: dict[str, object]) -> SourceList:
    """从上下文包中安全提取 source 列表。"""
    raw_sources = bundle.get("sources")
    if not isinstance(raw_sources, list):
        return []
    sources: SourceList = []
    for item in raw_sources:
        if isinstance(item, dict):
            sources.append(item)
    return sources


# 维护意图：读取 GraphRAG bundle 的模式信息并保底
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bundle_mode(bundle: dict[str, object], fallback: str) -> str:
    """读取 GraphRAG bundle 的模式信息并保底。"""
    if not bundle_sources(bundle):
        return fallback
    return str(bundle.get("mode", "")).strip() or fallback


# 维护意图：合并 bundle 返回的查询模式，保留默认顺序
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bundle_query_modes(
    bundle: dict[str, object],
    base_modes: Sequence[str] = ("local", "global", "drift"),
) -> list[str]:
    """合并 bundle 返回的查询模式，保留默认顺序。"""
    query_modes = list(base_modes)
    raw_query_modes = bundle.get("query_modes")
    if not isinstance(raw_query_modes, list):
        return query_modes
    for raw_mode in raw_query_modes:
        normalized_mode = str(raw_mode).strip()
        if normalized_mode and normalized_mode not in query_modes:
            query_modes.append(normalized_mode)
    return query_modes


# 维护意图：从 bundle 中提取去重后的正整数列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bundle_positive_ints(bundle: dict[str, object], key: str) -> list[int]:
    """从 bundle 中提取去重后的正整数列表。"""
    raw_values = bundle.get(key)
    if not isinstance(raw_values, list):
        return []
    return dedupe_ints(to_int(raw_value) for raw_value in raw_values)


# 维护意图：保持原始顺序去重字符串列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def dedupe_strings(items: Iterable[str]) -> list[str]:
    """保持原始顺序去重字符串列表。"""
    return ordered_unique(items, normalize_nonempty_string)


# 维护意图：保持原始顺序去重整数列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def dedupe_ints(items: Iterable[int]) -> list[int]:
    """保持原始顺序去重整数列表。"""
    return ordered_unique(items, normalize_positive_int)


# 维护意图：压缩多余空白，避免回答出现长段空行
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def sanitize_answer_text(text: str) -> str:
    """压缩多余空白，避免回答出现长段空行。"""
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


# 维护意图：将索引文档标题转为更适合前端展示的名称
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def humanize_document_title(document: dict[str, object]) -> str:
    """将索引文档标题转为更适合前端展示的名称。"""
    kind = str(document.get("kind", "")).strip()
    title = str(document.get("title", "")).strip()
    if title:
        return title
    if kind == "knowledge_point":
        return "知识点"
    if kind == "community_report":
        return "社区报告"
    if kind == "resource":
        return "课程资源"
    if kind == "question":
        return "练习题"
    return "课程证据"


# 维护意图：将内部资源追加为统一的前端响应结构
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def append_internal_resource(
    bucket: list[dict[str, object]],
    resource: Resource,
    reason: str,
    completed_resource_ids: set[str],
    learning_tips: str,
) -> None:
    """将内部资源追加为统一的前端响应结构。"""
    bucket.append({
        "resource_id": model_pk(resource),
        "title": resource.title,
        "type": resource.resource_type,
        "url": _safe_url(resource),
        "description": resource.description or "",
        "duration": resource.duration,
        "required": resource.resource_type in {"video", "document"},
        "recommended_reason": reason,
        "learning_tips": learning_tips,
        "is_internal": True,
        "completed": str(model_pk(resource)) in completed_resource_ids,
    })


# 维护意图：承载单一 GraphRAG 查询模式的上下文结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class RankedContext:
    """承载单一 GraphRAG 查询模式的上下文结果。"""

    context: str
    sources: list[dict[str, object]]
    matched_entity_ids: list[str]
