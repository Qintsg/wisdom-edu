"""学习者画像生成流程。"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Protocol

from django.db import DatabaseError

from assessments.models import AnswerHistory, ProfileHistory
from common.logging_utils import build_log_message
from knowledge.models import KnowledgeMastery, ProfileSummary
from .models import User

logger = logging.getLogger(__name__)


class LearnerProfileServiceProtocol(Protocol):
    """画像生成依赖的服务方法集合，避免与主服务类形成导入环。"""

    user: User

    def get_knowledge_mastery(self, course_id: int | None = None) -> List[Dict[str, Any]]:
        """获取知识掌握度。"""

    def get_ability_scores(self, course_id: int | None = None) -> Dict[str, float]:
        """获取能力分。"""

    def get_habit_preferences(self) -> Dict[str, Any]:
        """获取学习习惯偏好。"""

    def _build_cached_profile_result(self, course_id: int) -> Dict[str, Any] | None:
        """获取可复用的缓存画像结果。"""


def generate_profile_for_course(
    profile_service: LearnerProfileServiceProtocol,
    course_id: int,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """为指定课程生成或刷新学习者画像。"""
    user = profile_service.user
    try:
        if not force_refresh:
            cached_result = profile_service._build_cached_profile_result(course_id)
            if cached_result:
                logger.info(
                    build_log_message(
                        'profile.refresh.cache_hit',
                        user_id=user.id,
                        course_id=course_id,
                    )
                )
                return cached_result

        mastery_list = profile_service.get_knowledge_mastery(course_id)
        ability_scores = profile_service.get_ability_scores(course_id)
        habit_prefs = profile_service.get_habit_preferences()
        course_name = _resolve_course_name(course_id)
        kt_predictions: Dict[str, Any] = {}
        kt_enhanced = False

        try:
            kt_predictions = _refresh_mastery_with_kt(
                user=user,
                course_id=course_id,
            )
            if kt_predictions:
                mastery_list = profile_service.get_knowledge_mastery(course_id)
                kt_enhanced = True
                logger.info(
                    build_log_message(
                        'kt.profile_refresh.success',
                        user_id=user.id,
                        course_id=course_id,
                        knowledge_points=len(kt_predictions),
                    )
                )
        except (DatabaseError, ImportError, RuntimeError, TypeError, ValueError) as exc:
            logger.warning(
                build_log_message(
                    'kt.profile_refresh.fail',
                    user_id=user.id,
                    course_id=course_id,
                    error=exc,
                )
            )

        summary, weakness, suggestion, strength_list = _build_profile_text(
            user=user,
            course_id=course_id,
            mastery_list=mastery_list,
            ability_scores=ability_scores,
            habit_prefs=habit_prefs,
            course_name=course_name,
            kt_predictions=kt_predictions,
        )

        ProfileSummary.objects.update_or_create(
            user=user,
            course_id=course_id,
            defaults={
                'summary': summary,
                'weakness': weakness,
                'suggestion': suggestion
            }
        )
        ProfileHistory.objects.create(
            user=user,
            course_id=course_id,
            knowledge_mastery={str(m['point_id']): m['mastery_rate'] for m in mastery_list},
            ability_scores=ability_scores,
            habit_preferences=habit_prefs,
            update_reason='ai_refresh' if force_refresh else 'auto'
        )
        _record_profile_llm_log(
            user=user,
            course_id=course_id,
            mastery_count=len(mastery_list),
            kt_enhanced=kt_enhanced,
            summary=summary,
        )
        logger.info(
            build_log_message(
                'profile.refresh.complete',
                user_id=user.id,
                course_id=course_id,
                kt_enhanced=kt_enhanced,
            )
        )

        return {
            'success': True,
            'course_id': course_id,
            'summary': summary,
            'weakness': weakness,
            'suggestion': suggestion,
            'strength': strength_list,
            'kt_enhanced': kt_enhanced,
            'cached': False,
        }
    except Exception as exc:
        logger.error(
            build_log_message(
                'profile.refresh.fail',
                user_id=user.id,
                course_id=course_id,
                error=exc,
            )
        )
        return {'success': False, 'error': str(exc)}


def _resolve_course_name(course_id: int) -> str | None:
    """查询课程名；失败时返回 None，避免画像刷新中断。"""
    try:
        from courses.models import Course

        return Course.objects.filter(id=course_id).values_list('name', flat=True).first()
    except (DatabaseError, ImportError):
        return None


def _refresh_mastery_with_kt(user: User, course_id: int) -> Dict[str, Any]:
    """调用 KT 服务预测掌握度，并将预测结果回写到知识掌握度表。"""
    from ai_services.services import kt_service

    answer_records = AnswerHistory.objects.filter(
        user=user, course_id=course_id
    ).order_by('answered_at').values(
        'question_id', 'knowledge_point_id', 'is_correct'
    )
    if not answer_records.exists():
        return {}

    answer_history = [
        {
            'question_id': record['question_id'],
            'knowledge_point_id': record['knowledge_point_id'],
            'correct': 1 if record['is_correct'] else 0
        }
        for record in answer_records if record['knowledge_point_id']
    ]
    kt_result = kt_service.predict_mastery(
        user_id=user.id,
        course_id=course_id,
        answer_history=answer_history
    )
    kt_predictions = kt_result.get('predictions') or {}
    for kp_id_str, rate in kt_predictions.items():
        try:
            rate_float = float(rate)
        except (TypeError, ValueError):
            continue
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course_id=course_id,
            knowledge_point_id=kp_id_str,
            defaults={'mastery_rate': rate_float}
        )
    return kt_predictions


def _build_profile_text(
    user: User,
    course_id: int,
    mastery_list: List[Dict[str, Any]],
    ability_scores: Dict[str, float],
    habit_prefs: Dict[str, Any],
    course_name: str | None,
    kt_predictions: Dict[str, Any],
) -> tuple[str, str, str, List[Any]]:
    """优先使用 LLM 生成画像文案，失败时降级为规则摘要。"""
    try:
        from ai_services.services import llm_service as llm

        llm_result = llm.analyze_profile(
            mastery_data=mastery_list,
            ability_data=ability_scores or None,
            habit_data=habit_prefs or None,
            course_name=course_name,
            kt_predictions=kt_predictions or None,
        )
        weakness_raw = llm_result.get('weakness', [])
        weakness = '、'.join(weakness_raw) if isinstance(weakness_raw, list) else str(weakness_raw)
        strength_list = llm_result.get('strength', [])
        logger.info(
            build_log_message(
                'llm.profile.success',
                user_id=user.id,
                course_id=course_id,
                strength_count=len(strength_list),
            )
        )
        return (
            llm_result.get('summary', ''),
            weakness,
            llm_result.get('suggestion', ''),
            strength_list,
        )
    except (DatabaseError, ImportError, RuntimeError, TypeError, ValueError) as exc:
        logger.warning(
            build_log_message(
                'llm.profile.fail',
                user_id=user.id,
                course_id=course_id,
                error=exc,
            )
        )
        avg_mastery = sum(m['mastery_rate'] for m in mastery_list) / len(mastery_list) if mastery_list else 0
        weak_points = [m['point_name'] for m in mastery_list if m['mastery_rate'] < 0.6]
        summary = f"您的平均知识掌握度为{avg_mastery:.0%}。"
        weakness = '、'.join(weak_points[:5]) if weak_points else '暂无明显薄弱点'
        suggestion = '建议多练习薄弱知识点相关的题目，加深理解。' if weak_points else '继续保持，可以挑战更高难度的内容。'
        return summary, weakness, suggestion, []


def _record_profile_llm_log(
    user: User,
    course_id: int,
    mastery_count: int,
    kt_enhanced: bool,
    summary: str,
) -> None:
    """写入画像 LLM 调用日志；日志失败不影响主流程。"""
    try:
        from ai_services.models import LLMCallLog

        LLMCallLog.objects.create(
            user=user,
            call_type='profile_analysis',
            input_summary=f"course:{course_id}, mastery:{mastery_count}, kt:{kt_enhanced}",
            output_summary=summary[:500],
            is_success=True
        )
    except DatabaseError:
        return
