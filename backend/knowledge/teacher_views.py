"""
知识图谱模块教师端视图兼容入口。

URL 与旧导入路径仍指向 knowledge.teacher_views；具体实现按资源、题库、关系、知识点和图谱职责拆分。
"""
import logging

from application.teacher.contracts import first_present, normalize_question_point_ids
from assessments.models import Question
from common.neo4j_service import neo4j_service
from common.utils import resolve_course_id as _resolve_course_id

from .models import KnowledgePoint, KnowledgeRelation, Resource
from .teacher_helpers import (
    KnowledgePointReference,
    KnowledgePointRelationAdder as _KnowledgePointRelationAdder,
    KnowledgePointRelationSetter as _KnowledgePointRelationSetter,
    UTF8_BOM,
    bad_request as _bad_request,
    build_csv_download_response as _build_csv_download_response,
    extract_question_answer_text as _extract_question_answer_text,
    link_knowledge_points as _link_knowledge_points,
    parse_pagination as _parse_pagination,
    refresh_course_rag_index as _refresh_course_rag_index,
    replace_knowledge_points as _replace_knowledge_points,
    require_point_ids as _require_point_ids,
)
from .teacher_map_views import (
    knowledge_graph_save,
    knowledge_map_build_rag_index,
    knowledge_map_export,
    knowledge_map_import,
    knowledge_map_publish,
    knowledge_map_template,
)
from .teacher_point_views import (
    knowledge_point_create,
    knowledge_point_delete,
    knowledge_point_list,
    knowledge_point_update,
)
from .teacher_question_views import (
    question_batch_delete,
    question_create,
    question_delete,
    question_detail,
    question_export,
    question_import,
    question_link_knowledge,
    question_list,
    question_template,
    question_update,
)
from .teacher_relation_views import (
    knowledge_relation_create,
    knowledge_relation_delete,
    knowledge_relation_list,
)
from .teacher_resource_views import (
    resource_create,
    resource_delete,
    resource_link_knowledge,
    resource_list,
    resource_update,
    resource_upload,
)


logger = logging.getLogger(__name__)


__all__ = [
    'KnowledgePoint',
    'KnowledgePointReference',
    'KnowledgeRelation',
    'Question',
    'Resource',
    'UTF8_BOM',
    '_KnowledgePointRelationAdder',
    '_KnowledgePointRelationSetter',
    '_bad_request',
    '_build_csv_download_response',
    '_extract_question_answer_text',
    '_link_knowledge_points',
    '_parse_pagination',
    '_refresh_course_rag_index',
    '_replace_knowledge_points',
    '_require_point_ids',
    '_resolve_course_id',
    'first_present',
    'knowledge_graph_save',
    'knowledge_map_build_rag_index',
    'knowledge_map_export',
    'knowledge_map_import',
    'knowledge_map_publish',
    'knowledge_map_template',
    'knowledge_point_create',
    'knowledge_point_delete',
    'knowledge_point_list',
    'knowledge_point_update',
    'knowledge_relation_create',
    'knowledge_relation_delete',
    'knowledge_relation_list',
    'logger',
    'neo4j_service',
    'normalize_question_point_ids',
    'question_batch_delete',
    'question_create',
    'question_delete',
    'question_detail',
    'question_export',
    'question_import',
    'question_link_knowledge',
    'question_list',
    'question_template',
    'question_update',
    'resource_create',
    'resource_delete',
    'resource_link_knowledge',
    'resource_list',
    'resource_update',
    'resource_upload',
]
