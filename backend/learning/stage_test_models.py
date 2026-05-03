"""阶段测试提交链路的共享数据结构与常量。"""

from __future__ import annotations

from dataclasses import dataclass

from assessments.models import Question


PASS_THRESHOLD = 60.0
TOTAL_SCORE = 100.0


# 维护意图：阶段测试评分结果和后续持久化所需上下文
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
