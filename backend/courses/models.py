"""
课程模块 - 数据模型
包含课程、班级和选课相关的模型

Course: 课程模型
Class: 班级模型（独立于课程，可以发布多门课程）
ClassCourse: 班级-课程关联模型（一个班级可以发布多个课程）
Enrollment: 选课/加入班级记录
"""

from django.db import models
from django.conf import settings
from django.db.models import Q


# 维护意图：课程模型 代表一门完整的课程，包含： - 基本信息（名称、描述、封面） - 学期信息 - 创建者信息 - 是否公开（所有教师可见）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Course(models.Model):
    """
    课程模型

    代表一门完整的课程，包含：
    - 基本信息（名称、描述、封面）
    - 学期信息
    - 创建者信息
    - 是否公开（所有教师可见）
    """

    name = models.CharField("课程名称", max_length=200, help_text="课程的完整名称")
    description = models.TextField(
        "课程描述", blank=True, null=True, help_text="课程的详细介绍"
    )
    cover = models.ImageField(
        "封面图片", upload_to="course_covers/", blank=True, null=True
    )
    term = models.CharField(
        "学期", max_length=50, blank=True, null=True, help_text="如：2024春季学期"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_courses",
        verbose_name="创建者",
    )
    is_public = models.BooleanField(
        "是否公开", default=True, help_text="公开课程对所有教师可见，可发布到班级"
    )
    initial_assessment_count = models.IntegerField(
        "初始评测题目数量",
        default=10,
        help_text="学生进入课程时随机抽取的初始评测题目数量",
    )
    config = models.JSONField(
        "课程配置",
        default=dict,
        blank=True,
        help_text="存储考试配置、课程管理等自定义参数。"
        '例：{"exam_pass_score": 60, "exam_duration": 90, '
        '"allow_retake": true, "max_retake_times": 3, '
        '"resource_approval": false}',
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "courses"
        verbose_name = "课程"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    # 维护意图：检查用户是否有编辑权限
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def can_edit(self, user):
        """检查用户是否有编辑权限"""
        if user.is_superuser or user.role == "admin":
            return True
        if self.created_by == user:
            return True
        if getattr(user, "role", None) != "teacher":
            return False
        return (
            ClassCourse.objects.filter(
                course=self,
                is_active=True,
                class_obj__teacher=user,
            ).exists()
            or Class.objects.filter(course=self, teacher=user).exists()
        )

    # 维护意图：返回教师/管理员可管理的课程集合
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @classmethod
    def get_manageable_courses(cls, user):
        """返回教师/管理员可管理的课程集合。"""
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return cls.objects.all()
        return cls.objects.filter(
            Q(created_by=user)
            | Q(class_courses__class_obj__teacher=user, class_courses__is_active=True)
            | Q(classes__teacher=user)
        ).distinct()


# 维护意图：班级模型 代表一个教学班级，由教师创建和管理： - 班级名称 - 授课教师（创建者） - 学期信息 - 班级描述 注意：班级与课程是多对多关系，通过ClassCourse模型关联
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Class(models.Model):
    """
    班级模型

    代表一个教学班级，由教师创建和管理：
    - 班级名称
    - 授课教师（创建者）
    - 学期信息
    - 班级描述

    注意：班级与课程是多对多关系，通过ClassCourse模型关联
    """

    name = models.CharField("班级名称", max_length=200, help_text="如：2024级计算机1班")
    description = models.TextField("班级描述", blank=True, null=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="teaching_classes",
        verbose_name="授课教师",
    )
    semester = models.CharField("学期", max_length=50, blank=True, null=True)
    is_active = models.BooleanField("是否激活", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    # 兼容性：保留原有的course外键（作为默认课程）
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes",
        verbose_name="默认课程",
    )

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "classes"
        verbose_name = "班级"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    # 维护意图：获取班级学生数量
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_student_count(self):
        """获取班级学生数量"""
        return self.enrollments.filter(role="student").count()

    # 维护意图：获取班级发布的所有课程
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def courses_list(self):
        """获取班级发布的所有课程"""
        return [cc.course for cc in self.class_courses.filter(is_active=True)]


# 维护意图：班级-课程关联模型 一个班级可以发布多门课程，一门课程可以被多个班级使用
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ClassCourse(models.Model):
    """
    班级-课程关联模型

    一个班级可以发布多门课程，一门课程可以被多个班级使用
    """

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="class_courses",
        verbose_name="班级",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="class_courses",
        verbose_name="课程",
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="published_class_courses",
        verbose_name="发布者",
    )
    is_active = models.BooleanField("是否激活", default=True)
    published_at = models.DateTimeField("发布时间", auto_now_add=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "class_courses"
        verbose_name = "班级课程"
        verbose_name_plural = verbose_name
        unique_together = ["class_obj", "course"]

    def __str__(self):
        return f"{self.class_obj.name} - {self.course.name}"


# 维护意图：选课/班级成员关系模型 记录用户与班级的关联关系，包含： - 用户 - 班级 - 在班级中的角色（学生/助教等） - 加入时间
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Enrollment(models.Model):
    """
    选课/班级成员关系模型

    记录用户与班级的关联关系，包含：
    - 用户
    - 班级
    - 在班级中的角色（学生/助教等）
    - 加入时间
    """

    ROLE_CHOICES = [
        ("student", "学生"),
        ("assistant", "助教"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="用户",
    )
    class_obj = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="enrollments", verbose_name="班级"
    )
    role = models.CharField(
        "班级角色", max_length=20, choices=ROLE_CHOICES, default="student"
    )
    enrolled_at = models.DateTimeField("加入时间", auto_now_add=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "enrollments"
        verbose_name = "选课记录"
        verbose_name_plural = verbose_name
        # 确保用户不重复加入同一班级
        unique_together = ["user", "class_obj"]

    def __str__(self):
        return f"{self.user.username} - {self.class_obj.name}"


# 维护意图：班级公告模型 教师可以在班级中发布公告，学生进入班级后可查看
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Announcement(models.Model):
    """
    班级公告模型

    教师可以在班级中发布公告，学生进入班级后可查看。
    """

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="announcements",
        verbose_name="班级",
    )
    title = models.CharField("公告标题", max_length=200)
    content = models.TextField("公告内容")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
        verbose_name="发布者",
    )
    created_at = models.DateTimeField("发布时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "announcements"
        verbose_name = "班级公告"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.class_obj.name} - {self.title}"
