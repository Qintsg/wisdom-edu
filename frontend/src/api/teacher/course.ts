/**
 * 教师端 - 课程管理API
 * 提供课程的增删改查功能
 */
import request from '../index'

/**
 * 获取我的课程列表
 * 返回当前教师创建或负责的所有课程
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Array>} 课程列表
 */
export function getMyCourses(params = {}) {
  return request.get('/api/teacher/courses/my', { params })
}

/**
 * 获取课程详情
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 课程详情
 */
export function getCourseDetail(courseId) {
  return request.get(`/api/teacher/courses/${courseId}`)
}

/**
 * 创建课程
 * @param {Object} data - 课程信息
 * @param {string} data.course_name - 课程名称
 * @param {string} [data.course_description] - 课程描述
 * @param {File} [data.course_cover] - 课程封面图片
 * @param {File} [data.archive] - 课程资源压缩包
 * @param {number} [data.publish_class_id] - 创建后立即发布到的班级ID
 * @returns {Promise<Object>} 创建结果
 */
export function createCourse(data) {
  const formData = new FormData()
  Object.keys(data).forEach(key => {
    if (data[key] !== undefined && data[key] !== null) {
      formData.append(key, data[key])
    }
  })
  return request.post('/api/teacher/courses/create', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 更新课程信息
 * @param {number} courseId - 课程ID
 * @param {Object} data - 更新的课程信息
 * @param {string} [data.course_name] - 课程名称
 * @param {string} [data.course_description] - 课程描述
 * @returns {Promise<Object>} 更新结果
 */
export function updateCourse(courseId, data) {
  return request.put(`/api/teacher/courses/${courseId}`, data)
}

/**
 * 删除课程
 * 删除后课程及相关数据将无法恢复
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteCourse(courseId) {
  return request.delete(`/api/teacher/courses/${courseId}/delete`)
}

/**
 * 上传课程封面
 * @param {number} courseId - 课程ID
 * @param {File} file - 封面图片文件
 * @returns {Promise<Object>} 上传结果，包含图片URL
 */
export function uploadCourseCover(courseId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/api/teacher/courses/${courseId}/cover/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 获取课程统计数据
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 统计数据
 */
export function getCourseStats(courseId) {
  return request.get(`/api/teacher/courses/${courseId}/statistics`)
}
