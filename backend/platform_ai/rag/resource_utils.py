"""课程资源 URL、排序与知识点匹配工具。"""

from __future__ import annotations

import re
from collections.abc import Iterable

from knowledge.models import KnowledgePoint, Resource


WHITESPACE_PATTERN = re.compile(r"\s+")


def coerce_resource_text(value: object) -> str:
    """
    将资源字段规整为单行文本。

    :param value: 模型字段、外部 JSON 字段或测试替身字段。
    :return: 去除多余空白后的文本。
    """
    return WHITESPACE_PATTERN.sub(" ", str(value or "")).strip()


def safe_resource_url(resource: Resource) -> str:
    """
    返回课程内资源的稳定可访问 URL。

    :param resource: 课程资源对象。
    :return: URL 字符串；缺失或文件字段异常时返回空字符串。
    """
    resource_url = coerce_resource_text(getattr(resource, "url", ""))
    if resource_url:
        return resource_url
    file_field = getattr(resource, "file", None)
    if not file_field:
        return ""
    try:
        return coerce_resource_text(file_field.url)
    except (AttributeError, OSError, ValueError):
        return ""


def normalize_resource_match_text(value: object) -> str:
    """
    归一化中英文匹配文本，减少空格导致的漏召回。

    :param value: 待匹配文本。
    :return: 小写且去空格的匹配文本。
    """
    return coerce_resource_text(value).lower().replace(" ", "")


def dedupe_resource_terms(items: Iterable[str]) -> list[str]:
    """
    保留顺序去重非空资源匹配词。

    :param items: 原始匹配词序列。
    :return: 去重后的匹配词。
    """
    seen: set[str] = set()
    results: list[str] = []
    for item in items:
        normalized = coerce_resource_text(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        results.append(normalized)
    return results


def ascii_resource_terms(value: str) -> list[str]:
    """
    提取 Spark SQL、HDFS 等英文/数字术语。

    :param value: 原始知识点或章节文本。
    :return: 英文/数字术语列表。
    """
    terms: list[str] = []
    buffer: list[str] = []
    for char in value:
        if char.isascii() and (char.isalnum() or char in {"+", "#", ".", " "}):
            buffer.append(char)
            continue
        term = " ".join("".join(buffer).split())
        if len(term) >= 2:
            terms.append(term)
        buffer = []
    term = " ".join("".join(buffer).split())
    if len(term) >= 2:
        terms.append(term)
    return terms


def point_resource_match_terms(point: KnowledgePoint) -> list[str]:
    """
    从知识点名称、章节和常见后缀中提取资源匹配词。

    :param point: 知识点对象。
    :return: 可用于资源匹配的词列表。
    """
    point_name = coerce_resource_text(getattr(point, "name", ""))
    chapter = coerce_resource_text(getattr(point, "chapter", ""))
    terms: list[str] = []
    for raw_term in [point_name, *chapter.replace("＞", ">").split(">")]:
        term = raw_term.strip()
        if len(term) >= 2:
            terms.append(term)
        terms.extend(ascii_resource_terms(term))

    for suffix in ("定义与特征", "原理与特征", "基本操作", "工作原理", "模型原理", "方法原理", "应用"):
        if point_name.endswith(suffix) and len(point_name) > len(suffix) + 1:
            terms.append(point_name[: -len(suffix)].strip())
    if point_name.startswith("大数据"):
        terms.append("大数据")
    return dedupe_resource_terms(terms)


def score_resource_point_match(resource: Resource, point: KnowledgePoint) -> int:
    """
    计算未绑定课程资源与知识点上下文的文本匹配分。

    :param resource: 课程资源对象。
    :param point: 当前知识点。
    :return: 匹配分，0 表示不匹配。
    """
    haystack = normalize_resource_match_text(
        " ".join(
            [
                coerce_resource_text(getattr(resource, "title", "")),
                coerce_resource_text(getattr(resource, "description", "")),
                coerce_resource_text(getattr(resource, "chapter_number", "")),
            ]
        )
    )
    if not haystack:
        return 0

    score = 0
    for index, term in enumerate(point_resource_match_terms(point)):
        normalized_term = normalize_resource_match_text(term)
        if normalized_term and normalized_term in haystack:
            score += max(6, 30 - index)
    return score


def resource_rank_key(
    resource: Resource, mastery_value: float | None
) -> tuple[int, int, int, str]:
    """
    根据学生掌握度排序课程内资源。

    :param resource: 课程资源对象。
    :param mastery_value: 当前掌握度。
    :return: 可传给 `sorted` 的稳定排序键。
    """
    beginner_priority = {"video": 0, "document": 1, "exercise": 2, "link": 3}
    advanced_priority = {"exercise": 0, "video": 1, "document": 2, "link": 3}
    priority_map = advanced_priority if mastery_value is not None and mastery_value >= 0.7 else beginner_priority
    resource_type = coerce_resource_text(getattr(resource, "resource_type", ""))
    duration = getattr(resource, "duration", None) or 10**9
    sort_order = getattr(resource, "sort_order", 0) or 0
    return (priority_map.get(resource_type, 9), int(sort_order), int(duration), coerce_resource_text(resource.title))


__all__ = [
    "coerce_resource_text",
    "safe_resource_url",
    "normalize_resource_match_text",
    "dedupe_resource_terms",
    "ascii_resource_terms",
    "point_resource_match_terms",
    "score_resource_point_match",
    "resource_rank_key",
]
