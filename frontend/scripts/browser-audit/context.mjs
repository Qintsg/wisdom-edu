import { apiJson, createAuthedClient } from './api.mjs'

export async function resolveStudentContext(apiBaseUrl, token) {
  const client = await createAuthedClient(apiBaseUrl, token)

  const coursesResponse = await client.get('/api/courses')
  const coursesPayload = await coursesResponse.json().catch(() => ({}))
  const courses = (coursesPayload.data?.courses || coursesPayload.data || coursesPayload.courses || []).filter(Boolean)
  const currentCourse = courses[0] || null

  let taskId = null
  let examId = null
  let feedbackId = null

  if (currentCourse?.['course_id']) {
    const pathResponse = await client.get(`/api/student/learning-path?course_id=${currentCourse['course_id']}`)
    const pathPayload = await pathResponse.json().catch(() => ({}))
    const nodes = pathPayload.data?.nodes || []
    const firstNode = nodes.find((item) => item?.['node_id']) || nodes[0]
    taskId = firstNode?.['node_id'] || null

    const examsResponse = await client.get(`/api/student/exams?course_id=${currentCourse['course_id']}`)
    const examsPayload = await examsResponse.json().catch(() => ({}))
    const exams = examsPayload.data?.exams || []
    const firstExam = exams.find((item) => item?.['exam_id']) || exams[0]
    const submittedExam = exams.find((item) => item?.['submitted'] && item?.['exam_id']) || null
    examId = firstExam?.['exam_id'] || null
    feedbackId = submittedExam?.['exam_id'] || null
  }

  await client.dispose()

  return {
    currentCourse: currentCourse
      ? {
        course_id: currentCourse.course_id,
        course_name: currentCourse['course_name'] || currentCourse.name,
        class_id: currentCourse['class_id'] || null,
        class_name: currentCourse['class_name'] || ''
      }
      : null,
    taskId,
    examId,
    feedbackId
  }
}

export async function resolveDefenseCourseContext(apiBaseUrl, token) {
  const context = await resolveStudentContext(apiBaseUrl, token)
  if (context.currentCourse?.course_name === '大数据技术与应用') {
    return context
  }

  const client = await createAuthedClient(apiBaseUrl, token)
  try {
    const courses = await apiJson(client, 'GET', '/api/courses')
    const list = (courses.courses || courses || []).filter(Boolean)
    const preferredCourse = list.find((item) => (item.course_name || item.name) === '大数据技术与应用')
    if (preferredCourse) {
      return {
        ...context,
        currentCourse: {
          course_id: preferredCourse.course_id,
          course_name: preferredCourse.course_name || preferredCourse.name,
          class_id: preferredCourse.class_id || null,
          class_name: preferredCourse.class_name || ''
        }
      }
    }
    return context
  } finally {
    await client.dispose()
  }
}

export function buildRoutes(role, context) {
  if (role === 'student') {
    return buildStudentRoutes(context)
  }
  if (role === 'teacher') {
    return [
      '/teacher/dashboard',
      '/teacher/courses',
      '/teacher/classes',
      '/teacher/knowledge',
      '/teacher/resources',
      '/teacher/questions',
      '/teacher/exams',
      '/teacher/settings'
    ]
  }
  return [
    '/admin/dashboard',
    '/admin/users',
    '/admin/courses',
    '/admin/classes',
    '/admin/activation-codes',
    '/admin/logs'
  ]
}

function buildStudentRoutes(context) {
  const routes = [
    '/student/course-select',
    '/student/dashboard',
    '/student/assessment',
    `/student/assessment/report?course_id=${context.currentCourse?.course_id || ''}`,
    '/student/profile',
    '/student/knowledge-map',
    '/student/learning-path',
    '/student/resources',
    '/student/exams',
    '/student/classes',
    '/student/settings'
  ]
  if (context.taskId) routes.push(`/student/task/${context.taskId}`)
  if (context.examId) routes.push(`/student/exam/${context.examId}`)
  if (context.feedbackId) routes.push(`/student/feedback/${context.feedbackId}`)
  return routes
}
