import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { aiChat, getAINodeIntro } from '@/api/student/ai'
import {
  completePathNode,
  completeResource,
  getAIResources,
  getNodeExams,
  getPathNodeDetail,
  getStageTest,
  submitStageTest
} from '@/api/student/learning'
import { useCourseStore } from '@/stores/course'
import { renderMarkdown } from '@/utils/markdown'
import {
  buildDefaultNodeExamModel,
  buildDefaultNodeIntroModel,
  buildDefaultNodeQuizResultModel,
  buildDefaultResourceModel,
  buildDefaultStageTestResultModel,
  buildDefaultTaskModel,
  buildStageTestAnswers,
  formatStageAnswer,
  getDifficultyLabel,
  getDifficultyTagType,
  isEmptyStageAnswer,
  normalizeListFromPayload,
  normalizeNodeExamPayload,
  normalizeNodeIntroPayload,
  normalizeNullableNumber,
  normalizeNumber,
  normalizeObjectFromPayload,
  normalizeResourcePayload,
  normalizeStageQuestionPayload,
  normalizeStageTestResultPayload,
  normalizeTaskPayload,
  normalizeText
} from './taskLearningModels'

const resolveTemplateElement = (templateRef) => {
  const currentValue = templateRef.value
  if (!currentValue) return null
  if (currentValue instanceof HTMLElement) return currentValue
  if (typeof currentValue === 'object' && currentValue.$el instanceof HTMLElement) return currentValue.$el
  return null
}

export function useTaskLearning() {
  const router = useRouter()
  const route = useRoute()
  const courseStore = useCourseStore()

  const currentNodeId = computed(() => normalizeNumber(route.params.nodeId, 0))
  const currentPointId = computed(() => normalizeNullableNumber(route.query.pointId))
  const currentNodeType = computed(() => normalizeText(route.query.nodeType) || 'study')
  const shouldViewStageReport = computed(() => normalizeText(route.query.viewReport) === 'true')
  const isTestNode = computed(() => currentNodeType.value === 'test')

  const loading = ref(true)
  const introLoading = ref(false)
  const aiResourcesLoading = ref(false)
  const currentTask = ref(buildDefaultTaskModel())
  const currentResourceRecord = ref(buildDefaultResourceModel())
  const resourceRecords = ref([])
  const nodeIntro = ref(buildDefaultNodeIntroModel())
  const masteryBeforeRate = ref(null)
  const masteryAfterRate = ref(null)
  const chatDrawerVisible = ref(false)
  const chatMessages = ref([])
  const chatInput = ref('')
  const chatLoading = ref(false)
  const chatMessagesRef = ref(null)
  const currentNodeExam = ref(buildDefaultNodeExamModel())
  const nodeQuizResult = ref(buildDefaultNodeQuizResultModel())
  const stageTestQuestions = ref([])
  const stageTestAnswers = ref({})
  const stageTestResult = ref(buildDefaultStageTestResultModel())
  const stageTestLoading = ref(false)
  const stageTestTitle = ref('')
  const stageTestPassScore = ref(60)
  const stageTestCardRef = ref(null)

  const hasNodeIntro = computed(() => Boolean(
    nodeIntro.value.introductionText
    || nodeIntro.value.learningTipsText
    || nodeIntro.value.keyConceptList.length
  ))
  const hasNodeExam = computed(() => currentNodeExam.value.hasExam)
  const hasNodeQuizResult = computed(() => nodeQuizResult.value.hasResult)
  const hasStageTestResult = computed(() => stageTestResult.value.hasResult)
  const hasStageFeedbackReport = computed(() => {
    const feedbackReport = stageTestResult.value.feedbackReport
    return Boolean(
      feedbackReport.summaryText
      || feedbackReport.analysisText
      || feedbackReport.knowledgeGapList.length
      || feedbackReport.recommendationList.length
      || feedbackReport.nextTaskList.length
      || feedbackReport.conclusionText
    )
  })
  const difficultyTagType = computed(() => getDifficultyTagType(nodeIntro.value.difficultyLevel))
  const difficultyLabel = computed(() => getDifficultyLabel(nodeIntro.value.difficultyLevel))
  const completedResourceCount = computed(() => resourceRecords.value.filter((item) => item.isCompleted).length)
  const requiredResources = computed(() => resourceRecords.value.filter((item) => item.isRequired))
  const requiredCompletedCount = computed(() => requiredResources.value.filter((item) => item.isCompleted).length)
  const progressPercent = computed(() => {
    if (resourceRecords.value.length === 0) return 0
    return Math.round((completedResourceCount.value / resourceRecords.value.length) * 100)
  })
  const allCompleted = computed(() => {
    return requiredResources.value.length > 0 && requiredCompletedCount.value >= requiredResources.value.length
  })
  const displayStageConclusion = computed(() => {
    const feedbackReport = stageTestResult.value.feedbackReport
    const conclusionText = feedbackReport.conclusionText.trim()
    const summaryText = feedbackReport.summaryText.trim()
    const analysisText = feedbackReport.analysisText.trim()
    return !conclusionText || conclusionText === summaryText || conclusionText === analysisText ? '' : conclusionText
  })

  const loadNodeData = async () => {
    if (!currentNodeId.value) {
      ElMessage.warning('缺少任务节点ID')
      return
    }

    loading.value = true
    try {
      const nodePayload = normalizeObjectFromPayload(await getPathNodeDetail(currentNodeId.value, courseStore.courseId))
      currentTask.value = normalizeTaskPayload(nodePayload, currentNodeId.value, currentPointId.value)
      masteryBeforeRate.value = normalizeNullableNumber(nodePayload.mastery_before)
      masteryAfterRate.value = normalizeNullableNumber(nodePayload.mastery_after)
    } catch (error) {
      console.error('加载节点数据失败:', error)
      ElMessage.error('加载学习资源失败')
    } finally {
      loading.value = false
    }

    if (!isTestNode.value) void loadAIResources()
  }

  const loadAIResources = async () => {
    aiResourcesLoading.value = true
    try {
      const recommendationPayload = normalizeObjectFromPayload(await getAIResources(currentNodeId.value))
      const internalResourceList = normalizeListFromPayload(recommendationPayload.internal_resources).map(normalizeResourcePayload)
      const externalResourceList = normalizeListFromPayload(recommendationPayload.external_resources).map(normalizeResourcePayload)
      resourceRecords.value = [...internalResourceList, ...externalResourceList]
    } catch (error) {
      console.warn('AI资源推荐加载失败:', error)
    } finally {
      aiResourcesLoading.value = false
    }
  }

  const loadNodeIntro = async () => {
    if (!currentTask.value.pointNameText) return

    introLoading.value = true
    try {
      const introPayload = await getAINodeIntro({
        point_name: currentTask.value.pointNameText,
        point_id: currentTask.value.knowledgePointId,
        course_id: courseStore.courseId || null,
        course_name: courseStore.courseName || ''
      })
      nodeIntro.value = normalizeNodeIntroPayload(introPayload)
    } catch (error) {
      console.error('加载知识点介绍失败:', error)
    } finally {
      introLoading.value = false
    }
  }

  const goBack = () => {
    const shouldShowRefreshing = stageTestResult.value.isPassed && stageTestResult.value.isPathRefreshed
    void router.push(shouldShowRefreshing ? '/student/learning-path?refreshing=1' : '/student/learning-path')
  }

  const selectResource = async (resourceRecord) => {
    currentResourceRecord.value = resourceRecord
    if (resourceRecord.resourceUrl) window.open(resourceRecord.resourceUrl, '_blank')
    if (!resourceRecord.isCompleted) {
      try {
        await completeResource(currentNodeId.value, resourceRecord.resourceId, courseStore.courseId)
        resourceRecord.isCompleted = true
        ElMessage.success('资源学习完成！')
      } catch (error) {
        console.error('标记资源完成失败:', error)
        ElMessage.error('标记资源完成失败，请稍后重试')
      }
    }
  }

  const completeTask = async () => {
    try {
      await completePathNode(currentNodeId.value, courseStore.courseId)
      ElMessage.success('恭喜！任务学习完成！')
      await router.push('/student/learning-path?refreshing=1')
    } catch (error) {
      console.error('完成任务失败:', error)
      ElMessage.error('完成任务失败，请稍后重试')
    }
  }

  const loadNodeExam = async () => {
    try {
      const examPayload = normalizeObjectFromPayload(await getNodeExams(currentNodeId.value, courseStore.courseId))
      const examList = normalizeListFromPayload(examPayload.exams).map(normalizeNodeExamPayload)
      currentNodeExam.value = examList[0] || buildDefaultNodeExamModel()
    } catch (error) {
      console.error('加载节点测验失败:', error)
    }
  }

  const loadStageTest = async () => {
    stageTestLoading.value = true
    try {
      const stageTestPayload = normalizeObjectFromPayload(await getStageTest(currentNodeId.value))
      const questionList = normalizeListFromPayload(stageTestPayload.questions).map(normalizeStageQuestionPayload)
      stageTestTitle.value = normalizeText(stageTestPayload.node_title ?? stageTestPayload.title) || '阶段测试'
      stageTestPassScore.value = normalizeNumber(stageTestPayload.pass_score, 60)
      stageTestQuestions.value = questionList
      stageTestAnswers.value = buildStageTestAnswers(questionList)

      const normalizedResult = normalizeStageTestResultPayload(stageTestPayload.result)
      stageTestResult.value = normalizedResult
      if (normalizedResult.hasResult) stageTestPassScore.value = normalizedResult.passThresholdValue
    } catch (error) {
      if (error?.response?.status !== 404 && error?.status !== 404) console.error('加载阶段测试失败:', error)
    } finally {
      stageTestLoading.value = false
    }
  }

  const submitStageTestAnswers = async () => {
    const unansweredQuestions = stageTestQuestions.value.filter((questionItem) => {
      return isEmptyStageAnswer(stageTestAnswers.value[questionItem.questionId])
    })
    if (unansweredQuestions.length > 0) {
      ElMessage.warning(`还有 ${unansweredQuestions.length} 题未作答`)
      return
    }

    stageTestLoading.value = true
    try {
      const answerPayload = {}
      stageTestQuestions.value.forEach((questionItem) => {
        answerPayload[questionItem.questionId] = stageTestAnswers.value[questionItem.questionId]
      })
      const submissionResult = normalizeStageTestResultPayload(await submitStageTest(currentNodeId.value, { answers: answerPayload }))
      stageTestResult.value = submissionResult
      stageTestPassScore.value = submissionResult.passThresholdValue || stageTestPassScore.value
      if (submissionResult.isPassed) {
        ElMessage.success(`测试通过！得分：${submissionResult.scoreValue}分`)
      } else {
        ElMessage.warning(`未通过，得分：${submissionResult.scoreValue}分，需要${stageTestPassScore.value}分`)
      }
    } catch (error) {
      console.error('提交阶段测试失败:', error)
      ElMessage.error('提交失败，请重试')
    } finally {
      stageTestLoading.value = false
    }
  }

  const retryStageTest = () => {
    stageTestResult.value = buildDefaultStageTestResultModel()
    stageTestAnswers.value = buildStageTestAnswers(stageTestQuestions.value)
  }

  const resetNodeQuizResult = () => {
    nodeQuizResult.value = buildDefaultNodeQuizResultModel()
  }

  const startQuiz = async () => {
    if (!currentNodeExam.value.examId) return
    try {
      await ElMessageBox.confirm(
        `即将开始「${currentNodeExam.value.titleText}」作业，准备好了吗？`,
        '节点作业',
        { confirmButtonText: '开始', cancelButtonText: '稍后', type: 'info' }
      )
      await router.push({ path: `/student/exam/${currentNodeExam.value.examId}`, query: { nodeId: currentNodeId.value } })
    } catch {
      // 用户主动取消时不提示错误。
    }
  }

  const scrollChat = async () => {
    await nextTick()
    const chatContainerElement = resolveTemplateElement(chatMessagesRef)
    if (chatContainerElement) chatContainerElement.scrollTop = chatContainerElement.scrollHeight
  }

  const sendChat = async () => {
    const questionText = chatInput.value.trim()
    if (!questionText || chatLoading.value) return

    const recentHistory = chatMessages.value.slice(-12)
    chatMessages.value.push({ role: 'user', content: questionText })
    chatInput.value = ''
    chatLoading.value = true
    await scrollChat()

    try {
      const chatReplyPayload = normalizeObjectFromPayload(await aiChat({
        question: questionText,
        message: questionText,
        course_id: courseStore.courseId || null,
        point_id: currentTask.value.knowledgePointId || null,
        knowledge_point: currentTask.value.pointNameText || '',
        course_name: courseStore.courseName || '',
        history: recentHistory
      }))
      chatMessages.value.push({ role: 'assistant', content: normalizeText(chatReplyPayload.reply) || '暂无回复' })
    } catch {
      chatMessages.value.push({ role: 'assistant', content: '抱歉，AI助手暂时无法回复，请稍后重试。' })
    } finally {
      chatLoading.value = false
      await scrollChat()
    }
  }

  const scrollStageTestCardIntoView = () => {
    const stageTestElement = resolveTemplateElement(stageTestCardRef)
    if (stageTestElement && typeof stageTestElement.scrollIntoView === 'function') {
      stageTestElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  const openFullAssistant = () => {
    chatDrawerVisible.value = false
    void router.push({
      path: '/student/ai-assistant',
      query: { pointId: currentTask.value.knowledgePointId || '', keyword: currentTask.value.pointNameText || '' }
    })
  }

  const formatMessage = (content) => renderMarkdown(content)

  onMounted(async () => {
    if (isTestNode.value) stageTestLoading.value = true
    await loadNodeData()

    if (isTestNode.value) {
      void loadStageTest()
    } else {
      void loadNodeIntro()
      void loadNodeExam()
    }

    if (shouldViewStageReport.value) {
      await nextTick()
      window.setTimeout(() => scrollStageTestCardIntoView(), 500)
    }
  })

  return {
    allCompleted,
    aiResourcesLoading,
    chatDrawerVisible,
    chatInput,
    chatLoading,
    chatMessages,
    chatMessagesRef,
    completeTask,
    completedResourceCount,
    currentNodeExam,
    currentResourceRecord,
    currentTask,
    difficultyLabel,
    difficultyTagType,
    displayStageConclusion,
    formatMessage,
    formatStageAnswer,
    goBack,
    hasNodeExam,
    hasNodeIntro,
    hasNodeQuizResult,
    hasStageFeedbackReport,
    hasStageTestResult,
    introLoading,
    isTestNode,
    loadStageTest,
    loading,
    masteryAfterRate,
    masteryBeforeRate,
    nodeIntro,
    nodeQuizResult,
    openFullAssistant,
    progressPercent,
    renderMarkdown,
    resetNodeQuizResult,
    resourceRecords,
    retryStageTest,
    selectResource,
    sendChat,
    stageTestAnswers,
    stageTestCardRef,
    stageTestLoading,
    stageTestPassScore,
    stageTestQuestions,
    stageTestResult,
    stageTestTitle,
    startQuiz,
    submitStageTestAnswers
  }
}
