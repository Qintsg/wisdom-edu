/**
 * 管理端 - 统计数据API
 * 提供系统级别的统计和分析数据
 */
import request from '../index'

/**
 * 获取系统概览统计
 * 返回用户数、课程数、班级数等基本统计
 * @returns {Promise<Object>} 概览统计数据
 */
export function getOverviewStats() {
  return request.get('/api/admin/statistics/overview')
}

/**
 * 获取系统统计数据（别名兼容旧代码）
 * @returns {Promise<Object>} 概览统计数据
 */
export function getSystemStats() {
  return request.get('/api/admin/statistics/overview')
}

/**
 * 获取用户统计
 * 用户增长趋势、活跃度等
 * @param {Object} [params] - 统计参数
 * @param {string} [params.start_date] - 开始日期
 * @param {string} [params.end_date] - 结束日期
 * @param {string} [params.granularity] - 粒度：day/week/month
 * @returns {Promise<Object>} 用户统计数据
 */
export function getUserStats(params) {
  return request.get('/api/admin/statistics/users', { params })
}

/**
 * 获取课程统计
 * 课程使用情况、热门课程等
 * @param {Object} [params] - 统计参数
 * @param {string} [params.start_date] - 开始日期
 * @param {string} [params.end_date] - 结束日期
 * @returns {Promise<Object>} 课程统计数据
 */
export function getCourseStats(params) {
  return request.get('/api/admin/statistics/courses', { params })
}

/**
 * 获取学习统计
 * 整体学习时长、完成率等
 * @param {Object} [params] - 统计参数
 * @param {string} [params.start_date] - 开始日期
 * @param {string} [params.end_date] - 结束日期
 * @param {number} [params.course_id] - 课程ID筛选
 * @returns {Promise<Object>} 学习统计数据
 */
export function getLearningStats(params) {
  return request.get('/api/admin/statistics/learning', { params })
}

/**
 * 获取作业统计
 * 考试参与率、平均分等
 * @param {Object} [params] - 统计参数
 * @returns {Promise<Object>} 考试统计数据
 */
export function getExamStats(params) {
  return request.get('/api/admin/statistics/exams', { params })
}

/**
 * 获取活跃用户排行
 * @param {Object} [params] - 统计参数
 * @param {number} [params.limit] - 返回数量
 * @returns {Promise<Array>} 活跃用户列表
 */
export function getActiveUserRanking(params) {
  return request.get('/api/admin/statistics/active-users', { params })
}

/**
 * 获取系统运行报告
 * @param {Object} [params] - 报告参数
 * @param {string} [params.type] - 报告类型：daily/weekly/monthly
 * @returns {Promise<Object>} 系统报告
 */
export function getSystemReport(params) {
  return request.get('/api/admin/statistics/report', { params })
}

/**
 * 导出统计数据
 * @param {Object} params - 导出参数
 * @param {string} params.type - 数据类型：users/courses/learning
 * @param {string} [params.format] - 格式：xlsx/csv
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportStatistics(params) {
  return request.get('/api/admin/statistics/export', {
    params,
    responseType: 'blob'
  })
}
