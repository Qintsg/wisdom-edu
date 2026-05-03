from __future__ import annotations

from typing import Any

from ai_services.services.llm_profile_path_support import resolve_learning_stage


# 维护意图：构造外部资源推荐 prompt 与降级模板
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_external_resources_prompt(
    *,
    point_name: str,
    student_mastery: float | None,
    existing_titles: list[str] | None,
    course_name: str | None,
    count: int,
) -> tuple[str, str, list[dict[str, Any]]]:
    """构造外部资源推荐 prompt 与降级模板。"""
    stage, _ = resolve_learning_stage(student_mastery)
    existing_text = ""
    if existing_titles:
        existing_text = f"\n已有课内资源（请勿推荐相同内容）：{', '.join(existing_titles[:5])}"
    course_context = f"所属课程：{course_name}\n" if course_name else ""
    prompt = f"""# 任务
请直接使用 DeepSeek / 当前模型提供方的原生联网搜索能力，为正在学习「{point_name}」的学生推荐 {count} 个优质外部学习资源。

# 学生信息
- 知识点：{point_name}
- 掌握度：{f"{student_mastery * 100:.0f}%" if student_mastery is not None else "未评测"}
- 学习阶段：{stage}
{course_context}{existing_text}

# 重要要求
1. 必须由模型直接联网获取真实存在、可正常访问的资源 URL，禁止使用后端预检索候选列表
2. 资源难度应匹配学生当前{stage}阶段
3. 至少返回 {count} 个资源
4. 优先推荐以下知名平台的资源：
   - 视频类：B站(bilibili.com)、中国大学MOOC(icourse163.com)、网易公开课
   - 文档类：菜鸟教程(runoob.com)、W3Cschool、官方技术文档
   - 英文经典：Coursera、Khan Academy、官方文档(如Apache/Spark官网)
5. 每个资源需说明推荐理由，理由要具体到知识点内容
6. URL格式要完整（以 http:// 或 https:// 开头）
7. 不要返回搜索结果页 URL，优先返回具体课程、视频、文章或文档页面

# JSON输出格式
{{
    "resources": [
        {{
            "title": "资源标题（准确描述资源内容）",
            "url": "完整的资源URL",
            "type": "video/document/link/exercise",
            "reason": "推荐理由，说明与知识点的关联（30-50字）"
        }}
    ]
}}"""
    search_keyword = point_name.replace(" ", "+")
    fallback_templates = [
        {
            "title": f"{point_name} - B站视频教程",
            "url": f"https://search.bilibili.com/all?keyword={search_keyword}",
            "type": "video",
        },
        {
            "title": f"{point_name} - 中国大学MOOC",
            "url": f"https://www.icourse163.org/search.htm?search={search_keyword}",
            "type": "video",
        },
        {
            "title": f"{point_name} - 菜鸟教程",
            "url": "https://www.runoob.com/",
            "type": "document",
        },
    ]
    fallback_resources = [
        {**template, "reason": f"该平台有丰富的{point_name}学习内容，适合{stage}阶段。"}
        for template in fallback_templates[:count]
    ]
    return prompt, stage, fallback_resources


# 维护意图：规整外部资源返回并补足最少条数
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_external_resource_result(
    *,
    result: dict[str, Any],
    fallback_resources: list[dict[str, Any]],
    point_name: str,
    count: int,
) -> dict[str, Any]:
    """规整外部资源返回并补足最少条数。"""
    normalized = result if isinstance(result.get("resources"), list) else {"resources": list(fallback_resources)}
    normalized["resources"] = [item for item in normalized["resources"] if item.get("url")]
    if len(normalized["resources"]) < count:
        used_urls = {item.get("url") for item in normalized["resources"]}
        for fallback_item in fallback_resources:
            if fallback_item["url"] in used_urls:
                continue
            normalized["resources"].append(
                {**fallback_item, "reason": f"推荐学习{point_name}相关内容。"}
            )
            if len(normalized["resources"]) >= count:
                break
    return normalized


# 维护意图：构造内部资源推荐 prompt 与降级返回
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_internal_resources_prompt(
    *,
    point_name: str,
    student_mastery: float | None,
    available_resources: list[dict[str, Any]],
    course_name: str | None,
    count: int,
) -> tuple[str, str, dict[str, Any]]:
    """构造内部资源推荐 prompt 与降级返回。"""
    stage, _ = resolve_learning_stage(student_mastery)
    candidate_text = "\n".join(
        [
            f"  - ID:{item['id']} | 类型:{item.get('type', '未知')} | 标题:{item.get('title', '无标题')} | 描述:{item.get('description', '')[:60]} | 章节:{item.get('chapter', '')}"
            for item in available_resources[:40]
        ]
    )
    course_context = f"所属课程：{course_name}\n" if course_name else ""
    prompt = f"""# 任务
从课程内部资源库中，选出最适合学生当前学习状态的 {count} 个学习资源。

# 学生信息
- 正在学习的知识点：{point_name}
- 当前掌握度：{f"{student_mastery * 100:.0f}%" if student_mastery is not None else "未评测"}
- 学习阶段：{stage}
{course_context}
# 候选内部资源
{candidate_text}

# 选择原则
1. 优先选择与知识点「{point_name}」内容最相关的资源
2. 资源类型多样化（如PPT+视频组合优于两个PPT）
3. 难度匹配学生当前{stage}阶段（入门选基础、精通选进阶）
4. 至少选出 {count} 个资源，如果高度相关的不足则放宽相关性
5. 每种资源类型（PPT/视频/电子教材）最多选1个

# JSON输出格式
{{
    "resources": [
        {{
            "id": "<int, 选中资源的ID>",
            "reason": "推荐理由（30-50字，说明该资源与知识点的关联性）",
            "learning_tips": "使用该资源的学习建议（20-40字）"
        }}
    ]
}}"""
    fallback_resources: list[dict[str, Any]] = []
    for resource in available_resources:
        title = resource.get("title", "")
        if point_name in title or any(keyword in title for keyword in point_name.split("与")):
            fallback_resources.append(
                {
                    "id": resource["id"],
                    "reason": f"该资源与「{point_name}」相关，适合{stage}阶段学习。",
                    "learning_tips": "建议结合笔记进行学习。",
                }
            )
        if len(fallback_resources) >= count:
            break
    if len(fallback_resources) < count:
        used_ids = {resource["id"] for resource in fallback_resources}
        for resource in available_resources:
            if resource["id"] in used_ids:
                continue
            fallback_resources.append(
                {
                    "id": resource["id"],
                    "reason": f"推荐学习此{resource.get('type', '资源')}以加深理解。",
                    "learning_tips": "建议配合其他资源一起学习。",
                }
            )
            if len(fallback_resources) >= count:
                break
    return prompt, stage, {"resources": fallback_resources}


# 维护意图：规整内部资源推荐结果
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_internal_resource_result(
    result: dict[str, Any],
    fallback: dict[str, Any],
) -> dict[str, Any]:
    """规整内部资源推荐结果。"""
    return result if isinstance(result.get("resources"), list) else fallback


# 维护意图：构造阶段测试选题 prompt 与默认回退
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_stage_question_prompt(
    *,
    candidates: list[dict[str, Any]],
    kp_names: list[str],
    count: int,
) -> tuple[str, dict[str, Any]]:
    """构造阶段测试选题 prompt 与默认回退。"""
    candidate_text = "\n".join(
        [
            f"  - ID:{item['id']} | 类型:{item['type']} | 难度:{item['difficulty']} | 题干:{item['content']}"
            for item in candidates[:30]
        ]
    )
    prompt = f"""# 任务
从以下候选题目中选出最适合用于阶段测试的 {count} 道题目。

# 测试覆盖的知识点
{", ".join(kp_names)}

# 候选题目
{candidate_text}

# 选题原则
1. 覆盖尽可能多的知识点
2. 难度均衡分布（易/中/难合理搭配）
3. 题型多样化（单选/多选/判断搭配）
4. 避免重复或相似的题目

# JSON输出格式
{{
    "selected_ids": [所选题目的ID列表，整数数组],
    "reason": "选题理由简述（30字以内）"
}}"""
    fallback = {
        "selected_ids": [item["id"] for item in candidates[:count]],
        "reason": "按默认顺序选取",
    }
    return prompt, fallback
