"""
教师端知识管理共享工具。

集中放置分页、CSV 响应、知识点关联和 RAG 索引刷新等跨端点复用逻辑。
"""
from __future__ import annotations

import codecs
import logging
from collections.abc import Iterable
from typing import Protocol, cast

from django.http import HttpResponse
from rest_framework.request import Request
from rest_framework.response import Response

from assessments.models import Question
from common.responses import error_response

from .models import KnowledgePoint, Resource


logger = logging.getLogger(__name__)
UTF8_BOM = codecs.BOM_UTF8.decode("utf-8")
KnowledgePointReference = int | str | KnowledgePoint


# 维护意图：支持 set 的知识点关系管理器协议
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgePointRelationSetter(Protocol):
    """支持 set 的知识点关系管理器协议。"""

    # 维护意图：替换知识点关联
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def set(self, points: Iterable[KnowledgePointReference]) -> None:
        """替换知识点关联。"""


# 维护意图：支持 add 的知识点关系管理器协议
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgePointRelationAdder(Protocol):
    """支持 add 的知识点关系管理器协议。"""

    # 维护意图：追加知识点关联
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def add(self, *points: KnowledgePoint) -> None:
        """追加知识点关联。"""


# 维护意图：返回 400 错误响应
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bad_request(msg: str) -> Response:
    """返回 400 错误响应。"""
    return error_response(msg=msg)


# 维护意图：解析分页参数
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_pagination(
    request: Request,
    *,
    size_keys: tuple[str, ...] = ("page_size", "size"),
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    """解析分页参数。"""
    try:
        page = max(1, int(request.query_params.get("page", 1)))
        size = default_size
        for size_key in size_keys:
            size_value = request.query_params.get(size_key)
            if size_value not in (None, ""):
                size = int(size_value)
                break
        size = min(max(1, size), max_size)
    except (ValueError, TypeError):
        page = 1
        size = default_size
    return page, size


# 维护意图：统一替换多对多知识点关联
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def replace_knowledge_points(
    relation_manager: KnowledgePointRelationSetter,
    point_values: Iterable[KnowledgePointReference],
) -> None:
    """统一替换多对多知识点关联。"""
    relation_manager.set(point_values)


# 维护意图：从请求中提取必填知识点 ID 列表
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def require_point_ids(request: Request) -> tuple[list[int | str], Response | None]:
    """从请求中提取必填知识点 ID 列表。"""
    raw_point_ids = request.data.get("knowledge_point_ids", [])
    if isinstance(raw_point_ids, list):
        point_ids = raw_point_ids
    elif raw_point_ids in (None, ""):
        point_ids = []
    else:
        point_ids = [raw_point_ids]

    if not point_ids:
        return [], bad_request("请提供知识点ID列表")
    return point_ids, None


# 维护意图：为资源或题目补充知识点关联并刷新 RAG 索引
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def link_knowledge_points(target: Resource | Question, point_ids: list[int | str]) -> int:
    """为资源或题目补充知识点关联并刷新 RAG 索引。"""
    points = list(KnowledgePoint.objects.filter(id__in=point_ids, course_id=target.course_id))
    cast(KnowledgePointRelationAdder, target.knowledge_points).add(*points)
    refresh_course_rag_index(target.course_id)
    return len(points)


# 维护意图：提取题目的导出答案文本
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_question_answer_text(question: Question) -> str:
    """提取题目的导出答案文本。"""
    answer_payload = question.answer if isinstance(question.answer, dict) else {}
    answer_value = answer_payload.get("answer")
    if answer_value not in (None, ""):
        return str(answer_value)
    answers = answer_payload.get("answers")
    if isinstance(answers, list):
        return ",".join(str(answer) for answer in answers if answer is not None)
    return ""


# 维护意图：构造带 BOM 的 CSV 下载响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_csv_download_response(filename: str) -> HttpResponse:
    """构造带 BOM 的 CSV 下载响应。"""
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(UTF8_BOM)
    return response


# 维护意图：在知识图谱、题库、资源变更后刷新课程级 RAG 索引
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def refresh_course_rag_index(course_id: int) -> None:
    """在知识图谱、题库、资源变更后刷新课程级 RAG 索引。"""
    try:
        from tools.rag_index import refresh_rag_corpus

        refresh_rag_corpus(course_id=course_id)
        logger.info("课程 RAG 索引刷新成功: course=%s", course_id)
    except Exception as error:
        logger.warning("课程 RAG 索引刷新失败: course=%s error=%s", course_id, error)
