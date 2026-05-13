#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
课程题目、资源与知识点绑定命令。
@Project : wisdom-edu
@File : bind_course_content.py
@Author : Qintsg
@Date : 2026-05-13 10:35
'''

from __future__ import annotations

from typing import cast

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from assessments.models import AssessmentResult
from assessments.services.knowledge_result_refresh import refresh_course_knowledge_result_snapshots
from courses.models import Course
from knowledge.services.content_binding import (
    ContentBindingChange,
    CourseContentBindingPlan,
    CourseContentBindingService,
)


class Command(BaseCommand):
    """同步课程内容与知识点绑定。"""

    help = "根据题干、资源标题和知识点名称为课程题目/资源补齐知识点绑定"

    def add_arguments(self, parser: CommandParser) -> None:
        """注册命令行参数。"""
        parser.add_argument("--course-id", type=int, default=None, help="课程 ID")
        parser.add_argument("--course-name", type=str, default="大数据技术与应用", help="课程名称")
        parser.add_argument("--apply", action="store_true", help="实际写入数据库；默认只 dry-run")
        parser.add_argument("--replace-existing", action="store_true", help="重新计算并覆盖已有题目/资源绑定")
        parser.add_argument(
            "--sync-initial-history",
            action="store_true",
            help="同时根据测评结果快照补齐既有初始评测 AnswerHistory",
        )
        parser.add_argument(
            "--replace-initial-history",
            action="store_true",
            help="同步历史时先删除目标用户课程下既有 source=initial 历史再重建",
        )
        parser.add_argument(
            "--refresh-assessment-results",
            action="store_true",
            help="写回绑定后同步重算既有知识测评结果快照",
        )

    def handle(self, *args: object, **options: object) -> None:
        """执行课程内容绑定。"""
        course = self._resolve_course(
            course_id=cast(int | None, options.get("course_id")),
            course_name=str(options.get("course_name") or "").strip(),
        )
        apply_changes = bool(options.get("apply"))
        sync_initial_history = bool(options.get("sync_initial_history"))
        replace_existing = bool(options.get("replace_existing"))
        replace_initial_history = bool(options.get("replace_initial_history"))
        refresh_assessment_results = bool(options.get("refresh_assessment_results"))

        service = CourseContentBindingService(course_id=int(course.id))
        plan = service.build_plan(
            sync_initial_history=sync_initial_history,
            replace_existing=replace_existing,
            replace_initial_history=replace_initial_history,
        )
        self._write_plan_summary(
            course=course,
            plan=plan,
            apply_changes=apply_changes,
            refresh_assessment_results=refresh_assessment_results,
        )
        if not apply_changes:
            self.stdout.write(self.style.WARNING("dry-run 完成；添加 --apply 后才会写回数据库。"))
            return

        with transaction.atomic():
            service.apply_plan(plan, replace_initial_history=replace_initial_history)
        refresh_count = 0
        if refresh_assessment_results:
            refresh_count = len(refresh_course_knowledge_result_snapshots(int(course.id)))
        total_changes = (
            len(plan.question_changes)
            + len(plan.resource_changes)
            + len(plan.history_changes)
            + refresh_count
        )
        self.stdout.write(self.style.SUCCESS(f"已写回 {total_changes} 项绑定/历史变更。"))

    def _resolve_course(self, *, course_id: int | None, course_name: str) -> Course:
        """解析目标课程。"""
        if course_id is not None:
            return Course.objects.get(id=course_id)
        if not course_name:
            raise Course.DoesNotExist("必须提供 --course-id 或 --course-name")
        return Course.objects.get(name=course_name)

    def _write_plan_summary(
        self,
        *,
        course: Course,
        plan: CourseContentBindingPlan,
        apply_changes: bool,
        refresh_assessment_results: bool,
    ) -> None:
        """输出绑定计划摘要。"""
        mode_label = "apply" if apply_changes else "dry-run"
        self.stdout.write(f"模式: {mode_label}")
        self.stdout.write(f"课程: {course.id} {course.name}")
        self.stdout.write(f"待绑定题目: {len(plan.question_changes)}")
        self.stdout.write(f"待绑定资源: {len(plan.resource_changes)}")
        self.stdout.write(f"待补齐初始评测历史: {len(plan.history_changes)}")
        if refresh_assessment_results:
            result_count = AssessmentResult.objects.filter(
                course=course,
                assessment__assessment_type="knowledge",
            ).count()
            self.stdout.write(f"待刷新知识测评结果快照: {result_count}")
        self._write_change_preview("题目", plan.question_changes)
        self._write_change_preview("资源", plan.resource_changes)

    def _write_change_preview(
        self,
        label: str,
        changes: tuple[ContentBindingChange, ...],
    ) -> None:
        """输出绑定变更预览。"""
        for change in changes[:20]:
            point_text = "、".join(change.point_names)
            self.stdout.write(
                f"- {label} {change.item_id}: {change.title[:60]} -> {point_text} ({change.reason})"
            )
        if len(changes) > 20:
            self.stdout.write(f"... 其余 {len(changes) - 20} 条{label}绑定省略")
