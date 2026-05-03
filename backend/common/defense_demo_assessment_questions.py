from __future__ import annotations

from decimal import Decimal
from typing import cast

from assessments.models import Question
from courses.models import Course
from knowledge.models import KnowledgePoint
from users.models import User

from common.defense_demo_progress import (
    _question_knowledge_points,
    _question_options,
    _set_related_knowledge_points,
)
from common.utils import build_answer_display, decorate_question_options, extract_answer_value

# 维护意图：优先使用课程资源导入的初始评测题，缺失时才创建固定兜底题目。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _ensure_demo_assessment_questions(
    course: Course, teacher: User, points: list[KnowledgePoint],
) -> list[Question]:
    """
    优先使用课程资源导入的初始评测题，缺失时才创建固定兜底题目。
    :param course: 所属课程。
    :param teacher: 教师（创建者）。
    :param points: 知识点列表。
    :return: 题目列表（按出题顺序）。
    """

    imported_questions = list(
        Question.objects.filter(course=course, for_initial_assessment=True)
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    if imported_questions:
        Course.objects.filter(pk=course.pk).update(
            initial_assessment_count=len(imported_questions),
        )
        course.initial_assessment_count = len(imported_questions)
        return imported_questions

    # 题目规格：知识点 → 2 道题，总分 100（16.67*4 + 16.66*2）
    specs = [
        # ---- 大数据概念与特征（points[0]）----
        {
            "content": '下列哪项是大数据"4V"特征中用于描述数据产生速度的维度？',
            "question_type": "single_choice",
            "answer": {"answer": "B"},
            "analysis": "Velocity 指数据产生和流动的速度，是大数据区别于传统数据集的关键维度之一。",
            "knowledge_point": points[0],
            "options": [
                {"label": "A", "content": "Volume"},
                {"label": "B", "content": "Velocity"},
                {"label": "C", "content": "Variety"},
                {"label": "D", "content": "Value"},
            ],
            "score": Decimal("16.67"),
        },
        {
            "content": "大数据处理与传统数据处理的关键区别在于？",
            "question_type": "single_choice",
            "answer": {"answer": "C"},
            "analysis": "大数据处理需要分布式架构才能在可接受的时间内完成海量异构数据的存储与计算。",
            "knowledge_point": points[0],
            "options": [
                {"label": "A", "content": "数据量大但处理逻辑完全相同"},
                {"label": "B", "content": "必须使用云计算平台"},
                {"label": "C", "content": "需要分布式架构支持海量异构数据的存储与计算"},
                {"label": "D", "content": "只能处理结构化数据"},
            ],
            "score": Decimal("16.67"),
        },
        # ---- Hadoop 生态组成（points[1]）----
        {
            "content": "在 Hadoop 生态系统中，负责分布式文件存储的核心组件是？",
            "question_type": "single_choice",
            "answer": {"answer": "C"},
            "analysis": "HDFS（Hadoop Distributed File System）是 Hadoop 的分布式文件存储层，提供高吞吐量的数据访问。",
            "knowledge_point": points[1],
            "options": [
                {"label": "A", "content": "MapReduce"},
                {"label": "B", "content": "YARN"},
                {"label": "C", "content": "HDFS"},
                {"label": "D", "content": "Hive"},
            ],
            "score": Decimal("16.67"),
        },
        {
            "content": "YARN 在 Hadoop 中的主要职责是什么？",
            "question_type": "single_choice",
            "answer": {"answer": "C"},
            "analysis": "YARN 统一管理集群资源并调度各类计算框架的任务，是 Hadoop 2.x 后的核心组件。",
            "knowledge_point": points[1],
            "options": [
                {"label": "A", "content": "数据存储"},
                {"label": "B", "content": "数据清洗"},
                {"label": "C", "content": "资源调度与集群管理"},
                {"label": "D", "content": "数据可视化"},
            ],
            "score": Decimal("16.67"),
        },
        # ---- Spark 核心计算模型（points[2]）----
        {
            "content": "Spark 相比 MapReduce 的核心优势主要体现在？",
            "question_type": "single_choice",
            "answer": {"answer": "A"},
            "analysis": "Spark 利用内存计算模型，大幅减少了中间结果的磁盘 IO，尤其适合迭代和交互式计算。",
            "knowledge_point": points[2],
            "options": [
                {"label": "A", "content": "基于内存的计算模型减少磁盘 IO"},
                {"label": "B", "content": "使用更少的集群节点"},
                {"label": "C", "content": "不需要集群环境即可运行"},
                {"label": "D", "content": "只能处理批量数据"},
            ],
            "score": Decimal("16.66"),
        },
        {
            "content": "以下关于 RDD（弹性分布式数据集）的描述，哪些是正确的？",
            "question_type": "multiple_choice",
            "answer": {"answers": ["A", "C"]},
            "analysis": "RDD 是只读的分区数据集合，支持惰性求值（lazy evaluation），在行动算子触发时才真正执行计算。",
            "knowledge_point": points[2],
            "options": [
                {"label": "A", "content": "RDD 是只读的分区数据集合"},
                {"label": "B", "content": "RDD 不支持容错机制"},
                {"label": "C", "content": "RDD 支持惰性求值"},
                {"label": "D", "content": "RDD 只能存储文本数据"},
            ],
            "score": Decimal("16.66"),
        },
    ]

    ordered: list[Question] = []
    for spec in specs:
        # 以课程+题目内容为唯一键，确保幂等
        question, _ = Question.objects.update_or_create(
            course=course,
            content=spec["content"],
            defaults={
                "chapter": "初始评测",
                "question_type": spec["question_type"],
                "options": spec["options"],
                "answer": spec["answer"],
                "analysis": spec["analysis"],
                "difficulty": "medium",
                "score": spec["score"],
                "is_visible": False,
                "for_initial_assessment": True,
                "created_by": teacher,
            },
        )
        _set_related_knowledge_points(question, cast(KnowledgePoint, spec["knowledge_point"]))
        ordered.append(question)
    return ordered


# 维护意图：根据题目结构生成可提交的演示答案。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_planned_answer_value(question: Question, force_correct: bool) -> object:
    """
    根据题目结构生成可提交的演示答案。
    :param question: 初始评测题目。
    :param force_correct: 是否生成正确答案。
    :return: 与真实提交接口一致的原始答案值。
    """
    correct_raw = extract_answer_value(question.answer)
    if force_correct:
        return correct_raw

    options = _question_options(question)
    if question.question_type == "multiple_choice":
        correct_values = (
            [str(value) for value in correct_raw]
            if isinstance(correct_raw, list)
            else [str(correct_raw)]
        )
        fallback = next(
            (
                str(option.get("label"))
                for option in options
                if str(option.get("label")) not in correct_values
            ),
            "A",
        )
        return [correct_values[0], fallback] if correct_values else [fallback]

    if question.question_type == "true_false":
        normalized = str(correct_raw).strip().lower()
        return "false" if normalized in {"true", "a", "正确", "对"} else "true"

    return next(
        (
            str(option.get("label"))
            for option in options
            if str(option.get("label")) != str(correct_raw)
        ),
        "B" if str(correct_raw).upper() != "B" else "A",
    )


# 维护意图：构建初始评测答题明细（含故意错题），匹配真实提交流程的数据结构。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_assessment_report_payload(
    questions: list[Question],
    planned_raw: list[object],
) -> tuple[dict[str, object], list[dict[str, object]], list[bool]]:
    """
    构建初始评测答题明细（含故意错题），匹配真实提交流程的数据结构。
    :param questions: 评测题目（优先来自课程资源，顺序固定）。
    :return: (原始答案字典, 题目详情列表, 各题正误列表)。
    """

    if len(planned_raw) != len(questions):
        planned_raw = [
            _build_planned_answer_value(question, force_correct=index % 5 != 1)
            for index, question in enumerate(questions)
        ]

    raw_answers: dict[str, object] = {}
    question_details: list[dict[str, object]] = []
    is_correct_flags: list[bool] = []

    for question, student_raw in zip(questions, planned_raw, strict=True):
        q_id = str(question.id)
        raw_answers[q_id] = student_raw

        correct_raw = extract_answer_value(question.answer)

        # 判定正误（匹配 submit_knowledge_assessment 逻辑）
        if question.question_type == "multiple_choice":
            correct_set = {
                str(x).strip().upper()
                for x in (correct_raw if isinstance(correct_raw, list) else [correct_raw])
            }
            student_set = {
                str(x).strip().upper()
                for x in (student_raw if isinstance(student_raw, list) else [student_raw])
            }
            is_correct = correct_set == student_set
        else:
            is_correct = str(student_raw).strip().upper() == str(correct_raw).strip().upper()

        is_correct_flags.append(is_correct)

        # 选项装饰
        decorated_options = decorate_question_options(
            question.options,
            question.question_type,
            student_answer=student_raw,
            correct_answer=correct_raw,
        )
        question_details.append({
            "question_id": question.id,
            "content": question.content,
            "question_type": question.question_type,
            "student_answer": student_raw,
            "correct_answer": correct_raw,
            "student_answer_display": build_answer_display(student_raw, question.question_type, decorated_options),
            "correct_answer_display": build_answer_display(correct_raw, question.question_type, decorated_options),
            "is_correct": is_correct,
            "analysis": question.analysis or "",
            "options": decorated_options,
            "knowledge_points": [
                {"id": point.id, "name": point.name}
                for point in _question_knowledge_points(question)
            ],
        })

    return raw_answers, question_details, is_correct_flags
