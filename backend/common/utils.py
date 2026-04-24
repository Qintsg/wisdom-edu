"""
工具函数和自定义异常处理。

提供统一的 API 响应格式以及评分、判题等公共工具。
"""

from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.conf import settings
from django.db import DatabaseError
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _normalize_error_detail(detail: Any) -> Any:
    """
    将 DRF ErrorDetail / 列表 / 字典转为可 JSON 序列化的错误详情。

    :param detail: DRF 原始错误数据。
    :return: 仅包含字符串、列表和字典的错误详情。
    """
    if isinstance(detail, dict):
        return {
            str(key): _normalize_error_detail(value)
            for key, value in detail.items()
        }
    if isinstance(detail, (list, tuple)):
        return [_normalize_error_detail(item) for item in detail]
    if detail is None:
        return None
    return str(detail)


def _flatten_error_messages(detail: Any) -> List[str]:
    """
    提取可直接展示给用户的错误消息，优先保留字段名上下文。

    :param detail: 归一化后的错误详情。
    :return: 消息列表。
    """
    if isinstance(detail, dict):
        messages: List[str] = []
        for key, value in detail.items():
            child_messages = _flatten_error_messages(value)
            if key == "detail":
                messages.extend(child_messages)
            elif child_messages:
                messages.extend(f"{key}: {message}" for message in child_messages)
        return messages
    if isinstance(detail, list):
        messages: List[str] = []
        for item in detail:
            messages.extend(_flatten_error_messages(item))
        return messages
    if detail is None:
        return []
    text = str(detail).strip()
    return [text] if text else []


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    自定义异常处理，统一 API 响应格式。
    返回格式: {"code": xxx, "msg": "xxx", "data": null}
    """
    response = exception_handler(exc, context)

    if response is not None:
        normalized_errors = _normalize_error_detail(response.data)
        message = get_error_message(response)
        response.data = {
            "code": response.status_code,
            "msg": message,
            "data": {"errors": normalized_errors} if normalized_errors else None,
            "error": {
                "type": exc.__class__.__name__,
                "details": normalized_errors,
            },
        }
    else:
        request = context.get("request") if isinstance(context, dict) else None
        request_method = getattr(request, "method", "-")
        request_path = getattr(request, "path", "-")
        logger.exception(
            "Unhandled exception | method=%s | path=%s | exc=%s",
            request_method,
            request_path,
            exc,
        )
        response = Response(
            {
                "code": 500,
                "msg": "服务器内部错误" if not settings.DEBUG else str(exc),
                "data": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def get_error_message(response):
    """从 DRF 响应中提取错误信息。"""
    if hasattr(response, "data"):
        normalized_errors = _normalize_error_detail(response.data)
        messages = _flatten_error_messages(normalized_errors)
        if messages:
            return messages[0]

    status_messages = {
        400: "请求参数错误",
        401: "未授权，请先登录",
        403: "权限不足",
        404: "资源不存在",
        405: "不允许的请求方法",
        500: "服务器内部错误",
    }
    return status_messages.get(response.status_code, "请求处理失败")


def calculate_mastery(correct_count, total_count):
    """计算掌握度。"""
    if total_count == 0:
        return 0.0
    return round(correct_count / total_count, 3)


def extract_answer_value(answer: Any) -> Any:
    """解析 JSONField 中的真实答案值。"""
    if isinstance(answer, dict):
        if "answers" in answer and answer.get("answers") is not None:
            return answer.get("answers")
        if "answer" in answer:
            return answer.get("answer")
    return answer


def _normalize_text_answer(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return re.sub(r"\s+", " ", str(value)).strip().upper()


def _normalize_option_values(answer: Any) -> List[str]:
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


def _normalize_boolean_answer(answer: Any) -> Optional[bool]:
    value = _normalize_text_answer(extract_answer_value(answer))
    if value in {"TRUE", "1", "YES", "Y", "T", "对", "正确"}:
        return True
    if value in {"FALSE", "0", "NO", "N", "F", "错", "错误"}:
        return False
    return None


def check_answer(question_type, student_answer, correct_answer):
    """
    判断单道题目的答案正误。

    Args:
        question_type: 题目类型
        student_answer: 学生提交的答案
        correct_answer: 正确答案（原始值或 dict）

    Returns:
        bool - 是否正确
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


def build_normalized_score_map(
    score_items: Iterable[Tuple[Any, Any]],
    target_total_score: Optional[float] = None,
    equal_weight: bool = False,
) -> Dict[str, float]:
    """
    根据原始权重构建归一化后的题目分值。

    Args:
        score_items: [(item_id, raw_score), ...]
        target_total_score: 归一化后的总分
        equal_weight: 是否强制等权重

    Returns:
        dict: {str(item_id): normalized_score}
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


def score_questions(answers, questions, score_map=None):
    """
    统一评分入口，支持显式题目权重。

    Returns:
        {
            'score': float,
            'total_score': float,
            'mistakes': list,
            'point_stats': dict,
            'question_results': list,
        }
    """
    total_score = 0.0
    earned_score = 0.0
    mistakes = []
    point_stats = {}
    question_results = []
    normalized_score_map = {
        str(key): float(value) for key, value in (score_map or {}).items()
    }

    for question in questions:
        q_id = str(question.id)
        assigned_score = normalized_score_map.get(q_id, float(question.score or 0))
        student_answer = answers.get(q_id)
        correct_answer = extract_answer_value(question.answer)
        is_correct = check_answer(
            question.question_type, student_answer, question.answer
        )
        current_score = assigned_score if is_correct else 0.0

        total_score += assigned_score
        earned_score += current_score

        question_result = {
            "question_id": question.id,
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "assigned_score": round(assigned_score, 2),
            "earned_score": round(current_score, 2),
            "analysis": getattr(question, "analysis", None),
        }
        question_results.append(question_result)

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


def grade_exam(answers, questions, score_map=None):
    """
    兼容旧调用的自动评分入口。

    Returns:
        (score, mistakes, point_stats)
    """
    result = score_questions(answers, questions, score_map=score_map)
    return result["score"], result["mistakes"], result["point_stats"]


def validate_course_exists(course_id):
    """
    验证课程是否存在。

    Args:
        course_id: 课程ID

    Returns:
        Course 对象，不存在时返回 None
    """
    from courses.models import Course

    try:
        return Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return None


def resolve_course_id(request):
    """
    从请求中提取课程ID：优先使用请求参数/体，其次使用用户的课程上下文。

    返回 (course_id:int | None, error_response | None)
    """
    from common.responses import error_response as _error_response

    course_id = (
        request.query_params.get("course_id")
        if hasattr(request, "query_params")
        else None
    )
    source = "request"
    if not course_id:
        course_id = request.data.get("course_id") if hasattr(request, "data") else None

    if not course_id and request.user and request.user.is_authenticated:
        try:
            from users.models import UserCourseContext

            context = UserCourseContext.objects.filter(user=request.user).first()
            context_course_id = getattr(context, "current_course_id", None)
            if context_course_id:
                course_id = context_course_id
                source = "context"
        except (AttributeError, DatabaseError, ImportError) as error:
            logger.warning("failed to resolve course_id from user context: %s", error)

    if not course_id:
        return None, _error_response(msg="缺少课程ID")

    course_id_text = str(course_id).strip()

    try:
        course_id_int = int(course_id_text)
        if source == "context":
            logger.debug("course_id resolved from user context: %s", course_id_int)
        return course_id_int, None
    except (ValueError, TypeError):
        logger.warning("invalid course_id format: %s", course_id)
        return None, _error_response(msg="课程ID格式错误")


def paginate_list(items, page=1, page_size=20):
    """
    对列表进行分页。

    Args:
        items: 列表数据
        page: 页码（从1开始）
        page_size: 每页大小

    Returns:
        (paginated_items, total)
    """
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = max(1, min(100, int(page_size)))
    except (TypeError, ValueError):
        page_size = 20

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total


def safe_int(value, default=None):
    """安全地将值转换为整数，失败时返回默认值。"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clean_display_text(value: Any) -> str:
    """将可能的空值、NaN 或 HTML 文本转为安全显示文本。"""
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return str(value).strip()

    text = strip_tags(str(value)).strip()
    if text.lower() in {"", "nan", "none", "null", "n/a", "na"}:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def answer_tokens(answer: Any, question_type: Optional[str] = None) -> set[str]:
    """提取答案匹配时使用的 token 集合。"""
    payload = extract_answer_value(answer)
    tokens: set[str] = set()

    if isinstance(payload, (list, tuple, set)):
        values = payload
    elif payload is None:
        values = []
    else:
        values = [payload]

    for value in values:
        cleaned = clean_display_text(value)
        if not cleaned:
            continue
        tokens.add(cleaned)
        tokens.add(cleaned.lower())
        tokens.add(cleaned.upper())
        if question_type == "true_false":
            lower = cleaned.lower()
            if lower in {"正确", "true", "1", "yes", "对", "是", "t", "√"}:
                tokens.update({"true", "TRUE", "正确"})
            if lower in {"错误", "false", "0", "no", "错", "否", "f", "×"}:
                tokens.update({"false", "FALSE", "错误"})
    return tokens


def normalize_question_options(
    raw_options: Any, question_type: Optional[str] = None
) -> List[Dict[str, str]]:
    """将题目选项归一化为统一的 value/label/content/letter 结构。"""
    normalized: List[Dict[str, str]] = []

    if not raw_options and question_type == "true_false":
        raw_options = [
            {"value": "true", "label": "正确"},
            {"value": "false", "label": "错误"},
        ]

    for index, option in enumerate(raw_options or []):
        letter = chr(ord("A") + index)

        if isinstance(option, dict):
            raw_value = (
                option.get("value")
                or option.get("key")
                or option.get("option_id")
                or option.get("letter")
                or option.get("label")
                or option.get("content")
                or option.get("text")
                or option.get("id")
            )
            raw_label = (
                option.get("content")
                or option.get("text")
                or option.get("label")
                or raw_value
            )
            value = clean_display_text(raw_value) or f"opt_{index + 1}"
            label = clean_display_text(raw_label) or f"选项{letter}"
            letter = (
                clean_display_text(option.get("letter") or option.get("key")) or letter
            )
        elif isinstance(option, str):
            cleaned = clean_display_text(option)
            value = cleaned or f"opt_{index + 1}"
            label = cleaned or f"选项{letter}"
        else:
            continue

        normalized.append(
            {
                "value": str(value),
                "label": label,
                "content": label,
                "letter": letter,
            }
        )

    return normalized


def option_tokens(option: Dict[str, Any]) -> set[str]:
    """提取选项匹配 token。"""
    tokens: set[str] = set()
    for value in (
        option.get("value"),
        option.get("letter"),
        option.get("label"),
        option.get("content"),
    ):
        cleaned = clean_display_text(value)
        if cleaned:
            tokens.update({cleaned, cleaned.lower(), cleaned.upper()})
    return tokens


def decorate_question_options(
    raw_options: Any,
    question_type: Optional[str] = None,
    student_answer: Any = None,
    correct_answer: Any = None,
) -> List[Dict[str, Any]]:
    """为选项补充学生选择和正确答案标记。"""
    normalized = normalize_question_options(raw_options, question_type)
    student_token_set = answer_tokens(student_answer, question_type)
    correct_token_set = answer_tokens(correct_answer, question_type)

    return [
        {
            **option,
            "is_student_selected": bool(option_tokens(option) & student_token_set),
            "is_correct_option": bool(option_tokens(option) & correct_token_set),
        }
        for option in normalized
    ]


def format_option_display(option: Dict[str, Any]) -> str:
    """格式化单个选项展示文本。"""
    prefix = clean_display_text(option.get("letter") or option.get("value"))
    content = clean_display_text(
        option.get("content") or option.get("label") or option.get("value")
    )
    return f"{prefix}. {content}" if prefix and content else content or prefix


def build_answer_display(
    answer: Any,
    question_type: Optional[str] = None,
    options: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """构建题目答案展示文本。"""
    token_set = answer_tokens(answer, question_type)
    if options:
        matched = [
            format_option_display(option)
            for option in options
            if option_tokens(option) & token_set
        ]
        if matched:
            return "；".join(matched)

    payload = extract_answer_value(answer)
    if isinstance(payload, (list, tuple, set)):
        values = [
            clean_display_text(item) for item in payload if clean_display_text(item)
        ]
        return "；".join(values) if values else "未作答"
    if isinstance(payload, bool):
        return "正确" if payload else "错误"

    bool_value = _normalize_boolean_answer(payload)
    if question_type == "true_false" and bool_value is not None:
        return "正确" if bool_value else "错误"

    cleaned = clean_display_text(payload)
    return cleaned or "未作答"


def serialize_answer_payload(
    question_type: Optional[str], answer: Any
) -> Dict[str, Any]:
    """将答案序列化为统一 JSON 结构，便于持久化。"""
    payload = extract_answer_value(answer)
    if question_type == "multiple_choice":
        if payload is None or payload == "":
            return {"answers": []}
        if isinstance(payload, (list, tuple, set)):
            return {"answers": list(payload)}
        return {"answers": [payload]}

    if question_type == "true_false":
        bool_value = _normalize_boolean_answer(payload)
        return {"answer": bool_value if bool_value is not None else payload}

    return {"answer": payload}


__all__ = [
    "custom_exception_handler",
    "get_error_message",
    "calculate_mastery",
    "extract_answer_value",
    "check_answer",
    "build_normalized_score_map",
    "score_questions",
    "grade_exam",
    "validate_course_exists",
    "resolve_course_id",
    "paginate_list",
    "safe_int",
    "clean_display_text",
    "answer_tokens",
    "normalize_question_options",
    "option_tokens",
    "decorate_question_options",
    "format_option_display",
    "build_answer_display",
    "serialize_answer_payload",
]
