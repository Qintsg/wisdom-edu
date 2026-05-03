"""数据库管理功能。

包含数据库检查、Django系统检查、清空数据库、创建测试数据、PostgreSQL初始化等功能。
"""

from typing import List, Optional

from tools.common import User
from tools.db_demo_preset import (
    DEFAULT_BOOTSTRAP_COURSE_NAME,
    preset_student1_demo_course_state,
)
from tools.db_seed_support import seed_database_from_testdata, sync_seeded_courses
from tools.testing import CheckResult, _load_testdata, _print_checks, _status_flag


# 维护意图：执行数据库关键数据存在性检查。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def db_check(as_json: bool = False):
    """执行数据库关键数据存在性检查。

    检查课程、知识点、题库、问卷、资源等核心业务数据是否存在。

    Args:
        as_json (bool): 是否以 JSON 格式输出结果
    """
    from assessments.models import Question, SurveyQuestion
    from courses.models import Course
    from knowledge.models import KnowledgePoint, Resource

    checks = [
        CheckResult("课程存在性", Course.objects.count() > 0, f"count={Course.objects.count()}"),
        CheckResult("知识点存在性", KnowledgePoint.objects.count() > 0, f"count={KnowledgePoint.objects.count()}"),
        CheckResult("题库存在性", Question.objects.count() > 0, f"count={Question.objects.count()}"),
        CheckResult("问卷存在性", SurveyQuestion.objects.count() > 0, f"count={SurveyQuestion.objects.count()}"),
        CheckResult("资源存在性", Resource.objects.count() > 0, f"count={Resource.objects.count()}"),
    ]
    _print_checks(checks, as_json=as_json)


# 维护意图：执行 Django 系统检查。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def django_check(as_json: bool = False):
    """执行 Django 系统检查。

    Args:
        as_json (bool): 是否以 JSON 格式输出结果
    """
    from django.core.management import call_command

    checks: List[CheckResult] = []
    try:
        call_command("check")
        checks.append(CheckResult("Django系统检查", True, "ok"))
    except Exception as error:
        checks.append(CheckResult("Django系统检查", False, str(error)))
    _print_checks(checks, as_json=as_json)


# 维护意图：清空数据库中的核心业务数据。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clear_database(model_names: Optional[List[str]] = None):
    """清空数据库中的核心业务数据。

    按照正确的依赖顺序删除数据，避免外键约束错误。

    Args:
        model_names (Optional[List[str]]): 要清空的模型名称列表，None 表示全部清空
    """
    from django.db import transaction

    from assessments.models import (
        AbilityScore,
        Assessment,
        AssessmentQuestion,
        AssessmentStatus,
        Question,
        SurveyQuestion,
    )
    from courses.models import Class, ClassCourse, Course, Enrollment
    from exams.models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
    from knowledge.models import (
        KnowledgeMastery,
        KnowledgePoint,
        KnowledgeRelation,
        ProfileSummary,
        Resource,
    )
    from learning.models import LearningPath, NodeProgress, PathNode
    from users.models import ActivationCode, ClassInvitation, HabitPreference

    all_models = [
        NodeProgress,
        FeedbackReport,
        ExamSubmission,
        PathNode,
        LearningPath,
        ProfileSummary,
        KnowledgeMastery,
        AbilityScore,
        AssessmentStatus,
        ExamQuestion,
        Exam,
        AssessmentQuestion,
        Assessment,
        Question,
        SurveyQuestion,
        Resource,
        KnowledgeRelation,
        KnowledgePoint,
        HabitPreference,
        ActivationCode,
        ClassInvitation,
        Enrollment,
        ClassCourse,
        Class,
        Course,
        User,
    ]

    model_map = {model.__name__: model for model in all_models}

    if model_names:
        to_clear = [model_map[name] for name in model_names if name in model_map]
        invalid = [name for name in model_names if name not in model_map]
        if invalid:
            print(f"  {_status_flag(False)} 无效模型名: {', '.join(invalid)}")
    else:
        to_clear = all_models

    total = 0
    with transaction.atomic():
        for model in to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            total += count
            print(f"  {_status_flag(True)} 已删除 {model.__name__}: {count}")
    print(f"数据库清理完成，共删除 {total} 条记录。")


# 维护意图：从 testdata.json5 创建基础测试数据（用户、课程、班级）。
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def create_test_data():
    """从 testdata.json5 创建基础测试数据（用户、课程、班级）。

    知识点、题库、资源等课程数据需通过 `bootstrap-course-assets` 命令导入。
    """
    from django.db import transaction

    data = _load_testdata()
    if not data:
        return

    print("开始创建测试数据...")
    with transaction.atomic():
        seeded_state = seed_database_from_testdata(data)

    print("测试数据创建完成。")
    sync_seeded_courses(seeded_state.courses)

    if seeded_state.courses:
        print("\n提示: 课程资源（知识图谱、题库、PPT等）需通过导入命令导入：")
        print("  python tools.py bootstrap-course-assets --course-name 大数据技术与应用")


# 维护意图：初始化 PostgreSQL 测试环境。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def pg_bootstrap(
    run_migrate: bool = True,
    clear_first: bool = True,
    import_course_assets: bool = True,
    course_name: str | None = None,
):
    """初始化 PostgreSQL 测试环境。

    默认执行：迁移 → 清空 → 创建基础数据 → 导入课程资源/同步 Neo4j/刷新 GraphRAG
    → 重新修正 student1 的真实初测态预置。

    Args:
        run_migrate (bool): 是否执行数据库迁移
        clear_first (bool): 是否先清空数据库
        import_course_assets (bool): 是否额外导入课程资源并同步图谱
        course_name (str | None): 指定需要优先重建 student1 预置的课程名
    """
    from django.core.management import call_command
    from tools.bootstrap import import_course_resources

    print("开始初始化 PostgreSQL 测试样例...")

    if run_migrate:
        call_command("migrate")
        print(f"  {_status_flag(True)} 迁移完成")

    if clear_first:
        clear_database()

    create_test_data()

    if import_course_assets:
        target_course_name = (course_name or "").strip() or None
        try:
            import_course_resources(target_course_name)
        except Exception as error:
            print(f"  {_status_flag(False)} 课程资源自动导入失败: {error}")

        preset_student1_demo_course_state(
            target_course_name or DEFAULT_BOOTSTRAP_COURSE_NAME
        )

    print("PostgreSQL 测试样例初始化完成。")
