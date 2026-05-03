"""学生端 GraphRAG 问答响应组装工具。"""
from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol, TypeAlias

from knowledge.models import KnowledgePoint

from .student_utils import (
    bundle_mode,
    bundle_positive_ints,
    bundle_query_modes,
    bundle_sources,
    dedupe_ints,
    dedupe_strings,
    sanitize_answer_text,
    to_int,
)


logger = logging.getLogger(__name__)
SourceList: TypeAlias = list[dict[str, object]]
SourceMerger: TypeAlias = Callable[[SourceList, SourceList], SourceList]


# 维护意图：学生问答只依赖 LLM 门面的可用性和 fallback 调用能力
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class LLMAnswerFacade(Protocol):
    """学生问答只依赖 LLM 门面的可用性和 fallback 调用能力。"""

    is_available: bool

    # 维护意图：调用 LLM，并在底层失败时返回 fallback 响应
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def call_with_fallback(
        self,
        *,
        prompt: str,
        call_type: str,
        fallback_response: dict[str, object],
    ) -> dict[str, object]:
        """调用 LLM，并在底层失败时返回 fallback 响应。"""


# 维护意图：学生问答只依赖运行时的结构化图查询能力
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class GraphQueryRuntime(Protocol):
    """学生问答只依赖运行时的结构化图查询能力。"""

    # 维护意图：按课程、问题和可选知识点焦点查询图谱证据
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def query_graph(
        self,
        *,
        course_id: int,
        query: str,
        focus_point_id: int | None,
        focus_point_name: str,
        limit: int,
    ) -> dict[str, object]:
        """按课程、问题和可选知识点焦点查询图谱证据。"""


# 维护意图：课程级 GraphRAG 查询焦点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class CourseGraphFocus:
    """课程级 GraphRAG 查询焦点。"""

    seed_point_ids: list[int]
    seed_entity_ids: set[str]
    focus_point_id: int | None
    focus_point_name: str


# 维护意图：课程级问答命中的知识点与候选展示名
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class CourseAnswerCandidates:
    """课程级问答命中的知识点与候选展示名。"""

    matched_point_ids: list[int]
    candidate_names: list[str]


# 维护意图：LLM 答案生成前的证据、模式和降级内容
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class AnswerEvidenceBundle:
    """LLM 答案生成前的证据、模式和降级内容。"""

    combined_context: str
    sources: SourceList
    query_modes: list[str]
    resolved_mode: str
    fallback_answer: str
    fallback_response: dict[str, object]


# 维护意图：从课程索引实体中提取知识点 ID 到名称的映射
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_point_name_map(entities: Iterable[dict[str, object]]) -> dict[int, str]:
    """从课程索引实体中提取知识点 ID 到名称的映射。"""
    point_name_map: dict[int, str] = {}
    for entity in entities:
        if str(entity.get("entity_type", "")).strip() != "knowledge_point":
            continue
        point_id = _entity_knowledge_point_id(entity)
        point_name = str(entity.get("title", "")).strip()
        if point_id > 0 and point_name:
            point_name_map[point_id] = point_name
    return point_name_map


# 维护意图：兼容 metadata 与 kp:<id> 两种索引实体主键来源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _entity_knowledge_point_id(entity: dict[str, object]) -> int:
    """兼容 metadata 与 kp:<id> 两种索引实体主键来源。"""
    metadata = entity.get("metadata")
    point_id = to_int(metadata.get("knowledge_point_id"), default=0) if isinstance(metadata, dict) else 0
    if point_id > 0:
        return point_id
    entity_id = str(entity.get("id", "")).strip()
    if entity_id.startswith("kp:"):
        return to_int(entity_id.partition(":")[2], default=0)
    return 0


# 维护意图：将课程级问答种子知识点规整为 GraphRAG 查询焦点
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_graph_focus(
    *,
    seed_point_ids: Sequence[int],
    point_name_map: dict[int, str],
) -> CourseGraphFocus:
    """将课程级问答种子知识点规整为 GraphRAG 查询焦点。"""
    resolved_seed_ids = [point_id for point_id in seed_point_ids if point_id > 0]
    focus_point_id = resolved_seed_ids[0] if resolved_seed_ids else None
    return CourseGraphFocus(
        seed_point_ids=resolved_seed_ids,
        seed_entity_ids={f"kp:{point_id}" for point_id in resolved_seed_ids},
        focus_point_id=focus_point_id,
        focus_point_name=point_name_map.get(focus_point_id or 0, ""),
    )


# 维护意图：合并结构化图查询与 local/global/drift 证据上下文
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def combine_answer_context(
    graph_query_bundle: dict[str, object],
    context_bundle: dict[str, object],
) -> str:
    """合并结构化图查询与 local/global/drift 证据上下文。"""
    return "\n\n".join(
        section
        for section in [
            str(graph_query_bundle.get("context", "")).strip(),
            str(context_bundle.get("context", "")).strip(),
        ]
        if section
    )


# 维护意图：组装知识点级问答所需的证据和 fallback
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_graph_answer_evidence(
    *,
    graph_query_bundle: dict[str, object],
    context_bundle: dict[str, object],
    sources: SourceList,
    point: KnowledgePoint,
) -> AnswerEvidenceBundle:
    """组装知识点级问答所需的证据和 fallback。"""
    source_titles = extract_source_titles(sources, limit=4)
    fallback_answer = build_graph_fallback_answer(point, source_titles)
    fallback_response = {"answer": fallback_answer, "key_points": dedupe_strings(source_titles)}
    return AnswerEvidenceBundle(
        combined_context=combine_answer_context(graph_query_bundle, context_bundle),
        sources=sources,
        query_modes=bundle_query_modes(graph_query_bundle),
        resolved_mode=bundle_mode(graph_query_bundle, "graph_rag"),
        fallback_answer=fallback_answer,
        fallback_response=fallback_response,
    )


# 维护意图：组装课程级问答所需的证据、fallback 与候选知识点
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_answer_evidence(
    *,
    course_id: int,
    graph_query_bundle: dict[str, object],
    context_bundle: dict[str, object],
    sources: SourceList,
    focus: CourseGraphFocus,
    point_name_map: dict[int, str],
) -> tuple[AnswerEvidenceBundle, CourseAnswerCandidates]:
    """组装课程级问答所需的证据、fallback 与候选知识点。"""
    candidates = resolve_course_answer_candidates(
        course_id=course_id,
        point_name_map=point_name_map,
        seed_point_ids=focus.seed_point_ids,
        graph_query_bundle=graph_query_bundle,
    )
    source_titles = extract_source_titles(sources, limit=5)
    fallback_answer = build_course_fallback_answer(candidates.candidate_names, source_titles)
    fallback_response = {
        "answer": fallback_answer,
        "key_points": dedupe_strings(candidates.candidate_names + source_titles)[:5],
    }
    evidence = AnswerEvidenceBundle(
        combined_context=combine_answer_context(graph_query_bundle, context_bundle),
        sources=sources,
        query_modes=bundle_query_modes(graph_query_bundle),
        resolved_mode=bundle_mode(graph_query_bundle, "graph_rag_course"),
        fallback_answer=fallback_answer,
        fallback_response=fallback_response,
    )
    return evidence, candidates


# 维护意图：合并种子知识点与图查询命中，补齐候选知识点名称
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_course_answer_candidates(
    *,
    course_id: int,
    point_name_map: dict[int, str],
    seed_point_ids: Sequence[int],
    graph_query_bundle: dict[str, object],
) -> CourseAnswerCandidates:
    """合并种子知识点与图查询命中，补齐候选知识点名称。"""
    matched_point_ids = dedupe_ints(
        list(seed_point_ids) + bundle_positive_ints(graph_query_bundle, "matched_point_ids")
    )
    candidate_names = dedupe_strings(point_name_map.get(point_id, "") for point_id in matched_point_ids)
    missing_point_ids = [point_id for point_id in matched_point_ids if point_id not in point_name_map]
    if missing_point_ids:
        candidate_names = _append_missing_point_names(course_id, candidate_names, missing_point_ids)
    return CourseAnswerCandidates(
        matched_point_ids=matched_point_ids,
        candidate_names=candidate_names,
    )


# 维护意图：从数据库补齐索引缺失的知识点名称
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _append_missing_point_names(
    course_id: int,
    candidate_names: list[str],
    missing_point_ids: list[int],
) -> list[str]:
    """从数据库补齐索引缺失的知识点名称。"""
    database_names = list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True, id__in=missing_point_ids)
        .order_by("order", "id")
        .values_list("name", flat=True)
    )
    return dedupe_strings(candidate_names + database_names)


# 维护意图：提取前端证据标题并去重
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_source_titles(sources: Iterable[dict[str, object]], *, limit: int) -> list[str]:
    """提取前端证据标题并去重。"""
    return dedupe_strings(str(source.get("title", "")).strip() for source in sources)[:limit]


# 维护意图：调用结构化图查询，失败时返回空证据包并保留日志
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def query_graph_bundle(
    runtime: GraphQueryRuntime,
    *,
    course_id: int,
    question: str,
    focus_point_id: int | None,
    focus_point_name: str,
    warning_label: str,
) -> dict[str, object]:
    """调用结构化图查询，失败时返回空证据包并保留日志。"""
    try:
        return runtime.query_graph(
            course_id=course_id,
            query=question,
            focus_point_id=focus_point_id,
            focus_point_name=focus_point_name,
            limit=6,
        )
    except Exception as error:
        logger.warning("%s: course=%s error=%s", warning_label, course_id, error)
        return {}


# 维护意图：构造知识点级无 LLM 或 LLM 失败时的图谱证据回答
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_graph_fallback_answer(point: KnowledgePoint, source_titles: Sequence[str]) -> str:
    """构造知识点级无 LLM 或 LLM 失败时的图谱证据回答。"""
    return sanitize_answer_text(
        "\n".join(
            section
            for section in [
                f"围绕“{point.name}”，当前课程图谱显示：{point.introduction or point.description or point.name}",
                (
                    f"建议优先结合这些证据继续学习：{'、'.join(source_titles)}。"
                    if source_titles
                    else "建议优先查看课程内与该知识点直接关联的资源。"
                ),
                "如果你想追问先修关系、典型题型或资源推荐，也可以继续细化问题。",
            ]
            if section
        )
    )


# 维护意图：构造课程级无 LLM 或 LLM 失败时的图谱证据回答
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_fallback_answer(candidate_names: Sequence[str], source_titles: Sequence[str]) -> str:
    """构造课程级无 LLM 或 LLM 失败时的图谱证据回答。"""
    return sanitize_answer_text(
        "\n".join(
            section
            for section in [
                (
                    f"围绕当前课程问题，系统命中了这些候选知识点：{'、'.join(candidate_names[:4])}。"
                    if candidate_names
                    else "系统已结合当前课程知识图谱与课程证据进行回答。"
                ),
                (
                    f"可优先查看这些证据：{'、'.join(source_titles[:4])}。"
                    if source_titles
                    else "如果你希望继续深挖，可追问更具体的知识点、先修关系或资源名称。"
                ),
            ]
            if section
        )
    )


# 维护意图：构造知识点级 GraphRAG 问答 prompt
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_graph_answer_prompt(
    *,
    point: KnowledgePoint,
    question: str,
    combined_context: str,
) -> str:
    """构造知识点级 GraphRAG 问答 prompt。"""
    return f"""# 任务
请基于给定 GraphRAG 证据，用中文回答学生问题。

# 学生问题
{question}

# 当前知识点
- 名称：{point.name}
- 章节：{point.chapter or '未分章'}
- 描述：{point.description or ''}

# GraphRAG 上下文
{combined_context}

# JSON输出格式
{{
  "answer": "80-200字回答",
  "key_points": ["要点1", "要点2"]
}}

# 回答约束
1. 只能基于证据回答，不要编造课程外事实。
2. 回答需先直接答题，再补充学习建议。
3. 若证据不足，要明确说“当前证据不足”。
4. 输出必须是合法 JSON。
"""


# 维护意图：构造课程级 GraphRAG 问答 prompt
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_answer_prompt(
    *,
    question: str,
    candidate_names: Sequence[str],
    combined_context: str,
) -> str:
    """构造课程级 GraphRAG 问答 prompt。"""
    candidate_text = (
        "、".join(candidate_names[:6])
        if candidate_names
        else "当前问题未命中唯一知识点，请以课程级证据回答。"
    )
    return f"""# 任务
请基于给定课程的 GraphRAG 证据，用中文直接回答学生问题。

# 学生问题
{question}

# 候选知识点
{candidate_text}

# GraphRAG 上下文
{combined_context}

# JSON输出格式
{{
  "answer": "80-220字回答",
  "key_points": ["要点1", "要点2"]
}}

# 回答约束
1. 只能基于证据回答，不要编造课程外事实。
2. 先直接回答学生问题，再补充下一步学习建议。
3. 如果证据不足，要明确提示“当前证据不足”。
4. 输出必须是合法 JSON。
"""


# 维护意图：调用 LLM 门面，并把异常统一收敛到 fallback
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def call_llm_answer(
    llm: LLMAnswerFacade,
    *,
    prompt: str,
    call_type: str,
    fallback_response: dict[str, object],
) -> dict[str, object]:
    """调用 LLM 门面，并把异常统一收敛到 fallback。"""
    try:
        return llm.call_with_fallback(
            prompt=prompt,
            call_type=call_type,
            fallback_response=fallback_response,
        )
    except Exception as error:
        logger.warning("GraphRAG 学生问答 LLM 调用失败，使用 fallback: type=%s error=%s", call_type, error)
        return fallback_response


# 维护意图：构造知识点级无 LLM 响应
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def graph_answer_without_llm(evidence: AnswerEvidenceBundle) -> dict[str, object]:
    """构造知识点级无 LLM 响应。"""
    return {
        "answer": evidence.fallback_answer,
        "sources": evidence.sources,
        "mode": evidence.resolved_mode or "graph_rag",
        "query_modes": evidence.query_modes,
    }


# 维护意图：构造课程级无 LLM 响应
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def course_answer_without_llm(
    evidence: AnswerEvidenceBundle,
    candidates: CourseAnswerCandidates,
) -> dict[str, object]:
    """构造课程级无 LLM 响应。"""
    return {
        "answer": evidence.fallback_answer,
        "sources": evidence.sources,
        "mode": evidence.resolved_mode,
        "query_modes": evidence.query_modes,
        "key_points": evidence.fallback_response["key_points"],
        "matched_point_ids": candidates.matched_point_ids,
    }


# 维护意图：构造知识点级 LLM 响应并保留证据来源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def graph_answer_with_llm(
    *,
    llm_result: dict[str, object],
    evidence: AnswerEvidenceBundle,
) -> dict[str, object]:
    """构造知识点级 LLM 响应并保留证据来源。"""
    return {
        "answer": sanitize_answer_text(str(llm_result.get("answer", evidence.fallback_answer))),
        "sources": evidence.sources,
        "mode": evidence.resolved_mode or "graph_rag",
        "query_modes": evidence.query_modes,
        "key_points": llm_result.get("key_points", evidence.fallback_response.get("key_points", [])),
    }


# 维护意图：构造课程级 LLM 响应并保留命中知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def course_answer_with_llm(
    *,
    llm_result: dict[str, object],
    evidence: AnswerEvidenceBundle,
    candidates: CourseAnswerCandidates,
) -> dict[str, object]:
    """构造课程级 LLM 响应并保留命中知识点。"""
    return {
        "answer": sanitize_answer_text(str(llm_result.get("answer", evidence.fallback_answer))),
        "sources": evidence.sources,
        "mode": evidence.resolved_mode,
        "query_modes": evidence.query_modes,
        "key_points": llm_result.get("key_points", evidence.fallback_response["key_points"]),
        "matched_point_ids": candidates.matched_point_ids,
    }


# 维护意图：合并结构化图查询和上下文检索来源并限制前端展示数量
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_answer_sources(
    graph_query_bundle: dict[str, object],
    context_bundle: dict[str, object],
    merge_sources: SourceMerger,
) -> SourceList:
    """合并结构化图查询和上下文检索来源并限制前端展示数量。"""
    return merge_sources(bundle_sources(graph_query_bundle), bundle_sources(context_bundle))[:8]
