import { request as playwrightRequest } from 'playwright'

export async function loginApi(apiBaseUrl, username, password) {
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

export async function ensureBackendReady(apiBaseUrl) {
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

export async function createAuthedClient(apiBaseUrl, token) {
  return playwrightRequest.newContext({
    baseURL: apiBaseUrl,
    extraHTTPHeaders: { Authorization: `Bearer ${token}` }
  })
}

export async function apiJson(client, method, url, data = undefined, timeout = 180000) {
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
