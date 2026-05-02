import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  buildKnowledgeRagIndex,
  createKnowledgePoint,
  deleteKnowledgePoint,
  getKnowledgePoints,
  getKnowledgeRelations,
  saveKnowledgeGraph,
  updateKnowledgePoint
} from '@/api/teacher/knowledge'
import { useCourseStore } from '@/stores/course'
import {
  buildKnowledgeTree,
  normalizeKnowledgePointListPayload,
  normalizeKnowledgeRelationListPayload,
  normalizeRagIndexBuildResult,
  normalizeSearchKeyword
} from './knowledgeManageModels'

export function useTeacherKnowledgeManage() {
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

  const pointDialogVisible = ref(false)
  const editingPoint = ref(null)
  const submitting = ref(false)
  const indexBuilding = ref(false)
  const pointFormRef = ref(null)
  const pointForm = reactive({ pointName: '', chapterText: '', descriptionText: '' })
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

  const resetPointForm = () => {
    pointForm.pointName = ''
    pointForm.chapterText = ''
    pointForm.descriptionText = ''
  }

  const refreshStats = () => {
    const pointIds = new Set(
      knowledgePoints.value
        .map((knowledgePoint) => knowledgePoint.pointId)
        .filter(Boolean)
    )
    const linkedIds = new Set()

    knowledgeRelations.value.forEach((knowledgeRelation) => {
      if (knowledgeRelation.fromPointId) linkedIds.add(knowledgeRelation.fromPointId)
      if (knowledgeRelation.toPointId) linkedIds.add(knowledgeRelation.toPointId)
    })

    const chapterNames = new Set(
      knowledgePoints.value.map((knowledgePoint) => knowledgePoint.chapterText || '未分类')
    )

    stats.totalPoints = knowledgePoints.value.length
    stats.totalRelations = knowledgeRelations.value.length
    stats.totalChapters = chapterNames.size
    stats.isolatedPoints = [...pointIds].filter((pointId) => !linkedIds.has(pointId)).length
  }

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

      knowledgePoints.value = normalizeKnowledgePointListPayload(knowledgePointPayload)
      knowledgeRelations.value = normalizeKnowledgeRelationListPayload(knowledgeRelationPayload)
      knowledgeTree.value = buildKnowledgeTree(knowledgePoints.value)
      refreshStats()
    } catch (error) {
      console.error('加载知识图谱失败:', error)
      ElMessage.error('加载知识图谱失败')
    } finally {
      loading.value = false
    }
  }

  const graphData = computed(() => {
    if (!knowledgePoints.value.length) return { nodes: [], edges: [] }

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

    if (!keyword) return knowledgeRelations.value

    return knowledgeRelations.value.filter((knowledgeRelation) => {
      const fromPointName = normalizeSearchKeyword(knowledgeRelation.fromPointName)
      const toPointName = normalizeSearchKeyword(knowledgeRelation.toPointName)
      return fromPointName.includes(keyword) || toPointName.includes(keyword)
    })
  })

  const addPoint = () => {
    if (!currentCourseId.value) {
      ElMessage.warning('请先在右上角选择课程')
      return
    }

    editingPoint.value = null
    resetPointForm()
    pointDialogVisible.value = true
  }

  const editPoint = (selectedTreeNode) => {
    editingPoint.value = selectedTreeNode
    pointForm.pointName = selectedTreeNode.pointName
    pointForm.chapterText = selectedTreeNode.chapterText
    pointForm.descriptionText = selectedTreeNode.descriptionText
    pointDialogVisible.value = true
  }

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

  const handleNodeClick = (_clickedNode) => {
    // 当前页暂不需要在父组件侧处理节点点击。
  }

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

  watch(currentCourseId, () => {
    loadAll()
  })

  return {
    addPoint,
    buildRagIndex,
    deletePoint,
    editPoint,
    editingPoint,
    existingChapters,
    filteredRelations,
    graphData,
    handleGraphSave,
    handleNodeClick,
    indexBuilding,
    knowledgePoints,
    knowledgeTree,
    loadAll,
    loading,
    pointDialogVisible,
    pointForm,
    pointFormRef,
    pointRules,
    relationKeyword,
    showGraph,
    stats,
    submitting,
    submitPointForm
  }
}
