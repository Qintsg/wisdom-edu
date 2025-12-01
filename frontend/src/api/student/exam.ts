/**
 * 学生端 - 考试相关API
 * 管理作业、答卷、成绩、反馈等
 */
import request from '../index'

/**
 * 获取作业列表
 * 返回学生参加或可参加的所有考试
 * @param {number} [courseId] - 课程ID，不提供则返回所有课程的考试
 * @param {Object} [params] - 额外参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * @returns {Promise} 作业列表
 */
export function getExamList(courseId, params = {}) {
  const queryParams = courseId ? { course_id: courseId, ...params } : params
  return request.get('/api/student/exams', { params: queryParams })
}

/**
 * 获取作业详情（开始作答）
 * 返回考试的题目、时间限制等信息，学生据此开始作答
 * @param {number} examId - 考试ID
 * @returns {Promise} 考试详情，包括题目列表、时间限制等
 */
export function getExamDetail(examId) {
  return request.get(`/api/student/exams/${examId}`)
}

/**
 * 保存考试草稿
 * 学生在作答过程中保存当前的作答进度
 * @param {number} examId - 考试ID
 * @param {Object} data - 答案草稿数据
 * @returns {Promise} 保存结果
 */
export function saveExamDraft(examId, data) {
  return request.post(`/api/student/exams/${examId}/draft`, data)
}

/**
 * 提交考试答案
 * 学生完成考试并提交所有答案
 * @param {number} examId - 考试ID
 * @param {Object} data
 * @param {Array<{question_id: number, answer: string}>} data.answers - 答题数据
 * @param {number} [data.duration] - 作答耗时（秒）
 * @returns {Promise} 提交结果
 */
export function submitExam(examId, data) {
  return request.post(`/api/student/exams/${examId}/submit`, data)
}

/**
 * 获取作业结果
 * 返回学生的考试成绩和各题答题情况
 * @param {number} examId - 考试ID
 * @returns {Promise} 考试结果，包括总分、各题分数等
 */
export function getExamResult(examId) {
  return request.get(`/api/student/exams/${examId}/result`)
}

/**
 * 生成作业反馈报告
 * 触发AI生成基于考试成绩的个性化反馈报告
 * 后端会自动集成KT知识追踪预测 + LLM分析
 * 并结合能力评测结果和习惯问卷数据
 * @param {number} examId - 考试ID
 * @param {boolean} [force=false] - 是否强制重新生成
 * @returns {Promise} 生成结果，包含KT分析、能力评估和习惯上下文
 */
export function generateFeedback(examId, force = false) {
  return request.post('/api/student/feedback/generate', { exam_id: examId, force })
}

/**
 * 获取作业反馈报告
 * 返回AI为学生生成的反馈报告（含KT+LLM分析结果）
 * @param {number} examId - 考试ID
 * @returns {Promise} 反馈报告内容
 */
export function getFeedback(examId) {
  return request.get(`/api/student/feedback/${examId}`)
}

/**
 * 获取作业统计数据
 * 返回考试的整体统计（平均分、通过率等）
 * @param {number} examId - 考试ID
 * @returns {Promise} 统计数据
 */
export function getExamStatistics(examId) {
  return request.get(`/api/student/exams/${examId}/statistics`)
}

/**
 * 下载考试答案
 * 导出考试的答案和成绩报告
 * @param {number} examId - 考试ID
 * @param {string} [format] - 导出格式（pdf/xlsx等）
 * @returns {Promise} 下载结果
 */
export function downloadExamReport(examId, format = 'pdf') {
  return request.get(`/api/student/exams/${examId}/download`, {
    params: { format }
  })
}

/**
 * 重新参加考试
 * 学生可以重新参加某个开放重考的考试
 * @param {number} examId - 考试ID
 * @returns {Promise} 新考试信息
 */
export function retakeExam(examId) {
  return request.post(`/api/student/exams/${examId}/retake`)
}

/**
 * 查看答卷
 * 获取作业的标准答案（作业结束后可用）
 * @param {number} examId - 考试ID
 * @returns {Promise} 答卷详情和标准答案
 */
export function getExamAnswerSheet(examId) {
  return request.get(`/api/student/exams/${examId}/answer-sheet`)
}
