"""
知识图谱模块 - 数据模型
包含知识点和知识关系相关的模型

KnowledgePoint: 知识点模型
KnowledgeRelation: 知识点之间的关系
Resource: 学习资源
KnowledgeMastery: 用户对知识点的掌握度
ProfileSummary: 学习者画像摘要
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# 维护意图：知识点模型 代表知识图谱中的一个节点，包含： - 所属课程 - 知识点名称和描述 - 所属章节 - 层级信息 - 标签（重点、难点、考点等） - 认知维度（记忆、理解、应用、分析、评价、创造）。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgePoint(models.Model):
    """
    知识点模型

    代表知识图谱中的一个节点，包含：
    - 所属课程
    - 知识点名称和描述
    - 所属章节
    - 层级信息
    - 标签（重点、难点、考点等）
    - 认知维度（记忆、理解、应用、分析、评价、创造）
    - 分类（事实性、概念性、程序性、元认知）
    - 教学目标
    - 排序和发布状态
    """

    POINT_TYPES = [
        ("knowledge", "知识点"),
        ("skill", "技能"),
        ("concept", "概念"),
    ]

    COGNITIVE_DIMENSIONS = [
        ("remember", "记忆"),
        ("understand", "理解"),
        ("apply", "应用"),
        ("analyze", "分析"),
        ("evaluate", "评价"),
        ("create", "创造"),
    ]

    KNOWLEDGE_CATEGORIES = [
        ("factual", "事实性"),
        ("conceptual", "概念性"),
        ("procedural", "程序性"),
        ("metacognitive", "元认知"),
    ]

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="knowledge_points",
        verbose_name="所属课程",
    )
    name = models.CharField("知识点名称", max_length=200, help_text="知识点的完整名称")
    description = models.TextField("描述", blank=True, null=True, help_text="知识点的详细描述")
    introduction = models.TextField(
        "知识点简介",
        blank=True,
        null=True,
        help_text="面向学生展示的知识点介绍，优先由数据库缓存提供",
    )
    introduction_generated_at = models.DateTimeField(
        "简介生成时间",
        blank=True,
        null=True,
        help_text="最后一次生成知识点简介的时间",
    )
    chapter = models.CharField(
        "所属章节",
        max_length=200,
        blank=True,
        null=True,
        help_text='层级路径，如"大数据技术基础 > Hadoop"',
    )
    point_type = models.CharField("类型", max_length=50, choices=POINT_TYPES, default="knowledge")
    level = models.IntegerField("层级", default=1, help_text="知识点在层级结构中的级别（1-7）")
    tags = models.CharField(
        "标签",
        max_length=200,
        blank=True,
        null=True,
        help_text='多个标签用分号分隔，如"重点;难点;考点"',
    )
    cognitive_dimension = models.CharField(
        "认知维度",
        max_length=50,
        blank=True,
        null=True,
        help_text="如：记忆、理解、应用、分析、评价、创造",
    )
    category = models.CharField(
        "分类",
        max_length=50,
        blank=True,
        null=True,
        help_text="如：事实性、概念性、程序性、元认知",
    )
    teaching_goal = models.CharField("教学目标", max_length=200, blank=True, null=True)
    order = models.IntegerField("排序", default=0, help_text="用于控制知识点的显示顺序")
    is_published = models.BooleanField("是否发布", default=False, help_text="发布后学生可见")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "knowledge_points"
        verbose_name = "知识点"
        verbose_name_plural = verbose_name
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    # 维护意图：获取前置知识点列表
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_prerequisites(self):
        """获取前置知识点列表"""
        return [relation.pre_point for relation in self.pre_relations.all()]

    # 维护意图：获取后续知识点列表
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_dependents(self):
        """获取后续知识点列表"""
        return [relation.post_point for relation in self.post_relations.all()]

    # 维护意图：获取标签列表
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(";") if tag.strip()]
        return []


# 维护意图：知识点关系模型 表示知识图谱中节点之间的关系（边），支持： - prerequisite: 先修关系（A是B的前置知识） - part_of: 包含关系（A包含于B） - related: 相。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeRelation(models.Model):
    """
    知识点关系模型

    表示知识图谱中节点之间的关系（边），支持：
    - prerequisite: 先修关系（A是B的前置知识）
    - part_of: 包含关系（A包含于B）
    - related: 相关关系（A和B相关）
    """

    RELATION_TYPES = [
        ("prerequisite", "先修关系"),
        ("part_of", "包含关系"),
        ("related", "相关关系"),
        ("includes", "层级包含"),
    ]

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="knowledge_relations",
        verbose_name="所属课程",
    )
    pre_point = models.ForeignKey(
        KnowledgePoint,
        on_delete=models.CASCADE,
        related_name="post_relations",
        verbose_name="前序知识点",
    )
    post_point = models.ForeignKey(
        KnowledgePoint,
        on_delete=models.CASCADE,
        related_name="pre_relations",
        verbose_name="后续知识点",
    )
    relation_type = models.CharField(
        "关系类型",
        max_length=20,
        choices=RELATION_TYPES,
        default="prerequisite",
    )

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "knowledge_relations"
        verbose_name = "知识点关系"
        verbose_name_plural = verbose_name
        unique_together = ["pre_point", "post_point"]

    def __str__(self):
        return f"{self.pre_point.name} -> {self.post_point.name}"


# 维护意图：学习资源模型 代表课程中的学习资源，支持： - 视频资源 - 文档资源 - 外部链接 - 练习题
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Resource(models.Model):
    """
    学习资源模型

    代表课程中的学习资源，支持：
    - 视频资源
    - 文档资源
    - 外部链接
    - 练习题
    """

    RESOURCE_TYPES = [
        ("video", "视频"),
        ("document", "文档"),
        ("link", "外部链接"),
        ("exercise", "练习"),
    ]

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="resources",
        verbose_name="所属课程",
    )
    title = models.CharField("资源标题", max_length=300)
    resource_type = models.CharField("资源类型", max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField("资源文件", upload_to="resources/", blank=True, null=True)
    url = models.URLField("资源链接", blank=True, null=True)
    description = models.TextField("描述", blank=True, null=True)
    duration = models.IntegerField("时长(秒)", blank=True, null=True, help_text="视频资源的时长，单位为秒")
    chapter_number = models.CharField(
        "章节编号",
        max_length=20,
        blank=True,
        null=True,
        help_text="资源对应的章节编号，如 1.1、1.2",
    )
    sort_order = models.IntegerField("排序序号", default=0, help_text="用于控制资源的显示顺序")
    knowledge_points = models.ManyToManyField(
        KnowledgePoint,
        blank=True,
        related_name="resources",
        verbose_name="关联知识点",
    )
    is_visible = models.BooleanField("对学生可见", default=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_resources",
        verbose_name="上传者",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "resources"
        verbose_name = "学习资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 维护意图：知识点掌握度模型 记录用户对每个知识点的掌握程度， 掌握度范围为0-1，通过测评和练习动态更新
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeMastery(models.Model):
    """
    知识点掌握度模型

    记录用户对每个知识点的掌握程度，
    掌握度范围为0-1，通过测评和练习动态更新
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mastery_records",
        verbose_name="用户",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="mastery_records",
        verbose_name="课程",
    )
    knowledge_point = models.ForeignKey(
        KnowledgePoint,
        on_delete=models.CASCADE,
        related_name="mastery_records",
        verbose_name="知识点",
    )
    mastery_rate = models.DecimalField(
        "掌握度",
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        default=0,
        help_text="0表示完全不掌握，1表示完全掌握",
    )
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "knowledge_mastery"
        verbose_name = "知识掌握度"
        verbose_name_plural = verbose_name
        # 确保每个用户对每个知识点只有一条记录
        unique_together = ["user", "knowledge_point"]

    def __str__(self):
        return f"{self.user.username} - {self.knowledge_point.name}: {self.mastery_rate:.0%}"


# 维护意图：画像摘要模型 存储AI生成的学习者画像总结，包含： - 总体摘要 - 薄弱点分析 - 学习建议
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ProfileSummary(models.Model):
    """
    画像摘要模型

    存储AI生成的学习者画像总结，包含：
    - 总体摘要
    - 薄弱点分析
    - 学习建议
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_summaries",
        verbose_name="用户",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="profile_summaries",
        verbose_name="课程",
    )
    summary = models.TextField("总体摘要", blank=True, null=True)
    weakness = models.TextField("薄弱点", blank=True, null=True)
    suggestion = models.TextField("学习建议", blank=True, null=True)
    generated_at = models.DateTimeField("生成时间", auto_now=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        db_table = "profile_summaries"
        verbose_name = "画像摘要"
        verbose_name_plural = verbose_name
        unique_together = ["user", "course"]

    def __str__(self):
        return f"{self.user.username} - {self.course.name} 画像"
