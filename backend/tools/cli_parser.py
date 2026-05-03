#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""CLI argparse 命令解析与分发。"""

from __future__ import annotations

import argparse

from tools.activation import generate_activation_codes
from tools.ai_services_test import test_kt_service, test_llm_service
from tools.api_regression import api_regression
from tools.api_smoke import api_smoke, student_flow_smoke, test_business_logic
from tools.bootstrap import bootstrap_course_assets
from tools.browser_audit import browser_audit
from tools.common import list_courses
from tools.course_cleanup import delete_course_with_cleanup
from tools.db_management import (
    clear_database,
    create_test_data,
    db_check,
    django_check,
    pg_bootstrap,
)
from tools.demo_course_archive import generate_demo_course_archive
from tools.diagnostics import diagnose_env
from tools.exam_sets import import_exam_sets
from tools.excel_templates import generate_template
from tools.knowledge import (
    export_knowledge_map,
    import_knowledge,
    import_knowledge_map,
    validate_json,
)
from tools.mefkt_training import mefkt_status, train_mefkt_v2
from tools.neo4j_tools import neo4j_clear, neo4j_status, neo4j_sync_all, sync_neo4j
from tools.questions import import_question_bank, import_questions_json
from tools.rag_index import build_rag_index, refresh_rag_corpus
from tools.rebuild_demo import rebuild_demo_data
from tools.resources import delete_link_resources, import_resources_json
from tools.survey import import_ability_scale, import_survey_questions


# 维护意图：为 JSON 导入类子命令追加通用参数
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _add_json_import_args(parser: argparse.ArgumentParser) -> None:
    """为 JSON 导入类子命令追加通用参数。"""
    parser.add_argument("--file", required=True)
    parser.add_argument("--course-id", required=True, type=int)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--dry-run", action="store_true")


# 维护意图：构建 CLI 参数解析器
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器。"""
    parser = argparse.ArgumentParser(
        description="自适应学习系统 - 数据工具 / 模型训练 / 验证",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    knowledge_parser = sub.add_parser("import-knowledge-map", help="导入知识图谱")
    knowledge_parser.add_argument("file")
    knowledge_parser.add_argument("--course-id", type=int)
    knowledge_parser.add_argument("--course-name")

    survey_parser = sub.add_parser("import-survey", help="导入问卷")
    survey_parser.add_argument("type", choices=["ability", "habit"])
    survey_parser.add_argument("file")
    survey_parser.add_argument("--course-id", type=int)

    question_bank_parser = sub.add_parser("import-question-bank", help="导入题库")
    question_bank_parser.add_argument("file")
    question_bank_parser.add_argument("--course-id", type=int, required=True)

    ability_parser = sub.add_parser("import-ability-scale", help="导入能力量表")
    ability_parser.add_argument("file")
    ability_parser.add_argument("--course-id", type=int)

    export_parser = sub.add_parser("export-knowledge-map", help="导出知识图谱")
    export_parser.add_argument("course_id", type=int)
    export_parser.add_argument("output")

    _add_json_import_args(sub.add_parser("import-knowledge", help="导入知识点(JSON)"))
    _add_json_import_args(sub.add_parser("import-questions-json", help="导入题库(JSON)"))
    _add_json_import_args(sub.add_parser("import-resources", help="导入资源(JSON)"))

    exam_parser = sub.add_parser("import-exam-sets", help="导入套题(ExamSet)")
    exam_parser.add_argument("--course-id", type=int, required=True)
    exam_parser.add_argument("--homework-dir", type=str, default=None)
    exam_parser.add_argument("--replace", action="store_true")
    exam_parser.add_argument("--dry-run", action="store_true")

    bootstrap_parser = sub.add_parser("bootstrap-course-assets", help="一键初始化课程资源")
    bootstrap_parser.add_argument("--course-name", required=True)
    bootstrap_parser.add_argument("--teacher", default="teacher1")
    bootstrap_parser.add_argument("--replace", action="store_true")
    bootstrap_parser.add_argument("--sync-neo4j", action="store_true")
    bootstrap_parser.add_argument("--dry-run", action="store_true")
    bootstrap_parser.add_argument("--resources-root", type=str)

    template_parser = sub.add_parser("generate-template", help="生成Excel导入模板")
    template_parser.add_argument("type", choices=["ability", "habit", "questions"])

    demo_archive_parser = sub.add_parser("generate-demo-course-archive", help="生成答辩演示课程导入包")
    demo_archive_parser.add_argument("--course-name", default="大数据技术与应用")
    demo_archive_parser.add_argument("--output", default="../output/答辩演示课程导入包.zip")

    code_parser = sub.add_parser("generate-codes", help="生成激活码")
    code_parser.add_argument("type", choices=["teacher", "admin"])
    code_parser.add_argument("count", type=int, nargs="?", default=1)
    code_parser.add_argument("--creator", default="admin")

    validate_parser = sub.add_parser("validate-json", help="校验JSON格式")
    validate_parser.add_argument("--file", required=True)
    validate_parser.add_argument("--schema", required=True, choices=["knowledge", "questions", "resources"])

    course_parser = sub.add_parser("list-courses", help="列出课程")
    course_parser.add_argument("--show-all", action="store_true")

    delete_resource_parser = sub.add_parser("delete-link-resources", help="删除外部链接资源")
    delete_resource_parser.add_argument("--course-id", type=int, default=None)
    delete_resource_parser.add_argument("--no-dry-run", action="store_true")

    delete_course_parser = sub.add_parser("delete-course", help="删除课程并清理图谱索引")
    delete_course_parser.add_argument("--course-id", type=int, required=True)
    delete_course_parser.add_argument("--yes", action="store_true")

    db_check_parser = sub.add_parser("db-check", help="数据库检查")
    db_check_parser.add_argument("--json", action="store_true")
    django_check_parser = sub.add_parser("django-check", help="Django系统检查")
    django_check_parser.add_argument("--json", action="store_true")
    clear_parser = sub.add_parser("clear-db", help="清空数据库")
    clear_parser.add_argument("--models", type=str, default="")
    sub.add_parser("create-test-data", help="创建测试数据")

    pg_parser = sub.add_parser("pg-bootstrap", aliases=["pg_bootstrap"], help="PostgreSQL初始化(迁移+清库+创建+课程资源导入)")
    pg_parser.add_argument("--no-migrate", action="store_true")
    pg_parser.add_argument("--no-clear", action="store_true")
    pg_parser.add_argument("--no-course-assets", action="store_true")
    pg_parser.add_argument("--course-name", default=None)

    sub.add_parser("neo4j-status", help="查看Neo4j状态")
    sync_parser = sub.add_parser("sync-neo4j", help="同步到Neo4j")
    sync_parser.add_argument("course_id", type=int)
    sub.add_parser("neo4j-sync-all", help="同步全部到Neo4j")
    neo4j_clear_parser = sub.add_parser("neo4j-clear", help="清理Neo4j数据")
    neo4j_clear_parser.add_argument("--course-id", type=int)
    neo4j_clear_parser.add_argument("--yes", action="store_true")

    smoke_parser = sub.add_parser("api-smoke", help="API烟雾测试")
    smoke_parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    smoke_parser.add_argument("--username", default="student1")
    smoke_parser.add_argument("--password", default="Test123456")
    smoke_parser.add_argument("--strict", action="store_true")
    smoke_parser.add_argument("--json", action="store_true")

    flow_parser = sub.add_parser("student-flow-smoke", help="学生链路回归")
    flow_parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    flow_parser.add_argument("--username", default="student1")
    flow_parser.add_argument("--password", default="Test123456")
    flow_parser.add_argument("--course-id", type=int, default=None)
    flow_parser.add_argument("--json", action="store_true")

    sub.add_parser("test-business-logic", help="业务逻辑测试")
    regression_parser = sub.add_parser("api-regression", help="公开API回归测试")
    regression_parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    regression_parser.add_argument("--all", action="store_true")
    regression_parser.add_argument("--json", action="store_true")

    browser_parser = sub.add_parser("browser-audit", help="前端真实浏览器巡检")
    browser_parser.add_argument("--frontend-url", default="http://127.0.0.1:3000")
    browser_parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    browser_parser.add_argument("--output-dir", default=None)
    browser_parser.add_argument(
        "--scenario",
        choices=["audit", "prepare-demo", "simulate-demo", "prepare-defense-demo", "simulate-defense-demo"],
        default="audit",
    )
    browser_parser.add_argument("--headed", action="store_true")
    sub.add_parser("test-kt-service", help="测试KT服务")
    sub.add_parser("test-llm-service", help="测试LLM服务")
    sub.add_parser("diagnose", help="环境诊断")

    rebuild_parser = sub.add_parser("rebuild-demo-data", help="全库重建并导入演示数据")
    rebuild_parser.add_argument("--course-name", default="大数据技术与应用")
    rebuild_parser.add_argument("--teacher", default="teacher1")
    rebuild_parser.add_argument("--resources-root", default=None)

    sub.add_parser("mefkt-status", help="MEFKT模型状态")
    mefkt_parser = sub.add_parser("train-mefkt", help="训练MEFKT模型")
    mefkt_parser.add_argument("--course-id", type=int)
    mefkt_parser.add_argument("--epochs", type=int, default=16)
    mefkt_parser.add_argument("--pretrain-epochs", type=int, default=8)
    mefkt_parser.add_argument("--batch-size", type=int, default=32)
    mefkt_parser.add_argument("--learning-rate", type=float, default=0.001)
    mefkt_parser.add_argument("--hidden-dim", type=int, default=128)
    mefkt_parser.add_argument("--align-dim", type=int, default=128)
    mefkt_parser.add_argument("--similarity-weight", type=float, default=0.5)
    mefkt_parser.add_argument("--dataset", type=str, default=None)
    mefkt_parser.add_argument("--synthetic", action="store_true")
    mefkt_parser.add_argument("--synthetic-students", type=int, default=96)
    mefkt_parser.add_argument("--max-sequences", type=int, default=None)
    mefkt_parser.add_argument("--output", type=str, default=None)

    build_rag_parser = sub.add_parser("build-rag-index", help="构建 RAG 索引")
    build_rag_parser.add_argument("--course-id", type=int)
    refresh_rag_parser = sub.add_parser("refresh-rag-corpus", help="刷新 RAG 索引")
    refresh_rag_parser.add_argument("--course-id", type=int)

    return parser


# 维护意图：将逗号分隔的模型过滤参数转换为列表
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_model_filters(raw_models: str) -> list[str] | None:
    """将逗号分隔的模型过滤参数转换为列表。"""
    if not raw_models:
        return None
    return [model_name.strip() for model_name in raw_models.split(",") if model_name.strip()]


# 维护意图：处理导入、导出和模板相关命令
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _dispatch_import_commands(args: argparse.Namespace) -> bool:
    """处理导入、导出和模板相关命令。"""
    if args.cmd == "import-knowledge-map":
        import_knowledge_map(args.file, args.course_id, getattr(args, "course_name", None))
    elif args.cmd == "import-survey":
        import_survey_questions(args.file, args.type, args.course_id)
    elif args.cmd == "import-question-bank":
        import_question_bank(args.file, args.course_id)
    elif args.cmd == "import-ability-scale":
        import_ability_scale(args.file, args.course_id)
    elif args.cmd == "export-knowledge-map":
        export_knowledge_map(args.course_id, args.output)
    elif args.cmd == "import-knowledge":
        import_knowledge(args.file, args.course_id, replace=args.replace, dry_run=args.dry_run)
    elif args.cmd == "import-questions-json":
        import_questions_json(args.file, args.course_id, replace=args.replace, dry_run=args.dry_run)
    elif args.cmd == "import-resources":
        import_resources_json(args.file, args.course_id, replace=args.replace, dry_run=args.dry_run)
    elif args.cmd == "import-exam-sets":
        import_exam_sets(args.course_id, homework_dir=args.homework_dir, replace=args.replace, dry_run=args.dry_run)
    elif args.cmd == "bootstrap-course-assets":
        bootstrap_course_assets(args.course_name, args.teacher, args.replace, args.sync_neo4j, args.dry_run, args.resources_root)
    elif args.cmd == "generate-template":
        generate_template(args.type)
    elif args.cmd == "generate-demo-course-archive":
        generate_demo_course_archive(course_name=args.course_name, output_path=args.output)
    elif args.cmd == "generate-codes":
        generate_activation_codes(args.type, args.count, args.creator)
    elif args.cmd == "validate-json":
        validate_json(args.file, args.schema)
    else:
        return False
    return True


# 维护意图：处理课程列表、删除、数据库和 Neo4j 管理命令
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _dispatch_data_admin_commands(args: argparse.Namespace) -> bool:
    """处理课程列表、删除、数据库和 Neo4j 管理命令。"""
    if args.cmd == "list-courses":
        list_courses(show_all=args.show_all)
    elif args.cmd == "delete-link-resources":
        delete_link_resources(course_id=args.course_id, dry_run=not args.no_dry_run)
    elif args.cmd == "delete-course":
        delete_course_with_cleanup(course_id=args.course_id, yes=args.yes)
    elif args.cmd == "db-check":
        db_check(as_json=getattr(args, "json", False))
    elif args.cmd == "django-check":
        django_check(as_json=getattr(args, "json", False))
    elif args.cmd == "clear-db":
        clear_database(_parse_model_filters(args.models))
    elif args.cmd == "create-test-data":
        create_test_data()
    elif args.cmd in {"pg-bootstrap", "pg_bootstrap"}:
        pg_bootstrap(not args.no_migrate, not args.no_clear, not args.no_course_assets, args.course_name)
    elif args.cmd == "neo4j-status":
        neo4j_status()
    elif args.cmd == "sync-neo4j":
        sync_neo4j(args.course_id)
    elif args.cmd == "neo4j-sync-all":
        neo4j_sync_all()
    elif args.cmd == "neo4j-clear":
        neo4j_clear(getattr(args, "course_id", None), yes=getattr(args, "yes", False))
    else:
        return False
    return True


# 维护意图：处理测试、巡检和演示重建命令
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _dispatch_test_commands(args: argparse.Namespace) -> bool:
    """处理测试、巡检和演示重建命令。"""
    if args.cmd == "api-smoke":
        api_smoke(args.base_url, args.username, args.password, strict=args.strict, as_json=getattr(args, "json", False))
    elif args.cmd == "student-flow-smoke":
        student_flow_smoke(args.base_url, args.username, args.password, args.course_id, as_json=getattr(args, "json", False))
    elif args.cmd == "test-business-logic":
        test_business_logic()
    elif args.cmd == "api-regression":
        api_regression(args.base_url, include_all=args.all, as_json=getattr(args, "json", False))
    elif args.cmd == "browser-audit":
        browser_audit(args.frontend_url, args.api_base_url, args.output_dir, args.scenario, args.headed)
    elif args.cmd == "test-kt-service":
        test_kt_service()
    elif args.cmd == "test-llm-service":
        test_llm_service()
    elif args.cmd == "diagnose":
        diagnose_env()
    elif args.cmd == "rebuild-demo-data":
        rebuild_demo_data(args.course_name, args.teacher, args.resources_root)
    else:
        return False
    return True


# 维护意图：处理 MEFKT 训练与 RAG 索引命令
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _dispatch_training_commands(args: argparse.Namespace) -> bool:
    """处理 MEFKT 训练与 RAG 索引命令。"""
    if args.cmd == "mefkt-status":
        mefkt_status()
    elif args.cmd == "train-mefkt":
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
    elif args.cmd == "build-rag-index":
        print("\n".join(build_rag_index(course_id=args.course_id)))
    elif args.cmd == "refresh-rag-corpus":
        print("\n".join(refresh_rag_corpus(course_id=args.course_id)))
    else:
        return False
    return True


DISPATCH_HANDLERS = (
    _dispatch_import_commands,
    _dispatch_data_admin_commands,
    _dispatch_test_commands,
    _dispatch_training_commands,
)


# 维护意图：按命令名分发 argparse 子命令
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def dispatch_command(args: argparse.Namespace) -> None:
    """按命令名分发 argparse 子命令。"""
    for handler in DISPATCH_HANDLERS:
        if handler(args):
            return
