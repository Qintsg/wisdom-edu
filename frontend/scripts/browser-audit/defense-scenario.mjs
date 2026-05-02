import path from 'node:path'

import { apiJson, createAuthedClient, loginApi } from './api.mjs'
import { buildDefenseStageTestAnswers } from './answers.mjs'
import { DEFAULT_PASSWORDS } from './constants.mjs'
import { resolveDefenseCourseContext } from './context.mjs'
import { ensureDefenseArchiveExists, ensureDir, writeJson } from './files.mjs'
import {
  captureCurrentPage,
  captureRoute,
  createBrowserSession,
  slugifyRoute
} from './session.mjs'

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
    await captureQuestionWorkspace(popup, args, courseId, screenshotDir, steps)
  }

  await popup.close()
  return steps
}

async function captureQuestionWorkspace(popup, args, courseId, screenshotDir, steps) {
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

export async function prepareDefenseDemoScenario(apiBaseUrl, browser, args) {
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
    prepared.push(await prepareDefenseAccount(apiBaseUrl, browser, args, account, archivePath, screenshotDir))
  }

  await writeJson(path.join(reportDir, 'defense-demo-state.json'), prepared)
  return prepared
}

async function prepareDefenseAccount(apiBaseUrl, browser, args, account, archivePath, screenshotDir) {
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
  const result = {
    username: account.username,
    role: account.role,
    archivePath,
    currentCourse: currentContext.currentCourse,
    routes: routeResults,
    console: session.errors,
    failedRequests: session.failedRequests
  }
  await session.context.close()
  await login.client.dispose()
  return result
}

export async function simulateDefenseDemoScenario(apiBaseUrl, browser, args) {
  const reportDir = path.resolve(args.outputDir, 'reports')
  const screenshotDir = path.resolve(args.outputDir, 'screenshots', 'simulate-defense-demo')
  await ensureDir(reportDir)
  await ensureDir(screenshotDir)

  const simulationReport = []
  simulationReport.push(await simulateTeacherDefenseFlow(apiBaseUrl, browser, args, screenshotDir))
  simulationReport.push(await simulateWarmupDefenseFlow(apiBaseUrl, browser, args, screenshotDir))
  simulationReport.push(await simulateStudentDefenseFlow(apiBaseUrl, browser, args, screenshotDir))

  await writeJson(path.join(reportDir, 'simulate-defense-demo.json'), simulationReport)
  return simulationReport
}

async function simulateTeacherDefenseFlow(apiBaseUrl, browser, args, screenshotDir) {
  const teacherLogin = await loginApi(apiBaseUrl, 'teacher', DEFAULT_PASSWORDS.teacher)
  const teacherSession = await createBrowserSession(browser, {
    token: teacherLogin.token,
    refresh: teacherLogin.refresh,
    currentCourse: null
  })
  const importedCourseName = `答辩导入演示课程-${Date.now()}`
  const teacherSteps = await openTeacherImportCourseFlow(teacherSession, args, importedCourseName, screenshotDir)
  const result = {
    username: 'teacher',
    steps: teacherSteps,
    console: teacherSession.errors,
    failedRequests: teacherSession.failedRequests
  }
  await teacherSession.context.close()
  await teacherLogin.client.dispose()
  return result
}

async function simulateWarmupDefenseFlow(apiBaseUrl, browser, args, screenshotDir) {
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
  const result = {
    username: 'student1',
    steps: warmupSteps,
    console: warmupSession.errors,
    failedRequests: warmupSession.failedRequests
  }
  await warmupSession.context.close()
  await warmupLogin.client.dispose()
  return result
}

async function simulateStudentDefenseFlow(apiBaseUrl, browser, args, screenshotDir) {
  const studentLogin = await loginApi(apiBaseUrl, 'student', DEFAULT_PASSWORDS.student)
  const studentContext = await resolveDefenseCourseContext(apiBaseUrl, studentLogin.token)
  const studentSession = await createBrowserSession(browser, {
    token: studentLogin.token,
    refresh: studentLogin.refresh,
    currentCourse: studentContext.currentCourse
  })
  const authedClient = await createAuthedClient(apiBaseUrl, studentLogin.token)
  const studentSteps = await captureStudentDefenseSteps(authedClient, studentSession, args, studentContext, screenshotDir)
  const result = {
    username: 'student',
    steps: studentSteps,
    console: studentSession.errors,
    failedRequests: studentSession.failedRequests
  }
  await authedClient.dispose()
  await studentSession.context.close()
  await studentLogin.client.dispose()
  return result
}

async function captureStudentDefenseSteps(authedClient, studentSession, args, studentContext, screenshotDir) {
  const courseId = studentContext.currentCourse?.course_id
  const studentSteps = []
  await captureStudentBasics(studentSession, args, courseId, screenshotDir, studentSteps)

  let pathPayload = await apiJson(authedClient, 'GET', `/api/student/learning-path?course_id=${courseId}`)
  const studyNodes = (pathPayload.nodes || []).filter((node) => node?.['node_type'] !== 'test').slice(0, 3)
  for (const [index, node] of studyNodes.entries()) {
    studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/task/${node['node_id']}`, screenshotDir, `student-study-node-${index + 1}`))
    await apiJson(authedClient, 'POST', `/api/student/path-nodes/${node['node_id']}/complete`, { course_id: courseId })
  }

  pathPayload = await apiJson(authedClient, 'GET', `/api/student/learning-path?course_id=${courseId}`)
  await captureStageTestIfAvailable(authedClient, studentSession, args, pathPayload, screenshotDir, studentSteps)
  await captureStudentFinalRoutes(studentSession, args, screenshotDir, studentSteps)
  return studentSteps
}

async function captureStudentBasics(studentSession, args, courseId, screenshotDir, studentSteps) {
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/assessment', screenshotDir, 'student-assessment'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/assessment/report?course_id=${courseId}`, screenshotDir, 'student-assessment-report'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/profile', screenshotDir, 'student-profile'))
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, '/student/learning-path', screenshotDir, 'student-path-before'))
}

async function captureStageTestIfAvailable(authedClient, studentSession, args, pathPayload, screenshotDir, studentSteps) {
  const stageTestNode = (pathPayload.nodes || []).find((node) => node?.['node_type'] === 'test')
  if (!stageTestNode?.['node_id']) {
    return
  }
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/task/${stageTestNode['node_id']}?nodeType=test`, screenshotDir, 'student-stage-test'))
  const stageAnswers = await buildDefenseStageTestAnswers(authedClient, stageTestNode['node_id'])
  await apiJson(authedClient, 'POST', `/api/student/path-nodes/${stageTestNode['node_id']}/stage-test/submit`, { answers: stageAnswers })
  studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, `/student/task/${stageTestNode['node_id']}?nodeType=test&viewReport=true`, screenshotDir, 'student-stage-report'))
}

async function captureStudentFinalRoutes(studentSession, args, screenshotDir, studentSteps) {
  const routes = [
    ['/student/learning-path?refreshing=1', 'student-path-refreshing'],
    ['/student/learning-path', 'student-path-after'],
    ['/student/ai-assistant', 'student-ai-assistant'],
    ['/student/exams', 'student-exams'],
    ['/student/knowledge-map', 'student-knowledge-map'],
    ['/student/resources', 'student-resources']
  ]
  for (const [route, label] of routes) {
    studentSteps.push(await captureRoute(studentSession.page, args.frontendUrl, route, screenshotDir, label))
  }
}
