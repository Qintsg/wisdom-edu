"""学生端 GraphRAG 知识点解释与路径规划 mixin。"""
from __future__ import annotations

import logging
from collections.abc import Sequence

from courses.models import Course
from knowledge.models import KnowledgePoint, Resource

from .student_utils import bundle_mode, bundle_sources, dedupe_strings, model_pk, sanitize_answer_text, to_float


logger = logging.getLogger(__name__)


class StudentPointPathMixin:
    """提供知识点解释、详情页支撑证据和学习路径规划能力。"""

    def _find_point(self, course_id: int, point_name: str = "", point_id: int | None = None) -> KnowledgePoint | None:
        """按 point_id 或名称定位课程知识点。"""
        queryset = KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
        if point_id is not None:
            return queryset.filter(id=point_id).first()
        normalized_name = point_name.strip()
        if not normalized_name:
            return None
        return queryset.filter(name__icontains=normalized_name).order_by("order", "id").first()

    def _estimate_point_difficulty(self, point: KnowledgePoint) -> str:
        """根据知识点元数据估计学习难度。"""
        if point.level <= 2:
            return "基础"
        if point.level <= 4:
            return "中等"
        return "进阶"

    def build_path_context(self, *, course_id: int, target: str, pending_points: Sequence[KnowledgePoint]) -> dict[str, object]:
        """为学习路径规划构建 GraphRAG 背景。"""
        pending_names = [point.name for point in pending_points if point is not None]
        seed_entity_ids = {f"kp:{model_pk(point)}" for point in pending_points if point is not None and model_pk(point) > 0}
        query = f"{target or '提升课程掌握度'}；待规划知识点：{'、'.join(pending_names[:8])}"
        context_bundle = self._compose_query_context(course_id, query, seed_entity_ids)
        retrieved_context = "\n".join(
            section
            for section in [
                f"学习目标：{target or '提升课程掌握度'}",
                f"优先关注知识点：{'、'.join(pending_names[:8])}" if pending_names else "",
                str(context_bundle.get("context", "")).strip(),
            ]
            if section
        )
        return {"retrieved_context": retrieved_context, "retrieved_sources": bundle_sources(context_bundle)[:10]}

    def build_point_support_payload(self, *, course_id: int, point: KnowledgePoint) -> dict[str, object]:
        """为知识图谱详情页生成可解释的 GraphRAG 证据摘要。"""
        point_pk = model_pk(point)
        context_bundle = self._compose_query_context(course_id, f"解释知识点：{point.name}", {f"kp:{point_pk}"})
        graph_query_bundle: dict[str, object] = {}
        try:
            graph_query_bundle = self._runtime().query_graph(
                course_id=course_id,
                query=f"{point.name} 的前置知识、后续知识和课程证据是什么？",
                focus_point_id=point_pk,
                focus_point_name=point.name,
                limit=5,
            )
        except Exception as error:
            logger.warning("知识点详情图查询失败，回退现有 GraphRAG 摘要: course=%s point=%s error=%s", course_id, point_pk, error)
            graph_query_bundle = {}

        context_lines = [
            line.strip()
            for line in (str(graph_query_bundle.get("context", "")).splitlines() + str(context_bundle.get("context", "")).splitlines())
            if line.strip() and not line.startswith("[")
        ]
        merged_sources = self._merge_sources(bundle_sources(graph_query_bundle), bundle_sources(context_bundle))
        resolved_mode = bundle_mode(graph_query_bundle, "graph_rag")
        return {"summary": " ".join(context_lines[:4])[:280], "sources": merged_sources[:6], "mode": resolved_mode or "graph_rag"}

    def explain_knowledge_point(
        self,
        *,
        course_id: int,
        point_name: str,
        point_id: int | None = None,
        question: str,
    ) -> dict[str, object]:
        """基于 GraphRAG 解释知识点。"""
        point = self._find_point(course_id, point_name=point_name, point_id=point_id)
        if point is None:
            return {
                "point_id": point_id,
                "point_name": point_name,
                "introduction": f"暂未在当前课程中定位到“{point_name}”的知识图谱实体。",
                "key_concepts": [],
                "learning_tips": ["请确认知识点名称后重试。"],
                "difficulty": "未知",
                "sources": [],
            }

        query = question or f"解释知识点：{point.name}"
        point_pk = model_pk(point)
        context_bundle = self._compose_query_context(course_id, query, {f"kp:{point_pk}"})
        prerequisite_names = [item.name for item in point.get_prerequisites()[:3]]
        postrequisite_names = [item.name for item in point.get_dependents()[:3]]
        visible_resources = list(Resource.objects.filter(knowledge_points=point, is_visible=True).order_by("sort_order", "id")[:3])
        resource_titles = [resource.title for resource in visible_resources]
        key_concepts = dedupe_strings(point.get_tags_list() + prerequisite_names + postrequisite_names + resource_titles)[:6]
        learning_tips = dedupe_strings([
            f"先回顾前置知识：{'、'.join(prerequisite_names)}。" if prerequisite_names else "",
            f"优先学习课程资源：{'、'.join(resource_titles)}。" if resource_titles else "",
            f"掌握后可继续衔接：{'、'.join(postrequisite_names)}。" if postrequisite_names else "",
            "建议先理解定义与例子，再通过练习题检验掌握情况。",
        ])[:4]
        fallback = {
            "point_id": point_pk,
            "point_name": point.name,
            "introduction": point.introduction or point.description or point.name,
            "key_concepts": key_concepts,
            "learning_tips": learning_tips,
            "difficulty": self._estimate_point_difficulty(point),
            "sources": bundle_sources(context_bundle)[:6],
        }

        llm = self._llm_facade()
        if not llm.is_available:
            return fallback

        prompt = f"""# 任务
请基于提供的 GraphRAG 证据，用中文解释课程知识点并给出学习建议。

# 学生问题
{query}

# 知识点实体
- 名称：{point.name}
- 章节：{point.chapter or '未分章'}
- 描述：{point.description or ''}
- 简介：{point.introduction or ''}
- 前置知识：{'、'.join(prerequisite_names) if prerequisite_names else '暂无'}
- 后续知识：{'、'.join(postrequisite_names) if postrequisite_names else '暂无'}

# GraphRAG 上下文
{context_bundle.get('context', '')}

# JSON输出格式
{{
  "point_id": {point_pk},
  "point_name": "{point.name}",
  "introduction": "80-160字的知识点介绍",
  "key_concepts": ["关键概念1", "关键概念2"],
  "learning_tips": ["学习建议1", "学习建议2"],
  "difficulty": "基础/中等/进阶"
}}

# 约束
1. 仅使用给定证据，不要臆造未出现的课程事实。
2. 若证据不足，可以用“建议结合课程资源继续确认”表达不确定性。
3. 输出必须是合法 JSON。
"""
        result = llm.call_with_fallback(prompt=prompt, call_type="graph_rag_point_explain", fallback_response=fallback)
        result["sources"] = fallback["sources"]
        return result

    def plan_learning_path(
        self,
        *,
        course: Course,
        mastery_data: list[dict[str, object]],
        target: str,
        constraints: dict[str, object] | None,
        max_nodes: int = 6,
    ) -> dict[str, object]:
        """将 GraphRAG 上下文注入 LLM 路径规划。"""
        ranked_mastery = sorted(mastery_data, key=lambda item: to_float(item.get("mastery_rate", 0.0), default=0.0))
        weak_names = [str(item.get("point_name", "")).strip() for item in ranked_mastery[:max_nodes]]
        course_pk = model_pk(course)
        point_queryset = KnowledgePoint.objects.filter(course_id=course_pk, is_published=True)
        point_map = {point.name: point for point in point_queryset}
        pending_points = [point_map[name] for name in weak_names if name in point_map]

        rag_context = self.build_path_context(course_id=course_pk, target=target, pending_points=pending_points)
        merged_constraints = dict(constraints or {})
        if not merged_constraints.get("retrieved_context"):
            merged_constraints["retrieved_context"] = rag_context["retrieved_context"]
        if not merged_constraints.get("retrieved_sources"):
            merged_constraints["retrieved_sources"] = rag_context["retrieved_sources"]

        result = self._llm_facade().plan_learning_path(
            mastery_data=mastery_data,
            target=target,
            constraints=merged_constraints,
            course_name=course.name,
            max_nodes=max_nodes,
        )
        result["sources"] = rag_context["retrieved_sources"]
        return result
