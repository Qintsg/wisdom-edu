"""学生端 GraphRAG 编排服务。"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Sequence
from dataclasses import dataclass
import logging
from typing import TypeAlias, TypeVar

from courses.models import Course
from knowledge.models import KnowledgePoint, Resource
from learning.models import PathNode
from platform_ai.llm import llm_facade

from .corpus import build_course_graph_index, load_course_index, save_course_index, tokenize
from .runtime import student_graphrag_runtime


logger = logging.getLogger(__name__)


SourceList: TypeAlias = list[dict[str, object]]
InputItem = TypeVar("InputItem")
NormalizedItem = TypeVar("NormalizedItem", bound=Hashable)


def _to_int(value: object, default: int = 0) -> int:
	"""将未知输入稳健转换为整数。"""
	if isinstance(value, bool):
		return int(value)
	if isinstance(value, int):
		return value
	if isinstance(value, float):
		return int(value)
	if isinstance(value, str):
		try:
			return int(value.strip())
		except ValueError:
			return default
	try:
		return int(str(value).strip())
	except (TypeError, ValueError):
		return default


def _to_float(value: object, default: float = 0.0) -> float:
	"""将未知输入稳健转换为浮点数。"""
	if isinstance(value, bool):
		return float(int(value))
	if isinstance(value, (int, float)):
		return float(value)
	if isinstance(value, str):
		try:
			return float(value.strip())
		except ValueError:
			return default
	try:
		return float(str(value).strip())
	except (TypeError, ValueError):
		return default


def _model_pk(instance: object) -> int:
	"""以类型安全方式读取 Django 模型主键。"""
	return _to_int(getattr(instance, "id", 0))


def _ordered_unique(
	items: Iterable[InputItem],
	normalize: Callable[[InputItem], NormalizedItem | None],
) -> list[NormalizedItem]:
	"""按归一化结果去重并保留原始顺序。"""
	seen: set[NormalizedItem] = set()
	ordered: list[NormalizedItem] = []
	for item in items:
		normalized = normalize(item)
		if normalized is None or normalized in seen:
			continue
		seen.add(normalized)
		ordered.append(normalized)
	return ordered


def _normalize_nonempty_string(item: str) -> str | None:
	"""将字符串规整为可去重的非空值。"""
	normalized = item.strip()
	return normalized or None


def _normalize_positive_int(item: int) -> int | None:
	"""过滤非正整数，避免无效主键进入结果。"""
	if item <= 0:
		return None
	return item


def _bundle_sources(bundle: dict[str, object]) -> SourceList:
	"""从上下文包中安全提取 source 列表。"""
	raw_sources = bundle.get("sources")
	if not isinstance(raw_sources, list):
		return []
	sources: SourceList = []
	for item in raw_sources:
		if isinstance(item, dict):
			sources.append(item)
	return sources


def _bundle_mode(bundle: dict[str, object], fallback: str) -> str:
	"""读取 GraphRAG bundle 的模式信息并保底。"""
	if not _bundle_sources(bundle):
		return fallback
	return str(bundle.get("mode", "")).strip() or fallback


def _bundle_query_modes(
	bundle: dict[str, object],
	base_modes: Sequence[str] = ("local", "global", "drift"),
) -> list[str]:
	"""合并 bundle 返回的查询模式，保留默认顺序。"""
	query_modes = list(base_modes)
	raw_query_modes = bundle.get("query_modes")
	if not isinstance(raw_query_modes, list):
		return query_modes
	for raw_mode in raw_query_modes:
		normalized_mode = str(raw_mode).strip()
		if normalized_mode and normalized_mode not in query_modes:
			query_modes.append(normalized_mode)
	return query_modes


def _bundle_positive_ints(bundle: dict[str, object], key: str) -> list[int]:
	"""从 bundle 中提取去重后的正整数列表。"""
	raw_values = bundle.get(key)
	if not isinstance(raw_values, list):
		return []
	return _dedupe_ints(_to_int(raw_value) for raw_value in raw_values)


def _safe_url(resource: Resource) -> str:
	"""返回资源的稳定可访问地址。"""
	if resource.url:
		return resource.url
	if resource.file:
		try:
			return str(resource.file.url)
		except (AttributeError, OSError, ValueError):
			return ""
	return ""


def _resource_rank_key(resource: Resource, mastery_value: float | None) -> tuple[int, int, int, str]:
	"""根据当前掌握度对内部资源进行稳定排序。"""
	# 掌握度低时优先视频/文档，掌握度高时允许练习前置。
	beginner_priority = {
		"video": 0,
		"document": 1,
		"exercise": 2,
		"link": 3,
	}
	advanced_priority = {
		"exercise": 0,
		"video": 1,
		"document": 2,
		"link": 3,
	}
	is_advanced = mastery_value is not None and mastery_value >= 0.7
	priority_map = advanced_priority if is_advanced else beginner_priority
	type_rank = priority_map.get(resource.resource_type, 9)
	# sort_order 越小越靠前；无时长资源排到后面，便于优先推荐更完整内容。
	duration_rank = resource.duration or 10**9
	return (type_rank, int(resource.sort_order or 0), duration_rank, resource.title)


def _dedupe_strings(items: Iterable[str]) -> list[str]:
	"""保持原始顺序去重字符串列表。"""
	return _ordered_unique(items, _normalize_nonempty_string)


def _dedupe_ints(items: Iterable[int]) -> list[int]:
	"""保持原始顺序去重整数列表。"""
	return _ordered_unique(items, _normalize_positive_int)


def _sanitize_answer_text(text: str) -> str:
	"""压缩多余空白，避免回答出现长段空行。"""
	return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _humanize_document_title(document: dict[str, object]) -> str:
	"""将索引文档标题转为更适合前端展示的名称。"""
	kind = str(document.get("kind", "")).strip()
	title = str(document.get("title", "")).strip()
	if title:
		return title
	if kind == "knowledge_point":
		return "知识点"
	if kind == "community_report":
		return "社区报告"
	if kind == "resource":
		return "课程资源"
	if kind == "question":
		return "练习题"
	return "课程证据"


def append_internal_resource(
	bucket: list[dict[str, object]],
	resource: Resource,
	reason: str,
	completed_resource_ids: set[str],
	learning_tips: str,
) -> None:
	"""将内部资源追加为统一的前端响应结构。"""
	bucket.append(
		{
			"resource_id": _model_pk(resource),
			"title": resource.title,
			"type": resource.resource_type,
			"url": _safe_url(resource),
			"description": resource.description or "",
			"duration": resource.duration,
			"required": resource.resource_type in {"video", "document"},
			"recommended_reason": reason,
			"learning_tips": learning_tips,
			"is_internal": True,
			"completed": str(_model_pk(resource)) in completed_resource_ids,
		}
	)


@dataclass(frozen=True)
class RankedContext:
	"""承载单一 GraphRAG 查询模式的上下文结果。"""

	context: str
	sources: list[dict[str, object]]
	matched_entity_ids: list[str]


class StudentLearningRAG:
	"""学生端统一 GraphRAG 服务。"""

	INDEX_VERSION = "neo4j_qdrant_graphrag_v2"

	def build_index(
		self, course_id: int, persist: bool = True, force_rebuild: bool = False
	) -> dict[str, object]:
		"""构建课程 GraphRAG 索引。"""
		if not force_rebuild:
			payload = load_course_index(course_id)
			if payload.get("index_type") == self.INDEX_VERSION and payload.get("entities"):
				return payload

		payload = build_course_graph_index(course_id)
		payload["index_type"] = self.INDEX_VERSION
		try:
			payload["graph_rag_artifacts"] = student_graphrag_runtime.materialize_course_payload(course_id, payload)
		except Exception as error:
			logger.warning("课程 GraphRAG 物化失败，保留本地索引回退: course=%s error=%s", course_id, error)
			payload["graph_rag_artifacts"] = {
				"collection_name": student_graphrag_runtime.collection_name(course_id),
				"qdrant_path": str(student_graphrag_runtime.qdrant_directory()),
				"vector_points": 0,
				"embedder_provider": "degraded",
				"neo4j_projection_ready": False,
				"projected_documents": 0,
				"projected_relations": 0,
			}
		if persist:
			save_course_index(course_id, payload)
		return payload

	def _ensure_index(self, course_id: int, persist: bool = True) -> dict[str, object]:
		"""确保课程索引已可用，必要时自动重建。"""
		payload = load_course_index(course_id)
		if payload.get("index_type") == self.INDEX_VERSION and payload.get("entities"):
			try:
				payload["graph_rag_artifacts"] = student_graphrag_runtime.ensure_materialized(course_id, payload)
			except Exception as error:
				logger.warning("课程 GraphRAG 物化校验失败，继续使用本地索引: course=%s error=%s", course_id, error)
			return payload
		return self.build_index(course_id, persist=persist, force_rebuild=True)

	def _entity_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
		"""安全读取实体列表。"""
		raw_entities = payload.get("entities")
		if not isinstance(raw_entities, list):
			return []
		entities: list[dict[str, object]] = []
		for item in raw_entities:
			if isinstance(item, dict):
				entities.append(item)
		return entities

	def _relationship_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
		"""安全读取关系列表。"""
		raw_relationships = payload.get("relationships")
		if not isinstance(raw_relationships, list):
			return []
		relationships: list[dict[str, object]] = []
		for item in raw_relationships:
			if isinstance(item, dict):
				relationships.append(item)
		return relationships

	def _document_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
		"""安全读取文档列表。"""
		raw_documents = payload.get("documents")
		if not isinstance(raw_documents, list):
			return []
		documents: list[dict[str, object]] = []
		for item in raw_documents:
			if isinstance(item, dict):
				documents.append(item)
		return documents

	def _community_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
		"""安全读取社区列表。"""
		raw_communities = payload.get("communities")
		if not isinstance(raw_communities, list):
			return []
		communities: list[dict[str, object]] = []
		for item in raw_communities:
			if isinstance(item, dict):
				communities.append(item)
		return communities

	def _community_report_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
		"""安全读取社区报告列表。"""
		raw_reports = payload.get("community_reports")
		if not isinstance(raw_reports, list):
			return []
		reports: list[dict[str, object]] = []
		for item in raw_reports:
			if isinstance(item, dict):
				reports.append(item)
		return reports

	def _entity_map(self, payload: dict[str, object]) -> dict[str, dict[str, object]]:
		"""将实体列表转换为按实体 ID 索引的映射。"""
		entity_map: dict[str, dict[str, object]] = {}
		for entity in self._entity_list(payload):
			entity_id = str(entity.get("id", "")).strip()
			if entity_id:
				entity_map[entity_id] = entity
		return entity_map

	def _community_lookup(self, payload: dict[str, object]) -> dict[str, dict[str, object]]:
		"""构建社区 ID 到社区描述的映射。"""
		community_lookup: dict[str, dict[str, object]] = {}
		for community in self._community_list(payload):
			community_id = str(community.get("id", "")).strip()
			if community_id:
				community_lookup[community_id] = community
		return community_lookup

	def _entity_to_communities(self, payload: dict[str, object]) -> dict[str, list[str]]:
		"""构建实体到社区的反向索引。"""
		membership: dict[str, list[str]] = defaultdict(list)
		for community in self._community_list(payload):
			community_id = str(community.get("id", "")).strip()
			if not community_id:
				continue
			entity_ids = community.get("entity_ids")
			if not isinstance(entity_ids, list):
				continue
			for entity_id in entity_ids:
				normalized = str(entity_id).strip()
				if normalized:
					membership[normalized].append(community_id)
		return dict(membership)

	def _document_excerpt(self, document: dict[str, object], limit: int = 180) -> str:
		"""提取适合进入上下文窗口的证据片段。"""
		content = str(document.get("content", "")).strip()
		metadata = document.get("metadata")
		answer_hidden = False
		if isinstance(metadata, dict):
			answer_hidden = bool(metadata.get("answer_hidden", False))
		if answer_hidden:
			content = content.split("解析：", 1)[0].strip()
		excerpt = _sanitize_answer_text(content)
		return excerpt[:limit]

	def _extract_point_ids(self, entity_ids: Iterable[str]) -> set[int]:
		"""从实体 ID 集合中提取知识点数字 ID。"""
		point_ids: set[int] = set()
		for entity_id in entity_ids:
			if not entity_id.startswith("kp:"):
				continue
			_, _, raw_id = entity_id.partition(":")
			if raw_id.isdigit():
				point_ids.add(int(raw_id))
		return point_ids

	def _source_from_document(
		self,
		document: dict[str, object],
		query_mode: str,
		limit: int = 140,
	) -> dict[str, object]:
		"""将索引文档转成统一 source 结构。"""
		return {
			"id": str(document.get("id", "")).strip(),
			"title": _humanize_document_title(document),
			"kind": str(document.get("kind", "")).strip() or "document",
			"url": str(document.get("url", "")).strip(),
			"excerpt": self._document_excerpt(document, limit=limit),
			"query_mode": query_mode,
		}

	def _source_from_report(
		self,
		report: dict[str, object],
		query_mode: str,
	) -> dict[str, object]:
		"""将社区报告转成统一 source 结构。"""
		community_id = str(report.get("community_id", "")).strip()
		summary = _sanitize_answer_text(str(report.get("summary", "")))
		return {
			"id": community_id,
			"title": str(report.get("title", "")).strip() or "社区报告",
			"kind": "community_report",
			"url": "",
			"excerpt": summary[:160],
			"query_mode": query_mode,
		}

	def _source_from_graphrag_hit(
		self,
		hit,
		query_mode: str,
	) -> dict[str, object]:
		"""把官方 GraphRAG 检索命中转换为统一 source 结构。"""
		return hit.as_source(query_mode)

	def _merge_sources(self, *source_groups: list[dict[str, object]]) -> list[dict[str, object]]:
		"""按来源 ID 去重，保留最先出现的证据。"""
		merged: list[dict[str, object]] = []
		seen_ids: set[str] = set()
		for source_group in source_groups:
			for source in source_group:
				source_id = str(source.get("id", "")).strip()
				if not source_id or source_id in seen_ids:
					continue
				seen_ids.add(source_id)
				merged.append(source)
		return merged

	def _entity_score(
		self,
		entity: dict[str, object],
		query_tokens: set[str],
		seed_entity_ids: set[str],
	) -> float:
		"""计算实体与查询的相关性分数。"""
		entity_id = str(entity.get("id", "")).strip()
		if not entity_id:
			return -1.0

		metadata = entity.get("metadata")
		searchable_parts: list[str] = [
			str(entity.get("title", "")).strip(),
			str(entity.get("summary", "")).strip(),
		]
		if isinstance(metadata, dict):
			for value in metadata.values():
				if isinstance(value, str):
					searchable_parts.append(value)
				elif isinstance(value, list):
					searchable_parts.extend(str(item) for item in value)

		searchable_text = " ".join(part for part in searchable_parts if part).lower()
		entity_tokens = tokenize(searchable_text)
		token_overlap = len(query_tokens & entity_tokens)
		substring_bonus = 0.0
		for token in query_tokens:
			if token and token in searchable_text:
				substring_bonus += 1.0

		entity_type = str(entity.get("entity_type", "")).strip()
		type_bonus = {
			"knowledge_point": 1.2,
			"resource": 1.0,
			"chapter": 0.6,
			"question": 0.2,
		}.get(entity_type, 0.0)
		seed_bonus = 12.0 if entity_id in seed_entity_ids else 0.0
		return token_overlap * 3.0 + substring_bonus + type_bonus + seed_bonus

	def _rank_entities(
		self,
		payload: dict[str, object],
		query: str,
		seed_entity_ids: Iterable[str] = (),
		limit: int = 6,
	) -> list[dict[str, object]]:
		"""对实体进行局部查询排序。"""
		seed_ids = {entity_id for entity_id in seed_entity_ids if entity_id}
		query_tokens = tokenize(query)
		ranked: list[tuple[float, str, dict[str, object]]] = []

		for entity in self._entity_list(payload):
			score = self._entity_score(entity, query_tokens, seed_ids)
			if score <= 0 and str(entity.get("id", "")) not in seed_ids:
				continue
			ranked.append((score, str(entity.get("title", "")), entity))

		ranked.sort(key=lambda item: (-item[0], item[1]))
		return [entity for _, _, entity in ranked[:limit]]

	def _collect_neighbor_ids(
		self,
		payload: dict[str, object],
		focus_entity_ids: Iterable[str],
		limit: int = 8,
	) -> list[str]:
		"""从关系表中收集一跳邻居实体。"""
		focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
		scores: dict[str, float] = defaultdict(float)

		for relationship in self._relationship_list(payload):
			source_id = str(relationship.get("source", "")).strip()
			target_id = str(relationship.get("target", "")).strip()
			weight = _to_float(relationship.get("weight", 0.0))
			if source_id in focus_ids and target_id and target_id not in focus_ids:
				scores[target_id] += 1.0 + weight
			elif target_id in focus_ids and source_id and source_id not in focus_ids:
				scores[source_id] += 1.0 + weight

		ordered_ids = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
		return [entity_id for entity_id, _ in ordered_ids[:limit]]

	def _relationship_lines(
		self,
		payload: dict[str, object],
		focus_entity_ids: Iterable[str],
		limit: int = 8,
	) -> list[str]:
		"""将关系边转换为适合 prompt 的短句。"""
		focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
		entity_map = self._entity_map(payload)
		relation_lines: list[str] = []
		for relationship in self._relationship_list(payload):
			source_id = str(relationship.get("source", "")).strip()
			target_id = str(relationship.get("target", "")).strip()
			if source_id not in focus_ids and target_id not in focus_ids:
				continue
			source_title = str(entity_map.get(source_id, {}).get("title", source_id)).strip()
			target_title = str(entity_map.get(target_id, {}).get("title", target_id)).strip()
			relation_type = str(relationship.get("relation_type", "相关")).strip() or "相关"
			relation_lines.append(f"{source_title} -[{relation_type}]-> {target_title}")
			if len(relation_lines) >= limit:
				break
		return _dedupe_strings(relation_lines)

	def _rank_documents(
		self,
		payload: dict[str, object],
		query: str,
		focus_entity_ids: Iterable[str] = (),
		limit: int = 6,
		include_questions: bool = False,
	) -> list[dict[str, object]]:
		"""按 query 与焦点实体综合排序证据文档。"""
		query_tokens = tokenize(query)
		focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
		focus_point_ids = self._extract_point_ids(focus_ids)
		ranked_documents: list[tuple[float, str, dict[str, object]]] = []

		for document in self._document_list(payload):
			kind = str(document.get("kind", "")).strip()
			metadata = document.get("metadata")
			if kind == "question" and not include_questions:
				continue

			searchable_text = (
				f"{document.get('title', '')} {document.get('content', '')}"
			).lower()
			document_tokens = tokenize(searchable_text)
			token_overlap = len(query_tokens & document_tokens)
			score = float(token_overlap * 2)

			document_id = str(document.get("id", "")).strip()
			if document_id in focus_ids:
				score += 8.0

			if isinstance(metadata, dict):
				knowledge_point_ids = metadata.get("knowledge_point_ids")
				if isinstance(knowledge_point_ids, list):
					overlap = {
						int(item)
						for item in knowledge_point_ids
						if str(item).isdigit()
					} & focus_point_ids
					score += float(len(overlap) * 3)

				knowledge_point_id = metadata.get("knowledge_point_id")
				normalized_point_id = _to_int(knowledge_point_id, default=-1)
				if normalized_point_id in focus_point_ids:
					score += 3.0

			if score <= 0:
				continue
			ranked_documents.append((score, _humanize_document_title(document), document))

		ranked_documents.sort(key=lambda item: (-item[0], item[1]))
		return [document for _, _, document in ranked_documents[:limit]]

	def _rank_community_reports(
		self,
		payload: dict[str, object],
		query: str,
		focus_entity_ids: Iterable[str] = (),
		limit: int = 4,
	) -> list[dict[str, object]]:
		"""按查询与实体焦点排序社区报告。"""
		query_tokens = tokenize(query)
		focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
		community_lookup = self._community_lookup(payload)
		ranked_reports: list[tuple[float, str, dict[str, object]]] = []

		for report in self._community_report_list(payload):
			community_id = str(report.get("community_id", "")).strip()
			community = community_lookup.get(community_id, {})
			searchable_parts: list[str] = [
				str(report.get("title", "")).strip(),
				str(report.get("summary", "")).strip(),
			]
			themes = report.get("themes")
			if isinstance(themes, list):
				searchable_parts.extend(str(theme) for theme in themes)
			top_entities = report.get("top_entities")
			if isinstance(top_entities, list):
				for item in top_entities:
					if isinstance(item, dict):
						searchable_parts.append(str(item.get("title", "")))

			searchable_text = " ".join(part for part in searchable_parts if part).lower()
			score = float(len(query_tokens & tokenize(searchable_text)) * 4)

			entity_ids = community.get("entity_ids")
			if isinstance(entity_ids, list):
				entity_overlap = len({str(entity_id) for entity_id in entity_ids} & focus_ids)
				score += float(entity_overlap * 4)

			if score <= 0 and not focus_ids:
				continue
			ranked_reports.append((score, str(report.get("title", "")), report))

		ranked_reports.sort(key=lambda ranked_item: (-ranked_item[0], ranked_item[1]))
		return [report for _, _, report in ranked_reports[:limit]]

	def _build_local_context(
		self,
		course_id: int,
		query: str,
		seed_entity_ids: Iterable[str] = (),
		include_questions: bool = False,
	) -> RankedContext:
		"""实现 GraphRAG Local Search。"""
		payload = self._ensure_index(course_id)
		seed_ids = {entity_id for entity_id in seed_entity_ids if entity_id}
		hybrid_hits = []
		try:
			hybrid_hits = student_graphrag_runtime.search_documents(
				course_id=course_id,
				query=query,
				limit=6,
				seed_point_ids=sorted(self._extract_point_ids(seed_ids)),
			)
		except Exception as error:
			logger.warning("课程 GraphRAG 混合检索失败，回退本地图排序: course=%s error=%s", course_id, error)
		hybrid_entity_ids = {
			f"kp:{point_id}"
			for hit in hybrid_hits
			for point_id in hit.point_ids
		}
		ranked_entities = self._rank_entities(payload, query, seed_ids | hybrid_entity_ids, limit=5)
		ranked_entity_ids = [str(entity.get("id", "")).strip() for entity in ranked_entities]
		focus_ids = seed_ids | hybrid_entity_ids | set(ranked_entity_ids)
		focus_ids.update(self._collect_neighbor_ids(payload, focus_ids, limit=6))

		entity_map = self._entity_map(payload)
		focus_titles = [
			str(entity_map[entity_id].get("title", entity_id)).strip()
			for entity_id in focus_ids
			if entity_id in entity_map
		]
		relation_lines = self._relationship_lines(payload, focus_ids)
		documents = self._rank_documents(
			payload,
			query,
			focus_ids,
			limit=5,
			include_questions=include_questions,
		)
		reports = self._rank_community_reports(payload, query, focus_ids, limit=2)

		context_lines: list[str] = []
		if focus_titles:
			context_lines.append(f"命中实体：{'、'.join(_dedupe_strings(focus_titles)[:6])}")
		if relation_lines:
			context_lines.append("关键关系：\n- " + "\n- ".join(relation_lines[:6]))
		if reports:
			report_summaries = [
				_sanitize_answer_text(str(report.get("summary", "")))
				for report in reports
				if str(report.get("summary", "")).strip()
			]
			if report_summaries:
				context_lines.append("社区洞察：\n- " + "\n- ".join(report_summaries[:2]))
		if hybrid_hits:
			hybrid_lines = [
				f"{hit.title}：{hit.excerpt}"
				for hit in hybrid_hits
				if hit.excerpt
			]
			if hybrid_lines:
				context_lines.append("向量证据：\n- " + "\n- ".join(hybrid_lines[:5]))
		if documents:
			evidence_lines = [
				f"{_humanize_document_title(document)}：{self._document_excerpt(document, limit=120)}"
				for document in documents
				if self._document_excerpt(document, limit=120)
			]
			if evidence_lines:
				context_lines.append("局部证据：\n- " + "\n- ".join(evidence_lines[:5]))

		sources = self._merge_sources(
			[self._source_from_graphrag_hit(hit, "local") for hit in hybrid_hits],
			[self._source_from_document(document, "local") for document in documents],
			[self._source_from_report(report, "local") for report in reports],
		)
		return RankedContext(
			context="\n".join(context_lines),
			sources=sources,
			matched_entity_ids=[entity_id for entity_id in focus_ids if entity_id],
		)

	def _build_global_context(self, course_id: int, query: str) -> RankedContext:
		"""实现 GraphRAG Global Search。"""
		payload = self._ensure_index(course_id)
		reports = self._rank_community_reports(payload, query, (), limit=4)
		if not reports:
			return RankedContext(context="", sources=[], matched_entity_ids=[])

		context_lines: list[str] = ["高层主题概览："]
		community_ids: list[str] = []
		for report in reports:
			title = str(report.get("title", "")).strip() or "社区报告"
			summary = _sanitize_answer_text(str(report.get("summary", "")))
			context_lines.append(f"- {title}：{summary}")
			community_id = str(report.get("community_id", "")).strip()
			if community_id:
				community_ids.append(community_id)

		return RankedContext(
			context="\n".join(context_lines),
			sources=[self._source_from_report(report, "global") for report in reports],
			matched_entity_ids=community_ids,
		)

	def _build_drift_context(
		self,
		course_id: int,
		query: str,
		seed_entity_ids: Iterable[str] = (),
	) -> RankedContext:
		"""实现 GraphRAG DRIFT Search。"""
		payload = self._ensure_index(course_id)
		local_context = self._build_local_context(course_id, query, seed_entity_ids)
		if not local_context.matched_entity_ids:
			return RankedContext(context="", sources=[], matched_entity_ids=[])

		entity_to_communities = self._entity_to_communities(payload)
		community_lookup = self._community_lookup(payload)

		related_community_ids: set[str] = set()
		for entity_id in local_context.matched_entity_ids:
			related_community_ids.update(entity_to_communities.get(entity_id, []))

		expanded_entity_ids: set[str] = set(local_context.matched_entity_ids)
		expanded_reports: list[dict[str, object]] = []
		for community_id in related_community_ids:
			community = community_lookup.get(community_id, {})
			entity_ids = community.get("entity_ids")
			if isinstance(entity_ids, list):
				expanded_entity_ids.update(str(entity_id) for entity_id in entity_ids)
			for report in self._community_report_list(payload):
				if str(report.get("community_id", "")).strip() == community_id:
					expanded_reports.append(report)
					break

		entity_map = self._entity_map(payload)
		expanded_titles = [
			str(entity_map[entity_id].get("title", entity_id)).strip()
			for entity_id in expanded_entity_ids
			if entity_id in entity_map
		]
		documents = self._rank_documents(payload, query, expanded_entity_ids, limit=5)

		context_lines: list[str] = []
		if expanded_titles:
			context_lines.append(
				"扩展实体：" + "、".join(_dedupe_strings(expanded_titles)[:8])
			)
		if expanded_reports:
			report_summaries = [
				_sanitize_answer_text(str(report.get("summary", "")))
				for report in expanded_reports
				if str(report.get("summary", "")).strip()
			]
			if report_summaries:
				context_lines.append("社区延展：\n- " + "\n- ".join(report_summaries[:2]))
		if documents:
			drift_lines = [
				f"{_humanize_document_title(document)}：{self._document_excerpt(document, limit=110)}"
				for document in documents
				if self._document_excerpt(document, limit=110)
			]
			if drift_lines:
				context_lines.append("扩展事实：\n- " + "\n- ".join(drift_lines[:5]))

		sources = self._merge_sources(
			[self._source_from_document(document, "drift") for document in documents],
			[self._source_from_report(report, "drift") for report in expanded_reports],
		)
		return RankedContext(
			context="\n".join(context_lines),
			sources=sources,
			matched_entity_ids=sorted(expanded_entity_ids),
		)

	def _compose_query_context(
		self,
		course_id: int,
		query: str,
		seed_entity_ids: Iterable[str] = (),
		include_questions: bool = False,
	) -> dict[str, object]:
		"""组合 local / global / drift 三类上下文。"""
		local_context = self._build_local_context(
			course_id,
			query,
			seed_entity_ids,
			include_questions=include_questions,
		)
		global_context = self._build_global_context(course_id, query)
		drift_context = self._build_drift_context(course_id, query, seed_entity_ids)

		context_sections: list[str] = []
		if local_context.context:
			context_sections.append(f"[Local Search]\n{local_context.context}")
		if global_context.context:
			context_sections.append(f"[Global Search]\n{global_context.context}")
		if drift_context.context:
			context_sections.append(f"[DRIFT Search]\n{drift_context.context}")

		merged_sources = self._merge_sources(
			local_context.sources,
			global_context.sources,
			drift_context.sources,
		)
		matched_entity_ids = _dedupe_strings(
			list(local_context.matched_entity_ids)
			+ list(global_context.matched_entity_ids)
			+ list(drift_context.matched_entity_ids)
		)
		return {
			"context": "\n\n".join(section for section in context_sections if section),
			"sources": merged_sources,
			"matched_entity_ids": matched_entity_ids,
		}

	def _find_point(
		self,
		course_id: int,
		point_name: str = "",
		point_id: int | None = None,
	) -> KnowledgePoint | None:
		"""按 point_id 或名称定位课程知识点。"""
		queryset = KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
		if point_id is not None:
			return queryset.filter(id=point_id).first()
		normalized_name = point_name.strip()
		if not normalized_name:
			return None
		return queryset.filter(name__icontains=normalized_name).order_by("order", "id").first()

	def _estimate_point_difficulty(self, point: KnowledgePoint) -> str:
		"""根据知识点元数据估计学习难度。"""
		if point.level <= 2:
			return "基础"
		if point.level <= 4:
			return "中等"
		return "进阶"

	def build_path_context(
		self,
		*,
		course_id: int,
		target: str,
		pending_points: Sequence[KnowledgePoint],
	) -> dict[str, object]:
		"""为学习路径规划构建 GraphRAG 背景。"""
		pending_names = [point.name for point in pending_points if point is not None]
		seed_entity_ids = {
			f"kp:{_model_pk(point)}"
			for point in pending_points
			if point is not None and _model_pk(point) > 0
		}
		query = f"{target or '提升课程掌握度'}；待规划知识点：{'、'.join(pending_names[:8])}"
		context_bundle = self._compose_query_context(course_id, query, seed_entity_ids)

		retrieved_context = "\n".join(
			section
			for section in [
				f"学习目标：{target or '提升课程掌握度'}",
				f"优先关注知识点：{'、'.join(pending_names[:8])}" if pending_names else "",
				str(context_bundle.get("context", "")).strip(),
			]
			if section
		)
		return {
			"retrieved_context": retrieved_context,
			"retrieved_sources": _bundle_sources(context_bundle)[:10],
		}

	def build_point_support_payload(
		self,
		*,
		course_id: int,
		point: KnowledgePoint,
	) -> dict[str, object]:
		"""为知识图谱详情页生成可解释的 GraphRAG 证据摘要。"""
		point_pk = _model_pk(point)
		context_bundle = self._compose_query_context(
			course_id,
			f"解释知识点：{point.name}",
			{f"kp:{point_pk}"},
		)
		graph_query_bundle: dict[str, object] = {}
		try:
			graph_query_bundle = student_graphrag_runtime.query_graph(
				course_id=course_id,
				query=f"{point.name} 的前置知识、后续知识和课程证据是什么？",
				focus_point_id=point_pk,
				focus_point_name=point.name,
				limit=5,
			)
		except Exception as error:
			logger.warning(
				"知识点详情图查询失败，回退现有 GraphRAG 摘要: course=%s point=%s error=%s",
				course_id,
				point_pk,
				error,
			)
			graph_query_bundle = {}
		context_lines = [
			line.strip()
			for line in (
				str(graph_query_bundle.get("context", "")).splitlines()
				+ str(context_bundle.get("context", "")).splitlines()
			)
			if line.strip() and not line.startswith("[")
		]
		merged_sources = self._merge_sources(
			_bundle_sources(graph_query_bundle),
			_bundle_sources(context_bundle),
		)
		resolved_mode = _bundle_mode(graph_query_bundle, "graph_rag")
		return {
			"summary": " ".join(context_lines[:4])[:280],
			"sources": merged_sources[:6],
			"mode": resolved_mode or "graph_rag",
		}

	def explain_knowledge_point(
		self,
		*,
		course_id: int,
		point_name: str,
		point_id: int | None = None,
		question: str,
	) -> dict[str, object]:
		"""基于 GraphRAG 解释知识点。"""
		point = self._find_point(course_id, point_name=point_name, point_id=point_id)
		if point is None:
			return {
				"point_id": point_id,
				"point_name": point_name,
				"introduction": f"暂未在当前课程中定位到“{point_name}”的知识图谱实体。",
				"key_concepts": [],
				"learning_tips": ["请确认知识点名称后重试。"],
				"difficulty": "未知",
				"sources": [],
			}

		query = question or f"解释知识点：{point.name}"
		point_pk = _model_pk(point)
		context_bundle = self._compose_query_context(course_id, query, {f"kp:{point_pk}"})

		prerequisite_names = [item.name for item in point.get_prerequisites()[:3]]
		postrequisite_names = [item.name for item in point.get_dependents()[:3]]
		visible_resources = list(
			Resource.objects.filter(knowledge_points=point, is_visible=True).order_by("sort_order", "id")[:3]
		)
		resource_titles = [resource.title for resource in visible_resources]
		key_concepts = _dedupe_strings(
			point.get_tags_list() + prerequisite_names + postrequisite_names + resource_titles
		)[:6]
		learning_tips = _dedupe_strings(
			[
				f"先回顾前置知识：{'、'.join(prerequisite_names)}。" if prerequisite_names else "",
				f"优先学习课程资源：{'、'.join(resource_titles)}。" if resource_titles else "",
				f"掌握后可继续衔接：{'、'.join(postrequisite_names)}。" if postrequisite_names else "",
				"建议先理解定义与例子，再通过练习题检验掌握情况。",
			]
		)[:4]
		fallback = {
			"point_id": point_pk,
			"point_name": point.name,
			"introduction": point.introduction or point.description or point.name,
			"key_concepts": key_concepts,
			"learning_tips": learning_tips,
			"difficulty": self._estimate_point_difficulty(point),
			"sources": _bundle_sources(context_bundle)[:6],
		}

		if not llm_facade.is_available:
			return fallback

		prompt = f"""# 任务
请基于提供的 GraphRAG 证据，用中文解释课程知识点并给出学习建议。

# 学生问题
{query}

# 知识点实体
- 名称：{point.name}
- 章节：{point.chapter or '未分章'}
- 描述：{point.description or ''}
- 简介：{point.introduction or ''}
- 前置知识：{'、'.join(prerequisite_names) if prerequisite_names else '暂无'}
- 后续知识：{'、'.join(postrequisite_names) if postrequisite_names else '暂无'}

# GraphRAG 上下文
{context_bundle.get('context', '')}

# JSON输出格式
{{
	"point_id": {point_pk},
  "point_name": "{point.name}",
  "introduction": "80-160字的知识点介绍",
  "key_concepts": ["关键概念1", "关键概念2"],
  "learning_tips": ["学习建议1", "学习建议2"],
  "difficulty": "基础/中等/进阶"
}}

# 约束
1. 仅使用给定证据，不要臆造未出现的课程事实。
2. 若证据不足，可以用“建议结合课程资源继续确认”表达不确定性。
3. 输出必须是合法 JSON。
"""
		result = llm_facade.call_with_fallback(
			prompt=prompt,
			call_type="graph_rag_point_explain",
			fallback_response=fallback,
		)
		result["sources"] = fallback["sources"]
		return result

	def plan_learning_path(
		self,
		*,
		course: Course,
		mastery_data: list[dict[str, object]],
		target: str,
		constraints: dict[str, object] | None,
		max_nodes: int = 6,
	) -> dict[str, object]:
		"""将 GraphRAG 上下文注入 LLM 路径规划。"""
		ranked_mastery = sorted(
			mastery_data,
			key=lambda item: _to_float(item.get("mastery_rate", 0.0), default=0.0),
		)
		weak_names = [str(item.get("point_name", "")).strip() for item in ranked_mastery[:max_nodes]]
		course_pk = _model_pk(course)
		point_queryset = KnowledgePoint.objects.filter(course_id=course_pk, is_published=True)
		point_map = {point.name: point for point in point_queryset}
		pending_points = [point_map[name] for name in weak_names if name in point_map]

		rag_context = self.build_path_context(
			course_id=course_pk,
			target=target,
			pending_points=pending_points,
		)
		merged_constraints = dict(constraints or {})
		if not merged_constraints.get("retrieved_context"):
			merged_constraints["retrieved_context"] = rag_context["retrieved_context"]
		if not merged_constraints.get("retrieved_sources"):
			merged_constraints["retrieved_sources"] = rag_context["retrieved_sources"]

		result = llm_facade.plan_learning_path(
			mastery_data=mastery_data,
			target=target,
			constraints=merged_constraints,
			course_name=course.name,
			max_nodes=max_nodes,
		)
		result["sources"] = rag_context["retrieved_sources"]
		return result

	def answer_graph_question(
		self,
		*,
		course_id: int,
		point: KnowledgePoint,
		question: str,
	) -> dict[str, object]:
		"""使用三种 GraphRAG 查询模式回答学生问题。"""
		context_bundle = self._compose_query_context(
			course_id,
			question,
			{f"kp:{_model_pk(point)}"},
		)
		graph_query_bundle: dict[str, object] = {}
		try:
			graph_query_bundle = student_graphrag_runtime.query_graph(
				course_id=course_id,
				query=question,
				focus_point_id=_model_pk(point),
				focus_point_name=point.name,
				limit=6,
			)
		except Exception as error:
			logger.warning(
				"Graph query 增强失败，回退原三段式 GraphRAG: course=%s point=%s error=%s",
				course_id,
				_model_pk(point),
				error,
			)
			graph_query_bundle = {}
		combined_context = "\n\n".join(
			section
			for section in [
				str(graph_query_bundle.get("context", "")).strip(),
				str(context_bundle.get("context", "")).strip(),
			]
			if section
		)
		sources = self._merge_sources(
			_bundle_sources(graph_query_bundle),
			_bundle_sources(context_bundle),
		)[:8]
		source_titles = _dedupe_strings(
			str(source.get("title", "")).strip() for source in sources
		)[:4]
		fallback_answer = _sanitize_answer_text(
			"\n".join(
				section
				for section in [
					f"围绕“{point.name}”，当前课程图谱显示：{point.introduction or point.description or point.name}",
					f"建议优先结合这些证据继续学习：{'、'.join(source_titles)}。" if source_titles else "建议优先查看课程内与该知识点直接关联的资源。",
					"如果你想追问先修关系、典型题型或资源推荐，也可以继续细化问题。",
				]
				if section
			)
		)

		fallback = {
			"answer": fallback_answer,
			"key_points": _dedupe_strings(source_titles),
		}
		query_modes = _bundle_query_modes(graph_query_bundle)
		resolved_mode = _bundle_mode(graph_query_bundle, "graph_rag")
		if not llm_facade.is_available:
			return {
				"answer": fallback_answer,
				"sources": sources,
				"mode": resolved_mode or "graph_rag",
				"query_modes": query_modes,
			}

		prompt = f"""# 任务
请基于给定 GraphRAG 证据，用中文回答学生问题。

# 学生问题
{question}

# 当前知识点
- 名称：{point.name}
- 章节：{point.chapter or '未分章'}
- 描述：{point.description or ''}

# GraphRAG 上下文
{combined_context}

# JSON输出格式
{{
  "answer": "80-200字回答",
  "key_points": ["要点1", "要点2"]
}}

# 回答约束
1. 只能基于证据回答，不要编造课程外事实。
2. 回答需先直接答题，再补充学习建议。
3. 若证据不足，要明确说“当前证据不足”。
4. 输出必须是合法 JSON。
"""
		result = llm_facade.call_with_fallback(
			prompt=prompt,
			call_type="graph_rag_answer",
			fallback_response=fallback,
		)
		return {
			"answer": _sanitize_answer_text(str(result.get("answer", fallback_answer))),
			"sources": sources,
			"mode": resolved_mode or "graph_rag",
			"query_modes": query_modes,
			"key_points": result.get("key_points", fallback.get("key_points", [])),
		}

	def answer_course_question(
		self,
		*,
		course_id: int,
		question: str,
		seed_point_ids: Sequence[int] = (),
	) -> dict[str, object]:
		"""在未指定知识点时，使用课程级 GraphRAG 证据回答学生问题。"""
		payload = self._ensure_index(course_id)
		point_name_map: dict[int, str] = {}
		for entity in self._entity_list(payload):
			if str(entity.get("entity_type", "")).strip() != "knowledge_point":
				continue
			metadata = entity.get("metadata")
			point_id = 0
			if isinstance(metadata, dict):
				point_id = _to_int(metadata.get("knowledge_point_id"), default=0)
			if point_id <= 0:
				entity_id = str(entity.get("id", "")).strip()
				if entity_id.startswith("kp:"):
					point_id = _to_int(entity_id.partition(":")[2], default=0)
			point_name = str(entity.get("title", "")).strip()
			if point_id > 0 and point_name:
				point_name_map[point_id] = point_name

		resolved_seed_ids = [point_id for point_id in seed_point_ids if point_id > 0]
		seed_entity_ids = {f"kp:{point_id}" for point_id in resolved_seed_ids}
		focus_point_id = resolved_seed_ids[0] if resolved_seed_ids else None
		focus_point_name = point_name_map.get(focus_point_id or 0, "")

		context_bundle = self._compose_query_context(
			course_id,
			question,
			seed_entity_ids,
		)
		graph_query_bundle: dict[str, object] = {}
		try:
			graph_query_bundle = student_graphrag_runtime.query_graph(
				course_id=course_id,
				query=question,
				focus_point_id=focus_point_id,
				focus_point_name=focus_point_name,
				limit=6,
			)
		except Exception as error:
			logger.warning(
				"课程级 Graph query 失败，回退课程证据上下文: course=%s error=%s",
				course_id,
				error,
			)
			graph_query_bundle = {}

		combined_context = "\n\n".join(
			section
			for section in [
				str(graph_query_bundle.get("context", "")).strip(),
				str(context_bundle.get("context", "")).strip(),
			]
			if section
		)
		sources = self._merge_sources(
			_bundle_sources(graph_query_bundle),
			_bundle_sources(context_bundle),
		)[:8]
		matched_point_ids = _dedupe_ints(
			list(resolved_seed_ids) + _bundle_positive_ints(graph_query_bundle, "matched_point_ids")
		)
		candidate_names = _dedupe_strings(
			point_name_map.get(point_id, "")
			for point_id in matched_point_ids
		)
		missing_point_ids = [
			point_id for point_id in matched_point_ids if point_id not in point_name_map
		]
		if missing_point_ids:
			candidate_names = _dedupe_strings(
				candidate_names
				+ list(
					KnowledgePoint.objects.filter(
						course_id=course_id,
						is_published=True,
						id__in=missing_point_ids,
					)
					.order_by("order", "id")
					.values_list("name", flat=True)
				)
			)
		source_titles = _dedupe_strings(
			str(source.get("title", "")).strip()
			for source in sources
		)[:5]
		fallback_answer = _sanitize_answer_text(
			"\n".join(
				section
				for section in [
					(
						f"围绕当前课程问题，系统命中了这些候选知识点：{'、'.join(candidate_names[:4])}。"
						if candidate_names
						else "系统已结合当前课程知识图谱与课程证据进行回答。"
					),
					(
						f"可优先查看这些证据：{'、'.join(source_titles[:4])}。"
						if source_titles
						else "如果你希望继续深挖，可追问更具体的知识点、先修关系或资源名称。"
					),
				]
				if section
			)
		)

		fallback = {
			"answer": fallback_answer,
			"key_points": _dedupe_strings(candidate_names + source_titles)[:5],
		}
		query_modes = _bundle_query_modes(graph_query_bundle)
		resolved_mode = _bundle_mode(graph_query_bundle, "graph_rag_course")
		if not llm_facade.is_available:
			return {
				"answer": fallback_answer,
				"sources": sources,
				"mode": resolved_mode,
				"query_modes": query_modes,
				"key_points": fallback["key_points"],
				"matched_point_ids": matched_point_ids,
			}

		prompt = f"""# 任务
请基于给定课程的 GraphRAG 证据，用中文直接回答学生问题。

# 学生问题
{question}

# 候选知识点
{'、'.join(candidate_names[:6]) if candidate_names else '当前问题未命中唯一知识点，请以课程级证据回答。'}

# GraphRAG 上下文
{combined_context}

# JSON输出格式
{{
  "answer": "80-220字回答",
  "key_points": ["要点1", "要点2"]
}}

# 回答约束
1. 只能基于证据回答，不要编造课程外事实。
2. 先直接回答学生问题，再补充下一步学习建议。
3. 如果证据不足，要明确提示“当前证据不足”。
4. 输出必须是合法 JSON。
"""
		result = llm_facade.call_with_fallback(
			prompt=prompt,
			call_type="graph_rag_course_answer",
			fallback_response=fallback,
		)
		return {
			"answer": _sanitize_answer_text(str(result.get("answer", fallback_answer))),
			"sources": sources,
			"mode": resolved_mode,
			"query_modes": query_modes,
			"key_points": result.get("key_points", fallback["key_points"]),
			"matched_point_ids": matched_point_ids,
		}

	def recommend_node_resources(
		self,
		*,
		node: PathNode,
		user,
		mastery_value: float | None,
		completed_resource_ids: set[str],
		internal_count: int = 3,
		external_count: int = 2,
	) -> dict[str, object]:
		"""为学习节点推荐图谱支撑的内部/外部资源。"""
		point = node.knowledge_point
		student_id = _model_pk(user)
		if point is None:
			logger.info("学习节点缺少知识点，跳过资源推荐: node=%s user=%s", _model_pk(node), student_id)
			return {"internal_resources": [], "external_resources": []}

		# 先合并节点绑定资源与知识点绑定资源，避免重复曝光。
		candidate_resources: dict[int, Resource] = {}
		for bound_resource in node.resources.filter(is_visible=True).order_by("sort_order", "id"):
			candidate_resources[_model_pk(bound_resource)] = bound_resource
		for linked_resource in Resource.objects.filter(knowledge_points=point, is_visible=True).order_by("sort_order", "id"):
			candidate_resources.setdefault(_model_pk(linked_resource), linked_resource)

		ordered_resources = sorted(
			candidate_resources.values(),
			key=lambda candidate_resource: _resource_rank_key(candidate_resource, mastery_value),
		)
		available_resources = [
			{
				"id": _model_pk(candidate_resource),
				"title": candidate_resource.title,
				"type": candidate_resource.resource_type,
				"description": candidate_resource.description or "",
				"chapter": candidate_resource.chapter_number or point.chapter or "",
			}
			for candidate_resource in ordered_resources
		]

		selected_internal_ids: list[int] = []
		selected_reason_map: dict[int, tuple[str, str]] = {}
		if llm_facade.is_available and available_resources:
			internal_result = llm_facade.recommend_internal_resources(
				point_name=point.name,
				student_mastery=mastery_value,
				available_resources=available_resources,
				course_name=node.path.course.name,
				count=internal_count,
			)
			raw_resources = internal_result.get("resources")
			if isinstance(raw_resources, list):
				for item in raw_resources:
					if not isinstance(item, dict):
						continue
					resource_id = item.get("id")
					normalized_id = _to_int(resource_id, default=0)
					if normalized_id <= 0:
						continue
					if normalized_id not in candidate_resources:
						continue
					selected_internal_ids.append(normalized_id)
					selected_reason_map[normalized_id] = (
						str(item.get("reason", "")).strip()
						or f"该资源与“{point.name}”直接关联。",
						str(item.get("learning_tips", "")).strip()
						or "建议结合笔记梳理关键知识点。",
					)

		if not selected_internal_ids:
			selected_internal_ids = [_model_pk(candidate_resource) for candidate_resource in ordered_resources[:internal_count]]
			for candidate_resource in ordered_resources[:internal_count]:
				selected_reason_map[_model_pk(candidate_resource)] = (
					f"该课程资源直接关联“{point.name}”，适合当前阶段优先学习。",
					"建议先看定义与示例，再完成对应练习巩固。",
				)

		internal_resources: list[dict[str, object]] = []
		for resource_id in _dedupe_strings(str(item) for item in selected_internal_ids):
			normalized_id = int(resource_id)
			resource = candidate_resources.get(normalized_id)
			if resource is None:
				continue
			reason, learning_tips = selected_reason_map.get(
				normalized_id,
				(
					f"该资源与“{point.name}”紧密相关。",
					"建议完成学习后立即自测。",
				),
			)
			append_internal_resource(
				internal_resources,
				resource,
				reason,
				completed_resource_ids,
				learning_tips,
			)

		external_resources: list[dict[str, object]] = []
		if external_count > 0:
			existing_titles = [candidate_resource.title for candidate_resource in ordered_resources]
			external_result = llm_facade.recommend_external_resources(
				point_name=point.name,
				student_mastery=mastery_value,
				existing_titles=existing_titles,
				course_name=node.path.course.name,
				count=external_count,
			)
			external_payload = external_result.get("resources")
			if isinstance(external_payload, list):
				for item in external_payload[:external_count]:
					if not isinstance(item, dict):
						continue
					external_resources.append(
						{
							"title": str(item.get("title", "")).strip() or f"{point.name} 外部资源",
							"url": str(item.get("url", "")).strip(),
							"type": str(item.get("type", "link")).strip() or "link",
							"recommended_reason": str(item.get("reason", "")).strip()
							or f"该外部资源与“{point.name}”相关，可作为补充学习材料。",
							"learning_tips": "建议先完成课程内资源，再使用外部资源扩展理解。",
							"is_internal": False,
							"completed": False,
						}
					)

		return {
			"internal_resources": internal_resources,
			"external_resources": external_resources,
		}

	def recommend_resources_for_node(
		self,
		*,
		node: PathNode,
		user,
		mastery_value: float | None,
		completed_resource_ids: set[str],
		external_count: int = 2,
	) -> dict[str, object]:
		"""对外暴露稳定的节点资源推荐入口。"""
		return self.recommend_node_resources(
			node=node,
			user=user,
			mastery_value=mastery_value,
			completed_resource_ids=completed_resource_ids,
			external_count=external_count,
		)


student_learning_rag = StudentLearningRAG()
