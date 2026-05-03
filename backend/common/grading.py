"""题目判分与考试得分计算工具。"""

from __future__ import annotations

import re
from typing import Any, Iterable


# 维护意图：计算知识点掌握度。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def calculate_mastery(correct_count: int | float, total_count: int | float) -> float:
    """
    计算知识点掌握度。

    :param correct_count: 正确数量。
    :param total_count: 总数量。
    :return: 0 到 1 之间的三位小数。
    """
    if total_count == 0:
        return 0.0
    return round(correct_count / total_count, 3)


# 维护意图：解析 JSONField 中的真实答案值。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_answer_value(answer: Any) -> Any:
    """
    解析 JSONField 中的真实答案值。

    :param answer: 原始答案或 envelope。
    :return: 可直接判题的答案值。
    """
    if isinstance(answer, dict):
        if "answers" in answer and answer.get("answers") is not None:
            return answer.get("answers")
        if "answer" in answer:
            return answer.get("answer")
    return answer


# 维护意图：将文本答案规整为用于比较的大小写无关形式
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _normalize_text_answer(value: Any) -> str:
    """将文本答案规整为用于比较的大小写无关形式。"""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return re.sub(r"\s+", " ", str(value)).strip().upper()


# 维护意图：将单选/多选答案规整为去重后的选项值列表
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _normalize_option_values(answer: Any) -> list[str]:
    """将单选/多选答案规整为去重后的选项值列表。"""
    value = extract_answer_value(answer)
    if value is None:
        return []

    if isinstance(value, str):
        raw_items = value.split(",") if "," in value else [value]
    elif isinstance(value, (list, tuple, set)):
        raw_items = list(value)
    else:
        raw_items = [value]

    normalized = []
    for item in raw_items:
        text = _normalize_text_answer(item)
        if text:
            normalized.append(text)
    return sorted(set(normalized))


# 维护意图：将中英文真假值规整为布尔值
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _normalize_boolean_answer(answer: Any) -> bool | None:
    """将中英文真假值规整为布尔值。"""
    value = _normalize_text_answer(extract_answer_value(answer))
    if value in {"TRUE", "1", "YES", "Y", "T", "对", "正确"}:
        return True
    if value in {"FALSE", "0", "NO", "N", "F", "错", "错误"}:
        return False
    return None


# 维护意图：判断单道题目的答案正误。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def check_answer(question_type: str, student_answer: Any, correct_answer: Any) -> bool:
    """
    判断单道题目的答案正误。

    :param question_type: 题目类型。
    :param student_answer: 学生提交的答案。
    :param correct_answer: 正确答案。
    :return: 答案是否正确。
    """
    if student_answer is None:
        return False

    if question_type == "multiple_choice":
        correct_set = set(_normalize_option_values(correct_answer))
        student_set = set(_normalize_option_values(student_answer))
        return bool(correct_set) and correct_set == student_set

    if question_type == "true_false":
        correct_bool = _normalize_boolean_answer(correct_answer)
        student_bool = _normalize_boolean_answer(student_answer)
        if correct_bool is None or student_bool is None:
            return _normalize_text_answer(student_answer) == _normalize_text_answer(
                extract_answer_value(correct_answer)
            )
        return correct_bool == student_bool

    correct_value = extract_answer_value(correct_answer)
    if question_type in ("single_choice", "fill_blank", "short_answer", "code"):
        return _normalize_text_answer(student_answer) == _normalize_text_answer(
            correct_value
        )

    return False


# 维护意图：根据原始权重构建归一化后的题目分值。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_normalized_score_map(
    score_items: Iterable[tuple[Any, Any]],
    target_total_score: float | None = None,
    equal_weight: bool = False,
) -> dict[str, float]:
    """
    根据原始权重构建归一化后的题目分值。

    :param score_items: 题目 ID 与原始分值序列。
    :param target_total_score: 归一化后的目标总分。
    :param equal_weight: 是否强制等权重。
    :return: 题目 ID 到归一化分值的映射。
    """
    normalized_items = [
        (str(item_id), max(float(raw_score or 0), 0.0))
        for item_id, raw_score in score_items
    ]
    if not normalized_items:
        return {}

    raw_total = sum(score for _, score in normalized_items)
    if target_total_score is None or float(target_total_score) <= 0:
        base_total = raw_total or float(len(normalized_items))
    else:
        base_total = float(target_total_score)

    if equal_weight or raw_total <= 0:
        per_score = base_total / len(normalized_items)
        score_map = {item_id: round(per_score, 2) for item_id, _ in normalized_items}
    else:
        score_map = {
            item_id: round(base_total * raw_score / raw_total, 2)
            for item_id, raw_score in normalized_items
        }

    current_total = round(sum(score_map.values()), 2)
    rounding_diff = round(base_total - current_total, 2)
    if rounding_diff and normalized_items:
        last_id = normalized_items[-1][0]
        score_map[last_id] = round(score_map[last_id] + rounding_diff, 2)

    return score_map


# 维护意图：统一评分入口，支持显式题目权重。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def score_questions(
    answers: dict[str, Any], questions: Iterable[Any], score_map: dict[str, float] | None = None
) -> dict[str, Any]:
    """
    统一评分入口，支持显式题目权重。

    :param answers: 学生答案映射。
    :param questions: 题目对象序列。
    :param score_map: 可选题目分值映射。
    :return: 得分、错题、知识点统计与逐题结果。
    """
    total_score = 0.0
    earned_score = 0.0
    mistakes = []
    point_stats: dict[int, dict[str, Any]] = {}
    question_results = []
    normalized_score_map = {
        str(key): float(value) for key, value in (score_map or {}).items()
    }

    for question in questions:
        question_id = str(question.id)
        assigned_score = normalized_score_map.get(
            question_id, float(question.score or 0)
        )
        student_answer = answers.get(question_id)
        correct_answer = extract_answer_value(question.answer)
        is_correct = check_answer(
            question.question_type, student_answer, question.answer
        )
        current_score = assigned_score if is_correct else 0.0

        total_score += assigned_score
        earned_score += current_score
        question_results.append(
            {
                "question_id": question.id,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "assigned_score": round(assigned_score, 2),
                "earned_score": round(current_score, 2),
                "analysis": getattr(question, "analysis", None),
            }
        )

        if not is_correct:
            mistakes.append(
                {
                    "question_id": question.id,
                    "correct_answer": correct_answer,
                    "student_answer": student_answer,
                    "analysis": getattr(question, "analysis", None),
                    "assigned_score": round(assigned_score, 2),
                }
            )

        for point in question.knowledge_points.all():
            if point.id not in point_stats:
                point_stats[point.id] = {
                    "correct": 0,
                    "total": 0,
                    "name": point.name,
                    "earned_score": 0.0,
                    "total_score": 0.0,
                }
            point_stats[point.id]["total"] += 1
            point_stats[point.id]["total_score"] += assigned_score
            if is_correct:
                point_stats[point.id]["correct"] += 1
                point_stats[point.id]["earned_score"] += current_score

    return {
        "score": round(earned_score, 2),
        "total_score": round(total_score, 2),
        "mistakes": mistakes,
        "point_stats": point_stats,
        "question_results": question_results,
    }


# 维护意图：兼容旧调用的自动评分入口。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def grade_exam(
    answers: dict[str, Any], questions: Iterable[Any], score_map: dict[str, float] | None = None
) -> tuple[float, list[dict[str, Any]], dict[int, dict[str, Any]]]:
    """
    兼容旧调用的自动评分入口。

    :return: 得分、错题列表和知识点统计。
    """
    result = score_questions(answers, questions, score_map=score_map)
    return result["score"], result["mistakes"], result["point_stats"]


__all__ = [
    "calculate_mastery",
    "extract_answer_value",
    "check_answer",
    "build_normalized_score_map",
    "score_questions",
    "grade_exam",
]
