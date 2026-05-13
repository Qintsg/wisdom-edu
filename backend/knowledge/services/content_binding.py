#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
课程内容与知识点绑定服务。
@Project : wisdom-edu
@File : content_binding.py
@Author : Qintsg
@Date : 2026-05-13 10:35
'''

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from assessments.models import AssessmentResult, Question
from common.domain.utils import serialize_answer_payload
from knowledge.models import KnowledgePoint, Resource
from knowledge.services.content_binding_rules import (
    BIG_DATA_BINDING_RULES,
    FORCE_RULE_POINT_NAMES,
    GENERIC_POINT_NAMES,
    normalize_binding_text,
)


ContentKind = Literal["question", "resource"]


@dataclass(frozen=True)
class ContentBindingChange:
    """一次内容绑定变更计划。"""

    kind: ContentKind
    item_id: int
    title: str
    point_ids: tuple[int, ...]
    point_names: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class InitialHistorySyncChange:
    """一次初始评测历史补齐计划。"""

    user_id: int
    course_id: int
    question_id: int
    point_id: int | None


@dataclass(frozen=True)
class CourseContentBindingPlan:
    """课程内容绑定计划。"""

    question_changes: tuple[ContentBindingChange, ...]
    resource_changes: tuple[ContentBindingChange, ...]
    history_changes: tuple[InitialHistorySyncChange, ...]


class CourseContentBindingService:
    """基于题干、资源标题和知识点名称同步课程内容绑定。"""

    def __init__(self, course_id: int) -> None:
        """
        初始化课程绑定服务。
        :param course_id: 课程 ID。
        :return: None。
        """
        self.course_id = int(course_id)
        self.points = list(KnowledgePoint.objects.filter(course_id=self.course_id).order_by("order", "id"))
        self.points_by_name = {point.name: point for point in self.points}
        self.bound_question_points = self._build_bound_question_points()

    def build_plan(
        self,
        *,
        sync_initial_history: bool = False,
        replace_existing: bool = False,
        replace_initial_history: bool = False,
    ) -> CourseContentBindingPlan:
        """
        构建课程内容绑定计划。
        :param sync_initial_history: 是否同时补齐既有初始评测答题历史。
        :param replace_existing: 是否重新计算并覆盖已有题目/资源绑定。
        :param replace_initial_history: 是否忽略既有初始测评历史并重建。
        :return: 绑定计划。
        """
        question_changes = tuple(self._build_question_changes(replace_existing=replace_existing))
        resource_changes = tuple(self._build_resource_changes(replace_existing=replace_existing))
        planned_question_points = {
            change.item_id: list(change.point_ids)
            for change in question_changes
        }
        history_changes = (
            tuple(
                self._build_initial_history_changes(
                    planned_question_points,
                    ignore_existing=replace_initial_history,
                )
            )
            if sync_initial_history
            else ()
        )
        return CourseContentBindingPlan(
            question_changes=question_changes,
            resource_changes=resource_changes,
            history_changes=history_changes,
        )

    def apply_plan(self, plan: CourseContentBindingPlan, *, replace_initial_history: bool = False) -> None:
        """
        写入课程内容绑定计划。
        :param plan: 待写入计划。
        :param replace_initial_history: 是否先删除目标用户既有初始测评历史。
        :return: None。
        """
        for change in plan.question_changes:
            question = Question.objects.get(id=change.item_id, course_id=self.course_id)
            question.knowledge_points.set(change.point_ids)
        for change in plan.resource_changes:
            resource = Resource.objects.get(id=change.item_id, course_id=self.course_id)
            resource.knowledge_points.set(change.point_ids)
        self._apply_initial_history_changes(
            plan.history_changes,
            replace_initial_history=replace_initial_history,
        )

    def _build_bound_question_points(self) -> dict[str, tuple[int, ...]]:
        """读取已有题目绑定，用于复制同题干题目的知识点。"""
        bound_map: dict[str, tuple[int, ...]] = {}
        for question in Question.objects.filter(course_id=self.course_id).prefetch_related("knowledge_points"):
            point_ids = tuple(question.knowledge_points.order_by("order", "id").values_list("id", flat=True))
            if not point_ids:
                continue
            normalized_content = normalize_binding_text(question.content)
            bound_map.setdefault(normalized_content, point_ids)
        return bound_map

    def _build_question_changes(self, *, replace_existing: bool = False) -> Iterable[ContentBindingChange]:
        """生成题目绑定变更。"""
        questions = Question.objects.filter(course_id=self.course_id).prefetch_related("knowledge_points").order_by("id")
        for question in questions:
            current_point_ids = tuple(question.knowledge_points.order_by("order", "id").values_list("id", flat=True))
            if current_point_ids and not replace_existing:
                continue
            matched_point_ids, reason = self._match_text_to_points(question.content)
            if not matched_point_ids:
                duplicated_points = self.bound_question_points.get(normalize_binding_text(question.content), ())
                matched_point_ids = duplicated_points
                reason = "duplicate_question"
            if not matched_point_ids:
                continue
            if set(current_point_ids) == set(matched_point_ids):
                continue
            yield self._build_change(
                kind="question",
                item_id=int(question.id),
                title=str(question.content)[:120],
                point_ids=matched_point_ids,
                reason=reason,
            )

    def _build_resource_changes(self, *, replace_existing: bool = False) -> Iterable[ContentBindingChange]:
        """生成资源绑定变更。"""
        resources = Resource.objects.filter(course_id=self.course_id).prefetch_related("knowledge_points").order_by("sort_order", "id")
        for resource in resources:
            current_point_ids = tuple(resource.knowledge_points.order_by("order", "id").values_list("id", flat=True))
            if current_point_ids and not replace_existing:
                continue
            searchable_text = " ".join(
                str(part or "")
                for part in (resource.title, resource.description, resource.chapter_number)
            )
            matched_point_ids, reason = self._match_text_to_points(searchable_text)
            if not matched_point_ids:
                continue
            if set(current_point_ids) == set(matched_point_ids):
                continue
            yield self._build_change(
                kind="resource",
                item_id=int(resource.id),
                title=resource.title,
                point_ids=matched_point_ids,
                reason=reason,
            )

    def _match_text_to_points(self, text: str) -> tuple[tuple[int, ...], str]:
        """将文本匹配到课程知识点。"""
        normalized_text = normalize_binding_text(text)
        exact_point_ids = self._match_by_exact_point_name(normalized_text)
        rule_point_ids = self._match_by_big_data_rules(normalized_text)
        if rule_point_ids and self._should_prefer_rule(rule_point_ids, exact_point_ids):
            return rule_point_ids, "big_data_rule"
        if exact_point_ids:
            return exact_point_ids, "point_name"
        if rule_point_ids:
            return rule_point_ids, "big_data_rule"
        return (), ""

    def _match_by_exact_point_name(self, normalized_text: str) -> tuple[int, ...]:
        """按知识点名称子串匹配。"""
        matched_points: list[KnowledgePoint] = []
        for point in sorted(self.points, key=lambda item: len(item.name), reverse=True):
            normalized_name = normalize_binding_text(point.name)
            if len(normalized_name) < 3:
                continue
            if normalized_name in normalized_text:
                matched_points.append(point)
        specific_points = self._drop_contained_generic_points(matched_points)
        return self._dedupe_point_ids(int(point.id) for point in specific_points[:3])

    def _drop_contained_generic_points(self, points: list[KnowledgePoint]) -> list[KnowledgePoint]:
        """删除被更具体知识点名称包含的泛化匹配。"""
        filtered: list[KnowledgePoint] = []
        normalized_names = {
            int(point.id): normalize_binding_text(point.name)
            for point in points
        }
        for point in points:
            current_name = normalized_names[int(point.id)]
            contained_by_specific = any(
                int(other.id) != int(point.id)
                and current_name
                and current_name in normalized_names[int(other.id)]
                for other in points
            )
            if contained_by_specific:
                continue
            filtered.append(point)
        return filtered

    def _match_by_big_data_rules(self, normalized_text: str) -> tuple[int, ...]:
        """按大数据课程领域规则匹配。"""
        for raw_patterns, point_names in BIG_DATA_BINDING_RULES:
            normalized_patterns = [normalize_binding_text(pattern) for pattern in raw_patterns]
            matched_patterns = [
                pattern
                for pattern in normalized_patterns
                if pattern and pattern in normalized_text
            ]
            if not matched_patterns:
                continue
            point_ids = [
                int(self.points_by_name[point_name].id)
                for point_name in point_names
                if point_name in self.points_by_name
            ]
            if point_ids:
                return self._dedupe_point_ids(point_ids)
        return ()

    def _should_prefer_rule(
        self,
        rule_point_ids: tuple[int, ...],
        exact_point_ids: tuple[int, ...],
    ) -> bool:
        """判断领域规则是否比名称子串匹配更可靠。"""
        if not rule_point_ids:
            return False
        if not exact_point_ids:
            return True
        exact_names = {
            point.name
            for point in self.points
            if int(point.id) in set(exact_point_ids)
        }
        rule_names = {
            point.name
            for point in self.points
            if int(point.id) in set(rule_point_ids)
        }
        if rule_names & FORCE_RULE_POINT_NAMES:
            return True
        return bool(exact_names) and all(name in GENERIC_POINT_NAMES for name in exact_names)

    def _build_change(
        self,
        *,
        kind: ContentKind,
        item_id: int,
        title: str,
        point_ids: tuple[int, ...],
        reason: str,
    ) -> ContentBindingChange:
        """构造绑定变更对象。"""
        point_names = tuple(
            point.name
            for point in self.points
            if int(point.id) in set(point_ids)
        )
        return ContentBindingChange(
            kind=kind,
            item_id=item_id,
            title=title,
            point_ids=point_ids,
            point_names=point_names,
            reason=reason,
        )

    def _build_initial_history_changes(
        self,
        planned_question_points: dict[int, list[int]],
        *,
        ignore_existing: bool,
    ) -> Iterable[InitialHistorySyncChange]:
        """为既有初始测评结果补齐题目级历史记录。"""
        from assessments.models import AnswerHistory

        results = AssessmentResult.objects.filter(
            course_id=self.course_id,
            assessment__assessment_type="knowledge",
        ).order_by("user_id", "completed_at")
        existing_keys = (
            set()
            if ignore_existing
            else set(
                AnswerHistory.objects.filter(course_id=self.course_id, source="initial").values_list(
                    "user_id",
                    "question_id",
                    "knowledge_point_id",
                )
            )
        )
        for result in results:
            result_data = result.result_data if isinstance(result.result_data, dict) else {}
            details = result_data.get("question_details") if isinstance(result_data, dict) else []
            if not isinstance(details, list):
                continue
            for detail in details:
                if not isinstance(detail, dict) or not detail.get("question_id"):
                    continue
                question_id = int(detail["question_id"])
                current_point_ids = planned_question_points.get(question_id) or self._question_current_point_ids(question_id)
                for point_id in (current_point_ids or [None]):
                    key = (result.user_id, question_id, point_id)
                    if key in existing_keys:
                        continue
                    existing_keys.add(key)
                    yield InitialHistorySyncChange(
                        user_id=int(result.user_id),
                        course_id=self.course_id,
                        question_id=question_id,
                        point_id=point_id,
                    )

    def _question_current_point_ids(self, question_id: int) -> list[int]:
        """读取题目当前绑定知识点。"""
        try:
            question = Question.objects.get(id=question_id, course_id=self.course_id)
        except Question.DoesNotExist:
            return []
        return [
            int(point_id)
            for point_id in question.knowledge_points.order_by("order", "id").values_list("id", flat=True)
        ]

    def _apply_initial_history_changes(
        self,
        changes: tuple[InitialHistorySyncChange, ...],
        *,
        replace_initial_history: bool,
    ) -> None:
        """写入缺失的初始测评答题历史。"""
        from assessments.models import AnswerHistory

        if not changes:
            return
        if replace_initial_history:
            user_ids = {change.user_id for change in changes}
            AnswerHistory.objects.filter(
                user_id__in=user_ids,
                course_id=self.course_id,
                source="initial",
            ).delete()
        result_lookup = self._build_assessment_result_lookup()
        history_models: list[AnswerHistory] = []
        for change in changes:
            result = result_lookup.get(change.user_id)
            if result is None:
                continue
            detail = self._find_question_detail(result, change.question_id)
            if detail is None:
                continue
            question = Question.objects.get(id=change.question_id, course_id=self.course_id)
            history_models.append(
                AnswerHistory(
                    user_id=change.user_id,
                    course_id=self.course_id,
                    question=question,
                    knowledge_point_id=change.point_id,
                    student_answer=serialize_answer_payload(question.question_type, detail.get("student_answer")),
                    correct_answer=serialize_answer_payload(question.question_type, detail.get("correct_answer")),
                    is_correct=bool(detail.get("is_correct")),
                    score=float(question.score or 0) if detail.get("is_correct") else 0,
                    source="initial",
                )
            )
        if history_models:
            AnswerHistory.objects.bulk_create(history_models, batch_size=200)

    def _build_assessment_result_lookup(self) -> dict[int, AssessmentResult]:
        """按用户读取最新知识测评结果。"""
        lookup: dict[int, AssessmentResult] = {}
        results = AssessmentResult.objects.filter(
            course_id=self.course_id,
            assessment__assessment_type="knowledge",
        ).order_by("user_id", "-completed_at")
        for result in results:
            lookup.setdefault(int(result.user_id), result)
        return lookup

    def _find_question_detail(self, result: AssessmentResult, question_id: int) -> dict[str, object] | None:
        """从测评快照中读取题目详情。"""
        result_data = result.result_data if isinstance(result.result_data, dict) else {}
        details = result_data.get("question_details") if isinstance(result_data, dict) else []
        if not isinstance(details, list):
            return None
        for detail in details:
            if isinstance(detail, dict) and int(detail.get("question_id") or 0) == question_id:
                return detail
        return None

    @staticmethod
    def _dedupe_point_ids(point_ids: Iterable[int]) -> tuple[int, ...]:
        """保持顺序去重知识点 ID。"""
        return tuple(dict.fromkeys(int(point_id) for point_id in point_ids))
