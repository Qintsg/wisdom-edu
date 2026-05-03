"""阶段测试取题与响应构造逻辑。"""

from __future__ import annotations

import logging
import random

from assessments.models import Question
from common.utils import build_normalized_score_map, normalize_question_options
from exams.models import Exam, ExamQuestion
from knowledge.models import KnowledgePoint
from learning.models import NodeProgress, PathNode
from learning.view_helpers import _clean_text_for_llm


logger = logging.getLogger(__name__)


# 维护意图：为阶段测试节点构造题目响应数据和可选提示消息
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_stage_test_payload(node: PathNode, node_id: int) -> tuple[dict[str, object], str | None]:
    """为阶段测试节点构造题目响应数据和可选提示消息。"""
    knowledge_point_ids = _stage_knowledge_point_ids(node)
    questions = _select_stage_questions(node, node_id, knowledge_point_ids)
    stage_test_result = _stage_test_result(node)
    if not questions:
        return _empty_stage_test_payload(node, stage_test_result), "暂无可用题目"

    return (
        {
            "node_id": node.id,
            "node_title": node.title,
            "questions": _serialize_stage_questions(questions, knowledge_point_ids),
            "total_score": 100,
            "pass_score": 60,
            "result": stage_test_result,
        },
        None,
    )


# 维护意图：收集当前测试覆盖的上一段学习节点知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _stage_knowledge_point_ids(node: PathNode) -> set[int]:
    """收集当前测试覆盖的上一段学习节点知识点。"""
    prev_test = (
        PathNode.objects.filter(
            path=node.path,
            order_index__lt=node.order_index,
            node_type="test",
        )
        .order_by("-order_index")
        .first()
    )
    lower_bound = prev_test.order_index if prev_test else -1
    point_ids = set(
        PathNode.objects.filter(
            path=node.path,
            order_index__gt=lower_bound,
            order_index__lt=node.order_index,
            node_type="study",
            knowledge_point_id__isnull=False,
        ).values_list("knowledge_point_id", flat=True)
    )
    if not point_ids and node.knowledge_point_id:
        point_ids.add(node.knowledge_point_id)
    return point_ids


# 维护意图：优先使用绑定套题，否则从题库候选中取题
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _select_stage_questions(
    node: PathNode,
    node_id: int,
    knowledge_point_ids: set[int],
) -> list[Question]:
    """优先使用绑定套题，否则从题库候选中取题。"""
    exam_set = _resolve_stage_exam(node, knowledge_point_ids)
    if exam_set:
        return _questions_from_exam(exam_set)
    return _questions_from_bank(node, node_id, knowledge_point_ids)


# 维护意图：获取节点显式绑定或课程内已发布的阶段测试套题
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _resolve_stage_exam(node: PathNode, knowledge_point_ids: set[int]) -> Exam | None:
    """获取节点显式绑定或课程内已发布的阶段测试套题。"""
    if node.exam_id:
        return node.exam
    return (
        Exam.objects.filter(
            course=node.path.course,
            exam_type="question_set",
            status="published",
        )
        .filter(questions__knowledge_points__id__in=knowledge_point_ids)
        .distinct()
        .first()
    )


# 维护意图：按试卷题序读取阶段测试题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _questions_from_exam(exam_set: Exam) -> list[Question]:
    """按试卷题序读取阶段测试题目。"""
    exam_questions = (
        ExamQuestion.objects.filter(exam=exam_set)
        .select_related("question")
        .order_by("order")
    )
    return [exam_question.question for exam_question in exam_questions]


# 维护意图：从课程题库候选题中选择阶段测试题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _questions_from_bank(
    node: PathNode,
    node_id: int,
    knowledge_point_ids: set[int],
) -> list[Question]:
    """从课程题库候选题中选择阶段测试题目。"""
    candidates = _candidate_questions(node, knowledge_point_ids)
    if not candidates:
        logger.info(
            "阶段测试KP匹配无题，降级到课程级别查询: node_id=%s, kp_ids=%s",
            node_id,
            knowledge_point_ids,
        )
        candidates = _course_questions(node)
    if len(candidates) <= 10:
        return candidates
    return _pick_stage_questions_with_llm(node, candidates, knowledge_point_ids)


# 维护意图：读取知识点关联候选题
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _candidate_questions(node: PathNode, knowledge_point_ids: set[int]) -> list[Question]:
    """读取知识点关联候选题。"""
    return list(
        Question.objects.filter(
            course=node.path.course,
            knowledge_points__id__in=knowledge_point_ids,
            is_visible=True,
        )
        .distinct()
        .prefetch_related("knowledge_points")
    )


# 维护意图：知识点无题时回退到课程可见题库
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _course_questions(node: PathNode) -> list[Question]:
    """知识点无题时回退到课程可见题库。"""
    return list(
        Question.objects.filter(course=node.path.course, is_visible=True)
        .distinct()
        .prefetch_related("knowledge_points")
    )


# 维护意图：使用 LLM 从候选题中选择阶段测试题，失败时随机回退
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _pick_stage_questions_with_llm(
    node: PathNode,
    candidates: list[Question],
    knowledge_point_ids: set[int],
) -> list[Question]:
    """使用 LLM 从候选题中选择阶段测试题，失败时随机回退。"""
    try:
        from ai_services.services import llm_service as _llm

        selected_ids = _llm.select_stage_test_questions(
            candidates=_candidate_info(candidates),
            kp_names=_knowledge_point_names(knowledge_point_ids),
            count=10,
        )
        if not selected_ids:
            return candidates[:10]
        id_set = set(selected_ids)
        selected_questions = [question for question in candidates if question.id in id_set]
        return selected_questions or candidates[:10]
    except Exception as exc:
        logger.warning("LLM选题失败，回退随机选题: %s", exc)
        random.shuffle(candidates)
        return candidates[:10]


# 维护意图：限制 LLM 输入体积，只传递候选题摘要
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _candidate_info(candidates: list[Question]) -> list[dict[str, object]]:
    """限制 LLM 输入体积，只传递候选题摘要。"""
    return [
        {
            "id": question.id,
            "content": _clean_text_for_llm(question.content),
            "type": question.question_type,
            "difficulty": question.difficulty,
        }
        for question in candidates[:50]
    ]


# 维护意图：读取阶段测试覆盖知识点名称
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _knowledge_point_names(knowledge_point_ids: set[int]) -> list[str]:
    """读取阶段测试覆盖知识点名称。"""
    return [
        KnowledgePoint.objects.filter(id=knowledge_point_id)
        .values_list("name", flat=True)
        .first()
        or ""
        for knowledge_point_id in knowledge_point_ids
    ]


# 维护意图：读取节点已有阶段测试结果，供前端回显
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _stage_test_result(node: PathNode) -> object:
    """读取节点已有阶段测试结果，供前端回显。"""
    progress = NodeProgress.objects.filter(node=node, user=node.path.user).first()
    if progress and isinstance(progress.extra_data, dict):
        return progress.extra_data.get("stage_test_result")
    return None


# 维护意图：构造暂无题目时的兼容响应
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _empty_stage_test_payload(node: PathNode, stage_test_result: object) -> dict[str, object]:
    """构造暂无题目时的兼容响应。"""
    return {
        "questions": [],
        "node_id": node.id,
        "message": "暂无可用题目",
        "pass_score": 60,
        "total_score": 100,
        "result": stage_test_result,
    }


# 维护意图：序列化阶段测试题目列表
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _serialize_stage_questions(
    questions: list[Question],
    knowledge_point_ids: set[int],
) -> list[dict[str, object]]:
    """序列化阶段测试题目列表。"""
    stage_score_map = build_normalized_score_map(
        [(question.id, 1) for question in questions],
        target_total_score=100,
        equal_weight=True,
    )
    return [
        _serialize_stage_question(question, knowledge_point_ids, stage_score_map)
        for question in questions
    ]


# 维护意图：序列化单道阶段测试题
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _serialize_stage_question(
    question: Question,
    knowledge_point_ids: set[int],
    stage_score_map: dict[str, float],
) -> dict[str, object]:
    """序列化单道阶段测试题。"""
    item = {
        "id": question.id,
        "content": question.content,
        "question_type": question.question_type,
        "difficulty": question.difficulty,
        "score": stage_score_map.get(str(question.id), 0),
        "knowledge_points": [
            {"id": point.id, "name": point.name}
            for point in question.knowledge_points.filter(id__in=knowledge_point_ids)
        ],
    }
    if question.question_type in ("single_choice", "multiple_choice", "true_false"):
        item["options"] = _serialize_stage_options(question)
    return item


# 维护意图：将题目选项规整为前端阶段测试需要的字段
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _serialize_stage_options(question: Question) -> list[dict[str, object]]:
    """将题目选项规整为前端阶段测试需要的字段。"""
    return [
        {
            "key": option.get("letter") or option.get("value"),
            "value": option.get("content") or option.get("label") or option.get("value"),
            "answer_value": option.get("value"),
        }
        for option in normalize_question_options(question.options, question.question_type)
    ]
