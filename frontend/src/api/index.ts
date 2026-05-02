/**
 * API核心模块
 * 提供 Axios 实例和请求/响应拦截器，保持 `import request from '@/api'` 契约。
 */
import axios from 'axios'
import type { AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { API_BASE_URL } from './backend'
import {
  clearStoredAuthTokens,
  getAuthStorage,
  getStoredAccessToken,
  getStoredRefreshToken
} from './authTokens'
import {
  ApiClientError,
  createApiError,
  extractApiErrorMessage,
  extractPayloadMessage,
  isApiErrorHandled,
  normalizeError
} from './errors'
import type { ApiClient, ApiEnvelope, RefreshSubscriber, RetryableRequestConfig } from './types'

export { ApiClientError, extractApiErrorMessage, isApiErrorHandled }

const MAX_RETRY_COUNT = 2
const REFRESH_TOKEN_TIMEOUT = 10000
const MAX_REFRESH_RETRY = 2
const REFRESH_RETRY_DELAY = 1000

let isRefreshing = false
let refreshSubscribers: RefreshSubscriber[] = []
let tokenRefreshFailed = false
let isLoggingOut = false

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function notifyError(message: string): void {
  ElMessage.error(message || '请求失败')
}

function isAuthEntryRequest(config?: RetryableRequestConfig): boolean {
  const requestUrl = String(config?.url ?? '')
  return [
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/token/refresh',
    '/api/auth/password/reset',
    '/api/auth/password/reset/send'
  ].some(authEndpoint => requestUrl.includes(authEndpoint))
}

function onTokenRefreshed(token: string | null): void {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

function onTokenRefreshFailed(error: Error): void {
  refreshSubscribers.forEach(callback => callback(null, error))
  refreshSubscribers = []
}

function addRefreshSubscriber(callback: RefreshSubscriber): void {
  refreshSubscribers.push(callback)
}

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
}) as ApiClient

request.interceptors.request.use(
  (config: RetryableRequestConfig) => {
    const token = getStoredAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (config._retryCount === undefined) {
      config._retryCount = 0
    }

    return config
  },
  error => Promise.reject(error)
)

request.interceptors.response.use(
  response => {
    if (response.config.responseType === 'blob' || response.data instanceof Blob) {
      return response.data
    }

    const payload = response.data as ApiEnvelope
    const { code, msg, data } = payload
    if (code === 200 || code === 201 || code === 202) {
      return data !== undefined ? data : payload
    }

    const message = extractPayloadMessage(payload, msg || '请求失败')
    notifyError(message)
    return Promise.reject(createApiError(message, {
      status: response.status,
      code,
      payload,
      handled: true
    }))
  },
  async (error: AxiosError) => {
    const { response } = error
    const config = error.config as RetryableRequestConfig | undefined

    if ((config?._retryCount ?? 0) >= MAX_RETRY_COUNT) {
      const message = '请求失败次数过多，请稍后重试'
      notifyError(message)
      return Promise.reject(createApiError(message, {
        status: response?.status,
        payload: response?.data,
        handled: true
      }))
    }

    if (response) {
      const fallbackMessageMap: Record<number, string> = {
        401: '登录已过期，请重新登录',
        403: '没有权限访问',
        404: '请求的资源不存在',
        500: '服务器内部错误'
      }
      const backendMessage = extractPayloadMessage(
        response.data,
        fallbackMessageMap[response.status] || '请求失败'
      )
      switch (response.status) {
        case 401:
          return handleUnauthorizedResponse(config, response.data, backendMessage)
        case 403:
        case 404:
        case 500:
        default:
          notifyError(backendMessage)
      }
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      if ((config?._retryCount ?? 0) < MAX_RETRY_COUNT && config) {
        config._retryCount = (config._retryCount ?? 0) + 1
        return request.request(config)
      }
      notifyError('请求超时，请检查网络连接')
    } else {
      if ((config?._retryCount ?? 0) < MAX_RETRY_COUNT && config) {
        config._retryCount = (config._retryCount ?? 0) + 1
        return request.request(config)
      }
      notifyError('网络连接失败')
    }

    return Promise.reject(createApiError(
      extractApiErrorMessage(error),
      {
        status: response?.status,
        payload: response?.data,
        handled: true
      }
    ))
  }
)

async function handleUnauthorizedResponse(
  config: RetryableRequestConfig | undefined,
  payload: unknown,
  backendMessage: string
): Promise<unknown> {
  if (isLoggingOut) {
    return Promise.reject(createApiError('用户已登出', { status: 401, payload }))
  }
  if (isAuthEntryRequest(config)) {
    return Promise.reject(createApiError(backendMessage, { status: 401, payload }))
  }
  if (tokenRefreshFailed) {
    clearAuthTokens()
    await router.push('/login')
    return Promise.reject(createApiError(backendMessage || '认证失败', { status: 401, payload }))
  }
  if (!getStoredRefreshToken()) {
    clearAuthTokens()
    notifyError(backendMessage || '登录已过期，请重新登录')
    await router.push('/login')
    return Promise.reject(createApiError(backendMessage || '认证失败', {
      status: 401,
      payload,
      handled: true
    }))
  }

  if (!isRefreshing) {
    return refreshTokenAndReplayRequest(config, payload)
  }

  if (!config) {
    return Promise.reject(createApiError('请求配置缺失，无法重试', { status: 401, payload }))
  }
  return new Promise((resolve, reject) => {
    addRefreshSubscriber((token, err) => {
      if (err || !token) {
        reject(err || new Error('Token刷新失败'))
        return
      }
      config.headers.Authorization = `Bearer ${token}`
      config._retryCount = (config._retryCount ?? 0) + 1
      resolve(request.request(config))
    })
  })
}

async function refreshTokenAndReplayRequest(
  config: RetryableRequestConfig | undefined,
  payload: unknown
): Promise<unknown> {
  isRefreshing = true
  tokenRefreshFailed = false

  try {
    const refreshed = await tryRefreshToken()
    isRefreshing = false

    if (!refreshed) {
      tokenRefreshFailed = true
      const refreshFailedError = createApiError('Token刷新失败', { status: 401, payload })
      onTokenRefreshFailed(refreshFailedError)
      clearAuthTokens()
      notifyError('登录已过期，请重新登录')
      await router.push('/login')
      return Promise.reject(refreshFailedError)
    }

    const newToken = getStoredAccessToken()
    if (!newToken) {
      tokenRefreshFailed = true
      const missingTokenError = createApiError('Token刷新后缺少访问令牌', { status: 401, payload })
      onTokenRefreshFailed(missingTokenError)
      clearAuthTokens()
      await router.push('/login')
      return Promise.reject(missingTokenError)
    }

    onTokenRefreshed(newToken)
    if (!config) {
      return Promise.reject(createApiError('请求配置缺失，无法重试', { status: 401, payload }))
    }
    config.headers.Authorization = `Bearer ${newToken}`
    config._retryCount = (config._retryCount ?? 0) + 1
    return request.request(config)
  } catch (refreshError) {
    const normalizedError = normalizeError(refreshError)
    isRefreshing = false
    tokenRefreshFailed = true
    onTokenRefreshFailed(normalizedError)
    clearAuthTokens()
    notifyError('登录已过期，请重新登录')
    await router.push('/login')
    return Promise.reject(normalizedError)
  }
}

function clearAuthTokens(): void {
  clearStoredAuthTokens()
  isRefreshing = false
  refreshSubscribers = []
  tokenRefreshFailed = false
}

async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = getStoredRefreshToken()
  if (!refreshToken) return false

  for (let attempt = 0; attempt < MAX_REFRESH_RETRY; attempt++) {
    try {
      const response = await axios.post<ApiEnvelope<{ access?: string; token?: string; refresh?: string }>>(
        `${API_BASE_URL}/api/auth/token/refresh`,
        { refresh: refreshToken },
        { timeout: REFRESH_TOKEN_TIMEOUT }
      )

      if (response.data.code === 200) {
        const tokenPayload = response.data.data
        const newToken = tokenPayload?.access || tokenPayload?.token
        if (!newToken) return false
        const storage = getAuthStorage()
        storage.setItem('access_token', newToken)
        storage.setItem('token', newToken)
        if (tokenPayload?.refresh) {
          storage.setItem('refresh_token', tokenPayload.refresh)
        }
        return true
      }
      return false
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response) {
        return false
      }
      if (attempt < MAX_REFRESH_RETRY - 1) {
        await delay(REFRESH_RETRY_DELAY)
        continue
      }
      return false
    }
  }

  return false
}

export function resetTokenRefreshState(): void {
  tokenRefreshFailed = false
  isRefreshing = false
  refreshSubscribers = []
  isLoggingOut = false
}

export function setLoggingOut(value = true): void {
  isLoggingOut = value
}

export default request
