/**
 * 课程相关API
 * 提供课程列表获取和课程切换功能
 */
import request from './index'

/**
 * 获取我的课程列表
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 分页页码
 * @param {number} [params.size] - 分页大小
 * @param {string} [params.query] - 搜索关键词
 * @returns {Promise} 课程列表，包含total和courses数组
 */
export function getCourses(params = {}) {
  return request.get('/api/courses', { params })
}

/**
 * 切换当前课程
 * @param {Object} data - 课程选择数据
 * @param {number} data.course_id - 课程ID（必填）
 * @param {number} [data.class_id] - 班级ID（选填）
 * @returns {Promise} 切换结果，包含course_id、course_name等
 */
export function selectCourse(data) {
  return request.post('/api/courses/select', data)
}

/**
 * 搜索课程
 * @param {string} query - 搜索关键词
 * @returns {Promise} 搜索结果
 */
export function searchCourses(query) {
  return request.get('/api/courses/search', {
    params: { query }
  })
}
