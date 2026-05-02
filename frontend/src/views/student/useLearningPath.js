import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  completePathNode,
  getLearningPath,
  refreshLearningPathWithAI,
  skipPathNode,
  startLearningNode
} from '@/api/student/learning'
import { useCourseStore } from '@/stores/course'
import { useAIProgress } from '@/composables/useAIProgress'
import {
  getNodeStatusText,
  getNodeTagType,
  normalizeLearningPathPayload,
  normalizeLearningPathRefreshSummary,
  normalizeText
} from './learningPathModels'

export function useLearningPath() {
  const router = useRouter()
  const route = useRoute()
  const courseStore = useCourseStore()
  const aiProgress = useAIProgress({
    stages: [
      { at: 0, text: '正在分析知识图谱结构...' },
      { at: 15, text: '学习画像匹配中...' },
      { at: 35, text: '知识追踪模型推理中...' },
      { at: 55, text: '规划最优学习路径...' },
      { at: 75, text: '渲染学习节点...' },
      { at: 90, text: '即将完成...' }
    ]
  })

  const loading = ref(true)
  const loadError = ref('')
  const needAssessment = ref(false)
  const assessmentHint = ref('请先完成初始评测')
  const refreshingPath = ref(false)
  const generating = ref(false)
  const refreshingMessage = ref('正在为您刷新个性化学习路径...')
  const pathNodes = ref([])
  const selectedNode = ref(null)
  const trackWrapperRef = ref(null)
  const trackRef = ref(null)

  const totalNodes = computed(() => pathNodes.value.length)
  const completedNodes = computed(() => pathNodes.value.filter((pathNode) => pathNode.learningStatus === 'completed').length)
  const progressPercent = computed(() => totalNodes.value === 0 ? 0 : Math.round((completedNodes.value / totalNodes.value) * 100))
  const aiProgressStageText = computed(() => normalizeText(aiProgress.stageText.value) || '正在准备学习路径...')
  const aiProgressPercentage = computed(() => Number(aiProgress.progress.value) || 0)
  const isAiProgressRunning = computed(() => Boolean(aiProgress.isRunning.value))
  const isRefreshingRoute = computed(() => normalizeText(route.query['refreshing']) === '1')
  const showRefreshingAnimation = computed(() => generating.value || refreshingPath.value || isAiProgressRunning.value)
  const refreshingDescription = computed(() => refreshingMessage.value)

  const selectNode = (node) => {
    selectedNode.value = node
    nextTick(() => {
      const trackWrapperElement = trackWrapperRef.value
      const trackElement = trackRef.value
      if (!trackWrapperElement || !trackElement) return
      const nodeIndex = pathNodes.value.findIndex((pathNode) => pathNode.nodeId === node.nodeId)
      const stationElements = trackElement.querySelectorAll('.subway-station')
      if (stationElements[nodeIndex]) {
        const stationElement = stationElements[nodeIndex]
        const wrapperRect = trackWrapperElement.getBoundingClientRect()
        const stationRect = stationElement.getBoundingClientRect()
        const scrollLeft = trackWrapperElement.scrollLeft + stationRect.left - wrapperRect.left - wrapperRect.width / 2 + stationRect.width / 2
        trackWrapperElement.scrollTo({ left: Math.max(0, scrollLeft), behavior: 'smooth' })
      }
    })
  }

  const loadLearningPath = async () => {
    if (!courseStore.courseId) {
      pathNodes.value = []
      selectedNode.value = null
      loading.value = false
      return
    }

    loading.value = true
    loadError.value = ''
    selectedNode.value = null
    try {
      const learningPathPayload = normalizeLearningPathPayload(
        await getLearningPath(courseStore.courseId)
      )

      if (learningPathPayload.needAssessment) {
        needAssessment.value = true
        assessmentHint.value = learningPathPayload.assessmentHint
        generating.value = false
        aiProgress.complete()
        pathNodes.value = []
        return
      }

      needAssessment.value = false

      if (learningPathPayload.generating) {
        generating.value = true
        aiProgress.start()
        pathNodes.value = []
        window.setTimeout(() => {
          if (generating.value) void loadLearningPath()
        }, 2000)
        return
      }

      generating.value = false
      aiProgress.complete()
      pathNodes.value = learningPathPayload.nodes

      await nextTick()
      const currentNode = pathNodes.value.find((pathNode) => pathNode.learningStatus === 'current')
      if (currentNode) {
        selectNode(currentNode)
      } else if (pathNodes.value.length) {
        selectNode(pathNodes.value[0])
      }
    } catch (error) {
      console.error('获取学习路径失败:', error)
      loadError.value = '加载学习路径失败，请点击重试'
    } finally {
      loading.value = false
      if (isRefreshingRoute.value) {
        refreshingPath.value = false
        await router.replace({ path: '/student/learning-path' })
      }
    }
  }

  const resolveLiveNode = (node) => {
    if (!node?.nodeId) return null
    return pathNodes.value.find((pathNode) => pathNode.nodeId === node.nodeId) || null
  }

  const startLearning = async (node) => {
    try {
      const liveNode = resolveLiveNode(node)
      if (!liveNode) {
        await loadLearningPath()
        ElMessage.warning('当前节点已刷新，请重新选择后再操作')
        return
      }
      await startLearningNode(liveNode.nodeId, courseStore.courseId)
      await router.push({
        path: `/student/task/${liveNode.nodeId}`,
        query: { pointId: liveNode.pointId, nodeType: liveNode.nodeTypeText || 'study' }
      })
    } catch (error) {
      console.error('开始学习失败:', error)
      ElMessage.error('开始学习失败，请稍后重试')
    }
  }

  const handleCompleteNode = async (node) => {
    try {
      await ElMessageBox.confirm('确定要标记此节点为已完成吗？', '完成学习', {
        confirmButtonText: '确认完成',
        cancelButtonText: '取消',
        type: 'success'
      })
      const liveNode = resolveLiveNode(node)
      if (!liveNode) {
        await loadLearningPath()
        ElMessage.warning('当前节点已刷新，请重新选择后再操作')
        return
      }
      const wasLastVisibleNode = totalNodes.value > 0 && completedNodes.value + 1 >= totalNodes.value
      if (wasLastVisibleNode) {
        refreshingMessage.value = '当前路径已学习完成，系统正在为你规划下一阶段内容，请稍候。'
        refreshingPath.value = true
        aiProgress.start()
      }
      await completePathNode(liveNode.nodeId, courseStore.courseId)
      ElMessage.success('恭喜完成学习！')
      await loadLearningPath()
    } catch (error) {
      if (error !== 'cancel') console.error('标记完成失败:', error)
    } finally {
      aiProgress.complete()
      refreshingPath.value = false
      refreshingMessage.value = '正在为您刷新个性化学习路径...'
    }
  }

  const reviewNode = (node) => {
    const liveNode = resolveLiveNode(node)
    if (!liveNode) {
      ElMessage.warning('当前节点已刷新，请重新选择')
      return
    }
    void router.push({
      path: `/student/task/${liveNode.nodeId}`,
      query: { pointId: liveNode.pointId, review: 'true', nodeType: liveNode.nodeTypeText || 'study' }
    })
  }

  const viewTestReport = (node) => {
    const liveNode = resolveLiveNode(node)
    if (!liveNode) {
      ElMessage.warning('当前节点已刷新，请重新选择')
      return
    }
    void router.push({
      path: `/student/task/${liveNode.nodeId}`,
      query: { pointId: liveNode.pointId, nodeType: 'test', viewReport: 'true' }
    })
  }

  const handleSkipNode = async (node) => {
    try {
      await ElMessageBox.confirm('确定要跳过此学习节点吗？跳过后可以稍后返回学习。', '提示', {
        confirmButtonText: '确定跳过',
        cancelButtonText: '取消',
        type: 'warning'
      })
      const liveNode = resolveLiveNode(node)
      if (!liveNode) {
        await loadLearningPath()
        ElMessage.warning('当前节点已刷新，请重新选择后再操作')
        return
      }

      await skipPathNode(liveNode.nodeId, '', courseStore.courseId)
      ElMessage.success('已跳过该节点')
      await loadLearningPath()
    } catch (error) {
      if (error !== 'cancel') console.error('跳过节点失败:', error)
    }
  }

  const goToAssessment = () => {
    void router.push('/student/assessment')
  }

  const refreshPath = async () => {
    if (!courseStore.courseId) return
    refreshingMessage.value = '系统正在根据你最新的掌握度与学习进度重规划路径，请稍候。'
    refreshingPath.value = true
    aiProgress.start()
    try {
      const refreshSummary = normalizeLearningPathRefreshSummary(
        await refreshLearningPathWithAI(courseStore.courseId)
      )

      const summaryParts = [`保留节点 ${refreshSummary.preservedCount} 个，新规划节点 ${refreshSummary.newCount} 个。`]
      if (refreshSummary.changeSummary.preservedContext > 0) summaryParts.push(`已保留当前节点上下文，避免学习进度被重置。`)
      if (refreshSummary.changeSummary.removedCount > 0) summaryParts.push(`替换未来节点 ${refreshSummary.changeSummary.removedCount} 个。`)
      if (refreshSummary.ktInfo.answerCount > 0) summaryParts.push(`基于 ${refreshSummary.ktInfo.answerCount} 条答题记录的知识追踪分析。`)
      if (refreshSummary.profile.summaryText) summaryParts.push(`画像：${refreshSummary.profile.summaryText.slice(0, 80)}`)

      ElMessage.success({ message: `学习路径已刷新：${summaryParts.join(' ')}`, duration: 5000 })
    } catch (error) {
      console.error('刷新学习路径失败:', error)
      ElMessage.error('刷新失败，请稍后重试')
    } finally {
      aiProgress.complete()
      await loadLearningPath()
      refreshingPath.value = false
      refreshingMessage.value = '正在为您刷新个性化学习路径...'
    }
  }

  onMounted(() => {
    if (isRefreshingRoute.value) {
      refreshingMessage.value = '当前路径已刷新，正在同步最新节点状态，请稍候。'
      refreshingPath.value = true
    }
    void loadLearningPath()
  })

  watch(() => courseStore.courseId, () => {
    void loadLearningPath()
  })

  return {
    aiProgressPercentage,
    aiProgressStageText,
    assessmentHint,
    completedNodes,
    courseStore,
    getNodeStatusText,
    getNodeTagType,
    goToAssessment,
    handleCompleteNode,
    handleSkipNode,
    isAiProgressRunning,
    loadError,
    loadLearningPath,
    loading,
    needAssessment,
    pathNodes,
    progressPercent,
    refreshPath,
    refreshingDescription,
    refreshingPath,
    reviewNode,
    selectedNode,
    selectNode,
    showRefreshingAnimation,
    startLearning,
    totalNodes,
    trackRef,
    trackWrapperRef,
    viewTestReport
  }
}
