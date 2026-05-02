"""
用户模块 - 服务层

提供学习者画像生成、更新和管理相关的业务逻辑服务。
将画像相关功能集中管理，便于维护和扩展。
"""
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone

from knowledge.models import KnowledgeMastery, ProfileSummary
from assessments.models import AbilityScore, AnswerHistory, ProfileHistory, AssessmentStatus
from .models import User, HabitPreference


class LearnerProfileService:
    """
    学习者画像服务类
    
    提供学习者画像的生成、更新、查询等功能。
    画像数据包括：
    - 知识掌握度（按课程和知识点）
    - 能力评分（按维度）
    - 学习习惯偏好
    - 画像摘要和建议
    """
    
    def __init__(self, user: User):
        """
        初始化画像服务
        
        Args:
            user: 用户对象
        """
        self.user = user

    def get_knowledge_mastery(self, course_id: int = None) -> List[Dict]:
        """
        获取用户的知识掌握度数据
        
        Args:
            course_id: 课程ID（可选，为空返回所有课程）
        
        Returns:
            知识掌握度列表
        """
        queryset = KnowledgeMastery.objects.filter(user=self.user)

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return [
            {
                'point_id': m.knowledge_point_id,
                'point_name': m.knowledge_point.name,
                'course_id': m.course_id,
                'mastery_rate': float(m.mastery_rate) if m.mastery_rate else 0,
                'tags': getattr(m.knowledge_point, 'tags', '') or '',
                'cognitive_dimension': getattr(m.knowledge_point, 'cognitive_dimension', '') or '',
                'category': getattr(m.knowledge_point, 'category', '') or '',
                'teaching_goal': getattr(m.knowledge_point, 'teaching_goal', '') or '',
                'updated_at': m.updated_at.isoformat() if m.updated_at else None
            }
            for m in queryset.select_related('knowledge_point')
        ]

    def get_ability_scores(self, course_id: int = None) -> Dict[str, float]:
        """
        获取用户的能力评分
        
        Args:
            course_id: 课程ID（可选）
        
        Returns:
            能力维度得分字典
        """
        scores = {}
        queryset = AbilityScore.objects.filter(user=self.user)

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        for score in queryset:
            if score.scores:
                scores.update(score.scores)

        return scores

    def get_habit_preferences(self) -> Dict[str, Any]:
        """
        获取用户的学习习惯偏好
        
        Returns:
            学习偏好字典
        """
        habit_pref = HabitPreference.objects.filter(user=self.user).first()

        if not habit_pref:
            return {}

        result = {
            'preferred_resource': habit_pref.preferred_resource or 'video',
            'preferred_study_time': habit_pref.preferred_study_time or 'evening',
            'study_pace': habit_pref.study_pace or 'moderate',
            'study_duration': habit_pref.study_duration or 'medium',
            'review_frequency': habit_pref.review_frequency or 'weekly',
            'learning_style': habit_pref.learning_style or 'visual',
            'accept_challenge': habit_pref.accept_challenge if habit_pref.accept_challenge is not None else True,
            'daily_goal_minutes': habit_pref.daily_goal_minutes or 60,
            'weekly_goal_days': habit_pref.weekly_goal_days or 5,
        }
        if isinstance(habit_pref.preferences, dict):
            result.update(habit_pref.preferences)

        return result

    def get_profile_summary(self, course_id: int = None) -> Dict[str, Any]:
        """
        获取用户的画像摘要
        
        Args:
            course_id: 课程ID（可选）
        
        Returns:
            画像摘要信息
        """
        queryset = ProfileSummary.objects.filter(user=self.user)

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        summary = queryset.first()

        if not summary:
            return {
                'summary': '',
                'weakness': '',
                'suggestion': '',
                'generated_at': None
            }

        return {
            'summary': summary.summary or '',
            'weakness': summary.weakness or '',
            'suggestion': summary.suggestion or '',
            'generated_at': summary.generated_at.isoformat() if summary.generated_at else None
        }

    @staticmethod
    def _derive_strength_points(mastery_list: List[Dict[str, Any]]) -> List[str]:
        """从掌握度列表中提取适合展示的优势知识点名称。"""
        highlighted_points = [
            str(item.get('point_name'))
            for item in mastery_list
            if item.get('point_name') and float(item.get('mastery_rate') or 0) >= 0.75
        ]
        if highlighted_points:
            return highlighted_points[:3]

        ranked_points = sorted(
            [item for item in mastery_list if item.get('point_name')],
            key=lambda item: float(item.get('mastery_rate') or 0),
            reverse=True,
        )
        return [str(item.get('point_name')) for item in ranked_points[:3]]

    def _build_cached_profile_result(self, course_id: int) -> Dict[str, Any] | None:
        """命中已生成画像时直接返回，避免重复触发 KT 与 LLM。"""
        cached_summary = ProfileSummary.objects.filter(
            user=self.user,
            course_id=course_id,
        ).first()
        if not cached_summary:
            return None

        mastery_list = self.get_knowledge_mastery(course_id)
        return {
            'success': True,
            'course_id': course_id,
            'summary': cached_summary.summary or '',
            'weakness': cached_summary.weakness or '',
            'suggestion': cached_summary.suggestion or '',
            'strength': self._derive_strength_points(mastery_list),
            'kt_enhanced': False,
            'cached': True,
            'generated_at': cached_summary.generated_at.isoformat() if cached_summary.generated_at else None,
        }

    def get_full_profile(self, course_id: int = None) -> Dict[str, Any]:
        """
        获取用户的完整学习者画像
        
        Args:
            course_id: 课程ID（可选）
        
        Returns:
            完整的画像数据
        """
        return {
            'user_id': self.user.id,
            'username': self.user.username,
            'knowledge_mastery': self.get_knowledge_mastery(course_id),
            'ability_scores': self.get_ability_scores(course_id),
            'habit_preferences': self.get_habit_preferences(),
            'profile_summary': self.get_profile_summary(course_id),
            'last_update': timezone.now().isoformat()
        }

    def update_mastery_from_answers(
        self, 
        course_id: int, 
        update_reason: str = 'practice'
    ) -> Dict[str, Any]:
        """
        根据答题历史更新知识掌握度
        
        Args:
            course_id: 课程ID
            update_reason: 更新原因（practice/exam/initial/manual）
        
        Returns:
            更新结果
        """
        answer_histories = AnswerHistory.objects.filter(
            user=self.user,
            course_id=course_id
        )

        # 按知识点汇总历史答题表现，生成基础掌握度基线。
        point_stats = {}  # {point_id: {'correct': 0, 'total': 0, 'name': ''}}

        for answer in answer_histories:
            point_id = answer.knowledge_point_id
            if point_id:
                if point_id not in point_stats:
                    point_stats[point_id] = {
                        'correct': 0, 
                        'total': 0,
                        'name': answer.knowledge_point.name if answer.knowledge_point else ''
                    }
                point_stats[point_id]['total'] += 1
                if answer.is_correct:
                    point_stats[point_id]['correct'] += 1

        updated_count = 0
        mastery_data = {}

        with transaction.atomic():
            for point_id, stats in point_stats.items():
                if stats['total'] > 0:
                    mastery_rate = round(stats['correct'] / stats['total'], 3)

                    KnowledgeMastery.objects.update_or_create(
                        user=self.user,
                        course_id=course_id,
                        knowledge_point_id=point_id,
                        defaults={'mastery_rate': mastery_rate}
                    )

                    mastery_data[str(point_id)] = mastery_rate
                    updated_count += 1

            ProfileHistory.objects.create(
                user=self.user,
                course_id=course_id,
                knowledge_mastery=mastery_data,
                ability_scores=self.get_ability_scores(course_id),
                habit_preferences=self.get_habit_preferences(),
                update_reason=update_reason
            )

        return {
            'course_id': course_id,
            'updated_count': updated_count,
            'knowledge_mastery': mastery_data
        }

    def get_profile_history(
        self, 
        course_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取画像变化历史
        
        Args:
            course_id: 课程ID
            limit: 返回记录数
        
        Returns:
            画像历史列表
        """
        histories = ProfileHistory.objects.filter(
            user=self.user,
            course_id=course_id
        ).order_by('-created_at')[:limit]

        return [
            {
                'id': h.id,
                'knowledge_mastery': h.knowledge_mastery,
                'ability_scores': h.ability_scores,
                'update_reason': h.update_reason,
                'created_at': h.created_at.isoformat()
            }
            for h in histories
        ]

    def check_assessment_status(self, course_id: int = None) -> Dict[str, Any]:
        """
        检查用户的初始评测完成状态
        
        对于新用户（刚注册）：需要完成能力评测和习惯问卷
        对于加入新课程：需要完成该课程的知识评测
        
        Args:
            course_id: 课程ID（可选）
        
        Returns:
            评测状态信息
        """
        has_ability = AbilityScore.objects.filter(user=self.user).exists()
        has_habit = HabitPreference.objects.filter(user=self.user).exists()
        course_statuses: List[Dict[str, Any]] = []

        result = {
            'user_id': self.user.id,
            'global_assessment_done': has_ability and has_habit,
            'ability_done': has_ability,
            'habit_done': has_habit,
            'courses': course_statuses
        }

        if course_id:
            status = AssessmentStatus.objects.filter(
                user=self.user,
                course_id=course_id
            ).first()

            course_statuses.append({
                'course_id': course_id,
                'knowledge_done': status.knowledge_done if status else False,
                'profile_generated': ProfileSummary.objects.filter(
                    user=self.user, course_id=course_id
                ).exists()
            })
        else:
            statuses = AssessmentStatus.objects.filter(user=self.user)
            for status in statuses:
                course_statuses.append({
                    'course_id': status.course_id,
                    'knowledge_done': status.knowledge_done,
                    'profile_generated': ProfileSummary.objects.filter(
                        user=self.user, course_id=status.course_id
                    ).exists()
                })

        return result

    def generate_profile_for_course(self, course_id: int, force_refresh: bool = False) -> Dict[str, Any]:
        """
        为指定课程生成/更新学习者画像
        
        集成KT服务细化掌握度预测 + LLM服务生成深度分析
        
        Args:
            course_id: 课程ID
            force_refresh: 是否强制刷新（忽略缓存）
        
        Returns:
            生成结果
        """
        from .profile_generation import generate_profile_for_course

        return generate_profile_for_course(self, course_id, force_refresh)


def get_learner_profile_service(user: User) -> LearnerProfileService:
    """
    获取学习者画像服务实例
    
    Args:
        user: 用户对象
    
    Returns:
        LearnerProfileService实例
    """
    return LearnerProfileService(user)
