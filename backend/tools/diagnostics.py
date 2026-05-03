"""
环境诊断模块。

该模块只做只读检查，供命令行工具快速判断本地数据库、依赖和配置状态。
"""

from __future__ import annotations

import importlib.util
import os
from collections.abc import Iterable
from io import StringIO

from common.neo4j_service import neo4j_service
from tools.common import BASE_DIR, COURSE_RESOURCES_DIR


DEPENDENCY_PACKAGES = ("pandas", "openpyxl", "torch", "neo4j", "langchain", "requests")
LLM_KEY_ENV_NAMES = (
    "LLM_API_KEY",
    "CUSTOM_LLM_API_KEY",
    "DASHSCOPE_API_KEY",
    "DEEPSEEK_API_KEY",
    "ARK_API_KEY",
    "DOUBAO_API_KEY",
    "ZAI_API_KEY",
    "ZHIPU_API_KEY",
    "MOONSHOT_API_KEY",
    "KIMI_API_KEY",
)


# 维护意图：输出本地运行环境诊断结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def diagnose_env() -> None:
    """输出本地运行环境诊断结果。"""
    _print_header("环境诊断")
    _print_directory_section()
    _print_config_section()
    _print_database_section()
    _print_migration_section()
    _print_dependency_section(DEPENDENCY_PACKAGES)
    _print_llm_section()
    _print_data_summary_section()
    print("\n" + "=" * 50)


# 维护意图：打印诊断报告头部，保持 CLI 输出结构稳定
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_header(title: str) -> None:
    """打印诊断报告头部，保持 CLI 输出结构稳定。"""
    print("=" * 50)
    print(title)
    print("=" * 50)


# 维护意图：检查关键目录是否存在且 media 目录是否可写
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_directory_section() -> None:
    """检查关键目录是否存在且 media 目录是否可写。"""
    media_dir = BASE_DIR / "media"
    media_writable = media_dir.exists() and os.access(media_dir, os.W_OK)

    print("\n[目录]")
    print(f"  BASE_DIR: {BASE_DIR}")
    print(f"  课程资源目录: {COURSE_RESOURCES_DIR} ({_mark(COURSE_RESOURCES_DIR.exists())})")
    print(f"  media目录: {media_dir} ({'✓ 可写' if media_writable else '✗'})")


# 维护意图：检查仓库根配置文件是否存在
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_config_section() -> None:
    """检查仓库根配置文件是否存在。"""
    config_path = BASE_DIR / "config.ini"

    print("\n[配置文件]")
    print(f"  config.ini: {_mark(config_path.exists(), fail_text='✗ 缺失')}")


# 维护意图：检查 PostgreSQL 和 Neo4j 可用性
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_database_section() -> None:
    """检查 PostgreSQL 和 Neo4j 可用性。"""
    print("\n[数据库]")
    try:
        _check_postgres()
        print("  PostgreSQL: ✓ 连接正常")
    except Exception as exc:  # pragma: no cover - 诊断脚本需保留真实错误文本。
        print(f"  PostgreSQL: ✗ {exc}")

    print(f"  Neo4j: {'✓ 可用' if neo4j_service.is_available else '✗ 不可用'}")


# 维护意图：执行最小查询，验证 Django 当前数据库连接
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _check_postgres() -> None:
    """执行最小查询，验证 Django 当前数据库连接。"""
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")


# 维护意图：展示未应用迁移的数量和前几项名称
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_migration_section() -> None:
    """展示未应用迁移的数量和前几项名称。"""
    print("\n[迁移状态]")
    try:
        unapplied_migrations = _get_unapplied_migrations()
    except Exception as exc:  # pragma: no cover - 本地诊断需要捕获配置/数据库异常。
        print(f"  ✗ 无法检查迁移状态: {exc}")
        return

    if not unapplied_migrations:
        print("  ✓ 所有迁移已应用")
        return

    print(f"  ✗ {len(unapplied_migrations)} 个未应用的迁移:")
    for migration_name in unapplied_migrations[:5]:
        print(f"    - {migration_name}")


# 维护意图：调用 Django showmigrations 并解析未应用项
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _get_unapplied_migrations() -> list[str]:
    """调用 Django showmigrations 并解析未应用项。"""
    from django.core.management import call_command

    output_buffer = StringIO()
    call_command("showmigrations", "--list", stdout=output_buffer)
    return [
        line.strip()
        for line in output_buffer.getvalue().splitlines()
        if "[ ]" in line
    ]


# 维护意图：检查 Python 依赖是否可被当前解释器发现
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_dependency_section(package_names: Iterable[str]) -> None:
    """检查 Python 依赖是否可被当前解释器发现。"""
    print("\n[依赖包]")
    for package_name in package_names:
        installed = importlib.util.find_spec(package_name) is not None
        print(f"  {package_name}: {_mark(installed, fail_text='✗ 未安装')}")


# 维护意图：展示当前 LLM 相关环境变量的有效配置
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_llm_section() -> None:
    """展示当前 LLM 相关环境变量的有效配置。"""
    llm_key = _first_configured_env(LLM_KEY_ENV_NAMES)

    print("\n[API密钥]")
    print(f"  LLM API Key: {'✓ 已配置' if llm_key else '✗ 未配置'}")
    print(f'  LLM_PROVIDER: {os.environ.get("LLM_PROVIDER", "deepseek") or "deepseek"}')
    print(f'  LLM_MODEL: {os.environ.get("LLM_MODEL", "deepseek-v4-flash") or "deepseek-v4-flash"}')
    print(
        "  LLM_API_FORMAT: "
        f'{os.environ.get("LLM_API_FORMAT", "openai-compatible") or "openai-compatible"}'
    )


# 维护意图：返回第一个已配置的环境变量值
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _first_configured_env(env_names: Iterable[str]) -> str:
    """返回第一个已配置的环境变量值。"""
    for env_name in env_names:
        env_value = os.environ.get(env_name)
        if env_value:
            return env_value
    return ""


# 维护意图：查询核心业务表规模，帮助确认演示/开发数据状态
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _print_data_summary_section() -> None:
    """查询核心业务表规模，帮助确认演示/开发数据状态。"""
    print("\n[数据摘要]")
    try:
        summary = _collect_data_summary()
    except Exception as exc:  # pragma: no cover - 诊断命令需要直接展示现场异常。
        print(f"  ✗ 查询失败: {exc}")
        return

    print(
        "  用户: "
        f"{summary['users']} (学生: {summary['students']}, 教师: {summary['teachers']})"
    )
    print(f"  课程: {summary['courses']}")
    print(f"  知识点: {summary['knowledge_points']}")
    print(f"  题目: {summary['questions']}")
    print(f"  考试: {summary['exams']}")


# 维护意图：集中统计数据，避免诊断入口函数直接触碰多个模型
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _collect_data_summary() -> dict[str, int]:
    """集中统计数据，避免诊断入口函数直接触碰多个模型。"""
    from assessments.models import Question
    from courses.models import Course
    from exams.models import Exam
    from knowledge.models import KnowledgePoint
    from users.models import User

    return {
        "users": User.objects.count(),
        "students": User.objects.filter(role="student").count(),
        "teachers": User.objects.filter(role="teacher").count(),
        "courses": Course.objects.count(),
        "knowledge_points": KnowledgePoint.objects.count(),
        "questions": Question.objects.count(),
        "exams": Exam.objects.count(),
    }


# 维护意图：统一 CLI 成功/失败标记文本
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _mark(condition: bool, *, fail_text: str = "✗") -> str:
    """统一 CLI 成功/失败标记文本。"""
    return "✓" if condition else fail_text
