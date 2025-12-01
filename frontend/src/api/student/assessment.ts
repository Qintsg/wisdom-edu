/**
 * 学生端 - 测评相关API
 * 包括初测（能力评测、习惯问卷、知识测评）和学习者画像生成
 */
import request from '../index'

export interface AssessmentStatusPayload {
  ability_completed?: boolean
  habit_completed?: boolean
  knowledge_completed?: boolean
  [key: string]: unknown
}

export interface AssessmentQuestion {
  question_id?: number
  id?: number
  [key: string]: unknown
}

export interface AssessmentQuestionResponse {
  questions?: AssessmentQuestion[]
  [key: string]: unknown
}

export interface AssessmentAnswerPayload {
  question_id: number
  answer: string
}

export interface AbilityAssessmentSubmitPayload {
  answers: AssessmentAnswerPayload[]
}

export interface HabitSurveySubmitPayload {
  responses: AssessmentAnswerPayload[]
}

export interface KnowledgeAssessmentSubmitPayload {
  course_id: number | null | undefined
  answers: AssessmentAnswerPayload[]
}

/**
 * 获取测评完成状态
 * 返回学生的各项测评是否已完成
 * @param {number} [courseId] - 课程ID，可选
 * @returns {Promise} 测评状态信息
 */
export function getAssessmentStatus(courseId?: number | null): Promise<AssessmentStatusPayload> {
  return request.get<AssessmentStatusPayload>('/api/student/assessments/status', {
    params: courseId ? { course_id: courseId } : {}
  })
}

/**
 * 获取能力评测题目
 * 返回能力评测的所有题目，用于学生填答
 * @param {number} courseId - 课程ID
 * @returns {Promise} 能力评测题目列表
 */
export function getAbilityAssessment(courseId: number | null = null): Promise<AssessmentQuestionResponse | AssessmentQuestion[]> {
  return request.get<AssessmentQuestionResponse | AssessmentQuestion[]>('/api/student/assessments/initial/ability', {
    params: { course_id: courseId }
  })
}

/**
 * 提交能力评测答案
 * @param {Object} data
 * @param {Array<{question_id: number, answer: string}>} data.answers - 答题数据
 * @returns {Promise} 提交结果
 */
export function submitAbilityAssessment(data: AbilityAssessmentSubmitPayload): Promise<unknown> {
  return request.post('/api/student/assessments/initial/ability/submit', data)
}

/**
 * 获取习惯问卷题目
 * 返回学习习惯问卷的所有题目
 * @param {number} [courseId] - 课程ID，可选
 * @returns {Promise} 习惯问卷题目列表
 */
export function getHabitSurvey(courseId: number | null = null): Promise<AssessmentQuestionResponse | AssessmentQuestion[]> {
  return request.get<AssessmentQuestionResponse | AssessmentQuestion[]>('/api/student/assessments/initial/habit', {
    params: courseId ? { course_id: courseId } : {}
  })
}

/**
 * 提交习惯问卷答案
 * @param {Object} data
 * @param {Array<{question_id: number, answer: string}>} data.responses - 问卷答题数据
 * @returns {Promise} 提交结果
 */
export function submitHabitSurvey(data: HabitSurveySubmitPayload): Promise<unknown> {
  return request.post('/api/student/assessments/initial/habit/submit', data)
}

/**
 * 获取知识测评题目
 * 返回特定课程的知识测评题目
 * @param {number} courseId - 课程ID
 * @returns {Promise} 知识测评题目列表
 */
export function getKnowledgeAssessment(courseId: number | null | undefined): Promise<AssessmentQuestionResponse | AssessmentQuestion[]> {
  return request.get<AssessmentQuestionResponse | AssessmentQuestion[]>('/api/student/assessments/initial/knowledge', {
    params: { course_id: courseId }
  })
}

/**
 * 提交知识测评答案
 * @param {Object} data
 * @param {number} data.course_id - 课程ID
 * @param {Array<{question_id: number, answer: string}>} data.answers - 答题数据
 * @returns {Promise} 提交结果
 */
export function submitKnowledgeAssessment(data: KnowledgeAssessmentSubmitPayload): Promise<unknown> {
  return request.post('/api/student/assessments/initial/knowledge/submit', data)
}

/**
 * 轮询获取知识测评结果（含异步生成状态）
 * 后端提交后异步生成学习路径/画像/报告，前端通过此接口轮询获取完整结果
 * @param {number} courseId - 课程ID
 * @returns {Promise} 评测结果 + generating状态
 */
export function getKnowledgeResult(courseId: number): Promise<unknown> {
  return request.get('/api/student/assessments/initial/knowledge/result', {
    params: { course_id: courseId }
  })
}

/**
 * 生成学习者画像
 * 基于学生的初测数据（能力评测、习惯问卷、知识测评）生成学习者画像
 * @param {number} courseId - 课程ID
 * @returns {Promise} 生成结果，可能是异步任务
 */
export function generateProfile(courseId: number): Promise<unknown> {
  return request.post('/api/student/assessments/profile/generate', {
    course_id: courseId
  })
}

/**
 * 重新进行能力评测
 * @param {number} courseId - 课程ID
 * @returns {Promise} 新的评测题目
 */
export function retakeAbilityAssessment(courseId: number): Promise<AssessmentQuestionResponse | AssessmentQuestion[]> {
  return request.get<AssessmentQuestionResponse | AssessmentQuestion[]>('/api/student/assessments/initial/ability/retake', {
    params: { course_id: courseId }
  })
}
