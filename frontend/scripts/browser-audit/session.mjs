import path from 'node:path'

export function slugifyRoute(route) {
  return route.replace(/^[\\/]+/, '').replace(/[?=&/:]+/g, '-')
}

export async function createBrowserSession(browser, config) {
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

export async function captureRoute(page, frontendUrl, route, screenshotDir, label = null) {
  const targetUrl = `${frontendUrl}${route}`
  await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 60000 })
  const fileName = `${label || slugifyRoute(route)}.png`
  await page.screenshot({
    path: path.join(screenshotDir, fileName),
    fullPage: true
  })
  return { route, url: page.url(), screenshot: fileName, ok: true }
}

export async function captureCurrentPage(page, screenshotDir, label) {
  const fileName = `${label}.png`
  await page.screenshot({
    path: path.join(screenshotDir, fileName),
    fullPage: true
  })
  return { route: page.url(), url: page.url(), screenshot: fileName, ok: true }
}
