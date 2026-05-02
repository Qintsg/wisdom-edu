import { toBackendAbsoluteUrl } from '@/api/backend'

export const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') return rawValue
  if (typeof rawValue === 'number') return String(rawValue)
  return ''
}

export const normalizeIdentifier = (rawValue) => normalizeText(rawValue).trim()

export const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

export const normalizeNullableNumber = (rawValue) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : null
}

export const normalizeBoolean = (rawValue, fallbackValue = false) => {
  if (typeof rawValue === 'boolean') return rawValue
  if (typeof rawValue === 'number') return rawValue !== 0
  if (typeof rawValue === 'string') {
    const loweredValue = rawValue.trim().toLowerCase()
    if (['true', '1', 'yes'].includes(loweredValue)) return true
    if (['false', '0', 'no'].includes(loweredValue)) return false
  }
  return fallbackValue
}

export const normalizeObjectFromPayload = (rawValue) => {
  return rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue) ? rawValue : {}
}

export const normalizeListFromPayload = (rawValue) => Array.isArray(rawValue) ? rawValue : []

export const normalizeStringList = (rawValue) => {
  return normalizeListFromPayload(rawValue)
    .map((item) => normalizeText(item).trim())
    .filter(Boolean)
}

export const normalizePercentValue = (rawValue) => {
  const numericValue = normalizeNumber(rawValue)
  return Math.round((numericValue <= 1 ? numericValue * 100 : numericValue) || 0)
}

export const formatDuration = (rawSeconds) => {
  const totalSeconds = normalizeNumber(rawSeconds)
  if (totalSeconds <= 0) return '未知时长'
  const minutes = Math.round(totalSeconds / 60)
  if (minutes < 1) return `${totalSeconds}秒`
  if (minutes < 60) return `${minutes}分钟`
  const hours = Math.floor(minutes / 60)
  const remainMinutes = minutes % 60
  return remainMinutes > 0 ? `${hours}小时${remainMinutes}分钟` : `${hours}小时`
}

export const isEmptyStageAnswer = (answerValue) => {
  if (Array.isArray(answerValue)) return answerValue.length === 0
  return normalizeText(answerValue).trim().length === 0
}

export const buildDefaultTaskModel = () => ({
  taskId: '',
  titleText: '',
  descriptionText: '',
  pointNameText: '',
  knowledgePointId: null
})

export const buildDefaultResourceModel = () => ({
  resourceId: '',
  titleText: '',
  resourceType: 'document',
  descriptionText: '',
  durationText: '未知时长',
  isCompleted: false,
  isRequired: true,
  resourceUrl: '',
  isServerHosted: false,
  sourceText: '',
  providerText: ''
})

export const buildDefaultNodeIntroModel = () => ({
  introductionText: '',
  keyConceptList: [],
  learningTipsText: '',
  difficultyLevel: ''
})

export const buildDefaultNodeExamModel = () => ({
  hasExam: false,
  examId: '',
  titleText: '',
  passScore: 60
})

export const buildDefaultNodeQuizResultModel = () => ({
  hasResult: false,
  isPassed: false,
  scoreValue: 0
})

export const buildDefaultStageFeedbackReportModel = () => ({
  summaryText: '',
  analysisText: '',
  knowledgeGapList: [],
  recommendationList: [],
  nextTaskList: [],
  conclusionText: ''
})

export const buildDefaultStageTestResultModel = () => ({
  hasResult: false,
  scoreValue: 0,
  totalScoreValue: 100,
  isPassed: false,
  passThresholdValue: 60,
  correctCount: 0,
  totalCount: 0,
  accuracyPercent: 0,
  mistakeList: [],
  masteryChangeList: [],
  feedbackReport: buildDefaultStageFeedbackReportModel(),
  isPathRefreshed: false
})

export const normalizeDifficultyLevel = (rawDifficulty) => {
  const difficultyText = normalizeText(rawDifficulty).trim()
  return ['easy', 'medium', 'hard'].includes(difficultyText) ? difficultyText : ''
}

export const normalizeTaskPayload = (rawPayload, fallbackNodeId, fallbackPointId) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    taskId: normalizeIdentifier(payload.node_id ?? payload.id ?? fallbackNodeId),
    titleText: normalizeText(payload.node_title ?? payload.title) || '学习任务',
    descriptionText: normalizeText(payload.goal ?? payload.description),
    pointNameText: normalizeText(payload.knowledge_point_name ?? payload.node_title ?? payload.title),
    knowledgePointId: normalizeNullableNumber(payload.knowledge_point_id ?? fallbackPointId)
  }
}

export const normalizeNodeIntroPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    introductionText: normalizeText(payload.introduction),
    keyConceptList: normalizeStringList(payload.key_concepts),
    learningTipsText: normalizeText(payload.learning_tips),
    difficultyLevel: normalizeDifficultyLevel(payload.difficulty)
  }
}

export const normalizeResourceType = (rawType) => {
  const resourceType = normalizeText(rawType).trim().toLowerCase()
  return resourceType || 'document'
}

export const normalizeResourcePayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  const rawResourceUrl = normalizeText(payload.url)
  const resourceUrl = toBackendAbsoluteUrl(rawResourceUrl)
  const explicitServerFlag = payload.is_internal
  const isServerHosted = explicitServerFlag !== undefined
    ? normalizeBoolean(explicitServerFlag)
    : Boolean(rawResourceUrl) && (rawResourceUrl.startsWith('/media') || rawResourceUrl.startsWith('/api'))

  return {
    ...buildDefaultResourceModel(),
    resourceId: normalizeIdentifier(payload.resource_id ?? payload.id),
    titleText: normalizeText(payload.title) || '未命名资源',
    resourceType: normalizeResourceType(payload.type ?? payload.resource_type),
    descriptionText: normalizeText(payload.description) || (!isServerHosted ? '外部扩展学习资源' : ''),
    durationText: formatDuration(payload.duration),
    isCompleted: normalizeBoolean(payload.completed),
    isRequired: payload.required === undefined ? true : normalizeBoolean(payload.required, true),
    resourceUrl,
    isServerHosted,
    sourceText: normalizeText(payload.source),
    providerText: normalizeText(payload.provider)
  }
}

export const normalizeNodeExamPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  const examId = normalizeIdentifier(payload.exam_id ?? payload.id)
  return {
    hasExam: Boolean(examId),
    examId,
    titleText: normalizeText(payload.title),
    passScore: normalizeNumber(payload.pass_score, 60)
  }
}

const normalizeStageQuestionOptionPayload = (rawPayload, optionIndex) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  const fallbackKey = String.fromCharCode(65 + optionIndex)
  const optionKey = normalizeText(payload.key ?? payload.label ?? payload.value) || fallbackKey
  return {
    optionKey,
    optionLabel: normalizeText(payload.value ?? payload.text ?? payload.label ?? payload.content) || optionKey,
    answerValue: normalizeText(payload.answer_value ?? payload.value ?? optionKey)
  }
}

export const normalizeStageQuestionPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    questionId: normalizeIdentifier(payload.id),
    contentText: normalizeText(payload.content ?? payload.question_text),
    questionType: normalizeText(payload.question_type) || 'single_choice',
    difficultyLevel: normalizeDifficultyLevel(payload.difficulty),
    scoreValue: normalizeNumber(payload.score),
    optionList: normalizeListFromPayload(payload.options).map((item, optionIndex) => normalizeStageQuestionOptionPayload(item, optionIndex))
  }
}

const normalizeStageFeedbackReportPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    summaryText: normalizeText(payload.summary),
    analysisText: normalizeText(payload.analysis),
    knowledgeGapList: normalizeStringList(payload.knowledge_gaps),
    recommendationList: normalizeStringList(payload.recommendations),
    nextTaskList: normalizeStringList(payload.next_tasks),
    conclusionText: normalizeText(payload.conclusion ?? payload.encouragement)
  }
}

const normalizeStageMasteryChangePayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    pointId: normalizeIdentifier(payload.knowledge_point_id ?? payload.point_id ?? payload.id),
    pointName: normalizeText(payload.knowledge_point_name ?? payload.point_name ?? payload.name) || '未知知识点',
    masteryBeforePercent: normalizePercentValue(payload.mastery_before),
    masteryAfterPercent: normalizePercentValue(payload.mastery_after)
  }
}

const normalizeStageMistakePayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    questionId: normalizeIdentifier(payload.question_id),
    questionText: normalizeText(payload.question_text),
    studentAnswer: payload.student_answer,
    correctAnswer: payload.correct_answer,
    studentAnswerDisplayText: normalizeText(payload.student_answer_display),
    correctAnswerDisplayText: normalizeText(payload.correct_answer_display),
    analysisText: normalizeText(payload.analysis)
  }
}

export const normalizeStageTestResultPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  if (!Object.keys(payload).length) return buildDefaultStageTestResultModel()

  return {
    hasResult: true,
    scoreValue: normalizeNumber(payload.score),
    totalScoreValue: normalizeNumber(payload.total_score, 100),
    isPassed: normalizeBoolean(payload.passed),
    passThresholdValue: normalizeNumber(payload.pass_threshold, 60),
    correctCount: normalizeNumber(payload.correct_count ?? payload.correct),
    totalCount: normalizeNumber(payload.total_count ?? payload.total),
    accuracyPercent: normalizeNumber(payload.accuracy),
    mistakeList: normalizeListFromPayload(payload.mistakes).map(normalizeStageMistakePayload),
    masteryChangeList: normalizeListFromPayload(payload.mastery_changes).map(normalizeStageMasteryChangePayload),
    feedbackReport: normalizeStageFeedbackReportPayload(payload.feedback_report),
    isPathRefreshed: normalizeBoolean(payload.path_refreshed)
  }
}

export const buildStageTestAnswers = (questionList) => {
  return questionList.reduce((answerMap, questionItem) => {
    answerMap[questionItem.questionId] = questionItem.questionType === 'multiple_choice' ? [] : ''
    return answerMap
  }, {})
}

export const getDifficultyTagType = (difficultyLevel) => {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[difficultyLevel] || 'info'
}

export const getDifficultyLabel = (difficultyLevel) => {
  const map = { easy: '基础', medium: '中等', hard: '进阶' }
  return map[difficultyLevel] || '未知'
}

export const formatStageAnswer = (answerValue) => {
  if (answerValue === null || answerValue === undefined || answerValue === '') return '未作答'
  if (typeof answerValue === 'boolean') return answerValue ? '正确' : '错误'
  if (Array.isArray(answerValue)) return answerValue.map((item) => normalizeText(item)).filter(Boolean).join('、')

  const answerPayload = normalizeObjectFromPayload(answerValue)
  if (Object.keys(answerPayload).length) {
    if (Array.isArray(answerPayload.answers)) {
      return answerPayload.answers.map((item) => normalizeText(item)).filter(Boolean).join('、')
    }
    if (typeof answerPayload.answer === 'boolean') return answerPayload.answer ? '正确' : '错误'
    if (answerPayload.answer !== undefined) return normalizeText(answerPayload.answer)
  }
  return normalizeText(answerValue)
}
