export const aiProgressStages = [
  { at: 0, text: '正在准备分析环境...' },
  { at: 12, text: '正在解析答题数据...' },
  { at: 28, text: '正在评估知识掌握度...' },
  { at: 45, text: '正在生成个性化建议...' },
  { at: 65, text: '正在整合分析报告...' },
  { at: 82, text: '正在优化报告内容...' },
  { at: 92, text: '即将完成，请稍候...' }
]

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

export function buildDefaultExamResult(targetReportId = '') {
  return {
    reportId: targetReportId,
    titleText: '',
    score: 0,
    totalScore: 100,
    correctCount: 0,
    wrongCount: 0,
    accuracy: 0,
    passed: false
  }
}

export function buildDefaultAiAnalysis() {
  return {
    summary: '',
    analysis: '',
    knowledgeGaps: [],
    suggestions: [],
    nextTasks: [],
    conclusion: ''
  }
}

function normalizeReviewOption(option, optionIndex) {
  const fallbackPrefix = String.fromCharCode(65 + (optionIndex % 26))
  const optionPrefix = normalizeText(option?.['letter'] ?? option?.['value'] ?? option?.['label'], fallbackPrefix)
  const optionText = normalizeText(option?.['label'] ?? option?.['content'] ?? option?.['value'], optionPrefix)
  return {
    optionKey: `${optionPrefix}-${optionIndex}`,
    optionPrefix,
    optionText,
    isCorrectOption: option?.['is_correct_option'] === true,
    isStudentSelected: option?.['is_student_selected'] === true
  }
}

function normalizeQuestionDetail(question, questionIndex) {
  return {
    questionId: normalizeIdentifier(question?.['question_id'], String(questionIndex + 1)),
    contentText: normalizeText(question?.['content'], `第 ${questionIndex + 1} 题`),
    isCorrect: question?.['is_correct'] === true,
    studentAnswer: question?.['student_answer'],
    correctAnswer: question?.['correct_answer'],
    studentAnswerText: normalizeText(question?.['student_answer_display']),
    correctAnswerText: normalizeText(question?.['correct_answer_display']),
    analysisText: normalizeText(question?.['analysis']),
    optionList: normalizeListFromPayload(question?.['options']).map((option, optionIndex) => (
      normalizeReviewOption(option, optionIndex)
    ))
  }
}

function normalizeQuestionDetails(resultData) {
  const detailedQuestionList = normalizeListFromPayload(resultData?.['question_details'])
  const fallbackQuestionList = normalizeListFromPayload(resultData?.['questions'])
  const questionList = detailedQuestionList.length > 0 ? detailedQuestionList : fallbackQuestionList
  return questionList.map((question, questionIndex) => normalizeQuestionDetail(question, questionIndex))
}

export function normalizeExamResultPayload(resultData, targetReportId = '') {
  const normalizedQuestionDetails = normalizeQuestionDetails(resultData)
  const correctCount = Math.max(
    0,
    normalizeNumber(resultData?.['correct_count'], normalizedQuestionDetails.filter((item) => item.isCorrect).length)
  )
  const totalCount = Math.max(0, normalizeNumber(resultData?.['total_count'], normalizedQuestionDetails.length))
  const accuracy = normalizeNumber(resultData?.['accuracy'], totalCount ? Math.round((correctCount / totalCount) * 1000) / 10 : 0)

  return {
    examResult: {
      reportId: targetReportId,
      titleText: normalizeText(resultData?.['exam_title'], '作业反馈'),
      score: normalizeNumber(resultData?.['score'], 0),
      totalScore: Math.max(normalizeNumber(resultData?.['total_score'], 100), 1),
      correctCount,
      wrongCount: Math.max(totalCount - correctCount, 0),
      accuracy,
      passed: resultData?.['passed'] === true
    },
    questionDetails: normalizedQuestionDetails
  }
}

function normalizeTaskText(task) {
  if (typeof task === 'string') return normalizeText(task)
  if (task && typeof task === 'object') {
    const preferredText = normalizeText(task['description'] ?? task['title'] ?? task['content'])
    return preferredText || JSON.stringify(task)
  }
  return ''
}

function normalizeMasteryChange(item, itemIndex) {
  return {
    knowledgePointId: normalizeIdentifier(item?.['knowledge_point_id'], String(itemIndex + 1)),
    knowledgePointName: normalizeText(item?.['knowledge_point_name'], `知识点 ${itemIndex + 1}`),
    masteryBefore: normalizeNumber(item?.['mastery_before'], 0),
    masteryAfter: normalizeNumber(item?.['mastery_after'], 0)
  }
}

export function normalizeAiFeedbackPayload(feedbackData) {
  const overview = feedbackData && typeof feedbackData === 'object' && feedbackData['overview'] && typeof feedbackData['overview'] === 'object'
    ? feedbackData['overview']
    : {}
  const normalizedStatus = normalizeText(feedbackData?.['status'], 'completed') || 'completed'

  return {
    status: normalizedStatus,
    pollIntervalMs: Math.max(normalizeNumber(feedbackData?.['poll_interval_ms'], 2000), 500),
    analysis: {
      summary: normalizeText(
        feedbackData?.['summary'] ?? overview['summary'],
        normalizedStatus === 'pending' ? '成绩已生成，AI 报告正在生成中...' : '暂无分析摘要'
      ),
      analysis: normalizeText(feedbackData?.['analysis']),
      knowledgeGaps: normalizeListFromPayload(feedbackData?.['knowledge_gaps'] ?? overview['knowledge_gaps'])
        .map((item) => normalizeText(item))
        .filter(Boolean),
      suggestions: normalizeListFromPayload(feedbackData?.['recommendations'])
        .map((item) => normalizeTaskText(item))
        .filter(Boolean),
      nextTasks: normalizeListFromPayload(feedbackData?.['next_tasks'])
        .map((item) => normalizeTaskText(item))
        .filter(Boolean),
      conclusion: normalizeText(feedbackData?.['conclusion'])
    },
    masteryChanges: normalizeListFromPayload(feedbackData?.['mastery_changes'])
      .map((item, itemIndex) => normalizeMasteryChange(item, itemIndex))
  }
}

export function formatAnswer(answer) {
  if (answer === null || answer === undefined || answer === '') return '未作答'
  if (typeof answer === 'boolean') return answer ? '正确' : '错误'
  if (Array.isArray(answer)) return answer.join('、')
  if (typeof answer === 'object') {
    if (Array.isArray(answer.answers)) return answer.answers.join('、')
    if (answer.answer !== undefined) return String(answer.answer)
  }
  return String(answer)
}
