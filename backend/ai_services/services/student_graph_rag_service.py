"""GraphRAG service for the student AI assistant."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import logging
import re

from dataclasses import dataclass

from django.db.models import Q

from common.neo4j_service import neo4j_service
from knowledge.models import KnowledgeMastery, KnowledgePoint
from platform_ai.llm import llm_facade
from platform_ai.rag import student_learning_rag
from platform_ai.rag.runtime import COURSE_RETRIEVAL_MODE, student_graphrag_runtime


logger = logging.getLogger(__name__)


GRAPH_STRUCTURE_KEYWORDS: tuple[str, ...] = (
    "关系",
    "联系",
    "区别",
    "差异",
    "依赖",
    "先修",
    "前置",
    "后续",
    "顺序",
    "路径",
    "链路",
    "关联",
)


@dataclass(frozen=True)
class PointSearchItem:
    """Graph search result item."""

    point_id: int
    point_name: str
    chapter: str
    description: str
    mastery_rate: float
    prerequisites: list[str]
    postrequisites: list[str]

    def to_dict(self) -> dict[str, object]:
        """Convert the search item into a response payload."""

        return {
            "point_id": self.point_id,
            "point_name": self.point_name,
            "chapter": self.chapter,
            "description": self.description,
            "mastery_rate": self.mastery_rate,
            "prerequisites": self.prerequisites,
            "postrequisites": self.postrequisites,
        }


class StudentGraphRAGService:
    """Provide graph search and graph-grounded Q&A capabilities."""

    def _normalize_match_text(self, text: str) -> str:
        """Normalize free-form text for stable in-question point-name matching."""

        lowered_text = text.strip().lower()
        return re.sub(r"[\W_]+", "", lowered_text, flags=re.UNICODE)

    def _is_graph_structure_question(self, question: str) -> bool:
        """Detect whether the question is mainly about graph structure or relations."""

        normalized_question = question.strip()
        return any(keyword in normalized_question for keyword in GRAPH_STRUCTURE_KEYWORDS)

    def _match_points_by_query_text(
        self,
        *,
        course_id: int,
        query: str,
        limit: int = 3,
    ) -> list[KnowledgePoint]:
        """Resolve explicit course knowledge points directly mentioned in a question."""

        normalized_query = self._normalize_match_text(query)
        if not normalized_query:
            return []

        ranked_points: list[tuple[int, int, int, KnowledgePoint]] = []
        point_queryset = KnowledgePoint.objects.filter(
            course_id=course_id,
            is_published=True,
        ).only("id", "name", "order")
        for point in point_queryset:
            normalized_name = self._normalize_match_text(point.name)
            if len(normalized_name) < 2 or normalized_name not in normalized_query:
                continue
            ranked_points.append((
                -len(normalized_name),
                int(getattr(point, "order", 0) or 0),
                int(point.id),
                point,
            ))

        ranked_points.sort(key=lambda item: (item[0], item[1], item[2]))
        matched_points: list[KnowledgePoint] = []
        seen_ids: set[int] = set()
        for _, _, point_id, point in ranked_points:
            if point_id in seen_ids:
                continue
            seen_ids.add(point_id)
            matched_points.append(point)
            if len(matched_points) >= limit:
                break
        return matched_points

    def _resolve_point_from_ids(
        self,
        *,
        course_id: int,
        point_ids: list[int],
    ) -> KnowledgePoint | None:
        """Pick the first existing published point from a candidate ID list."""

        normalized_ids = [point_id for point_id in point_ids if point_id > 0]
        if not normalized_ids:
            return None

        point_map = {
            int(point.id): point
            for point in KnowledgePoint.objects.filter(
                course_id=course_id,
                is_published=True,
                id__in=normalized_ids,
            )
        }
        for point_id in normalized_ids:
            matched_point = point_map.get(point_id)
            if matched_point is not None:
                return matched_point
        return None

    def _extract_text_list(self, payload: Mapping[str, object], field: str) -> list[str]:
        """Normalize a response field into a compact string list."""

        raw_items = payload.get(field)
        if not isinstance(raw_items, list):
            return []
        return [
            str(item).strip()
            for item in raw_items
            if str(item).strip()
        ]

    def _extract_matched_point_ids(
        self,
        rag_result: Mapping[str, object] | None,
    ) -> list[int]:
        """Normalize matched point IDs from a course-level RAG payload."""

        if not isinstance(rag_result, Mapping):
            return []
        raw_point_ids = rag_result.get("matched_point_ids", [])
        if not isinstance(raw_point_ids, Iterable) or isinstance(raw_point_ids, (str, bytes, Mapping)):
            return []

        normalized_ids: list[int] = []
        for raw_point_id in raw_point_ids:
            if isinstance(raw_point_id, bool):
                continue
            if isinstance(raw_point_id, int):
                if raw_point_id > 0:
                    normalized_ids.append(raw_point_id)
                continue
            point_id_text = str(raw_point_id).strip()
            if point_id_text.isdigit():
                normalized_ids.append(int(point_id_text))
        return normalized_ids

    def _has_course_rag_result(self, rag_result: Mapping[str, object] | None) -> bool:
        """Check whether the course-level RAG payload contains usable evidence."""

        if not isinstance(rag_result, Mapping):
            return False
        raw_sources = rag_result.get("sources", [])
        return bool(raw_sources) or bool(self._extract_matched_point_ids(rag_result))

    def _extract_first_search_point_id(self, search_result: Mapping[str, object]) -> int | None:
        """Get the first matched point ID from a search payload when available."""

        raw_matches = search_result.get("matched_points", [])
        if not isinstance(raw_matches, list) or not raw_matches:
            return None

        first_match = raw_matches[0]
        if not isinstance(first_match, Mapping):
            return None
        raw_point_id = first_match.get("point_id")
        if isinstance(raw_point_id, bool):
            return None
        if isinstance(raw_point_id, int):
            return raw_point_id if raw_point_id > 0 else None
        point_id_text = str(raw_point_id).strip()
        return int(point_id_text) if point_id_text.isdigit() else None

    def _build_graph_answer_payload(
        self,
        *,
        user,
        matched_point: KnowledgePoint | None,
        rag_result: dict[str, object],
    ) -> dict[str, object]:
        """Convert RAG service output into the stable API response shape."""

        search_item = self._build_search_item(user, matched_point) if matched_point is not None else None
        related_points = {
            "prerequisites": search_item.prerequisites if search_item is not None else [],
            "postrequisites": search_item.postrequisites if search_item is not None else [],
        }
        return {
            "reply": str(rag_result.get("answer", rag_result.get("reply", ""))).strip(),
            "sources": rag_result.get("sources", []),
            "mode": str(rag_result.get("mode", "")).strip() or "graph_rag",
            "query_modes": self._extract_text_list(rag_result, "query_modes"),
            "key_points": self._extract_text_list(rag_result, "key_points"),
            "matched_point": search_item.to_dict() if search_item is not None else None,
            "related_points": related_points,
        }

    def _build_search_item(self, user, point: KnowledgePoint) -> PointSearchItem:
        """Build a graph search item with relation summaries."""

        mastery_record = KnowledgeMastery.objects.filter(
            user=user,
            course_id=point.course_id,
            knowledge_point_id=point.id,
        ).first()
        mastery_rate = float(mastery_record.mastery_rate) if mastery_record else 0.0

        prerequisites: list[str] = []
        postrequisites: list[str] = []
        if neo4j_service.is_available:
            neo4j_point = neo4j_service.get_knowledge_point_neo4j(point.id)
            if neo4j_point:
                prerequisites = [
                    str(item.get("point_name", "")).strip()
                    for item in neo4j_point.get("prerequisites", [])
                    if str(item.get("point_name", "")).strip()
                ][:4]
                postrequisites = [
                    str(item.get("point_name", "")).strip()
                    for item in neo4j_point.get("postrequisites", [])
                    if str(item.get("point_name", "")).strip()
                ][:4]

        return PointSearchItem(
            point_id=point.id,
            point_name=point.name,
            chapter=point.chapter or "未分章",
            description=(point.introduction or point.description or "")[:180],
            mastery_rate=mastery_rate,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
        )

    def search_points(
        self, *, user, course_id: int, query: str, limit: int = 8
    ) -> dict[str, object]:
        """Search knowledge points within the current course graph."""

        normalized_query = query.strip()
        if not normalized_query:
            return {
                "query": "",
                "matched_points": [],
                "retrieval_mode": "empty_query",
            }

        # 优先走 Neo4j GraphRAG + Qdrant 混合检索，确保 AI 助手与知识图谱共用同一底座。
        try:
            graph_rag_matches = student_graphrag_runtime.search_points(
                course_id=course_id,
                query=normalized_query,
                limit=limit,
            )
        except Exception as error:
            logger.warning("GraphRAG 混合检索失败，回退课程内关键字检索: course=%s error=%s", course_id, error)
            graph_rag_matches = []

        if graph_rag_matches:
            point_ids = [
                int(item.get("point_id", 0))
                for item in graph_rag_matches
                if int(item.get("point_id", 0)) > 0
            ]
            point_map = {
                getattr(point, "id", 0): point
                for point in KnowledgePoint.objects.filter(
                    course_id=course_id,
                    is_published=True,
                    id__in=point_ids,
                )
            }
            matched_points = []
            for match in graph_rag_matches:
                point_id = int(match.get("point_id", 0))
                point = point_map.get(point_id)
                if point is None:
                    continue
                item = self._build_search_item(user, point).to_dict()
                item["graph_rag_score"] = float(match.get("graph_rag_score", 0.0))
                item["supporting_sources"] = [
                    str(title).strip()
                    for title in match.get("source_titles", [])
                    if str(title).strip()
                ]
                if not item["prerequisites"]:
                    item["prerequisites"] = [
                        str(entry.get("point_name", "")).strip()
                        for entry in match.get("prerequisites", [])
                        if isinstance(entry, dict)
                        and str(entry.get("point_name", "")).strip()
                    ][:4]
                if not item["postrequisites"]:
                    item["postrequisites"] = [
                        str(entry.get("point_name", "")).strip()
                        for entry in match.get("postrequisites", [])
                        if isinstance(entry, dict)
                        and str(entry.get("point_name", "")).strip()
                    ][:4]
                matched_points.append(item)

            if matched_points:
                return {
                    "query": normalized_query,
                    "matched_points": matched_points,
                    "retrieval_mode": COURSE_RETRIEVAL_MODE,
                }

        point_name_matches = self._match_points_by_query_text(
            course_id=course_id,
            query=normalized_query,
            limit=limit,
        )
        if point_name_matches:
            return {
                "query": normalized_query,
                "matched_points": [
                    self._build_search_item(user, point).to_dict()
                    for point in point_name_matches
                ],
                "retrieval_mode": "name_match",
            }

        point_queryset = (
            KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
            .filter(
                Q(name__icontains=normalized_query)
                | Q(description__icontains=normalized_query)
                | Q(introduction__icontains=normalized_query)
                | Q(tags__icontains=normalized_query)
            )
            .order_by("order", "id")[:limit]
        )
        matched_points = [
            self._build_search_item(user, point).to_dict() for point in point_queryset
        ]
        return {
            "query": normalized_query,
            "matched_points": matched_points,
            "retrieval_mode": "graph_search" if matched_points else "no_match",
        }

    def ask(
        self, *, user, course_id: int, question: str, point_id: int | None = None
    ) -> dict[str, object]:
        """Run GraphRAG question answering under the current course context."""

        matched_point: KnowledgePoint | None = None
        course_rag_result: dict[str, object] | None = None
        if point_id is not None:
            matched_point = KnowledgePoint.objects.filter(
                id=point_id,
                course_id=course_id,
                is_published=True,
            ).first()

        if matched_point is None:
            explicit_points = self._match_points_by_query_text(
                course_id=course_id,
                query=question,
                limit=3,
            )
            if len(explicit_points) >= 2 or self._is_graph_structure_question(question):
                course_rag_response = student_learning_rag.answer_course_question(
                    course_id=course_id,
                    question=question,
                    seed_point_ids=[int(point.id) for point in explicit_points],
                )
                course_rag_result = course_rag_response
                matched_point = explicit_points[0] if explicit_points else self._resolve_point_from_ids(
                    course_id=course_id,
                    point_ids=self._extract_matched_point_ids(course_rag_response),
                )
                if self._has_course_rag_result(course_rag_response):
                    return self._build_graph_answer_payload(
                        user=user,
                        matched_point=matched_point,
                        rag_result=course_rag_response,
                    )

            if explicit_points:
                matched_point = explicit_points[0]

        if matched_point is None:
            search_result = self.search_points(
                user=user,
                course_id=course_id,
                query=question,
                limit=1,
            )
            best_point_id = self._extract_first_search_point_id(search_result)
            if best_point_id is not None:
                matched_point = KnowledgePoint.objects.filter(
                    id=best_point_id,
                    course_id=course_id,
                    is_published=True,
                ).first()

        if matched_point is not None:
            rag_result = student_learning_rag.answer_graph_question(
                course_id=course_id,
                point=matched_point,
                question=question,
            )
            return self._build_graph_answer_payload(
                user=user,
                matched_point=matched_point,
                rag_result=rag_result,
            )

        if course_rag_result is None:
            course_rag_result = student_learning_rag.answer_course_question(
                course_id=course_id,
                question=question,
            )
        assert course_rag_result is not None
        matched_point = self._resolve_point_from_ids(
            course_id=course_id,
            point_ids=self._extract_matched_point_ids(course_rag_result),
        )
        if self._has_course_rag_result(course_rag_result):
            return self._build_graph_answer_payload(
                user=user,
                matched_point=matched_point,
                rag_result=course_rag_result,
            )

        fallback = {
            "reply": (
                f"当前问题是“{question}”。系统暂未在当前课程知识图谱中命中明确知识点，"
                "下面给出课程级通用学习建议。"
            ),
            "sources": [],
            "mode": "llm_fallback",
            "matched_point": None,
            "related_points": {
                "prerequisites": [],
                "postrequisites": [],
            },
        }
        if llm_facade.is_available:
            result = llm_facade.call_with_fallback(
                prompt=(
                    "请以中文回答学生的问题，回答需要适用于教学场景，尽量给出下一步学习建议。"
                    f"\n课程ID：{course_id}"
                    f"\n问题：{question}"
                ),
                call_type="graph_rag_chat_fallback",
                fallback_response=fallback,
            )
            return {
                **fallback,
                "reply": result.get("reply", result.get("answer", fallback["reply"])),
            }
        return fallback


student_graph_rag_service = StudentGraphRAGService()
