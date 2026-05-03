"""GraphRAG 课程图社区检测与报告生成。"""

from __future__ import annotations

from collections import Counter
from typing import Protocol

import networkx as nx
from networkx.algorithms import community as nx_community

from .corpus_types import CorpusDocument, GraphEntity
from .corpus_utils import _top_themes


# 维护意图：Subset of GraphCorpusBuildState required for community reporting
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class CommunityBuildState(Protocol):
    """Subset of GraphCorpusBuildState required for community reporting."""

    course_id: int
    graph: nx.Graph
    documents: list[CorpusDocument]
    entities: dict[str, GraphEntity]


# 维护意图：Return deterministic graph communities for the current course graph
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def detect_communities(graph: nx.Graph) -> list[set[str]]:
    """Return deterministic graph communities for the current course graph."""
    if graph.number_of_nodes() == 0:
        return []
    if graph.number_of_edges() == 0:
        return [{str(node_id)} for node_id in graph.nodes]
    return [set(group) for group in nx_community.greedy_modularity_communities(graph)]


# 维护意图：Compute centrality with a stable single-node fallback
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def community_centrality(subgraph: nx.Graph) -> dict[str, float]:
    """Compute centrality with a stable single-node fallback."""
    if subgraph.number_of_nodes() <= 1:
        return {str(node_id): 1.0 for node_id in subgraph.nodes}
    return {str(node_id): score for node_id, score in nx.degree_centrality(subgraph).items()}


# 维护意图：Pick the highest-centrality entities for report highlights
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def select_top_node_ids(centrality: dict[str, float], limit: int = 6) -> list[str]:
    """Pick the highest-centrality entities for report highlights."""
    return [
        node_id
        for node_id, _ in sorted(
            centrality.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:limit]
    ]


# 维护意图：Count relationship types inside a detected community
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def relation_breakdown(subgraph: nx.Graph) -> Counter[str]:
    """Count relationship types inside a detected community."""
    return Counter(
        str(edge_data.get("relation_type", "related"))
        for _, _, edge_data in subgraph.edges(data=True)
    )


# 维护意图：Extract stable keywords from entity titles and summaries
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def community_themes(state: CommunityBuildState, community_nodes: set[str]) -> list[str]:
    """Extract stable keywords from entity titles and summaries."""
    return _top_themes(
        [
            f"{state.entities[node_id].title} {state.entities[node_id].summary}"
            for node_id in community_nodes
            if node_id in state.entities
        ]
    )


# 维护意图：Render a compact Chinese community report summary
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def community_summary(
    *,
    top_titles: list[str],
    relation_counter: Counter[str],
    themes: list[str],
) -> str:
    """Render a compact Chinese community report summary."""
    return (
        f"该社区围绕 {'、'.join(top_titles[:4]) or '课程核心实体'} 组织，"
        f"主要关系为 {'、'.join(relation_type for relation_type, _ in relation_counter.most_common(3)) or '关联'}，"
        f"主题集中在 {'、'.join(themes[:5]) or '课程核心知识'}。"
    )


# 维护意图：Build the serializable community payload
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_community_payload(
    *,
    community_id: str,
    community_nodes: set[str],
    top_node_ids: list[str],
    themes: list[str],
) -> dict[str, object]:
    """Build the serializable community payload."""
    return {
        "id": community_id,
        "entity_ids": sorted(community_nodes),
        "entity_count": len(community_nodes),
        "top_entities": top_node_ids,
        "themes": themes,
    }


# 维护意图：Build the human-readable community report payload
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_community_report(
    *,
    state: CommunityBuildState,
    community_id: str,
    community_index: int,
    top_node_ids: list[str],
    report_summary: str,
    themes: list[str],
    relation_counter: Counter[str],
) -> dict[str, object]:
    """Build the human-readable community report payload."""
    return {
        "community_id": community_id,
        "title": f"社区报告 {community_index}",
        "summary": report_summary,
        "themes": themes,
        "top_entities": [
            {
                "id": node_id,
                "title": state.entities[node_id].title,
                "entity_type": state.entities[node_id].entity_type,
            }
            for node_id in top_node_ids
            if node_id in state.entities
        ],
        "relation_breakdown": dict(relation_counter),
    }


# 维护意图：Append the synthetic community report document used by retrieval
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def append_community_document(
    *,
    state: CommunityBuildState,
    community_id: str,
    community_index: int,
    community_nodes: set[str],
    report_summary: str,
    themes: list[str],
) -> None:
    """Append the synthetic community report document used by retrieval."""
    state.documents.append(
        CorpusDocument(
            id=community_id,
            kind="community_report",
            title=f"社区报告 {community_index}",
            content=report_summary,
            url="",
            metadata={
                "course_id": state.course_id,
                "community_id": community_id,
                "themes": themes,
                "entity_ids": sorted(community_nodes),
            },
        )
    )


# 维护意图：Build community payloads, reports, and synthetic report documents
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_community_records(state: CommunityBuildState) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Build community payloads, reports, and synthetic report documents."""
    community_payloads: list[dict[str, object]] = []
    community_reports: list[dict[str, object]] = []
    for community_index, community_nodes in enumerate(detect_communities(state.graph), start=1):
        subgraph = state.graph.subgraph(community_nodes)
        centrality = community_centrality(subgraph)
        top_node_ids = select_top_node_ids(centrality)
        top_titles = [state.entities[node_id].title for node_id in top_node_ids if node_id in state.entities]
        relation_counter = relation_breakdown(subgraph)
        themes = community_themes(state, community_nodes)
        community_id = f"community:{community_index}"
        report_summary = community_summary(
            top_titles=top_titles,
            relation_counter=relation_counter,
            themes=themes,
        )

        community_payloads.append(
            build_community_payload(
                community_id=community_id,
                community_nodes=community_nodes,
                top_node_ids=top_node_ids,
                themes=themes,
            )
        )
        community_reports.append(
            build_community_report(
                state=state,
                community_id=community_id,
                community_index=community_index,
                top_node_ids=top_node_ids,
                report_summary=report_summary,
                themes=themes,
                relation_counter=relation_counter,
            )
        )
        append_community_document(
            state=state,
            community_id=community_id,
            community_index=community_index,
            community_nodes=community_nodes,
            report_summary=report_summary,
            themes=themes,
        )
    return community_payloads, community_reports


__all__ = ["build_community_records"]
