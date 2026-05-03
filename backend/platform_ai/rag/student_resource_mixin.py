"""学生端学习节点资源推荐 mixin。"""
from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass

from django.contrib.auth.models import AbstractBaseUser

from knowledge.models import KnowledgePoint, Resource
from learning.models import PathNode
from platform_ai.mcp.resources import InternalResourceCandidate

from .student_utils import append_internal_resource, dedupe_strings, model_pk, to_int


logger = logging.getLogger(__name__)


# 维护意图：节点资源推荐所需上下文，避免在多个 helper 间传递长参数列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class NodeResourceRecommendationRequest:
    """节点资源推荐所需上下文，避免在多个 helper 间传递长参数列表。"""

    node: PathNode
    user: AbstractBaseUser
    mastery_value: float | None
    completed_resource_ids: set[str]
    internal_count: int = 3
    external_count: int = 2


# 维护意图：为学习路径节点推荐内部课程资源和外部补充材料
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentResourceRecommendationMixin:
    """为学习路径节点推荐内部课程资源和外部补充材料。"""

    # 维护意图：兼容历史调用形态的节点资源推荐入口
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def recommend_node_resources(self, **request_data: object) -> dict[str, object]:
        """兼容历史调用形态的节点资源推荐入口。"""
        request_context = NodeResourceRecommendationRequest(
            node=request_data["node"],
            user=request_data["user"],
            mastery_value=request_data.get("mastery_value"),
            completed_resource_ids=request_data["completed_resource_ids"],
            internal_count=int(request_data.get("internal_count", 3) or 3),
            external_count=int(request_data.get("external_count", 2) or 2),
        )
        return self._recommend_node_resources(request_context)

    # 维护意图：对外暴露稳定的节点资源推荐入口
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def recommend_resources_for_node(
        self,
        *,
        node: PathNode,
        user: AbstractBaseUser,
        mastery_value: float | None,
        completed_resource_ids: set[str],
        external_count: int = 2,
    ) -> dict[str, object]:
        """对外暴露稳定的节点资源推荐入口。"""
        request_context = NodeResourceRecommendationRequest(
            node=node,
            user=user,
            mastery_value=mastery_value,
            completed_resource_ids=completed_resource_ids,
            external_count=external_count,
        )
        return self._recommend_node_resources(request_context)

    # 维护意图：按知识点上下文生成内部和外部资源推荐
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _recommend_node_resources(
        self,
        request_context: NodeResourceRecommendationRequest,
    ) -> dict[str, object]:
        """按知识点上下文生成内部和外部资源推荐。"""
        point = request_context.node.knowledge_point
        if point is None:
            logger.info(
                "学习节点缺少知识点，跳过资源推荐: node=%s user=%s",
                model_pk(request_context.node),
                model_pk(request_context.user),
            )
            return {"internal_resources": [], "external_resources": []}

        internal_candidates = self._search_internal_candidates(request_context, point)
        candidate_resources = _resource_map(internal_candidates)
        ordered_resources = _ordered_resources(internal_candidates, candidate_resources)
        internal_resources = self._build_internal_resources(
            request_context,
            point,
            candidate_resources,
            ordered_resources,
        )
        external_resources = self._build_external_resources(
            request_context,
            point,
            ordered_resources,
        )
        return {
            "internal_resources": internal_resources,
            "external_resources": external_resources,
        }

    # 维护意图：从 MCP 资源服务取项目内候选资源
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _search_internal_candidates(
        self,
        request_context: NodeResourceRecommendationRequest,
        point: KnowledgePoint,
    ) -> list[InternalResourceCandidate]:
        """从 MCP 资源服务取项目内候选资源。"""
        return self._resource_mcp_service().search_internal_resources(
            node=request_context.node,
            point=point,
            mastery_value=request_context.mastery_value,
            limit=max(request_context.internal_count * 4, request_context.internal_count),
        )

    # 维护意图：结合 LLM 选择结果或排序候选，生成内部资源响应
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_internal_resources(
        self,
        request_context: NodeResourceRecommendationRequest,
        point: KnowledgePoint,
        candidate_resources: Mapping[int, Resource],
        ordered_resources: list[Resource],
    ) -> list[dict[str, object]]:
        """结合 LLM 选择结果或排序候选，生成内部资源响应。"""
        selected_ids, selected_reason_map = self._select_internal_resources(
            request_context,
            point,
            candidate_resources,
            ordered_resources,
        )
        internal_resources: list[dict[str, object]] = []
        for resource_id_text in dedupe_strings(str(item) for item in selected_ids):
            resource_id = int(resource_id_text)
            resource = candidate_resources.get(resource_id)
            if resource is None:
                continue
            reason, learning_tips = selected_reason_map.get(
                resource_id,
                (f"该资源与“{point.name}”紧密相关。", "建议完成学习后立即自测。"),
            )
            append_internal_resource(
                internal_resources,
                resource,
                reason,
                request_context.completed_resource_ids,
                learning_tips,
            )
        return internal_resources

    # 维护意图：优先用 LLM 选择内部资源，失败时回退到图谱排序结果
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _select_internal_resources(
        self,
        request_context: NodeResourceRecommendationRequest,
        point: KnowledgePoint,
        candidate_resources: Mapping[int, Resource],
        ordered_resources: list[Resource],
    ) -> tuple[list[int], dict[int, tuple[str, str]]]:
        """优先用 LLM 选择内部资源，失败时回退到图谱排序结果。"""
        selected_ids: list[int] = []
        selected_reason_map: dict[int, tuple[str, str]] = {}
        llm = self._llm_facade()
        available_resources = _serialize_available_resources(point, ordered_resources)

        if llm.is_available and available_resources:
            selected_ids, selected_reason_map = _parse_internal_llm_result(
                llm.recommend_internal_resources(
                    point_name=point.name,
                    student_mastery=request_context.mastery_value,
                    available_resources=available_resources,
                    course_name=request_context.node.path.course.name,
                    count=request_context.internal_count,
                ),
                point,
                candidate_resources,
            )

        if selected_ids:
            return selected_ids, selected_reason_map
        return _fallback_internal_selection(
            point,
            ordered_resources,
            request_context.internal_count,
        )

    # 维护意图：生成外部资源推荐，MCP 搜索为空时再调用 LLM 兜底
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_external_resources(
        self,
        request_context: NodeResourceRecommendationRequest,
        point: KnowledgePoint,
        ordered_resources: list[Resource],
    ) -> list[dict[str, object]]:
        """生成外部资源推荐，MCP 搜索为空时再调用 LLM 兜底。"""
        if request_context.external_count <= 0:
            return []

        existing_titles = [candidate_resource.title for candidate_resource in ordered_resources]
        external_candidates = self._resource_mcp_service().search_external_resources(
            point_name=point.name,
            student_mastery=request_context.mastery_value,
            existing_titles=existing_titles,
            course_name=request_context.node.path.course.name,
            count=request_context.external_count,
        )
        if external_candidates:
            return [
                candidate.to_response()
                for candidate in external_candidates[: request_context.external_count]
            ]

        return _parse_external_llm_result(
            self._llm_facade().recommend_external_resources(
                point_name=point.name,
                student_mastery=request_context.mastery_value,
                existing_titles=existing_titles,
                course_name=request_context.node.path.course.name,
                count=request_context.external_count,
            ),
            point.name,
            request_context.external_count,
        )


# 维护意图：按资源 ID 去重候选资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _resource_map(
    internal_candidates: list[InternalResourceCandidate],
) -> dict[int, Resource]:
    """按资源 ID 去重候选资源。"""
    return {
        candidate.resource_id: candidate.resource
        for candidate in internal_candidates
        if candidate.resource_id > 0
    }


# 维护意图：保持 MCP 候选排序，同时过滤无效资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _ordered_resources(
    internal_candidates: list[InternalResourceCandidate],
    candidate_resources: Mapping[int, Resource],
) -> list[Resource]:
    """保持 MCP 候选排序，同时过滤无效资源。"""
    return [
        candidate.resource
        for candidate in internal_candidates
        if candidate.resource_id in candidate_resources
    ]


# 维护意图：序列化给 LLM 选择内部资源的候选摘要
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _serialize_available_resources(
    point: KnowledgePoint,
    ordered_resources: list[Resource],
) -> list[dict[str, object]]:
    """序列化给 LLM 选择内部资源的候选摘要。"""
    return [
        {
            "id": model_pk(candidate_resource),
            "title": candidate_resource.title,
            "type": candidate_resource.resource_type,
            "description": candidate_resource.description or "",
            "chapter": candidate_resource.chapter_number or point.chapter or "",
        }
        for candidate_resource in ordered_resources
    ]


# 维护意图：解析 LLM 内部资源推荐，剔除不在候选集内的资源 ID
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_internal_llm_result(
    internal_result: Mapping[str, object],
    point: KnowledgePoint,
    candidate_resources: Mapping[int, Resource],
) -> tuple[list[int], dict[int, tuple[str, str]]]:
    """解析 LLM 内部资源推荐，剔除不在候选集内的资源 ID。"""
    raw_resources = internal_result.get("resources")
    if not isinstance(raw_resources, list):
        return [], {}

    selected_ids: list[int] = []
    selected_reason_map: dict[int, tuple[str, str]] = {}
    for item in raw_resources:
        if not isinstance(item, Mapping):
            continue
        resource_id = to_int(item.get("id"), default=0)
        if resource_id <= 0 or resource_id not in candidate_resources:
            continue
        selected_ids.append(resource_id)
        selected_reason_map[resource_id] = (
            str(item.get("reason", "")).strip() or f"该资源与“{point.name}”直接关联。",
            str(item.get("learning_tips", "")).strip() or "建议结合笔记梳理关键知识点。",
        )
    return selected_ids, selected_reason_map


# 维护意图：LLM 不可用或未返回有效 ID 时，使用图谱排序候选兜底
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _fallback_internal_selection(
    point: KnowledgePoint,
    ordered_resources: list[Resource],
    internal_count: int,
) -> tuple[list[int], dict[int, tuple[str, str]]]:
    """LLM 不可用或未返回有效 ID 时，使用图谱排序候选兜底。"""
    selected_resources = ordered_resources[:internal_count]
    selected_ids = [model_pk(candidate_resource) for candidate_resource in selected_resources]
    selected_reason_map = {
        model_pk(candidate_resource): (
            f"该课程资源直接关联“{point.name}”，适合当前阶段优先学习。",
            "建议先看定义与示例，再完成对应练习巩固。",
        )
        for candidate_resource in selected_resources
    }
    return selected_ids, selected_reason_map


# 维护意图：将 LLM 外部资源推荐转换为统一响应结构
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_external_llm_result(
    external_result: Mapping[str, object],
    point_name: str,
    external_count: int,
) -> list[dict[str, object]]:
    """将 LLM 外部资源推荐转换为统一响应结构。"""
    external_payload = external_result.get("resources")
    if not isinstance(external_payload, list):
        return []

    external_resources: list[dict[str, object]] = []
    for item in external_payload[:external_count]:
        if not isinstance(item, Mapping):
            continue
        external_resources.append(
            {
                "title": str(item.get("title", "")).strip() or f"{point_name} 外部资源",
                "url": str(item.get("url", "")).strip(),
                "type": str(item.get("type", "link")).strip() or "link",
                "recommended_reason": str(item.get("reason", "")).strip()
                or f"该外部资源与“{point_name}”相关，可作为补充学习材料。",
                "learning_tips": "建议先完成课程内资源，再使用外部资源扩展理解。",
                "is_internal": False,
                "completed": False,
            }
        )
    return external_resources
