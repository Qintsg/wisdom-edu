"""课程模型信号。"""

from __future__ import annotations

import logging

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .course_cleanup import cleanup_course_runtime_artifacts
from .models import Course


logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Course)
def cleanup_deleted_course_artifacts(sender, instance: Course, **_kwargs) -> None:
    """课程删除后同步清理外部 GraphRAG / Neo4j 运行时资产。"""
    _ = sender
    course_id = int(getattr(instance, "id", 0) or 0)
    if course_id <= 0:
        return
    try:
        cleanup_course_runtime_artifacts(course_id)
    except Exception as error:  # noqa: BLE001
        logger.warning("课程删除后清理外部资产失败: course=%s error=%s", course_id, error)