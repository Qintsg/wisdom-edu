/**
 * 学生端 - 学习路径相关API
 * 管理个性化学习路径、学习节点、资源完成情况等
 */
import request from '../index'

/**
 * 获取学习路径
 * 返回为学生生成的个性化学习路径
 * @param {number} courseId - 课程ID
 * @returns {Promise} 学习路径信息，包括所有节点和建议顺序
 */
export function getLearningPath(courseId) {
  return request.get('/api/student/learning-path', {
    params: { course_id: courseId }
  })
}

/**
 * 调整学习路径
 * 学生可以手动调整路径，改变学习顺序或选择不同分支
 * @param {Object} data
 * @param {number} data.course_id - 课程ID
 * @param {Array<number>} data.node_ids - 调整后的节点顺序
 * @returns {Promise} 调整结果
 */
export function adjustLearningPath(data) {
  return request.post('/api/student/learning-path/adjust', data)
}

/**
 * 获取路径节点详情
 * 返回特定学习节点的详细信息
 * @param {number} nodeId - 路径节点ID
 * @param {number} [courseId] - 课程ID，用于按当前课程上下文获取节点详情
 * @returns {Promise} 节点详情，包含学习资源、测验等
 */
export function getPathNodeDetail(nodeId, courseId) {
  return request.get(`/api/student/path-nodes/${nodeId}`, {
    params: courseId ? { course_id: courseId } : {}
  })
}

/**
 * 开始学习节点
 * 标记节点为进行中状态
 * @param {number} nodeId - 路径节点ID
 * @param {number} [courseId] - 课程ID，用于记录当前课程下的学习进度
 * @returns {Promise} 开始结果
 */
export function startLearningNode(nodeId, courseId) {
  return request.post(`/api/student/path-nodes/${nodeId}/start`, courseId ? { course_id: courseId } : {})
}

/**
 * 完成资源学习
 * 标记节点中的某个学习资源为已完成
 * @param {number} nodeId - 路径节点ID
 * @param {number} resourceId - 资源ID
 * @param {number} [courseId] - 课程ID，用于同步当前课程的资源完成状态
 * @returns {Promise} 完成结果
 */
export function completeResource(nodeId, resourceId, courseId) {
  return request.post(`/api/student/path-nodes/${nodeId}/resources/${resourceId}/complete`, courseId ? { course_id: courseId } : {})
}

/**
 * 暂停资源学习
 * 标记资源学习为暂停状态
 * @param {number} nodeId - 路径节点ID
 * @param {number} resourceId - 资源ID
 * @returns {Promise} 暂停结果
 */
export function pauseResource(nodeId, resourceId) {
  return request.post(`/api/student/path-nodes/${nodeId}/resources/${resourceId}/pause`)
}

/**
 * 获取节点中的资源列表
 * @param {number} nodeId - 路径节点ID
 * @param {number} [courseId] - 课程ID，用于按课程上下文筛选资源
 * @returns {Promise} 资源列表
 */
export function getNodeResources(nodeId, courseId) {
  return request.get(`/api/student/path-nodes/${nodeId}/resources`, {
    params: courseId ? { course_id: courseId } : {}
  })
}

/**
 * 获取节点的AI推荐资源（异步加载）
 * 返回DB资源的AI推荐理由和外部AI推荐资源
 * @param {number} nodeId - 路径节点ID
 * @returns {Promise<{ai_reasons: Object, external_resources: Array}>}
 */
export function getAIResources(nodeId) {
  return request.get(`/api/student/path-nodes/${nodeId}/ai-resources`, {
    timeout: 90000
  })
}

/**
 * 提交节点测验
 * 学生完成节点中的测验并提交答案
 * @param {number} nodeId - 路径节点ID
 * @param {number} examId - 考试/测验ID
 * @param {Object} data - 考试答案数据
 * @returns {Promise} 提交结果
 */
export function submitNodeExam(nodeId, examId, data) {
  return request.post(`/api/student/path-nodes/${nodeId}/exams/${examId}/submit`, data)
}

/**
 * 获取节点的测验列表
 * @param {number} nodeId - 路径节点ID
 * @param {number} [courseId] - 课程ID，用于获取当前课程中的节点测验
 * @returns {Promise} 测验列表
 */
export function getNodeExams(nodeId, courseId) {
  return request.get(`/api/student/path-nodes/${nodeId}/exams`, {
    params: courseId ? { course_id: courseId } : {}
  })
}

/**
 * 完成学习节点
 * 标记整个节点为已完成状态
 * @param {number} nodeId - 路径节点ID
 * @param {number} [courseId] - 课程ID，用于更新当前课程下的节点完成状态
 * @returns {Promise} 完成结果
 */
export function completePathNode(nodeId, courseId) {
  return request.post(`/api/student/path-nodes/${nodeId}/complete`, courseId ? { course_id: courseId } : {})
}

/**
 * 跳过学习节点
 * 学生可以选择跳过某个节点
 * @param {number} nodeId - 路径节点ID
 * @param {string} [reason] - 跳过原因
 * @param {number} [courseId] - 课程ID，用于记录当前课程内的跳过行为
 * @returns {Promise} 跳过结果
 */
export function skipPathNode(nodeId, reason, courseId) {
  return request.post(`/api/student/path-nodes/${nodeId}/skip`, {
    reason,
    ...(courseId ? { course_id: courseId } : {})
  })
}

/**
 * 获取学习进度
 * 返回课程的整体学习进度
 * @param {number} courseId - 课程ID
 * @returns {Promise} 进度信息
 */
export function getLearningProgress(courseId) {
  return request.get('/api/student/learning-progress', {
    params: { course_id: courseId }
  })
}

/**
 * AI主动刷新学习路径
 * 调用KT服务更新知识掌握度，然后使用LLM结合能力评测和习惯偏好重新规划路径
 * @param {number} courseId - 课程ID
 * @returns {Promise} 刷新后的学习路径数据
 */
export function refreshLearningPathWithAI(courseId) {
  return request.post('/api/student/ai/refresh-learning-path', {
    course_id: courseId
  }, {
    timeout: 180000 // LLM调用耗时较长，设置3分钟超时
  })
}

/**
 * 获取阶段测试题目
 * 阶段测试节点嵌入式做题，不跳转考试页面
 * @param {number} nodeId - 路径节点ID（test类型节点）
 * @returns {Promise<{questions: Array, title: string, pass_score: number}>} 测试题目
 */
export function getStageTest(nodeId) {
  return request.get(`/api/student/path-nodes/${nodeId}/stage-test`)
}

/**
 * 提交阶段测试答案
 * @param {number} nodeId - 路径节点ID
 * @param {Object} data - 答案数据
 * @param {Object.<string, string>} data.answers - 答案字典 {question_id: answer}
 * @returns {Promise<{score: number, passed: boolean, total: number, correct: number}>} 测试结果
 */
export function submitStageTest(nodeId, data) {
  return request.post(`/api/student/path-nodes/${nodeId}/stage-test/submit`, data)
}
