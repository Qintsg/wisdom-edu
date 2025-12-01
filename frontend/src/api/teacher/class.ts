/**
 * 教师端 - 班级管理API
 * 提供班级创建、学生管理、邀请码管理等功能
 */
import request from '../index'

/**
 * 获取我的班级列表
 * 返回当前教师管理的所有班级
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Array>} 班级列表
 */
export function getMyClasses(params = {}) {
  return request.get('/api/teacher/classes/my', { params })
}

/**
 * 获取班级详情
 * @param {number} classId - 班级ID
 * @returns {Promise<Object>} 班级详情
 */
export function getClassDetail(classId) {
  return request.get(`/api/teacher/classes/${classId}`)
}

/**
 * 创建班级
 * @param {Object} data - 班级信息
 * @param {string} data.class_name - 班级名称
 * @param {number} [data.course_id] - 关联课程ID
 * @param {string} [data.description] - 班级描述
 * @returns {Promise<Object>} 创建结果
 */
export function createClass(data) {
  return request.post('/api/teacher/classes/create', data)
}

/**
 * 更新班级信息
 * @param {number} classId - 班级ID
 * @param {Object} data - 更新的班级信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateClass(classId, data) {
  return request.put(`/api/teacher/classes/${classId}`, data)
}

/**
 * 删除班级
 * @param {number} classId - 班级ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteClass(classId) {
  return request.delete(`/api/teacher/classes/${classId}/delete`)
}

/**
 * 发布课程到班级
 * 将课程与班级关联，班级学生可以学习该课程
 * @param {number} classId - 班级ID
 * @param {Object} data - 发布信息
 * @param {number} data.course_id - 课程ID
 * @returns {Promise<Object>} 发布结果
 */
export function publishCourse(classId, data) {
  return request.post(`/api/teacher/classes/${classId}/publish-course`, data)
}

/**
 * 获取班级学生列表
 * @param {number} classId - 班级ID
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Object>} 学生列表
 */
export function getClassStudents(classId, params = {}) {
  return request.get(`/api/teacher/classes/${classId}/students`, { params })
}

/**
 * 移除班级学生
 * @param {number} classId - 班级ID
 * @param {number} studentId - 学生ID
 * @returns {Promise<Object>} 移除结果
 */
export function removeStudent(classId, studentId) {
  return request.delete(`/api/teacher/classes/${classId}/students/${studentId}`)
}

/**
 * 获取班级邀请码列表
 * @param {number} classId - 班级ID
 * @returns {Promise<Array>} 邀请码列表
 */
export function getInvitations(classId) {
  return request.get(`/api/teacher/classes/${classId}/invitations`)
}

/**
 * 生成邀请码
 * @param {Object} data - 邀请码配置
 * @param {number} data.class_id - 班级ID
 * @param {number} [data.max_uses] - 最大使用次数，0表示不限
 * @param {string} [data.expires_at] - 过期时间（ISO格式）
 * @returns {Promise<Object>} 生成的邀请码信息
 */
export function generateInvitation(data) {
  return request.post('/api/teacher/invitations/generate', data)
}

/**
 * 删除邀请码
 * @param {number} invitationId - 邀请码ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteInvitation(invitationId) {
  return request.delete(`/api/teacher/invitations/${invitationId}`)
}

/**
 * 获取班级学生画像列表
 * @param {number} classId - 班级ID
 * @param {Object} [params] - 查询参数
 * @returns {Promise<Array>} 学生画像列表
 */
export function getStudentProfiles(classId, params = {}) {
  return request.get(`/api/teacher/classes/${classId}/student-profiles`, { params })
}

/**
 * 获取单个学生画像详情
 * 
 * @param {number} classId - 班级ID（保留参数，用于前端兼容性）
 * @param {number} studentId - 学生ID
 * @param {number} [courseId] - 课程ID
 * @returns {Promise<Object>} 学生画像详情
 */
export function getStudentProfileDetail(classId, studentId, courseId) {
  const params: Record<string, any> = {}
  if (courseId) params.course_id = courseId
  return request.get(`/api/teacher/students/${studentId}/profile`, { params })
}

/**
 * 获取班级学习进度统计
 * @param {number} classId - 班级ID
 * @returns {Promise<Object>} 学习进度统计数据
 */
export function getClassProgress(classId) {
  return request.get(`/api/teacher/classes/${classId}/progress`)
}

// ============ 班级公告 ============

/**
 * 获取班级公告列表
 * @param {number} classId - 班级ID
 * @returns {Promise<Object>} 公告列表
 */
export function getAnnouncements(classId) {
  return request.get(`/api/teacher/classes/${classId}/announcements`)
}

/**
 * 创建班级公告
 * @param {number} classId - 班级ID
 * @param {Object} data - { title, content }
 * @returns {Promise<Object>} 创建结果
 */
export function createAnnouncement(classId, data) {
  return request.post(`/api/teacher/classes/${classId}/announcements`, data)
}

/**
 * 更新班级公告
 * @param {number} announcementId - 公告ID
 * @param {Object} data - { title, content }
 * @returns {Promise<Object>} 更新结果
 */
export function updateAnnouncement(announcementId, data) {
  return request.put(`/api/teacher/announcements/${announcementId}`, data)
}

/**
 * 删除班级公告
 * @param {number} announcementId - 公告ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteAnnouncement(announcementId) {
  return request.delete(`/api/teacher/announcements/${announcementId}`)
}
