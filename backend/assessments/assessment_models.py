"""测评模块 - 测评定义、结果与能力评分模型。"""

from django.conf import settings
from django.db import models

from .question_models import Question


class Assessment(models.Model):
    """测评模型。"""

    ASSESSMENT_TYPES = [
        ('knowledge', '知识掌握度测评'),
        ('ability', '学习能力评估'),
        ('habit', '学习习惯问卷'),
    ]

    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assessments', verbose_name='所属课程')
    title = models.CharField('测评标题', max_length=200)
    assessment_type = models.CharField('测评类型', max_length=20, choices=ASSESSMENT_TYPES)
    description = models.TextField('描述', blank=True, null=True)
    questions = models.ManyToManyField(Question, through='AssessmentQuestion', related_name='assessments', verbose_name='题目')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'assessments'
        verbose_name = '测评'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class AssessmentQuestion(models.Model):
    """测评-题目关联模型。"""

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField('排序', default=0)

    class Meta:
        db_table = 'assessment_questions'
        ordering = ['order']


class AssessmentResult(models.Model):
    """测评结果模型。"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_results', verbose_name='用户')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assessment_results', verbose_name='课程')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='results', verbose_name='测评')
    answers = models.JSONField('答案', default=dict, help_text='格式: {question_id: answer, ...}')
    score = models.DecimalField('得分', max_digits=5, decimal_places=2, null=True, blank=True)
    result_data = models.JSONField('结果数据', default=dict)
    completed_at = models.DateTimeField('完成时间', auto_now_add=True)

    class Meta:
        db_table = 'assessment_results'
        verbose_name = '测评结果'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'assessment']

    def __str__(self):
        return f"{self.user.username} - {self.assessment.title}"


class AssessmentStatus(models.Model):
    """测评状态模型。"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_status', verbose_name='用户')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assessment_status', verbose_name='课程')
    knowledge_done = models.BooleanField('知识测评完成', default=False)
    ability_done = models.BooleanField('能力测评完成', default=False)
    habit_done = models.BooleanField('习惯问卷完成', default=False)
    generating = models.BooleanField('正在生成中', default=False)
    generation_error = models.TextField('生成错误信息', null=True, blank=True)

    class Meta:
        db_table = 'assessment_status'
        verbose_name = '测评状态'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} 测评状态"

    @property
    def is_all_done(self):
        """判断是否全部完成。"""
        return self.knowledge_done and self.ability_done and self.habit_done


class AbilityScore(models.Model):
    """能力评分模型。"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ability_scores', verbose_name='用户')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='ability_scores', verbose_name='课程')
    scores = models.JSONField('能力维度得分', default=dict, help_text='格式: {"逻辑推理": 85, "抽象思维": 72, ...}')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'ability_scores'
        verbose_name = '能力评分'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} 能力评分"
