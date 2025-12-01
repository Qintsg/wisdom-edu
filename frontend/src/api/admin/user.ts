/**
 * 管理端 - 用户管理API
 * 提供用户的增删改查、密码重置、批量导入等功能
 */
import request from '../index'

/**
 * 获取用户列表
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @param {string} [params.role] - 角色筛选：student/teacher/admin
 * @param {string} [params.query] - 搜索关键词（用户名/邮箱/手机号）
 * @param {string} [params.status] - 状态筛选：active/inactive
 * @returns {Promise<Object>} 用户列表和分页信息
 */
export function getUsers(params) {
  return request.get('/api/admin/users', { params })
}

/**
 * 获取用户列表（别名兼容旧代码）
 * @param {Object} [params] - 查询参数
 * @returns {Promise<Object>} 用户列表
 */
export function getUserList(params) {
  return request.get('/api/admin/users', { params })
}

/**
 * 获取用户详情
 * @param {number} userId - 用户ID
 * @returns {Promise<Object>} 用户详细信息
 */
export function getUserDetail(userId) {
  return request.get(`/api/admin/users/${userId}`)
}

/**
 * 创建用户
 * @param {Object} data - 用户信息
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @param {string} data.role - 角色
 * @param {string} [data.email] - 邮箱
 * @param {string} [data.phone] - 手机号
 * @returns {Promise<Object>} 创建结果
 */
export function createUser(data) {
  return request.post('/api/admin/users/create', data)
}

/**
 * 更新用户信息
 * @param {number} userId - 用户ID
 * @param {Object} data - 更新的用户信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateUser(userId, data) {
  return request.put(`/api/admin/users/${userId}/update`, data)
}

/**
 * 删除用户
 * @param {number} userId - 用户ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteUser(userId) {
  return request.delete(`/api/admin/users/${userId}/delete`)
}

/**
 * 批量删除用户
 * @param {Array<number>} userIds - 用户ID列表
 * @returns {Promise<Object>} 删除结果
 */
export function batchDeleteUsers(userIds) {
  return request.post('/api/admin/users/batch-delete', { user_ids: userIds })
}

/**
 * 重置用户密码
 * @param {number} userId - 用户ID
 * @param {string} [newPassword] - 新密码，不提供则自动生成
 * @returns {Promise<Object>} 重置结果，可能包含新密码
 */
export function resetUserPassword(userId, newPassword) {
  return request.post(`/api/admin/users/${userId}/reset-password`, {
    new_password: newPassword
  })
}

/**
 * 禁用用户
 * @param {number} userId - 用户ID
 * @returns {Promise<Object>} 操作结果
 */
export function disableUser(userId) {
  return request.post(`/api/admin/users/${userId}/disable`)
}

/**
 * 启用用户
 * @param {number} userId - 用户ID
 * @returns {Promise<Object>} 操作结果
 */
export function enableUser(userId) {
  return request.post(`/api/admin/users/${userId}/enable`)
}

/**
 * 批量导入用户
 * 支持Excel/CSV格式文件
 * @param {File} file - 用户数据文件
 * @returns {Promise<Object>} 导入结果，包含成功/失败数量
 */
export function importUsers(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/admin/users/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 导出用户列表
 * @param {Object} [params] - 筛选参数
 * @param {string} [params.format] - 导出格式：xlsx/csv
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportUsers(params) {
  return request.get('/api/admin/users/export', {
    params,
    responseType: 'blob'
  })
}

/**
 * 获取用户导入模板
 * @returns {Promise<Blob>} 模板文件
 */
export function getUserImportTemplate() {
  return request.get('/api/admin/users/template', {
    responseType: 'blob'
  })
}
