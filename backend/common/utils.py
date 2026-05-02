"""公共工具兼容入口。

该模块保留历史导入路径，具体实现按职责拆分到相邻模块，避免单文件继续承担
异常处理、判题评分、分页和课程上下文解析等多类职责。
"""

from __future__ import annotations

from .course_utils import resolve_course_id, validate_course_exists
from .errors import custom_exception_handler, get_error_message
from .grading import (
    build_normalized_score_map,
    calculate_mastery,
    check_answer,
    extract_answer_value,
    grade_exam,
    score_questions,
)
from .pagination import paginate_list, parse_pagination, safe_int
from .question_options import (
    answer_tokens,
    build_answer_display,
    clean_display_text,
    decorate_question_options,
    format_option_display,
    normalize_question_options,
    option_tokens,
    serialize_answer_payload,
)


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
