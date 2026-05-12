"""
学习路径模块 - 数据模型
包含学习路径和节点相关的模型

LearningPath: 个性化学习路径
PathNode: 路径中的节点
NodeProgress: 节点学习进度
"""
from django.db import models
from django.conf import settings


class LearningPath(models.Model):
    """
    学习路径模型
    
    代表用户的个性化学习路径，包含：
    - 路径规划理由
    - 是否经过动态调整
    - 关联的节点列表
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_paths',
        verbose_name='用户'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='learning_paths',
        verbose_name='课程'
    )
    ai_reason = models.TextField(
        '路径理由',
        blank=True,
        null=True,
        help_text='AI根据用户画像生成的路径规划说明'
    )
    is_dynamic = models.BooleanField(
        '是否动态调整过',
        default=False,
        help_text='标记路径是否经过后续的动态调整'
    )
    generated_at = models.DateTimeField('生成时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'learning_paths'
        verbose_name = '学习路径'
        verbose_name_plural = verbose_name
        # 每个用户每门课程只有一条学习路径
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} 学习路径"

    @property
    def progress_percent(self):
        """计算路径完成进度百分比"""
        total = self.nodes.count()
        if total == 0:
            return 0
        completed = self.nodes.filter(status='completed').count()
        return round(completed / total * 100, 1)


class PathNode(models.Model):
    """
    路径节点模型
    
    代表学习路径中的一个学习节点，包含：
    - 节点标题和学习目标
    - 达标条件和学习建议
    - 节点状态（锁定/进行中/已完成等）
    - 关联的知识点、资源和测验
    """
    STATUS_CHOICES = [
        ('locked', '未解锁'),
        ('active', '进行中'),
        ('completed', '已完成'),
        ('failed', '未通过'),
        ('skipped', '已跳过'),
    ]

    NODE_TYPE_CHOICES = [
        ('study', '学习节点'),
        ('test', '测试节点'),
    ]

    path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='nodes',
        verbose_name='所属路径'
    )
    node_type = models.CharField(
        '节点类型',
        max_length=10,
        choices=NODE_TYPE_CHOICES,
        default='study',
        help_text='study=学习节点, test=测试节点'
    )
    knowledge_point = models.ForeignKey(
        'knowledge.KnowledgePoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='path_nodes',
        verbose_name='关联知识点'
    )
    title = models.CharField(
        '节点标题',
        max_length=200
    )
    goal = models.TextField(
        '学习目标',
        blank=True,
        null=True
    )
    criterion = models.TextField(
        '达标条件',
        blank=True,
        null=True,
        help_text='完成该节点需要达到的条件'
    )
    suggestion = models.TextField(
        '学习建议',
        blank=True,
        null=True
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='locked'
    )
    order_index = models.IntegerField(
        '顺序',
        default=0
    )
    estimated_minutes = models.IntegerField(
        '预计时长(分钟)',
        default=30,
        help_text='预计完成该节点需要的时间（分钟）'
    )
    is_inserted = models.BooleanField(
        '是否动态插入',
        default=False,
        help_text='标记是否为系统动态插入的补充节点'
    )
    exam = models.ForeignKey(
        'exams.Exam',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='path_nodes',
        verbose_name='节点测验'
    )
    resources = models.ManyToManyField(
        'knowledge.Resource',
        blank=True,
        related_name='path_nodes',
        verbose_name='关联资源'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'path_nodes'
        verbose_name = '路径节点'
        verbose_name_plural = verbose_name
        ordering = ['order_index']

    def __str__(self):
        return f"{self.path.user.username} - {self.title}"


class NodeProgress(models.Model):
    """
    节点进度模型
    
    记录用户在节点上的学习进度，包含：
    - 已完成的资源和测验
    - 学习前后的知识掌握度对比
    """
    node = models.ForeignKey(
        PathNode,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name='节点'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='node_progress',
        verbose_name='用户'
    )
    completed_resources = models.JSONField(
        '已完成资源ID列表',
        default=list
    )
    completed_exams = models.JSONField(
        '已完成测验ID列表',
        default=list
    )
    extra_data = models.JSONField(
        '扩展进度数据',
        default=dict,
        blank=True,
        help_text='用于存储阶段测试报告、资源播放进度等附加数据'
    )
    mastery_before = models.DecimalField(
        '学习前掌握度',
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True
    )
    mastery_after = models.DecimalField(
        '学习后掌握度',
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'node_progress'
        verbose_name = '节点进度'
        verbose_name_plural = verbose_name
        unique_together = ['node', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.node.title} 进度"

    @property
    def mastery_improvement(self):
        """计算掌握度提升"""
        if self.mastery_before is not None and self.mastery_after is not None:
            return float(self.mastery_after - self.mastery_before)
        return None
