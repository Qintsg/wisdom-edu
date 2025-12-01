"""教师课程工作台聚合服务。"""

from __future__ import annotations

from django.db.models import Q

from courses.models import Class, Course
from exams.models import Exam
from knowledge.models import KnowledgePoint, Resource
from assessments.models import Question


def build_course_workspace(course: Course, teacher) -> dict:
    """
    聚合教师课程工作台首页所需的数据。

    该结构用于把教师端逐步切到路由级 course workspace。
    """
    classes = (
        Class.objects.filter(
            teacher=teacher,
        ).filter(
            Q(course=course) | Q(class_courses__course=course, class_courses__is_active=True)
        )
        .distinct()
        .order_by("-created_at")
    )
    resource_count = Resource.objects.filter(course=course).count()
    question_count = Question.objects.filter(course=course).count()
    exam_count = Exam.objects.filter(course=course).count()
    knowledge_count = KnowledgePoint.objects.filter(course=course).count()
    return {
        "course": {
            "course_id": course.id,
            "name": course.name,
            "description": course.description or "",
            "term": course.term or "",
            "is_public": course.is_public,
        },
        "summary": {
            "class_count": classes.count(),
            "resource_count": resource_count,
            "question_count": question_count,
            "exam_count": exam_count,
            "knowledge_count": knowledge_count,
        },
        "recent_classes": [
            {
                "class_id": item.id,
                "name": item.name,
                "semester": item.semester or "",
                "student_count": item.get_student_count(),
                "is_active": item.is_active,
            }
            for item in classes[:6]
        ],
    }
