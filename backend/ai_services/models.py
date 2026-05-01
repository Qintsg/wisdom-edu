"""
AI服务模块 - 数据模型
包含大模型调用日志相关的模型

LLMCallLog: 大模型调用日志，记录每次调用的输入输出
"""
from django.db import models
from django.conf import settings


class LLMCallLog(models.Model):
    """
    大模型调用日志模型
    
    记录每次大模型调用的详细信息，用于：
    - 调用追踪和调试
    - 用量统计
    - 性能分析
    """
    CALL_TYPES = [
        ('profile_analysis', '画像诊断'),
        ('path_planning', '路径规划'),
        ('resource_reason', '资源推荐'),
        ('feedback_report', '反馈报告'),
        ('chat', 'AI对话'),
        ('node_intro', '知识点介绍'),
        ('kt_analysis', 'KT分析'),
        ('resource_recommend', '资源推荐(AI)'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='llm_calls', 
        verbose_name='用户'
    )
    call_type = models.CharField(
        '调用类型', 
        max_length=30, 
        choices=CALL_TYPES
    )
    input_summary = models.TextField(
        '输入摘要', 
        blank=True, 
        null=True
    )
    output_summary = models.TextField(
        '输出摘要', 
        blank=True, 
        null=True
    )
    model = models.CharField(
        '模型', 
        max_length=50, 
        blank=True, 
        null=True,
        help_text='如: deepseek-v4-flash, deepseek-chat, qwen-plus'
    )
    tokens_used = models.IntegerField(
        'Token用量', 
        null=True, 
        blank=True
    )
    duration_ms = models.IntegerField(
        '耗时(毫秒)', 
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
    created_at = models.DateTimeField('调用时间', auto_now_add=True)

    class Meta:
        db_table = 'llm_call_logs'
        verbose_name = 'LLM调用日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.username if self.user else '匿名'
        return f"{user_name} - {self.get_call_type_display()} @ {self.created_at}"
