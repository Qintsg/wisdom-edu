import { toBackendAbsoluteUrl } from '@/api/backend'

export function normalizeText(value, fallback = '') {
  if (Array.isArray(value)) return normalizeText(value[0], fallback)
  if (typeof value === 'string') {
    const trimmedValue = value.trim()
    return trimmedValue || fallback
  }
  if (typeof value === 'number') return String(value)
  return fallback
}

export function normalizeIdentifier(value, fallback = '') {
  if (Array.isArray(value)) return normalizeIdentifier(value[0], fallback)
  if (value === null || value === undefined) return fallback
  const normalizedValue = String(value).trim()
  return normalizedValue || fallback
}

export function normalizeListFromPayload(value) {
  return Array.isArray(value) ? value : []
}

function normalizeOptionalNumber(value) {
  if (value === null || value === undefined || value === '') return null
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : null
}

export function normalizeGraphNode(node, index) {
  return {
    nodeId: normalizeIdentifier(node?.['id'] ?? node?.['point_id'], `node-${index}`),
    pointId: normalizeIdentifier(node?.['point_id'] ?? node?.['id']),
    nodeName: normalizeText(node?.['name'] ?? node?.['point_name'], '未命名知识点'),
    chapterText: normalizeText(node?.['chapter']),
    nodeDescription: normalizeText(node?.['description']),
    masteryRate: normalizeOptionalNumber(node?.['mastery'] ?? node?.['mastery_rate'])
  }
}

export function normalizeGraphEdge(edge, index) {
  return {
    edgeId: normalizeIdentifier(edge?.['id'], `edge-${index}`),
    sourceNodeId: normalizeIdentifier(edge?.['source'] ?? edge?.['source_id']),
    targetNodeId: normalizeIdentifier(edge?.['target'] ?? edge?.['target_id']),
    relationType: normalizeText(edge?.['relation_type'] ?? edge?.['label'], 'related')
  }
}

function normalizeResourceItem(resource, index) {
  return {
    resourceId: normalizeIdentifier(resource?.['resource_id'] ?? resource?.['id'], `resource-${index}`),
    resourceTitle: normalizeText(resource?.['title'], '未命名资源'),
    resourceUrl: toBackendAbsoluteUrl(normalizeText(resource?.['url']))
  }
}

export function normalizeNodeDetail(node, detail = {}) {
  return {
    ...node,
    nodeName: normalizeText(detail?.['point_name'] ?? detail?.['name'], node.nodeName),
    chapterText: normalizeText(detail?.['chapter'], node.chapterText),
    nodeDescription: normalizeText(detail?.['description'], node.nodeDescription),
    masteryRate: normalizeOptionalNumber(detail?.['mastery_rate'] ?? detail?.['mastery']) ?? node.masteryRate
  }
}

export function normalizeNodeResources(detail) {
  return normalizeListFromPayload(detail?.['resources'])
    .map((resource, index) => normalizeResourceItem(resource, index))
}

export function getLinkCoordinate(linkDatum, endpointKey, coordinateKey) {
  const endpoint = linkDatum?.[endpointKey]
  if (endpoint && typeof endpoint === 'object') {
    const coordinate = Number(endpoint[coordinateKey])
    return Number.isFinite(coordinate) ? coordinate : 0
  }
  return 0
}

export function getRelationStroke(relationType) {
  if (relationType === 'prerequisite') return { color: '#475569', dash: null, width: 1.8 }
  if (relationType === 'related') return { color: '#94a3b8', dash: '2 8', width: 1.4 }
  return { color: '#64748b', dash: '10 6', width: 1.3 }
}
