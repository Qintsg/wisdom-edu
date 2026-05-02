import { apiJson } from './api.mjs'

const ANSWER_VARIANTS = {
  multipleChoice: ['A', 'C'],
  trueValue: 'true',
  falseValue: 'false'
}

export async function buildDefenseStageTestAnswers(client, nodeId) {
  const payload = await apiJson(client, 'GET', `/api/student/path-nodes/${nodeId}/stage-test`)
  const questions = payload.questions || []
  const answers = {}
  questions.forEach((question, index) => {
    if ((question.question_type || question.type) === 'multiple_choice') {
      answers[String(question.id)] = ANSWER_VARIANTS.multipleChoice
      return
    }
    answers[String(question.id)] = index === 0 ? 'A' : 'B'
  })
  return answers
}

export function pickOptionValue(options = [], offset = 0) {
  if (!options.length) return ''
  const safeOffset = Math.abs(offset) % options.length
  const option = options[safeOffset]
  return option?.['answer_value'] || option.value || option.key || option.label
}

export function buildSurveyAnswers(questions = [], offset = 0) {
  return questions.map((question, index) => ({
    question_id: question.question_id || question.id,
    answer: pickOptionValue(question.options || [], offset + index)
  }))
}

export function buildKnowledgeAnswers(questions = [], offset = 0) {
  return questions.map((question, index) => buildKnowledgeAnswer(question, index, offset))
}

function buildKnowledgeAnswer(question, index, offset) {
  const options = question.options || []
  const type = question.type || question.question_type
  if (type === 'multiple_choice') {
    const selected = options
      .slice(0, Math.min(2, options.length))
      .map((option) => option.value || option?.['answer_value'] || option.key)
    return { question_id: question.question_id || question.id, answer: selected }
  }
  if (type === 'true_false') {
    return {
      question_id: question.question_id || question.id,
      answer: index % 2 === 0 ? ANSWER_VARIANTS.trueValue : ANSWER_VARIANTS.falseValue
    }
  }
  return {
    question_id: question.question_id || question.id,
    answer: pickOptionValue(options, offset + index)
  }
}

export async function submitExamWithGeneratedAnswers(client, examId, courseId, offset = 0) {
  const detail = await apiJson(client, 'GET', `/api/student/exams/${examId}`)
  const answers = {}
  ;(detail.questions || []).forEach((question, index) => {
    const answer = buildKnowledgeAnswer(question, index, offset).answer
    answers[String(question.question_id || question.id)] = answer
  })
  return apiJson(client, 'POST', `/api/student/exams/${examId}/submit`, {
    answers,
    course_id: courseId
  }, null, 180000)
}

export async function waitForFeedbackReady(client, examId, attempts = 40, delayMs = 2000) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const feedback = await apiJson(client, 'GET', `/api/student/feedback/${examId}`).catch(() => null)
    if (feedback?.status === 'completed' || feedback?.status === 'failed') {
      return feedback
    }
    await new Promise((resolve) => setTimeout(resolve, delayMs))
  }
  return null
}
