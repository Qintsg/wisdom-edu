"""知识点服务。"""

from __future__ import annotations

from typing import TypedDict

from django.utils import timezone

from ai_services.services import llm_service

from .models import KnowledgePoint


# 维护意图：知识点简介载荷
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgePointIntro(TypedDict):
    """知识点简介载荷。"""

    introduction: str
    key_concepts: list[str]
    learning_tips: str
    difficulty: str
    sources: list[str]


# 维护意图：为知识点生成稳定兜底简介
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_intro_fallback(point: KnowledgePoint) -> KnowledgePointIntro:
    """为知识点生成稳定兜底简介。"""

    point_name = point.name.strip() or "当前知识点"
    course_name = point.course.name if point.course_id and point.course else "当前课程"
    return {
        "introduction": f"{point_name} 是 {course_name} 中的重要知识点，建议先理解核心定义，再结合资源与练习完成巩固。",
        "key_concepts": [point_name],
        "learning_tips": "先梳理知识图谱中的上下游关系，再完成对应学习资源和练习。",
        "difficulty": "medium",
        "sources": [point_name],
    }


# 维护意图：获取知识点简介，缺失时再调用模型生成并写回数据库
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_or_generate_point_intro(point: KnowledgePoint) -> KnowledgePointIntro:
    """获取知识点简介，缺失时再调用模型生成并写回数据库。"""

    cached_intro = (point.introduction or "").strip()
    if cached_intro:
        return {
            "introduction": cached_intro,
            "key_concepts": [point.name],
            "learning_tips": "结合当前学习路径中的资源继续巩固该知识点。",
            "difficulty": "medium",
            "sources": [point.name],
        }

    fallback = build_intro_fallback(point)
    prompt = f"""请为以下知识点生成一个简短的学习介绍。

课程：{point.course.name if point.course_id and point.course else "未指定"}
知识点：{point.name}
描述：{point.description or "暂无补充描述"}

请按以下 JSON 格式输出：
{{
    \"introduction\": \"知识点简介（2-3句话，通俗易懂）\",
    \"key_concepts\": [\"核心概念1\", \"核心概念2\", \"核心概念3\"],
    \"learning_tips\": \"学习建议（1-2句话）\",
    \"difficulty\": \"easy/medium/hard\",
    \"sources\": [\"知识点名称\"]
}}"""

    result = llm_service.call_with_fallback(
        prompt=prompt,
        call_type="node_intro",
        fallback_response=fallback,
    )
    introduction = str(result.get("introduction") or fallback["introduction"]).strip()
    point.introduction = introduction
    point.introduction_generated_at = timezone.now()
    point.save(
        update_fields=["introduction", "introduction_generated_at", "updated_at"]
    )

    key_concepts = result.get("key_concepts")
    normalized_key_concepts = [
        str(item).strip()
        for item in (key_concepts if isinstance(key_concepts, list) else [point.name])
        if str(item).strip()
    ]
    sources = result.get("sources")
    normalized_sources = [
        str(item).strip()
        for item in (sources if isinstance(sources, list) else [point.name])
        if str(item).strip()
    ]
    return {
        "introduction": introduction,
        "key_concepts": normalized_key_concepts or [point.name],
        "learning_tips": str(
            result.get("learning_tips") or fallback["learning_tips"]
        ).strip(),
        "difficulty": str(result.get("difficulty") or fallback["difficulty"]).strip()
        or "medium",
        "sources": normalized_sources or [point.name],
    }
