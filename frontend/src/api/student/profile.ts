/**
 * 学生端 - 学习画像相关API
 * 管理学习者画像、学习习惯偏好等
 * 画像刷新集成KT知识追踪 + LLM大模型分析
 */
import request from '../index'

/**
 * 获取学习画像
 * 返回学生在特定课程中的学习画像信息
 * @param {number} courseId - 课程ID
 * @returns {Promise} 学习画像详情，包括学习特征、掌握度等
 */
export function getProfile(courseId) {
  return request.get('/api/student/profile', {
    params: { course_id: courseId }
  })
}

/**
 * 更新学习习惯偏好
 * 学生可以调整或确认自己的学习习惯偏好
 * @param {Object} data - 偏好数据
 * @param {number} data.course_id - 课程ID
 * @param {Object} data.preferences - 偏好设置（学习时间、学习频率等）
 * @returns {Promise} 更新后的偏好信息
 */
export function updateHabitPreference(data) {
  return request.put('/api/student/profile/habit', data)
}

/**
 * 请求更新学习画像
 * 触发一次完整的画像重新评估：KT细化掌握度 + LLM深度分析
 * 结合能力评测结果和习惯问卷结果生成综合画像
 * @param {number} courseId - 课程ID
 * @returns {Promise} 更新后的画像数据，包含summary/weakness/suggestion/strength/kt_enhanced
 */
export function updateProfile(courseId) {
  return request.post('/api/student/profile/update', {
    course_id: courseId
  })
}

/**
 * AI主动刷新学习画像
 * 通过AI服务端点主动调用KT+LLM完整管线重新生成画像
 * 适用于主动触发刷新按钮场景
 * @param {number} courseId - 课程ID
 * @returns {Promise} 刷新后的画像数据
 */
export function refreshProfileWithAI(courseId) {
  return request.post('/api/student/ai/refresh-profile', {
    course_id: courseId
  })
}

/**
 * 获取画像历史
 * 返回学生学习画像的历史版本记录
 * @param {number} courseId - 课程ID
 * @param {Object} [params] - 额外参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * @returns {Promise} 画像历史列表
 */
export function getProfileHistory(courseId, params = {}) {
  return request.get('/api/student/profile/history', {
    params: { course_id: courseId, ...params }
  })
}

/**
 * 获取画像对比
 * 比较不同时间的学习画像变化
 * @param {number} courseId - 课程ID
 * @param {string} date1 - 第一个画像时间点，通常为历史画像的日期字符串
 * @param {string} date2 - 第二个画像时间点，通常为历史画像的日期字符串
 * @returns {Promise} 对比分析数据
 */
export function compareProfiles(courseId, date1, date2) {
  return request.get('/api/student/profile/compare', {
    params: { course_id: courseId, date1, date2 }
  })
}

/**
 * 导出学习画像
 * 以PDF或其他格式导出学习画像报告
 * @param {number} courseId - 课程ID
 * @returns {Promise} 导出结果（可能返回下载链接）
 */
export function exportProfile(courseId) {
  return request.post('/api/student/profile/export', {
    course_id: courseId
  })
}
