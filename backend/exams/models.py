"""
考试模块 - 数据模型
包含考试、提交记录和反馈报告相关的模型

Exam: 考试/测验定义
ExamQuestion: 考试与题目的关联
ExamSubmission: 考试提交记录
FeedbackReport: 考试反馈报告
"""

from django.conf import settings
from django.db import models


# 维护意图：考试/测验模型 支持多种考试类型： - 章节测验：对应某个章节的小测 - 期中/期末考试：大型阶段性考试 - 练习：日常练习 - 节点测验：学习路径节点的过关测试
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Exam(models.Model):
    """
    考试/测验模型

    支持多种考试类型：
    - 章节测验：对应某个章节的小测
    - 期中/期末考试：大型阶段性考试
    - 练习：日常练习
    - 节点测验：学习路径节点的过关测试
    """

    EXAM_TYPES = [
        ('chapter', '章节测验'),
        ('midterm', '期中考试'),
        ('final', '期末考试'),
        ('practice', '练习'),
        ('node_test', '节点测验'),
        ('question_set', '套题'),
    ]

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('closed', '已结束'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name='所属课程',
    )
    title = models.CharField('考试标题', max_length=200)
    description = models.TextField('考试说明', blank=True, null=True)
    exam_type = models.CharField(
        '考试类型',
        max_length=20,
        choices=EXAM_TYPES,
        default='practice',
    )
    questions = models.ManyToManyField(
        'assessments.Question',
        through='ExamQuestion',
        related_name='exams',
        verbose_name='题目',
    )
    total_score = models.DecimalField('总分', max_digits=5, decimal_places=2, default=100)
    pass_score = models.DecimalField('及格分', max_digits=5, decimal_places=2, default=60)
    duration = models.IntegerField('考试时长(分钟)', null=True, blank=True, help_text='不设置表示不限时')
    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    target_class = models.ForeignKey(
        'courses.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exams',
        verbose_name='目标班级',
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='published',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_exams',
        verbose_name='创建者',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = 'exams'
        verbose_name = '考试'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    # 维护意图：获取题目数量
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def question_count(self):
        """获取题目数量"""
        return self.questions.count()


# 维护意图：考试-题目关联模型 关联考试和题目，支持自定义分值和排序
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamQuestion(models.Model):
    """
    考试-题目关联模型

    关联考试和题目，支持自定义分值和排序
    """

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey('assessments.Question', on_delete=models.CASCADE)
    score = models.DecimalField('分值', max_digits=5, decimal_places=2, default=1)
    order = models.IntegerField('排序', default=0)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = 'exam_questions'
        ordering = ['order']


# 维护意图：考试提交记录模型 存储学生的考试答案和成绩
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamSubmission(models.Model):
    """
    考试提交记录模型

    存储学生的考试答案和成绩
    """

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='考试',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_submissions',
        verbose_name='学生',
    )
    answers = models.JSONField('答案', default=dict, help_text='格式: {question_id: answer, ...}')
    score = models.DecimalField('得分', max_digits=5, decimal_places=2, null=True, blank=True)
    is_passed = models.BooleanField('是否通过', null=True, blank=True)
    graded_at = models.DateTimeField('评分时间', null=True, blank=True)
    submitted_at = models.DateTimeField('提交时间', auto_now_add=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = 'exam_submissions'
        verbose_name = '考试提交'
        verbose_name_plural = verbose_name
        unique_together = ['exam', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"

    # 维护意图：获取得分百分比
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def score_percent(self):
        """获取得分百分比"""
        if self.score is not None and self.exam.total_score > 0:
            return round(float(self.score) / float(self.exam.total_score) * 100, 1)
        return None


# 维护意图：反馈报告模型 存储AI生成的考试反馈报告，包含： - 成绩概览 - 错因分析 - 学习建议 - 下一步任务
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class FeedbackReport(models.Model):
    """
    反馈报告模型

    存储AI生成的考试反馈报告，包含：
    - 成绩概览
    - 错因分析
    - 学习建议
    - 下一步任务
    """

    STATUS_CHOICES = [
        ('pending', '生成中'),
        ('completed', '已完成'),
        ('failed', '生成失败'),
    ]

    SOURCE_CHOICES = [
        ('exam', '考试'),
        ('assessment', '初始评测'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedback_reports',
        verbose_name='用户',
    )
    source = models.CharField('来源', max_length=20, choices=SOURCE_CHOICES, default='exam')
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='feedback_reports',
        verbose_name='考试',
        null=True,
        blank=True,
    )
    exam_submission = models.ForeignKey(
        ExamSubmission,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedback_reports',
        verbose_name='提交记录',
    )
    assessment_result = models.ForeignKey(
        'assessments.AssessmentResult',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedback_reports',
        verbose_name='评测结果',
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    overview = models.JSONField('概览', default=dict, help_text='成绩概览信息')
    analysis = models.JSONField('错因分析', default=list, help_text='每道错题的分析')
    recommendations = models.JSONField('建议', default=list)
    next_tasks = models.JSONField('下一步任务', default=list)
    conclusion = models.TextField('总结', blank=True, null=True)
    generated_at = models.DateTimeField('生成时间', auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = 'feedback_reports'
        verbose_name = '反馈报告'
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.exam:
            return f"{self.user.username} - {self.exam.title} 反馈"
        return f"{self.user.username} - 初始评测反馈"
