/**
 * 管理端 - 学生画像管理API
 */
import request from '../index'

/**
 * 获取所有学生画像列表
 * @param {Object} [params]
 * @param {number} [params.page]
 * @param {number} [params.size]
 * @param {number} [params.course_id]
 */
export function getStudentProfiles(params) {
  return request.get('/api/admin/student-profiles', { params })
}

/**
 * 获取学生画像详情
 * @param {number} studentId
 * @param {number} courseId
 */
export function getStudentProfileDetail(studentId, courseId) {
  return request.get(`/api/admin/student-profiles/${studentId}`, {
    params: { course_id: courseId }
  })
}
