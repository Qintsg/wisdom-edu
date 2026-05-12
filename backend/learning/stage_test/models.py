"""阶段测试提交链路的共享数据结构与常量。"""

from __future__ import annotations

from dataclasses import dataclass

from assessments.models import Question


PASS_THRESHOLD = 60.0
TOTAL_SCORE = 100.0


@dataclass(frozen=True)
class StageTestEvaluation:
    """阶段测试评分结果和后续持久化所需上下文。"""

    answers: dict[str, object]
    questions: list[Question]
    question_map: dict[int, Question]
    point_stats: dict[int, dict[str, object]]
    question_details: list[dict[str, object]]
    detailed_mistakes: list[dict[str, object]]
    score: float
    passed: bool
    correct_count: int
    total_count: int
    accuracy: float
