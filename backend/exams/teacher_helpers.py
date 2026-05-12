"""
考试教师端共享工具。

集中放置教师考试视图共用的分页、权限、分值校验与题目关联构造逻辑，
避免各视图模块重复实现同一套边界判断。
"""

from collections.abc import Iterable, Mapping
from decimal import Decimal, InvalidOperation

from rest_framework.response import Response

from common.responses import error_response, forbidden_response
from courses.models import Class
from users.models import User
from assessments.models import Question

from .models import Exam, ExamQuestion


def _validate_exam_scores(total_score, pass_score) -> None:
    """校验总分与及格分关系。"""
    try:
        total_val = Decimal(str(total_score))
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError('总分格式错误')

    try:
        pass_val = Decimal(str(pass_score))
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError('及格分格式错误')

    if total_val <= 0:
        raise ValueError('总分必须大于0')
    if pass_val <= 0:
        raise ValueError('及格分必须大于0')
    if pass_val > total_val:
        raise ValueError('及格分不能大于总分')


def _parse_pagination(
    query_params: Mapping[str, object],
    *,
    size_key: str = 'page_size',
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    """安全解析分页参数。"""

    try:
        page = max(1, int(query_params.get('page', 1)))
        page_size = min(max(1, int(query_params.get(size_key, default_size))), max_size)
    except (ValueError, TypeError):
        return 1, default_size
    return page, page_size


def _normalize_choice_answer_set(answer_value: object) -> set[str]:
    """将多选答案规整成可比较的字符串集合。"""

    resolved_answer = (
        answer_value.get('answer', answer_value)
        if isinstance(answer_value, Mapping)
        else answer_value
    )
    if isinstance(resolved_answer, Iterable) and not isinstance(
        resolved_answer, (str, bytes, Mapping)
    ):
        return {
            str(item).strip().lower()
            for item in resolved_answer
            if str(item).strip()
        }
    normalized_text = str(resolved_answer).strip().lower()
    return {normalized_text} if normalized_text else set()


def _get_exam_or_404(exam_id: int) -> tuple[Exam | None, Response | None]:
    """按 ID 获取考试，不存在时返回标准错误响应。"""

    try:
        return Exam.objects.get(id=exam_id), None
    except Exam.DoesNotExist:
        return None, error_response(msg='作业不存在', code=404)


def _get_owned_exam_or_404(user: User, exam_id: int) -> tuple[Exam | None, Response | None]:
    """获取当前教师创建的考试，不存在时返回标准错误响应。"""

    try:
        return Exam.objects.get(id=exam_id, created_by=user), None
    except Exam.DoesNotExist:
        return None, error_response(msg='作业不存在', code=404)


def _get_teacher_course_ids(user: User) -> set[int]:
    """获取教师可管理的课程 ID 集合。"""

    return set(Class.objects.filter(teacher=user).values_list('course_id', flat=True))


def _ensure_teacher_exam_access(
    user: User,
    exam: Exam,
    *,
    deny_message: str,
    allow_creator_bypass: bool = True,
) -> Response | None:
    """校验教师是否可访问指定考试。"""

    if user.role != 'teacher':
        return None
    if allow_creator_bypass and exam.created_by_id == user.id:
        return None
    if exam.course_id in _get_teacher_course_ids(user):
        return None
    return forbidden_response(msg=deny_message)


def _build_exam_question_rows(
    exam: Exam,
    questions: Iterable[Question],
    *,
    start_order: int = 0,
) -> list[ExamQuestion]:
    """按顺序构造考试题目关联记录。"""

    return [
        ExamQuestion(exam=exam, question=question, score=question.score, order=start_order + index)
        for index, question in enumerate(questions)
    ]


__all__ = [
    '_build_exam_question_rows',
    '_ensure_teacher_exam_access',
    '_get_exam_or_404',
    '_get_owned_exam_or_404',
    '_get_teacher_course_ids',
    '_normalize_choice_answer_set',
    '_parse_pagination',
    '_validate_exam_scores',
]
