export const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') return rawValue
  if (typeof rawValue === 'number') return String(rawValue)
  return ''
}

export const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

const normalizeBoolean = (rawValue, fallbackValue = false) => {
  if (typeof rawValue === 'boolean') return rawValue
  if (typeof rawValue === 'number') return rawValue !== 0
  if (typeof rawValue === 'string') {
    if (rawValue === 'true' || rawValue === '1') return true
    if (rawValue === 'false' || rawValue === '0') return false
  }
  return fallbackValue
}

const normalizeListFromPayload = (rawValue) => Array.isArray(rawValue) ? rawValue : []

const normalizeObjectFromPayload = (rawValue) => {
  return rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue) ? rawValue : {}
}

const normalizeTextList = (rawValue) => {
  if (Array.isArray(rawValue)) {
    return rawValue
      .map((item) => normalizeText(item).trim())
      .filter(Boolean)
  }

  const singleText = normalizeText(rawValue).trim()
  return singleText ? [singleText] : []
}

const normalizePercentageValue = (rawValue) => {
  const parsedValue = normalizeNumber(rawValue)
  const percentageValue = parsedValue <= 1 ? parsedValue * 100 : parsedValue
  return Math.max(0, Math.min(100, Math.round(percentageValue)))
}

export const buildDefaultProfileSnapshot = () => ({
  learnerTagList: [],
  abilityEntries: [],
  masteryEntries: [],
  summaryText: '',
  weaknessText: '',
  strengthText: ''
})

const getAbilityName = (key) => {
  const names = {
    '言语理解': '言语理解',
    '工作记忆': '工作记忆',
    '知觉推理': '知觉推理',
    '处理速度': '处理速度',
    logical_reasoning: '逻辑推理',
    memory: '记忆能力',
    analysis: '分析能力',
    innovation: '创新能力',
    comprehension: '理解能力',
    application: '应用能力'
  }
  return names[key] || key
}

const normalizeAbilityEntry = (rawKey, rawValue) => ({
  abilityName: getAbilityName(normalizeText(rawKey) || '综合能力'),
  scoreValue: normalizePercentageValue(rawValue)
})

const normalizeKnowledgeMasteryEntry = (rawItem) => ({
  pointId: normalizeText(rawItem?.point_id),
  pointName: normalizeText(rawItem?.point_name ?? rawItem?.name) || '未命名知识点',
  masteryPercent: normalizePercentageValue(rawItem?.mastery_rate)
})

export const normalizeProfilePayload = (rawPayload) => {
  const abilityScoreMap = normalizeObjectFromPayload(rawPayload?.ability_scores)
  const strengthText = normalizeTextList(rawPayload?.strength).join('；')
  const weaknessText = normalizeTextList(rawPayload?.weakness).join('；')

  return {
    ...buildDefaultProfileSnapshot(),
    learnerTagList: normalizeTextList(rawPayload?.learner_tags),
    abilityEntries: Object.entries(abilityScoreMap)
      .filter(([, rawScore]) => rawScore != null)
      .map(([abilityKey, rawScore]) => normalizeAbilityEntry(abilityKey, rawScore)),
    masteryEntries: normalizeListFromPayload(rawPayload?.knowledge_mastery)
      .map((rawItem) => normalizeKnowledgeMasteryEntry(rawItem)),
    summaryText: normalizeText(rawPayload?.profile_summary),
    weaknessText,
    strengthText
  }
}

export const normalizeProfileSuggestionList = (rawPayload) => {
  const mergedSuggestions = [
    ...normalizeTextList(rawPayload?.suggestion),
    ...normalizeTextList(rawPayload?.recommendations),
    ...normalizeTextList(rawPayload?.suggestions)
  ]

  return [...new Set(mergedSuggestions)]
}

export const normalizeAssessmentReadyState = (rawPayload, activeCourseId) => {
  const normalizedCourseId = normalizeNumber(activeCourseId, 0)
  const courseStatusList = normalizeListFromPayload(rawPayload?.courses)
  const activeCourseStatus = courseStatusList.find((courseStatus) => {
    return normalizeNumber(courseStatus?.course_id, 0) === normalizedCourseId
  })

  const abilityDone = normalizeBoolean(rawPayload?.ability_done ?? rawPayload?.ability_completed)
  const courseKnowledgeDone = activeCourseStatus
    ? normalizeBoolean(activeCourseStatus?.knowledge_done ?? activeCourseStatus?.knowledge_completed)
    : normalizeBoolean(rawPayload?.knowledge_done ?? rawPayload?.knowledge_completed)

  return { ready: abilityDone && courseKnowledgeDone }
}

export const getProgressColor = (scoreValue) => {
  if (scoreValue >= 80) return '#22a06b'
  if (scoreValue >= 60) return '#6d927d'
  if (scoreValue >= 40) return '#dd8f1d'
  return '#d45050'
}

export const wrapAxisLabel = (label) => {
  const text = String(label || '')
  if (text.length <= 10) return text
  const segments = []
  for (let index = 0; index < text.length; index += 10) {
    segments.push(text.slice(index, index + 10))
  }
  return segments.join('\n')
}
