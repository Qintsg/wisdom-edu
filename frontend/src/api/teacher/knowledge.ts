/**
 * 教师端 - 知识图谱管理API
 * 提供知识点、知识关系、资源的管理功能
 */
import request from '../index'

// ==================== 知识点管理 ====================

/**
 * 获取知识点列表
 * @param {number} courseId - 课程ID
 * @param {Object} [params] - 查询参数
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @returns {Promise<Object>} 知识点列表
 */
export function getKnowledgePoints(courseId, params = {}) {
  return request.get('/api/teacher/knowledge-points', {
    params: { course_id: courseId, ...params }
  })
}

/**
 * 获取知识点详情
 * @param {number} pointId - 知识点ID
 * @returns {Promise<Object>} 知识点详情
 */
export function getKnowledgePointDetail(pointId) {
  return request.get(`/api/teacher/knowledge-points/${pointId}`)
}

/**
 * 创建知识点
 * @param {Object} data - 知识点信息
 * @param {number} data.course_id - 课程ID
 * @param {string} data.point_name - 知识点名称
 * @param {string} [data.description] - 知识点描述
 * @param {number} [data.parent_id] - 父知识点ID
 * @param {number} [data.order] - 排序序号
 * @returns {Promise<Object>} 创建结果
 */
export function createKnowledgePoint(data) {
  return request.post('/api/teacher/knowledge-points/create', data)
}

/**
 * 更新知识点
 * @param {number} pointId - 知识点ID
 * @param {Object} data - 更新的知识点信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateKnowledgePoint(pointId, data) {
  return request.put(`/api/teacher/knowledge-points/${pointId}`, data)
}

/**
 * 删除知识点
 * @param {number} pointId - 知识点ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteKnowledgePoint(pointId) {
  return request.delete(`/api/teacher/knowledge-points/${pointId}/delete`)
}

// ==================== 知识关系管理 ====================

/**
 * 获取知识点关系列表
 * @param {number} courseId - 课程ID
 * @returns {Promise<Array>} 知识点关系列表
 */
export function getKnowledgeRelations(courseId) {
  return request.get('/api/teacher/knowledge-relations', {
    params: { course_id: courseId }
  })
}

/**
 * 创建知识点关系
 * @param {Object} data - 关系信息
 * @param {number} data.from_point_id - 源知识点ID
 * @param {number} data.to_point_id - 目标知识点ID
 * @param {string} data.relation_type - 关系类型：prerequisite/related/extends
 * @returns {Promise<Object>} 创建结果
 */
export function createKnowledgeRelation(data) {
  return request.post('/api/teacher/knowledge-relations/create', data)
}

/**
 * 删除知识点关系
 * @param {number} relationId - 关系ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteKnowledgeRelation(relationId) {
  return request.delete(`/api/teacher/knowledge-relations/${relationId}`)
}

// ==================== 知识图谱导入导出 ====================

/**
 * 导入知识图谱
 * 支持Excel/JSON格式文件
 * @param {number} courseId - 课程ID
 * @param {File} file - 知识图谱文件
 * @returns {Promise<Object>} 导入结果
 */
export function importKnowledgeMap(courseId, file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('course_id', courseId)
  return request.post('/api/teacher/knowledge-map/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 批量保存知识图谱（来自可视化编辑器）
 * @param {number} courseId - 课程ID
 * @param {{ nodes: Array, edges: Array }} graphData - 图谱数据
 * @returns {Promise<Object>} 保存结果
 */
export function saveKnowledgeGraph(courseId, graphData) {
  return request.post('/api/teacher/knowledge-map/save', {
    course_id: courseId,
    ...graphData
  })
}

/**
 * 导出知识图谱
 * @param {number} courseId - 课程ID
 * @param {string} [format] - 导出格式：xlsx/json
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportKnowledgeMap(courseId, format = 'xlsx') {
  return request.get('/api/teacher/knowledge-map/export', {
    params: { course_id: courseId, format },
    responseType: 'blob'
  })
}

/**
 * 发布知识图谱到Neo4j
 * 将知识图谱同步到图数据库
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 发布结果
 */
export function publishKnowledgeMap(courseId) {
  return request.post('/api/teacher/knowledge-map/publish', {
    course_id: courseId
  })
}

/**
 * 构建课程 GraphRAG 索引
 * @param {number} courseId - 课程ID
 * @returns {Promise<Object>} 索引构建结果
 */
export function buildKnowledgeRagIndex(courseId) {
  return request.post('/api/teacher/knowledge-map/build-rag-index', {
    course_id: courseId
  })
}

/**
 * 获取知识图谱模板
 * @returns {Promise<Blob>} 模板文件
 */
export function getKnowledgeMapTemplate() {
  return request.get('/api/teacher/knowledge-map/template', {
    responseType: 'blob'
  })
}

// ==================== 资源管理 ====================

/**
 * 获取资源列表
 * @param {Object} params - 查询参数
 * @param {number} params.course_id - 课程ID
 * @param {number} [params.knowledge_point_id] - 知识点ID
 * @param {string} [params.resource_type] - 资源类型：video/document/link/exercise
 * @returns {Promise<Object>} 资源列表
 */
export function getResources(params) {
  return request.get('/api/teacher/resources', { params })
}

/**
 * 获取资源详情
 * @param {number} resourceId - 资源ID
 * @returns {Promise<Object>} 资源详情
 */
export function getResourceDetail(resourceId) {
  return request.get(`/api/teacher/resources/${resourceId}`)
}

/**
 * 创建资源
 * @param {Object} data - 资源信息
 * @param {number} data.course_id - 课程ID
 * @param {string} data.resource_name - 资源名称
 * @param {string} data.resource_type - 资源类型：video/document/link/exercise
 * @param {string} data.resource_url - 资源URL
 * @param {number} [data.knowledge_point_id] - 关联知识点ID
 * @param {string} [data.description] - 资源描述
 * @param {number} [data.duration] - 时长（分钟，视频资源）
 * @returns {Promise<Object>} 创建结果
 */
export function createResource(data) {
  return request.post('/api/teacher/resources/create', data)
}

/**
 * 上传资源文件
 * @param {File} file - 资源文件
 * @param {Function} [onProgress] - 上传进度回调
 * @returns {Promise<Object>} 上传结果，包含文件URL
 */
export function uploadResource(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/teacher/resources/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
  })
}

/**
 * 更新资源
 * @param {number} resourceId - 资源ID
 * @param {Object} data - 更新的资源信息
 * @returns {Promise<Object>} 更新结果
 */
export function updateResource(resourceId, data) {
  return request.put(`/api/teacher/resources/${resourceId}`, data)
}

/**
 * 删除资源
 * @param {number} resourceId - 资源ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteResource(resourceId) {
  return request.delete(`/api/teacher/resources/${resourceId}/delete`)
}

/**
 * 关联资源到知识点
 * @param {number} resourceId - 资源ID
 * @param {number} knowledgePointId - 知识点ID
 * @returns {Promise<Object>} 关联结果
 */
export function linkResourceToKnowledge(resourceId, knowledgePointId) {
  return request.post(`/api/teacher/resources/${resourceId}/link-knowledge`, {
    knowledge_point_id: knowledgePointId
  })
}
