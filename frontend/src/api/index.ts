/**
 * API核心模块
 * 提供Axios实例和请求/响应拦截器
 * 
 * 功能特性：
 * - 自动添加Authorization头
 * - Token过期自动刷新
 * - 统一错误处理和提示
 * - 请求重试机制（带次数限制）
 * 
 * 使用方式：
 * import request from '@/api'
 * 或
 * import { login, register } from '@/api/auth'
 */
import axios from 'axios'
import type { AxiosError, AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { API_BASE_URL } from './backend'

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retryCount?: number
}

type RefreshSubscriber = (token?: string | null, error?: Error | null) => void

type ApiClient = Omit<AxiosInstance, 'request' | 'get' | 'delete' | 'head' | 'options' | 'post' | 'put' | 'patch'> & {
  request<T = any, D = any>(config: AxiosRequestConfig<D>): Promise<T>
  get<T = any, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  delete<T = any, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  head<T = any, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  options<T = any, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  post<T = any, D = any>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<T>
  put<T = any, D = any>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<T>
  patch<T = any, D = any>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<T>
}

// ==================== 配置常量 ====================

/** 最大请求重试次数（包括Token刷新后的重放） */
const MAX_RETRY_COUNT = 2
/** Token刷新超时时间（毫秒） */
const REFRESH_TOKEN_TIMEOUT = 10000
/** Token刷新失败时的最大重试次数 */
const MAX_REFRESH_RETRY = 2
/** Token刷新重试间隔（毫秒） */
const REFRESH_RETRY_DELAY = 1000

// ==================== 状态变量 ====================

// 标记是否正在刷新Token，防止并发刷新
let isRefreshing = false
// 等待Token刷新的请求队列
let refreshSubscribers: RefreshSubscriber[] = []
// Token刷新失败标记，防止死循环
let tokenRefreshFailed = false
// 主动登出标记，防止退出时提示"登录已过期"
let isLoggingOut = false

/**
 * 获取当前可用的认证存储对象
 * 优先取localStorage，其次sessionStorage
 */
function getAuthStorage(): Storage {
  if (localStorage.getItem('access_token') || localStorage.getItem('token')) {
    return localStorage
  }
  if (sessionStorage.getItem('access_token') || sessionStorage.getItem('token')) {
    return sessionStorage
  }
  return localStorage
}

/**
 * 获取访问令牌（兼容local/session）
 */
function getStoredAccessToken(): string | null {
  return (
    localStorage.getItem('access_token') ||
    localStorage.getItem('token') ||
    sessionStorage.getItem('access_token') ||
    sessionStorage.getItem('token')
  )
}

/**
 * 获取刷新令牌（兼容local/session）
 */
function getStoredRefreshToken(): string | null {
  return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
}

/**
 * 简单的延时函数
 * @param {number} ms - 毫秒数
 * @returns {Promise<void>}
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 将未知异常统一转换为 Error 对象
 * @param {unknown} error - 原始异常
 * @returns {Error} 规范化后的异常对象
 */
function normalizeError(error: unknown): Error {
  if (error instanceof Error) {
    return error
  }
  if (axios.isAxiosError(error)) {
    return new Error(error.message)
  }
  return new Error('未知错误')
}

/**
 * 通知所有等待的请求，Token已刷新
 * @param {string} token - 新的访问令牌
 */
function onTokenRefreshed(token: string | null): void {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

/**
 * 通知所有等待的请求，Token刷新失败
 * @param {Error} error - 错误对象
 */
function onTokenRefreshFailed(error: Error): void {
  refreshSubscribers.forEach(callback => callback(null, error))
  refreshSubscribers = []
}

/**
 * 添加等待Token刷新的请求到队列
 * @param {Function} callback - 刷新完成后的回调 (token, error) => {}
 */
function addRefreshSubscriber(callback: RefreshSubscriber): void {
  refreshSubscribers.push(callback)
}

// 创建Axios实例
const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
}) as ApiClient

// 请求拦截器 - 自动添加Token和重试计数
request.interceptors.request.use(
  (config: RetryableRequestConfig) => {
    // 兼容localStorage/sessionStorage以及旧key
    const token = getStoredAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (config._retryCount === undefined) {
      config._retryCount = 0
    }

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一处理响应和错误
request.interceptors.response.use(
  response => {
    const { code, msg, data } = response.data

    // 业务成功（200/201/202都视为成功）
    if (code === 200 || code === 201 || code === 202) {
      // 直接返回data字段，简化调用方代码
      return data !== undefined ? data : response.data
    }

    // 业务错误
    ElMessage.error(msg || '请求失败')
    return Promise.reject(new Error(msg))
  },
  async (error: AxiosError) => {
    const { response } = error
    const config = error.config as RetryableRequestConfig | undefined

    // 检查是否超过最大重试次数（使用 > 确保能重试 MAX_RETRY_COUNT 次）
    if ((config?._retryCount ?? 0) >= MAX_RETRY_COUNT) {
      ElMessage.error('请求失败次数过多，请稍后重试')
      return Promise.reject(new Error('超过最大重试次数'))
    }

    if (response) {
      switch (response.status) {
        case 401:
          // 用户主动登出时，不弹过期提示
          if (isLoggingOut) {
            return Promise.reject(new Error('用户已登出'))
          }
          // 如果Token刷新已经失败过，直接跳转登录，避免死循环
          if (tokenRefreshFailed) {
            clearAuthTokens()
            await router.push('/login')
            return Promise.reject(new Error('认证失败'))
          }

          // Token过期，尝试刷新
          if (!isRefreshing) {
            isRefreshing = true
            tokenRefreshFailed = false

            try {
              const refreshed = await tryRefreshToken()
              isRefreshing = false

              if (refreshed) {
                // 刷新成功，通知等待的请求并重试原请求
                const newToken = getStoredAccessToken()
                if (!newToken) {
                  tokenRefreshFailed = true
                  onTokenRefreshFailed(new Error('Token刷新后缺少访问令牌'))
                  clearAuthTokens()
                  await router.push('/login')
                  return Promise.reject(new Error('Token刷新后缺少访问令牌'))
                }

                onTokenRefreshed(newToken)
                if (!config) {
                  return Promise.reject(new Error('请求配置缺失，无法重试'))
                }
                config.headers.Authorization = `Bearer ${newToken}`
                config._retryCount = (config._retryCount ?? 0) + 1
                return request.request(config)
              } else {
                // 刷新失败，标记并通知所有等待的请求
                tokenRefreshFailed = true
                onTokenRefreshFailed(new Error('Token刷新失败'))
                clearAuthTokens()
                ElMessage.error('登录已过期，请重新登录')
                await router.push('/login')
                return Promise.reject(new Error('Token刷新失败'))
              }
            } catch (refreshError) {
              const normalizedError = normalizeError(refreshError)
              isRefreshing = false
              tokenRefreshFailed = true
              onTokenRefreshFailed(normalizedError)
              clearAuthTokens()
              ElMessage.error('登录已过期，请重新登录')
              await router.push('/login')
              return Promise.reject(normalizedError)
            }
          } else {
            // 正在刷新，将请求加入队列
            if (!config) {
              return Promise.reject(new Error('请求配置缺失，无法重试'))
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
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error((response.data as any)?.msg || '请求失败')
      }
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // 请求超时：在限制次数内自动重试
      if ((config?._retryCount ?? 0) < MAX_RETRY_COUNT && config) {
        config._retryCount = (config._retryCount ?? 0) + 1
        return request.request(config)
      }
      ElMessage.error('请求超时，请检查网络连接')
    } else {
      // 网络错误（无响应）：在限制次数内自动重试
      if ((config?._retryCount ?? 0) < MAX_RETRY_COUNT && config) {
        config._retryCount = (config._retryCount ?? 0) + 1
        return request.request(config)
      }
      ElMessage.error('网络连接失败')
    }

    return Promise.reject(error)
  }
)

/**
 * 清除认证Token
 * 清除所有本地存储的认证信息
 */
function clearAuthTokens() {
  const keys = ['access_token', 'refresh_token', 'token', 'userInfo', 'current_course']
  keys.forEach(key => {
    localStorage.removeItem(key)
    sessionStorage.removeItem(key)
  })

  // 重置状态
  isRefreshing = false
  refreshSubscribers = []
  tokenRefreshFailed = false
}

/**
 * 刷新Token函数
 * 当access_token过期时，使用refresh_token换取新的access_token
 * @returns {Promise<boolean>} 是否刷新成功
 */
async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = getStoredRefreshToken()
  if (!refreshToken) return false

  for (let attempt = 0; attempt < MAX_REFRESH_RETRY; attempt++) {
    try {
      // 使用独立的axios实例进行刷新，避免被拦截器处理
      const response = await axios.post(
        `${API_BASE_URL}/api/auth/token/refresh`,
        { refresh: refreshToken },
        { timeout: REFRESH_TOKEN_TIMEOUT }
      )

      if (response.data.code === 200) {
        const data = response.data.data
        const newToken = data.access || data.token
        const storage = getAuthStorage()
        storage.setItem('access_token', newToken)
        storage.setItem('token', newToken) // 兼容旧key
        if (data.refresh) {
          storage.setItem('refresh_token', data.refresh)
        }
        return true
      }
      // 业务上刷新失败（如refresh过期），不再重试
      return false
    } catch (err: unknown) {
      // 如果是服务器返回的明确错误（有response），不重试
      if (axios.isAxiosError(err) && err.response) {
        return false
      }
      // 网络错误/超时则在限制次数内重试
      if (attempt < MAX_REFRESH_RETRY - 1) {
        await delay(REFRESH_RETRY_DELAY)
        continue
      }
      return false
    }
  }

  return false
}

/**
 * 重置Token刷新失败标记
 * 在用户成功登录后调用
 */
export function resetTokenRefreshState(): void {
  tokenRefreshFailed = false
  isRefreshing = false
  refreshSubscribers = []
  isLoggingOut = false
}

/**
 * 设置主动登出标记
 * 在用户主动登出时调用，防止触发"登录已过期"提示
 */
export function setLoggingOut(value = true): void {
  isLoggingOut = value
}

export default request
