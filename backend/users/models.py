"""
用户模块 - 数据模型
包含用户认证和权限相关的模型

User: 自定义用户模型，扩展Django AbstractUser
HabitPreference: 学习习惯偏好
UserCourseContext: 用户当前课程上下文
ActivationCode: 教师/管理员注册激活码
ClassInvitation: 班级邀请码
"""
import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    用户模型
    
    扩展Django默认用户，增加角色、头像、手机号等字段
    角色类型：学生(student)、教师(teacher)、管理员(admin)
    """
    ROLE_CHOICES = [
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    ]
    
    role = models.CharField(
        '角色', 
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student',
        help_text='用户在系统中的角色'
    )
    email = models.EmailField(
        '邮箱',
        blank=True,
        null=True,
        unique=True,
        help_text='可选，用于登录和找回密码'
    )
    avatar = models.ImageField(
        '头像', 
        upload_to='avatars/', 
        blank=True, 
        null=True
    )
    phone = models.CharField(
        '手机号', 
        max_length=11,
        blank=True, 
        null=True,
        unique=True,
        help_text='可选，用于登录'
    )
    real_name = models.CharField(
        '真实姓名',
        max_length=50,
        blank=True,
        null=True
    )
    student_id = models.CharField(
        '学号/工号',
        max_length=50,
        blank=True,
        null=True
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_teacher(self):
        """判断是否为教师"""
        return self.role == 'teacher'
    
    @property
    def is_student(self):
        """判断是否为学生"""
        return self.role == 'student'
    
    @property
    def is_admin(self):
        """判断是否为管理员"""
        return self.role == 'admin' or self.is_superuser


class ActivationCode(models.Model):
    """
    激活码模型
    
    用于教师和管理员注册时的身份验证。
    激活码由管理员生成，每个激活码只能使用一次。
    """
    CODE_TYPES = [
        ('teacher', '教师激活码'),
        ('admin', '管理员激活码'),
    ]
    
    code = models.CharField(
        '激活码',
        max_length=20,
        unique=True,
        help_text='8位随机激活码'
    )
    code_type = models.CharField(
        '类型',
        max_length=20,
        choices=CODE_TYPES,
        default='teacher'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_activation_codes',
        verbose_name='创建者'
    )
    used_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_activation_codes',
        verbose_name='使用者'
    )
    is_used = models.BooleanField(
        '是否已使用',
        default=False
    )
    used_at = models.DateTimeField(
        '使用时间',
        null=True,
        blank=True
    )
    expires_at = models.DateTimeField(
        '过期时间',
        null=True,
        blank=True,
        help_text='为空表示永不过期'
    )
    remark = models.CharField(
        '备注',
        max_length=200,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'activation_codes'
        verbose_name = '激活码'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        status = '已使用' if self.is_used else '未使用'
        return f"{self.code} ({self.get_code_type_display()}) - {status}"
    
    @staticmethod
    def generate_code():
        """生成8位随机激活码"""
        return secrets.token_hex(4).upper()  # 4字节 = 8个十六进制字符
    
    def is_valid(self):
        """检查激活码是否有效"""
        if self.is_used:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    def use(self, user):
        """使用激活码"""
        if not self.is_valid():
            return False
        self.is_used = True
        self.used_by = user
        self.used_at = timezone.now()
        self.save()
        return True


class ClassInvitation(models.Model):
    """
    班级邀请码模型
    
    由教师生成，用于学生加入班级。
    每个邀请码可以设置使用次数限制和过期时间。
    """
    code = models.CharField(
        '邀请码',
        max_length=20,
        unique=True,
        help_text='6位随机邀请码'
    )
    class_obj = models.ForeignKey(
        'courses.Class',
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='班级'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invitations',
        verbose_name='创建者'
    )
    max_uses = models.IntegerField(
        '最大使用次数',
        default=0,
        help_text='0表示无限制'
    )
    use_count = models.IntegerField(
        '已使用次数',
        default=0
    )
    expires_at = models.DateTimeField(
        '过期时间',
        null=True,
        blank=True,
        help_text='为空表示永不过期'
    )
    is_active = models.BooleanField(
        '是否激活',
        default=True
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'class_invitations'
        verbose_name = '班级邀请码'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.class_obj.name}"
    
    @staticmethod
    def generate_code():
        """生成6位随机邀请码"""
        return secrets.token_hex(3).upper()  # 3字节 = 6个十六进制字符
    
    def is_valid(self):
        """检查邀请码是否有效"""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses <= 0:
            return True
        if self.use_count >= self.max_uses:
            return False
        return True
    
    def use(self):
        """使用邀请码（增加使用次数）"""
        self.use_count += 1
        self.save()



class HabitPreference(models.Model):
    """
    学习习惯偏好模型
    
    记录用户的学习偏好设置，包括：
    - 偏好的资源类型（视频/文档/练习等）
    - 高效学习时间段
    - 学习节奏偏好
    - 学习环境偏好
    - 复习频率偏好
    - 其他个性化偏好设置
    """
    RESOURCE_TYPES = [
        ('video', '视频'),
        ('document', '文档'),
        ('exercise', '练习'),
        ('link', '外部链接'),
        ('mixed', '混合'),
    ]
    
    STUDY_TIME_CHOICES = [
        ('morning', '早上 (6:00-12:00)'),
        ('afternoon', '下午 (12:00-18:00)'),
        ('evening', '晚上 (18:00-24:00)'),
        ('night', '深夜 (0:00-6:00)'),
        ('flexible', '灵活安排'),
    ]
    
    STUDY_PACE_CHOICES = [
        ('fast', '快节奏（快速浏览）'),
        ('moderate', '中等节奏'),
        ('slow', '慢节奏（深度学习）'),
        ('adaptive', '自适应'),
    ]
    
    STUDY_DURATION_CHOICES = [
        ('short', '短时间（15-30分钟）'),
        ('medium', '中等（30-60分钟）'),
        ('long', '长时间（60分钟以上）'),
    ]
    
    REVIEW_FREQUENCY_CHOICES = [
        ('daily', '每日复习'),
        ('weekly', '每周复习'),
        ('before_exam', '考前复习'),
        ('spaced', '间隔复习（记忆曲线）'),
        ('never', '很少复习'),
    ]
    
    LEARNING_STYLE_CHOICES = [
        ('visual', '视觉型（图表、图片）'),
        ('auditory', '听觉型（讲解、音频）'),
        ('reading', '阅读型（文字阅读）'),
        ('kinesthetic', '动手型（练习、实践）'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='habit_preference', 
        verbose_name='用户'
    )
    preferred_resource = models.CharField(
        '偏好资源类型', 
        max_length=50, 
        choices=RESOURCE_TYPES,
        default='video'
    )
    preferred_study_time = models.CharField(
        '高效学习时间', 
        max_length=50, 
        choices=STUDY_TIME_CHOICES,
        default='evening'
    )
    study_pace = models.CharField(
        '学习节奏',
        max_length=50,
        choices=STUDY_PACE_CHOICES,
        default='moderate'
    )
    study_duration = models.CharField(
        '单次学习时长',
        max_length=50,
        choices=STUDY_DURATION_CHOICES,
        default='medium'
    )
    review_frequency = models.CharField(
        '复习频率',
        max_length=50,
        choices=REVIEW_FREQUENCY_CHOICES,
        default='weekly'
    )
    learning_style = models.CharField(
        '学习风格',
        max_length=50,
        choices=LEARNING_STYLE_CHOICES,
        default='visual'
    )
    accept_challenge = models.BooleanField(
        '接受挑战性内容',
        default=True,
        help_text='是否愿意尝试难度较高的内容'
    )
    daily_goal_minutes = models.IntegerField(
        '每日学习目标(分钟)',
        default=60
    )
    weekly_goal_days = models.IntegerField(
        '每周学习目标(天)',
        default=5
    )
    preferences = models.JSONField(
        '其他偏好', 
        default=dict,
        help_text='存储其他个性化偏好设置'
    )
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'habit_preferences'
        verbose_name = '学习习惯偏好'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.user.username} 的学习偏好"


class UserCourseContext(models.Model):
    """
    用户当前课程上下文
    
    记录用户当前选择的课程和班级，
    用于前端展示和API数据筛选
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='course_context', 
        verbose_name='用户'
    )
    current_course = models.ForeignKey(
        'courses.Course', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='+', 
        verbose_name='当前课程'
    )
    current_class = models.ForeignKey(
        'courses.Class', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='+', 
        verbose_name='当前班级'
    )
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user_course_context'
        verbose_name = '用户课程上下文'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        course_name = self.current_course.name if self.current_course else '未选择'
        return f"{self.user.username} - 当前课程: {course_name}"
