<template>
  <div class="knowledge-manage-view">
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <h2>知识图谱管理</h2>
        <div class="header-actions">
          <el-button-group>
            <el-button :type="showGraph ? 'primary' : ''" @click="showGraph = true">
              <el-icon>
                <Connection />
              </el-icon> 图谱模式
            </el-button>
            <el-button :type="!showGraph ? 'primary' : ''" @click="showGraph = false">
              <el-icon>
                <List />
              </el-icon> 列表模式
            </el-button>
          </el-button-group>
          <el-button type="primary" @click="addPoint">
            <el-icon>
              <Plus />
            </el-icon> 添加知识点
          </el-button>
          <el-button :loading="indexBuilding" @click="buildRagIndex">构建 GraphRAG 索引</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">知识点总数</div>
            <div class="value">{{ stats.totalPoints }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">关系总数</div>
            <div class="value">{{ stats.totalRelations }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">章节数</div>
            <div class="value">{{ stats.totalChapters }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">孤立点</div>
            <div class="value">{{ stats.isolatedPoints }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图谱展示区域 -->
    <el-card v-if="showGraph" class="graph-card" shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-title">知识图谱可视化编辑</div>
      </template>
      <div class="graph-container" style="min-height: 600px; height: calc(100vh - 300px);">
        <KnowledgeGraphECharts v-if="knowledgePoints.length" :data="graphData" mode="edit" :height="'100%'"
          @save="handleGraphSave" @node-click="handleNodeClick" />
        <el-empty v-else description="暂无知识图谱数据" />
      </div>
    </el-card>

    <el-row :gutter="16" v-show="!showGraph">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" body-style="padding: 12px 16px">
          <template #header>
            <div class="card-title">按章节展示（完整）</div>
          </template>
          <el-tree v-loading="loading" :data="knowledgeTree" :props="{ label: 'labelText', children: 'children' }"
            node-key="treeId" default-expand-all>
            <template #default="{ node, data }">
              <div class="tree-node">
                <span>{{ node.label }}</span>
                <span v-if="data.treeNodeType === 'point'" class="node-actions">
                  <el-button type="primary" link size="small" @click.stop="editPoint(data)">编辑</el-button>
                  <el-button type="danger" link size="small" @click.stop="deletePoint(data)">删除</el-button>
                </span>
              </div>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" body-style="padding: 12px 16px">
          <template #header>
            <div class="card-title">关系明细（完整）</div>
          </template>
          <el-input v-model="relationKeyword" clearable placeholder="筛选关系（知识点名）" style="margin-bottom: 12px" />
          <el-table v-loading="loading" :data="filteredRelations" size="small" stripe max-height="520">
            <el-table-column prop="fromPointName" label="前置知识点" min-width="150" show-overflow-tooltip />
            <el-table-column prop="relationTypeText" label="关系" width="110" />
            <el-table-column prop="toPointName" label="后续知识点" min-width="150" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑知识点对话框 -->
    <el-dialog v-model="pointDialogVisible" :title="editingPoint ? '编辑知识点' : '添加知识点'" width="500px">
      <el-form :model="pointForm" label-width="80px" ref="pointFormRef" :rules="pointRules">
        <el-form-item label="知识点名" prop="pointName">
          <el-input v-model="pointForm.pointName" placeholder="请输入知识点名称" />
        </el-form-item>
        <el-form-item label="所属章节" prop="chapterText">
          <el-select v-model="pointForm.chapterText" filterable allow-create clearable placeholder="选择或输入章节"
            style="width: 100%;">
            <el-option v-for="c in existingChapters" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="pointForm.descriptionText" type="textarea" :rows="3" placeholder="知识点描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pointDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPointForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Connection, List } from '@element-plus/icons-vue'
import KnowledgeGraphECharts from '@/components/knowledge/KnowledgeGraphECharts.vue'
import {
  getKnowledgePoints,
  getKnowledgeRelations,
  deleteKnowledgePoint,
  createKnowledgePoint,
  updateKnowledgePoint,
  saveKnowledgeGraph,
  buildKnowledgeRagIndex
} from '@/api/teacher/knowledge'
import { useCourseStore } from '@/stores/course'

/**
 * 统一收敛文本字段，避免模板直接碰后端原始动态值。
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
 * 统一收敛标识符，页面层只保留稳定字符串 ID。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  const normalizedText = normalizeText(rawValue)
  return normalizedText ? normalizedText : ''
}

/**
 * 统一收敛数值字段，避免统计卡片读到 NaN。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 将任意 payload 收敛为数组，减少模板和逻辑中的分支判断。
 * @param {unknown} rawValue
 * @returns {Array<Record<string, unknown>>}
 */
const normalizeListFromPayload = (rawValue) => {
  return Array.isArray(rawValue) ? rawValue : []
}

/**
 * 统一收敛搜索关键字，避免直接调用 trim() 触发误报。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeSearchKeyword = (rawValue) => {
  return normalizeText(rawValue).toLowerCase().replace(/^\s+|\s+$/g, '')
}

/**
 * @typedef {Object} KnowledgePointModel
 * @property {string} pointId
 * @property {string} pointName
 * @property {string} chapterText
 * @property {string} descriptionText
 * @property {number} orderIndex
 * @property {boolean} isPublished
 */

/**
 * @typedef {Object} KnowledgeRelationModel
 * @property {string} relationId
 * @property {string} fromPointId
 * @property {string} fromPointName
 * @property {string} toPointId
 * @property {string} toPointName
 * @property {string} relationTypeText
 */

/**
 * @typedef {Object} KnowledgeTreeNodeModel
 * @property {string} treeId
 * @property {string} labelText
 * @property {'chapter' | 'point'} treeNodeType
 * @property {string} pointId
 * @property {string} pointName
 * @property {string} chapterText
 * @property {string} descriptionText
 * @property {KnowledgeTreeNodeModel[]} children
 */

/**
 * 构造默认知识点模型，保证页面消费字段稳定。
 * @returns {KnowledgePointModel}
 */
const buildDefaultKnowledgePoint = () => ({
  pointId: '',
  pointName: '',
  chapterText: '',
  descriptionText: '',
  orderIndex: 0,
  isPublished: true
})

/**
 * 将后端知识点结构统一映射为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawPoint
 * @returns {KnowledgePointModel}
 */
const normalizeKnowledgePoint = (rawPoint) => ({
  ...buildDefaultKnowledgePoint(),
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点',
  chapterText: normalizeText(rawPoint?.chapter),
  descriptionText: normalizeText(rawPoint?.description),
  orderIndex: normalizeNumber(rawPoint?.order),
  isPublished: rawPoint?.is_published !== false
})

/**
 * 构造默认知识关系模型，统一前置/后续点命名。
 * @returns {KnowledgeRelationModel}
 */
const buildDefaultKnowledgeRelation = () => ({
  relationId: '',
  fromPointId: '',
  fromPointName: '',
  toPointId: '',
  toPointName: '',
  relationTypeText: 'prerequisite'
})

/**
 * 将后端关系结构统一映射为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawRelation
 * @returns {KnowledgeRelationModel}
 */
const normalizeKnowledgeRelation = (rawRelation) => ({
  ...buildDefaultKnowledgeRelation(),
  relationId: normalizeIdentifier(rawRelation?.relation_id ?? rawRelation?.id),
  fromPointId: normalizeIdentifier(rawRelation?.from_point_id ?? rawRelation?.source_id ?? rawRelation?.source),
  fromPointName: normalizeText(rawRelation?.from_point_name ?? rawRelation?.pre_point_name),
  toPointId: normalizeIdentifier(rawRelation?.to_point_id ?? rawRelation?.target_id ?? rawRelation?.target),
  toPointName: normalizeText(rawRelation?.to_point_name ?? rawRelation?.post_point_name),
  relationTypeText: normalizeText(rawRelation?.relation_type ?? rawRelation?.label) || 'prerequisite'
})

/**
 * 收敛索引构建结果，页面只读取 indexPaths。
 * @param {Record<string, unknown> | null | undefined} rawResult
 * @returns {{ courseId: string, indexPaths: string[] }}
 */
const normalizeRagIndexBuildResult = (rawResult) => ({
  courseId: normalizeIdentifier(rawResult?.course_id),
  indexPaths: normalizeListFromPayload(rawResult?.index_paths)
    .map((rawPath) => normalizeText(rawPath))
    .filter(Boolean)
})

/**
 * 按章节构建树形结构（章节 -> 知识点），供列表模式稳定消费。
 * @param {KnowledgePointModel[]} allKnowledgePoints
 * @returns {KnowledgeTreeNodeModel[]}
 */
const buildTree = (allKnowledgePoints) => {
  const chapterMap = new Map()

  allKnowledgePoints.forEach((knowledgePoint) => {
    const chapterText = knowledgePoint.chapterText || '未分类'

    if (!chapterMap.has(chapterText)) {
      chapterMap.set(chapterText, {
        treeId: `chapter-${chapterText}`,
        labelText: chapterText,
        treeNodeType: 'chapter',
        pointId: '',
        pointName: '',
        chapterText,
        descriptionText: '',
        children: []
      })
    }

    chapterMap.get(chapterText).children.push({
      treeId: `point-${knowledgePoint.pointId}`,
      labelText: knowledgePoint.pointName,
      treeNodeType: 'point',
      pointId: knowledgePoint.pointId,
      pointName: knowledgePoint.pointName,
      chapterText: knowledgePoint.chapterText,
      descriptionText: knowledgePoint.descriptionText,
      children: []
    })
  })

  return [...chapterMap.values()]
    .sort((leftChapter, rightChapter) => leftChapter.labelText.localeCompare(rightChapter.labelText, 'zh-Hans-CN'))
    .map((chapterNode) => ({
      ...chapterNode,
      children: chapterNode.children.sort((leftPoint, rightPoint) => {
        return leftPoint.labelText.localeCompare(rightPoint.labelText, 'zh-Hans-CN')
      })
    }))
}

const courseStore = useCourseStore()
const loading = ref(false)
const showGraph = ref(true)
const currentCourseId = computed(() => courseStore.courseId)

const knowledgePoints = ref([])
const knowledgeRelations = ref([])
const relationKeyword = ref('')
const knowledgeTree = ref([])
const stats = reactive({
  totalPoints: 0,
  totalRelations: 0,
  totalChapters: 0,
  isolatedPoints: 0
})

// 知识点表单状态统一使用 camelCase，模板不再直接碰后端字段名。
const pointDialogVisible = ref(false)
const editingPoint = ref(null)
const submitting = ref(false)
const indexBuilding = ref(false)
const pointFormRef = ref(null)
const pointForm = reactive({
  pointName: '',
  chapterText: '',
  descriptionText: ''
})
const pointRules = {
  pointName: [{ required: true, message: '请输入知识点名称', trigger: 'blur' }]
}

const existingChapters = computed(() => {
  const chapterNames = new Set(
    knowledgePoints.value
      .map((knowledgePoint) => knowledgePoint.chapterText)
      .filter(Boolean)
  )

  return [...chapterNames].sort((leftChapter, rightChapter) => leftChapter.localeCompare(rightChapter, 'zh-Hans-CN'))
})

/**
 * 重置知识点表单，避免打开弹窗时残留上一次编辑内容。
 * @returns {void}
 */
const resetPointForm = () => {
  pointForm.pointName = ''
  pointForm.chapterText = ''
  pointForm.descriptionText = ''
}

/**
 * 刷新统计卡片，确保统计基于内部模型而不是原始 payload。
 * @returns {void}
 */
const refreshStats = () => {
  const pointIds = new Set(
    knowledgePoints.value
      .map((knowledgePoint) => knowledgePoint.pointId)
      .filter(Boolean)
  )
  const linkedIds = new Set()

  knowledgeRelations.value.forEach((knowledgeRelation) => {
    if (knowledgeRelation.fromPointId) {
      linkedIds.add(knowledgeRelation.fromPointId)
    }
    if (knowledgeRelation.toPointId) {
      linkedIds.add(knowledgeRelation.toPointId)
    }
  })

  const chapterNames = new Set(
    knowledgePoints.value.map((knowledgePoint) => knowledgePoint.chapterText || '未分类')
  )

  stats.totalPoints = knowledgePoints.value.length
  stats.totalRelations = knowledgeRelations.value.length
  stats.totalChapters = chapterNames.size
  stats.isolatedPoints = [...pointIds].filter((pointId) => !linkedIds.has(pointId)).length
}

/**
 * 加载知识点和关系，并统一收敛为页面内部模型。
 * @returns {Promise<void>}
 */
const loadAll = async () => {
  const courseId = currentCourseId.value

  if (!courseId) {
    ElMessage.warning('请先在右上角选择课程')
    return
  }

  loading.value = true

  try {
    const [knowledgePointPayload, knowledgeRelationPayload] = await Promise.all([
      getKnowledgePoints(courseId),
      getKnowledgeRelations(courseId)
    ])

    knowledgePoints.value = normalizeListFromPayload(knowledgePointPayload?.points)
      .map((rawPoint) => normalizeKnowledgePoint(rawPoint))
    knowledgeRelations.value = normalizeListFromPayload(knowledgeRelationPayload?.relations)
      .map((rawRelation) => normalizeKnowledgeRelation(rawRelation))
    knowledgeTree.value = buildTree(knowledgePoints.value)
    refreshStats()
  } catch (error) {
    console.error('加载知识图谱失败:', error)
    ElMessage.error('加载知识图谱失败')
  } finally {
    loading.value = false
  }
}

// 图谱组件继续接收通用 nodes / edges 结构，但来源全部改为内部模型。
const graphData = computed(() => {
  if (!knowledgePoints.value.length) {
    return { nodes: [], edges: [] }
  }

  return {
    nodes: knowledgePoints.value.map((knowledgePoint) => ({
      id: knowledgePoint.pointId,
      name: knowledgePoint.pointName,
      chapter: knowledgePoint.chapterText,
      description: knowledgePoint.descriptionText
    })),
    edges: knowledgeRelations.value.map((knowledgeRelation) => ({
      source: knowledgeRelation.fromPointId,
      target: knowledgeRelation.toPointId,
      label: knowledgeRelation.relationTypeText
    }))
  }
})

const filteredRelations = computed(() => {
  const keyword = normalizeSearchKeyword(relationKeyword.value)

  if (!keyword) {
    return knowledgeRelations.value
  }

  return knowledgeRelations.value.filter((knowledgeRelation) => {
    const fromPointName = normalizeSearchKeyword(knowledgeRelation.fromPointName)
    const toPointName = normalizeSearchKeyword(knowledgeRelation.toPointName)
    return fromPointName.includes(keyword) || toPointName.includes(keyword)
  })
})

/**
 * 添加知识点 - 打开空白弹窗。
 * @returns {void}
 */
const addPoint = () => {
  if (!currentCourseId.value) {
    ElMessage.warning('请先在右上角选择课程')
    return
  }

  editingPoint.value = null
  resetPointForm()
  pointDialogVisible.value = true
}

/**
 * 编辑知识点 - 从树节点模型回填表单。
 * @param {KnowledgeTreeNodeModel} selectedTreeNode
 * @returns {void}
 */
const editPoint = (selectedTreeNode) => {
  editingPoint.value = selectedTreeNode
  pointForm.pointName = selectedTreeNode.pointName
  pointForm.chapterText = selectedTreeNode.chapterText
  pointForm.descriptionText = selectedTreeNode.descriptionText
  pointDialogVisible.value = true
}

/**
 * 提交知识点表单。
 * @returns {Promise<void>}
 */
const submitPointForm = async () => {
  const pointFormInstance = pointFormRef.value

  try {
    await pointFormInstance?.validate()
  } catch {
    return
  }

  submitting.value = true

  try {
    const editingKnowledgePoint = editingPoint.value

    if (editingKnowledgePoint?.pointId) {
      await updateKnowledgePoint(editingKnowledgePoint.pointId, {
        point_name: pointForm.pointName,
        chapter: pointForm.chapterText,
        description: pointForm.descriptionText
      })
      ElMessage.success('更新成功')
    } else {
      await createKnowledgePoint({
        point_name: pointForm.pointName,
        chapter: pointForm.chapterText,
        description: pointForm.descriptionText,
        course_id: currentCourseId.value
      })
      ElMessage.success('添加成功')
    }

    pointDialogVisible.value = false
    await loadAll()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 删除知识点。
 * @param {KnowledgeTreeNodeModel} selectedTreeNode
 * @returns {Promise<void>}
 */
const deletePoint = async (selectedTreeNode) => {
  try {
    await ElMessageBox.confirm(`确定删除知识点“${selectedTreeNode.pointName}”吗？`, '删除确认', { type: 'warning' })
    await deleteKnowledgePoint(selectedTreeNode.pointId)
    ElMessage.success('删除成功')
    await loadAll()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 图谱编辑保存。
 * @param {{ nodes: Array<Record<string, unknown>>, edges: Array<Record<string, unknown>> }} graphPayload
 * @returns {Promise<void>}
 */
const handleGraphSave = async (graphPayload) => {
  const courseId = currentCourseId.value

  if (!courseId) {
    ElMessage.warning('请先选择课程')
    return
  }

  try {
    await saveKnowledgeGraph(courseId, graphPayload)
    ElMessage.success('知识图谱保存成功')
    await loadAll()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('知识图谱保存失败')
  }
}

/**
 * 节点点击事件预留给后续扩展，当前显式保留便于接口对齐。
 * @param {unknown} _clickedNode
 * @returns {void}
 */
const handleNodeClick = (_clickedNode) => {
  // 当前页暂不需要在父组件侧处理节点点击。
}

/**
 * 构建当前课程的 GraphRAG 索引。
 * @returns {Promise<void>}
 */
const buildRagIndex = async () => {
  if (!currentCourseId.value) {
    ElMessage.warning('请先选择课程')
    return
  }

  indexBuilding.value = true

  try {
    const ragIndexBuildResult = normalizeRagIndexBuildResult(
      await buildKnowledgeRagIndex(currentCourseId.value)
    )
    const builtFileCount = ragIndexBuildResult.indexPaths.length
    ElMessage.success(`GraphRAG 索引构建完成${builtFileCount ? `（输出 ${builtFileCount} 个索引文件）` : ''}`)
  } catch (error) {
    console.error('构建 GraphRAG 索引失败:', error)
    ElMessage.error('构建 GraphRAG 索引失败，请稍后重试')
  } finally {
    indexBuilding.value = false
  }
}

onMounted(() => {
  loadAll()
})

// 监听课程切换，自动重新加载当前知识图谱。
watch(currentCourseId, () => {
  loadAll()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.stats-row {
  margin-bottom: 12px;
}

.stat-item {
  text-align: center;
}

.stat-item .label {
  color: #909399;
  font-size: 13px;
}

.stat-item .value {
  font-size: 24px;
  font-weight: 600;
  margin-top: 6px;
  color: #303133;
}

.card-title {
  font-weight: 600;
}

.tree-node {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-right: 8px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.3s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}
</style>
