"""
测评模块 - 数据模型
包含测评、题目和能力评分相关的模型

Question: 题库题目
SurveyQuestion: 问卷题目（能力测评、习惯问卷）
Assessment: 测评定义
AssessmentQuestion: 测评与题目的关联
AssessmentResult: 测评结果
AssessmentStatus: 测评完成状态
AbilityScore: 能力评分
"""
from django.db import models
from django.conf import settings


class Question(models.Model):
    """
    题库题目模型
    
    支持多种题型：
    - 单选题、多选题
    - 判断题
    - 填空题
    - 简答题
    - 编程题
    
    功能：
    - 是否对学生可见
    - 是否用于初始评测
    - 关联知识点
    """
    QUESTION_TYPES = [
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('true_false', '判断题'),
        ('fill_blank', '填空题'),
        ('short_answer', '简答题'),
        ('code', '编程题'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='所属课程'
    )
    chapter = models.CharField(
        '所属章节',
        max_length=200,
        blank=True,
        null=True,
        help_text='题目所属的章节或目录信息'
    )
    content = models.TextField(
        '题目内容',
        help_text='题目的完整描述'
    )
    question_type = models.CharField(
        '题目类型',
        max_length=20,
        choices=QUESTION_TYPES
    )
    options = models.JSONField(
        '选项',
        default=list,
        blank=True,
        help_text='格式: [{"label": "A", "content": "选项内容"}, ...]'
    )
    answer = models.JSONField(
        '正确答案',
        default=dict,
        help_text='格式: {"answer": "A"} 或 {"answers": ["A", "B"]}'
    )
    analysis = models.TextField(
        '解析',
        blank=True,
        null=True,
        help_text='题目的详细解析'
    )
    knowledge_points = models.ManyToManyField(
        'knowledge.KnowledgePoint',
        blank=True,
        related_name='questions',
        verbose_name='关联知识点'
    )
    difficulty = models.CharField(
        '难度',
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    score = models.DecimalField(
        '默认分值',
        max_digits=5,
        decimal_places=2,
        default=1
    )
    suggested_score = models.DecimalField(
        '建议分数',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='从试卷导入时的建议分数'
    )
    is_visible = models.BooleanField(
        '对学生可见',
        default=True,
        help_text='是否在题库中对学生可见'
    )
    for_initial_assessment = models.BooleanField(
        '用于初始评测',
        default=False,
        help_text='是否可用于初始评测随机抽题'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questions',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'questions'
        verbose_name = '题目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.content[:50]}..."


class SurveyQuestion(models.Model):
    """
    问卷题目模型
    
    用于能力测评问卷（智力量表）和学习习惯问卷
    支持：单选、多选、量表、文本等题型
    """
    QUESTION_TYPES = [
        ('single_select', '单选'),
        ('multi_select', '多选'),
        ('scale', '量表'),
        ('text', '文本'),
    ]

    SURVEY_TYPES = [
        ('ability', '智力量表'),
        ('habit', '学习偏好问卷'),
    ]

    survey_type = models.CharField(
        '问卷类型',
        max_length=20,
        choices=SURVEY_TYPES,
        default='habit'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='survey_questions',
        verbose_name='所属课程'
    )
    text = models.TextField(
        '题目文本',
        help_text='问卷题目的完整描述'
    )
    question_type = models.CharField(
        '题目类型',
        max_length=20,
        choices=QUESTION_TYPES
    )
    options = models.JSONField(
        '选项',
        default=list,
        help_text='格式: [{"value": "A", "label": "选项文本", "score": 1}, ...]'
    )
    dimension = models.CharField(
        '能力维度',
        max_length=50,
        blank=True,
        null=True,
        help_text='该题测量的能力维度，如"逻辑推理"、"抽象思维"等'
    )
    order = models.IntegerField(
        '排序',
        default=0
    )
    is_global = models.BooleanField(
        '全局通用',
        default=True,
        help_text='全局通用的题目适用于所有课程'
    )
    is_required = models.BooleanField(
        '是否必答',
        default=True
    )

    class Meta:
        db_table = 'survey_questions'
        verbose_name = '问卷题目'
        verbose_name_plural = verbose_name
        ordering = ['survey_type', 'order']

    def __str__(self):
        return f"{self.get_survey_type_display()}: {self.text[:50]}..."


class Assessment(models.Model):
    """
    测评模型
    
    用于定义初始测评三件套：
    - knowledge: 知识掌握度测评
    - ability: 学习能力评估（问卷形式）
    - habit: 学习习惯问卷
    """
    ASSESSMENT_TYPES = [
        ('knowledge', '知识掌握度测评'),
        ('ability', '学习能力评估'),
        ('habit', '学习习惯问卷'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='assessments',
        verbose_name='所属课程'
    )
    title = models.CharField(
        '测评标题',
        max_length=200
    )
    assessment_type = models.CharField(
        '测评类型',
        max_length=20,
        choices=ASSESSMENT_TYPES
    )
    description = models.TextField(
        '描述',
        blank=True,
        null=True
    )
    questions = models.ManyToManyField(
        Question,
        through='AssessmentQuestion',
        related_name='assessments',
        verbose_name='题目'
    )
    is_active = models.BooleanField(
        '是否启用',
        default=True
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'assessments'
        verbose_name = '测评'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class AssessmentQuestion(models.Model):
    """
    测评-题目关联模型
    
    用于关联测评和题目，支持自定义排序
    """
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    order = models.IntegerField('排序', default=0)

    class Meta:
        db_table = 'assessment_questions'
        ordering = ['order']


class AssessmentResult(models.Model):
    """
    测评结果模型
    
    存储用户完成测评后的结果数据
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_results',
        verbose_name='用户'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='assessment_results',
        verbose_name='课程'
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='测评'
    )
    answers = models.JSONField(
        '答案',
        default=dict,
        help_text='格式: {question_id: answer, ...}'
    )
    score = models.DecimalField(
        '得分',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    result_data = models.JSONField(
        '结果数据',
        default=dict
    )
    completed_at = models.DateTimeField('完成时间', auto_now_add=True)

    class Meta:
        db_table = 'assessment_results'
        verbose_name = '测评结果'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'assessment']

    def __str__(self):
        return f"{self.user.username} - {self.assessment.title}"


class AssessmentStatus(models.Model):
    """
    测评状态模型
    
    记录用户在某门课程下的初始测评三件套完成情况
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_status',
        verbose_name='用户'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='assessment_status',
        verbose_name='课程'
    )
    knowledge_done = models.BooleanField(
        '知识测评完成',
        default=False
    )
    ability_done = models.BooleanField(
        '能力测评完成',
        default=False
    )
    habit_done = models.BooleanField(
        '习惯问卷完成',
        default=False
    )
    generating = models.BooleanField(
        '正在生成中',
        default=False
    )
    generation_error = models.TextField(
        '生成错误信息',
        null=True, blank=True
    )

    class Meta:
        db_table = 'assessment_status'
        verbose_name = '测评状态'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} 测评状态"

    @property
    def is_all_done(self):
        """判断是否全部完成"""
        return self.knowledge_done and self.ability_done and self.habit_done


class AbilityScore(models.Model):
    """
    能力评分模型
    
    存储用户在各个能力维度上的得分
    维度包括：逻辑推理、抽象思维、记忆力、专注力等
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ability_scores',
        verbose_name='用户'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='ability_scores',
        verbose_name='课程'
    )
    scores = models.JSONField(
        '能力维度得分',
        default=dict,
        help_text='格式: {"逻辑推理": 85, "抽象思维": 72, ...}'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'ability_scores'
        verbose_name = '能力评分'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} 能力评分"


class AnswerHistory(models.Model):
    """
    学生答题历史记录模型
    
    记录学生每次答题的详细信息，用于分析学习情况和更新画像
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answer_histories',
        verbose_name='用户'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='answer_histories',
        verbose_name='课程'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_histories',
        verbose_name='题目'
    )
    knowledge_point = models.ForeignKey(
        'knowledge.KnowledgePoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answer_histories',
        verbose_name='知识点'
    )
    student_answer = models.JSONField(
        '学生答案',
        default=dict
    )
    correct_answer = models.JSONField(
        '正确答案',
        default=dict
    )
    is_correct = models.BooleanField(
        '是否正确',
        default=False
    )
    score = models.DecimalField(
        '得分',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    source = models.CharField(
        '来源',
        max_length=50,
        default='practice',
        help_text='答题来源：initial（初始评测）, exam（考试）, practice（练习）'
    )
    exam_id = models.IntegerField(
        '考试ID',
        null=True,
        blank=True
    )
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
    """
    学生画像历史记录模型
    
    用于存储学生画像的更新记录，支持趋势对比
    每次画像更新时保存快照
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_histories',
        verbose_name='用户'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='profile_histories',
        verbose_name='课程'
    )
    knowledge_mastery = models.JSONField(
        '知识掌握度',
        default=dict,
        help_text='格式: {"知识点ID": 掌握度, ...}'
    )
    ability_scores = models.JSONField(
        '能力得分',
        default=dict,
        help_text='格式: {"能力维度": 得分, ...}'
    )
    habit_preferences = models.JSONField(
        '学习偏好',
        default=dict
    )
    summary = models.TextField(
        '画像摘要',
        blank=True,
        null=True
    )
    update_reason = models.CharField(
        '更新原因',
        max_length=100,
        default='manual',
        help_text='更新原因：initial（初始评测）, exam（考试完成）, manual（手动更新）'
    )
    external_mastery = models.JSONField(
        '外部掌握情况',
        default=dict,
        null=True,
        blank=True,
        help_text='预留字段：外部接口返回的掌握情况分析'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'profile_histories'
        verbose_name = '画像历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} - {self.created_at}"


class SurveyResult(models.Model):
    """
    问卷结果模型
    
    存储智力量表和学习偏好问卷的完成结果
    可以重做/修改
    """
    SURVEY_TYPES = [
        ('ability', '智力量表'),
        ('habit', '学习偏好问卷'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='survey_results',
        verbose_name='用户'
    )
    survey_type = models.CharField(
        '问卷类型',
        max_length=20,
        choices=SURVEY_TYPES
    )
    answers = models.JSONField(
        '答案',
        default=dict,
        help_text='格式: {question_id: answer, ...}'
    )
    result = models.JSONField(
        '结果',
        default=dict,
        help_text='根据答案计算出的结果，如能力得分或偏好设置'
    )
    version = models.IntegerField(
        '版本号',
        default=1
    )
    is_current = models.BooleanField(
        '是否当前版本',
        default=True
    )
    completed_at = models.DateTimeField('完成时间', auto_now_add=True)

    class Meta:
        db_table = 'survey_results'
        verbose_name = '问卷结果'
        verbose_name_plural = verbose_name
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_survey_type_display()} v{self.version}"
