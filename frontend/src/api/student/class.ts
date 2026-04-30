/**
 * 学生端 - 班级相关API
 * 管理班级加入、退出、班级成员等
 */
import request from '../index'

export interface StudentClassCourseSummary {
  course_id: number
  course_name: string
  course_cover?: string | null
}

export interface StudentClassSummary {
  class_id: number
  class_name: string
  description?: string
  teacher_name?: string | null
  teacher_username?: string | null
  student_count?: number
  courses?: StudentClassCourseSummary[]
  course_id?: number | null
  course_name?: string | null
  enrolled_at?: string
}

export interface StudentClassListResponse {
  classes: StudentClassSummary[]
}

export interface JoinClassPayload {
  code: string
}

/**
 * 获取班级列表
 * 返回学生所在的所有班级
 * @returns {Promise} 班级列表
 */
export function getClassList(): Promise<StudentClassListResponse> {
  return request.get<StudentClassListResponse>('/api/student/classes')
}

/**
 * 获取班级详情
 * 返回班级的详细信息和成员列表
 * @param {number} classId - 班级ID
 * @returns {Promise} 班级详情
 */
export function getClassDetail(classId: number | string) {
  return request.get(`/api/student/classes/${classId}`)
}

/**
 * 加入班级
 * 学生使用邀请码加入班级
 * @param {Object} data
 * @param {string} data.code - 邀请码
 * @returns {Promise} 加入结果
 */
export function joinClass(data: JoinClassPayload): Promise<StudentClassSummary> {
  return request.post<StudentClassSummary, { code: string }>('/api/student/classes/join', {
    code: data.code.trim().toUpperCase()
  })
}

/**
 * 退出班级
 * 学生退出某个班级
 * @param {number} classId - 班级ID
 * @returns {Promise} 退出结果
 */
export function leaveClass(classId: number | string) {
  return request.delete(`/api/student/classes/${classId}/leave`)
}

/**
 * 获取班级成员列表
 * 返回班级中的所有成员信息
 * @param {number} classId - 班级ID
 * @param {Object} [params] - 分页参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * @returns {Promise} 成员列表
 */
export function getClassMembers(classId: number | string, params = {}) {
  return request.get(`/api/student/classes/${classId}/members`, { params })
}

/**
 * 获取班级排行榜
 * 返回班级内学生的学习进度排行
 * @param {number} classId - 班级ID
 * @param {string} [sortBy] - 排序字段（progress/score/completion）
 * @returns {Promise} 排行榜数据
 */
export function getClassRanking(classId: number | string, sortBy = 'progress') {
  return request.get(`/api/student/classes/${classId}/ranking`, {
    params: { sort_by: sortBy }
  })
}

/**
 * 获取班级通知
 * 返回班级的公告和通知
 * @param {number} classId - 班级ID
 * @param {Object} [params] - 分页参数
 * @returns {Promise} 通知列表
 */
export function getClassNotifications(classId: number | string, params = {}) {
  return request.get(`/api/student/classes/${classId}/notifications`, { params })
}

/**
 * 获取班级作业列表
 * 返回班级分配的作业
 * @param {number} classId - 班级ID
 * @param {Object} [params] - 筛选参数
 * @returns {Promise} 作业列表
 */
export function getClassAssignments(classId: number | string, params = {}) {
  return request.get(`/api/student/classes/${classId}/assignments`, { params })
}
