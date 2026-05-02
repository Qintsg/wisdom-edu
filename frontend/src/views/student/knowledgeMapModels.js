import { toBackendAbsoluteUrl } from '@/api/backend'

export const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') return rawValue
  if (typeof rawValue === 'number') return String(rawValue)
  return ''
}

export const normalizeIdentifier = (rawValue) => {
  const normalizedText = normalizeText(rawValue)
  return normalizedText ? normalizedText : ''
}

const normalizeListFromPayload = (rawValue) => Array.isArray(rawValue) ? rawValue : []

const normalizeRate = (rawValue) => {
  const parsedValue = Number(rawValue)

  if (!Number.isFinite(parsedValue)) return 0
  if (parsedValue > 1) return Math.min(parsedValue / 100, 1)
  return Math.max(parsedValue, 0)
}

const normalizeTagList = (rawValue) => {
  return normalizeText(rawValue)
    .split(',')
    .map((tagText) => normalizeText(tagText).replace(/^\s+|\s+$/g, ''))
    .filter(Boolean)
}

const buildDefaultKnowledgeNode = () => ({
  nodeId: '',
  pointId: '',
  pointName: '',
  masteryRate: 0,
  chapterText: '',
  nodeDescription: '',
  tagsText: '',
  cognitiveDimensionText: '',
  categoryText: '',
  teachingGoalText: ''
})

const normalizeKnowledgeNode = (rawNode) => ({
  ...buildDefaultKnowledgeNode(),
  nodeId: normalizeIdentifier(rawNode?.id ?? rawNode?.point_id),
  pointId: normalizeIdentifier(rawNode?.point_id ?? rawNode?.id),
  pointName: normalizeText(rawNode?.point_name ?? rawNode?.name) || '未命名知识点',
  masteryRate: normalizeRate(rawNode?.mastery_rate ?? rawNode?.mastery),
  chapterText: normalizeText(rawNode?.chapter),
  nodeDescription: normalizeText(rawNode?.description),
  tagsText: normalizeText(rawNode?.tags),
  cognitiveDimensionText: normalizeText(rawNode?.cognitive_dimension),
  categoryText: normalizeText(rawNode?.category),
  teachingGoalText: normalizeText(rawNode?.teaching_goal)
})

const buildDefaultKnowledgeEdge = () => ({
  edgeId: '',
  sourceNodeId: '',
  targetNodeId: '',
  relationTypeText: 'prerequisite'
})

const normalizeKnowledgeEdge = (rawEdge) => {
  const sourceNodeId = normalizeIdentifier(rawEdge?.source ?? rawEdge?.source_id ?? rawEdge?.from_point_id)
  const targetNodeId = normalizeIdentifier(rawEdge?.target ?? rawEdge?.target_id ?? rawEdge?.to_point_id)

  return {
    ...buildDefaultKnowledgeEdge(),
    edgeId: normalizeIdentifier(rawEdge?.id ?? rawEdge?.edge_id) || `${sourceNodeId}-${targetNodeId}`,
    sourceNodeId,
    targetNodeId,
    relationTypeText: normalizeText(rawEdge?.relation_type) || 'prerequisite'
  }
}

const normalizeRelatedKnowledgePoint = (rawPoint) => ({
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点'
})

const normalizeKnowledgeResource = (rawResource) => ({
  resourceId: normalizeIdentifier(rawResource?.resource_id ?? rawResource?.id),
  resourceTitle: normalizeText(rawResource?.title ?? rawResource?.resource_name) || '未命名资源',
  resourceType: normalizeText(rawResource?.type ?? rawResource?.resource_type) || 'link',
  resourceUrl: toBackendAbsoluteUrl(normalizeText(rawResource?.url ?? rawResource?.resource_url)),
  durationText: normalizeText(rawResource?.duration_display)
})

const normalizeGraphRagSource = (rawSource) => {
  if (!rawSource || typeof rawSource === 'string') {
    const sourceTitle = normalizeText(rawSource) || '课程证据'
    return { sourceKey: sourceTitle, sourceTitle, sourceKind: 'document' }
  }

  const sourceKind = normalizeText(rawSource.kind) || 'document'
  const sourceTitle = normalizeText(rawSource.title ?? rawSource.label) || sourceKind || '课程证据'
  return {
    sourceKey: `${normalizeIdentifier(rawSource.id) || sourceTitle}-${sourceKind}`,
    sourceTitle,
    sourceKind
  }
}

const buildDefaultPointDetail = () => ({
  pointId: '',
  pointName: '',
  descriptionText: '',
  masteryRate: 0,
  tagsText: '',
  tagList: [],
  cognitiveDimensionText: '',
  categoryText: '',
  teachingGoalText: '',
  graphRagSummary: '',
  graphRagSourceList: [],
  prerequisiteList: [],
  postrequisiteList: [],
  resourceList: []
})

export const normalizePointDetail = (rawDetail) => {
  const tagsText = normalizeText(rawDetail?.tags)

  return {
    ...buildDefaultPointDetail(),
    pointId: normalizeIdentifier(rawDetail?.point_id ?? rawDetail?.id),
    pointName: normalizeText(rawDetail?.point_name ?? rawDetail?.name) || '未命名知识点',
    descriptionText: normalizeText(rawDetail?.description),
    masteryRate: normalizeRate(rawDetail?.mastery_rate),
    tagsText,
    tagList: normalizeTagList(tagsText),
    cognitiveDimensionText: normalizeText(rawDetail?.cognitive_dimension),
    categoryText: normalizeText(rawDetail?.category),
    teachingGoalText: normalizeText(rawDetail?.teaching_goal),
    graphRagSummary: normalizeText(rawDetail?.graph_rag_summary),
    graphRagSourceList: normalizeListFromPayload(rawDetail?.graph_rag_sources)
      .map((sourceItem) => normalizeGraphRagSource(sourceItem)),
    prerequisiteList: normalizeListFromPayload(rawDetail?.prerequisites)
      .map((relatedPoint) => normalizeRelatedKnowledgePoint(relatedPoint)),
    postrequisiteList: normalizeListFromPayload(rawDetail?.postrequisites)
      .map((relatedPoint) => normalizeRelatedKnowledgePoint(relatedPoint)),
    resourceList: normalizeListFromPayload(rawDetail?.resources)
      .map((resourceItem) => normalizeKnowledgeResource(resourceItem))
  }
}

export const buildKnowledgeTree = (allKnowledgeNodes) => {
  const chapterMap = new Map()

  allKnowledgeNodes.forEach((knowledgeNode) => {
    const chapterText = knowledgeNode.chapterText || '其他'

    if (!chapterMap.has(chapterText)) {
      chapterMap.set(chapterText, {
        treeId: `chapter-${chapterText}`,
        labelText: chapterText,
        pointId: '',
        masteryPercent: 0,
        children: []
      })
    }

    chapterMap.get(chapterText).children.push({
      treeId: `point-${knowledgeNode.pointId}`,
      labelText: knowledgeNode.pointName,
      pointId: knowledgeNode.pointId,
      masteryPercent: Math.round(knowledgeNode.masteryRate * 100),
      children: []
    })
  })

  return [...chapterMap.values()].map((chapterNode) => {
    const childCount = chapterNode.children.length
    const chapterMasteryTotal = chapterNode.children.reduce((masterySum, childNode) => {
      return masterySum + childNode.masteryPercent
    }, 0)

    return {
      ...chapterNode,
      masteryPercent: childCount ? Math.round(chapterMasteryTotal / childCount) : 0
    }
  })
}

export const normalizeKnowledgeMapPayload = (rawKnowledgeMapPayload) => {
  const knowledgeMapPayload = rawKnowledgeMapPayload?.data || rawKnowledgeMapPayload
  return {
    nodes: normalizeListFromPayload(knowledgeMapPayload?.nodes)
      .map((rawNode) => normalizeKnowledgeNode(rawNode)),
    edges: normalizeListFromPayload(knowledgeMapPayload?.edges)
      .map((rawEdge) => normalizeKnowledgeEdge(rawEdge))
  }
}

export const getMasteryColor = (rate) => {
  if (!rate || rate === 0) return '#7a8d87'
  if (rate >= 0.8) return '#22a06b'
  if (rate >= 0.6) return '#dd8f1d'
  return '#d45050'
}
