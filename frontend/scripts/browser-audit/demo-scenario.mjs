import path from 'node:path'

import { apiJson, createAuthedClient, loginApi } from './api.mjs'
import { DEFAULT_PASSWORDS } from './constants.mjs'
import { resolveStudentContext } from './context.mjs'
import { readJson, writeJson, ensureDir } from './files.mjs'
import { createBrowserSession, captureRoute, slugifyRoute } from './session.mjs'
import {
  prepareStableStudent,
  prepareTriggerStudent,
  refreshLearningPath
} from './student-prep.mjs'
import {
  submitExamWithGeneratedAnswers,
  waitForFeedbackReady
} from './answers.mjs'

export async function prepareDemoScenario(apiBaseUrl, browser, args) {
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
    preparedStates.push(await prepareStudentDemoState(apiBaseUrl, browser, args, student, screenshotDir))
  }

  await writeJson(path.join(reportDir, 'demo-account-states.json'), preparedStates)
  return preparedStates
}

async function prepareStudentDemoState(apiBaseUrl, browser, args, student, screenshotDir) {
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
  const routes = buildPreparedStudentRoutes(student, state)
  const routeResults = []
  for (const route of routes) {
    routeResults.push(await captureRoute(session.page, args.frontendUrl, route, screenshotDir, `${student.username}-${slugifyRoute(route)}`))
  }

  const result = {
    username: student.username,
    currentCourse: currentContext.currentCourse,
    ...state,
    routes: routeResults,
    console: session.errors,
    failedRequests: session.failedRequests
  }
  await session.context.close()
  await login.client.dispose()
  return result
}

function buildPreparedStudentRoutes(student, state) {
  if (student.kind === 'trigger') {
    return ['/student/profile', '/student/learning-path', '/student/exams', `/student/exam/${state.triggerExamId}`]
  }
  return [
    '/student/dashboard',
    '/student/profile',
    '/student/learning-path',
    state.reportExamId ? `/student/feedback/${state.reportExamId}` : '/student/exams'
  ]
}

export async function simulateDemoScenario(apiBaseUrl, browser, args) {
  const reportDir = path.resolve(args.outputDir, 'reports')
  const screenshotDir = path.resolve(args.outputDir, 'screenshots', 'simulate-demo')
  await ensureDir(reportDir)
  await ensureDir(screenshotDir)

  const preparedStates = (await readJson(path.join(reportDir, 'demo-account-states.json'))) || []
  const statesByUser = Object.fromEntries(preparedStates.map((state) => [state.username, state]))
  const simulationReport = []
  for (const username of ['student1', 'student2']) {
    simulationReport.push(
      await simulateStudentDemoFlow(apiBaseUrl, browser, args, username, statesByUser[username] || {}, screenshotDir)
    )
  }

  await writeJson(path.join(reportDir, 'simulate-demo.json'), simulationReport)
  return simulationReport
}

async function simulateStudentDemoFlow(apiBaseUrl, browser, args, username, state, screenshotDir) {
  const login = await loginApi(apiBaseUrl, username, DEFAULT_PASSWORDS[username])
  const currentContext = await resolveStudentContext(apiBaseUrl, login.token)
  const session = await createBrowserSession(browser, {
    token: login.token,
    refresh: login.refresh,
    currentCourse: currentContext.currentCourse
  })
  const authedClient = await createAuthedClient(apiBaseUrl, login.token)
  const steps = username === 'student1'
    ? await captureStableStudentSimulation(session, args, username, state, screenshotDir)
    : await captureTriggerStudentSimulation(authedClient, session, args, username, state, currentContext, screenshotDir)

  const result = {
    username,
    steps,
    console: session.errors,
    failedRequests: session.failedRequests
  }
  await authedClient.dispose()
  await session.context.close()
  await login.client.dispose()
  return result
}

async function captureStableStudentSimulation(session, args, username, state, screenshotDir) {
  const routes = [
    '/student/dashboard',
    '/student/profile',
    '/student/learning-path',
    state.reportExamId ? `/student/feedback/${state.reportExamId}` : '/student/exams'
  ]
  const steps = []
  for (const route of routes) {
    steps.push(await captureRoute(session.page, args.frontendUrl, route, screenshotDir, `${username}-${slugifyRoute(route)}`))
  }
  return steps
}

async function captureTriggerStudentSimulation(authedClient, session, args, username, state, currentContext, screenshotDir) {
  const steps = []
  const courseId = currentContext.currentCourse?.course_id
  const triggerExamId = state.triggerExamId
  steps.push(await captureRoute(session.page, args.frontendUrl, '/student/profile', screenshotDir, `${username}-profile-before`))
  steps.push(await captureRoute(session.page, args.frontendUrl, '/student/learning-path', screenshotDir, `${username}-path-before`))
  if (!triggerExamId) {
    return steps
  }
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
  return steps
}
