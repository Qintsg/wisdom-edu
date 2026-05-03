"""知识图谱导入解析辅助工具。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.common import clean_nan, load_json, split_multi_values


# 维护意图：加载并校验导入 JSON 结构
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_import_json_payload(file_path: str, schema: str) -> dict[str, Any]:
    """加载并校验导入 JSON 结构。"""
    data = load_json(file_path)
    if not isinstance(data, dict):
        if schema == "knowledge":
            raise ValueError("知识图谱JSON必须是对象")
        if schema == "questions":
            raise ValueError("题库JSON必须是对象")
        if schema == "resources":
            raise ValueError("资源JSON必须是对象")
    if schema == "knowledge":
        if "nodes" not in data or not isinstance(data["nodes"], list):
            raise ValueError("知识图谱JSON缺少 nodes(list)")
    elif schema == "questions":
        if "questions" not in data or not isinstance(data["questions"], list):
            raise ValueError("题库JSON缺少 questions(list)")
    elif schema == "resources":
        if "resources" not in data or not isinstance(data["resources"], list):
            raise ValueError("资源JSON缺少 resources(list)")
    else:
        raise ValueError(f"未知schema: {schema}")
    return data


# 维护意图：读取知识图谱导入源，兼容 JSON 与 Excel
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def read_knowledge_import_source(path: Path) -> dict[str, Any] | None:
    """读取知识图谱导入源，兼容 JSON 与 Excel。"""
    if path.suffix.lower() == ".json":
        payload = load_json(str(path))
        return payload if isinstance(payload, dict) else None
    if path.suffix.lower() in [".xlsx", ".xls"]:
        return parse_knowledge_excel(path)
    return None


# 维护意图：解析 Excel 格式的知识图谱文件
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_knowledge_excel(path: Path) -> dict[str, Any] | None:
    """解析 Excel 格式的知识图谱文件。"""
    try:
        import pandas as pd
    except ImportError:
        print("错误：未安装pandas，无法解析Excel")
        return None

    excel_file = pd.ExcelFile(path)
    if "nodes" in excel_file.sheet_names and "edges" in excel_file.sheet_names:
        nodes_df = pd.read_excel(path, sheet_name="nodes")
        edges_df = pd.read_excel(path, sheet_name="edges")
        return {
            "nodes": nodes_df.to_dict("records"),
            "edges": edges_df.to_dict("records"),
        }

    raw_frame = pd.read_excel(path, sheet_name=0, header=None, nrows=5)
    header_row = resolve_hierarchical_header_row(raw_frame)
    if header_row is not None:
        return parse_hierarchical_knowledge_excel(path, header_row)
    return parse_flat_knowledge_excel(path)


# 维护意图：判断工作表是否使用层级知识点表头
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_hierarchical_header_row(raw_frame) -> int | None:
    """判断工作表是否使用层级知识点表头。"""
    for check_row in range(min(3, len(raw_frame))):
        row_values = [str(value) for value in raw_frame.iloc[check_row]]
        if any("级知识点" in value for value in row_values):
            return check_row
    return None


# 维护意图：识别层级知识点表中的层级列、关系列与元数据列
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_hierarchical_columns(columns: list[str]) -> tuple[list[str], dict[str, str | None], dict[str, str | None]]:
    """识别层级知识点表中的层级列、关系列与元数据列。"""
    cn_num_order = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    level_columns = sorted(
        [column for column in columns if "级知识点" in column],
        key=lambda column: cn_num_order.get(column[0], 99),
    )
    relation_columns = {
        "pre_col": next((column for column in columns if "前置" in column), None),
        "post_col": next((column for column in columns if "后置" in column), None),
        "related_col": next((column for column in columns if "关联" in column), None),
    }
    metadata_columns = {
        "tag_col": next((column for column in columns if "标签" in column), None),
        "dim_col": next((column for column in columns if "认知维度" in column), None),
        "cat_col": next((column for column in columns if column == "分类"), None),
        "desc_col": next(
            (column for column in columns if any(keyword in column for keyword in ["知识点说明", "说明", "描述"])),
            None,
        ),
        "goal_col": next((column for column in columns if "教学目标" in column), None),
    }
    return level_columns, relation_columns, metadata_columns


# 维护意图：从层级列中解析当前行的知识点名称与层级
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_hierarchical_point(row, level_columns: list[str], current_parents: list[str]) -> tuple[str, int]:
    """从层级列中解析当前行的知识点名称与层级。"""
    for level_index, level_column in enumerate(level_columns):
        value = clean_nan(row.get(level_column, ""))
        if not value:
            continue
        current_parents[level_index] = value
        for deeper_index in range(level_index + 1, len(level_columns)):
            current_parents[deeper_index] = ""
        return value, level_index + 1
    return "", 0


# 维护意图：构造层级 Excel 中的知识点节点载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_hierarchical_node(
    *,
    row,
    node_id: str,
    point_name: str,
    point_level: int,
    current_parents: list[str],
    metadata_columns: dict[str, str | None],
) -> dict[str, Any]:
    """构造层级 Excel 中的知识点节点载荷。"""
    chapter_parts = [current_parents[index] for index in range(point_level - 1) if current_parents[index]]
    return {
        "id": node_id,
        "name": point_name,
        "chapter": " > ".join(chapter_parts) if chapter_parts else "",
        "description": clean_nan(row.get(metadata_columns["desc_col"], "")) if metadata_columns["desc_col"] else "",
        "level": point_level,
        "tags": clean_nan(row.get(metadata_columns["tag_col"], "")) if metadata_columns["tag_col"] else "",
        "cognitive_dimension": clean_nan(row.get(metadata_columns["dim_col"], "")) if metadata_columns["dim_col"] else "",
        "category": clean_nan(row.get(metadata_columns["cat_col"], "")) if metadata_columns["cat_col"] else "",
        "teaching_goal": clean_nan(row.get(metadata_columns["goal_col"], "")) if metadata_columns["goal_col"] else "",
    }


# 维护意图：为层级知识点追加父子包含关系
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def append_parent_edge(
    *,
    edges: list[dict[str, Any]],
    point_level: int,
    current_parents: list[str],
    id_by_name: dict[str, str],
    node_id: str,
) -> None:
    """为层级知识点追加父子包含关系。"""
    if point_level <= 1:
        return
    parent_name = current_parents[point_level - 2]
    if parent_name and parent_name in id_by_name:
        edges.append({"source": id_by_name[parent_name], "target": node_id, "relation": "includes"})


# 维护意图：解析层级知识点 Excel
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_hierarchical_knowledge_excel(path: Path, header_row: int) -> dict[str, Any]:
    """解析层级知识点 Excel。"""
    import pandas as pd

    dataframe = pd.read_excel(path, sheet_name=0, header=header_row)
    columns = [str(column).strip() for column in dataframe.columns]
    level_columns, relation_columns, metadata_columns = resolve_hierarchical_columns(columns)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    id_by_name: dict[str, str] = {}
    current_parents = [""] * len(level_columns)
    node_id_counter = 0

    for _, row in dataframe.iterrows():
        point_name, point_level = resolve_hierarchical_point(row, level_columns, current_parents)
        if not point_name:
            continue

        node_id_counter += 1
        node_id = str(node_id_counter)
        nodes.append(
            build_hierarchical_node(
                row=row,
                node_id=node_id,
                point_name=point_name,
                point_level=point_level,
                current_parents=current_parents,
                metadata_columns=metadata_columns,
            )
        )
        id_by_name[point_name] = node_id

        append_parent_edge(
            edges=edges,
            point_level=point_level,
            current_parents=current_parents,
            id_by_name=id_by_name,
            node_id=node_id,
        )
        append_relation_edges(edges, row, relation_columns, id_by_name, node_id)

    return {"nodes": nodes, "edges": edges}


# 维护意图：按前置/后置/关联列补充边
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def append_relation_edges(
    edges: list[dict[str, Any]],
    row,
    relation_columns: dict[str, str | None],
    id_by_name: dict[str, str],
    node_id: str,
) -> None:
    """按前置/后置/关联列补充边。"""
    relation_specs = [
        (relation_columns["pre_col"], "prerequisite", False),
        (relation_columns["post_col"], "prerequisite", True),
        (relation_columns["related_col"], "related", True),
    ]
    for column, relation_type, is_source in relation_specs:
        if not column:
            continue
        value = clean_nan(row.get(column, ""))
        if not value:
            continue
        for reference_name in split_multi_values(value):
            if reference_name not in id_by_name:
                continue
            source = node_id if is_source else id_by_name[reference_name]
            target = id_by_name[reference_name] if is_source else node_id
            edges.append({"source": source, "target": target, "relation": relation_type})


# 维护意图：解析普通单 sheet 知识图谱 Excel
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_flat_knowledge_excel(path: Path) -> dict[str, Any]:
    """解析普通单 sheet 知识图谱 Excel。"""
    import pandas as pd

    dataframe = pd.read_excel(path, sheet_name=0)
    columns = [str(column) for column in dataframe.columns]
    column_map = resolve_flat_columns(columns)
    nodes, id_by_name = collect_flat_nodes(dataframe, column_map)
    edges = collect_flat_prerequisite_edges(dataframe, column_map, id_by_name)
    return {"nodes": nodes, "edges": edges}


# 维护意图：识别普通知识点表的名称、章节、描述和前置列
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_flat_columns(columns: list[str]) -> dict[str, str | None]:
    """识别普通知识点表的名称、章节、描述和前置列。"""
    name_column = next(
        (column for column in columns if any(keyword in column.lower() for keyword in ["知识点", "名称", "name", "point"])),
        columns[0],
    )
    chapter_column = next(
        (column for column in columns if any(keyword in column.lower() for keyword in ["章节", "chapter", "目录"])),
        None,
    )
    description_column = next(
        (column for column in columns if any(keyword in column.lower() for keyword in ["描述", "说明", "description"])),
        None,
    )
    prerequisite_column = next(
        (column for column in columns if any(keyword in column.lower() for keyword in ["先修", "前置", "prerequisite"])),
        None,
    )
    return {
        "name": name_column,
        "chapter": chapter_column,
        "description": description_column,
        "prerequisite": prerequisite_column,
    }


# 维护意图：从普通表中收集知识点节点与名称索引
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def collect_flat_nodes(dataframe, column_map: dict[str, str | None]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """从普通表中收集知识点节点与名称索引。"""
    nodes: list[dict[str, Any]] = []
    id_by_name: dict[str, str] = {}

    for index, (_, row) in enumerate(dataframe.iterrows()):
        point_name = clean_nan(row.get(column_map["name"], ""))
        if not point_name:
            continue
        node_id = str(index + 1)
        nodes.append(
            {
                "id": node_id,
                "name": point_name,
                "chapter": clean_nan(row.get(column_map["chapter"], "")) if column_map["chapter"] else "",
                "description": clean_nan(row.get(column_map["description"], "")) if column_map["description"] else "",
            }
        )
        id_by_name[point_name] = node_id
    return nodes, id_by_name


# 维护意图：从普通表中收集先修关系边
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def collect_flat_prerequisite_edges(
    dataframe,
    column_map: dict[str, str | None],
    id_by_name: dict[str, str],
) -> list[dict[str, Any]]:
    """从普通表中收集先修关系边。"""
    edges: list[dict[str, Any]] = []
    name_column = column_map["name"]
    prerequisite_column = column_map["prerequisite"]
    if prerequisite_column:
        for _, row in dataframe.iterrows():
            target_name = clean_nan(row.get(name_column, ""))
            if not target_name:
                continue
            target = id_by_name.get(target_name, target_name)
            prerequisite_value = clean_nan(row.get(prerequisite_column, ""))
            for prerequisite_name in split_multi_values(prerequisite_value):
                source = id_by_name.get(prerequisite_name, prerequisite_name)
                edges.append({"source": source, "target": target, "relation": "prerequisite"})
    return edges


# 维护意图：为知识图谱导入构造课程内节点索引
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_point_maps(course) -> tuple[dict[str, Any], dict[str, Any]]:
    """为知识图谱导入构造课程内节点索引。"""
    name_to_point = {point.name: point for point in course.knowledgepoint_set.all()} if hasattr(course, "knowledgepoint_set") else {}
    if not name_to_point:
        from knowledge.models import KnowledgePoint

        name_to_point = {
            point.name: point for point in KnowledgePoint.objects.filter(course=course)
        }
    id_to_point: dict[str, Any] = {}
    return name_to_point, id_to_point


# 维护意图：将解析后的知识图谱写入临时 JSON 文件
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def write_tmp_knowledge_json(data: dict[str, Any]) -> Path:
    """将解析后的知识图谱写入临时 JSON 文件。"""
    from tools.common import BASE_DIR

    tmp_json = BASE_DIR / "runtime_logs" / "tmp_knowledge_import.json"
    tmp_json.parent.mkdir(parents=True, exist_ok=True)
    tmp_json.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return tmp_json


# 维护意图：写入课程知识点节点并返回名称/ID 映射
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def upsert_course_knowledge_nodes(
    *,
    course,
    nodes: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """写入课程知识点节点并返回名称/ID 映射。"""
    from knowledge.models import KnowledgePoint

    name_to_point = {point.name: point for point in KnowledgePoint.objects.filter(course=course)}
    id_to_point: dict[str, Any] = {}

    for index, node in enumerate(nodes):
        node_name = clean_nan(node.get("name", f"知识点{index + 1}"))
        if not node_name:
            continue

        point = name_to_point.get(node_name)
        if point is None:
            point = KnowledgePoint.objects.create(
                course=course,
                name=node_name,
                chapter=clean_nan(node.get("chapter")),
                description=clean_nan(node.get("description")),
                level=int(node.get("level") or 1),
                tags=clean_nan(node.get("tags", "")),
                cognitive_dimension=clean_nan(node.get("cognitive_dimension", "")),
                category=clean_nan(node.get("category", "")),
                teaching_goal=clean_nan(node.get("teaching_goal", "")),
                order=index,
                is_published=True,
            )
            name_to_point[node_name] = point
        else:
            patch_existing_point_from_node(point, node)

        if node.get("id"):
            id_to_point[str(node["id"])] = point
    return name_to_point, id_to_point


# 维护意图：仅在字段为空时补齐已有知识点的扩展信息
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def patch_existing_point_from_node(point, node: dict[str, Any]) -> None:
    """仅在字段为空时补齐已有知识点的扩展信息。"""
    updated = False
    for field_name in ("tags", "cognitive_dimension", "category", "teaching_goal"):
        new_value = clean_nan(node.get(field_name, ""))
        if new_value and not getattr(point, field_name, ""):
            setattr(point, field_name, new_value)
            updated = True
    description = clean_nan(node.get("description"))
    if description and not point.description:
        point.description = description
        updated = True
    if updated:
        point.save()


# 维护意图：写入课程知识点关系，并返回新增或命中的边数量
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def upsert_course_knowledge_edges(
    *,
    course,
    edges: list[dict[str, Any]],
    name_to_point: dict[str, Any],
    id_to_point: dict[str, Any],
) -> int:
    """写入课程知识点关系，并返回新增或命中的边数量。"""
    from knowledge.models import KnowledgeRelation

    relation_count = 0
    for edge in edges:
        source_raw = str(edge.get("source", ""))
        target_raw = str(edge.get("target", ""))
        source = id_to_point.get(source_raw) or name_to_point.get(source_raw)
        target = id_to_point.get(target_raw) or name_to_point.get(target_raw)
        if not source or not target or source == target:
            continue
        KnowledgeRelation.objects.get_or_create(
            course=course,
            pre_point=source,
            post_point=target,
            defaults={"relation_type": edge.get("relation") or "prerequisite"},
        )
        relation_count += 1
    return relation_count


# 维护意图：在 PostgreSQL 写入后刷新 Neo4j 图副本
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def sync_knowledge_graph_copy(course) -> None:
    """在 PostgreSQL 写入后刷新 Neo4j 图副本。"""
    from common.neo4j_service import neo4j_service
    from tools.testing import _status_flag

    try:
        if neo4j_service.is_available:
            result = neo4j_service.sync_knowledge_graph(int(course.pk))
            print(
                f'Neo4j同步完成: nodes={result.get("nodes", 0)}, '
                f'relations={result.get("relations", 0)}'
            )
        else:
            print(f"{_status_flag(False)} Neo4j不可用，跳过同步。知识图谱仅保存在PostgreSQL中。")
    except Exception as error:
        print(f"{_status_flag(False)} Neo4j同步失败: {error}")
