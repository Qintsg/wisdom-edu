"""
考试模块 - 教师接口兼容层。

具体实现已按职责拆分到教师考试管理、题库管理、结果分析与共享 helper 模块；
本文件保留旧导入路径，供 urls、tests 和外部 patch 继续使用。
"""

from exams.api.teacher.exam_management import (
    exam_create,
    exam_delete,
    exam_manage_list,
    exam_publish,
    exam_teacher_detail,
    exam_unpublish,
    exam_update,
    teacher_exam_add_questions,
    teacher_exam_remove_questions,
)
from exams.api.teacher.helpers import (
    _build_exam_question_rows,
    _ensure_teacher_exam_access,
    _get_exam_or_404,
    _get_owned_exam_or_404,
    _get_teacher_course_ids,
    _normalize_choice_answer_set,
    _parse_pagination,
    _validate_exam_scores,
)
from exams.api.teacher.question import (
    question_create,
    question_delete,
    question_list,
    question_update,
)
from exams.api.teacher.result import (
    UTF8_BOM,
    exam_analysis,
    exam_results,
    exam_student_detail,
    teacher_exam_export,
)


__all__ = [
    'UTF8_BOM',
    '_build_exam_question_rows',
    '_ensure_teacher_exam_access',
    '_get_exam_or_404',
    '_get_owned_exam_or_404',
    '_get_teacher_course_ids',
    '_normalize_choice_answer_set',
    '_parse_pagination',
    '_validate_exam_scores',
    'exam_analysis',
    'exam_create',
    'exam_delete',
    'exam_manage_list',
    'exam_publish',
    'exam_results',
    'exam_student_detail',
    'exam_teacher_detail',
    'exam_unpublish',
    'exam_update',
    'question_create',
    'question_delete',
    'question_list',
    'question_update',
    'teacher_exam_add_questions',
    'teacher_exam_export',
    'teacher_exam_remove_questions',
]
