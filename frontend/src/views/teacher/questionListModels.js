export const questionTypeOptions = [
  { optionLabel: '单选题', optionValue: 'single_choice' },
  { optionLabel: '多选题', optionValue: 'multiple_choice' },
  { optionLabel: '判断题', optionValue: 'true_false' },
  { optionLabel: '填空题', optionValue: 'fill_blank' },
  { optionLabel: '简答题', optionValue: 'short_answer' },
  { optionLabel: '编程题', optionValue: 'code' }
]

export const difficultyOptions = [
  { optionLabel: '简单', optionValue: 'easy' },
  { optionLabel: '中等', optionValue: 'medium' },
  { optionLabel: '困难', optionValue: 'hard' }
]

const questionTypeLabelMap = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题',
  code: '编程题'
}

const difficultyLabelMap = {
  easy: '简单',
  medium: '中等',
  hard: '困难'
}

export const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') return rawValue
  if (typeof rawValue === 'number') return String(rawValue)
  return ''
}

const normalizeIdentifier = (rawValue) => normalizeText(rawValue).trim()

const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

const normalizeListFromPayload = (rawValue) => Array.isArray(rawValue) ? rawValue : []

const normalizeQuestionType = (rawValue) => normalizeText(rawValue) || 'single_choice'

const normalizeDifficulty = (rawValue) => normalizeText(rawValue) || 'medium'

const normalizeQuestionOptionTextList = (rawValue) => {
  const optionTextList = normalizeListFromPayload(rawValue)
    .map((rawOption) => {
      if (rawOption && typeof rawOption === 'object') {
        return normalizeText(rawOption.content ?? rawOption.text ?? rawOption.label).trim()
      }
      return normalizeText(rawOption).trim()
    })
    .filter(Boolean)

  return optionTextList.length ? optionTextList : ['', '', '', '']
}

const normalizeQuestionPointIdList = (rawValue) => {
  return normalizeListFromPayload(rawValue)
    .map((rawPoint) => {
      if (rawPoint && typeof rawPoint === 'object') {
        return normalizeIdentifier(rawPoint.point_id ?? rawPoint.id ?? rawPoint.knowledge_point_id)
      }
      return normalizeIdentifier(rawPoint)
    })
    .filter(Boolean)
}

const normalizeQuestionAnswerText = (rawValue) => {
  if (rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue)) {
    return normalizeText(rawValue.answer ?? rawValue.value)
  }
  return normalizeText(rawValue)
}

const buildDefaultKnowledgePointOption = () => ({
  pointId: '',
  pointName: ''
})

const buildDefaultQuestionRecord = () => ({
  questionId: '',
  contentText: '',
  questionTypeText: 'single_choice',
  typeLabel: '单选题',
  difficultyText: 'medium',
  difficultyLabel: '中等',
  scoreValue: null,
  pointIdList: [],
  knowledgePointText: '',
  optionTextList: ['', '', '', ''],
  answerText: '',
  analysisText: ''
})

const normalizeKnowledgePointOption = (rawPoint) => ({
  ...buildDefaultKnowledgePointOption(),
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.knowledge_point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点'
})

const extractKnowledgePointNameList = (rawValue) => {
  return normalizeListFromPayload(rawValue)
    .map((rawPoint) => {
      if (rawPoint && typeof rawPoint === 'object') {
        return normalizeText(rawPoint.point_name ?? rawPoint.name).trim()
      }
      return ''
    })
    .filter(Boolean)
}

const resolveKnowledgePointText = (pointIdList, pointNameById, rawPoints) => {
  const explicitPointNames = extractKnowledgePointNameList(rawPoints)
  if (explicitPointNames.length) return explicitPointNames.join(', ')

  return pointIdList
    .map((pointId) => pointNameById[pointId] || '')
    .filter(Boolean)
    .join(', ')
}

export const normalizeQuestionRecord = (rawQuestion, pointNameById) => {
  const questionTypeText = normalizeQuestionType(rawQuestion?.type ?? rawQuestion?.question_type)
  const difficultyText = normalizeDifficulty(rawQuestion?.difficulty)
  const pointIdList = normalizeQuestionPointIdList(rawQuestion?.points ?? rawQuestion?.knowledge_points)

  return {
    ...buildDefaultQuestionRecord(),
    questionId: normalizeIdentifier(rawQuestion?.question_id ?? rawQuestion?.id),
    contentText: normalizeText(rawQuestion?.content),
    questionTypeText,
    typeLabel: questionTypeLabelMap[questionTypeText] || questionTypeText,
    difficultyText,
    difficultyLabel: difficultyLabelMap[difficultyText] || difficultyText,
    scoreValue: rawQuestion?.score === undefined || rawQuestion?.score === null || rawQuestion?.score === ''
      ? null
      : normalizeNumber(rawQuestion?.score, 1),
    pointIdList,
    knowledgePointText: resolveKnowledgePointText(pointIdList, pointNameById, rawQuestion?.points ?? rawQuestion?.knowledge_points),
    optionTextList: normalizeQuestionOptionTextList(rawQuestion?.options),
    answerText: normalizeQuestionAnswerText(rawQuestion?.answer),
    analysisText: normalizeText(rawQuestion?.analysis)
  }
}

export const normalizeQuestionListPayload = (rawPayload, pointNameById) => ({
  records: normalizeListFromPayload(rawPayload?.questions)
    .map((rawQuestion) => normalizeQuestionRecord(rawQuestion, pointNameById)),
  totalCount: normalizeNumber(rawPayload?.total)
})

export const normalizeKnowledgePointListPayload = (rawPayload) => {
  return normalizeListFromPayload(rawPayload?.points)
    .map((rawPoint) => normalizeKnowledgePointOption(rawPoint))
}

export const buildDefaultQuestionForm = () => ({
  questionType: 'single_choice',
  contentText: '',
  optionTextList: ['', '', '', ''],
  answerText: '',
  analysisText: '',
  difficultyText: 'medium',
  scoreValue: 1,
  pointIdList: []
})

export const supportsOptions = (questionTypeText) => {
  return questionTypeText === 'single_choice' || questionTypeText === 'multiple_choice'
}

export const getOptionLabel = (optionIndex) => String.fromCharCode(65 + optionIndex)

export const getDifficultyTagType = (difficultyText) => {
  if (difficultyText === 'hard') return 'danger'
  if (difficultyText === 'medium') return 'warning'
  return 'success'
}

export const formatScoreText = (scoreValue) => {
  return typeof scoreValue === 'number' && Number.isFinite(scoreValue)
    ? String(scoreValue)
    : '—'
}
