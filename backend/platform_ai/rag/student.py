"""学生端 GraphRAG 编排服务兼容入口。"""
from __future__ import annotations

import logging

from courses.models import Course
from knowledge.models import KnowledgePoint, Resource
from learning.models import PathNode
from platform_ai.llm import llm_facade
from platform_ai.mcp import resource_mcp_service

from .corpus import build_course_graph_index, load_course_index, save_course_index, tokenize
from .resource_utils import (
    resource_rank_key as _resource_rank_key,
    safe_resource_url as _safe_url,
    score_resource_point_match as _score_resource_point_match,
)
from .runtime import student_graphrag_runtime
from .student_answer_mixin import StudentAnswerMixin
from .student_context_mixin import StudentContextMixin
from .student_dependencies import StudentRAGDependenciesMixin
from .student_index_mixin import StudentIndexMixin
from .student_point_path_mixin import StudentPointPathMixin
from .student_resource_mixin import StudentResourceRecommendationMixin
from .student_retrieval_mixin import StudentRetrievalMixin
from .student_utils import (
    InputItem,
    NormalizedItem,
    RankedContext,
    SourceList,
    append_internal_resource,
    bundle_mode as _bundle_mode,
    bundle_positive_ints as _bundle_positive_ints,
    bundle_query_modes as _bundle_query_modes,
    bundle_sources as _bundle_sources,
    dedupe_ints as _dedupe_ints,
    dedupe_strings as _dedupe_strings,
    humanize_document_title as _humanize_document_title,
    model_pk as _model_pk,
    normalize_nonempty_string as _normalize_nonempty_string,
    normalize_positive_int as _normalize_positive_int,
    ordered_unique as _ordered_unique,
    sanitize_answer_text as _sanitize_answer_text,
    to_float as _to_float,
    to_int as _to_int,
)


logger = logging.getLogger(__name__)


# 维护意图：学生端统一 GraphRAG 服务
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentLearningRAG(
    StudentResourceRecommendationMixin,
    StudentAnswerMixin,
    StudentPointPathMixin,
    StudentContextMixin,
    StudentRetrievalMixin,
    StudentIndexMixin,
    StudentRAGDependenciesMixin,
):
    """学生端统一 GraphRAG 服务。"""

    INDEX_VERSION = "neo4j_qdrant_graphrag_v2"


student_learning_rag = StudentLearningRAG()


__all__ = [
    'Course',
    'InputItem',
    'KnowledgePoint',
    'NormalizedItem',
    'PathNode',
    'RankedContext',
    'Resource',
    'SourceList',
    'StudentLearningRAG',
    '_bundle_mode',
    '_bundle_positive_ints',
    '_bundle_query_modes',
    '_bundle_sources',
    '_dedupe_ints',
    '_dedupe_strings',
    '_humanize_document_title',
    '_model_pk',
    '_normalize_nonempty_string',
    '_normalize_positive_int',
    '_ordered_unique',
    '_resource_rank_key',
    '_safe_url',
    '_sanitize_answer_text',
    '_score_resource_point_match',
    '_to_float',
    '_to_int',
    'append_internal_resource',
    'build_course_graph_index',
    'llm_facade',
    'load_course_index',
    'logger',
    'resource_mcp_service',
    'save_course_index',
    'student_graphrag_runtime',
    'student_learning_rag',
    'tokenize',
]
