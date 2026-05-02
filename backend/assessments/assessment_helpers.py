"""
测评视图共享工具。

集中存放跨知识测评、能力评测和习惯问卷复用的轻量转换逻辑，避免视图入口重复实现。
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from rest_framework.request import Request

from common.utils import (
    answer_tokens,
    build_answer_display,
    clean_display_text,
    normalize_question_options,
    option_tokens,
)
from knowledge.models import KnowledgeMastery
from users.models import User

from .models import Assessment, AssessmentResult, Question


HABIT_SURVEY_FIXED_ID = 5001
ABILITY_ASSESSMENT_FIXED_ID = 5002


def get_authenticated_user(request: Request) -> User:
    """
    将请求中的用户对象收窄为项目内 User 类型。
    :param request: DRF 请求对象。
    :return: 已认证用户。
    """
    return cast(User, request.user)


def calculate_initial_mastery_baseline(correct_count: int, total_count: int) -> float:
    """
    初始评测掌握度基线。

    使用保守的样本量平滑，避免少量题目或随机作答导致掌握度虚高。
    """
    prior_mean = 0.25
    prior_strength = 4.0
    if total_count <= 0:
        return round(prior_mean, 4)
    mastery = (correct_count + prior_mean * prior_strength) / (total_count + prior_strength)
    return round(max(0.0, min(0.85, mastery)), 4)


def extract_answer_payload(answer: object) -> object:
    """提取题目答案载荷中的统一答案值。"""
    if isinstance(answer, Mapping):
        if 'answers' in answer:
            return answer.get('answers')
        return answer.get('answer', answer)
    return answer


def answer_tokens_for(answer: object, question_type: str) -> set[str]:
    """将作答内容规整为可比较的 token 集合。"""
    return answer_tokens(answer, question_type)


def option_tokens_for(option: object) -> set[str]:
    """将选项对象规整为 token 集合。"""
    return option_tokens(option)


def format_option_display(option: Mapping[str, object]) -> str:
    """生成选项展示文本。"""
    prefix = option.get('letter') or option.get('value') or ''
    content = option.get('label') or option.get('content') or option.get('value') or ''
    return f"{prefix}. {content}" if prefix else str(content)


def build_answer_display_value(
    answer: object,
    question_type: str,
    options: list[dict[str, object]],
) -> str:
    """构建学生答案或正确答案的展示文本。"""
    return build_answer_display(answer, question_type, options)


def clean_text(value: object) -> str:
    """清洗文本，避免 nan、空白和脏字符直接进入响应。"""
    return clean_display_text(value)


def get_question_title(question: Question) -> str:
    """为题干提供稳健的显示文本，避免出现 'nan'。"""
    content = clean_text(getattr(question, 'content', ''))
    if not content:
        content = clean_text(getattr(question, 'title', ''))
    if not content and getattr(question, 'analysis', None):
        content = clean_text(str(question.analysis).splitlines()[0])
    if not content:
        content = f"题干缺失（题目ID {question.id}），请联系教师补充"
    return content


def normalize_options(raw_options: object, question_type: str) -> list[dict[str, object]]:
    """统一规整题目选项结构。"""
    return normalize_question_options(raw_options, question_type)


def persist_mastery_snapshot(
    user: User,
    course_id: int | str,
    mastery_map: dict[int, float],
    point_stats: dict[int, dict[str, object]],
) -> list[dict[str, object]]:
    """
    回写知识点掌握度并生成接口响应所需的掌握度列表。
    :param user: 当前学生用户。
    :param course_id: 课程 ID。
    :param mastery_map: 知识点掌握度映射。
    :param point_stats: 知识点统计信息。
    :return: 掌握度列表。
    """
    normalized_course_id = int(course_id)
    mastery_list: list[dict[str, object]] = []
    for point_id, mastery_rate in mastery_map.items():
        point_name = str(point_stats.get(point_id, {}).get('name', f'知识点{point_id}'))
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course_id=normalized_course_id,
            knowledge_point_id=point_id,
            defaults={'mastery_rate': mastery_rate},
        )
        mastery_list.append({
            'point_id': point_id,
            'point_name': point_name,
            'mastery_rate': mastery_rate,
        })
    return mastery_list


def upsert_knowledge_assessment_result(
    user: User,
    assessment: Assessment,
    course_id: int | str,
    answer_dict: dict[str, object],
    total_score: float,
    mastery_list: list[dict[str, object]],
    question_details: list[dict[str, object]],
    questions: list[Question],
    correct_count: int,
    total_question_count: int,
) -> None:
    """
    统一写入知识测评结果，避免重复组装结果载荷。
    :param user: 当前学生用户。
    :param assessment: 知识测评对象。
    :param course_id: 课程 ID。
    :param answer_dict: 作答映射。
    :param total_score: 学生得分。
    :param mastery_list: 掌握度列表。
    :param question_details: 题目明细。
    :param questions: 题目列表。
    :param correct_count: 答对题数。
    :param total_question_count: 题目总数。
    :return: None。
    """
    AssessmentResult.objects.update_or_create(
        user=user,
        assessment=assessment,
        defaults={
            'course_id': course_id,
            'answers': answer_dict,
            'score': total_score,
            'result_data': {
                'mastery': mastery_list,
                'question_details': question_details,
                'total_score': sum(float(question.score or 0) for question in questions),
                'correct_count': correct_count,
                'total_count': total_question_count,
            },
        },
    )
