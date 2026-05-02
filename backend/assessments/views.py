"""
测评模块视图兼容入口。

公开 URL 仍通过 assessments.views 绑定；具体实现按职责拆分到相邻模块。
"""
from .ability_views import (
    get_ability_assessment,
    retake_ability_assessment,
    submit_ability_assessment,
)
from .assessment_helpers import (
    ABILITY_ASSESSMENT_FIXED_ID,
    HABIT_SURVEY_FIXED_ID,
    answer_tokens_for as _answer_tokens,
    build_answer_display_value as _build_answer_display,
    calculate_initial_mastery_baseline as _calculate_initial_mastery_baseline,
    clean_text as _clean_text,
    extract_answer_payload as _extract_answer_payload,
    format_option_display as _format_option_display,
    get_authenticated_user as _get_authenticated_user,
    get_question_title as _get_question_title,
    normalize_options as _normalize_options,
    option_tokens_for as _option_tokens,
    persist_mastery_snapshot as _persist_mastery_snapshot,
    upsert_knowledge_assessment_result as _upsert_knowledge_assessment_result,
)
from .habit_views import get_habit_survey, submit_habit_survey
from .knowledge_generation import async_generate_after_assessment as _async_generate_after_assessment
from .knowledge_views import (
    get_knowledge_assessment,
    get_knowledge_result,
    submit_knowledge_assessment,
)
from .status_profile_views import generate_course_profile, get_assessment_status


__all__ = [
    'ABILITY_ASSESSMENT_FIXED_ID',
    'HABIT_SURVEY_FIXED_ID',
    '_answer_tokens',
    '_async_generate_after_assessment',
    '_build_answer_display',
    '_calculate_initial_mastery_baseline',
    '_clean_text',
    '_extract_answer_payload',
    '_format_option_display',
    '_get_authenticated_user',
    '_get_question_title',
    '_normalize_options',
    '_option_tokens',
    '_persist_mastery_snapshot',
    '_upsert_knowledge_assessment_result',
    'generate_course_profile',
    'get_ability_assessment',
    'get_assessment_status',
    'get_habit_survey',
    'get_knowledge_assessment',
    'get_knowledge_result',
    'retake_ability_assessment',
    'submit_ability_assessment',
    'submit_habit_survey',
    'submit_knowledge_assessment',
]
