"""MEFKT 题型与特征槽位常量。"""

from __future__ import annotations


QUESTION_TYPE_VOCAB: dict[str, int] = {
    "unknown": 0,
    "single_choice": 1,
    "multiple_choice": 2,
    "true_false": 3,
    "fill_blank": 4,
    "short_answer": 5,
    "code": 6,
}

NODE_FEATURE_SCHEMA: tuple[str, ...] = (
    "difficulty_proxy",
    "response_time_proxy",
    "occurrence_proxy",
    "degree_norm",
    "two_hop_density",
    "neighbor_difficulty",
    "knowledge_count_norm",
    "resource_count_norm",
    "prerequisite_count_norm",
    "dependent_count_norm",
    "related_count_norm",
    "chapter_position_norm",
    "content_length_norm",
    "analysis_length_norm",
    "question_score_norm",
    "historical_correct_rate",
)

RELATION_STAT_SCHEMA: tuple[str, ...] = (
    "degree_norm",
    "two_hop_density",
    "knowledge_overlap",
    "resource_overlap",
)


__all__ = ["QUESTION_TYPE_VOCAB", "NODE_FEATURE_SCHEMA", "RELATION_STAT_SCHEMA"]
