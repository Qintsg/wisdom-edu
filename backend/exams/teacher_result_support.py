"""教师端成绩详情和统计分析 helper。"""

from __future__ import annotations

from .models import ExamQuestion, ExamSubmission
from .teacher_helpers import _normalize_choice_answer_set


# 维护意图：构建成绩列表中的单条提交摘要
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_submission_result(submission: ExamSubmission) -> dict[str, object]:
    """构建成绩列表中的单条提交摘要。"""
    return {
        "submission_id": submission.id,
        "user_id": submission.user.id,
        "username": submission.user.username,
        "real_name": submission.user.real_name or "",
        "score": float(submission.score),
        "is_passed": submission.is_passed,
        "submitted_at": submission.submitted_at.isoformat(),
    }


# 维护意图：构建教师查看学生作业时的单题详情
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_teacher_question_detail(
    exam_question: ExamQuestion,
    answers: dict[str, object],
) -> dict[str, object]:
    """构建教师查看学生作业时的单题详情。"""
    question = exam_question.question
    student_answer = answers.get(str(question.id), "")
    correct_answer = extract_question_answer(question.answer)
    is_correct = is_teacher_answer_correct(
        question.question_type,
        student_answer,
        correct_answer,
    )
    return {
        "question_id": question.id,
        "content": question.content,
        "question_type": question.question_type,
        "options": question.options,
        "correct_answer": correct_answer,
        "student_answer": student_answer,
        "is_correct": is_correct,
        "score": exam_question.score if is_correct else 0,
    }


# 维护意图：兼容直接答案和 {'answer': value} 两种题库答案结构
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_question_answer(answer_payload: object) -> object:
    """兼容直接答案和 {'answer': value} 两种题库答案结构。"""
    if isinstance(answer_payload, dict):
        return answer_payload.get("answer", answer_payload)
    return answer_payload


# 维护意图：按教师端历史规则判断答案是否正确
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def is_teacher_answer_correct(
    question_type: str,
    student_answer: object,
    correct_answer: object,
) -> bool:
    """按教师端历史规则判断答案是否正确。"""
    if question_type in ["single_choice", "true_false"]:
        return student_answer == correct_answer
    if question_type == "multiple_choice":
        correct_set = _normalize_choice_answer_set(correct_answer)
        student_set = _normalize_choice_answer_set(student_answer)
        return correct_set == student_set
    return normalized_answer_text(student_answer) == normalized_answer_text(correct_answer)


# 维护意图：归一化非选择题答案文本
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalized_answer_text(answer: object) -> str:
    """归一化非选择题答案文本。"""
    return str(answer).strip().lower()


# 维护意图：按固定分段统计成绩分布
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_score_distribution(scores: list[object]) -> dict[str, int]:
    """按固定分段统计成绩分布。"""
    score_distribution = {
        "0-59": 0,
        "60-69": 0,
        "70-79": 0,
        "80-89": 0,
        "90-100": 0,
    }
    for score in scores:
        score_distribution[_score_bucket(float(score))] += 1
    return score_distribution


# 维护意图：定位成绩分段
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _score_bucket(score: float) -> str:
    """定位成绩分段。"""
    if score < 60:
        return "0-59"
    if score < 70:
        return "60-69"
    if score < 80:
        return "70-79"
    if score < 90:
        return "80-89"
    return "90-100"


# 维护意图：统计每道题的正确率
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_analysis(
    exam_questions,
    submissions: list[ExamSubmission],
) -> list[dict[str, object]]:
    """统计每道题的正确率。"""
    total_submissions = len(submissions)
    return [
        build_single_question_analysis(exam_question, submissions, total_submissions)
        for exam_question in exam_questions.order_by("order")
    ]


# 维护意图：构建单道题正确率分析
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_single_question_analysis(
    exam_question: ExamQuestion,
    submissions: list[ExamSubmission],
    total_submissions: int,
) -> dict[str, object]:
    """构建单道题正确率分析。"""
    question = exam_question.question
    correct_answer = extract_question_answer(question.answer)
    correct_count = sum(
        1
        for submission in submissions
        if is_teacher_analysis_answer_correct(
            question.question_type,
            (submission.answers or {}).get(str(question.id)),
            correct_answer,
        )
    )
    accuracy = correct_count / total_submissions if total_submissions > 0 else 0
    return {
        "question_id": question.id,
        "content": truncate_question_content(question.content),
        "accuracy": round(accuracy, 3),
        "correct_count": correct_count,
        "total_count": total_submissions,
    }


# 维护意图：按原统计逻辑判断正确率，非选择题空答不计正确
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def is_teacher_analysis_answer_correct(
    question_type: str,
    student_answer: object,
    correct_answer: object,
) -> bool:
    """按原统计逻辑判断正确率，非选择题空答不计正确。"""
    if question_type not in ["single_choice", "true_false", "multiple_choice"] and student_answer is None:
        return False
    return is_teacher_answer_correct(question_type, student_answer, correct_answer)


# 维护意图：教师统计页只展示题干摘要
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def truncate_question_content(content: str) -> str:
    """教师统计页只展示题干摘要。"""
    return content[:50] + "..." if len(content) > 50 else content
