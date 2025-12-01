/**
 * 管理端 - 课程管理API
 * 管理员可管理所有课程
 */
import request from '../index'

/**
 * 获取所有课程列表
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @param {string} [params.query] - 搜索关键词
 * @param {number} [params.teacher_id] - 教师ID筛选
 * @param {string} [params.status] - 状态筛选
 * @returns {Promise<Object>} 课程列表
 */
export function getAllCourses(params) {
  return request.get('/api/admin/courses', { params })
}

/**
 * 获取课程详情
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 课程详情
 */
export function getCourseDetail(courseId) {
  return request.get(`/api/admin/courses/${courseId}`)
}

/**
 * 创建课程
 * @param {Object} data - 课程信息
 * @param {string} data.course_name - 课程名称
 * @param {string} [data.course_description] - 课程描述
 * @param {number} [data.teacher_id] - 负责教师ID
 * @returns {Promise<Object>} 创建结果
 */
export function createCourse(data) {
  return request.post('/api/admin/courses/create', data)
}

/**
 * 更新课程信息
 * @param {number} courseId - 课程ID
 * @param {Object} data - 更新的课程信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateCourse(courseId, data) {
  return request.put(`/api/admin/courses/${courseId}`, data)
}

/**
 * 删除课程
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteCourse(courseId) {
  return request.delete(`/api/admin/courses/${courseId}`)
}

/**
 * 分配课程教师
 * @param {number} courseId - 课程ID
 * @param {number} teacherId - 教师ID
 * @returns {Promise<Object>} 分配结果
 */
export function assignCourseTeacher(courseId, teacherId) {
  return request.post(`/api/admin/courses/${courseId}/assign-teacher`, {
    teacher_id: teacherId
  })
}

/**
 * 获取课程统计
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 统计数据
 */
export function getCourseStats(courseId) {
  return request.get(`/api/admin/courses/${courseId}/statistics`)
}
