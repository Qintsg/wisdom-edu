import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { generateFeedback, getExamResult, getFeedback } from '@/api/student/exam'
import {
  aiProgressStages,
  buildDefaultAiAnalysis,
  buildDefaultExamResult,
  formatAnswer,
  normalizeAiFeedbackPayload,
  normalizeExamResultPayload,
  normalizeIdentifier
} from './feedbackReportModels'

export function useFeedbackReport() {
  const router = useRouter()
  const route = useRoute()
  const reportId = normalizeIdentifier(route.params['reportId'])
  const loading = ref(true)
  const aiRetrying = ref(false)
  const questionDetails = ref([])
  const masteryChanges = ref([])
  const feedbackStatus = ref('pending')
  const pollAttempts = ref(0)
  const pollTimer = ref(null)
  const maxPollAttempts = 60
  const aiProgressPercent = ref(0)
  const aiProgressStageText = ref('正在准备分析环境...')
  const examResult = ref(buildDefaultExamResult(reportId))
  const aiAnalysis = ref(buildDefaultAiAnalysis())
  let aiProgressTimer = null
  let aiProgressStageIndex = 0

  const statusLabel = computed(() => {
    if (feedbackStatus.value === 'pending') return '生成中'
    if (feedbackStatus.value === 'failed') return '生成失败'
    return '已完成'
  })

  const statusTagType = computed(() => {
    if (feedbackStatus.value === 'pending') return 'info'
    if (feedbackStatus.value === 'failed') return 'warning'
    return 'success'
  })

  const scorePercent = computed(() => {
    const totalScore = examResult.value.totalScore || 100
    return Math.min(Math.round((Number(examResult.value.score || 0) / totalScore) * 100), 100)
  })

  const scoreColor = computed(() => {
    const percentage = scorePercent.value
    if (percentage >= 90) return '#22a06b'
    if (percentage >= 70) return '#129a74'
    if (percentage >= 60) return '#dd8f1d'
    return '#d45050'
  })

  const displayConclusion = computed(() => {
    const conclusion = (aiAnalysis.value.conclusion || '').trim()
    const summary = (aiAnalysis.value.summary || '').trim()
    const analysis = (aiAnalysis.value.analysis || '').trim()
    return !conclusion || conclusion === summary || conclusion === analysis ? '' : conclusion
  })

  function stopAIProgress() {
    if (aiProgressTimer) {
      window.clearInterval(aiProgressTimer)
      aiProgressTimer = null
    }
  }

  function startAIProgress() {
    stopAIProgress()
    aiProgressPercent.value = 0
    aiProgressStageIndex = 0
    aiProgressStageText.value = aiProgressStages[0].text
    aiProgressTimer = window.setInterval(() => {
      aiProgressPercent.value = Math.min(aiProgressPercent.value + Math.floor(Math.random() * 4) + 1, 95)
      while (aiProgressStageIndex < aiProgressStages.length - 1 && aiProgressPercent.value >= aiProgressStages[aiProgressStageIndex + 1].at) {
        aiProgressStageIndex++
      }
      aiProgressStageText.value = aiProgressStages[aiProgressStageIndex].text
    }, 800)
  }

  function finishAIProgress() {
    stopAIProgress()
    aiProgressPercent.value = 100
    aiProgressStageText.value = 'AI 报告已生成'
  }

  function clearPollTimer() {
    if (pollTimer.value) {
      window.clearTimeout(pollTimer.value)
      pollTimer.value = null
    }
  }

  function schedulePoll(delay = 2000) {
    clearPollTimer()
    if (feedbackStatus.value !== 'pending' || pollAttempts.value >= maxPollAttempts) return
    pollTimer.value = window.setTimeout(async () => {
      pollAttempts.value += 1
      await loadAIFeedback(reportId)
    }, delay)
  }

  async function loadFeedbackReport() {
    loading.value = true
    try {
      if (!reportId) throw new Error('missing-report-id')

      const normalizedResult = normalizeExamResultPayload(await getExamResult(reportId), reportId)
      questionDetails.value = normalizedResult.questionDetails
      examResult.value = normalizedResult.examResult
    } catch (error) {
      console.error('获取反馈报告失败:', error)
      ElMessage.error('获取反馈报告失败')
    } finally {
      loading.value = false
    }

    if (!reportId) return
    pollAttempts.value = 0
    await loadAIFeedback(reportId)
  }

  async function loadAIFeedback(examId = reportId) {
    try {
      const normalizedExamId = normalizeIdentifier(examId, reportId)
      if (!normalizedExamId) throw new Error('missing-report-id')

      const normalizedFeedback = normalizeAiFeedbackPayload(await getFeedback(normalizedExamId))
      feedbackStatus.value = normalizedFeedback.status
      aiAnalysis.value = normalizedFeedback.analysis
      masteryChanges.value = normalizedFeedback.masteryChanges

      if (feedbackStatus.value === 'pending') {
        if (!aiProgressTimer) startAIProgress()
        schedulePoll(normalizedFeedback.pollIntervalMs)
      } else {
        finishAIProgress()
        clearPollTimer()
      }
    } catch (error) {
      stopAIProgress()
      clearPollTimer()
      feedbackStatus.value = 'failed'
      aiAnalysis.value = {
        ...buildDefaultAiAnalysis(),
        summary: '反馈报告获取失败'
      }
      masteryChanges.value = []
      console.error('获取 AI 分析失败:', error)
    }
  }

  async function retryAIFeedback() {
    aiRetrying.value = true
    try {
      if (!reportId) throw new Error('missing-report-id')

      await generateFeedback(reportId, true)
      feedbackStatus.value = 'pending'
      pollAttempts.value = 0
      startAIProgress()
      await loadAIFeedback(reportId)
      ElMessage.success('AI 报告已重新排队生成')
    } catch (error) {
      console.error('重新获取 AI 分析失败:', error)
      ElMessage.error('重新获取 AI 分析失败')
    } finally {
      aiRetrying.value = false
    }
  }

  function goBack() {
    router.push('/student/exams')
  }

  function retryExam() {
    router.push(`/student/exam/${reportId}`)
  }

  function goToLearningPath() {
    router.push('/student/learning-path')
  }

  onMounted(() => {
    void loadFeedbackReport()
  })

  onUnmounted(() => {
    stopAIProgress()
    clearPollTimer()
  })

  return {
    aiAnalysis,
    aiProgressPercent,
    aiProgressStageText,
    aiRetrying,
    displayConclusion,
    examResult,
    feedbackStatus,
    formatAnswer,
    goBack,
    goToLearningPath,
    loading,
    masteryChanges,
    questionDetails,
    retryAIFeedback,
    retryExam,
    scoreColor,
    scorePercent,
    statusLabel,
    statusTagType
  }
}
