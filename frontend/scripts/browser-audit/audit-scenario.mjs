import path from 'node:path'

import { loginApi } from './api.mjs'
import { DEFAULT_PASSWORDS } from './constants.mjs'
import { buildRoutes, resolveStudentContext } from './context.mjs'
import { ensureDir, writeJson } from './files.mjs'
import { captureRoute, createBrowserSession } from './session.mjs'

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

export async function runAuditScenario(browser, args) {
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
