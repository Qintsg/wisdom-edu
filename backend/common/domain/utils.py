"""公共领域工具聚合入口。"""

from __future__ import annotations

from common.domain.course_utils import resolve_course_id, validate_course_exists
from common.domain.grading import (
    build_normalized_score_map,
    calculate_mastery,
    check_answer,
    extract_answer_value,
    grade_exam,
    score_questions,
)
from common.domain.question_options import (
    answer_tokens,
    build_answer_display,
    clean_display_text,
    decorate_question_options,
    format_option_display,
    normalize_question_options,
    option_tokens,
    serialize_answer_payload,
)
from common.http.errors import custom_exception_handler, get_error_message
from common.http.pagination import paginate_list, parse_pagination, safe_int


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
    "parse_pagination",
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
