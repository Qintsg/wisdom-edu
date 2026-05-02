#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入模块。

保留 JSON / Excel 两类导入入口，具体清洗与解析逻辑下沉到辅助模块，
避免导入命令和教师端接口继续依赖同一团解析细节。
"""
from __future__ import annotations

from collections.abc import Mapping

from django.db import transaction

from assessments.models import Question
from tools.common import get_course
from tools.question_import_support import (
    QuestionImportSummary,
    build_json_question_payload,
    build_question_import_context,
    create_question_from_payload,
    iter_excel_question_payloads,
    link_question_knowledge_points,
    load_question_json_source,
    open_question_bank_workbook,
    resolve_filename_knowledge_point,
    strip_import_text,
)
from tools.testing import _status_flag


# 兼容现有模块直接 `from tools.questions import _strip_html` 的用法。
_strip_html = strip_import_text


def _build_result_payload(
    *,
    course_id: int,
    course_name: str,
    summary: QuestionImportSummary,
    dry_run: bool = False,
    replace: bool = False,
) -> dict[str, object]:
    """构建供 CLI 与教师端接口复用的导入结果载荷。"""
    return {
        "course_id": course_id,
        "course_name": course_name,
        "created_count": summary.imported_count,
        "linked_count": summary.linked_count,
        "unlinked_count": max(summary.imported_count - summary.linked_count, 0),
        "skipped_duplicates": summary.skipped_duplicates,
        "unmatched_knowledge_points": sorted(summary.unmatched_names),
        "dry_run": dry_run,
        "replace": replace,
    }


def _print_json_import_summary(course_name: str, summary: QuestionImportSummary) -> None:
    """输出 JSON 导入摘要。"""
    message = f"题库JSON导入完成: 课程={course_name}, 新增题目={summary.imported_count}"
    if summary.linked_count:
        message += f", {summary.linked_count} 题已关联知识点"
    if summary.skipped_duplicates:
        message += f", 跳过重复题目={summary.skipped_duplicates}"
    if summary.unmatched_names:
        message += f"\n  {_status_flag(False)} 未匹配的知识点: {', '.join(sorted(summary.unmatched_names))}"
    print(message)


def _print_excel_import_summary(summary: QuestionImportSummary) -> None:
    """输出 Excel 导入摘要。"""
    message = f"题库导入完成：{summary.imported_count} 题"
    if summary.linked_count:
        message += f"，{summary.linked_count} 题已关联知识点"
    if summary.imported_count > summary.linked_count:
        message += f"，{summary.imported_count - summary.linked_count} 题未关联知识点"
    if summary.unmatched_names:
        message += f"\n  {_status_flag(False)} 未匹配的知识点名称: {', '.join(sorted(summary.unmatched_names))}"
    print(message)


def import_questions_json(
    file: object,
    course_id: int,
    replace: bool = False,
    dry_run: bool = False,
) -> dict[str, object]:
    """
    导入 JSON 格式题库。

    `file` 兼容本地路径、Path 对象以及教师端接口已经解析好的 JSON 字典。
    """
    data = load_question_json_source(file)
    course = get_course(course_id)
    raw_questions = data.get("questions", [])
    questions = raw_questions if isinstance(raw_questions, list) else []

    if not questions:
        print("未找到questions，跳过导入。")
        return _build_result_payload(
            course_id=int(course.pk),
            course_name=course.name,
            summary=QuestionImportSummary(),
            dry_run=dry_run,
            replace=replace,
        )

    if dry_run:
        print(
            f"[DRY-RUN] 将导入题库JSON: 课程={course.name}, "
            f"题目={len(questions)}, replace={replace}"
        )
        dry_run_summary = QuestionImportSummary(imported_count=len(questions))
        return _build_result_payload(
            course_id=int(course.pk),
            course_name=course.name,
            summary=dry_run_summary,
            dry_run=True,
            replace=replace,
        )

    context = build_question_import_context(course)
    summary = QuestionImportSummary()
    with transaction.atomic():
        if replace:
            Question.objects.filter(course=course).delete()

        for raw_question in questions:
            if not isinstance(raw_question, Mapping):
                continue
            payload = build_json_question_payload(raw_question)
            if payload is None:
                continue
            if not replace and Question.objects.filter(course=course, content=payload.content).exists():
                summary.skipped_duplicates += 1
                continue
            question = create_question_from_payload(course, payload)
            linked = link_question_knowledge_points(
                question,
                payload.knowledge_point_names,
                context,
                summary.unmatched_names,
            )
            summary.record_import(linked)

    _print_json_import_summary(course.name, summary)
    return _build_result_payload(
        course_id=int(course.pk),
        course_name=course.name,
        summary=summary,
        replace=replace,
    )


def import_question_bank(
    file_path: object,
    course_id: int,
    for_initial_assessment: bool = False,
) -> dict[str, object]:
    """
    导入 Excel 格式题库。

    `file_path` 兼容本地路径与教师端上传文件对象。
    """
    try:
        import pandas as pd
    except ImportError:
        print("请先安装 pandas openpyxl")
        return {
            "course_id": course_id,
            "error": "missing_pandas",
            "created_count": 0,
            "linked_count": 0,
        }

    course = get_course(course_id)
    workbook = open_question_bank_workbook(file_path, pd)
    context = build_question_import_context(course)
    fallback_knowledge_point = resolve_filename_knowledge_point(workbook.stem, context)
    if fallback_knowledge_point is not None:
        print(f'  文件名匹配知识点: "{workbook.stem}" → {fallback_knowledge_point.name}')

    summary = QuestionImportSummary()
    with transaction.atomic():
        for payload in iter_excel_question_payloads(
            workbook,
            pd,
            for_initial_assessment=for_initial_assessment,
        ):
            question = create_question_from_payload(course, payload)
            linked = link_question_knowledge_points(
                question,
                payload.knowledge_point_names,
                context,
                summary.unmatched_names,
            )
            if not linked and fallback_knowledge_point is not None:
                question.knowledge_points.add(fallback_knowledge_point)
                linked = True
            summary.record_import(linked)

    _print_excel_import_summary(summary)
    return _build_result_payload(
        course_id=int(course.pk),
        course_name=course.name,
        summary=summary,
    )
