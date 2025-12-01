/**
 * 管理端 - 班级管理API
 * 管理员可管理所有班级
 */
import request from '../index'

/**
 * 获取班级列表
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @param {string} [params.query] - 搜索关键词
 * @param {number} [params.teacher_id] - 教师ID筛选
 * @param {number} [params.course_id] - 课程ID筛选
 * @returns {Promise<Object>} 班级列表
 */
export function getClassList(params) {
  return request.get('/api/admin/classes', { params })
}

/**
 * 获取班级详情
 * @param {number} classId - 班级ID
 * @returns {Promise<Object>} 班级详情
 */
export function getClassDetail(classId) {
  return request.get(`/api/admin/classes/${classId}`)
}

/**
 * 创建班级
 * @param {Object} data - 班级信息
 * @param {string} data.class_name - 班级名称
 * @param {number} [data.course_id] - 关联课程ID
 * @param {number} [data.teacher_id] - 负责教师ID
 * @returns {Promise<Object>} 创建结果
 */
export function createClass(data) {
  return request.post('/api/admin/classes/create', data)
}

/**
 * 更新班级信息
 * @param {number} classId - 班级ID
 * @param {Object} data - 更新的班级信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateClass(classId, data) {
  return request.put(`/api/admin/classes/${classId}`, data)
}

/**
 * 删除班级
 * @param {number} classId - 班级ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteClass(classId) {
  return request.delete(`/api/admin/classes/${classId}`)
}

/**
 * 获取班级学生列表
 * @param {number} classId - 班级ID
 * @param {Object} [params] - 查询参数
 * @returns {Promise<Object>} 学生列表
 */
export function getClassStudents(classId, params = {}) {
  return request.get(`/api/admin/classes/${classId}/students`, { params })
}

/**
 * 添加学生到班级
 * @param {number} classId - 班级ID
 * @param {Array<number>} studentIds - 学生ID列表
 * @returns {Promise<Object>} 添加结果
 */
export function addStudentsToClass(classId, studentIds) {
  return request.post(`/api/admin/classes/${classId}/students/add`, {
    student_ids: studentIds
  })
}

/**
 * 从班级移除学生
 * @param {number} classId - 班级ID
 * @param {number} studentId - 学生ID
 * @returns {Promise<Object>} 移除结果
 */
export function removeStudentFromClass(classId, studentId) {
  return request.delete(`/api/admin/classes/${classId}/students/${studentId}`)
}

/**
 * 分配班级教师
 * @param {number} classId - 班级ID
 * @param {number} teacherId - 教师ID
 * @returns {Promise<Object>} 分配结果
 */
export function assignClassTeacher(classId, teacherId) {
  return request.post(`/api/admin/classes/${classId}/assign-teacher`, {
    teacher_id: teacherId
  })
}

/**
 * 获取班级统计
 * @param {number} classId - 班级ID
 * @returns {Promise<Object>} 统计数据
 */
export function getClassStats(classId) {
  return request.get(`/api/admin/classes/${classId}/statistics`)
}
