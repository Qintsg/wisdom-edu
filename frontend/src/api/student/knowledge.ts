/**
 * 学生端 - 知识图谱相关API
 * 管理知识结构、知识点、掌握度等
 */
import request from '../index'

/**
 * 获取知识图谱
 * 返回课程的完整知识图谱结构和学生的掌握情况
 * @param {number} courseId - 课程ID
 * @returns {Promise} 知识图谱数据，包含节点和边的关系
 */
export function getKnowledgeMap(courseId) {
  return request.get('/api/student/knowledge-map', {
    params: { course_id: courseId }
  })
}

/**
 * 获取知识点列表
 * 返回课程中的所有知识点及其掌握度信息
 * @param {number} courseId - 课程ID
 * @param {Object} [params] - 可选筛选条件
 * @param {string} [params.status] - 筛选状态（mastered/learning/unknown）
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * @returns {Promise} 知识点列表
 */
export function getKnowledgePoints(courseId, params = {}) {
  return request.get('/api/student/knowledge/points', {
    params: { course_id: courseId, ...params }
  })
}

/**
 * 获取知识点详情
 * 返回特定知识点的详细信息、学习资源、相关题目等
 * @param {number} pointId - 知识点ID
 * @param {number} courseId - 课程ID
 * @returns {Promise} 知识点详情
 */
export function getKnowledgePointDetail(pointId, courseId) {
  return request.get(`/api/student/knowledge-points/${pointId}`, {
    params: { course_id: courseId }
  })
}

/**
 * 获取知识点关系
 * 返回知识点之间的依赖关系和关联关系
 * @param {number} courseId - 课程ID
 * @returns {Promise} 知识点关系图
 */
export function getKnowledgeRelations(courseId) {
  return request.get('/api/student/knowledge/relations', {
    params: { course_id: courseId }
  })
}

/**
 * 获取知识点掌握度
 * 返回学生对各知识点的掌握度评分
 * @param {number} courseId - 课程ID
 * @returns {Promise} 掌握度数据
 */
export function getKnowledgeMastery(courseId) {
  return request.get('/api/student/knowledge/mastery', {
    params: { course_id: courseId }
  })
}

/**
 * 更新知识点掌握度
 * 学生手动更新对某个知识点的掌握情况
 * @param {number} courseId - 课程ID
 * @param {number} pointId - 知识点ID
 * @param {number} mastery - 掌握度（0-100）
 * @returns {Promise} 更新结果
 */
export function updateKnowledgeMastery(courseId, pointId, mastery) {
  return request.put('/api/student/knowledge/mastery/update', {
    course_id: courseId,
    point_id: pointId,
    mastery
  })
}

/**
 * 获取知识点的学习资源
 * 返回与知识点相关的学习材料、视频等
 * @param {number} pointId - 知识点ID
 * @param {number} courseId - 课程ID
 * @returns {Promise} 学习资源列表
 */
export function getPointResources(pointId, courseId) {
  return request.get(`/api/student/knowledge-points/${pointId}/resources`, {
    params: { course_id: courseId }
  })
}

/**
 * 获取课程学习资源列表
 * @param {Object} params - 查询参数
 * @param {number} params.course_id - 课程ID
 * @param {string} [params.type] - 资源类型
 * @param {string} [params.keyword] - 搜索关键词
 * @param {number} [params.point_id] - 知识点ID
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * @returns {Promise} 资源列表
 */
export function getStudentResources(params) {
  return request.get('/api/student/resources', { params })
}

/**
 * 搜索知识点
 * @param {number} courseId - 课程ID
 * @param {string} keyword - 搜索关键词
 * @returns {Promise} 搜索结果
 */
export function searchKnowledgePoints(courseId, keyword) {
  return request.get('/api/student/knowledge/search', {
    params: { course_id: courseId, keyword }
  })
}
