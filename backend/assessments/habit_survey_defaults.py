"""学习习惯问卷的内置默认题目。"""

from __future__ import annotations


DEFAULT_HABIT_QUESTIONS: tuple[dict[str, object], ...] = (
    {
        "text": "你更喜欢通过哪种形式获取新知识？",
        "question_type": "single_select",
        "options": [
            {"value": "video", "label": "观看教学视频"},
            {"value": "document", "label": "阅读文字资料"},
            {"value": "exercise", "label": "通过练习题实践"},
            {"value": "mixed", "label": "多种形式混合学习"},
        ],
        "order": 1,
    },
    {
        "text": "通常哪段时间你的学习效率最高？",
        "question_type": "single_select",
        "options": [
            {"value": "morning", "label": "早上（6:00-12:00）"},
            {"value": "afternoon", "label": "下午（12:00-18:00）"},
            {"value": "evening", "label": "晚上（18:00-22:00）"},
            {"value": "night", "label": "深夜（22:00以后）"},
        ],
        "order": 2,
    },
    {
        "text": "你希望的学习节奏是怎样的？",
        "question_type": "single_select",
        "options": [
            {"value": "fast", "label": "快节奏：快速推进，挑战高难度"},
            {"value": "moderate", "label": "正常节奏：稳步推进"},
            {"value": "slow", "label": "慢节奏：仔细理解每个知识点"},
        ],
        "order": 3,
    },
    {
        "text": "你每天计划花多少时间学习这门课程？",
        "question_type": "single_select",
        "options": [
            {"value": "30", "label": "约30分钟"},
            {"value": "60", "label": "约1小时"},
            {"value": "90", "label": "约1.5小时"},
            {"value": "120", "label": "2小时以上"},
        ],
        "order": 4,
    },
    {
        "text": "你希望每周学习几天？",
        "question_type": "single_select",
        "options": [
            {"value": "3", "label": "3天"},
            {"value": "5", "label": "5天"},
            {"value": "7", "label": "每天都学"},
        ],
        "order": 5,
    },
    {
        "text": "你倾向于哪种复习频率？",
        "question_type": "single_select",
        "options": [
            {"value": "daily", "label": "每天复习当天内容"},
            {"value": "weekly", "label": "每周末集中复习"},
            {"value": "before_exam", "label": "考前集中复习"},
            {"value": "spaced", "label": "按记忆曲线间隔复习"},
        ],
        "order": 6,
    },
    {
        "text": "你的学习风格更偏向哪种？",
        "question_type": "single_select",
        "options": [
            {"value": "visual", "label": "视觉型：喜欢图表、思维导图"},
            {"value": "auditory", "label": "听觉型：喜欢听讲解"},
            {"value": "reading", "label": "阅读型：喜欢查阅文本资料"},
            {"value": "kinesthetic", "label": "动手型：喜欢实验和实操"},
        ],
        "order": 7,
    },
    {
        "text": "你喜欢接受有挑战性的学习任务吗？",
        "question_type": "single_select",
        "options": [
            {"value": "yes", "label": "喜欢，越有挑战越有动力"},
            {"value": "moderate", "label": "适度挑战，太难会焦虑"},
            {"value": "no", "label": "不太喜欢，更愿循序渐进"},
        ],
        "order": 8,
    },
    {
        "text": "遇到学习困难时，你更倾向于怎么做？",
        "question_type": "single_select",
        "options": [
            {"value": "self", "label": "自己查资料解决"},
            {"value": "ai", "label": "使用AI工具辅助"},
            {"value": "peer", "label": "与同学讨论"},
            {"value": "teacher", "label": "向老师请教"},
        ],
        "order": 9,
    },
)
