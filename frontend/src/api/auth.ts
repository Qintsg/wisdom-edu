/**
 * 用户认证相关API
 * 包含登录、注册、Token刷新、用户信息管理等功能
 * 
 * 认证流程：
 * 1. 用户登录/注册获取access_token和refresh_token
 * 2. 后续请求自动携带access_token
 * 3. access_token过期时使用refresh_token刷新
 * 4. refresh_token过期需重新登录
 */
import request from './index'

/**
 * 用户登录
 * @param {Object} data - 登录凭证
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise<{access: string, refresh: string, user: Object}>} 登录结果
 */
export function login(data) {
  return request.post('/api/auth/login', data)
}

/**
 * 用户注册
 * @param {Object} data - 注册信息
 * @param {string} data.username - 用户名（3-50字符）
 * @param {string} data.password - 密码（8+字符，建议包含大写和数字）
 * @param {string} data.role - 角色（student/teacher/admin）
 * @param {string} [data.email] - 邮箱
 * @param {string} [data.phone] - 手机号（中国格式）
 * @param {string} [data.activation_code] - 激活码（教师/管理员必填）
 * @returns {Promise<Object>} 注册结果
 */
export function register(data) {
  return request.post('/api/auth/register', data)
}

/**
 * 获取当前用户信息
 * 需要登录后调用，根据Token获取对应用户信息
 * @returns {Promise<Object>} 用户信息，包含user_id、username、role、email等
 */
export function getUserInfo() {
  return request.get('/api/auth/userinfo')
}

/**
 * 更新用户信息
 * 可更新字段：email、phone、avatar等
 * @param {Object} data - 更新的字段
 * @param {string} [data.email] - 新邮箱
 * @param {string} [data.phone] - 新手机号
 * @param {string} [data.avatar] - 新头像URL
 * @param {Object} [config={}] - 可选请求配置，如额外请求头或上传配置
 * @returns {Promise<Object>} 更新后的用户信息
 */
export function updateUserInfo(data, config = {}) {
  return request.put('/api/auth/userinfo/update', data, config)
}

/**
 * 刷新访问令牌
 * 使用refresh_token获取新的access_token
 * @param {string} refreshToken - 刷新令牌
 * @returns {Promise<{access: string, refresh?: string}>} 新的令牌
 */
export function refreshToken(refreshToken) {
  return request.post('/api/auth/token/refresh', { refresh: refreshToken })
}

/**
 * 修改密码
 * 需要验证旧密码后才能设置新密码
 * @param {Object} data - 密码信息
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码（8+字符）
 * @returns {Promise<Object>} 修改结果
 */
export function changePassword(data) {
  return request.post('/api/auth/password/change', data)
}

/**
 * 发送重置密码验证码
 * @param {Object} data - 邮箱或手机号
 * @param {string} [data.email] - 邮箱
 * @param {string} [data.phone] - 手机号
 * @returns {Promise<Object>} 发送结果
 */
export function sendResetCode(data) {
  return request.post('/api/auth/password/reset/send', data)
}

/**
 * 重置密码
 * @param {Object} data - 重置信息
 * @param {string} data.code - 验证码
 * @param {string} data.new_password - 新密码
 * @returns {Promise<Object>} 重置结果
 */
export function resetPassword(data) {
  return request.post('/api/auth/password/reset', data)
}

/**
 * 退出登录
 * 将refresh token加入黑名单
 * @returns {Promise<Object>} 退出结果
 */
export function logout() {
  const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
  return request.post('/api/auth/logout', { refresh: refreshToken })
}
