"""测评模块 - 题库与问卷题目模型。"""

from django.conf import settings
from django.db import models


# 维护意图：题库题目模型
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Question(models.Model):
    """题库题目模型。"""

    QUESTION_TYPES = [
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('true_false', '判断题'),
        ('fill_blank', '填空题'),
        ('short_answer', '简答题'),
        ('code', '编程题'),
    ]
    DIFFICULTY_CHOICES = [('easy', '简单'), ('medium', '中等'), ('hard', '困难')]

    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='questions', verbose_name='所属课程')
    chapter = models.CharField('所属章节', max_length=200, blank=True, null=True, help_text='题目所属的章节或目录信息')
    content = models.TextField('题目内容', help_text='题目的完整描述')
    question_type = models.CharField('题目类型', max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField('选项', default=list, blank=True, help_text='格式: [{"label": "A", "content": "选项内容"}, ...]')
    answer = models.JSONField('正确答案', default=dict, help_text='格式: {"answer": "A"} 或 {"answers": ["A", "B"]}')
    analysis = models.TextField('解析', blank=True, null=True, help_text='题目的详细解析')
    knowledge_points = models.ManyToManyField('knowledge.KnowledgePoint', blank=True, related_name='questions', verbose_name='关联知识点')
    difficulty = models.CharField('难度', max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    score = models.DecimalField('默认分值', max_digits=5, decimal_places=2, default=1)
    suggested_score = models.DecimalField('建议分数', max_digits=5, decimal_places=2, blank=True, null=True, help_text='从试卷导入时的建议分数')
    is_visible = models.BooleanField('对学生可见', default=True, help_text='是否在题库中对学生可见')
    for_initial_assessment = models.BooleanField('用于初始评测', default=False, help_text='是否可用于初始评测随机抽题')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_questions', verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = 'questions'
        verbose_name = '题目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.content[:50]}..."


# 维护意图：问卷题目模型
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class SurveyQuestion(models.Model):
    """问卷题目模型。"""

    QUESTION_TYPES = [('single_select', '单选'), ('multi_select', '多选'), ('scale', '量表'), ('text', '文本')]
    SURVEY_TYPES = [('ability', '智力量表'), ('habit', '学习偏好问卷')]

    survey_type = models.CharField('问卷类型', max_length=20, choices=SURVEY_TYPES, default='habit')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True, related_name='survey_questions', verbose_name='所属课程')
    text = models.TextField('题目文本', help_text='问卷题目的完整描述')
    question_type = models.CharField('题目类型', max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField('选项', default=list, help_text='格式: [{"value": "A", "label": "选项文本", "score": 1}, ...]')
    dimension = models.CharField('能力维度', max_length=50, blank=True, null=True, help_text='该题测量的能力维度，如"逻辑推理"、"抽象思维"等')
    order = models.IntegerField('排序', default=0)
    is_global = models.BooleanField('全局通用', default=True, help_text='全局通用的题目适用于所有课程')
    is_required = models.BooleanField('是否必答', default=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = 'survey_questions'
        verbose_name = '问卷题目'
        verbose_name_plural = verbose_name
        ordering = ['survey_type', 'order']

    def __str__(self):
        return f"{self.get_survey_type_display()}: {self.text[:50]}..."
