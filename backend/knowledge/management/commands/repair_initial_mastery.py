"""修复初始知识评测后异常聚集的掌握度数据。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from assessments.assessment_helpers import (
    INITIAL_MASTERY_MAX,
    calculate_initial_mastery_baseline,
)
from assessments.models import AnswerHistory
from ai_services.services.kt_prediction_support import (
    answered_point_ids,
    is_mefkt_prediction,
    normalize_prediction_map,
)
from knowledge.models import KnowledgeMastery, KnowledgePoint
from learning.path_rules import apply_prerequisite_caps


ABNORMAL_OLD_VALUES = (0.25, 0.30, 0.333, 0.50)
UPDATE_EPSILON = 0.0005


@dataclass(frozen=True)
class RepairTarget:
    """一个需要重算初始评测掌握度的学生课程组合。"""

    user_id: int
    course_id: int


@dataclass(frozen=True)
class MasteryChange:
    """单条掌握度修复结果。"""

    user_id: int
    course_id: int
    point_id: int
    old_rate: float | None
    new_rate: float
    has_answer_evidence: bool
    source: str


# 维护意图：提供可重复的初测掌握度数据修复入口。
# 边界说明：只修复 KnowledgeMastery，不改题库、作答历史和 schema。
# 风险说明：执行 --apply 前应先 dry-run，确认影响范围。
class Command(BaseCommand):
    """修复初始知识评测后异常聚集的掌握度数据。"""

    help = "根据初始评测作答历史和真实 MEFKT 预测修复异常掌握度数据"

    def add_arguments(self, parser: CommandParser) -> None:
        """注册命令行参数。"""
        parser.add_argument("--apply", action="store_true", help="实际写回数据库；默认只 dry-run")
        parser.add_argument("--user-id", type=int, default=None, help="仅修复指定学生用户")
        parser.add_argument("--course-id", type=int, default=None, help="仅修复指定课程")
        parser.add_argument(
            "--include-unpublished",
            action="store_true",
            help="同时处理未发布知识点；默认只处理已发布知识点",
        )

    def handle(self, *args: object, **options: object) -> None:
        """执行修复命令。"""
        apply_changes = bool(options.get("apply"))
        targets = self._load_targets(
            user_id=cast(int | None, options.get("user_id")),
            course_id=cast(int | None, options.get("course_id")),
        )
        if not targets:
            self.stdout.write(self.style.WARNING("未找到 source=initial 的初始评测作答历史。"))
            return

        include_unpublished = bool(options.get("include_unpublished"))
        all_changes: list[MasteryChange] = []
        for target in targets:
            all_changes.extend(
                self._build_target_changes(
                    target=target,
                    include_unpublished=include_unpublished,
                )
            )

        abnormal_changes = [
            change for change in all_changes if self._is_old_abnormal_value(change.old_rate)
        ]
        measured_changes = [change for change in all_changes if change.has_answer_evidence]
        inferred_changes = [change for change in all_changes if not change.has_answer_evidence]
        self._write_summary(
            targets=targets,
            changes=all_changes,
            abnormal_changes=abnormal_changes,
            measured_changes=measured_changes,
            inferred_changes=inferred_changes,
            apply_changes=apply_changes,
        )

        if not apply_changes:
            self.stdout.write(self.style.WARNING("dry-run 完成；添加 --apply 后才会写回数据库。"))
            return

        with transaction.atomic():
            for change in all_changes:
                KnowledgeMastery.objects.update_or_create(
                    user_id=change.user_id,
                    knowledge_point_id=change.point_id,
                    defaults={
                        "course_id": change.course_id,
                        "mastery_rate": round(change.new_rate, 3),
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"已写回 {len(all_changes)} 条 KnowledgeMastery。"))

    def _load_targets(self, *, user_id: int | None, course_id: int | None) -> list[RepairTarget]:
        """读取有初始评测历史的学生课程组合。"""
        queryset = AnswerHistory.objects.filter(source="initial")
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        if course_id is not None:
            queryset = queryset.filter(course_id=course_id)
        rows = (
            queryset.exclude(knowledge_point_id__isnull=True)
            .values("user_id", "course_id")
            .distinct()
            .order_by("course_id", "user_id")
        )
        return [
            RepairTarget(user_id=int(row["user_id"]), course_id=int(row["course_id"]))
            for row in rows
        ]

    def _build_target_changes(
        self,
        *,
        target: RepairTarget,
        include_unpublished: bool,
    ) -> list[MasteryChange]:
        """重算一个学生课程组合的掌握度变更。"""
        answer_history = self._load_kt_history(target)
        if not answer_history:
            return []

        direct_mastery = self._build_direct_mastery(answer_history)
        course_point_ids = self._load_course_point_ids(
            target.course_id,
            include_unpublished=include_unpublished,
        )
        prediction_map, prediction_source = self._predict_with_mefkt_first(
            target=target,
            answer_history=answer_history,
            course_point_ids=course_point_ids,
        )
        final_mastery = self._merge_mastery(
            direct_mastery=direct_mastery,
            prediction_map=prediction_map,
            prediction_source=prediction_source,
        )
        if not final_mastery:
            return []

        final_mastery = apply_prerequisite_caps(final_mastery, target.course_id, buffer=0.05)
        existing_rates = {
            row.knowledge_point_id: float(row.mastery_rate)
            for row in KnowledgeMastery.objects.filter(
                user_id=target.user_id,
                course_id=target.course_id,
                knowledge_point_id__in=final_mastery.keys(),
            )
        }
        changes: list[MasteryChange] = []
        direct_point_ids = set(direct_mastery)
        for point_id, new_rate in sorted(final_mastery.items()):
            old_rate = existing_rates.get(point_id)
            if old_rate is not None and abs(old_rate - new_rate) <= UPDATE_EPSILON:
                continue
            changes.append(
                MasteryChange(
                    user_id=target.user_id,
                    course_id=target.course_id,
                    point_id=point_id,
                    old_rate=old_rate,
                    new_rate=round(max(0.0, min(INITIAL_MASTERY_MAX, float(new_rate))), 4),
                    has_answer_evidence=point_id in direct_point_ids,
                    source=prediction_source,
                )
            )
        return changes

    def _load_kt_history(self, target: RepairTarget) -> list[dict[str, int]]:
        """读取初始评测作答历史并转换为 KT 输入。"""
        rows = (
            AnswerHistory.objects.filter(
                user_id=target.user_id,
                course_id=target.course_id,
                source="initial",
            )
            .exclude(knowledge_point_id__isnull=True)
            .order_by("answered_at", "id")
            .values("question_id", "knowledge_point_id", "is_correct")
        )
        return [
            {
                "question_id": int(row["question_id"]),
                "knowledge_point_id": int(row["knowledge_point_id"]),
                "correct": 1 if row["is_correct"] else 0,
            }
            for row in rows
        ]

    def _build_direct_mastery(self, answer_history: list[dict[str, int]]) -> dict[int, float]:
        """根据直接作答证据重算初测掌握度基线。"""
        point_stats: dict[int, dict[str, int]] = {}
        for record in answer_history:
            point_id = int(record["knowledge_point_id"])
            point_stats.setdefault(point_id, {"correct": 0, "total": 0})
            point_stats[point_id]["total"] += 1
            point_stats[point_id]["correct"] += int(record["correct"])
        return {
            point_id: calculate_initial_mastery_baseline(
                stats["correct"],
                stats["total"],
            )
            for point_id, stats in point_stats.items()
        }

    def _load_course_point_ids(self, course_id: int, *, include_unpublished: bool) -> list[int]:
        """读取课程知识点，用作 MEFKT 推断目标。"""
        queryset = KnowledgePoint.objects.filter(course_id=course_id).order_by("order", "id")
        if not include_unpublished:
            queryset = queryset.filter(is_published=True)
        return [int(point_id) for point_id in queryset.values_list("id", flat=True)]

    def _predict_with_mefkt_first(
        self,
        *,
        target: RepairTarget,
        answer_history: list[dict[str, int]],
        course_point_ids: list[int],
    ) -> tuple[dict[int, float], str]:
        """优先使用真实 MEFKT 预测，回退时只保留有作答证据的统计结果。"""
        from ai_services.services import kt_service

        if not course_point_ids:
            return {}, "no_course_points"
        result = kt_service.predict_mastery(
            user_id=target.user_id,
            course_id=target.course_id,
            answer_history=answer_history,
            knowledge_points=course_point_ids,
        )
        prediction_map = normalize_prediction_map(result.get("predictions"))
        if is_mefkt_prediction(result):
            model_type = str(result.get("model_type") or "mefkt")
            if model_type in {"fusion", "ensemble"}:
                model_type = f"mefkt_{model_type}"
            return prediction_map, model_type

        evidence_points = answered_point_ids(answer_history)
        return {
            point_id: rate
            for point_id, rate in prediction_map.items()
            if point_id in evidence_points
        }, str(result.get("model_type") or "fallback")

    def _merge_mastery(
        self,
        *,
        direct_mastery: dict[int, float],
        prediction_map: dict[int, float],
        prediction_source: str,
    ) -> dict[int, float]:
        """合并直接初测结果和 KT/MEFKT 预测结果。"""
        merged = dict(direct_mastery)
        uses_mefkt = prediction_source in {
            "mefkt_real",
            "mefkt_question_online",
            "mefkt_fusion",
            "mefkt_ensemble",
        }
        for point_id, predicted_rate in prediction_map.items():
            normalized_rate = max(0.0, min(INITIAL_MASTERY_MAX, float(predicted_rate)))
            if point_id not in merged:
                if uses_mefkt:
                    merged[point_id] = round(normalized_rate, 4)
                continue
            baseline = float(merged[point_id])
            blended = baseline * 0.72 + normalized_rate * 0.28
            merged[point_id] = round(min(INITIAL_MASTERY_MAX, max(0.0, blended)), 4)
        return merged

    def _write_summary(
        self,
        *,
        targets: list[RepairTarget],
        changes: list[MasteryChange],
        abnormal_changes: list[MasteryChange],
        measured_changes: list[MasteryChange],
        inferred_changes: list[MasteryChange],
        apply_changes: bool,
    ) -> None:
        """输出 dry-run 或 apply 摘要。"""
        mode_label = "apply" if apply_changes else "dry-run"
        self.stdout.write(f"模式: {mode_label}")
        self.stdout.write(f"扫描 user/course: {len(targets)}")
        self.stdout.write(f"待更新 KnowledgeMastery: {len(changes)}")
        self.stdout.write(f"其中旧尖峰值记录: {len(abnormal_changes)}")
        self.stdout.write(f"直接初测证据更新: {len(measured_changes)}")
        self.stdout.write(f"MEFKT 未测推断更新: {len(inferred_changes)}")
        for change in changes[:20]:
            old_text = "None" if change.old_rate is None else f"{change.old_rate:.4f}"
            evidence = "measured" if change.has_answer_evidence else "inferred"
            self.stdout.write(
                f"- user={change.user_id} course={change.course_id} point={change.point_id} "
                f"{old_text} -> {change.new_rate:.4f} {evidence} source={change.source}"
            )
        if len(changes) > 20:
            self.stdout.write(f"... 其余 {len(changes) - 20} 条省略")

    @staticmethod
    def _is_old_abnormal_value(rate: float | None) -> bool:
        """判断现值是否落在旧算法常见异常尖峰附近。"""
        if rate is None:
            return False
        return any(abs(float(rate) - old_value) <= 0.006 for old_value in ABNORMAL_OLD_VALUES)
