"""
知识图谱模块 - URL路由配置

API命名规范：
- /api/student/* - 学生专用接口
- /api/teacher/* - 教师专用接口
"""

from django.urls import path
from knowledge.api import map as map_views
from knowledge.api import resources as resource_views
from knowledge.api.teacher import map as teacher_map_views
from knowledge.api.teacher import point as teacher_point_views
from knowledge.api.teacher import question as teacher_question_views
from knowledge.api.teacher import relation as teacher_relation_views
from knowledge.api.teacher import resource as teacher_resource_views

app_name = "knowledge"

urlpatterns = [
    # ============ 学生端 ============
    path(
        "api/student/knowledge-map", map_views.get_knowledge_map, name="get_knowledge_map"
    ),
    path(
        "api/student/knowledge-points/<int:point_id>",
        map_views.get_knowledge_point_detail,
        name="get_knowledge_point_detail",
    ),
    path(
        "api/student/knowledge-points/<int:point_id>/resources",
        resource_views.knowledge_point_resources,
        name="knowledge_point_resources",
    ),
    path(
        "api/student/knowledge/points",
        map_views.get_knowledge_points_list,
        name="get_knowledge_points_list",
    ),
    path(
        "api/student/knowledge/relations",
        map_views.get_knowledge_relations,
        name="get_knowledge_relations",
    ),
    path(
        "api/student/knowledge/mastery",
        map_views.get_knowledge_mastery,
        name="get_knowledge_mastery",
    ),
    path(
        "api/student/knowledge/mastery/update",
        map_views.update_knowledge_mastery,
        name="update_knowledge_mastery",
    ),
    path(
        "api/student/knowledge/search", resource_views.knowledge_search, name="knowledge_search"
    ),
    path(
        "api/student/resources",
        resource_views.get_student_resources,
        name="get_student_resources",
    ),
    # ============ 教师端 ============
    # 资源管理
    path(
        "api/teacher/resources",
        teacher_resource_views.resource_list,
        name="teacher_resource_list",
    ),
    path(
        "api/teacher/resources/create",
        teacher_resource_views.resource_create,
        name="teacher_resource_create",
    ),
    path(
        "api/teacher/resources/upload",
        teacher_resource_views.resource_upload,
        name="teacher_resource_upload",
    ),
    path(
        "api/teacher/resources/<int:resource_id>",
        teacher_resource_views.resource_update,
        name="teacher_resource_update",
    ),
    path(
        "api/teacher/resources/<int:resource_id>/delete",
        teacher_resource_views.resource_delete,
        name="teacher_resource_delete",
    ),
    path(
        "api/teacher/resources/<int:resource_id>/link-knowledge",
        teacher_resource_views.resource_link_knowledge,
        name="teacher_resource_link_knowledge",
    ),
    # 题库管理
    path(
        "api/teacher/questions",
        teacher_question_views.question_list,
        name="teacher_question_list",
    ),
    path(
        "api/teacher/questions/create",
        teacher_question_views.question_create,
        name="teacher_question_create",
    ),
    path(
        "api/teacher/questions/batch-delete",
        teacher_question_views.question_batch_delete,
        name="teacher_question_batch_delete",
    ),
    path(
        "api/teacher/questions/import",
        teacher_question_views.question_import,
        name="teacher_question_import",
    ),
    path(
        "api/teacher/questions/export",
        teacher_question_views.question_export,
        name="teacher_question_export",
    ),
    path(
        "api/teacher/questions/template",
        teacher_question_views.question_template,
        name="teacher_question_template",
    ),
    path(
        "api/teacher/questions/<int:question_id>",
        teacher_question_views.question_detail,
        name="teacher_question_detail",
    ),
    path(
        "api/teacher/questions/<int:question_id>/update",
        teacher_question_views.question_update,
        name="teacher_question_update",
    ),
    path(
        "api/teacher/questions/<int:question_id>/delete",
        teacher_question_views.question_delete,
        name="teacher_question_delete",
    ),
    path(
        "api/teacher/questions/<int:question_id>/link-knowledge",
        teacher_question_views.question_link_knowledge,
        name="teacher_question_link_knowledge",
    ),
    # 知识图谱管理
    path(
        "api/teacher/knowledge-relations",
        teacher_relation_views.knowledge_relation_list,
        name="teacher_knowledge_relation_list",
    ),
    path(
        "api/teacher/knowledge-relations/create",
        teacher_relation_views.knowledge_relation_create,
        name="teacher_knowledge_relation_create",
    ),
    path(
        "api/teacher/knowledge-relations/<int:relation_id>",
        teacher_relation_views.knowledge_relation_delete,
        name="teacher_knowledge_relation_delete",
    ),
    path(
        "api/teacher/knowledge-points",
        teacher_point_views.knowledge_point_list,
        name="teacher_knowledge_point_list",
    ),
    path(
        "api/teacher/knowledge-points/create",
        teacher_point_views.knowledge_point_create,
        name="teacher_knowledge_point_create",
    ),
    path(
        "api/teacher/knowledge-points/<int:point_id>",
        teacher_point_views.knowledge_point_update,
        name="teacher_knowledge_point_update",
    ),
    path(
        "api/teacher/knowledge-points/<int:point_id>/delete",
        teacher_point_views.knowledge_point_delete,
        name="teacher_knowledge_point_delete",
    ),
    path(
        "api/teacher/knowledge-map/import",
        teacher_map_views.knowledge_map_import,
        name="teacher_knowledge_map_import",
    ),
    path(
        "api/teacher/knowledge-map/save",
        teacher_map_views.knowledge_graph_save,
        name="teacher_knowledge_graph_save",
    ),
    path(
        "api/teacher/knowledge-map/publish",
        teacher_map_views.knowledge_map_publish,
        name="teacher_knowledge_map_publish",
    ),
    path(
        "api/teacher/knowledge-map/build-rag-index",
        teacher_map_views.knowledge_map_build_rag_index,
        name="teacher_knowledge_map_build_rag_index",
    ),
    path(
        "api/teacher/knowledge-map/export",
        teacher_map_views.knowledge_map_export,
        name="teacher_knowledge_map_export",
    ),
    path(
        "api/teacher/knowledge-map/template",
        teacher_map_views.knowledge_map_template,
        name="teacher_knowledge_map_template",
    ),
]
