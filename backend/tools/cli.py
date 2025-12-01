#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
命令行入口（统一版）。
提供交互式菜单和 argparse 命令行接口。
@Project : wisdom-edu
@File : cli.py
@Author : Qintsg
@Date : 2026-03-23
"""

import argparse

from tools.common import list_courses
from tools.knowledge import (
    validate_json,
    import_knowledge,
    import_knowledge_map,
    export_knowledge_map,
)
from tools.questions import import_questions_json, import_question_bank
from tools.resources import import_resources_json, delete_link_resources
from tools.survey import import_survey_questions, import_ability_scale
from tools.bootstrap import bootstrap_course_assets, import_course_resources
from tools.neo4j_tools import sync_neo4j, neo4j_status, neo4j_sync_all, neo4j_clear
from tools.neo4j_tools import test_neo4j_connection, import_neo4j_test_data
from tools.activation import generate_activation_codes
from tools.diagnostics import diagnose_env
from tools.demo_course_archive import generate_demo_course_archive
from tools.db_management import (
    db_check,
    django_check,
    clear_database,
    create_test_data,
    pg_bootstrap,
)
from tools.course_cleanup import delete_course_with_cleanup
from tools.api_smoke import api_smoke, student_flow_smoke, test_business_logic
from tools.api_regression import api_regression
from tools.ai_services_test import test_kt_service, test_llm_service
from tools.browser_audit import browser_audit
from tools.excel_templates import generate_template
from tools.exam_sets import import_exam_sets
from tools.dkt_training import (
    train_dkt_v2 as train_dkt,
    dkt_status,
    export_training_data,
)
from tools.mefkt_training import mefkt_status, train_mefkt_v2
from tools.rebuild_demo import rebuild_demo_data
from tools.rag_index import build_rag_index, refresh_rag_corpus


MENU_SECTIONS = (
    "── 数据导入导出 ──",
    "[1]  导入知识图谱 (json/xlsx)",
    "[2]  导入题库 (xlsx)",
    "[3]  导入问卷 (ability/habit)",
    "[4]  导出知识图谱",
    "[5]  导入课程资源(目录)",
    "[6]  生成Excel导入模板",
    "[7]  生成激活码",
    "[8]  导入套题(ExamSet)",
    "",
    "── 数据库管理 ──",
    "[9]  数据库检查",
    "[10] Django系统检查",
    "[11] 清空数据库",
    "[12] 创建测试数据",
    "[13] PostgreSQL初始化(迁移+清库+创建)",
    "",
    "── Neo4j ──",
    "[14] Neo4j状态",
    "[15] 同步课程到Neo4j",
    "[16] 同步全部课程到Neo4j",
    "[17] 清理Neo4j数据",
    "[18] 测试Neo4j连接",
    "[19] 导入Neo4j测试数据",
    "",
    "── API 测试 ──",
    "[20] API烟雾测试",
    "[21] 学生关键链路回归",
    "[22] 业务逻辑测试",
    "",
    "── AI 服务测试 ──",
    "[23] 测试KT服务",
    "[24] 测试LLM服务",
    "",
    "── KT 模型管理 ──",
    "[25] DKT模型状态",
    "[26] 训练DKT模型(数据库)",
    "[27] 训练DKT模型(合成数据)",
    "[28] 导出训练数据",
    "[29] MEFKT模型状态",
    "[30] 训练MEFKT模型",
    "",
    "── GraphRAG / 演示验证 ──",
    "[31] 构建GraphRAG索引",
    "[32] 刷新GraphRAG语料",
    "[33] 重建演示数据",
    "[34] 生成答辩演示导入包",
    "[35] 浏览器巡检",
    "",
    "[0]  退出",
)


def _render_menu() -> None:
    """
    集中输出交互菜单文本。
    :return: None。
    """
    print("\n" + "=" * 60)
    print(" 自适应学习系统 - 数据工具 / 模型训练 / 验证")
    print("=" * 60)
    print()
    for line in MENU_SECTIONS:
        print(line)


def _parse_optional_course_id(prompt: str) -> int | None:
    """
    解析可留空的课程 ID 输入。
    :param prompt: 输入提示文本。
    :return: 课程 ID，留空时返回 None。
    """
    course_id = input(prompt).strip()
    return int(course_id) if course_id else None


def _prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """
    解析交互式 yes/no 输入。
    :param prompt: 输入提示文本。
    :param default: 默认返回值。
    :return: 解析后的布尔值。
    """
    raw_value = input(prompt).strip().lower()
    if not raw_value:
        return default
    return raw_value in {"y", "yes", "1", "true"}


def _handle_menu_choice(choice: str) -> bool:
    """
    执行单个菜单选项。
    :param choice: 用户输入的菜单选项。
    :return: False 表示退出交互式菜单，其余情况返回 True。
    """
    if choice == "1":
        file_path = input("文件路径: ").strip()
        course_id = input("课程ID(留空新建课程): ").strip()
        if course_id:
            import_knowledge_map(file_path, int(course_id))
        else:
            course_name = input("新课程名称(可空): ").strip() or None
            import_knowledge_map(file_path, None, course_name)
    elif choice == "2":
        file_path = input("题库文件路径: ").strip()
        course_id = int(input("课程ID: ").strip())
        import_question_bank(file_path, course_id)
    elif choice == "3":
        survey_type = input("问卷类型(ability/habit): ").strip()
        file_path = input("问卷文件路径: ").strip()
        import_survey_questions(file_path, survey_type, None)
    elif choice == "4":
        course_id = int(input("课程ID: ").strip())
        output_path = input("输出路径: ").strip()
        export_knowledge_map(course_id, output_path)
    elif choice == "5":
        course_name = input("课程名(留空则导入全部): ").strip()
        import_course_resources(course_name or None)
    elif choice == "6":
        template_type = input("模板类型(ability/habit/questions): ").strip()
        generate_template(template_type)
    elif choice == "7":
        code_type = input("类型(teacher/admin): ").strip() or "teacher"
        count = int(input("数量(默认1): ").strip() or "1")
        generate_activation_codes(code_type, count)
    elif choice == "8":
        course_id = int(input("课程ID: ").strip())
        homework_dir = input("作业库目录(留空使用默认): ").strip() or None
        import_exam_sets(course_id, homework_dir, replace=True)
    elif choice == "9":
        db_check()
    elif choice == "10":
        django_check()
    elif choice == "11":
        clear_database()
    elif choice == "12":
        create_test_data()
    elif choice == "13":
        pg_bootstrap(run_migrate=True, clear_first=True)
    elif choice == "14":
        neo4j_status()
    elif choice == "15":
        sync_neo4j(int(input("课程ID: ").strip()))
    elif choice == "16":
        neo4j_sync_all()
    elif choice == "17":
        neo4j_clear(_parse_optional_course_id("课程ID(留空全部): "), yes=False)
    elif choice == "18":
        test_neo4j_connection()
    elif choice == "19":
        import_neo4j_test_data()
    elif choice == "20":
        api_smoke("http://127.0.0.1:8000", "student1", "Test123456", strict=False)
    elif choice == "21":
        student_flow_smoke("http://127.0.0.1:8000", "student1", "Test123456", None)
    elif choice == "22":
        test_business_logic()
    elif choice == "23":
        test_kt_service()
    elif choice == "24":
        test_llm_service()
    elif choice == "25":
        dkt_status()
    elif choice == "26":
        course_id = _parse_optional_course_id("课程ID(留空全部): ")
        epochs = int(input("训练轮次(默认100): ").strip() or "100")
        train_dkt(course_id=course_id, epochs=epochs)
    elif choice == "27":
        course_id = _parse_optional_course_id("课程ID(留空全部): ")
        epochs = int(input("训练轮次(默认100): ").strip() or "100")
        train_dkt(course_id=course_id, epochs=epochs, use_synthetic=True)
    elif choice == "28":
        export_training_data(course_id=_parse_optional_course_id("课程ID(留空全部): "))
    elif choice == "29":
        mefkt_status()
    elif choice == "30":
        public_dataset = input("公开数据集(留空则使用业务数据，如 assist2009): ").strip() or None
        course_id = None if public_dataset else _parse_optional_course_id("课程ID(留空则使用业务数据默认): ")
        epochs = int(input("训练轮次(默认16): ").strip() or "16")
        pretrain_epochs = int(input("预训练轮次(默认8): ").strip() or "8")
        batch_size = int(input("批大小(默认32): ").strip() or "32")
        hidden_dim = int(input("隐藏维度(默认128): ").strip() or "128")
        align_dim = int(input("对齐维度(默认128): ").strip() or "128")
        synthetic_enabled = _prompt_yes_no("启用合成轨迹辅助(y/N): ", default=False)
        synthetic_students = int(input("合成学生数(默认96): ").strip() or "96")
        max_sequences_text = input("最大序列数(留空不限制): ").strip()
        output_path = input("输出路径(留空默认): ").strip() or None
        train_mefkt_v2(
            course_id=course_id,
            epochs=epochs,
            pretrain_epochs=pretrain_epochs,
            batch_size=batch_size,
            hidden_dim=hidden_dim,
            align_dim=align_dim,
            public_dataset=public_dataset,
            use_synthetic=synthetic_enabled,
            synthetic_students=synthetic_students,
            max_sequences=int(max_sequences_text) if max_sequences_text else None,
            output_path=output_path,
        )
    elif choice == "31":
        print("\n".join(build_rag_index(course_id=_parse_optional_course_id("课程ID(留空全部): "))))
    elif choice == "32":
        print("\n".join(refresh_rag_corpus(course_id=_parse_optional_course_id("课程ID(留空全部): "))))
    elif choice == "33":
        course_name = input("课程名(默认大数据技术与应用): ").strip() or "大数据技术与应用"
        teacher = input("教师账号(默认teacher1): ").strip() or "teacher1"
        resources_root = input("资源根目录(留空默认): ").strip() or None
        rebuild_demo_data(
            course_name=course_name,
            teacher=teacher,
            resources_root=resources_root,
        )
    elif choice == "34":
        course_name = input("课程名(默认大数据技术与应用): ").strip() or "大数据技术与应用"
        output_path = input("输出路径(默认../output/答辩演示课程导入包.zip): ").strip() or "../output/答辩演示课程导入包.zip"
        generate_demo_course_archive(
            course_name=course_name,
            output_path=output_path,
        )
    elif choice == "35":
        scenario = input("场景(audit/prepare-demo/simulate-demo/prepare-defense-demo/simulate-defense-demo): ").strip() or "audit"
        if scenario not in {"audit", "prepare-demo", "simulate-demo", "prepare-defense-demo", "simulate-defense-demo"}:
            print("无效场景")
            return True
        frontend_url = input("前端地址(默认http://127.0.0.1:3000): ").strip() or "http://127.0.0.1:3000"
        api_base_url = input("API地址(默认http://127.0.0.1:8000): ").strip() or "http://127.0.0.1:8000"
        headed = _prompt_yes_no("是否使用有头浏览器(y/N): ", default=False)
        browser_audit(
            frontend_url=frontend_url,
            api_base_url=api_base_url,
            scenario=scenario,
            headed=headed,
        )
    elif choice == "0":
        return False
    else:
        print("无效选项")
    return True


def show_menu():
    """循环展示交互式菜单并分发对应工具命令。"""
    while True:
        _render_menu()
        choice = input("\n请输入选项: ").strip()

        try:
            if not _handle_menu_choice(choice):
                break
        except Exception as exc:
            print(f"执行失败: {exc}")


def _add_json_import_args(p):
    """
    为 JSON 导入类子命令追加通用参数。
    :param p: argparse 子解析器。
    :return: None。
    """
    p.add_argument("--file", required=True)
    p.add_argument("--course-id", required=True, type=int)
    p.add_argument("--replace", action="store_true")
    p.add_argument("--dry-run", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    """
    构建 CLI 参数解析器。
    :return: 已配置完成的 argparse 解析器。
    """
    parser = argparse.ArgumentParser(
        description="自适应学习系统 - 数据工具 / 模型训练 / 验证",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    # ── 数据导入导出 ──
    p = sub.add_parser("import-knowledge-map", help="导入知识图谱")
    p.add_argument("file")
    p.add_argument("--course-id", type=int)
    p.add_argument("--course-name")

    p = sub.add_parser("import-survey", help="导入问卷")
    p.add_argument("type", choices=["ability", "habit"])
    p.add_argument("file")
    p.add_argument("--course-id", type=int)

    p = sub.add_parser("import-question-bank", help="导入题库")
    p.add_argument("file")
    p.add_argument("--course-id", type=int, required=True)

    p = sub.add_parser("import-ability-scale", help="导入能力量表")
    p.add_argument("file")
    p.add_argument("--course-id", type=int)

    p = sub.add_parser("export-knowledge-map", help="导出知识图谱")
    p.add_argument("course_id", type=int)
    p.add_argument("output")

    p = sub.add_parser("import-knowledge", help="导入知识点(JSON)")
    _add_json_import_args(p)

    p = sub.add_parser("import-questions-json", help="导入题库(JSON)")
    _add_json_import_args(p)

    p = sub.add_parser("import-resources", help="导入资源(JSON)")
    _add_json_import_args(p)

    p = sub.add_parser("import-exam-sets", help="导入套题(ExamSet)")
    p.add_argument("--course-id", type=int, required=True)
    p.add_argument("--homework-dir", type=str, default=None)
    p.add_argument("--replace", action="store_true")
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("bootstrap-course-assets", help="一键初始化课程资源")
    p.add_argument("--course-name", required=True)
    p.add_argument("--teacher", default="teacher1")
    p.add_argument("--replace", action="store_true")
    p.add_argument("--sync-neo4j", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--resources-root", type=str)

    p = sub.add_parser("generate-template", help="生成Excel导入模板")
    p.add_argument("type", choices=["ability", "habit", "questions"])

    p = sub.add_parser("generate-demo-course-archive", help="生成答辩演示课程导入包")
    p.add_argument("--course-name", default="大数据技术与应用")
    p.add_argument("--output", default="../output/答辩演示课程导入包.zip")

    p = sub.add_parser("generate-codes", help="生成激活码")
    p.add_argument("type", choices=["teacher", "admin"])
    p.add_argument("count", type=int, nargs="?", default=1)
    p.add_argument("--creator", default="admin")

    p = sub.add_parser("validate-json", help="校验JSON格式")
    p.add_argument("--file", required=True)
    p.add_argument(
        "--schema", required=True, choices=["knowledge", "questions", "resources"]
    )

    p = sub.add_parser("list-courses", help="列出课程")
    p.add_argument("--show-all", action="store_true")

    p = sub.add_parser("delete-link-resources", help="删除外部链接资源")
    p.add_argument("--course-id", type=int, default=None)
    p.add_argument("--no-dry-run", action="store_true")

    p = sub.add_parser("delete-course", help="删除课程并清理图谱索引")
    p.add_argument("--course-id", type=int, required=True)
    p.add_argument("--yes", action="store_true")

    # ── 数据库管理 ──
    p = sub.add_parser("db-check", help="数据库检查")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("django-check", help="Django系统检查")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("clear-db", help="清空数据库")
    p.add_argument("--models", type=str, default="")

    sub.add_parser("create-test-data", help="创建测试数据")

    p = sub.add_parser(
        "pg-bootstrap",
        aliases=["pg_bootstrap"],
        help="PostgreSQL初始化(迁移+清库+创建+课程资源导入)",
    )
    p.add_argument("--no-migrate", action="store_true")
    p.add_argument("--no-clear", action="store_true")
    p.add_argument("--no-course-assets", action="store_true")
    p.add_argument("--course-name", default=None)

    # ── Neo4j ──
    sub.add_parser("neo4j-status", help="查看Neo4j状态")
    p = sub.add_parser("sync-neo4j", help="同步到Neo4j")
    p.add_argument("course_id", type=int)
    sub.add_parser("neo4j-sync-all", help="同步全部到Neo4j")

    p = sub.add_parser("neo4j-clear", help="清理Neo4j数据")
    p.add_argument("--course-id", type=int)
    p.add_argument("--yes", action="store_true")

    # ── 测试 ──
    p = sub.add_parser("api-smoke", help="API烟雾测试")
    p.add_argument("--base-url", default="http://127.0.0.1:8000")
    p.add_argument("--username", default="student1")
    p.add_argument("--password", default="Test123456")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("student-flow-smoke", help="学生链路回归")
    p.add_argument("--base-url", default="http://127.0.0.1:8000")
    p.add_argument("--username", default="student1")
    p.add_argument("--password", default="Test123456")
    p.add_argument("--course-id", type=int, default=None)
    p.add_argument("--json", action="store_true")

    sub.add_parser("test-business-logic", help="业务逻辑测试")
    p = sub.add_parser("api-regression", help="公开API回归测试")
    p.add_argument("--base-url", default="http://127.0.0.1:8000")
    p.add_argument("--all", action="store_true")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("browser-audit", help="前端真实浏览器巡检")
    p.add_argument("--frontend-url", default="http://127.0.0.1:3000")
    p.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    p.add_argument("--output-dir", default=None)
    p.add_argument(
        "--scenario",
        choices=[
            "audit",
            "prepare-demo",
            "simulate-demo",
            "prepare-defense-demo",
            "simulate-defense-demo",
        ],
        default="audit",
    )
    p.add_argument("--headed", action="store_true")
    sub.add_parser("test-kt-service", help="测试KT服务")
    sub.add_parser("test-llm-service", help="测试LLM服务")
    sub.add_parser("diagnose", help="环境诊断")
    p = sub.add_parser("rebuild-demo-data", help="全库重建并导入演示数据")
    p.add_argument("--course-name", default="大数据技术与应用")
    p.add_argument("--teacher", default="teacher1")
    p.add_argument("--resources-root", default=None)

    # ── DKT ──
    sub.add_parser("dkt-status", help="DKT模型状态")

    p = sub.add_parser("train-dkt", help="训练DKT模型")
    p.add_argument("--course-id", type=int)
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--dataset", type=str, default=None)
    p.add_argument("--with-business-data", action="store_true")

    sub.add_parser("mefkt-status", help="MEFKT模型状态")

    p = sub.add_parser("train-mefkt", help="训练MEFKT模型")
    p.add_argument("--course-id", type=int)
    p.add_argument("--epochs", type=int, default=16)
    p.add_argument("--pretrain-epochs", type=int, default=8)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--learning-rate", type=float, default=0.001)
    p.add_argument("--hidden-dim", type=int, default=128)
    p.add_argument("--align-dim", type=int, default=128)
    p.add_argument("--similarity-weight", type=float, default=0.5)
    p.add_argument("--dataset", type=str, default=None)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--synthetic-students", type=int, default=96)
    p.add_argument("--max-sequences", type=int, default=None)
    p.add_argument("--output", type=str, default=None)

    p = sub.add_parser("export-training-data", help="导出DKT训练数据")
    p.add_argument("--course-id", type=int)

    p = sub.add_parser("build-rag-index", help="构建 RAG 索引")
    p.add_argument("--course-id", type=int)

    p = sub.add_parser("refresh-rag-corpus", help="刷新 RAG 索引")
    p.add_argument("--course-id", type=int)

    return parser


def _parse_model_filters(raw_models: str) -> list[str] | None:
    """
    将逗号分隔的模型过滤参数转换为列表。
    :param raw_models: 原始模型过滤字符串。
    :return: 模型名称列表，留空时返回 None。
    """
    if not raw_models:
        return None
    return [
        model_name.strip() for model_name in raw_models.split(",") if model_name.strip()
    ]


def _dispatch_command(args: argparse.Namespace) -> None:
    """
    按命令名分发 argparse 子命令。
    :param args: argparse 解析后的命令参数。
    :return: None。
    """
    cmd = args.cmd

    if cmd == "import-knowledge-map":
        import_knowledge_map(
            args.file, args.course_id, getattr(args, "course_name", None)
        )
    elif cmd == "import-survey":
        import_survey_questions(args.file, args.type, args.course_id)
    elif cmd == "import-question-bank":
        import_question_bank(args.file, args.course_id)
    elif cmd == "import-ability-scale":
        import_ability_scale(args.file, args.course_id)
    elif cmd == "export-knowledge-map":
        export_knowledge_map(args.course_id, args.output)
    elif cmd == "import-knowledge":
        import_knowledge(
            args.file, args.course_id, replace=args.replace, dry_run=args.dry_run
        )
    elif cmd == "import-questions-json":
        import_questions_json(
            args.file, args.course_id, replace=args.replace, dry_run=args.dry_run
        )
    elif cmd == "import-resources":
        import_resources_json(
            args.file, args.course_id, replace=args.replace, dry_run=args.dry_run
        )
    elif cmd == "import-exam-sets":
        import_exam_sets(
            args.course_id,
            homework_dir=args.homework_dir,
            replace=args.replace,
            dry_run=args.dry_run,
        )
    elif cmd == "bootstrap-course-assets":
        bootstrap_course_assets(
            course_name=args.course_name,
            teacher=args.teacher,
            replace=args.replace,
            sync_graph=args.sync_neo4j,
            dry_run=args.dry_run,
            resources_root=args.resources_root,
        )
    elif cmd == "generate-template":
        generate_template(args.type)
    elif cmd == "generate-demo-course-archive":
        generate_demo_course_archive(
            course_name=args.course_name,
            output_path=args.output,
        )
    elif cmd == "generate-codes":
        generate_activation_codes(args.type, args.count, args.creator)
    elif cmd == "validate-json":
        validate_json(args.file, args.schema)
    elif cmd == "list-courses":
        list_courses(show_all=args.show_all)
    elif cmd == "delete-link-resources":
        delete_link_resources(course_id=args.course_id, dry_run=not args.no_dry_run)
    elif cmd == "delete-course":
        delete_course_with_cleanup(course_id=args.course_id, yes=args.yes)
    elif cmd == "db-check":
        db_check(as_json=getattr(args, "json", False))
    elif cmd == "django-check":
        django_check(as_json=getattr(args, "json", False))
    elif cmd == "clear-db":
        clear_database(_parse_model_filters(args.models))
    elif cmd == "create-test-data":
        create_test_data()
    elif cmd in {"pg-bootstrap", "pg_bootstrap"}:
        pg_bootstrap(
            run_migrate=not args.no_migrate,
            clear_first=not args.no_clear,
            import_course_assets=not args.no_course_assets,
            course_name=args.course_name,
        )
    elif cmd == "neo4j-status":
        neo4j_status()
    elif cmd == "sync-neo4j":
        sync_neo4j(args.course_id)
    elif cmd == "neo4j-sync-all":
        neo4j_sync_all()
    elif cmd == "neo4j-clear":
        neo4j_clear(getattr(args, "course_id", None), yes=getattr(args, "yes", False))
    elif cmd == "api-smoke":
        api_smoke(
            args.base_url,
            args.username,
            args.password,
            strict=args.strict,
            as_json=getattr(args, "json", False),
        )
    elif cmd == "student-flow-smoke":
        student_flow_smoke(
            args.base_url,
            args.username,
            args.password,
            args.course_id,
            as_json=getattr(args, "json", False),
        )
    elif cmd == "test-business-logic":
        test_business_logic()
    elif cmd == "api-regression":
        api_regression(
            base_url=args.base_url,
            include_all=args.all,
            as_json=getattr(args, "json", False),
        )
    elif cmd == "browser-audit":
        browser_audit(
            frontend_url=args.frontend_url,
            api_base_url=args.api_base_url,
            output_dir=args.output_dir,
            scenario=args.scenario,
            headed=args.headed,
        )
    elif cmd == "test-kt-service":
        test_kt_service()
    elif cmd == "test-llm-service":
        test_llm_service()
    elif cmd == "diagnose":
        diagnose_env()
    elif cmd == "rebuild-demo-data":
        rebuild_demo_data(
            course_name=args.course_name,
            teacher=args.teacher,
            resources_root=args.resources_root,
        )
    elif cmd == "dkt-status":
        dkt_status()
    elif cmd == "train-dkt":
        train_dkt(
            course_id=args.course_id,
            epochs=args.epochs,
            use_synthetic=args.synthetic,
            public_dataset=args.dataset,
            blend_business_data=args.with_business_data,
        )
    elif cmd == "mefkt-status":
        mefkt_status()
    elif cmd == "train-mefkt":
        train_mefkt_v2(
            course_id=args.course_id,
            epochs=args.epochs,
            pretrain_epochs=args.pretrain_epochs,
            batch_size=args.batch_size,
            lr=args.learning_rate,
            hidden_dim=args.hidden_dim,
            align_dim=args.align_dim,
            similarity_weight=args.similarity_weight,
            public_dataset=args.dataset,
            use_synthetic=args.synthetic,
            synthetic_students=args.synthetic_students,
            max_sequences=args.max_sequences,
            output_path=args.output,
        )
    elif cmd == "export-training-data":
        export_training_data(course_id=args.course_id)
    elif cmd == "build-rag-index":
        print("\n".join(build_rag_index(course_id=args.course_id)))
    elif cmd == "refresh-rag-corpus":
        print("\n".join(refresh_rag_corpus(course_id=args.course_id)))


def main():
    """
    CLI 统一入口。
    :return: None。
    """
    parser = build_parser()
    args = parser.parse_args()

    if not args.cmd:
        show_menu()
        return

    _dispatch_command(args)
