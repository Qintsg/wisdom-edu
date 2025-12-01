/**
 * 管理端 - 激活码管理API
 * 提供激活码的生成、查询、删除功能
 * 激活码用于教师/管理员账号注册
 */
import request from '../index'

/**
 * 获取激活码列表
 * @param {Object} [params] - 查询参数
 * @param {string} [params.role] - 角色筛选：teacher/admin
 * @param {boolean} [params.used] - 使用状态筛选
 * @param {boolean} [params.expired] - 过期状态筛选
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Object>} 激活码列表
 */
export function getActivationCodes(params) {
  return request.get('/api/admin/activation-codes', { params })
}

/**
 * 获取激活码详情
 * @param {number} codeId - 激活码ID
 * @returns {Promise<Object>} 激活码详情
 */
export function getActivationCodeDetail(codeId) {
  return request.get(`/api/admin/activation-codes/${codeId}`)
}

/**
 * 生成激活码
 * @param {Object} data - 生成参数
 * @param {string} data.role - 目标角色：teacher/admin
 * @param {number} [data.count=1] - 生成数量
 * @param {string} [data.expires_at] - 过期时间（ISO格式）
 * @param {string} [data.remark] - 备注
 * @returns {Promise<Object>} 生成的激活码列表
 */
export function generateActivationCodes(data) {
  return request.post('/api/admin/activation-codes/generate', data)
}

/**
 * 删除激活码
 * @param {number} codeId - 激活码ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteActivationCode(codeId) {
  return request.delete(`/api/admin/activation-codes/${codeId}`)
}

/**
 * 批量删除激活码
 * @param {Array<number>} codeIds - 激活码ID列表
 * @returns {Promise<Object>} 删除结果
 */
export function batchDeleteActivationCodes(codeIds) {
  return request.post('/api/admin/activation-codes/batch-delete', {
    code_ids: codeIds
  })
}

/**
 * 验证激活码
 * @param {string} code - 激活码
 * @returns {Promise<Object>} 验证结果
 */
export function validateActivationCode(code) {
  return request.post('/api/admin/activation-codes/validate', { code })
}

/**
 * 导出激活码
 * @param {Object} [params] - 筛选参数
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportActivationCodes(params) {
  return request.get('/api/admin/activation-codes/export', {
    params,
    responseType: 'blob'
  })
}
