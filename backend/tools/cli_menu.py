#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""CLI 交互式菜单。"""

from __future__ import annotations

from tools.activation import generate_activation_codes
from tools.ai_services_test import test_kt_service, test_llm_service
from tools.api_smoke import api_smoke, student_flow_smoke, test_business_logic
from tools.bootstrap import import_course_resources
from tools.browser_audit import browser_audit
from tools.db_management import (
    clear_database,
    create_test_data,
    db_check,
    django_check,
    pg_bootstrap,
)
from tools.demo_course_archive import generate_demo_course_archive
from tools.exam_sets import import_exam_sets
from tools.excel_templates import generate_template
from tools.knowledge import export_knowledge_map, import_knowledge_map
from tools.mefkt_training import mefkt_status, train_mefkt_v2
from tools.neo4j_tools import (
    import_neo4j_test_data,
    neo4j_clear,
    neo4j_status,
    neo4j_sync_all,
    sync_neo4j,
    test_neo4j_connection,
)
from tools.questions import import_question_bank
from tools.rag_index import build_rag_index, refresh_rag_corpus
from tools.rebuild_demo import rebuild_demo_data
from tools.survey import import_survey_questions


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
    "[25] MEFKT模型状态",
    "[26] 训练MEFKT模型",
    "",
    "── GraphRAG / 演示验证 ──",
    "[27] 构建GraphRAG索引",
    "[28] 刷新GraphRAG语料",
    "[29] 重建演示数据",
    "[30] 生成答辩演示导入包",
    "[31] 浏览器巡检",
    "",
    "[0]  退出",
)


# 维护意图：集中输出交互菜单文本
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _render_menu() -> None:
    """集中输出交互菜单文本。"""
    print("\n" + "=" * 60)
    print(" 自适应学习系统 - 数据工具 / 模型训练 / 验证")
    print("=" * 60)
    print()
    for line in MENU_SECTIONS:
        print(line)


# 维护意图：解析可留空的课程 ID 输入
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_optional_course_id(prompt: str) -> int | None:
    """解析可留空的课程 ID 输入。"""
    course_id = input(prompt).strip()
    return int(course_id) if course_id else None


# 维护意图：解析交互式 yes/no 输入
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """解析交互式 yes/no 输入。"""
    raw_value = input(prompt).strip().lower()
    if not raw_value:
        return default
    return raw_value in {"y", "yes", "1", "true"}


# 维护意图：处理数据导入导出相关菜单选项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _handle_data_menu_choice(choice: str) -> bool | None:
    """处理数据导入导出相关菜单选项。"""
    if choice == "1":
        file_path = input("文件路径: ").strip()
        course_id = input("课程ID(留空新建课程): ").strip()
        if course_id:
            import_knowledge_map(file_path, int(course_id))
        else:
            course_name = input("新课程名称(可空): ").strip() or None
            import_knowledge_map(file_path, None, course_name)
        return True
    if choice == "2":
        file_path = input("题库文件路径: ").strip()
        course_id = int(input("课程ID: ").strip())
        import_question_bank(file_path, course_id)
        return True
    if choice == "3":
        survey_type = input("问卷类型(ability/habit): ").strip()
        file_path = input("问卷文件路径: ").strip()
        import_survey_questions(file_path, survey_type, None)
        return True
    if choice == "4":
        course_id = int(input("课程ID: ").strip())
        output_path = input("输出路径: ").strip()
        export_knowledge_map(course_id, output_path)
        return True
    if choice == "5":
        course_name = input("课程名(留空则导入全部): ").strip()
        import_course_resources(course_name or None)
        return True
    if choice == "6":
        template_type = input("模板类型(ability/habit/questions): ").strip()
        generate_template(template_type)
        return True
    if choice == "7":
        code_type = input("类型(teacher/admin): ").strip() or "teacher"
        count = int(input("数量(默认1): ").strip() or "1")
        generate_activation_codes(code_type, count)
        return True
    if choice == "8":
        course_id = int(input("课程ID: ").strip())
        homework_dir = input("作业库目录(留空使用默认): ").strip() or None
        import_exam_sets(course_id, homework_dir, replace=True)
        return True
    return None


# 维护意图：处理数据库管理菜单选项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _handle_database_menu_choice(choice: str) -> bool | None:
    """处理数据库管理菜单选项。"""
    if choice == "9":
        db_check()
        return True
    if choice == "10":
        django_check()
        return True
    if choice == "11":
        clear_database()
        return True
    if choice == "12":
        create_test_data()
        return True
    if choice == "13":
        pg_bootstrap(run_migrate=True, clear_first=True)
        return True
    return None


# 维护意图：处理 Neo4j 菜单选项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _handle_neo4j_menu_choice(choice: str) -> bool | None:
    """处理 Neo4j 菜单选项。"""
    if choice == "14":
        neo4j_status()
        return True
    if choice == "15":
        sync_neo4j(int(input("课程ID: ").strip()))
        return True
    if choice == "16":
        neo4j_sync_all()
        return True
    if choice == "17":
        neo4j_clear(_parse_optional_course_id("课程ID(留空全部): "), yes=False)
        return True
    if choice == "18":
        test_neo4j_connection()
        return True
    if choice == "19":
        import_neo4j_test_data()
        return True
    return None


# 维护意图：处理 API 与 AI 服务测试菜单选项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _handle_api_and_service_menu_choice(choice: str) -> bool | None:
    """处理 API 与 AI 服务测试菜单选项。"""
    if choice == "20":
        api_smoke("http://127.0.0.1:8000", "student1", "Test123456", strict=False)
        return True
    if choice == "21":
        student_flow_smoke("http://127.0.0.1:8000", "student1", "Test123456", None)
        return True
    if choice == "22":
        test_business_logic()
        return True
    if choice == "23":
        test_kt_service()
        return True
    if choice == "24":
        test_llm_service()
        return True
    return None


# 维护意图：处理 KT 模型管理菜单选项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _handle_kt_menu_choice(choice: str) -> bool | None:
    """处理 KT 模型管理菜单选项。"""
    if choice == "25":
        mefkt_status()
        return True
    if choice == "26":
        public_dataset = input("公开数据集(留空使用默认 assist2017，如 assist2009): ").strip() or None
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
            course_id=None,
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
        return True
    return None


# 维护意图：处理 GraphRAG 与演示验证菜单选项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _handle_graphrag_and_demo_menu_choice(choice: str) -> bool | None:
    """处理 GraphRAG 与演示验证菜单选项。"""
    if choice == "27":
        print("\n".join(build_rag_index(course_id=_parse_optional_course_id("课程ID(留空全部): "))))
        return True
    if choice == "28":
        print("\n".join(refresh_rag_corpus(course_id=_parse_optional_course_id("课程ID(留空全部): "))))
        return True
    if choice == "29":
        course_name = input("课程名(默认大数据技术与应用): ").strip() or "大数据技术与应用"
        teacher = input("教师账号(默认teacher1): ").strip() or "teacher1"
        resources_root = input("资源根目录(留空默认): ").strip() or None
        rebuild_demo_data(course_name=course_name, teacher=teacher, resources_root=resources_root)
        return True
    if choice == "30":
        course_name = input("课程名(默认大数据技术与应用): ").strip() or "大数据技术与应用"
        output_path = input("输出路径(默认../output/答辩演示课程导入包.zip): ").strip() or "../output/答辩演示课程导入包.zip"
        generate_demo_course_archive(course_name=course_name, output_path=output_path)
        return True
    if choice == "31":
        scenario = input("场景(audit/prepare-demo/simulate-demo/prepare-defense-demo/simulate-defense-demo): ").strip() or "audit"
        if scenario not in {"audit", "prepare-demo", "simulate-demo", "prepare-defense-demo", "simulate-defense-demo"}:
            print("无效场景")
            return True
        frontend_url = input("前端地址(默认http://127.0.0.1:3000): ").strip() or "http://127.0.0.1:3000"
        api_base_url = input("API地址(默认http://127.0.0.1:8000): ").strip() or "http://127.0.0.1:8000"
        headed = _prompt_yes_no("是否使用有头浏览器(y/N): ", default=False)
        browser_audit(frontend_url=frontend_url, api_base_url=api_base_url, scenario=scenario, headed=headed)
        return True
    return None


MENU_GROUP_HANDLERS = (
    _handle_data_menu_choice,
    _handle_database_menu_choice,
    _handle_neo4j_menu_choice,
    _handle_api_and_service_menu_choice,
    _handle_kt_menu_choice,
    _handle_graphrag_and_demo_menu_choice,
)


# 维护意图：执行单个菜单选项，返回 False 表示退出
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _handle_menu_choice(choice: str) -> bool:
    """执行单个菜单选项，返回 False 表示退出。"""
    if choice == "0":
        return False

    for handler in MENU_GROUP_HANDLERS:
        result = handler(choice)
        if result is not None:
            return result

    print("无效选项")
    return True


# 维护意图：循环展示交互式菜单并分发对应工具命令
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def show_menu() -> None:
    """循环展示交互式菜单并分发对应工具命令。"""
    while True:
        _render_menu()
        choice = input("\n请输入选项: ").strip()

        try:
            if not _handle_menu_choice(choice):
                break
        except Exception as exc:
            print(f"执行失败: {exc}")
