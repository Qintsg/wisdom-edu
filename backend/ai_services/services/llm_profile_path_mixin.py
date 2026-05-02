from __future__ import annotations

from typing import Any, Dict, List

from ai_services.services.llm_profile_path_support import (
    build_path_fallback,
    build_path_prompt,
    build_profile_fallback,
    build_profile_prompt,
    build_resource_reason_fallback,
    build_resource_reason_prompt,
    identify_strengths,
    identify_weaknesses,
)


class LLMProfilePathMixin:
    """学习画像、路径规划与资源理由生成能力。"""

    def analyze_profile(
        self,
        mastery_data: List[Dict],
        ability_data: Dict = None,
        habit_data: Dict = None,
        course_name: str = None,
        grade_level: str = None,
        kt_predictions: Dict = None,
    ) -> Dict[str, Any]:
        """
        分析学习者画像

        Args:
            mastery_data: 知识掌握度数据列表
            ability_data: 能力评分数据
            habit_data: 学习习惯数据
            course_name: 课程名称（可选，用于生成学科针对性建议）
            grade_level: 学段/年级（可选）
            kt_predictions: KT模型预测的知识点掌握度 {kp_name: mastery_rate}

        Returns:
            画像分析结果，包含summary, weakness, strength, suggestion
        """
        prompt = build_profile_prompt(
            mastery_data=mastery_data,
            ability_data=ability_data,
            habit_data=habit_data,
            course_name=course_name,
            grade_level=grade_level,
            kt_predictions=kt_predictions,
        )
        fallback = build_profile_fallback(mastery_data)
        return self._call_with_fallback(prompt, "profile_analysis", fallback)

    def plan_learning_path(
        self,
        mastery_data: List[Dict],
        target: str = None,
        constraints: Dict = None,
        course_name: str = None,
        max_nodes: int = None,
    ) -> Dict[str, Any]:
        """
        规划学习路径

        Args:
            mastery_data: 知识掌握度数据
            target: 学习目标
            constraints: 约束条件
            course_name: 课程名称（可选，提供领域上下文）
            max_nodes: 最大节点数（可选，默认从配置读取）

        Returns:
            路径规划结果
        """
        if max_nodes is None:
            from common.config import AppConfig

            max_nodes = AppConfig.max_path_nodes()

        prompt = build_path_prompt(
            mastery_data=mastery_data,
            target=target,
            constraints=constraints,
            course_name=course_name,
            max_nodes=max_nodes,
        )
        fallback = build_path_fallback(mastery_data)
        return self._call_with_fallback(prompt, "path_planning", fallback)

    def generate_resource_reason(
        self,
        resource_info: Dict,
        student_mastery: float = None,
        point_name: str = None,
        course_name: str = None,
    ) -> Dict[str, Any]:
        """
        生成资源推荐理由

        Args:
            resource_info: 资源信息
            student_mastery: 学生对相关知识点的掌握度
            point_name: 知识点名称
            course_name: 课程名称（可选，提供领域上下文）

        Returns:
            推荐理由
        """
        prompt = build_resource_reason_prompt(
            resource_info=resource_info,
            student_mastery=student_mastery,
            point_name=point_name,
            course_name=course_name,
        )
        fallback = build_resource_reason_fallback(
            resource_info=resource_info,
            student_mastery=student_mastery,
            point_name=point_name,
        )
        return self._call_with_fallback(
            prompt, "resource_reason", fallback, temperature=0.5
        )

    @staticmethod
    def _identify_weakness(mastery_data: List[Dict]) -> List[str]:
        """识别薄弱知识点"""
        return identify_weaknesses(mastery_data)

    @staticmethod
    def _identify_strength(mastery_data: List[Dict]) -> List[str]:
        """识别优势知识点"""
        return identify_strengths(mastery_data)
