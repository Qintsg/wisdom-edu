<template>
  <div class="knowledge-map-view fade-in-up">
    <el-card class="map-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>知识图谱</span>
          <div class="header-actions">
            <el-button-group>
              <el-button :type="viewMode === 'graph' ? 'primary' : ''" @click="viewMode = 'graph'">
                图谱视图
              </el-button>
              <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'">
                列表视图
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 图谱视图 -->
      <div v-else-if="viewMode === 'graph'" class="graph-container">
        <KnowledgeGraphECharts v-if="graphData.nodes.length" :data="graphData" :height="'calc(100vh - 220px)'"
          mode="view" :courseId="courseStore.courseId" :showDrawer="false" @node-click="handleNodeClick" />
        <el-empty v-else description="暂无知识图谱数据" />
      </div>

      <!-- 列表视图 -->
      <div v-else class="list-container">
        <el-tree :data="knowledgeTree" :props="{ label: 'labelText', children: 'children' }" node-key="treeId"
          default-expand-all>
          <template #default="{ node, data }">
            <div class="tree-node" @click="handleTreeNodeClick(data)">
              <span>{{ node.label }}</span>
              <el-progress :percentage="data.masteryPercent || 0" :stroke-width="6"
                :format="(percentage) => `${percentage}%`" style="width: 100px; margin-left: 16px;" />
            </div>
          </template>
        </el-tree>
      </div>
    </el-card>

    <!-- 知识点详情抽屉 -->
    <el-drawer v-model="drawerVisible" :title="selectedPoint?.pointName || '知识点详情'" direction="rtl" size="400px">
      <div v-if="selectedPoint" class="point-detail">
        <div class="detail-section">
          <h4>掌握程度</h4>
          <el-progress :percentage="Math.round((selectedPoint.masteryRate || 0) * 100)" :stroke-width="12"
            :color="getMasteryColor(selectedPoint.masteryRate)" />
        </div>

        <div v-if="selectedPoint.tagList.length || selectedPoint.cognitiveDimensionText || selectedPoint.categoryText"
          class="detail-section">
          <h4>属性信息</h4>
          <div class="point-attrs">
            <el-tag v-if="selectedPoint.cognitiveDimensionText" size="small" type="warning">{{
              selectedPoint.cognitiveDimensionText }}</el-tag>
            <el-tag v-if="selectedPoint.categoryText" size="small" type="success">{{ selectedPoint.categoryText
              }}</el-tag>
            <el-tag v-for="tagText in selectedPoint.tagList" :key="tagText" size="small" type="info">{{ tagText
              }}</el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.teachingGoalText" class="detail-section">
          <h4>教学目标</h4>
          <p>{{ selectedPoint.teachingGoalText }}</p>
        </div>

        <div class="detail-section">
          <h4>概念描述</h4>
          <p>{{ selectedPoint.descriptionText || '暂无描述' }}</p>
        </div>

        <div v-if="selectedPoint.graphRagSummary || selectedPoint.graphRagSourceList.length" class="detail-section">
          <h4>GraphRAG 证据</h4>
          <p>{{ selectedPoint.graphRagSummary || '当前知识点暂无额外图谱证据摘要。' }}</p>
          <div v-if="selectedPoint.graphRagSourceList.length" class="point-tags evidence-tags">
            <el-tag v-for="sourceItem in selectedPoint.graphRagSourceList" :key="sourceItem.sourceKey" size="small"
              type="success">
              {{ sourceItem.sourceTitle }}
            </el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.prerequisiteList.length" class="detail-section">
          <h4>前置知识</h4>
          <div class="point-tags">
            <el-tag v-for="relatedPoint in selectedPoint.prerequisiteList" :key="relatedPoint.pointId" size="small"
              type="info" class="clickable-tag" @click="loadPointDetail(relatedPoint.pointId)">
              {{ relatedPoint.pointName }}
            </el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.postrequisiteList.length" class="detail-section">
          <h4>后续知识</h4>
          <div class="point-tags">
            <el-tag v-for="relatedPoint in selectedPoint.postrequisiteList" :key="relatedPoint.pointId" size="small"
              class="clickable-tag" @click="loadPointDetail(relatedPoint.pointId)">
              {{ relatedPoint.pointName }}
            </el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.resourceList.length" class="detail-section">
          <h4>相关资源</h4>
          <div class="resource-list">
            <div v-for="resourceItem in selectedPoint.resourceList" :key="resourceItem.resourceId" class="resource-item"
              @click="openResource(resourceItem)">
              <el-icon>
                <VideoPlay v-if="resourceItem.resourceType === 'video'" />
                <Document v-else-if="resourceItem.resourceType === 'document'" />
                <Edit v-else />
              </el-icon>
              <span class="resource-title">{{ resourceItem.resourceTitle }}</span>
              <span v-if="resourceItem.durationText" class="resource-duration">{{ resourceItem.durationText }}</span>
            </div>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="primary" @click="goToLearning">
            开始学习
          </el-button>
        </div>
      </div>
    </el-drawer>

  </div>
</template>

<script setup>
/**
 * 知识图谱视图
 * 使用D3.js渲染交互式知识图谱，支持节点点击查看详情
 */
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, Document, Edit } from '@element-plus/icons-vue'
import KnowledgeGraphECharts from '@/components/knowledge/KnowledgeGraphECharts.vue'
import { toBackendAbsoluteUrl } from '@/api/backend'
import { useCourseStore } from '@/stores/course'
import { getKnowledgeMap, getKnowledgePointDetail } from '@/api/student/knowledge'

/**
 * 统一收敛文本字段，避免模板直接依赖动态 payload。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return String(rawValue)
  }
  return ''
}

/**
 * 统一收敛标识符字段，页面层只消费稳定字符串 ID。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  const normalizedText = normalizeText(rawValue)
  return normalizedText ? normalizedText : ''
}

/**
 * 统一收敛数值字段，避免百分比和排序出现 NaN。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 将掌握度规范到 0~1 区间。
 * @param {unknown} rawValue
 * @returns {number}
 */
const normalizeRate = (rawValue) => {
  const parsedValue = Number(rawValue)

  if (!Number.isFinite(parsedValue)) {
    return 0
  }

  if (parsedValue > 1) {
    return Math.min(parsedValue / 100, 1)
  }

  return Math.max(parsedValue, 0)
}

/**
 * 将任意 payload 收敛为数组，减少模板防御性判断。
 * @param {unknown} rawValue
 * @returns {Array<Record<string, unknown>>}
 */
const normalizeListFromPayload = (rawValue) => {
  return Array.isArray(rawValue) ? rawValue : []
}

/**
 * 将标签文本收敛为稳定数组，避免模板里 split/trim 直接操作动态值。
 * @param {unknown} rawValue
 * @returns {string[]}
 */
const normalizeTagList = (rawValue) => {
  return normalizeText(rawValue)
    .split(',')
    .map((tagText) => normalizeText(tagText).replace(/^\s+|\s+$/g, ''))
    .filter(Boolean)
}

/**
 * @typedef {Object} KnowledgeNodeModel
 * @property {string} nodeId
 * @property {string} pointId
 * @property {string} pointName
 * @property {number} masteryRate
 * @property {string} chapterText
 * @property {string} nodeDescription
 * @property {string} tagsText
 * @property {string} cognitiveDimensionText
 * @property {string} categoryText
 * @property {string} teachingGoalText
 */

/**
 * @typedef {Object} KnowledgeEdgeModel
 * @property {string} edgeId
 * @property {string} sourceNodeId
 * @property {string} targetNodeId
 * @property {string} relationTypeText
 */

/**
 * @typedef {Object} KnowledgeTreeNodeModel
 * @property {string} treeId
 * @property {string} labelText
 * @property {string} pointId
 * @property {number} masteryPercent
 * @property {KnowledgeTreeNodeModel[]} children
 */

/**
 * 构造默认图谱节点模型。
 * @returns {KnowledgeNodeModel}
 */
const buildDefaultKnowledgeNode = () => ({
  nodeId: '',
  pointId: '',
  pointName: '',
  masteryRate: 0,
  chapterText: '',
  nodeDescription: '',
  tagsText: '',
  cognitiveDimensionText: '',
  categoryText: '',
  teachingGoalText: ''
})

/**
 * 将知识图谱节点统一映射为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawNode
 * @returns {KnowledgeNodeModel}
 */
const normalizeKnowledgeNode = (rawNode) => ({
  ...buildDefaultKnowledgeNode(),
  nodeId: normalizeIdentifier(rawNode?.id ?? rawNode?.point_id),
  pointId: normalizeIdentifier(rawNode?.point_id ?? rawNode?.id),
  pointName: normalizeText(rawNode?.point_name ?? rawNode?.name) || '未命名知识点',
  masteryRate: normalizeRate(rawNode?.mastery_rate ?? rawNode?.mastery),
  chapterText: normalizeText(rawNode?.chapter),
  nodeDescription: normalizeText(rawNode?.description),
  tagsText: normalizeText(rawNode?.tags),
  cognitiveDimensionText: normalizeText(rawNode?.cognitive_dimension),
  categoryText: normalizeText(rawNode?.category),
  teachingGoalText: normalizeText(rawNode?.teaching_goal)
})

/**
 * 构造默认图谱边模型。
 * @returns {KnowledgeEdgeModel}
 */
const buildDefaultKnowledgeEdge = () => ({
  edgeId: '',
  sourceNodeId: '',
  targetNodeId: '',
  relationTypeText: 'prerequisite'
})

/**
 * 将知识关系统一映射为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawEdge
 * @returns {KnowledgeEdgeModel}
 */
const normalizeKnowledgeEdge = (rawEdge) => {
  const sourceNodeId = normalizeIdentifier(rawEdge?.source ?? rawEdge?.source_id ?? rawEdge?.from_point_id)
  const targetNodeId = normalizeIdentifier(rawEdge?.target ?? rawEdge?.target_id ?? rawEdge?.to_point_id)

  return {
    ...buildDefaultKnowledgeEdge(),
    edgeId: normalizeIdentifier(rawEdge?.id ?? rawEdge?.edge_id) || `${sourceNodeId}-${targetNodeId}`,
    sourceNodeId,
    targetNodeId,
    relationTypeText: normalizeText(rawEdge?.relation_type) || 'prerequisite'
  }
}

/**
 * 统一收敛相关知识点标签模型。
 * @param {Record<string, unknown> | null | undefined} rawPoint
 * @returns {{ pointId: string, pointName: string }}
 */
const normalizeRelatedKnowledgePoint = (rawPoint) => ({
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点'
})

/**
 * 统一收敛资源信息，抽屉只消费 camelCase 字段。
 * @param {Record<string, unknown> | null | undefined} rawResource
 * @returns {{ resourceId: string, resourceTitle: string, resourceType: string, resourceUrl: string, durationText: string }}
 */
const normalizeKnowledgeResource = (rawResource) => ({
  resourceId: normalizeIdentifier(rawResource?.resource_id ?? rawResource?.id),
  resourceTitle: normalizeText(rawResource?.title ?? rawResource?.resource_name) || '未命名资源',
  resourceType: normalizeText(rawResource?.type ?? rawResource?.resource_type) || 'link',
  resourceUrl: toBackendAbsoluteUrl(normalizeText(rawResource?.url ?? rawResource?.resource_url)),
  durationText: normalizeText(rawResource?.duration_display)
})

/**
 * 统一收敛 GraphRAG 证据来源。
 * @param {unknown} rawSource
 * @returns {{ sourceKey: string, sourceTitle: string, sourceKind: string }}
 */
const normalizeGraphRagSource = (rawSource) => {
  if (!rawSource || typeof rawSource === 'string') {
    const sourceTitle = normalizeText(rawSource) || '课程证据'
    return {
      sourceKey: sourceTitle,
      sourceTitle,
      sourceKind: 'document'
    }
  }

  const sourceKind = normalizeText(rawSource.kind) || 'document'
  const sourceTitle = normalizeText(rawSource.title ?? rawSource.label) || sourceKind || '课程证据'
  return {
    sourceKey: `${normalizeIdentifier(rawSource.id) || sourceTitle}-${sourceKind}`,
    sourceTitle,
    sourceKind
  }
}

/**
 * 构造默认知识点详情模型。
 * @returns {{ pointId: string, pointName: string, descriptionText: string, masteryRate: number, tagList: string[], cognitiveDimensionText: string, categoryText: string, teachingGoalText: string, graphRagSummary: string, graphRagSourceList: Array<{sourceKey: string, sourceTitle: string, sourceKind: string}>, prerequisiteList: Array<{pointId: string, pointName: string}>, postrequisiteList: Array<{pointId: string, pointName: string}>, resourceList: Array<{resourceId: string, resourceTitle: string, resourceType: string, resourceUrl: string, durationText: string}> }}
 */
const buildDefaultPointDetail = () => ({
  pointId: '',
  pointName: '',
  descriptionText: '',
  masteryRate: 0,
  tagsText: '',
  tagList: [],
  cognitiveDimensionText: '',
  categoryText: '',
  teachingGoalText: '',
  graphRagSummary: '',
  graphRagSourceList: [],
  prerequisiteList: [],
  postrequisiteList: [],
  resourceList: []
})

/**
 * 将知识点详情统一收敛为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawDetail
 * @returns {ReturnType<typeof buildDefaultPointDetail>}
 */
const normalizePointDetail = (rawDetail) => {
  const tagsText = normalizeText(rawDetail?.tags)

  return {
    ...buildDefaultPointDetail(),
    pointId: normalizeIdentifier(rawDetail?.point_id ?? rawDetail?.id),
    pointName: normalizeText(rawDetail?.point_name ?? rawDetail?.name) || '未命名知识点',
    descriptionText: normalizeText(rawDetail?.description),
    masteryRate: normalizeRate(rawDetail?.mastery_rate),
    tagsText,
    tagList: normalizeTagList(tagsText),
    cognitiveDimensionText: normalizeText(rawDetail?.cognitive_dimension),
    categoryText: normalizeText(rawDetail?.category),
    teachingGoalText: normalizeText(rawDetail?.teaching_goal),
    graphRagSummary: normalizeText(rawDetail?.graph_rag_summary),
    graphRagSourceList: normalizeListFromPayload(rawDetail?.graph_rag_sources)
      .map((sourceItem) => normalizeGraphRagSource(sourceItem)),
    prerequisiteList: normalizeListFromPayload(rawDetail?.prerequisites)
      .map((relatedPoint) => normalizeRelatedKnowledgePoint(relatedPoint)),
    postrequisiteList: normalizeListFromPayload(rawDetail?.postrequisites)
      .map((relatedPoint) => normalizeRelatedKnowledgePoint(relatedPoint)),
    resourceList: normalizeListFromPayload(rawDetail?.resources)
      .map((resourceItem) => normalizeKnowledgeResource(resourceItem))
  }
}

/**
 * 构建树形知识点列表，列表视图只消费内部树节点模型。
 * @param {KnowledgeNodeModel[]} allKnowledgeNodes
 * @returns {KnowledgeTreeNodeModel[]}
 */
const buildKnowledgeTree = (allKnowledgeNodes) => {
  const chapterMap = new Map()

  allKnowledgeNodes.forEach((knowledgeNode) => {
    const chapterText = knowledgeNode.chapterText || '其他'

    if (!chapterMap.has(chapterText)) {
      chapterMap.set(chapterText, {
        treeId: `chapter-${chapterText}`,
        labelText: chapterText,
        pointId: '',
        masteryPercent: 0,
        children: []
      })
    }

    chapterMap.get(chapterText).children.push({
      treeId: `point-${knowledgeNode.pointId}`,
      labelText: knowledgeNode.pointName,
      pointId: knowledgeNode.pointId,
      masteryPercent: Math.round(knowledgeNode.masteryRate * 100),
      children: []
    })
  })

  return [...chapterMap.values()].map((chapterNode) => {
    const childCount = chapterNode.children.length
    const chapterMasteryTotal = chapterNode.children.reduce((masterySum, childNode) => {
      return masterySum + childNode.masteryPercent
    }, 0)

    return {
      ...chapterNode,
      masteryPercent: childCount ? Math.round(chapterMasteryTotal / childCount) : 0
    }
  })
}

const router = useRouter()
const courseStore = useCourseStore()

// 状态
const loading = ref(true)
const viewMode = ref('graph')
const drawerVisible = ref(false)
const selectedPoint = ref(null)

// 图谱数据
const knowledgeNodes = ref([])
const knowledgeEdges = ref([])

// 图谱组件继续接收通用 nodes / edges 结构，但全部来自内部模型映射。
const graphData = computed(() => {
  return {
    nodes: knowledgeNodes.value.map((knowledgeNode) => ({
      id: knowledgeNode.nodeId,
      pointId: knowledgeNode.pointId,
      name: knowledgeNode.pointName,
      chapter: knowledgeNode.chapterText,
      description: knowledgeNode.nodeDescription,
      masteryRate: knowledgeNode.masteryRate,
      mastery_rate: knowledgeNode.masteryRate
    })),
    edges: knowledgeEdges.value.map((knowledgeEdge) => ({
      source: knowledgeEdge.sourceNodeId,
      target: knowledgeEdge.targetNodeId,
      label: knowledgeEdge.relationTypeText,
      relation_type: knowledgeEdge.relationTypeText
    }))
  }
})

// 列表树数据（由节点构建）
const knowledgeTree = ref([])

/**
 * 获取掌握度颜色
 */
const getMasteryColor = (rate) => {
  if (!rate || rate === 0) return '#7a8d87'
  if (rate >= 0.8) return '#22a06b'
  if (rate >= 0.6) return '#dd8f1d'
  return '#d45050'
}

/**
 * 加载知识图谱数据
 */
const fetchKnowledgeMap = async () => {
  // 检查课程ID
  if (!courseStore.courseId) {
    ElMessage.warning('请先选择课程')
    await router.push('/student/course-select')
    return
  }

  loading.value = true
  try {
    const rawKnowledgeMapPayload = await getKnowledgeMap(courseStore.courseId)
    const knowledgeMapPayload = rawKnowledgeMapPayload?.data || rawKnowledgeMapPayload
    knowledgeNodes.value = normalizeListFromPayload(knowledgeMapPayload?.nodes)
      .map((rawNode) => normalizeKnowledgeNode(rawNode))
    knowledgeEdges.value = normalizeListFromPayload(knowledgeMapPayload?.edges)
      .map((rawEdge) => normalizeKnowledgeEdge(rawEdge))
    knowledgeTree.value = buildKnowledgeTree(knowledgeNodes.value)
  } catch (error) {
    console.error('获取知识图谱失败:', error)
    ElMessage.error('获取知识图谱失败')
  } finally {
    loading.value = false
  }
}

/**
 * 处理节点点击
 */
const handleNodeClick = async (clickedNode) => {
  const pointId = normalizeIdentifier(clickedNode?.pointId ?? clickedNode?.point_id ?? clickedNode?.id)

  if (pointId) {
    await loadPointDetail(pointId)
  }
}

/**
 * 处理树节点点击
 */
const handleTreeNodeClick = async (treeNode) => {
  if (treeNode.pointId) {
    await loadPointDetail(treeNode.pointId)
  }
}

/**
 * 加载知识点详情
 */
const loadPointDetail = async (pointId) => {
  try {
    const rawPointDetail = await getKnowledgePointDetail(pointId, courseStore.courseId)
    selectedPoint.value = normalizePointDetail(rawPointDetail)
    drawerVisible.value = true
  } catch (error) {
    console.error('获取知识点详情失败:', error)
    ElMessage.error('获取知识点详情失败')
  }
}

/**
 * 打开资源
 */
const openResource = (resourceItem) => {
  if (resourceItem.resourceUrl) {
    window.open(resourceItem.resourceUrl, '_blank')
  } else {
    ElMessage.info('资源暂不可用')
  }
}

/**
 * 前往学习
 */
const goToLearning = async () => {
  if (selectedPoint.value?.pointId) {
    await router.push({
      name: 'LearningPath',
      query: { pointId: selectedPoint.value.pointId }
    })
    drawerVisible.value = false
  }
}

onMounted(() => {
  fetchKnowledgeMap()
})
</script>

<style scoped>
.knowledge-map-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.map-card {
  flex: 1;
  animation: fadeInUp 0.42s ease-out;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 加载状态 */
.loading-container {
  padding: 40px;
}

/* 图谱容器 */
.graph-container {
  min-height: 500px;
}

/* 列表容器 */
.list-container {
  padding: 10px 0;
}

.tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  cursor: pointer;
}

.tree-node:hover {
  color: var(--primary-color);
}

.evidence-tags {
  margin-top: 12px;
}

/* 详情抽屉 */
.point-detail {
  padding: 0 20px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px;
}

.detail-section p {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin: 0;
}

.point-attrs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.point-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.clickable-tag {
  cursor: pointer;
}

.clickable-tag:hover {
  opacity: 0.8;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(37, 99, 235, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: transform var(--transition-base), background var(--transition-base), box-shadow var(--transition-base);
}

.resource-item:hover {
  background: rgba(37, 99, 235, 0.12);
  color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.resource-item .el-icon {
  font-size: 18px;
}

.resource-title {
  font-size: 13px;
  flex: 1;
}

.resource-duration {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.detail-actions {
  margin-top: 32px;
  text-align: center;
}

/* 图例 */
.legend-items {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
</style>
