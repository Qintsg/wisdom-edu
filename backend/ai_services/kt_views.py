"""知识追踪兼容视图。"""

from __future__ import annotations

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.logging_utils import build_log_message
from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from platform_ai.kt import knowledge_tracing_facade

logger = logging.getLogger(__name__)


# 维护意图：Run single-student mastery prediction from the compatibility endpoint
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def kt_predict(request):
    """Run single-student mastery prediction from the compatibility endpoint."""
    course_id = request.data.get("course_id")
    answer_history = request.data.get("answer_history", [])
    knowledge_points = request.data.get("knowledge_points", [])
    if not course_id:
        return error_response(msg="缺少课程ID")

    try:
        result = knowledge_tracing_facade.predict_mastery(
            user_id=request.user.id,
            course_id=course_id,
            answer_history=answer_history,
            knowledge_points=knowledge_points if knowledge_points else None,
        )
    except Exception as exc:
        logger.error(
            build_log_message(
                "kt.predict.fail", user_id=request.user.id,
                course_id=course_id, error=exc,
            )
        )
        return error_response(msg="知识追踪预测服务暂时不可用", code=500)
    return success_response(data=result)


# 维护意图：Expose active KT model metadata for frontend capability checks
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def kt_model_info(request):
    """Expose active KT model metadata for frontend capability checks."""
    return success_response(data=knowledge_tracing_facade.get_model_info())


# 维护意图：Run batch mastery prediction for teacher-side cohort analysis
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def kt_batch_predict(request):
    """Run batch mastery prediction for teacher-side cohort analysis."""
    user_histories = request.data.get("user_histories", [])
    if not user_histories:
        return error_response(msg="缺少用户历史数据")
    try:
        results = knowledge_tracing_facade.batch_predict(user_histories)
    except Exception as exc:
        logger.error(
            build_log_message(
                "kt.batch_predict.fail", count=len(user_histories), error=exc,
            )
        )
        return error_response(msg="批量知识追踪预测服务暂时不可用", code=500)
    return success_response(data={"results": results})


# 维护意图：Translate KT prediction output into learner-facing study recommendations
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def kt_recommendations(request):
    """Translate KT prediction output into learner-facing study recommendations."""
    course_id = request.data.get("course_id")
    predictions = request.data.get("predictions", {})
    threshold = request.data.get("threshold", 0.6)
    if not course_id or not predictions:
        return error_response(msg="缺少 course_id 或 predictions")
    try:
        recommendations = knowledge_tracing_facade.get_learning_recommendations(
            user_id=request.user.id,
            course_id=course_id,
            mastery_predictions=predictions,
            threshold=threshold,
        )
    except Exception as exc:
        logger.error(
            build_log_message(
                "kt.recommendations.fail", user_id=request.user.id,
                course_id=course_id, error=exc,
            )
        )
        return error_response(msg="学习建议生成服务暂时不可用", code=500)
    return success_response(data={"recommendations": recommendations})
