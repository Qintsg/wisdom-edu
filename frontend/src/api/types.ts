import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'

export type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retryCount?: number
}

export type RefreshSubscriber = (token?: string | null, error?: Error | null) => void

export type ApiErrorDetail = string | number | boolean | null | ApiErrorDetail[] | { [key: string]: ApiErrorDetail }

export type ApiEnvelope<T = unknown> = {
  code?: number
  msg?: string
  data?: T
  detail?: string
  error?: {
    type?: string
    details?: ApiErrorDetail
  }
}

export type ApiClient = Omit<AxiosInstance, 'request' | 'get' | 'delete' | 'head' | 'options' | 'post' | 'put' | 'patch'> & {
  request<T = unknown, D = unknown>(config: AxiosRequestConfig<D>): Promise<T>
  get<T = unknown, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  delete<T = unknown, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  head<T = unknown, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  options<T = unknown, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  post<T = unknown, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<T>
  put<T = unknown, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<T>
  patch<T = unknown, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<T>
}
