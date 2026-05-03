"""
考试总分与及格线策略。

统一所有考试/套题的总分计算口径：
- 考试总分 = 所有关联 ExamQuestion.score 之和
- 及格分 = 总分 * default_pass_ratio
"""
from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from common.config import AppConfig


# 维护意图：to decimal
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _to_decimal(value) -> Decimal:
    return Decimal(str(value or 0))


# 维护意图：汇总考试题目配置中的分值并返回总分
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def sum_exam_question_scores(exam_questions: Iterable) -> Decimal:
    """汇总考试题目配置中的分值并返回总分。"""

    total = Decimal('0')
    for exam_question in exam_questions:
        score = getattr(exam_question, 'score', None)
        if score is None and getattr(exam_question, 'question', None) is not None:
            score = getattr(exam_question.question, 'score', 0)
        total += _to_decimal(score)
    return total


# 维护意图：根据总分与及格比例计算标准化后的及格分
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def compute_exam_pass_score(total_score: Decimal, pass_ratio: float | None = None) -> Decimal:
    """根据总分与及格比例计算标准化后的及格分。"""

    ratio = Decimal(str(pass_ratio if pass_ratio is not None else AppConfig.exam_pass_ratio()))
    return (total_score * ratio).quantize(Decimal('0.01'))


# 维护意图：同步单场考试的总分与及格分，并按需持久化
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def sync_exam_totals(exam, save: bool = True, pass_ratio: float | None = None) -> tuple[float, float]:
    """同步单场考试的总分与及格分，并按需持久化。"""

    exam_questions = exam.examquestion_set.select_related('question').all()
    total_score = sum_exam_question_scores(exam_questions).quantize(Decimal('0.01'))
    if total_score <= 0:
        total_score = Decimal('0.00')
    pass_score = compute_exam_pass_score(total_score, pass_ratio=pass_ratio) if total_score > 0 else Decimal('0.00')

    exam.total_score = total_score
    exam.pass_score = pass_score
    if save:
        exam.save(update_fields=['total_score', 'pass_score'])
    return float(total_score), float(pass_score)


# 维护意图：批量同步指定课程下考试的总分与及格分
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def sync_course_exam_totals(course_id: int, exam_types: list[str] | None = None) -> int:
    """批量同步指定课程下考试的总分与及格分。"""

    from exams.models import Exam

    queryset = Exam.objects.filter(course_id=course_id).prefetch_related('examquestion_set__question')
    if exam_types:
        queryset = queryset.filter(exam_type__in=exam_types)

    count = 0
    for exam in queryset:
        sync_exam_totals(exam, save=True)
        count += 1
    return count
