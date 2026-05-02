#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
考试模块学生接口兼容入口。

公开 URL 仍通过 exams.views -> exams.student_views 暴露；实现按考试、提交、报告、初始评测和班级职责拆分。
"""
import logging

from assessments.models import Question
from knowledge.models import KnowledgeMastery, KnowledgePoint

from .models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from .student_artifact_views import exam_answer_sheet, exam_download, exam_retake
from .student_class_views import (
    student_class_assignments,
    student_class_members,
    student_class_notifications,
    student_class_ranking,
)
from .student_exam_views import exam_detail, exam_list
from .student_feedback_views import generate_feedback_report, get_feedback_report
from .student_helpers import (
    build_exam_question_details as _build_exam_question_details,
    build_exam_score_map as _build_exam_score_map,
    build_feedback_overview as _build_feedback_overview,
    build_feedback_report_ref as _build_feedback_report_ref,
    build_mastery_change_payload as _build_mastery_change_payload,
    build_question_detail as _build_question_detail,
    build_submission_feedback_snapshot as _build_submission_feedback_snapshot,
    normalize_feedback_payload as _normalize_feedback_payload,
    resolve_pass_threshold as _resolve_pass_threshold,
    snapshot_mastery_for_points as _snapshot_mastery_for_points,
)
from .student_initial_assessment_views import initial_assessment_start, initial_assessment_submit
from .student_submission_views import exam_result, exam_save_draft, exam_statistics, exam_submit


logger = logging.getLogger(__name__)


__all__ = [
    'Exam',
    'ExamQuestion',
    'ExamSubmission',
    'FeedbackReport',
    'KnowledgeMastery',
    'KnowledgePoint',
    'Question',
    '_build_exam_question_details',
    '_build_exam_score_map',
    '_build_feedback_overview',
    '_build_feedback_report_ref',
    '_build_mastery_change_payload',
    '_build_question_detail',
    '_build_submission_feedback_snapshot',
    '_normalize_feedback_payload',
    '_resolve_pass_threshold',
    '_snapshot_mastery_for_points',
    'exam_answer_sheet',
    'exam_detail',
    'exam_download',
    'exam_list',
    'exam_result',
    'exam_retake',
    'exam_save_draft',
    'exam_statistics',
    'exam_submit',
    'generate_feedback_report',
    'get_feedback_report',
    'initial_assessment_start',
    'initial_assessment_submit',
    'logger',
    'student_class_assignments',
    'student_class_members',
    'student_class_notifications',
    'student_class_ranking',
]
