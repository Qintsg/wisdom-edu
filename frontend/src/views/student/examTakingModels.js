export function normalizeText(value, fallback = '') {
  if (Array.isArray(value)) return normalizeText(value[0], fallback)
  if (typeof value === 'string') {
    const trimmedValue = value.trim()
    return trimmedValue || fallback
  }
  if (typeof value === 'number') return String(value)
  return fallback
}

function normalizeNumber(value, fallback = 0) {
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : fallback
}

export function normalizeIdentifier(value, fallback = '') {
  if (Array.isArray(value)) return normalizeIdentifier(value[0], fallback)
  if (value === null || value === undefined) return fallback
  const normalizedValue = String(value).trim()
  return normalizedValue || fallback
}

function normalizeListFromPayload(value) {
  return Array.isArray(value) ? value : []
}

function normalizeQuestionType(type, optionCount = 0) {
  const normalizedType = normalizeText(type).toLowerCase()
  const questionTypeMap = {
    single: 'singleChoice',
    single_choice: 'singleChoice',
    multiple: 'multipleChoice',
    multiple_choice: 'multipleChoice',
    true_false: 'trueFalse',
    judge: 'trueFalse',
    fill_blank: 'fillBlank',
    fill: 'fillBlank',
    short_answer: 'shortAnswer',
    essay: 'shortAnswer'
  }
  return questionTypeMap[normalizedType] || (optionCount > 0 ? 'singleChoice' : 'shortAnswer')
}

function getQuestionTagType(type) {
  const types = {
    singleChoice: 'info',
    multipleChoice: 'warning',
    trueFalse: 'success',
    fillBlank: 'info',
    shortAnswer: 'danger'
  }
  return types[type] || 'info'
}

function getQuestionTypeName(type) {
  const names = {
    singleChoice: '单选',
    multipleChoice: '多选',
    trueFalse: '判断',
    fillBlank: '填空',
    shortAnswer: '简答'
  }
  return names[type] || '未知'
}

export function buildDefaultExamInfo(targetExamId = '') {
  return {
    examId: targetExamId,
    titleText: 'Loading...',
    durationMinutes: 60
  }
}

function normalizeQuestionOption(option, optionIndex) {
  const fallbackLabel = String.fromCharCode(65 + (optionIndex % 26))
  const primitiveOption = typeof option === 'string' || typeof option === 'number' ? String(option) : ''
  const optionValue = normalizeText(option?.['value'] ?? option?.['label'] ?? primitiveOption, fallbackLabel)
  const optionContent = normalizeText(option?.['content'] ?? option?.['text'] ?? primitiveOption, optionValue)
  return {
    optionValue,
    optionLabel: optionValue,
    optionContent
  }
}

function normalizeExamQuestion(question, questionIndex) {
  const optionList = normalizeListFromPayload(question?.['options']).map((option, optionIndex) => (
    normalizeQuestionOption(option, optionIndex)
  ))
  const answerMode = normalizeQuestionType(question?.['type'] ?? question?.['question_type'], optionList.length)
  return {
    questionId: normalizeIdentifier(question?.['question_id'] ?? question?.['id'], String(questionIndex + 1)),
    stem: normalizeText(question?.['content'] ?? question?.['title'], `题目 ${questionIndex + 1}`),
    answerMode,
    questionTypeText: getQuestionTypeName(answerMode),
    questionTagType: getQuestionTagType(answerMode),
    score: normalizeNumber(question?.['score'], 0),
    optionList
  }
}

export function normalizeExamDetail(payload, fallbackExamId = '') {
  const normalizedQuestions = normalizeListFromPayload(payload?.['questions']).map((question, questionIndex) => (
    normalizeExamQuestion(question, questionIndex)
  ))
  return {
    examId: normalizeIdentifier(payload?.['exam_id'] ?? payload?.['id'], fallbackExamId),
    titleText: normalizeText(payload?.['title'], '作业'),
    durationMinutes: Math.max(normalizeNumber(payload?.['duration'], 60), 1),
    questions: normalizedQuestions
  }
}

export function createEmptyAnswer(question) {
  return question?.answerMode === 'multipleChoice' ? [] : ''
}

export function normalizeFeedbackRouteId(payload, fallbackExamId = '') {
  if (payload && typeof payload !== 'object') return normalizeIdentifier(payload, fallbackExamId)
  const feedbackReport = payload && typeof payload === 'object' ? payload['feedback_report'] : null
  return normalizeIdentifier(
    feedbackReport?.['exam_id']
    ?? feedbackReport?.['report_id']
    ?? payload?.['exam_id']
    ?? payload?.['report_id'],
    fallbackExamId
  )
}

export function formatTime(seconds) {
  if (seconds < 0) return '00:00:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}
