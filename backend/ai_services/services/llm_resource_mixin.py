from __future__ import annotations

from typing import Any, Dict, List, Optional

from ai_services.services.llm_resource_support import (
    build_external_resources_prompt,
    build_internal_resources_prompt,
    build_stage_question_prompt,
    normalize_external_resource_result,
    normalize_internal_resource_result,
)

class LLMResourceMixin:
    """内部/外部学习资源推荐与阶段测试选题能力。"""

    def recommend_external_resources(
        self,
        point_name: str,
        student_mastery: float = None,
        existing_titles: List[str] = None,
        course_name: str = None,
        search_results: List[Dict[str, Any]] = None,
        count: int = 3,
    ) -> Dict[str, Any]:
        """
        根据知识点和学生掌握度，推荐外部学习资源（网站、视频、文章等）

        Args:
            point_name: 知识点名称
            student_mastery: 学生掌握度 0-1
            existing_titles: 已有内部资源标题列表（避免重复）
            course_name: 所属课程名称（提供领域上下文）
            count: 推荐数量（最少返回数）

        Returns:
            包含 resources 列表的字典
        """
        _ = search_results
        prompt, _, fallback_resources = build_external_resources_prompt(
            point_name=point_name,
            student_mastery=student_mastery,
            existing_titles=existing_titles,
            course_name=course_name,
            count=count,
        )
        fallback = {"resources": fallback_resources}

        result = self._call_with_fallback(
            prompt,
            "external_resources",
            fallback,
            temperature=0.7,
            extra_body_overrides={"enable_search": True},
        )
        return normalize_external_resource_result(
            result=result,
            fallback_resources=fallback_resources,
            point_name=point_name,
            count=count,
        )

    def recommend_internal_resources(
        self,
        point_name: str,
        student_mastery: float = None,
        available_resources: List[Dict] = None,
        course_name: str = None,
        count: int = 2,
    ) -> Dict[str, Any]:
        """
        从课程内部资源库中，由LLM选出最匹配当前知识点和学生掌握度的资源

        Args:
            point_name: 知识点名称
            student_mastery: 学生掌握度 0-1
            available_resources: 候选内部资源列表 [{'id','title','type','description','chapter'}]
            course_name: 课程名称
            count: 推荐数量（最少返回数）

        Returns:
            {'resources': [{'id': int, 'reason': str, 'learning_tips': str}]}
        """
        if not available_resources:
            return {"resources": []}
        prompt, _, fallback = build_internal_resources_prompt(
            point_name=point_name,
            student_mastery=student_mastery,
            available_resources=available_resources,
            course_name=course_name,
            count=count,
        )
        result = self._call_with_fallback(
            prompt, "internal_resources", fallback, temperature=0.3
        )
        return normalize_internal_resource_result(result, fallback)

    def select_stage_test_questions(
        self, candidates: List[Dict], kp_names: List[str], count: int = 10
    ) -> Optional[List[int]]:
        """
        LLM智能选择阶段测试题目

        从候选题目中挑选最能检验知识点掌握程度的题目。

        Args:
            candidates: 候选题目列表 [{'id': int, 'content': str, 'type': str, 'difficulty': str}]
            kp_names: 本次测试涉及的知识点名称列表
            count: 需要选出的题目数量

        Returns:
            选中题目的ID列表，失败时返回None
        """
        if not candidates:
            return None
        prompt, fallback = build_stage_question_prompt(
            candidates=candidates,
            kp_names=kp_names,
            count=count,
        )

        result = self._call_with_fallback(
            prompt, "question_selection", fallback, temperature=0.2
        )
        ids = result.get("selected_ids")
        if isinstance(ids, list) and ids:
            return [int(i) for i in ids]
        return None
