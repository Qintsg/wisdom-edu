"""
自适应学习系统 - 工具包（统一版）

模块列表:
- common: 公共工具函数
- cli: 命令行入口（统一菜单 + argparse）
- testing: 测试基础设施（HTTP 请求、登录、数据加载）
- knowledge: 知识图谱导入导出
- questions: 题库导入（JSON/Excel）
- exam_sets: 套题导入（从作业库Excel创建ExamSet）
- resources: 资源库导入
- survey: 问卷导入
- bootstrap: 一键初始化 + 课程资源批量导入
- neo4j_tools: Neo4j图数据库管理
- activation: 激活码生成
- diagnostics: 环境诊断
- db_management: 数据库管理
- api_smoke: API烟雾测试
- ai_services_test: AI服务测试
- browser_audit: 浏览器巡检
- demo_course_archive: 答辩演示课程导入包生成
- rebuild_demo: 演示数据全量重建
- excel_templates: Excel模板生成
- mefkt_training: MEFKT模型训练与管理
- rag_index: GraphRAG索引构建与刷新
"""

from tools.common import (
    BASE_DIR,
    COURSE_RESOURCES_DIR,
    CourseAssetBundle,
    list_courses,
)
from tools.bootstrap import bootstrap_course_assets, import_course_resources
from tools.browser_audit import browser_audit
from tools.cli import main
from tools.demo_course_archive import generate_demo_course_archive
from tools.testing import (
    CheckResult,
    _print_checks,
    _request,
    _extract_data,
    _login,
    _resolve_course_id,
    _load_testdata,
)
from tools.db_management import (
    db_check,
    django_check,
    clear_database,
    create_test_data,
    pg_bootstrap,
)
from tools.api_smoke import api_smoke, student_flow_smoke, test_business_logic
from tools.neo4j_tools import (
    test_neo4j_connection,
    import_neo4j_test_data,
    clear_neo4j_data,
    sync_neo4j,
    neo4j_status,
    neo4j_sync_all,
    neo4j_clear,
)
from tools.ai_services_test import test_kt_service, test_llm_service
from tools.exam_sets import import_exam_sets
from tools.excel_templates import generate_template
from tools.knowledge import (
    import_knowledge,
    import_knowledge_map,
    export_knowledge_map,
    validate_json,
)
from tools.questions import import_questions_json, import_question_bank
from tools.resources import import_resources_json, delete_link_resources
from tools.survey import import_survey_questions, import_ability_scale
from tools.activation import generate_activation_codes
from tools.diagnostics import diagnose_env
from tools.mefkt_training import train_mefkt_v2, mefkt_status
from tools.rag_index import build_rag_index, refresh_rag_corpus
from tools.rebuild_demo import rebuild_demo_data

__all__ = [
    # common
    'BASE_DIR',
    'COURSE_RESOURCES_DIR',
    'CourseAssetBundle',
    'list_courses',
    'bootstrap_course_assets',
    'import_course_resources',
    'browser_audit',
    'main',
    'generate_demo_course_archive',
    # testing infrastructure
    'CheckResult',
    '_print_checks',
    '_request',
    '_extract_data',
    '_login',
    '_resolve_course_id',
    '_load_testdata',
    # db management
    'db_check',
    'django_check',
    'clear_database',
    'create_test_data',
    'pg_bootstrap',
    # api testing
    'api_smoke',
    'student_flow_smoke',
    'test_business_logic',
    # neo4j
    'test_neo4j_connection',
    'import_neo4j_test_data',
    'clear_neo4j_data',
    'sync_neo4j',
    'neo4j_status',
    'neo4j_sync_all',
    'neo4j_clear',
    # ai services testing
    'test_kt_service',
    'test_llm_service',
    # exam sets
    'import_exam_sets',
    # excel templates
    'generate_template',
    # knowledge
    'import_knowledge',
    'import_knowledge_map',
    'export_knowledge_map',
    'validate_json',
    # questions
    'import_questions_json',
    'import_question_bank',
    # resources
    'import_resources_json',
    'delete_link_resources',
    # survey
    'import_survey_questions',
    'import_ability_scale',
    # activation
    'generate_activation_codes',
    # diagnostics
    'diagnose_env',
    # mefkt
    'train_mefkt_v2',
    'mefkt_status',
    # demo & rag
    'build_rag_index',
    'refresh_rag_corpus',
    'rebuild_demo_data',
]
