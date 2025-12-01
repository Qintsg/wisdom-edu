/**
 * 教师端 - 题库管理API
 * 提供题目的增删改查和批量导入功能
 */
import request from '../index'

/**
 * 获取题目列表
 * @param {Object} params - 查询参数
 * @param {number} params.course_id - 课程ID（必填）
 * @param {string} [params.type] - 题目类型：single_choice/multiple_choice/true_false/fill_blank/short_answer/code
 * @param {number} [params.point_id] - 知识点ID
 * @param {string} [params.difficulty] - 难度等级：easy/medium/hard
 * @param {string} [params.keyword] - 搜索关键词
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Object>} 题目列表
 */
export function getQuestions(params) {
  return request.get('/api/teacher/questions', { params })
}

/**
 * 获取题目详情
 * @param {number} questionId - 题目ID
 * @returns {Promise<Object>} 题目详情
 */
export function getQuestionDetail(questionId) {
  return request.get(`/api/teacher/questions/${questionId}`)
}

/**
 * 创建题目
 * @param {Object} data - 题目信息
 * @param {number} data.course_id - 课程ID
 * @param {string} data.content - 题目内容
 * @param {string} data.question_type - 题目类型
 * @param {Array} data.options - 选项列表
 * @param {string} data.answer - 正确答案
 * @param {Array<number>} [data.points] - 关联知识点ID列表
 * @param {string} [data.difficulty] - 难度等级：easy/medium/hard
 * @param {string} [data.analysis] - 答案解析
 * @param {number} [data.score] - 分值
 * @returns {Promise<Object>} 创建结果
 */
export function createQuestion(data) {
  return request.post('/api/teacher/questions/create', data)
}

/**
 * 更新题目
 * @param {number} questionId - 题目ID
 * @param {Object} data - 更新的题目信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateQuestion(questionId, data) {
  return request.put(`/api/teacher/questions/${questionId}`, data)
}

/**
 * 删除题目
 * @param {number} questionId - 题目ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteQuestion(questionId) {
  return request.delete(`/api/teacher/questions/${questionId}/delete`)
}

/**
 * 批量删除题目
 * @param {Array<number>} questionIds - 题目ID列表
 * @returns {Promise<Object>} 删除结果
 */
export function batchDeleteQuestions(questionIds) {
  return request.post('/api/teacher/questions/batch-delete', { question_ids: questionIds })
}

/**
 * 批量导入题目
 * 支持Excel/CSV格式文件
 * @param {number} courseId - 课程ID
 * @param {File} file - 题目文件
 * @returns {Promise<Object>} 导入结果，包含成功/失败数量
 */
export function importQuestions(courseId, file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('course_id', courseId)
  return request.post('/api/teacher/questions/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 导出题目
 * @param {Object} params - 导出参数
 * @param {number} params.course_id - 课程ID
 * @param {string} [params.format] - 导出格式：xlsx/csv
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportQuestions(params) {
  return request.get('/api/teacher/questions/export', {
    params,
    responseType: 'blob'
  })
}

/**
 * 获取题目模板
 * @returns {Promise<Blob>} 模板文件
 */
export function getQuestionTemplate() {
  return request.get('/api/teacher/questions/template', {
    responseType: 'blob'
  })
}

/**
 * 关联题目到知识点
 * @param {number} questionId - 题目ID
 * @param {number} knowledgePointId - 知识点ID
 * @returns {Promise<Object>} 关联结果
 */
export function linkQuestionToKnowledge(questionId, knowledgePointId) {
  return request.post(`/api/teacher/questions/${questionId}/link-knowledge`, {
    knowledge_point_id: knowledgePointId
  })
}
