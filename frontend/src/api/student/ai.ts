/**
 * 学生端 - AI服务相关API
 * AI画像分析、路径规划、资源推荐理由、反馈报告、知识追踪等
 * 所有AI服务均集成KT知识追踪和LLM大模型，并结合能力评测与习惯问卷结果
 */
import request from '../index'
import { buildBackendWebSocketUrl } from '../backend'

/**
 * 获取AI画像分析
 * 集成KT服务细化掌握度 + LLM服务深度分析
 * 结合能力评测结果和习惯问卷结果
 * @param {number} courseId - 课程ID
 * @param {boolean} [refresh=false] - 是否强制刷新
 * @returns {Promise} AI分析结果，包括summary/weakness/strength/suggestion/kt_enhanced
 */
export function getAIProfileAnalysis(courseId, refresh = false) {
  return request.post('/api/student/ai/profile-analysis', {
    course_id: courseId,
    refresh
  })
}

/**
 * 获取AI学习路径规划
 * AI结合掌握度、能力评测和习惯偏好为学生规划个性化学习路径
 * @param {number} courseId - 课程ID
 * @param {string} [target] - 学习目标
 * @param {Object} [constraints] - 约束条件
 * @returns {Promise} AI路径规划结果
 */
export function getAIPathPlanning(courseId, target = '', constraints = {}) {
  return request.post('/api/student/ai/path-planning', {
    course_id: courseId,
    target,
    constraints
  })
}

/**
 * 获取AI资源推荐理由
 * 返回AI为什么推荐某个学习资源给学生
 * @param {Object} data
 * @param {number} data.resource_id - 资源ID
 * @param {number} data.student_id - 学生ID
 * @param {number} [data.point_id] - 知识点ID
 * @returns {Promise} 推荐理由解释
 */
export function getAIResourceReason(data) {
  return request.post('/api/student/ai/resource-reason', data)
}

/**
 * 获取AI生成的反馈报告
 * AI基于考试成绩、KT预测、能力评测和习惯数据生成个性化反馈报告
 * @param {Object} data
 * @param {number} data.exam_id - 考试ID
 * @param {number} data.student_id - 学生ID
 * @param {boolean} [data.include_next_tasks=true] - 是否包含后续任务
 * @returns {Promise} 反馈报告内容（含KT分析、能力和习惯上下文）
 */
export function getAIFeedbackReport(data) {
  return request.post('/api/student/ai/feedback-report', data)
}

/**
 * 知识追踪预测
 * AI使用KT模型(DKT+PEBG融合)预测学生对各知识点的掌握概率
 * @param {Object} data
 * @param {number} data.course_id - 课程ID
 * @param {Array} data.answer_history - 答题历史
 * @param {Array<number>} [data.knowledge_points] - 指定知识点IDs
 * @returns {Promise} 预测结果
 */
export function getKnowledgeTracking(data) {
  return request.post('/api/ai/kt/predict', data)
}

/**
 * 获取AI学习建议
 * 结合KT预测、能力评测结果和习惯问卷生成个性化学习建议
 * @param {number} courseId - 课程ID
 * @returns {Promise} 学习建议（含KT洞察、能力评分、习惯偏好）
 */
export function getAILearningAdvice(courseId) {
  return request.post('/api/student/ai/learning-advice', {
    course_id: courseId
  })
}

/**
 * 主动刷新学习画像
 * 调用KT+LLM服务重新生成学习画像
 * @param {number} courseId - 课程ID
 * @returns {Promise} 刷新后的画像数据（含summary/weakness/suggestion/strength/kt_enhanced）
 */
export function refreshProfile(courseId) {
  return request.post('/api/student/ai/refresh-profile', {
    course_id: courseId
  })
}

/**
 * 主动刷新学习路径
 * 调用KT更新掌握度后使用LLM重新规划学习路径
 * @param {number} courseId - 课程ID
 * @returns {Promise} 刷新后的学习路径数据
 */
export function refreshLearningPath(courseId) {
  return request.post('/api/student/ai/refresh-learning-path', {
    course_id: courseId
  })
}

/**
 * 获取AI关键知识点提醒
 * AI识别学生需要重点关注的知识点
 * @param {number} userId - 用户ID
 * @param {number} courseId - 课程ID
 * @returns {Promise} 关键知识点列表和提醒信息
 */
export function getAIKeyPointsReminder(userId, courseId) {
  return request.post('/api/student/ai/key-points-reminder', {
    user_id: userId,
    course_id: courseId
  })
}

/**
 * 获取AI学习时间规划
 * AI根据学生的学习节奏推荐合适的学习时间安排
 * @param {number} userId - 用户ID
 * @param {number} courseId - 课程ID
 * @returns {Promise} 学习时间规划建议
 */
export function getAITimeScheduling(userId, courseId) {
  return request.post('/api/student/ai/time-scheduling', {
    user_id: userId,
    course_id: courseId
  })
}

/**
 * 对比AI分析结果
 * 比较两个不同时期的AI分析结果，查看学习进度变化
 * @param {number} userId - 用户ID
 * @param {number} courseId - 课程ID
 * @param {number} analysisId1 - 第一次分析的ID
 * @param {number} analysisId2 - 第二次分析的ID
 * @returns {Promise} 对比分析数据
 */
export function compareAIAnalysis(userId, courseId, analysisId1, analysisId2) {
  return request.get('/api/student/ai/analysis-compare', {
    params: { user_id: userId, course_id: courseId, analysis_id1: analysisId1, analysis_id2: analysisId2 }
  })
}

/**
 * AI学习对话
 * 与AI助手进行学习相关的对话问答
 * @param {Object} data
 * @param {string} data.message - 用户消息
 * @param {string} [data.knowledge_point] - 当前知识点名称
 * @param {string} [data.course_name] - 当前课程名称
 * @param {Array} [data.history] - 历史对话 [{role, content}, ...]
 * @returns {Promise} { reply: string, mock: boolean }
 */
export function aiChat(data) {
  return request.post('/api/student/ai/chat', data)
}

/**
 * GraphRAG知识图谱检索
 * @param {Object} data
 * @param {number} data.course_id - 课程ID
 * @param {string} data.query - 检索关键词
 * @param {number} [data.limit] - 返回数量上限
 * @returns {Promise} 检索结果与命中知识点
 */
export function searchGraphRAG(data) {
  return request.post('/api/student/ai/graph-rag/search', data)
}

/**
 * GraphRAG知识图谱问答
 * @param {Object} data
 * @param {number} data.course_id - 课程ID
 * @param {string} data.question - 提问内容
 * @param {number} [data.point_id] - 关联知识点ID
 * @returns {Promise} 图谱增强问答结果
 */
export function askGraphRAG(data) {
  return request.post('/api/student/ai/graph-rag/ask', data)
}

/**
 * 创建学生端 AI 助手 WebSocket 连接
 * @returns {WebSocket}
 */
export function createStudentAIChatSocket() {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token') || sessionStorage.getItem('access_token') || sessionStorage.getItem('token')
  const socketUrl = buildBackendWebSocketUrl('/ws/student/ai/chat', token ? { token } : undefined)
  return new WebSocket(socketUrl)
}

/**
 * AI知识点介绍
 * 为当前学习节点生成LLM知识点介绍
 * @param {Object} data
 * @param {string} data.point_name - 知识点名称
 * @param {string} [data.course_name] - 课程名称
 * @returns {Promise} { introduction, key_concepts, learning_tips, difficulty }
 */
export function getAINodeIntro(data) {
  return request.post('/api/student/ai/node-intro', data)
}
