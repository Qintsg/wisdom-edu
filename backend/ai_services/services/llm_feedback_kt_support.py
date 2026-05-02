"""LLM 作业反馈与 KT 洞察 prompt 组装工具。"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class FeedbackPerformance:
    """学生作业表现等级与降级建议。"""

    level: str
    level_desc: str
    analysis: str
    recommendations: list[str]
    next_tasks: list[str]


@dataclass(frozen=True)
class FeedbackReportInput:
    """作业反馈报告生成所需输入。"""

    exam_info: Mapping[str, object]
    score: float
    total_score: float
    mistakes: Sequence[Mapping[str, object]]
    kt_predictions: Mapping[object, object] | None

    @property
    def accuracy(self) -> float:
        """返回本次作业正确率。"""
        return self.score / self.total_score if self.total_score > 0 else 0.0


@dataclass(frozen=True)
class KTPredictionSummary:
    """KT 预测结果的可读统计摘要。"""

    named_predictions: dict[str, float]
    weak_points: dict[object, float]
    strong_points: dict[object, float]
    named_weak: dict[str, float]
    avg_mastery: float


@dataclass(frozen=True)
class KTAnswerTrend:
    """答题历史趋势统计。"""

    total_questions: int
    recent_accuracy: float


@dataclass(frozen=True)
class KTAnalysisInput:
    """KT 洞察报告生成所需输入。"""

    kt_result: Mapping[str, object]
    answer_history: Sequence[Mapping[str, object]] | None
    course_name: str | None
    point_name_map: Mapping[int, str] | None


def build_mistake_points(mistakes: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """提取前 5 道错题的可读上下文。"""
    mistake_points: list[dict[str, object]] = []
    for mistake in mistakes[:5]:
        point = {
            "question_text": mistake.get("question_text", ""),
            "knowledge_point": mistake.get("knowledge_point_name", ""),
            "student_answer": mistake.get("student_answer", ""),
            "correct_answer": mistake.get("correct_answer", ""),
            "analysis": mistake.get("analysis", ""),
        }
        mistake_points.append({key: value for key, value in point.items() if value})
    return mistake_points


def classify_feedback_performance(accuracy: float) -> FeedbackPerformance:
    """根据正确率生成表现等级和降级学习建议。"""
    if accuracy >= 0.9:
        return FeedbackPerformance(
            level="优秀",
            level_desc="你的表现非常出色，已经很好地掌握了本次作业涉及的知识点",
            analysis="你的表现非常出色，已经很好地掌握了本次作业涉及的知识点！继续保持，可以挑战更高难度的内容，拓展知识广度。",
            recommendations=["尝试更高难度的拓展题目", "帮助同学解答问题，巩固理解"],
            next_tasks=["学习进阶知识点", "参与课程讨论和实践项目"],
        )
    if accuracy >= 0.8:
        return FeedbackPerformance(
            level="良好",
            level_desc="你的表现良好，大部分知识点已经掌握",
            analysis="你的表现良好，大部分知识点已经掌握。建议针对错题涉及的知识点进行专项复习。",
            recommendations=["复习错题涉及的知识点", "多做同类型练习题", "整理错题笔记"],
            next_tasks=["完成针对性强化练习", "重做本次作业的错题"],
        )
    if accuracy >= 0.7:
        return FeedbackPerformance(
            level="中等",
            level_desc="你基本掌握了课程内容，但仍有提升空间",
            analysis="你基本掌握了课程内容，但仍有提升空间。建议针对错题涉及的知识点进行专项复习。",
            recommendations=["复习错题涉及的知识点", "多做同类型练习题", "整理错题笔记"],
            next_tasks=["完成针对性强化练习", "重做本次作业的错题"],
        )
    if accuracy >= 0.6:
        return FeedbackPerformance(
            level="及格",
            level_desc="你已达到本次作业的基本要求，但仍需加强对部分知识点的理解",
            analysis="你已达到本次作业的基本要求，但仍需加强对部分知识点的理解。需要系统复习课程内容，加强基础知识的理解。",
            recommendations=["系统复习课程重点内容", "观看知识点讲解视频", "做基础练习题"],
            next_tasks=["重新学习薄弱知识点", "制定复习计划并执行"],
        )
    return FeedbackPerformance(
        level="待提高",
        level_desc="你需要加强基础知识的学习",
        analysis="你需要加强基础知识的学习。建议从基础概念开始重新学习，循序渐进地掌握知识。",
        recommendations=["从基础概念开始学习", "多次观看教学视频", "寻求老师或同学帮助"],
        next_tasks=["制定详细学习计划", "从最基础的内容开始复习", "每日进行适量练习"],
    )


def build_feedback_report_prompt(report_input: FeedbackReportInput) -> str:
    """构造作业反馈报告 prompt。"""
    mistake_points = build_mistake_points(report_input.mistakes)
    performance = classify_feedback_performance(report_input.accuracy)
    return f"""# 任务
基于学生的作业表现，生成鼓励性、有针对性的学习反馈报告。

# 作业信息
- 作业名称：{report_input.exam_info.get("title", "未知作业")}
- 作业类型：{report_input.exam_info.get("type", "课程作业")}
- 总分：{report_input.total_score}分 / 学生得分：{report_input.score}分 / 正确率：{report_input.accuracy * 100:.1f}%
- 表现等级：{performance.level}（{performance.level_desc}）
- 错题数量：{len(report_input.mistakes)}题

# 错题详情
{json.dumps(mistake_points, ensure_ascii=False, indent=2) if mistake_points else "无错题数据"}

# 知识追踪分析
{json.dumps(report_input.kt_predictions, ensure_ascii=False, indent=2) if report_input.kt_predictions else "暂无KT模型预测数据"}

# JSON输出格式
{{
    "summary": "一句话摘要，先概括结果再点出最关键的改进方向（40-70字）",
    "analysis": "表现分析，包含整体评价、亮点和不足（80-120字）",
    "knowledge_gaps": ["需要加强的知识点或能力缺口，最多3项"],
    "recommendations": ["具体的改进建议，可操作性强，最多3项"],
    "next_tasks": ["下一步学习任务，包含具体行动，最多3项"],
    "encouragement": "鼓励性话语，激发学习动力（30-50字）"
}}

# 反馈原则
1. 先肯定进步，再指出不足
2. 建议要具体、可执行
3. 根据表现等级调整建议的难度"""


def build_feedback_report_fallback(report_input: FeedbackReportInput) -> dict[str, object]:
    """构造作业反馈报告降级响应。"""
    performance = classify_feedback_performance(report_input.accuracy)
    summary = (
        f"{report_input.exam_info.get('title', '本次作业')}得分{report_input.score}/{report_input.total_score}，"
        f"正确率{report_input.accuracy * 100:.1f}%，{performance.level_desc}。"
    )
    return {
        "summary": summary,
        "analysis": performance.analysis,
        "knowledge_gaps": [
            str(mistake.get("analysis", "相关知识点"))[:20]
            for mistake in report_input.mistakes[:3]
        ]
        if report_input.mistakes
        else [],
        "recommendations": performance.recommendations,
        "next_tasks": performance.next_tasks,
        "encouragement": "学习是一个渐进的过程，每一次努力都是进步。相信自己，持续学习一定会有收获！",
    }


def summarize_kt_predictions(
    predictions: Mapping[object, object],
    point_name_map: Mapping[int, str] | None,
) -> KTPredictionSummary:
    """将 KT 预测结果转换为可展示名称和统计数据。"""
    numeric_predictions = {
        point_id: float(mastery)
        for point_id, mastery in predictions.items()
        if isinstance(mastery, (int, float))
    }
    name_map = point_name_map or {}
    weak_points = {key: value for key, value in numeric_predictions.items() if value < 0.6}
    strong_points = {key: value for key, value in numeric_predictions.items() if value >= 0.8}
    named_predictions = {
        readable_point_name(point_id, name_map): mastery
        for point_id, mastery in numeric_predictions.items()
    }
    named_weak = {
        readable_point_name(point_id, name_map): mastery
        for point_id, mastery in weak_points.items()
    }
    avg_mastery = sum(numeric_predictions.values()) / len(numeric_predictions) if numeric_predictions else 0.0
    return KTPredictionSummary(
        named_predictions=named_predictions,
        weak_points=weak_points,
        strong_points=strong_points,
        named_weak=named_weak,
        avg_mastery=avg_mastery,
    )


def readable_point_name(point_id: object, point_name_map: Mapping[int, str]) -> str:
    """将知识点 ID 转成可读名称。"""
    normalized_id = int(point_id) if isinstance(point_id, (int, float)) else point_id
    return point_name_map.get(normalized_id, f"知识点{point_id}") if isinstance(normalized_id, int) else f"知识点{point_id}"


def summarize_answer_trend(answer_history: Sequence[Mapping[str, object]] | None) -> KTAnswerTrend:
    """统计答题历史数量和近期正确率。"""
    if not answer_history:
        return KTAnswerTrend(total_questions=0, recent_accuracy=0.0)
    total_questions = len(answer_history)
    correct_count = sum(1 for answer in answer_history if answer.get("correct", 0) == 1)
    return KTAnswerTrend(
        total_questions=total_questions,
        recent_accuracy=correct_count / total_questions if total_questions > 0 else 0.0,
    )


def build_kt_analysis_prompt(analysis_input: KTAnalysisInput) -> str:
    """构造 KT 学习洞察 prompt。"""
    predictions = analysis_input.kt_result.get("predictions", {})
    prediction_map = predictions if isinstance(predictions, Mapping) else {}
    prediction_summary = summarize_kt_predictions(prediction_map, analysis_input.point_name_map)
    answer_trend = summarize_answer_trend(analysis_input.answer_history)
    model_type = str(analysis_input.kt_result.get("model_type", "unknown"))
    confidence = float(analysis_input.kt_result.get("confidence", 0) or 0)
    active_models = analysis_input.kt_result.get("active_models", [])
    active_model_text = (
        ", ".join([str(model).upper() for model in active_models])
        if isinstance(active_models, list) and active_models
        else model_type.upper()
    )
    return f"""# 任务
基于知识追踪模型的预测结果，生成学习洞察报告。

# 知识追踪预测结果
- 使用模型：{active_model_text}
- 预测置信度：{confidence * 100:.1f}%
- 课程：{analysis_input.course_name or "未知课程"}

## 各知识点预测掌握率
{json.dumps(prediction_summary.named_predictions, ensure_ascii=False, indent=2)}

## 统计概要
- 总知识点数：{len(prediction_summary.named_predictions)} / 平均掌握率：{prediction_summary.avg_mastery * 100:.1f}%
- 薄弱知识点（<60%）：{len(prediction_summary.weak_points)}个 / 优势知识点（≥80%）：{len(prediction_summary.strong_points)}个
- 答题记录数：{answer_trend.total_questions} / 近期正确率：{answer_trend.recent_accuracy * 100:.1f}%

# JSON输出格式
{{
    "insight_summary": "学习状态核心洞察，基于模型预测的关键发现（60-100字）",
    "mastery_trend": "掌握度变化趋势分析和预判（40-60字）",
    "weak_point_analysis": ["薄弱知识点深度分析，说明可能原因，最多3项"],
    "improvement_strategy": ["针对性提升策略，具体可执行，最多3项"],
    "model_confidence_note": "关于预测置信度的解读和使用建议（30-50字）"
}}"""


def build_kt_analysis_fallback(analysis_input: KTAnalysisInput) -> dict[str, object]:
    """构造 KT 学习洞察降级响应。"""
    predictions = analysis_input.kt_result.get("predictions", {})
    prediction_map = predictions if isinstance(predictions, Mapping) else {}
    prediction_summary = summarize_kt_predictions(prediction_map, analysis_input.point_name_map)
    weak_analysis = build_weak_point_analysis(
        prediction_summary.weak_points,
        analysis_input.point_name_map or {},
    )
    model_type = str(analysis_input.kt_result.get("model_type", "unknown"))
    confidence = float(analysis_input.kt_result.get("confidence", 0) or 0)
    return {
        "insight_summary": (
            f"基于{model_type.upper()}模型分析，你的整体掌握率为{prediction_summary.avg_mastery * 100:.1f}%，"
            f"有{len(prediction_summary.weak_points)}个知识点需要加强。"
        ),
        "mastery_trend": "建议持续进行练习，关注薄弱知识点的掌握情况变化。",
        "weak_point_analysis": weak_analysis if weak_analysis else ["暂无明显薄弱知识点"],
        "improvement_strategy": [
            "针对薄弱知识点进行专项练习",
            "增加相关知识点的学习时间",
            "结合视频和文档多维度学习",
        ],
        "model_confidence_note": f"预测置信度{confidence * 100:.0f}%，结果可作为学习规划参考。",
    }


def build_weak_point_analysis(
    weak_points: Mapping[object, float],
    point_name_map: Mapping[int, str],
) -> list[str]:
    """构造最多 3 条薄弱知识点分析。"""
    weak_analysis: list[str] = []
    for point_id, mastery in list(weak_points.items())[:3]:
        name = readable_point_name(point_id, point_name_map)
        weak_analysis.append(f"{name}掌握率仅{mastery * 100:.0f}%，需重点关注")
    return weak_analysis
