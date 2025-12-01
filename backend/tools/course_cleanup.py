#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""课程清理工具。"""

from __future__ import annotations

from courses.course_cleanup import cleanup_course_runtime_artifacts
from courses.models import Course


def delete_course_with_cleanup(course_id: int, yes: bool = False) -> dict[str, object]:
    """删除课程；若课程已不存在，则补做残留图谱资产清理。"""
    if not yes:
        confirm = input(f"将删除课程 {course_id} 及其外部图谱资产，继续? (y/N): ").strip().lower()
        if confirm != "y":
            print("已取消")
            return {
                "course_id": course_id,
                "deleted": False,
                "cleanup_report": None,
            }

    course = Course.objects.filter(id=course_id).first()
    if course is not None:
        course_name = course.name
        course.delete()
        print(f"课程已删除: {course_name} (ID={course_id})")
        return {
            "course_id": course_id,
            "course_name": course_name,
            "deleted": True,
            "cleanup_report": "signal_triggered",
        }

    cleanup_report = cleanup_course_runtime_artifacts(course_id)
    print(f"课程记录不存在，已补做外部资产清理: {cleanup_report}")
    return {
        "course_id": course_id,
        "course_name": "",
        "deleted": False,
        "cleanup_report": cleanup_report,
    }