"""测评模块 - 答题历史、画像历史与问卷结果模型。"""

from django.conf import settings
from django.db import models

from .question_models import Question


class AnswerHistory(models.Model):
    """学生答题历史记录模型。"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answer_histories', verbose_name='用户')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='answer_histories', verbose_name='课程')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_histories', verbose_name='题目')
    knowledge_point = models.ForeignKey('knowledge.KnowledgePoint', on_delete=models.SET_NULL, null=True, blank=True, related_name='answer_histories', verbose_name='知识点')
    student_answer = models.JSONField('学生答案', default=dict)
    correct_answer = models.JSONField('正确答案', default=dict)
    is_correct = models.BooleanField('是否正确', default=False)
    score = models.DecimalField('得分', max_digits=5, decimal_places=2, default=0)
    source = models.CharField('来源', max_length=50, default='practice', help_text='答题来源：initial（初始评测）, exam（考试）, practice（练习）')
    exam_id = models.IntegerField('考试ID', null=True, blank=True)
    answered_at = models.DateTimeField('答题时间', auto_now_add=True)

    class Meta:
        db_table = 'answer_histories'
        verbose_name = '答题历史'
        verbose_name_plural = verbose_name
        ordering = ['-answered_at']

    def __str__(self):
        status = '正确' if self.is_correct else '错误'
        return f"{self.user.username} - {self.question.id} - {status}"


class ProfileHistory(models.Model):
    """学生画像历史记录模型。"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_histories', verbose_name='用户')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='profile_histories', verbose_name='课程')
    knowledge_mastery = models.JSONField('知识掌握度', default=dict, help_text='格式: {"知识点ID": 掌握度, ...}')
    ability_scores = models.JSONField('能力得分', default=dict, help_text='格式: {"能力维度": 得分, ...}')
    habit_preferences = models.JSONField('学习偏好', default=dict)
    summary = models.TextField('画像摘要', blank=True, null=True)
    update_reason = models.CharField('更新原因', max_length=100, default='manual', help_text='更新原因：initial（初始评测）, exam（考试完成）, manual（手动更新）')
    external_mastery = models.JSONField('外部掌握情况', default=dict, null=True, blank=True, help_text='预留字段：外部接口返回的掌握情况分析')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'profile_histories'
        verbose_name = '画像历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} - {self.created_at}"


class SurveyResult(models.Model):
    """问卷结果模型。"""

    SURVEY_TYPES = [('ability', '智力量表'), ('habit', '学习偏好问卷')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey_results', verbose_name='用户')
    survey_type = models.CharField('问卷类型', max_length=20, choices=SURVEY_TYPES)
    answers = models.JSONField('答案', default=dict, help_text='格式: {question_id: answer, ...}')
    result = models.JSONField('结果', default=dict, help_text='根据答案计算出的结果，如能力得分或偏好设置')
    version = models.IntegerField('版本号', default=1)
    is_current = models.BooleanField('是否当前版本', default=True)
    completed_at = models.DateTimeField('完成时间', auto_now_add=True)

    class Meta:
        db_table = 'survey_results'
        verbose_name = '问卷结果'
        verbose_name_plural = verbose_name
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_survey_type_display()} v{self.version}"
