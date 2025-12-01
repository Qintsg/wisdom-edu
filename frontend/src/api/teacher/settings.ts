/**
 * 教师端 - 课程配置管理API
 * 管理考试设置、课程行为配置等
 */
import request from '../index'

/**
 * 获取课程配置
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 课程配置信息
 */
export function getCourseSettings(courseId) {
  return request.get(`/api/teacher/courses/${courseId}/settings`)
}

/**
 * 更新课程配置
 * @param {number} courseId - 课程ID
 * @param {Object} data - 配置数据
 * @returns {Promise<Object>} 更新结果
 */
export function updateCourseSettings(courseId, data) {
  return request.put(`/api/teacher/courses/${courseId}/settings/update`, data)
}
