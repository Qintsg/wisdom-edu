"""学生端考试列表与详情视图的查询和序列化辅助逻辑。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from django.db.models import Q, QuerySet
from django.utils import timezone

from common.utils import safe_int
from courses.models import Enrollment
from users.models import User

from .models import Exam, ExamQuestion, ExamSubmission
from .student_helpers import build_exam_score_map, resolve_pass_threshold


# 维护意图：学生端考试列表筛选与分页参数
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class ExamListParams:
    """学生端考试列表筛选与分页参数。"""

    course_id: str | None
    exam_type: str | None
    page: int
    size: int

    # 维护意图：返回当前页起始偏移量
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def offset(self) -> int:
        """返回当前页起始偏移量。"""
        return (self.page - 1) * self.size

    # 维护意图：返回当前页结束偏移量
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def limit(self) -> int:
        """返回当前页结束偏移量。"""
        return self.page * self.size


# 维护意图：从查询字符串中解析考试列表筛选条件
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_exam_list_params(query_params: Mapping[str, object]) -> ExamListParams:
    """从查询字符串中解析考试列表筛选条件。"""
    return ExamListParams(
        course_id=normalize_query_value(query_params.get("course_id")),
        exam_type=normalize_query_value(query_params.get("type")),
        page=max(1, safe_int(query_params.get("page"), 1)),
        size=min(max(1, safe_int(query_params.get("size"), 20)), 100),
    )


# 维护意图：将空查询参数规范化为 None，避免生成无意义过滤条件
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_query_value(value: object | None) -> str | None:
    """将空查询参数规范化为 None，避免生成无意义过滤条件。"""
    if value is None or value == "":
        return None
    return str(value)


# 维护意图：构建学生端考试列表接口响应数据
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_exam_list_payload(query_params: Mapping[str, object], user: User) -> dict[str, object]:
    """构建学生端考试列表接口响应数据。"""
    params = parse_exam_list_params(query_params)
    exams = build_visible_exam_queryset(user, params)
    total = exams.count()
    page_exams = list(exams[params.offset:params.limit])
    submissions = build_submission_map(user, page_exams)
    return {
        "total": total,
        "exams": [
            serialize_exam_summary(exam, submissions.get(int(exam.id)))
            for exam in page_exams
        ],
    }


# 维护意图：按角色返回当前用户可见的已发布考试查询集
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_visible_exam_queryset(user: User, params: ExamListParams) -> QuerySet[Exam]:
    """按角色返回当前用户可见的已发布考试查询集。"""
    exams = Exam.objects.filter(status="published").select_related("course", "target_class", "created_by")
    exams = apply_exam_filters(exams, params)
    if user.role == "student":
        return apply_student_exam_visibility(exams, user, params)
    if user.role == "teacher":
        return exams.filter(created_by=user)
    return exams


# 维护意图：应用课程与考试类型过滤条件
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_exam_filters(exams: QuerySet[Exam], params: ExamListParams) -> QuerySet[Exam]:
    """应用课程与考试类型过滤条件。"""
    if params.course_id:
        exams = exams.filter(course_id=params.course_id)
    if params.exam_type:
        exams = exams.filter(exam_type=params.exam_type)
    return exams


# 维护意图：限定学生只能看到已开始且面向其班级或课程的考试
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_student_exam_visibility(
    exams: QuerySet[Exam],
    user: User,
    params: ExamListParams,
) -> QuerySet[Exam]:
    """限定学生只能看到已开始且面向其班级或课程的考试。"""
    now = timezone.now()
    class_ids, course_ids = load_student_exam_scope(user)
    visible_exams = exams.filter(Q(start_time__lte=now) | Q(start_time__isnull=True))
    if not params.course_id:
        visible_exams = visible_exams.filter(course_id__in=course_ids)
    return visible_exams.filter(Q(target_class_id__in=class_ids) | Q(target_class__isnull=True))


# 维护意图：读取学生所在班级与这些班级发布过的课程范围
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_student_exam_scope(user: User) -> tuple[set[int], set[int]]:
    """读取学生所在班级与这些班级发布过的课程范围。"""
    enrollment_rows = Enrollment.objects.filter(user=user).values(
        "class_obj_id",
        "class_obj__class_courses__course_id",
    )
    class_ids = {
        int(row["class_obj_id"])
        for row in enrollment_rows
        if row["class_obj_id"]
    }
    course_ids = {
        int(row["class_obj__class_courses__course_id"])
        for row in enrollment_rows
        if row["class_obj__class_courses__course_id"]
    }
    return class_ids, course_ids


# 维护意图：批量读取当前页考试的提交记录，避免列表序列化时循环查库
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_submission_map(user: User, exams: Sequence[Exam]) -> dict[int, ExamSubmission]:
    """批量读取当前页考试的提交记录，避免列表序列化时循环查库。"""
    exam_ids = [int(exam.id) for exam in exams]
    if not exam_ids:
        return {}
    return {
        submission.exam_id: submission
        for submission in ExamSubmission.objects.filter(user=user, exam_id__in=exam_ids)
    }


# 维护意图：序列化列表中的单个考试条目
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def serialize_exam_summary(exam: Exam, submission: ExamSubmission | None) -> dict[str, object]:
    """序列化列表中的单个考试条目。"""
    submission_score = resolve_submission_score(submission)
    is_submitted = submission_score is not None and submission_score >= 0
    passed = submission_score >= resolve_pass_threshold(exam) if is_submitted else None
    return {
        "exam_id": exam.id,
        "title": exam.title,
        "type": exam.exam_type,
        "status": exam.status,
        "total_score": float(exam.total_score),
        "duration": exam.duration,
        "start_time": exam.start_time.isoformat() if exam.start_time else None,
        "end_time": exam.end_time.isoformat() if exam.end_time else None,
        "created_at": exam.created_at.isoformat() if exam.created_at else None,
        "submitted": is_submitted,
        "score": submission_score if is_submitted else None,
        "passed": passed,
        "submitted_at": submission.submitted_at.isoformat() if submission and submission.submitted_at else None,
    }


# 维护意图：将未提交、草稿和有效成绩区分开
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_submission_score(submission: ExamSubmission | None) -> float | None:
    """将未提交、草稿和有效成绩区分开。"""
    if not submission or submission.score is None:
        return None
    return float(submission.score)


# 维护意图：读取已发布考试；不存在时返回 None 供视图转换为统一错误响应
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_published_exam(exam_id: int) -> Exam | None:
    """读取已发布考试；不存在时返回 None 供视图转换为统一错误响应。"""
    try:
        return Exam.objects.get(id=exam_id, status="published")
    except Exam.DoesNotExist:
        return None


# 维护意图：返回考试详情访问错误信息；允许访问时返回 None
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_exam_detail_access_error(exam: Exam, user: User) -> str | None:
    """返回考试详情访问错误信息；允许访问时返回 None。"""
    if user.role != "student":
        return None
    now = timezone.now()
    if exam.start_time and exam.start_time > now:
        return "作业尚未开始"
    if exam.end_time and exam.end_time < now:
        return "作业已结束"
    return None


# 维护意图：构建考试详情响应，题目不包含标准答案
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_exam_detail_payload(exam: Exam) -> dict[str, object]:
    """构建考试详情响应，题目不包含标准答案。"""
    exam_questions = list(
        ExamQuestion.objects.filter(exam=exam)
        .select_related("question")
        .order_by("order")
    )
    score_map = build_exam_score_map(exam, exam_questions)
    return {
        "exam_id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "total_score": float(exam.total_score),
        "pass_score": resolve_pass_threshold(exam),
        "duration": exam.duration,
        "questions": [
            serialize_exam_question(exam_question, score_map)
            for exam_question in exam_questions
        ],
    }


# 维护意图：序列化考试详情中的题目信息
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def serialize_exam_question(
    exam_question: ExamQuestion,
    score_map: dict[str, float],
) -> dict[str, object]:
    """序列化考试详情中的题目信息。"""
    question = exam_question.question
    return {
        "question_id": question.id,
        "content": question.content,
        "options": question.options,
        "type": question.question_type,
        "score": score_map.get(str(question.id), 0),
    }


__all__ = [
    "ExamListParams",
    "build_exam_detail_payload",
    "build_exam_list_payload",
    "build_submission_map",
    "build_visible_exam_queryset",
    "get_published_exam",
    "parse_exam_list_params",
    "resolve_exam_detail_access_error",
    "serialize_exam_question",
    "serialize_exam_summary",
]
