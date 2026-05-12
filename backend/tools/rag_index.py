"""RAG 索引构建工具。"""

from __future__ import annotations

from courses.models import Course
from platform_ai.rag import student_learning_rag
from platform_ai.rag.corpus import get_index_path


def build_rag_index(course_id: int | None = None) -> list[str]:
    """为指定课程或全部课程构建 GraphRAG 索引。"""

    course_ids: list[int]
    if course_id:
        course_ids = [int(course_id)]
    else:
        course_ids = list(Course.objects.values_list("id", flat=True))

    built_paths: list[str] = []
    for current_course_id in course_ids:
        student_learning_rag.build_index(current_course_id, persist=True)
        built_paths.append(str(get_index_path(current_course_id)))
    return built_paths


def refresh_rag_corpus(course_id: int | None = None) -> list[str]:
    """刷新课程 GraphRAG 语料并返回索引路径。"""

    return build_rag_index(course_id=course_id)
