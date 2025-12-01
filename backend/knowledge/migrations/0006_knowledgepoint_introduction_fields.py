# knowledge 应用的数据库迁移文件: 0006_knowledgepoint_introduction_fields.py
from django.db import migrations, models


# 定义数据库迁移操作，Django 将按顺序执行以下变更
class Migration(migrations.Migration):
    # 声明依赖的先前迁移版本
    dependencies = [
        ("knowledge", "0005_alter_knowledgerelation_relation_type"),
    ]

    # 要执行的数据库操作列表
    operations = [
        # 添加新字段
        migrations.AddField(
            # 目标模型: knowledgepoint
            model_name="knowledgepoint",
            name="introduction",
            field=models.TextField(
                blank=True,
                help_text="面向学生展示的知识点介绍，优先由数据库缓存提供",
                null=True,
                verbose_name="知识点简介",
            ),
        ),
        # 添加新字段
        migrations.AddField(
            # 目标模型: knowledgepoint
            model_name="knowledgepoint",
            name="introduction_generated_at",
            field=models.DateTimeField(
                blank=True,
                help_text="最后一次生成知识点简介的时间",
                null=True,
                verbose_name="简介生成时间",
            ),
        ),
    ]
