#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 在线运行时题目特征构建。"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ai_services.services.mefkt_runtime_types import QuestionFeaturePreparation, QuestionFeatureScales, QuestionLike, RuntimeFeatureSources

NormalizeValues = Callable[[list[float], float], list[float]]
DifficultyToScore = Callable[[str | None], float]
ClampValue = Callable[[float], float]


# 维护意图：为章节顺序生成归一化映射
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_chapter_norm_map(
    questions: list[QuestionLike],
    normalize_values: NormalizeValues,
) -> dict[str, float]:
    """为章节顺序生成归一化映射。"""
    chapter_values = sorted({str(question.chapter or "").strip() for question in questions})
    chapter_mapping = {chapter: index for index, chapter in enumerate(chapter_values)}
    chapter_norm = normalize_values(
        [float(chapter_mapping[chapter]) for chapter in chapter_values],
        0.0,
    )
    return {chapter: chapter_norm[index] for index, chapter in enumerate(chapter_values)}


# 维护意图：收集单题题图和答题统计特征
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def collect_question_feature_entry(
    *,
    question: QuestionLike,
    sources: RuntimeFeatureSources,
    question_id_to_index: dict[int, int],
    difficulty_to_score: DifficultyToScore,
) -> tuple[dict[str, object], list[float], dict[int, list[int]]]:
    """收集单题题图和答题统计特征。"""
    point_ids = [int(point_id) for point_id in question.knowledge_points.values_list("id", flat=True)]
    point_index_map = {point_id: [question_id_to_index[int(question.id)]] for point_id in point_ids}
    resource_ids = collect_resource_ids(point_ids, sources.point_to_resources)
    relation_counts = collect_relation_counts(point_ids, sources)
    stats = sources.answer_stats.get(int(question.id), {"total": 0.0, "correct": 0.0})
    attempt_count = float(stats["total"])
    correct_rate = float(stats["correct"] / stats["total"]) if stats["total"] > 0 else 0.5
    score_value = float(question.score or 1.0)
    meta = build_question_meta(
        question=question,
        point_ids=point_ids,
        resource_ids=resource_ids,
        relation_counts=relation_counts,
        attempt_count=attempt_count,
        correct_rate=correct_rate,
        score_value=score_value,
    )
    raw_values = build_question_raw_values(
        question=question,
        point_ids=point_ids,
        resource_ids=resource_ids,
        attempt_count=attempt_count,
        correct_rate=correct_rate,
        score_value=score_value,
        difficulty_to_score=difficulty_to_score,
    )
    return meta, raw_values, point_index_map


# 维护意图：基于知识点集合收集关联资源 ID
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def collect_resource_ids(
    point_ids: list[int],
    point_to_resources: dict[int, set[int]],
) -> set[int]:
    """基于知识点集合收集关联资源 ID。"""
    return {
        resource_id
        for point_id in point_ids
        for resource_id in point_to_resources.get(point_id, set())
    }


# 维护意图：统计题目知识点周边的先修、后继和相关关系数量
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def collect_relation_counts(
    point_ids: list[int],
    sources: RuntimeFeatureSources,
) -> tuple[int, int, int]:
    """统计题目知识点周边的先修、后继和相关关系数量。"""
    prereq_count = len({pre for point_id in point_ids for pre in sources.prereq_points.get(point_id, set())})
    dependent_count = len({post for point_id in point_ids for post in sources.dependent_points.get(point_id, set())})
    related_count = len({rel for point_id in point_ids for rel in sources.related_points.get(point_id, set())})
    return prereq_count, dependent_count, related_count


# 维护意图：整理后续归一化和图统计共享的题目元数据
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_meta(
    *,
    question: QuestionLike,
    point_ids: list[int],
    resource_ids: set[int],
    relation_counts: tuple[int, int, int],
    attempt_count: float,
    correct_rate: float,
    score_value: float,
) -> dict[str, object]:
    """整理后续归一化和图统计共享的题目元数据。"""
    prereq_count, dependent_count, related_count = relation_counts
    return {
        "question": question,
        "point_ids": point_ids,
        "resource_ids": resource_ids,
        "prereq_count": float(prereq_count),
        "dependent_count": float(dependent_count),
        "related_count": float(related_count),
        "attempt_count": attempt_count,
        "correct_rate": correct_rate,
        "score_value": score_value,
    }


# 维护意图：生成一组待归一化的题目原始数值
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_raw_values(
    *,
    question: QuestionLike,
    point_ids: list[int],
    resource_ids: set[int],
    attempt_count: float,
    correct_rate: float,
    score_value: float,
    difficulty_to_score: DifficultyToScore,
) -> list[float]:
    """生成一组待归一化的题目原始数值。"""
    return [
        score_value,
        float(len(question.content or "")),
        float(len(question.analysis or "")),
        attempt_count,
        correct_rate,
        float(len(point_ids)),
        float(len(resource_ids)),
        difficulty_to_score(question.difficulty),
    ]


# 维护意图：统一计算题目特征归一化结果
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_question_feature_scales(
    *,
    normalize_values: NormalizeValues,
    chapter_norm_map: dict[str, float],
    score_values: list[float],
    content_lengths: list[float],
    analysis_lengths: list[float],
    attempt_counts: list[float],
    question_kp_counts: list[float],
    question_resource_counts: list[float],
    difficulty_values_raw: list[float],
    question_meta: list[dict[str, object]],
) -> QuestionFeatureScales:
    """统一计算题目特征归一化结果。"""
    return QuestionFeatureScales(
        chapter_norm_map=chapter_norm_map,
        score_norm=normalize_values(score_values, 0.5),
        content_norm=normalize_values(content_lengths, 0.3),
        analysis_norm=normalize_values(analysis_lengths, 0.2),
        attempt_norm=normalize_values(attempt_counts, 0.0),
        kp_count_norm=normalize_values(question_kp_counts, 0.2),
        resource_count_norm=normalize_values(question_resource_counts, 0.0),
        prereq_norm=normalize_values([float(item["prereq_count"]) for item in question_meta], 0.0),
        dependent_norm=normalize_values([float(item["dependent_count"]) for item in question_meta], 0.0),
        related_norm=normalize_values([float(item["related_count"]) for item in question_meta], 0.0),
        difficulty_values_raw=difficulty_values_raw,
    )


# 维护意图：为题目级运行时构造元信息和归一化特征
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def prepare_question_features(
    *,
    questions: list[QuestionLike],
    sources: RuntimeFeatureSources,
    normalize_values: NormalizeValues,
    difficulty_to_score: DifficultyToScore,
) -> QuestionFeaturePreparation:
    """为题目级运行时构造元信息和归一化特征。"""
    question_ids = [int(question.id) for question in questions]
    question_id_to_index = {question_id: index for index, question_id in enumerate(question_ids)}
    collector = QuestionFeatureCollector(question_ids=question_ids, question_id_to_index=question_id_to_index)
    for question in questions:
        collector.add_question(
            question=question,
            sources=sources,
            difficulty_to_score=difficulty_to_score,
        )
    scales = normalize_question_feature_scales(
        normalize_values=normalize_values,
        chapter_norm_map=build_chapter_norm_map(questions, normalize_values),
        score_values=collector.score_values,
        content_lengths=collector.content_lengths,
        analysis_lengths=collector.analysis_lengths,
        attempt_counts=collector.attempt_counts,
        question_kp_counts=collector.question_kp_counts,
        question_resource_counts=collector.question_resource_counts,
        difficulty_values_raw=collector.difficulty_values_raw,
        question_meta=collector.question_meta,
    )
    return collector.to_preparation(scales)


# 维护意图：保存跨题目聚合过程中的中间列表，降低主流程分支复杂度
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class QuestionFeatureCollector:
    """保存跨题目聚合过程中的中间列表，降低主流程分支复杂度。"""

    def __init__(self, *, question_ids: list[int], question_id_to_index: dict[int, int]) -> None:
        self.question_ids = question_ids
        self.question_id_to_index = question_id_to_index
        self.score_values: list[float] = []
        self.content_lengths: list[float] = []
        self.analysis_lengths: list[float] = []
        self.attempt_counts: list[float] = []
        self.question_kp_counts: list[float] = []
        self.question_resource_counts: list[float] = []
        self.difficulty_values_raw: list[float] = []
        self.question_meta: list[dict[str, object]] = []
        self.question_to_points: dict[int, list[int]] = {}
        self.point_to_question_indices: dict[int, list[int]] = {}

    # 维护意图：收集一道题的元数据、关系索引与归一化原始值
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def add_question(
        self,
        *,
        question: QuestionLike,
        sources: RuntimeFeatureSources,
        difficulty_to_score: DifficultyToScore,
    ) -> None:
        """收集一道题的元数据、关系索引与归一化原始值。"""
        meta, raw_values, point_index_map = collect_question_feature_entry(
            question=question,
            sources=sources,
            question_id_to_index=self.question_id_to_index,
            difficulty_to_score=difficulty_to_score,
        )
        point_ids = [int(point_id) for point_id in meta["point_ids"]]
        self.question_to_points[int(question.id)] = point_ids
        for point_id, indices in point_index_map.items():
            self.point_to_question_indices.setdefault(point_id, []).extend(indices)
        self.score_values.append(raw_values[0])
        self.content_lengths.append(raw_values[1])
        self.analysis_lengths.append(raw_values[2])
        self.attempt_counts.append(raw_values[3])
        self.question_kp_counts.append(raw_values[5])
        self.question_resource_counts.append(float(len(meta["resource_ids"])))
        self.difficulty_values_raw.append(raw_values[7])
        self.question_meta.append(meta)

    # 维护意图：把收集器状态转换为不可变语义的准备结果对象
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def to_preparation(self, scales: QuestionFeatureScales) -> QuestionFeaturePreparation:
        """把收集器状态转换为不可变语义的准备结果对象。"""
        return QuestionFeaturePreparation(
            question_meta=self.question_meta,
            question_to_points=self.question_to_points,
            point_to_question_indices=self.point_to_question_indices,
            question_ids=self.question_ids,
            question_id_to_index=self.question_id_to_index,
            scales=scales,
        )
