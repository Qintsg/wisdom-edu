"""
知识测评判题、掌握度融合与结果载荷工具。

将视图中的长流程拆为可复用的纯逻辑步骤，减少入口函数复杂度并集中处理细节。
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from common.utils import decorate_question_options, serialize_answer_payload
from knowledge.models import KnowledgePoint
from learning.path_rules import apply_prerequisite_caps
from users.models import User

from .assessment_helpers import (
    build_answer_display_value,
    calculate_initial_mastery_baseline,
    clean_text,
    get_question_title,
)
from .history_models import AnswerHistory
from .question_models import Question


logger = logging.getLogger(__name__)


@dataclass
class KnowledgeAssessmentEvaluation:
    """Normalized evaluation result for a single knowledge-assessment submission."""

    total_score: float
    total_possible_score: float
    correct_count: int
    total_question_count: int
    point_stats: dict[int, dict[str, object]]
    question_details: list[dict[str, object]]
    answer_history_records: list[dict[str, int]]
    answer_history_models: list[AnswerHistory]
    mastery_map: dict[int, float]


def normalize_bool_answer(value: object) -> bool | None:
    """将真假题答案归一化为布尔值。"""
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in ['true', 't', '1', 'y', 'yes', '是', '对', '正确', '√', 'right']:
        return True
    if normalized in ['false', 'f', '0', 'n', 'no', '否', '错', '错误', '×', 'wrong']:
        return False
    return None


def resolve_correct_answer_payload(question: Question) -> object:
    """提取题目的标准答案载荷。"""
    if isinstance(question.answer, dict):
        return question.answer.get('answer', question.answer)
    return question.answer


def is_answer_correct(question: Question, student_answer_raw: object, correct_answer_raw: object) -> bool:
    """根据题型判断学生答案是否正确。"""
    if question.question_type == 'true_false':
        student_bool = normalize_bool_answer(student_answer_raw)
        correct_bool = normalize_bool_answer(correct_answer_raw)
        return student_bool is not None and correct_bool is not None and student_bool == correct_bool

    if question.question_type == 'single_choice':
        return clean_text(student_answer_raw) == clean_text(correct_answer_raw)

    if question.question_type == 'multiple_choice':
        correct_set = {
            clean_text(item)
            for item in (correct_answer_raw if isinstance(correct_answer_raw, list) else [correct_answer_raw])
            if clean_text(item)
        }
        student_set = {
            clean_text(item)
            for item in (student_answer_raw if isinstance(student_answer_raw, list) else [student_answer_raw])
            if clean_text(item)
        }
        return bool(correct_set) and correct_set == student_set

    return False


def build_question_detail_payload(
    question: Question,
    *,
    student_answer_raw: object,
    correct_answer_raw: object,
    is_correct: bool,
    knowledge_points: list[KnowledgePoint],
) -> dict[str, object]:
    """构建返回给前端的单题详情载荷。"""
    decorated_options = decorate_question_options(
        question.options,
        question.question_type,
        student_answer=student_answer_raw,
        correct_answer=correct_answer_raw,
    )
    return {
        'question_id': question.id,
        'content': get_question_title(question),
        'question_type': question.question_type,
        'student_answer': student_answer_raw,
        'correct_answer': correct_answer_raw,
        'student_answer_display': build_answer_display_value(
            student_answer_raw, question.question_type, decorated_options
        ),
        'correct_answer_display': build_answer_display_value(
            correct_answer_raw, question.question_type, decorated_options
        ),
        'is_correct': is_correct,
        'analysis': clean_text(question.analysis),
        'options': decorated_options,
        'knowledge_points': [{'id': point.id, 'name': point.name} for point in knowledge_points],
    }


def build_answer_history_models(
    *,
    user: User,
    course_id: int | str,
    question: Question,
    knowledge_points: list[KnowledgePoint],
    student_answer_raw: object,
    correct_answer_raw: object,
    is_correct: bool,
) -> tuple[list[dict[str, int]], list[AnswerHistory]]:
    """构建 KT 预测记录和批量落库所需的答题历史模型。"""
    history_records: list[dict[str, int]] = []
    history_models: list[AnswerHistory] = []
    serialized_student_answer = serialize_answer_payload(question.question_type, student_answer_raw)
    serialized_correct_answer = serialize_answer_payload(question.question_type, correct_answer_raw)
    awarded_score = float(question.score) if is_correct else 0.0
    normalized_course_id = int(course_id)

    for point in knowledge_points:
        history_records.append(
            {
                'question_id': question.id,
                'knowledge_point_id': point.id,
                'correct': 1 if is_correct else 0,
            }
        )
        history_models.append(
            AnswerHistory(
                user=user,
                course_id=normalized_course_id,
                question=question,
                knowledge_point=point,
                student_answer=serialized_student_answer,
                correct_answer=serialized_correct_answer,
                is_correct=is_correct,
                score=awarded_score,
                source='initial',
            )
        )
    return history_records, history_models


def evaluate_knowledge_answers(
    *,
    user: User,
    course_id: int | str,
    questions: list[Question],
    answer_dict: dict[str, object],
) -> KnowledgeAssessmentEvaluation:
    """对整份知识测评作答完成判题、统计与掌握度基线计算。"""
    total_score = 0.0
    total_possible_score = 0.0
    correct_count = 0
    point_stats: dict[int, dict[str, object]] = {}
    question_details: list[dict[str, object]] = []
    answer_history_records: list[dict[str, int]] = []
    answer_history_models: list[AnswerHistory] = []

    for question in questions:
        question_id = str(question.id)
        student_answer_raw = answer_dict.get(question_id)
        correct_answer_raw = resolve_correct_answer_payload(question)
        knowledge_points = list(question.knowledge_points.all())
        total_possible_score += float(question.score or 0)
        is_correct = is_answer_correct(question, student_answer_raw, correct_answer_raw)
        if is_correct:
            total_score += float(question.score or 0)
            correct_count += 1

        question_details.append(
            build_question_detail_payload(
                question,
                student_answer_raw=student_answer_raw,
                correct_answer_raw=correct_answer_raw,
                is_correct=is_correct,
                knowledge_points=knowledge_points,
            )
        )
        history_records, history_models = build_answer_history_models(
            user=user,
            course_id=course_id,
            question=question,
            knowledge_points=knowledge_points,
            student_answer_raw=student_answer_raw,
            correct_answer_raw=correct_answer_raw,
            is_correct=is_correct,
        )
        answer_history_records.extend(history_records)
        answer_history_models.extend(history_models)

        for point in knowledge_points:
            point_stats.setdefault(point.id, {'correct': 0, 'total': 0, 'name': point.name})
            point_stats[point.id]['total'] += 1
            if is_correct:
                point_stats[point.id]['correct'] += 1

    mastery_map = {
        point_id: calculate_initial_mastery_baseline(int(stats['correct']), int(stats['total']))
        for point_id, stats in point_stats.items()
    }
    return KnowledgeAssessmentEvaluation(
        total_score=total_score,
        total_possible_score=total_possible_score,
        correct_count=correct_count,
        total_question_count=len(questions),
        point_stats=point_stats,
        question_details=question_details,
        answer_history_records=answer_history_records,
        answer_history_models=answer_history_models,
        mastery_map=mastery_map,
    )


def blend_mastery_with_kt(
    *,
    user_id: int,
    course_id: int | str,
    mastery_map: dict[int, float],
    point_stats: dict[int, dict[str, object]],
    answer_history_records: list[dict[str, int]],
) -> dict[int, float]:
    """结合 KT 预测结果对知识测评基线掌握度做保守融合。"""
    try:
        from ai_services.services import kt_service

        kt_result = kt_service.predict_mastery(
            user_id=user_id,
            course_id=course_id,
            answer_history=answer_history_records,
        )
    except Exception as exc:
        logger.warning("KT预测或更新失败: %s", exc)
        return apply_prerequisite_caps(mastery_map, int(course_id))

    kt_predictions = kt_result.get('predictions') or {}
    if not kt_predictions:
        return apply_prerequisite_caps(mastery_map, int(course_id))

    blended_mastery_map = dict(mastery_map)
    for knowledge_point_id, rate in kt_predictions.items():
        try:
            normalized_point_id = int(knowledge_point_id)
            rate_f = float(rate)
        except (TypeError, ValueError):
            continue
        point_total = max(int(point_stats.get(normalized_point_id, {}).get('total', 0)), 0)
        baseline = float(mastery_map.get(normalized_point_id, 0.25))
        kt_weight = min(0.35, 0.1 + point_total * 0.08)
        blended = baseline * (1 - kt_weight) + rate_f * kt_weight
        blended = min(blended, baseline + 0.12)
        blended_mastery_map[normalized_point_id] = round(max(0.0, min(0.9, blended)), 4)
    return apply_prerequisite_caps(blended_mastery_map, int(course_id))


def build_feedback_report_payload(report: object | None) -> dict[str, object] | None:
    """将反馈报告模型规整为前端消费的响应结构。"""
    if report is None or getattr(report, 'status', '') != 'completed':
        return None
    overview = getattr(report, 'overview', None) or {}
    analysis = getattr(report, 'analysis', '')
    return {
        'report_id': getattr(report, 'id', None),
        'overview': overview,
        'summary': overview.get('summary', ''),
        'analysis': analysis if isinstance(analysis, str) else '',
        'knowledge_gaps': overview.get('knowledge_gaps', [])
        or (analysis if isinstance(analysis, list) else []),
        'recommendations': getattr(report, 'recommendations', None) or [],
        'next_tasks': getattr(report, 'next_tasks', None) or [],
        'encouragement': getattr(report, 'conclusion', '') or '',
        'conclusion': getattr(report, 'conclusion', '') or '',
    }


def build_empty_knowledge_result(
    *,
    generating: bool = False,
    generation_error: str | None = None,
    completed: bool = False,
) -> dict[str, object]:
    """构建知识测评结果接口的空载荷。"""
    return {
        'score': 0,
        'total_score': 0,
        'correct_count': 0,
        'total_count': 0,
        'mastery': [],
        'question_details': [],
        'feedback_report': None,
        'generating': generating,
        'generation_error': generation_error,
        'completed': completed,
    }


__all__ = [
    'KnowledgeAssessmentEvaluation',
    'normalize_bool_answer',
    'resolve_correct_answer_payload',
    'is_answer_correct',
    'build_question_detail_payload',
    'build_answer_history_models',
    'evaluate_knowledge_answers',
    'blend_mastery_with_kt',
    'build_feedback_report_payload',
    'build_empty_knowledge_result',
]
