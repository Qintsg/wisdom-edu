import axios from 'axios'
import type { ApiEnvelope } from './types'

export class ApiClientError extends Error {
  status?: number
  code?: number
  payload?: unknown
  handledByInterceptor: boolean

  constructor(message: string, options: { status?: number; code?: number; payload?: unknown; handled?: boolean } = {}) {
    super(message)
    this.name = 'ApiClientError'
    this.status = options.status
    this.code = options.code
    this.payload = options.payload
    this.handledByInterceptor = options.handled ?? false
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function collectDetailMessages(detail: unknown, prefix = ''): string[] {
  if (Array.isArray(detail)) {
    return detail.flatMap(item => collectDetailMessages(item, prefix))
  }
  if (isRecord(detail)) {
    return Object.entries(detail).flatMap(([key, value]) => {
      const nextPrefix = key === 'detail' ? prefix : (prefix ? `${prefix}.${key}` : key)
      return collectDetailMessages(value, nextPrefix)
    })
  }
  if (detail === null || detail === undefined || detail === '') {
    return []
  }

  const message = String(detail).trim()
  if (!message) {
    return []
  }
  return [prefix ? `${prefix}: ${message}` : message]
}

export function extractPayloadMessage(payload: unknown, fallback: string): string {
  if (isRecord(payload)) {
    const envelope = payload as ApiEnvelope
    if (typeof envelope.msg === 'string' && envelope.msg.trim()) {
      return envelope.msg.trim()
    }
    if (typeof envelope.detail === 'string' && envelope.detail.trim()) {
      return envelope.detail.trim()
    }
    const detailMessages = collectDetailMessages(envelope.data ?? envelope.error?.details)
    if (detailMessages.length) {
      return detailMessages[0]
    }
  }
  return fallback
}

export function createApiError(
  message: string,
  options: { status?: number; code?: number; payload?: unknown; handled?: boolean } = {}
): ApiClientError {
  return new ApiClientError(message || '请求失败', options)
}

export function extractApiErrorMessage(error: unknown, fallback = '请求失败'): string {
  if (error instanceof ApiClientError && error.message) {
    return error.message
  }
  if (axios.isAxiosError(error)) {
    return extractPayloadMessage(error.response?.data, error.message || fallback)
  }
  if (error instanceof Error && error.message) {
    return error.message
  }
  return fallback
}

export function isApiErrorHandled(error: unknown): boolean {
  return error instanceof ApiClientError && error.handledByInterceptor
}

export function normalizeError(error: unknown): Error {
  if (error instanceof Error) {
    return error
  }
  if (axios.isAxiosError(error)) {
    return new Error(error.message)
  }
  return new Error('未知错误')
}
