from __future__ import annotations

from decimal import Decimal
from typing import cast

from assessments.models import Question
from courses.models import Course
from exams.models import Exam, ExamQuestion
from knowledge.models import KnowledgePoint, KnowledgeRelation, Resource
from users.models import User

from common.defense_demo_progress import _set_related_knowledge_points

def _ensure_demo_points(course: Course) -> list[KnowledgePoint]:
    """
    创建演示专用知识点。
    :param course: 主课程。
    :return: 依顺序排列的知识点列表。
    """
    point_specs = [
        {
            "name": "大数据概念与特征",
            "chapter": "第1章 大数据技术基础",
            "description": "理解大数据的 4V 特征、典型应用与教学场景中的数据驱动价值。",
            "teaching_goal": "能概括大数据的核心特征，并说明其在真实业务中的意义。",
            "order": 9001,
        },
        {
            "name": "Hadoop 生态组成",
            "chapter": "第2章 Hadoop",
            "description": "区分 HDFS、MapReduce、YARN 在大数据平台中的职责。",
            "teaching_goal": "能解释 Hadoop 生态各组件之间的分工关系。",
            "order": 9002,
        },
        {
            "name": "Spark 核心计算模型",
            "chapter": "第3章 Spark",
            "description": "理解 Spark 的内存计算优势、RDD 抽象与批处理/迭代计算特点。",
            "teaching_goal": "能比较 Spark 与传统 MapReduce 在处理模式上的差异。",
            "order": 9003,
        },
    ]

    points: list[KnowledgePoint] = []
    for spec in point_specs:
        point, _ = KnowledgePoint.objects.update_or_create(
            course=course,
            name=spec["name"],
            defaults={
                "chapter": spec["chapter"],
                "description": spec["description"],
                "teaching_goal": spec["teaching_goal"],
                "order": spec["order"],
                "is_published": True,
            },
        )
        points.append(point)

    for index in range(len(points) - 1):
        KnowledgeRelation.objects.get_or_create(
            course=course,
            pre_point=points[index],
            post_point=points[index + 1],
            defaults={"relation_type": "prerequisite"},
        )
    return points


def _ensure_demo_resources(course: Course, teacher: User, points: list[KnowledgePoint]) -> dict[str, list[dict[str, object]]]:
    """
    创建学习节点固定展示用资源。
    :param course: 主演示课程。
    :param teacher: 教师对象。
    :param points: 知识点列表。
    :return: 按知识点名称组织的资源展示载荷。
    """
    resource_specs: dict[str, list[dict[str, object]]] = {
        points[0].name: [
            {
                "title": "大数据概念与特征导读",
                "resource_type": "document",
                "description": "帮助学生快速建立对 4V 特征和应用场景的整体认识。",
                "url": "/media/resources/bigdata-concepts-guide.pdf",
                "duration": 600,
            },
            {
                "title": "大数据典型应用案例",
                "resource_type": "video",
                "description": "通过案例说明大数据在真实场景中的业务价值。",
                "url": "/media/resources/bigdata-case-study.mp4",
                "duration": 420,
            },
        ],
        points[1].name: [
            {
                "title": "Hadoop 生态架构详解",
                "resource_type": "document",
                "description": "展示 HDFS、YARN 与 MapReduce 的协作关系及各组件职责。",
                "url": "/media/resources/hadoop-ecosystem-overview.pdf",
                "duration": 480,
            },
            {
                "title": "Hadoop 核心组件解析",
                "resource_type": "video",
                "description": "分模块说明 Hadoop 生态各核心组件职责。",
                "url": "/media/resources/hadoop-components-explained.mp4",
                "duration": 540,
            },
        ],
        points[2].name: [
            {
                "title": "Spark 内存计算原理",
                "resource_type": "document",
                "description": "从执行模型角度解释 Spark 的性能优势与 RDD 抽象。",
                "url": "/media/resources/spark-memory-computing.pdf",
                "duration": 360,
            },
            {
                "title": "Spark 与 MapReduce 对比分析",
                "resource_type": "link",
                "description": "对照展示两种计算框架在迭代任务中的性能差异。",
                "url": "/media/resources/spark-vs-mapreduce.pdf",
                "duration": 300,
            },
        ],
    }

    payload_map: dict[str, list[dict[str, object]]] = {}
    for point_idx, point in enumerate(points, start=1):
        payload_map[point.name] = []
        for index, spec in enumerate(resource_specs[point.name], start=1):
            resource, _ = Resource.objects.update_or_create(
                course=course,
                title=spec["title"],
                defaults={
                    "resource_type": spec["resource_type"],
                    "description": spec["description"],
                    "url": spec["url"],
                    "duration": spec["duration"],
                    "chapter_number": f"{point_idx}.{index}",
                    "sort_order": 9500 + index,
                    "is_visible": True,
                    "uploaded_by": teacher,
                },
            )
            _set_related_knowledge_points(resource, point)
            payload_map[point.name].append(
                {
                    "resource_id": resource.id,
                    "title": resource.title,
                    "type": resource.resource_type,
                    "description": resource.description or "",
                    "duration": resource.duration or 0,
                    "url": resource.url or "",
                    "required": True,
                    "is_internal": True,
                    "recommended_reason": f"该资源与“{point.name}”直接对应，有助于建立核心概念认知。",
                    "learning_tips": "建议先快速浏览核心概念，再带着整理笔记的方式回读重点段落。",
                    "completed": False,
                }
            )
    return payload_map


def _ensure_demo_stage_test(course: Course, teacher: User, points: list[KnowledgePoint]) -> Exam:
    """
    创建阶段测试题与试卷。
    :param course: 主课程。
    :param teacher: 教师对象。
    :param points: 知识点列表。
    :return: 阶段测试试卷对象。
    """
    question_specs = [
        {
            "content": "下列哪一项最能体现大数据区别于传统数据处理的核心特征？",
            "question_type": "single_choice",
            "answer": {"answer": "A"},
            "analysis": "4V 特征体现了大数据在规模、速度和多样性上的典型差异。",
            "knowledge_point": points[0],
            "options": [
                {"label": "A", "content": "数据规模大、类型多、处理速度要求高"},
                {"label": "B", "content": "只关注结构化数据的统计分析"},
                {"label": "C", "content": "仅在单机环境下进行离线处理"},
                {"label": "D", "content": "主要依赖人工整理和人工判断"},
            ],
        },
        {
            "content": "在 Hadoop 生态中，负责资源调度和集群管理的组件是哪个？",
            "question_type": "single_choice",
            "answer": {"answer": "B"},
            "analysis": "YARN 负责统一的资源管理与任务调度。",
            "knowledge_point": points[1],
            "options": [
                {"label": "A", "content": "HDFS"},
                {"label": "B", "content": "YARN"},
                {"label": "C", "content": "Hive"},
                {"label": "D", "content": "Sqoop"},
            ],
        },
        {
            "content": "关于 Spark 与 MapReduce 的区别，下列说法正确的是哪些？",
            "question_type": "multiple_choice",
            "answer": {"answers": ["A", "C"]},
            "analysis": "Spark 强调内存计算和更适合迭代场景，而 MapReduce 更偏批处理磁盘中转。",
            "knowledge_point": points[2],
            "options": [
                {"label": "A", "content": "Spark 更适合迭代计算场景"},
                {"label": "B", "content": "MapReduce 天然以内存计算为主"},
                {"label": "C", "content": "Spark 可通过 RDD 等抽象减少多轮磁盘落地"},
                {"label": "D", "content": "二者在执行模型上完全相同"},
            ],
        },
    ]

    ordered_questions: list[Question] = []
    for index, spec in enumerate(question_specs, start=1):
        question, _ = Question.objects.update_or_create(
            course=course,
            content=spec["content"],
            defaults={
                "chapter": "阶段测试",
                "question_type": spec["question_type"],
                "options": spec["options"],
                "answer": spec["answer"],
                "analysis": spec["analysis"],
                "difficulty": "medium",
                "score": Decimal("33.33") if index < 3 else Decimal("33.34"),
                "is_visible": True,
                "created_by": teacher,
            },
        )
        _set_related_knowledge_points(question, cast(KnowledgePoint, spec["knowledge_point"]))
        ordered_questions.append(question)

    exam, _ = Exam.objects.update_or_create(
        course=course,
        title="阶段测试：大数据基础综合",
        defaults={
            "description": "基于前三个学习节点的核心知识点出题，检验阶段学习成果并触发后续路径调整。",
            "exam_type": "node_test",
            "total_score": Decimal("100"),
            "pass_score": Decimal("60"),
            "duration": 10,
            "status": "published",
            "created_by": teacher,
        },
    )
    ExamQuestion.objects.filter(exam=exam).exclude(question__in=ordered_questions).delete()
    for index, question in enumerate(ordered_questions, start=1):
        exam_question, _ = ExamQuestion.objects.update_or_create(
            exam=exam,
            question=question,
            defaults={
                "order": index,
                "score": Decimal("35") if index < 3 else Decimal("30"),
            },
        )
        _ = exam_question
    return exam


def _build_point_intro_payloads(points: list[KnowledgePoint]) -> dict[str, dict[str, object]]:
    """
    为知识点创建固定介绍内容。
    :param points: 知识点列表。
    :return: 以知识点 ID 字符串为键的介绍映射。
    """
    payloads = [
        {
            "introduction": "大数据概念与特征节点主要帮助学生理解为什么现代数据处理要从单机思维转向分布式与海量场景。重点理解 4V 特征及其如何支撑后续 Hadoop 与 Spark 的学习。",
            "key_concepts": ["4V 特征", "分布式处理", "数据价值挖掘"],
            "learning_tips": "先抓住海量、多样、实时这三个关键词，再把它们和实际业务场景对应起来。",
            "difficulty": "easy",
            "sources": ["大数据概念与特征导读"],
        },
        {
            "introduction": "Hadoop 生态组成节点用于解释大数据平台为什么要把存储、计算和资源管理拆成多个组件。学生在这一节点应该能区分 HDFS、MapReduce 和 YARN 的职责分工。",
            "key_concepts": ["HDFS", "MapReduce", "YARN"],
            "learning_tips": "建议把组件关系先画成结构图，再用一句话分别概括每个组件负责什么。",
            "difficulty": "medium",
            "sources": ["Hadoop 生态架构详解"],
        },
        {
            "introduction": "Spark 核心计算模型节点用于引出内存计算与迭代任务优化这两个核心优势。这里展示的是从框架执行机制角度理解 Spark，而不是只背诵概念。",
            "key_concepts": ["RDD", "内存计算", "迭代任务"],
            "learning_tips": "把 Spark 与 MapReduce 做对比记忆，会更容易理解它为什么适合机器学习和图计算场景。",
            "difficulty": "medium",
            "sources": ["Spark 内存计算原理"],
        },
    ]

    intro_map: dict[str, dict[str, object]] = {}
    for point, payload in zip(points, payloads, strict=True):
        point.introduction = str(payload["introduction"])
        point.save(update_fields=["introduction", "updated_at"])
        intro_map[str(point.id)] = payload
    return intro_map


def _build_ai_demo_query_payloads(points: list[KnowledgePoint]) -> list[dict[str, object]]:
    """
    为答辩演示准备可直接复用的 AI 助手提问脚本。
    :param points: 主演示课程知识点列表。
    :return: 供课程配置与 CLI 输出复用的提问预置。
    """
    return [
        {
            "title": "图谱关系问答",
            "question": f"{points[2].name} 的前置知识是什么？为什么建议先学这些内容？",
            "point_id": points[2].id,
            "point_name": points[2].name,
            "expected_modes": ["graph_tools", "local"],
            "expected_focus": ["前置知识", "课程证据"],
        },
        {
            "title": "课程证据追问",
            "question": f"围绕 {points[1].name}，当前课程里有哪些资源或证据最值得先看？",
            "point_id": points[1].id,
            "point_name": points[1].name,
            "expected_modes": ["graph_tools", "local"],
            "expected_focus": ["资源推荐", "课程证据"],
        },
        {
            "title": "课程级学习建议",
            "question": "如果我接下来只剩 20 分钟，应该先复习哪些大数据基础内容？",
            "point_id": None,
            "point_name": "",
            "expected_modes": ["local", "global", "graph_tools"],
            "expected_focus": ["课程级 GraphRAG", "学习路径建议"],
        },
    ]
