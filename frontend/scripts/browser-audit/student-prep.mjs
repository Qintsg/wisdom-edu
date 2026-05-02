import { apiJson } from './api.mjs'
import {
  buildKnowledgeAnswers,
  buildSurveyAnswers,
  submitExamWithGeneratedAnswers,
  waitForFeedbackReady
} from './answers.mjs'

export async function ensureInitialAssessments(client, courseId, variantOffset = 0) {
  const status = await apiJson(client, 'GET', `/api/student/assessments/status?course_id=${courseId}`)

  if (!status?.['ability_done']) {
    const ability = await apiJson(client, 'GET', `/api/student/assessments/initial/ability?course_id=${courseId}`)
    await apiJson(client, 'POST', '/api/student/assessments/initial/ability/submit', {
      course_id: courseId,
      answers: buildSurveyAnswers(ability.questions || [], variantOffset)
    })
  }

  if (!status?.['habit_done']) {
    const habit = await apiJson(client, 'GET', `/api/student/assessments/initial/habit?course_id=${courseId}`)
    await apiJson(client, 'POST', '/api/student/assessments/initial/habit/submit', {
      course_id: courseId,
      responses: buildSurveyAnswers(habit.questions || [], variantOffset + 1)
    })
  }

  const refreshed = await apiJson(client, 'GET', `/api/student/assessments/status?course_id=${courseId}`)
  if (!refreshed?.['knowledge_done']) {
    const knowledge = await apiJson(client, 'GET', `/api/student/assessments/initial/knowledge?course_id=${courseId}`)
    await apiJson(client, 'POST', '/api/student/assessments/initial/knowledge/submit', {
      course_id: courseId,
      answers: buildKnowledgeAnswers(knowledge.questions || [], variantOffset + 2)
    })
  }
}

export async function ensureProfileAndPath(client, courseId) {
  await apiJson(client, 'POST', '/api/student/assessments/profile/generate', { course_id: courseId }).catch(() => null)
  await apiJson(client, 'POST', '/api/student/ai/refresh-profile', { course_id: courseId }, null, 180000).catch(() => null)
  const profile = await apiJson(client, 'GET', `/api/student/profile?course_id=${courseId}`)
  const pathData = await apiJson(client, 'GET', `/api/student/learning-path?course_id=${courseId}`)
  return { profile, pathData }
}

export async function fetchExamList(client, courseId) {
  const listData = await apiJson(client, 'GET', `/api/student/exams?course_id=${courseId}`)
  return listData.exams || []
}

export async function refreshLearningPath(client, courseId) {
  return apiJson(client, 'POST', '/api/student/ai/refresh-learning-path', {
    course_id: courseId
  }, null, 180000).catch(() => null)
}

export async function ensureNeo4jKnowledgeMap(client, courseId) {
  const knowledgeMap = await apiJson(client, 'GET', `/api/student/knowledge-map?course_id=${courseId}`)
  const stats = knowledgeMap.stats || {}
  if (stats.data_source !== 'neo4j' || (stats.node_count || 0) <= 0 || (stats.edge_count || 0) <= 0) {
    throw new Error(`知识图谱未使用Neo4j或图数据为空: ${JSON.stringify(stats)}`)
  }
  return stats
}

export async function prepareStableStudent(client, courseId, variantOffset = 0) {
  await ensureInitialAssessments(client, courseId, variantOffset)
  await ensureProfileAndPath(client, courseId)
  await ensureNeo4jKnowledgeMap(client, courseId)
  const exams = await fetchExamList(client, courseId)
  let submittedExam = exams.find((item) => item?.['submitted'])
  if (!submittedExam) {
    submittedExam = await submitFirstAvailableExam(client, exams, courseId, variantOffset)
  }
  const refreshedPath = await refreshLearningPath(client, courseId)
  const finalProfile = await apiJson(client, 'GET', `/api/student/profile?course_id=${courseId}`)
  const finalPath = await apiJson(client, 'GET', `/api/student/learning-path?course_id=${courseId}`)
  return {
    kind: 'stable',
    reportExamId: submittedExam?.['exam_id'] || null,
    refreshSummary: refreshedPath?.['change_summary'] || null,
    profileSummary: finalProfile?.['profile_summary'] || '',
    pathNodeCount: (finalPath?.nodes || []).length
  }
}

async function submitFirstAvailableExam(client, exams, courseId, variantOffset) {
  const targetExam = exams.find((item) => !item?.['submitted']) || exams[0]
  if (!targetExam?.['exam_id']) {
    return null
  }
  await submitExamWithGeneratedAnswers(client, targetExam['exam_id'], courseId, variantOffset)
  await waitForFeedbackReady(client, targetExam['exam_id'])
  return { exam_id: targetExam['exam_id'] }
}

export async function prepareTriggerStudent(client, courseId, variantOffset = 0) {
  await ensureInitialAssessments(client, courseId, variantOffset)
  await ensureProfileAndPath(client, courseId)
  await ensureNeo4jKnowledgeMap(client, courseId)
  const exams = await fetchExamList(client, courseId)
  const nextExam = exams.find((item) => !item?.['submitted']) || exams[0] || null
  return {
    kind: 'trigger',
    triggerExamId: nextExam?.exam_id || null
  }
}
