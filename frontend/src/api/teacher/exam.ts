/**
 * 教师端 - 作业管理API
 * 提供考试的创建、发布、成绩查看等功能
 */
import request from '../index'

/**
 * 获取作业列表
 * @param {number} courseId - 课程ID
 * @param {Object} [params] - 查询参数
 * @param {string} [params.status] - 考试状态：draft/published/ended
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Object>} 作业列表
 */
export function getExams(courseId, params = {}) {
  return request.get('/api/teacher/exams', {
    params: { course_id: courseId, ...params }
  })
}

/**
 * 获取作业详情
 * @param {number} examId - 考试ID
 * @returns {Promise<Object>} 考试详情
 */
export function getExamDetail(examId) {
  return request.get(`/api/teacher/exams/${examId}`)
}

/**
 * 创建作业
 * @param {Object} data - 考试信息
 * @param {string} data.exam_name - 作业名称
 * @param {number} data.course_id - 课程ID
 * @param {Array<number>} data.question_ids - 题目ID列表
 * @param {number} data.duration - 考试时长（分钟）
 * @param {string} [data.start_time] - 开始时间（ISO格式）
 * @param {string} [data.end_time] - 结束时间（ISO格式）
 * @param {number} [data.pass_score] - 及格分数
 * @param {boolean} [data.shuffle_questions] - 是否打乱题目顺序
 * @param {boolean} [data.shuffle_options] - 是否打乱选项顺序
 * @returns {Promise<Object>} 创建结果
 */
export function createExam(data) {
  return request.post('/api/teacher/exams/create', data)
}

/**
 * 更新考试信息
 * @param {number} examId - 考试ID
 * @param {Object} data - 更新的考试信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateExam(examId, data) {
  return request.put(`/api/teacher/exams/${examId}/update`, data)
}

/**
 * 删除考试
 * @param {number} examId - 考试ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteExam(examId) {
  return request.delete(`/api/teacher/exams/${examId}/delete`)
}

/**
 * 发布考试到班级
 * @param {number} examId - 考试ID
 * @param {Object} data - 发布信息
 * @param {number} data.class_id - 目标班级ID
 * @param {string} [data.start_time] - 开放时间
 * @param {string} [data.end_time] - 截止时间
 * @returns {Promise<Object>} 发布结果
 */
export function publishExam(examId, data) {
  return request.post(`/api/teacher/exams/${examId}/publish`, data)
}

/**
 * 取消发布考试
 * @param {number} examId - 考试ID
 * @returns {Promise<Object>} 取消结果
 */
export function unpublishExam(examId) {
  return request.post(`/api/teacher/exams/${examId}/unpublish`)
}

/**
 * 获取作业成绩列表
 * @param {number} examId - 考试ID
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Object>} 成绩列表
 */
export function getExamResults(examId, params = {}) {
  return request.get(`/api/teacher/exams/${examId}/results`, { params })
}

/**
 * 获取学生考试详情
 * 查看单个学生的答题情况和成绩
 * @param {number} examId - 考试ID
 * @param {number} studentId - 学生ID
 * @returns {Promise<Object>} 学生答题详情
 */
export function getStudentExamDetail(examId, studentId) {
  return request.get(`/api/teacher/exams/${examId}/students/${studentId}`)
}

/**
 * 获取作业统计分析
 * @param {number} examId - 考试ID
 * @returns {Promise<Object>} 统计分析数据
 */
export function getExamAnalysis(examId) {
  return request.get(`/api/teacher/exams/${examId}/analysis`)
}

/**
 * 导出考试成绩
 * @param {number} examId - 考试ID
 * @param {string} [format] - 导出格式：xlsx/csv/pdf
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportExamResults(examId, format = 'xlsx') {
  return request.get(`/api/teacher/exams/${examId}/export`, {
    params: { format },
    responseType: 'blob'
  })
}

/**
 * 添加题目到考试
 * @param {number} examId - 考试ID
 * @param {Array<number>} questionIds - 题目ID列表
 * @returns {Promise<Object>} 添加结果
 */
export function addQuestionsToExam(examId, questionIds) {
  return request.post(`/api/teacher/exams/${examId}/questions/add`, {
    question_ids: questionIds
  })
}

/**
 * 从考试移除题目
 * @param {number} examId - 考试ID
 * @param {Array<number>} questionIds - 题目ID列表
 * @returns {Promise<Object>} 移除结果
 */
export function removeQuestionsFromExam(examId, questionIds) {
  return request.post(`/api/teacher/exams/${examId}/questions/remove`, {
    question_ids: questionIds
  })
}
