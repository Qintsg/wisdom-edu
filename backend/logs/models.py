"""
操作日志模块 - 数据模型
Operation Logs Module - Data Models

记录系统操作日志，便于管理员追踪和审计
Records system operation logs for admin tracking and auditing
"""
from django.conf import settings
from django.db import models


class OperationLog(models.Model):
    """
    操作日志模型
    Operation Log Model
    
    记录用户在系统中的操作行为，包括：
    - 操作类型（创建、更新、删除、查询等）
    - 操作模块（用户、课程、考试等）
    - 操作详情（请求路径、方法、参数等）
    - 操作结果（成功/失败）
    - IP地址和设备信息
    """

    # 操作类型选项
    ACTION_TYPES = [
        ('create', '创建 Create'),
        ('update', '更新 Update'),
        ('delete', '删除 Delete'),
        ('read', '查询 Read'),
        ('login', '登录 Login'),
        ('logout', '登出 Logout'),
        ('export', '导出 Export'),
        ('import', '导入 Import'),
        ('other', '其他 Other'),
    ]
    
    # 模块选项
    MODULE_CHOICES = [
        ('users', '用户模块 Users'),
        ('courses', '课程模块 Courses'),
        ('knowledge', '知识模块 Knowledge'),
        ('exams', '考试模块 Exams'),
        ('assessments', '测评模块 Assessments'),
        ('learning', '学习模块 Learning'),
        ('ai_services', 'AI服务模块 AI Services'),
        ('logs', '日志模块 Logs'),
        ('system', '系统 System'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operation_logs',
        verbose_name='操作用户'
    )
    action_type = models.CharField(
        '操作类型',
        max_length=20,
        choices=ACTION_TYPES,
        default='other'
    )
    module = models.CharField(
        '操作模块',
        max_length=50,
        choices=MODULE_CHOICES,
        default='system'
    )
    description = models.CharField(
        '操作描述',
        max_length=500,
        blank=True,
        null=True
    )
    request_path = models.CharField(
        '请求路径',
        max_length=500,
        blank=True,
        null=True
    )
    request_method = models.CharField(
        '请求方法',
        max_length=10,
        blank=True,
        null=True
    )
    request_params = models.JSONField(
        '请求参数',
        default=dict,
        blank=True
    )
    response_status = models.IntegerField(
        '响应状态码',
        null=True,
        blank=True
    )
    is_success = models.BooleanField(
        '是否成功',
        default=True
    )
    error_message = models.TextField(
        '错误信息',
        blank=True,
        null=True
    )
    ip_address = models.GenericIPAddressField(
        'IP地址',
        null=True,
        blank=True
    )
    user_agent = models.CharField(
        '用户代理',
        max_length=500,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        '操作时间',
        auto_now_add=True
    )

    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        # 添加索引以提高查询性能
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['module', 'created_at']),
        ]

    def __str__(self):
        username = self.user.username if self.user else '匿名用户'
        return f"{username} - {self.get_action_type_display()} - {self.created_at}"
