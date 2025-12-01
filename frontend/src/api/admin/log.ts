/**
 * 管理端 - 系统日志API
 * 提供操作日志的查询、统计、导出功能
 */
import request from '../index'

/**
 * 获取操作日志列表
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @param {string} [params.module] - 模块筛选
 * @param {string} [params.action] - 操作类型筛选
 * @param {number} [params.user_id] - 用户ID筛选
 * @param {string} [params.level] - 日志级别：info/warning/error
 * @param {string} [params.start_time] - 开始时间（ISO格式）
 * @param {string} [params.end_time] - 结束时间（ISO格式）
 * @returns {Promise<Object>} 日志列表
 */
export function getLogs(params) {
  return request.get('/api/admin/logs', { params })
}

/**
 * 获取系统日志列表（别名兼容旧代码）
 * @param {Object} [params] - 查询参数
 * @returns {Promise<Object>} 日志列表
 */
export function getSystemLogs(params) {
  return request.get('/api/admin/logs', { params })
}

/**
 * 获取日志详情
 * @param {number} logId - 日志ID
 * @returns {Promise<Object>} 日志详情
 */
export function getLogDetail(logId) {
  return request.get(`/api/admin/logs/${logId}`)
}

/**
 * 获取日志统计
 * 返回各模块、操作类型的日志数量统计
 * @param {Object} [params] - 统计参数
 * @param {string} [params.start_time] - 开始时间
 * @param {string} [params.end_time] - 结束时间
 * @returns {Promise<Object>} 统计数据
 */
export function getLogStatistics(params) {
  return request.get('/api/admin/logs/statistics', { params })
}

/**
 * 获取日志筛选选项（操作类型、模块）
 * @returns {Promise<Object>} 筛选选项列表
 */
export function getLogOptions() {
  return request.get('/api/admin/logs/options')
}

/**
 * 获取日志模块列表
 * 返回所有可用的日志模块名称
 * @returns {Promise<Array>} 模块列表
 */
export function getLogModules() {
  return request.get('/api/admin/logs/modules')
}

/**
 * 获取日志操作类型列表
 * @returns {Promise<Array>} 操作类型列表
 */
export function getLogActions() {
  return request.get('/api/admin/logs/actions')
}

/**
 * 导出日志
 * @param {Object} [params] - 筛选条件（同getLogs）
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportLogs(params) {
  return request.get('/api/admin/logs/export', {
    params,
    responseType: 'blob'
  })
}

/**
 * 导出数据（别名兼容旧代码）
 * @param {Object} [params] - 筛选条件
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportData(params) {
  return request.get('/api/admin/logs/export', {
    params,
    responseType: 'blob'
  })
}

/**
 * 清理过期日志
 * @param {Object} data - 清理参数
 * @param {number} data.days - 保留天数
 * @returns {Promise<Object>} 清理结果
 */
export function cleanExpiredLogs(data) {
  return request.post('/api/admin/logs/clean', data)
}
