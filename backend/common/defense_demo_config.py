from __future__ import annotations

DEFENSE_DEMO_MARKER = "DEFENSE_DEMO_PRESET"
DEFENSE_DEMO_TEACHER_USERNAME = "teacher"
DEFENSE_DEMO_WARMUP_STUDENT_USERNAME = "student1"
DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME = "student"
DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS: tuple[dict[str, str], ...] = (
    {
        "username": "student2",
        "email": "student2@example.com",
        "real_name": "学生2",
        "student_id": "20240002",
    },
    {
        "username": "student3",
        "email": "student3@example.com",
        "real_name": "学生3",
        "student_id": "20240003",
    },
    {
        "username": "student4",
        "email": "student4@example.com",
        "real_name": "学生4",
        "student_id": "20240004",
    },
    {
        "username": "student5",
        "email": "student5@example.com",
        "real_name": "学生5",
        "student_id": "20240005",
    },
)
DEFENSE_DEMO_SUPPORT_COURSE_NAME = "数据库原理与应用"
DEFENSE_DEMO_CLASS_NAME = "2024级大数据技术1班"
DEMO_ASSESSMENT_PRESETS: dict[str, dict[str, object]] = {
    DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME: {
        "habit_preference": {
            "preferred_resource": "video",
            "preferred_study_time": "evening",
            "study_pace": "moderate",
            "study_duration": "medium",
            "review_frequency": "weekly",
            "learning_style": "visual",
            "accept_challenge": True,
            "daily_goal_minutes": 50,
            "weekly_goal_days": 5,
            "preferences": {
                "preferred_resource": "video",
                "preferred_study_time": "evening",
                "study_pace": "moderate",
                "daily_goal_minutes": 50,
                "weekly_goal_days": 5,
                "review_frequency": "weekly",
                "learning_style": "visual",
                "accept_challenge": True,
                "difficulty_strategy": "先看解析再重试",
            },
        },
        "ability_scores": {
            "逻辑推理": 84,
            "抽象思维": 79,
            "信息整合": 81,
            "学习迁移": 76,
        },
        "profile_summary": {
            "summary": "该学生对大数据基础概念有一定掌握，但在 Hadoop 组件识别和 Spark 高级特性理解上仍存在薄弱环节。",
            "weakness": "对 HDFS 与 MapReduce 的职责区分不够清晰；RDD 惰性求值与容错机制的判断有误。",
            "suggestion": "建议沿概念 → 生态结构 → 计算模型的顺序逐步学习，着重强化 Hadoop 组件辨识和 Spark 核心抽象。",
        },
        "planned_answers": ["B", "C", "A", "C", "A", ["A", "B"]],
        "assessment_feedback": {
            "summary": "初始评测显示该学生对大数据基础概念掌握较好，但在 Hadoop 组件辨识和 Spark 高级特性上存在知识盲区。",
            "analysis": "学生在概念类题目上表现稳定，但对平台组件职责和分布式计算高级抽象的区分仍需加强。",
            "recommendations": [
                "先沿知识图谱梳理概念与组件关系。",
                "重点复习 Hadoop 组件的职责划分，区分 HDFS、YARN 与 MapReduce。",
                "结合实例理解 RDD 惰性求值与容错特性，完成阶段测试后根据掌握度变化继续补强。",
            ],
            "next_tasks": [
                "进入学习路径完成前三个学习节点。",
                "在阶段测试中验证概念迁移效果。",
            ],
            "conclusion": "基础概念掌握较好，Hadoop 生态与 Spark 高级特性是当前主要提升方向，建议分阶段针对性强化。",
        },
    },
    DEFENSE_DEMO_WARMUP_STUDENT_USERNAME: {
        "habit_preference": {
            "preferred_resource": "document",
            "preferred_study_time": "morning",
            "study_pace": "adaptive",
            "study_duration": "medium",
            "review_frequency": "spaced",
            "learning_style": "reading",
            "accept_challenge": True,
            "daily_goal_minutes": 65,
            "weekly_goal_days": 5,
            "preferences": {
                "preferred_resource": "document",
                "preferred_study_time": "morning",
                "study_pace": "adaptive",
                "daily_goal_minutes": 65,
                "weekly_goal_days": 5,
                "review_frequency": "spaced",
                "learning_style": "reading",
                "accept_challenge": True,
                "difficulty_strategy": "先梳理框架再做题验证",
            },
        },
        "ability_scores": {
            "逻辑推理": 88,
            "抽象思维": 86,
            "信息整合": 85,
            "学习迁移": 83,
        },
        "profile_summary": {
            "summary": "该学生已经建立较稳定的大数据基础认知，能够较好地串联概念、平台组件与计算模型。",
            "weakness": "对 Spark 惰性求值和执行抽象仍需通过阶段测试后的资源巩固进一步加深。",
            "suggestion": "建议继续沿学习路径完成阶段测试后的进阶节点，并结合知识图谱复盘关键依赖关系。",
        },
        "planned_answers": ["B", "C", "C", "C", "A", ["A", "B"]],
        "assessment_feedback": {
            "summary": "初始评测结果表明该学生基础较扎实，已能准确识别 Hadoop 核心组件，但在 Spark 细节理解上仍有提升空间。",
            "analysis": "学生对概念与组件题表现稳定，说明前两章知识框架已建立；Spark 多选题失分显示其对执行抽象的细节掌握还不够牢固。",
            "recommendations": [
                "优先完成 Spark 计算模型相关学习节点，再通过阶段测试验证掌握度提升。",
                "结合资源页中的资料，复盘 RDD 与 MapReduce 的差异。",
            ],
            "next_tasks": [
                "查看学习路径并完成前三个学习节点。",
                "完成阶段测试，观察掌握度变化和后续节点刷新。",
            ],
            "conclusion": "学生已经具备继续推进阶段测试和进阶学习的基础，适合作为答辩演示中的预热账号。",
        },
    },
}


# 维护意图：获取演示账号的评测与画像预置。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _get_demo_assessment_preset(username: str) -> dict[str, object]:
    """
    获取演示账号的评测与画像预置。
    :param username: 演示账号用户名。
    :return: 评测预置字典；未知账号回退到主演示学生配置。
    """
    preset = DEMO_ASSESSMENT_PRESETS.get(username)
    if isinstance(preset, dict):
        return preset
    return DEMO_ASSESSMENT_PRESETS[DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME]
