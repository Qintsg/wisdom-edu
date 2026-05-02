from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from common.logging_utils import build_log_message

logger = logging.getLogger(__name__)


class LLMFeedbackKTMixin:
    """作业反馈报告与知识追踪结果解释能力。"""

    def generate_feedback_report(
        self,
        exam_info: Dict,
        score: float,
        total_score: float,
        mistakes: List[Dict],
        kt_predictions: Dict = None,
    ) -> Dict[str, Any]:
        """
        生成考试反馈报告

        Args:
            exam_info: 考试信息
            score: 得分
            total_score: 总分
            mistakes: 错题列表
            kt_predictions: KT模型预测的知识点掌握度 {kp_id: mastery_rate}

        Returns:
            反馈报告
        """
        accuracy = score / total_score if total_score > 0 else 0

        # 分析错题涉及的知识点（丰富上下文数据）
        mistake_points = []
        for m in mistakes[:5]:  # 取前5个错题分析
            point = {
                "question_text": m.get("question_text", ""),
                "knowledge_point": m.get("knowledge_point_name", ""),
                "student_answer": m.get("student_answer", ""),
                "correct_answer": m.get("correct_answer", ""),
                "analysis": m.get("analysis", ""),
            }
            mistake_points.append({k: v for k, v in point.items() if v})

        # 确定表现等级
        if accuracy >= 0.9:
            level = "优秀"
            level_desc = "你的表现非常出色，已经很好地掌握了本次作业涉及的知识点"
        elif accuracy >= 0.8:
            level = "良好"
            level_desc = "你的表现良好，大部分知识点已经掌握"
        elif accuracy >= 0.7:
            level = "中等"
            level_desc = "你基本掌握了课程内容，但仍有提升空间"
        elif accuracy >= 0.6:
            level = "及格"
            level_desc = "你已达到本次作业的基本要求，但仍需加强对部分知识点的理解"
        else:
            level = "待提高"
            level_desc = "你需要加强基础知识的学习"

        prompt = f"""# 任务
基于学生的作业表现，生成鼓励性、有针对性的学习反馈报告。

# 作业信息
- 作业名称：{exam_info.get("title", "未知作业")}
- 作业类型：{exam_info.get("type", "课程作业")}
- 总分：{total_score}分 / 学生得分：{score}分 / 正确率：{accuracy * 100:.1f}%
- 表现等级：{level}（{level_desc}）
- 错题数量：{len(mistakes)}题

# 错题详情
{json.dumps(mistake_points, ensure_ascii=False, indent=2) if mistake_points else "无错题数据"}

# 知识追踪分析
{json.dumps(kt_predictions, ensure_ascii=False, indent=2) if kt_predictions else "暂无KT模型预测数据"}

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

        # 根据正确率生成降级分析
        if accuracy >= 0.9:
            analysis = f"{level_desc}！继续保持，可以挑战更高难度的内容，拓展知识广度。"
            recommendations = ["尝试更高难度的拓展题目", "帮助同学解答问题，巩固理解"]
            next_tasks = ["学习进阶知识点", "参与课程讨论和实践项目"]
        elif accuracy >= 0.7:
            analysis = f"{level_desc}。建议针对错题涉及的知识点进行专项复习。"
            recommendations = [
                "复习错题涉及的知识点",
                "多做同类型练习题",
                "整理错题笔记",
            ]
            next_tasks = ["完成针对性强化练习", "重做本次作业的错题"]
        elif accuracy >= 0.6:
            analysis = f"{level_desc}。需要系统复习课程内容，加强基础知识的理解。"
            recommendations = [
                "系统复习课程重点内容",
                "观看知识点讲解视频",
                "做基础练习题",
            ]
            next_tasks = ["重新学习薄弱知识点", "制定复习计划并执行"]
        else:
            analysis = f"{level_desc}。建议从基础概念开始重新学习，循序渐进地掌握知识。"
            recommendations = [
                "从基础概念开始学习",
                "多次观看教学视频",
                "寻求老师或同学帮助",
            ]
            next_tasks = [
                "制定详细学习计划",
                "从最基础的内容开始复习",
                "每日进行适量练习",
            ]
        summary = f"{exam_info.get('title', '本次作业')}得分{score}/{total_score}，正确率{accuracy * 100:.1f}%，{level_desc}。"

        fallback = {
            "summary": summary,
            "analysis": analysis,
            "knowledge_gaps": [
                m.get("analysis", "相关知识点")[:20] for m in mistakes[:3]
            ]
            if mistakes
            else [],
            "recommendations": recommendations,
            "next_tasks": next_tasks,
            "encouragement": "学习是一个渐进的过程，每一次努力都是进步。相信自己，持续学习一定会有收获！",
        }

        from common.config import AppConfig

        if not AppConfig.ai_feedback_enabled():
            logger.debug(
                build_log_message(
                    "llm.feedback.disabled",
                    provider=self.provider_name,
                    model=self.model_name,
                )
            )
            return fallback

        return self._call_with_fallback(prompt, "feedback_report", fallback)

    def analyze_knowledge_tracing_result(
        self,
        kt_result: Dict[str, Any],
        answer_history: List[Dict] = None,
        course_name: str = None,
        point_name_map: Dict[int, str] = None,
    ) -> Dict[str, Any]:
        """
        分析知识追踪结果，生成学习洞察报告

        基于 DKT 知识追踪模型的预测结果，生成深度学习分析报告。

        Args:
            kt_result: 知识追踪服务返回的预测结果字典
            answer_history: 答题历史记录列表
            course_name: 课程名称
            point_name_map: 知识点ID到名称的映射 {id: name}，用于将数字ID转换为可读名称

        Returns:
            dict: 包含学习洞察、趋势分析和改进建议的报告
        """
        predictions = kt_result.get("predictions", {})
        model_type = kt_result.get("model_type", "unknown")
        confidence = kt_result.get("confidence", 0)
        active_models = kt_result.get("active_models", [])

        # 将知识点ID映射为名称（如有映射表）
        _name = point_name_map or {}
        weak_points = {k: v for k, v in predictions.items() if v < 0.6}
        strong_points = {k: v for k, v in predictions.items() if v >= 0.8}

        named_predictions = {
            _name.get(int(k) if isinstance(k, (int, float)) else k, f"知识点{k}"): v
            for k, v in predictions.items()
        }
        named_weak = {
            _name.get(int(k) if isinstance(k, (int, float)) else k, f"知识点{k}"): v
            for k, v in weak_points.items()
        }

        # 统计分析
        if predictions:
            # 提取字段值
            avg_mastery = sum(predictions.values()) / len(predictions)
        else:
            avg_mastery = 0

        # 答题趋势分析
        if answer_history:
            total_questions = len(answer_history)
            correct_count = sum(1 for a in answer_history if a.get("correct", 0) == 1)
            recent_accuracy = (
                correct_count / total_questions if total_questions > 0 else 0
            )
        else:
            total_questions = 0
            recent_accuracy = 0

        prompt = f"""# 任务
基于知识追踪模型的预测结果，生成学习洞察报告。

# 知识追踪预测结果
- 使用模型：{", ".join([m.upper() for m in active_models]) if active_models else model_type.upper()}
- 预测置信度：{confidence * 100:.1f}%
- 课程：{course_name or "未知课程"}

## 各知识点预测掌握率
{json.dumps(named_predictions, ensure_ascii=False, indent=2)}

## 统计概要
- 总知识点数：{len(predictions)} / 平均掌握率：{avg_mastery * 100:.1f}%
- 薄弱知识点（<60%）：{len(weak_points)}个 / 优势知识点（≥80%）：{len(strong_points)}个
- 答题记录数：{total_questions} / 近期正确率：{recent_accuracy * 100:.1f}%

# JSON输出格式
{{
    "insight_summary": "学习状态核心洞察，基于模型预测的关键发现（60-100字）",
    "mastery_trend": "掌握度变化趋势分析和预判（40-60字）",
    "weak_point_analysis": ["薄弱知识点深度分析，说明可能原因，最多3项"],
    "improvement_strategy": ["针对性提升策略，具体可执行，最多3项"],
    "model_confidence_note": "关于预测置信度的解读和使用建议（30-50字）"
}}"""

        # 构建降级响应
        weak_analysis = []
        for point_id, mastery in list(weak_points.items())[:3]:
            name = _name.get(
                int(point_id) if isinstance(point_id, (int, float)) else point_id,
                f"知识点{point_id}",
            )
            weak_analysis.append(f"{name}掌握率仅{mastery * 100:.0f}%，需重点关注")

        improvement = [
            "针对薄弱知识点进行专项练习",
            "增加相关知识点的学习时间",
            "结合视频和文档多维度学习",
        ]

        fallback = {
            "insight_summary": f"基于{model_type.upper()}模型分析，你的整体掌握率为{avg_mastery * 100:.1f}%，有{len(weak_points)}个知识点需要加强。",
            "mastery_trend": "建议持续进行练习，关注薄弱知识点的掌握情况变化。",
            "weak_point_analysis": weak_analysis
            if weak_analysis
            else ["暂无明显薄弱知识点"],
            "improvement_strategy": improvement,
            "model_confidence_note": f"预测置信度{confidence * 100:.0f}%，结果可作为学习规划参考。",
        }

        return self._call_with_fallback(prompt, "kt_analysis", fallback)
