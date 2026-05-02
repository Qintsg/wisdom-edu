#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""DKT 数据库读取与训练数据导出工具。"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

from tools.dkt_paths import DEFAULT_TRAINING_DATA_PATH


def _setup_django() -> None:
    """确保脚本环境具备 Django ORM 上下文。"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")
    import django

    django.setup()


def _get_num_kp(course_id=None):
    """获取知识点数量。"""
    _setup_django()
    from knowledge.models import KnowledgePoint

    qs = KnowledgePoint.objects.all()
    if course_id:
        qs = qs.filter(course_id=course_id)
    return qs.count()


def _get_kp_mapping(course_id=None):
    """获取知识点 ID 到连续索引的映射。"""
    _setup_django()
    from knowledge.models import KnowledgePoint

    qs = KnowledgePoint.objects.all()
    if course_id:
        qs = qs.filter(course_id=course_id)
    kp_ids = sorted(qs.values_list("id", flat=True))
    kp_to_idx = {kp_id: idx for idx, kp_id in enumerate(kp_ids)}
    idx_to_kp = {idx: kp_id for kp_id, idx in kp_to_idx.items()}
    return kp_to_idx, idx_to_kp


def _get_first_course_with_kps() -> int | None:
    """获取第一个包含知识点数据的课程 ID。"""
    _setup_django()
    from knowledge.models import KnowledgePoint

    return KnowledgePoint.objects.order_by("course_id", "id").values_list("course_id", flat=True).first()


def _get_kp_prerequisites(course_id=None):
    """获取知识点之间的先修关系，用于合成数据。"""
    _setup_django()
    from knowledge.models import KnowledgeRelation

    qs = KnowledgeRelation.objects.filter(relation_type="prerequisite")
    if course_id:
        qs = qs.filter(pre_point__course_id=course_id)
    prereqs = {}
    for rel in qs:
        prereqs.setdefault(rel.post_point_id, []).append(rel.pre_point_id)
    return prereqs


def _get_kp_metadata(course_id=None):
    """获取知识点元数据，用于构造更贴近真实情况的合成学习轨迹。"""
    _setup_django()
    from django.db.models import Count, Q as QueryExpression
    from assessments.models import Question
    from knowledge.models import KnowledgePoint

    qs = KnowledgePoint.objects.all()
    if course_id:
        qs = qs.filter(course_id=course_id)

    kp_ids = list(qs.values_list("id", flat=True))
    question_stats = {}
    if kp_ids:
        q_stats = (
            Question.objects.filter(knowledge_points__id__in=kp_ids)
            .values("knowledge_points")
            .annotate(
                total=Count("id", distinct=True),
                easy=Count("id", filter=QueryExpression(difficulty="easy"), distinct=True),
                medium=Count("id", filter=QueryExpression(difficulty="medium"), distinct=True),
                hard=Count("id", filter=QueryExpression(difficulty="hard"), distinct=True),
            )
        )
        question_stats = {
            row["knowledge_points"]: {
                "total": row["total"],
                "easy": row["easy"],
                "medium": row["medium"],
                "hard": row["hard"],
            }
            for row in q_stats
            if row["knowledge_points"] is not None
        }

    metadata = {}
    for kp in qs.iterator():
        metadata[kp.id] = {
            "name": kp.name,
            "order": kp.order or 0,
            "level": kp.level or 1,
            "chapter": (kp.chapter or "").strip(),
            "cognitive_dimension": (kp.cognitive_dimension or "").strip(),
            "category": (kp.category or "").strip(),
            "tags": kp.get_tags_list(),
            "question_stats": question_stats.get(kp.id, {"total": 0, "easy": 0, "medium": 0, "hard": 0}),
        }
    return metadata


def export_training_data(course_id=None, output_path=None, max_step=50):
    """从 AnswerHistory 导出 DKT 三行格式训练数据。"""
    if max_step < 2:
        raise ValueError("max_step 必须至少为 2，才能形成有效的 DKT 序列")

    _setup_django()
    from assessments.models import AnswerHistory

    kp_to_idx, _ = _get_kp_mapping(course_id)
    if not kp_to_idx:
        print("[错误] 没有知识点数据，无法导出")
        return None, 0, 0

    qs = AnswerHistory.objects.select_related("question")
    if course_id:
        qs = qs.filter(course_id=course_id)
    qs = qs.order_by("user_id", "answered_at")

    user_seqs = defaultdict(list)
    for record in qs.iterator():
        kp_id = record.knowledge_point_id
        if kp_id and kp_id in kp_to_idx:
            user_seqs[record.user_id].append({"kp_idx": kp_to_idx[kp_id], "correct": 1 if record.is_correct else 0})

    if not user_seqs:
        print("[警告] 没有有效的答题历史记录")
        return None, 0, 0

    if output_path is None:
        output_path = str(DEFAULT_TRAINING_DATA_PATH)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    total_records = 0
    with open(output_path, "w", encoding="utf-8") as handle:
        for seq in user_seqs.values():
            total_records += len(seq)
            handle.write(f"{len(seq)}\n")
            handle.write(f"{','.join(str(item['kp_idx']) for item in seq)}\n")
            handle.write(f"{','.join(str(item['correct']) for item in seq)}\n")

    print(
        f"[导出成功] {len(user_seqs)} 个学生, {total_records} 条记录 → {output_path} "
        f"(建议训练 max_step={max_step})"
    )
    return output_path, len(user_seqs), total_records
