import fs from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { chromium, request as playwrightRequest } from 'playwright'

const DEFAULT_PASSWORDS = {
  student: 'Test123456',
  student1: 'Test123456',
  student2: 'Test123456',
  student3: 'Test123456',
  teacher: 'Test123456',
  teacher1: 'Test123456',
  admin: 'Admin123456'
}

function parseArgs(argv) {
  const args = {
    frontendUrl: 'http://127.0.0.1:3000',
    apiBaseUrl: 'http://127.0.0.1:8000',
    outputDir: '../output/playwright',
    headed: false,
    scenario: 'audit'
  }

  for (let index = 2; index < argv.length; index += 1) {
    const current = argv[index]
    if (current === '--frontend-url') args.frontendUrl = argv[index + 1]
    if (current === '--api-base-url') args.apiBaseUrl = argv[index + 1]
    if (current === '--output-dir') args.outputDir = argv[index + 1]
    if (current === '--scenario') args.scenario = argv[index + 1]
    if (current === '--headed') args.headed = true
  }
  return args
}

async function ensureDir(target) {
  await fs.mkdir(target, { recursive: true })
}

async function writeJson(filePath, data) {
  await ensureDir(path.dirname(filePath))
  await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf-8')
}

async function readJson(filePath) {
  try {
    const raw = await fs.readFile(filePath, 'utf-8')
    return JSON.parse(raw)
  } catch {
    return null
  }
}

async function loginApi(apiBaseUrl, username, password) {
  const client = await playwrightRequest.newContext({ baseURL: apiBaseUrl })
  const response = await client.post('/api/auth/login', {
    data: { username, password }
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok()) {
    throw new Error(`登录失败: ${username}`)
  }
  const data = payload.data || {}
  return {
    token: data.access || data.token,
    refresh: data.refresh || data['refresh_token'] || '',
    client
  }
}

async function ensureBackendReady(apiBaseUrl) {
  const client = await playwrightRequest.newContext({ baseURL: apiBaseUrl })
  try {
    const response = await client.get('/health/', { timeout: 10000 })
    if (!response.ok()) {
      throw new Error(`后端健康检查失败: ${response.status()}`)
    }
  } finally {
    await client.dispose()
  }
}

async function createAuthedClient(apiBaseUrl, token) {
  return playwrightRequest.newContext({
    baseURL: apiBaseUrl,
    extraHTTPHeaders: { Authorization: `Bearer ${token}` }
  })
}

async function apiJson(client, method, url, data = undefined, timeout = 180000) {
  const response = await client.fetch(url, {
    method,
    data,
    timeout
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok()) {
    throw new Error(payload?.msg || `请求失败: ${method} ${url}`)
  }
  return payload.data || payload
}

async function resolveStudentContext(apiBaseUrl, token) {
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

async function resolveDefenseCourseContext(apiBaseUrl, token) {
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

function buildRoutes(role, context) {
  if (role === 'student') {
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

function slugifyRoute(route) {
  return route.replace(/^[\\/]+/, '').replace(/[?=&/:]+/g, '-')
}

async function createBrowserSession(browser, config) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 960 }
  })
  await context.addInitScript(({ token, refresh, currentCourse }) => {
    if (token) {
      localStorage.setItem('access_token', token)
      localStorage.setItem('token', token)
    }
    if (refresh) {
      localStorage.setItem('refresh_token', refresh)
    }
    if (currentCourse) {
      localStorage.setItem('current_course', JSON.stringify(currentCourse))
    }
  }, {
    token: config.token,
    refresh: config.refresh,
    currentCourse: config.currentCourse
  })

  const page = await context.newPage()
  const errors = []
  const failedRequests = []

  page.on('console', (message) => {
    if (['error', 'warning'].includes(message.type())) {
      errors.push({
        route: page.url(),
        type: message.type(),
        text: message.text()
      })
    }
  })
  page.on('requestfailed', (request) => {
    failedRequests.push({
      route: page.url(),
      url: request.url(),
      method: request.method(),
      failure: request.failure()?.errorText || 'requestfailed'
    })
  })

  return { context, page, errors, failedRequests }
}

async function captureRoute(page, frontendUrl, route, screenshotDir, label = null) {
  const targetUrl = `${frontendUrl}${route}`
  await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 60000 })
  const fileName = `${label || slugifyRoute(route)}.png`
  await page.screenshot({
    path: path.join(screenshotDir, fileName),
    fullPage: true
  })
  return { route, url: page.url(), screenshot: fileName, ok: true }
}

async function captureCurrentPage(page, screenshotDir, label) {
  const fileName = `${label}.png`
  await page.screenshot({
    path: path.join(screenshotDir, fileName),
    fullPage: true
  })
  return { route: page.url(), url: page.url(), screenshot: fileName, ok: true }
}

function resolveDefenseDemoArchivePath(args) {
  return path.resolve(args.outputDir, '..', '答辩演示课程导入包.zip')
}

async function ensureDefenseArchiveExists(args) {
  const archivePath = resolveDefenseDemoArchivePath(args)
  await fs.access(archivePath)
  return archivePath
}

async function buildDefenseStageTestAnswers(client, nodeId) {
  const payload = await apiJson(client, 'GET', `/api/student/path-nodes/${nodeId}/stage-test`)
  const questions = payload.questions || []
  const answers = {}
  questions.forEach((question, index) => {
    if ((question.question_type || question.type) === 'multiple_choice') {
      answers[String(question.id)] = ['A', 'C']
      return
    }
    answers[String(question.id)] = index === 0 ? 'A' : 'B'
  })
  return answers
}

async function openTeacherImportCourseFlow(session, args, courseName, screenshotDir) {
  const archivePath = await ensureDefenseArchiveExists(args)
  const steps = []

  await session.page.goto(`${args.frontendUrl}/teacher/courses`, { waitUntil: 'networkidle', timeout: 60000 })
  await session.page.getByRole('button', { name: '导入建课' }).click()

  const popup = await session.page.waitForEvent('popup', { timeout: 60000 })
  await popup.waitForLoadState('networkidle')
  await popup.getByPlaceholder('请输入课程名称').fill(courseName)
  await popup.locator('input[type="file"]').setInputFiles(archivePath)
  await popup.getByRole('button', { name: '创建课程' }).click()
  await popup.waitForURL(/\/teacher\/courses\/\d+/, { timeout: 180000 })
  steps.push(await captureCurrentPage(popup, screenshotDir, 'teacher-course-created'))

  const courseId = popup.url().match(/\/teacher\/courses\/(\d+)/)?.[1]
  if (courseId) {
    await popup.goto(`${args.frontendUrl}/teacher/courses/${courseId}/workspace/questions`, {
      waitUntil: 'networkidle',
      timeout: 60000
    })
    steps.push(await captureCurrentPage(popup, screenshotDir, 'teacher-question-workspace'))
    const editButton = popup.getByRole('button', { name: '编辑' }).first()
    if (await editButton.count()) {
      await editButton.click()
      await popup.waitForTimeout(800)
      steps.push(await captureCurrentPage(popup, screenshotDir, 'teacher-question-edit'))
    }
  }

  await popup.close()
  return steps
}

function pickOptionValue(options = [], offset = 0) {
  if (!options.length) return ''
  const safeOffset = Math.abs(offset) % options.length
  const option = options[safeOffset]
  return option?.['answer_value'] || option.value || option.key || option.label
}

function buildSurveyAnswers(questions = [], offset = 0) {
  return questions.map((question, index) => ({
    question_id: question.question_id || question.id,
    answer: pickOptionValue(question.options || [], offset + index)
  }))
}

function buildKnowledgeAnswers(questions = [], offset = 0) {
  return questions.map((question, index) => {
    const options = question.options || []
    const type = question.type || question.question_type
    if (type === 'multiple_choice') {
      const selected = options.slice(0, Math.min(2, options.length)).map((option) => option.value || option?.['answer_value'] || option.key)
      return { question_id: question.question_id || question.id, answer: selected }
    }
    if (type === 'true_false') {
      return { question_id: question.question_id || question.id, answer: index % 2 === 0 ? 'true' : 'false' }
    }
    return {
      question_id: question.question_id || question.id,
      answer: pickOptionValue(options, offset + index)
    }
  })
}

async function ensureInitialAssessments(client, courseId, variantOffset = 0) {
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

async function ensureProfileAndPath(client, courseId) {
  await apiJson(client, 'POST', '/api/student/assessments/profile/generate', { course_id: courseId }).catch(() => null)
  await apiJson(client, 'POST', '/api/student/ai/refresh-profile', { course_id: courseId }, null, 180000).catch(() => null)
  const profile = await apiJson(client, 'GET', `/api/student/profile?course_id=${courseId}`)
  const pathData = await apiJson(client, 'GET', `/api/student/learning-path?course_id=${courseId}`)
  return { profile, pathData }
}

async function fetchExamList(client, courseId) {
  const listData = await apiJson(client, 'GET', `/api/student/exams?course_id=${courseId}`)
  return listData.exams || []
}

async function submitExamWithGeneratedAnswers(client, examId, courseId, offset = 0) {
  const detail = await apiJson(client, 'GET', `/api/student/exams/${examId}`)
  const answers = {}
    ; (detail.questions || []).forEach((question, index) => {
      const type = question.type || question.question_type
      const options = question.options || []
      if (type === 'multiple_choice') {
        answers[String(question.question_id || question.id)] = options.slice(0, Math.min(2, options.length)).map((option) => option.value || option?.['answer_value'] || option.key)
        return
      }
      if (type === 'true_false') {
        answers[String(question.question_id || question.id)] = index % 2 === 0 ? 'true' : 'false'
        return
      }
      answers[String(question.question_id || question.id)] = pickOptionValue(options, offset + index)
    })
  return apiJson(client, 'POST', `/api/student/exams/${examId}/submit`, {
    answers,
    course_id: courseId
  }, null, 180000)
}

async function waitForFeedbackReady(client, examId, attempts = 40, delayMs = 2000) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const feedback = await apiJson(client, 'GET', `/api/student/feedback/${examId}`).catch(() => null)
    if (feedback?.status === 'completed' || feedback?.status === 'failed') {
      return feedback
    }
    await new Promise((resolve) => setTimeout(resolve, delayMs))
  }
  return null
}

async function refreshLearningPath(client, courseId) {
  return apiJson(client, 'POST', '/api/student/ai/refresh-learning-path', {
    course_id: courseId
  }, null, 180000).catch(() => null)
}

async function ensureNeo4jKnowledgeMap(client, courseId) {
  const knowledgeMap = await apiJson(client, 'GET', `/api/student/knowledge-map?course_id=${courseId}`)
  const stats = knowledgeMap.stats || {}
  if (stats.data_source !== 'neo4j' || (stats.node_count || 0) <= 0 || (stats.edge_count || 0) <= 0) {
    throw new Error(`知识图谱未使用Neo4j或图数据为空: ${JSON.stringify(stats)}`)
  }
  return stats
}

async function prepareStableStudent(client, courseId, variantOffset = 0) {
  await ensureInitialAssessments(client, courseId, variantOffset)
  await ensureProfileAndPath(client, courseId)
  await ensureNeo4jKnowledgeMap(client, courseId)
  const exams = await fetchExamList(client, courseId)
  let submittedExam = exams.find((item) => item?.['submitted'])
  if (!submittedExam) {
    const targetExam = exams.find((item) => !item?.['submitted']) || exams[0]
    if (targetExam?.['exam_id']) {
      await submitExamWithGeneratedAnswers(client, targetExam['exam_id'], courseId, variantOffset)
      submittedExam = { exam_id: targetExam['exam_id'] }
      await waitForFeedbackReady(client, targetExam['exam_id'])
    }
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

async function prepareTriggerStudent(client, courseId, variantOffset = 0) {
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

async function prepareDemoScenario(apiBaseUrl, browser, args) {
  const students = [
    { username: 'student1', kind: 'stable', offset: 0 },
    { username: 'student2', kind: 'trigger', offset: 1 },
    { username: 'student3', kind: 'stable', offset: 2 }
  ]

  const reportDir = path.resolve(args.outputDir, 'reports')
  const screenshotDir = path.resolve(args.outputDir, 'screenshots', 'prepare-demo')
  await ensureDir(reportDir)
  await ensureDir(screenshotDir)

  const preparedStates = []
  for (const student of students) {
    const login = await loginApi(apiBaseUrl, student.username, DEFAULT_PASSWORDS[student.username])
    const currentContext = await resolveStudentContext(apiBaseUrl, login.token)
    const courseId = currentContext.currentCourse?.course_id
    if (!courseId) {
      throw new Error(`未找到课程，无法准备 ${student.username}`)
    }
    const authedClient = await createAuthedClient(apiBaseUrl, login.token)
    const state = student.kind === 'trigger'
      ? await prepareTriggerStudent(authedClient, courseId, student.offset)
      : await prepareStableStudent(authedClient, courseId, student.offset)
    await authedClient.dispose()

    const session = await createBrowserSession(browser, {
      token: login.token,
      refresh: login.refresh,
      currentCourse: currentContext.currentCourse
    })

    const routes = student.kind === 'trigger'
      ? ['/student/profile', '/student/learning-path', '/student/exams', `/student/exam/${state.triggerExamId}`]
      : ['/student/dashboard', '/student/profile', '/student/learning-path', state.reportExamId ? `/student/feedback/${state.reportExamId}` : '/student/exams']

    const routeResults = []
    for (const route of routes) {
      routeResults.push(await captureRoute(session.page, args.frontendUrl, route, screenshotDir, `${student.username}-${slugifyRoute(route)}`))
    }

    preparedStates.push({
      username: student.username,
      currentCourse: currentContext.currentCourse,
      ...state,
      routes: routeResults,
      console: session.errors,
      failedRequests: session.failedRequests
    })
    await session.context.close()
    await login.client.dispose()
  }

  await writeJson(path.join(reportDir, 'demo-account-states.json'), preparedStates)
  return preparedStates
}

async function simulateDemoScenario(apiBaseUrl, browser, args) {
  const reportDir = path.resolve(args.outputDir, 'reports')
  const screenshotDir = path.resolve(args.outputDir, 'screenshots', 'simulate-demo')
  await ensureDir(reportDir)
  await ensureDir(screenshotDir)

  const preparedStates = (await readJson(path.join(reportDir, 'demo-account-states.json'))) || []
  const statesByUser = Object.fromEntries(preparedStates.map((state) => [state.username, state]))

  const students = ['student1', 'student2']
  const simulationReport = []

  for (const username of students) {
    const login = await loginApi(apiBaseUrl, username, DEFAULT_PASSWORDS[username])
    const currentContext = await resolveStudentContext(apiBaseUrl, login.token)
    const state = statesByUser[username] || {}
    const session = await createBrowserSession(browser, {
      token: login.token,
      refresh: login.refresh,
      currentCourse: currentContext.currentCourse
    })
    const authedClient = await createAuthedClient(apiBaseUrl, login.token)
    const steps = []

    if (username === 'student1') {
      for (const route of ['/student/dashboard', '/student/profile', '/student/learning-path', state.reportExamId ? `/student/feedback/${state.reportExamId}` : '/student/exams']) {
        steps.push(await captureRoute(session.page, args.frontendUrl, route, screenshotDir, `${username}-${slugifyRoute(route)}`))
      }
    } else {
      const courseId = currentContext.currentCourse?.course_id
      const triggerExamId = state.triggerExamId
      steps.push(await captureRoute(session.page, args.frontendUrl, '/student/profile', screenshotDir, `${username}-profile-before`))
      steps.push(await captureRoute(session.page, args.frontendUrl, '/student/learning-path', screenshotDir, `${username}-path-before`))
      if (triggerExamId) {
        steps.push(await captureRoute(session.page, args.frontendUrl, `/student/exam/${triggerExamId}`, screenshotDir, `${username}-exam`))
        const submitPayload = await submitExamWithGeneratedAnswers(authedClient, triggerExamId, courseId, 3)
        steps.push({
          route: `/api/student/exams/${triggerExamId}/submit`,
          screenshot: null,
          ok: true,
          result: submitPayload?.['feedback_report'] || null
        })
        steps.push(await captureRoute(session.page, args.frontendUrl, `/student/feedback/${triggerExamId}`, screenshotDir, `${username}-feedback-pending`))
        await waitForFeedbackReady(authedClient, triggerExamId)
        steps.push(await captureRoute(session.page, args.frontendUrl, `/student/feedback/${triggerExamId}`, screenshotDir, `${username}-feedback-completed`))
        await refreshLearningPath(authedClient, courseId)
        steps.push(await captureRoute(session.page, args.frontendUrl, '/student/learning-path', screenshotDir, `${username}-path-after`))
      }
    }

    simulationReport.push({
      username,
      steps,
      console: session.errors,
      failedRequests: session.failedRequests
    })

    await authedClient.dispose()
    await session.context.close()
    await login.client.dispose()
  }

  await writeJson(path.join(reportDir, 'simulate-demo.json'), simulationReport)
  return simulationReport
}

async function prepareDefenseDemoScenario(apiBaseUrl, browser, args) {
  const reportDir = path.resolve(args.outputDir, 'reports')
  const screenshotDir = path.resolve(args.outputDir, 'screenshots', 'prepare-defense-demo')
  await ensureDir(reportDir)
  await ensureDir(screenshotDir)

  const archivePath = await ensureDefenseArchiveExists(args)
  const accounts = [
    { username: 'teacher', role: 'teacher', routes: ['/teacher/courses', '/teacher/courses/create?entry=demo-import'] },
    { username: 'student1', role: 'warmup', routes: ['/student/assessment'] },
    { username: 'student', role: 'student', routes: ['/student/assessment', '/student/learning-path', '/student/profile'] }
  ]

  const prepared = []
  for (const account of accounts) {
    const login = await loginApi(apiBaseUrl, account.username, DEFAULT_PASSWORDS[account.username])
    const currentContext = account.role === 'teacher'
      ? { currentCourse: null }
      : await resolveDefenseCourseContext(apiBaseUrl, login.token)
    const session = await createBrowserSession(browser, {
      token: login.token,
      refresh: login.refresh,
      currentCourse: currentContext.currentCourse
    })

    const routeResults = []
    for (const route of account.routes) {
      routeResults.push(await captureRoute(session.page, args.frontendUrl, route, screenshotDir, `${account.username}-${slugifyRoute(route)}`))
    }

    prepared.push({
      username: account.username,
      role: account.role,
      archivePath,
      currentCourse: currentContext.currentCourse,
      routes: routeResults,
      console: session.errors,
      failedRequests: session.failedRequests
    })

    await session.context.close()
    await login.client.dispose()
  }

  await writeJson(path.join(reportDir, 'defense-demo-state.json'), prepared)
  return prepared
}

async function simulateDefenseDemoScenario(apiBaseUrl, browser, args) {
  const reportDir = path.resolve(args.outputDir, 'reports')
  const screenshotDir = path.resolve(args.outputDir, 'screenshots', 'simulate-defense-demo')
  await ensureDir(reportDir)
  await ensureDir(screenshotDir)

  const simulationReport = []

  const teacherLogin = await loginApi(apiBaseUrl, 'teacher', DEFAULT_PASSWORDS.teacher)
  const teacherSession = await createBrowserSession(browser, {
    token: teacherLogin.token,
    refresh: teacherLogin.refresh,
    currentCourse: null
  })
  const importedCourseName = `答辩导入演示课程-${Date.now()}`
  const teacherSteps = await openTeacherImportCourseFlow(teacherSession, args, importedCourseName, screenshotDir)
  simulationReport.push({
    username: 'teacher',
    steps: teacherSteps,
    console: teacherSession.errors,
    failedRequests: teacherSession.failedRequests
  })
  await teacherSession.context.close()
  await teacherLogin.client.dispose()

  const warmupLogin = await loginApi(apiBaseUrl, 'student1', DEFAULT_PASSWORDS.student1)
  const warmupContext = await resolveDefenseCourseContext(apiBaseUrl, warmupLogin.token)
  const warmupSession = await createBrowserSession(browser, {
    token: warmupLogin.token,
    refresh: warmupLogin.refresh,
    currentCourse: warmupContext.currentCourse
  })
  const warmupSteps = [
    await captureRoute(warmupSession.page, args.frontendUrl, '/student/assessment', screenshotDir, 'student1-assessment')
  ]
  simulationReport.push({
    username: 'student1',
    steps: warmupSteps,
    console: warmupSession.errors,
    failedRequests: warmupSession.failedRequests
  })
  await warmupSession.context.close()
  await warmupLogin.client.dispose()

  const studentLogin = await loginApi(apiBaseUrl, 'student', DEFAULT_PASSWORDS.student)
  const studentContext = await resolveDefenseCourseContext(apiBaseUrl, studentLogin.token)
  const studentSession = await createBrowserSession(browser, {
    token: studentLogin.token,
    refresh: studentLogin.refresh,
    currentCourse: studentContext.currentCourse
  })
  const authedClient = await createAuthedClient(apiBaseUrl, studentLogin.token)
  const courseId = studentContext.currentCourse?.course_id
  const studentSteps = []

  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/assessment', screenshotDir, 'student-assessment'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/assessment/report?course_id=${courseId}`, screenshotDir, 'student-assessment-report'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/profile', screenshotDir, 'student-profile'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/learning-path', screenshotDir, 'student-path-before'))

  let pathPayload = await apiJson(authedClient, 'GET', `/api/student/learning-path?course_id=${courseId}`)
  const visibleNodes = pathPayload.nodes || []
  const studyNodes = visibleNodes.filter((node) => node?.['node_type'] !== 'test').slice(0, 3)

  for (const [index, node] of studyNodes.entries()) {
    studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/task/${node['node_id']}`, screenshotDir, `student-study-node-${index + 1}`))
    await apiJson(authedClient, 'POST', `/api/student/path-nodes/${node['node_id']}/complete`, { course_id: courseId })
  }

  pathPayload = await apiJson(authedClient, 'GET', `/api/student/learning-path?course_id=${courseId}`)
  const stageTestNode = (pathPayload.nodes || []).find((node) => node?.['node_type'] === 'test')
  if (stageTestNode?.['node_id']) {
    studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/task/${stageTestNode['node_id']}?nodeType=test`, screenshotDir, 'student-stage-test'))
    const stageAnswers = await buildDefenseStageTestAnswers(authedClient, stageTestNode['node_id'])
    await apiJson(authedClient, 'POST', `/api/student/path-nodes/${stageTestNode['node_id']}/stage-test/submit`, { answers: stageAnswers })
    studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/task/${stageTestNode['node_id']}?nodeType=test&viewReport=true`, screenshotDir, 'student-stage-report'))
  }

  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/learning-path?refreshing=1', screenshotDir, 'student-path-refreshing'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/learning-path', screenshotDir, 'student-path-after'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/ai-assistant', screenshotDir, 'student-ai-assistant'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/exams', screenshotDir, 'student-exams'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/knowledge-map', screenshotDir, 'student-knowledge-map'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/resources', screenshotDir, 'student-resources'))

  simulationReport.push({
    username: 'student',
    steps: studentSteps,
    console: studentSession.errors,
    failedRequests: studentSession.failedRequests
  })

  await authedClient.dispose()
  await studentSession.context.close()
  await studentLogin.client.dispose()

  await writeJson(path.join(reportDir, 'simulate-defense-demo.json'), simulationReport)
  return simulationReport
}

async function auditRole(browser, config) {
  const roleDir = path.resolve(config.outputDir, 'screenshots', config.role)
  const reportDir = path.resolve(config.outputDir, 'reports')
  await ensureDir(roleDir)
  await ensureDir(reportDir)

  const session = await createBrowserSession(browser, config)
  const routeResults = []

  for (const route of config.routes) {
    try {
      routeResults.push(await captureRoute(session.page, config.frontendUrl, route, roleDir))
    } catch (error) {
      routeResults.push({ route, url: `${config.frontendUrl}${route}`, ok: false, error: error.message })
    }
  }

  await writeJson(
    path.join(reportDir, `${config.role}-audit.json`),
    {
      role: config.role,
      routes: routeResults,
      console: session.errors,
      failedRequests: session.failedRequests
    }
  )

  await session.context.close()
}

async function runAuditScenario(browser, args) {
  const studentLogin = await loginApi(args.apiBaseUrl, 'student1', DEFAULT_PASSWORDS.student1)
  const teacherLogin = await loginApi(args.apiBaseUrl, 'teacher1', DEFAULT_PASSWORDS.teacher1)
  const adminLogin = await loginApi(args.apiBaseUrl, 'admin', DEFAULT_PASSWORDS.admin)
  const studentContext = await resolveStudentContext(args.apiBaseUrl, studentLogin.token)

  const configs = [
    {
      role: 'student',
      token: studentLogin.token,
      refresh: studentLogin.refresh,
      currentCourse: studentContext.currentCourse,
      routes: buildRoutes('student', studentContext),
      frontendUrl: args.frontendUrl,
      outputDir: args.outputDir
    },
    {
      role: 'teacher',
      token: teacherLogin.token,
      refresh: teacherLogin.refresh,
      currentCourse: null,
      routes: buildRoutes('teacher', {}),
      frontendUrl: args.frontendUrl,
      outputDir: args.outputDir
    },
    {
      role: 'admin',
      token: adminLogin.token,
      refresh: adminLogin.refresh,
      currentCourse: null,
      routes: buildRoutes('admin', {}),
      frontendUrl: args.frontendUrl,
      outputDir: args.outputDir
    }
  ]

  for (const config of configs) {
    await auditRole(browser, config)
  }

  await studentLogin.client.dispose()
  await teacherLogin.client.dispose()
  await adminLogin.client.dispose()
}

async function main() {
  const args = parseArgs(process.argv)
  await ensureBackendReady(args.apiBaseUrl)
  const browser = await chromium.launch({ headless: !args.headed })

  try {
    if (args.scenario === 'prepare-demo') {
      await prepareDemoScenario(args.apiBaseUrl, browser, args)
    } else if (args.scenario === 'prepare-defense-demo') {
      await prepareDefenseDemoScenario(args.apiBaseUrl, browser, args)
    } else if (args.scenario === 'simulate-demo') {
      await simulateDemoScenario(args.apiBaseUrl, browser, args)
    } else if (args.scenario === 'simulate-defense-demo') {
      await simulateDefenseDemoScenario(args.apiBaseUrl, browser, args)
    } else {
      await runAuditScenario(browser, args)
    }
  } finally {
    await browser.close()
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
