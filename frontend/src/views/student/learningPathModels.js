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

const normalizeLearningStatus = (rawStatus) => {
  const statusText = normalizeText(rawStatus)
  if (statusText === 'completed') return 'completed'
  if (statusText === 'active' || statusText === 'in_progress' || statusText === 'failed') return 'current'
  if (statusText === 'skipped') return 'skipped'
  return 'pending'
}

const normalizeDurationMinutes = (rawValue) => {
  const durationMinutes = normalizeNumber(rawValue, 30)
  return durationMinutes > 0 ? durationMinutes : 30
}

const buildDefaultLearningPathNode = () => ({
  nodeId: '',
  titleText: '',
  descriptionText: '',
  suggestionText: '',
  learningStatus: 'pending',
  durationMinutes: 30,
  resourceCount: 0,
  pointId: '',
  nodeTypeText: 'study',
  isInserted: false
})

const normalizeLearningPathNode = (rawNode) => ({
  ...buildDefaultLearningPathNode(),
  nodeId: normalizeIdentifier(rawNode?.node_id ?? rawNode?.id),
  titleText: normalizeText(rawNode?.title) || '未命名节点',
  descriptionText: normalizeText(rawNode?.goal ?? rawNode?.description) || '暂无描述',
  suggestionText: normalizeText(rawNode?.suggestion),
  learningStatus: normalizeLearningStatus(rawNode?.status),
  durationMinutes: normalizeDurationMinutes(rawNode?.estimated_minutes ?? rawNode?.estimated_time),
  resourceCount: normalizeNumber(rawNode?.tasks_count ?? rawNode?.resource_count),
  pointId: normalizeIdentifier(rawNode?.knowledge_point_id ?? rawNode?.pointId),
  nodeTypeText: normalizeText(rawNode?.node_type ?? rawNode?.nodeType) || 'study',
  isInserted: Boolean(rawNode?.is_inserted)
})

export const normalizeLearningPathPayload = (rawPayload) => ({
  needAssessment: Boolean(rawPayload?.need_assessment),
  assessmentHint: normalizeText(rawPayload?.next_step_msg) || '请先完成初始评测后再进入学习路径',
  generating: Boolean(rawPayload?.generating),
  nodes: normalizeListFromPayload(rawPayload?.nodes)
    .map((pathNode) => normalizeLearningPathNode(pathNode))
})

export const normalizeLearningPathRefreshSummary = (rawPayload) => ({
  preservedCount: normalizeNumber(rawPayload?.preserved_count),
  newCount: normalizeNumber(rawPayload?.new_count),
  changeSummary: {
    preservedContext: normalizeNumber(rawPayload?.change_summary?.preserved_context),
    removedCount: normalizeNumber(rawPayload?.change_summary?.removed_count)
  },
  ktInfo: {
    answerCount: normalizeNumber(rawPayload?.kt_info?.answer_count)
  },
  profile: {
    summaryText: normalizeText(rawPayload?.profile?.summary)
  }
})

export const getNodeTagType = (status) => {
  const types = {
    completed: 'success',
    current: 'primary',
    skipped: 'warning',
    pending: 'info'
  }
  return types[status] || 'info'
}

export const getNodeStatusText = (status) => {
  const texts = {
    completed: '已完成',
    current: '学习中',
    skipped: '已跳过',
    pending: '待解锁'
  }
  return texts[status] || '待解锁'
}
