import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '@/stores/course'
import { getKnowledgeMap, getKnowledgePointDetail } from '@/api/student/knowledge'
import {
  buildKnowledgeTree,
  getMasteryColor,
  normalizeIdentifier,
  normalizeKnowledgeMapPayload,
  normalizePointDetail
} from './knowledgeMapModels'

export function useStudentKnowledgeMap() {
  const router = useRouter()
  const courseStore = useCourseStore()
  const loading = ref(true)
  const viewMode = ref('graph')
  const drawerVisible = ref(false)
  const selectedPoint = ref(null)
  const knowledgeNodes = ref([])
  const knowledgeEdges = ref([])
  const knowledgeTree = ref([])

  const graphData = computed(() => ({
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
  }))

  const fetchKnowledgeMap = async () => {
    if (!courseStore.courseId) {
      ElMessage.warning('请先选择课程')
      await router.push('/student/course-select')
      return
    }

    loading.value = true
    try {
      const knowledgeMapPayload = normalizeKnowledgeMapPayload(
        await getKnowledgeMap(courseStore.courseId)
      )
      knowledgeNodes.value = knowledgeMapPayload.nodes
      knowledgeEdges.value = knowledgeMapPayload.edges
      knowledgeTree.value = buildKnowledgeTree(knowledgeNodes.value)
    } catch (error) {
      console.error('获取知识图谱失败:', error)
      ElMessage.error('获取知识图谱失败')
    } finally {
      loading.value = false
    }
  }

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

  const handleNodeClick = async (clickedNode) => {
    const pointId = normalizeIdentifier(clickedNode?.pointId ?? clickedNode?.point_id ?? clickedNode?.id)
    if (pointId) await loadPointDetail(pointId)
  }

  const handleTreeNodeClick = async (treeNode) => {
    if (treeNode.pointId) await loadPointDetail(treeNode.pointId)
  }

  const openResource = (resourceItem) => {
    if (resourceItem.resourceUrl) {
      window.open(resourceItem.resourceUrl, '_blank')
    } else {
      ElMessage.info('资源暂不可用')
    }
  }

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

  return {
    courseStore,
    drawerVisible,
    getMasteryColor,
    goToLearning,
    graphData,
    handleNodeClick,
    handleTreeNodeClick,
    knowledgeTree,
    loadPointDetail,
    loading,
    openResource,
    selectedPoint,
    viewMode
  }
}
