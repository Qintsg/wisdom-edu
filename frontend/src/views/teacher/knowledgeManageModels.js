export const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') return rawValue
  if (typeof rawValue === 'number') return String(rawValue)
  return ''
}

const normalizeIdentifier = (rawValue) => {
  const normalizedText = normalizeText(rawValue)
  return normalizedText ? normalizedText : ''
}

const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

const normalizeListFromPayload = (rawValue) => Array.isArray(rawValue) ? rawValue : []

export const normalizeSearchKeyword = (rawValue) => {
  return normalizeText(rawValue).toLowerCase().replace(/^\s+|\s+$/g, '')
}

const buildDefaultKnowledgePoint = () => ({
  pointId: '',
  pointName: '',
  chapterText: '',
  descriptionText: '',
  orderIndex: 0,
  isPublished: true
})

const normalizeKnowledgePoint = (rawPoint) => ({
  ...buildDefaultKnowledgePoint(),
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点',
  chapterText: normalizeText(rawPoint?.chapter),
  descriptionText: normalizeText(rawPoint?.description),
  orderIndex: normalizeNumber(rawPoint?.order),
  isPublished: rawPoint?.is_published !== false
})

const buildDefaultKnowledgeRelation = () => ({
  relationId: '',
  fromPointId: '',
  fromPointName: '',
  toPointId: '',
  toPointName: '',
  relationTypeText: 'prerequisite'
})

const normalizeKnowledgeRelation = (rawRelation) => ({
  ...buildDefaultKnowledgeRelation(),
  relationId: normalizeIdentifier(rawRelation?.relation_id ?? rawRelation?.id),
  fromPointId: normalizeIdentifier(rawRelation?.from_point_id ?? rawRelation?.source_id ?? rawRelation?.source),
  fromPointName: normalizeText(rawRelation?.from_point_name ?? rawRelation?.pre_point_name),
  toPointId: normalizeIdentifier(rawRelation?.to_point_id ?? rawRelation?.target_id ?? rawRelation?.target),
  toPointName: normalizeText(rawRelation?.to_point_name ?? rawRelation?.post_point_name),
  relationTypeText: normalizeText(rawRelation?.relation_type ?? rawRelation?.label) || 'prerequisite'
})

export const normalizeKnowledgePointListPayload = (rawPayload) => {
  return normalizeListFromPayload(rawPayload?.points)
    .map((rawPoint) => normalizeKnowledgePoint(rawPoint))
}

export const normalizeKnowledgeRelationListPayload = (rawPayload) => {
  return normalizeListFromPayload(rawPayload?.relations)
    .map((rawRelation) => normalizeKnowledgeRelation(rawRelation))
}

export const normalizeRagIndexBuildResult = (rawResult) => ({
  courseId: normalizeIdentifier(rawResult?.course_id),
  indexPaths: normalizeListFromPayload(rawResult?.index_paths)
    .map((rawPath) => normalizeText(rawPath))
    .filter(Boolean)
})

export const buildKnowledgeTree = (allKnowledgePoints) => {
  const chapterMap = new Map()

  allKnowledgePoints.forEach((knowledgePoint) => {
    const chapterText = knowledgePoint.chapterText || '未分类'

    if (!chapterMap.has(chapterText)) {
      chapterMap.set(chapterText, {
        treeId: `chapter-${chapterText}`,
        labelText: chapterText,
        treeNodeType: 'chapter',
        pointId: '',
        pointName: '',
        chapterText,
        descriptionText: '',
        children: []
      })
    }

    chapterMap.get(chapterText).children.push({
      treeId: `point-${knowledgePoint.pointId}`,
      labelText: knowledgePoint.pointName,
      treeNodeType: 'point',
      pointId: knowledgePoint.pointId,
      pointName: knowledgePoint.pointName,
      chapterText: knowledgePoint.chapterText,
      descriptionText: knowledgePoint.descriptionText,
      children: []
    })
  })

  return [...chapterMap.values()]
    .sort((leftChapter, rightChapter) => leftChapter.labelText.localeCompare(rightChapter.labelText, 'zh-Hans-CN'))
    .map((chapterNode) => ({
      ...chapterNode,
      children: chapterNode.children.sort((leftPoint, rightPoint) => {
        return leftPoint.labelText.localeCompare(rightPoint.labelText, 'zh-Hans-CN')
      })
    }))
}
