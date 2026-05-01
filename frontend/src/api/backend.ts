/**
 * 前端运行时后端地址配置。
 * 默认后端入口跟随当前站点同源。
 * 开发环境继续保留相对路径，交由 Vite 直接代理到本地 Django；
 * 生产/预览环境默认通过 Nginx 同源反代访问后端，如需覆盖再显式设置 `VITE_BACKEND_ORIGIN`。
 */

/** 可选后端 HTTP 入口；留空时生产环境使用当前站点同源。 */
const RAW_BACKEND_ORIGIN = (import.meta.env.VITE_BACKEND_ORIGIN ?? '').trim()

/**
 * 统一清洗后端入口，避免拼接时出现双斜杠。
 * @param {string} rawOrigin
 * @returns {string}
 */
function normalizeBackendOrigin(rawOrigin: string): string {
    return rawOrigin.trim().replace(/\/+$/, '')
}

/** 显式配置时生产构建使用的后端基址。 */
const FIXED_BACKEND_ORIGIN = normalizeBackendOrigin(RAW_BACKEND_ORIGIN)

/** 前端所有 HTTP 请求统一使用的后端基址。开发态和未覆盖的生产态都保留相对路径给代理处理。 */
export const API_BASE_URL = import.meta.env.DEV ? '' : FIXED_BACKEND_ORIGIN

/** 获取资源和 WebSocket 需要拼接绝对地址时的运行时后端入口。 */
function getRuntimeBackendOrigin(): string {
    if (FIXED_BACKEND_ORIGIN) {
        return FIXED_BACKEND_ORIGIN
    }
    if (typeof window === 'undefined') {
        return ''
    }
    return window.location.origin.replace(/\/+$/, '')
}

/**
 * 判断是否已经是可直接访问的绝对 URL。
 * @param {string} targetUrl
 * @returns {boolean}
 */
function isAbsoluteUrl(targetUrl: string): boolean {
    return /^(https?:|wss?:|data:|blob:|\/\/)/i.test(targetUrl)
}

/**
 * 将后端返回的相对路径补全为固定后端地址。
 * @param {string | null | undefined} rawPath
 * @returns {string}
 */
export function toBackendAbsoluteUrl(rawPath: string | null | undefined): string {
    const normalizedPath = typeof rawPath === 'string' ? rawPath.trim() : ''
    if (!normalizedPath) {
        return ''
    }
    if (isAbsoluteUrl(normalizedPath)) {
        return normalizedPath
    }
    const pathWithLeadingSlash = normalizedPath.startsWith('/') ? normalizedPath : `/${normalizedPath}`
    if (import.meta.env.DEV) {
        return pathWithLeadingSlash
    }
    return `${getRuntimeBackendOrigin()}${pathWithLeadingSlash}`
}

/**
 * 获取当前环境下用于建立 WebSocket 连接的基址。
 * 开发态继续复用浏览器当前站点，由 Vite 代理 `/ws`；生产态固定连到本机后端或显式配置地址。
 * @returns {string}
 */
function getCurrentWebSocketBaseUrl(): string {
    if (!import.meta.env.DEV) {
        return getRuntimeBackendOrigin()
            .replace(/^http:/, 'ws:')
            .replace(/^https:/, 'wss:')
    }
    if (typeof window === 'undefined') {
        return ''
    }
    return window.location.origin
        .replace(/^http:/, 'ws:')
        .replace(/^https:/, 'wss:')
        .replace(/\/+$/, '')
}

/**
 * 生成固定后端地址下的 WebSocket URL。
 * @param {string} rawPath
 * @param {Record<string, string | number | boolean | null | undefined>} [query]
 * @returns {string}
 */
export function buildBackendWebSocketUrl(
    rawPath: string,
    query?: Record<string, string | number | boolean | null | undefined>
): string {
    const normalizedPath = rawPath.trim()
    const pathWithLeadingSlash = normalizedPath.startsWith('/') ? normalizedPath : `/${normalizedPath}`
    const searchParams = new URLSearchParams()

    Object.entries(query || {}).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
            searchParams.set(key, String(value))
        }
    })

    const queryString = searchParams.toString()
    return `${getCurrentWebSocketBaseUrl()}${pathWithLeadingSlash}${queryString ? `?${queryString}` : ''}`
}
