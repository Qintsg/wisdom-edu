import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getAIProfileAnalysis } from '@/api/student/ai'
import { getProfile, refreshProfileWithAI } from '@/api/student/profile'
import { useAIProgress } from '@/composables/useAIProgress'
import { useAssessmentStore } from '@/stores/assessment'
import { useCourseStore } from '@/stores/course'
import { useUserStore } from '@/stores/user'
import {
  buildDefaultProfileSnapshot,
  getProgressColor,
  normalizeAssessmentReadyState,
  normalizeNumber,
  normalizeProfilePayload,
  normalizeProfileSuggestionList,
  normalizeText,
  wrapAxisLabel
} from './profileModels'

export function useProfileView() {
  const userStore = useUserStore()
  const courseStore = useCourseStore()
  const assessmentStore = useAssessmentStore()
  const loading = ref(true)
  const aiLoading = ref(false)
  const refreshing = ref(false)
  const aiLoadFailed = ref(false)
  const profileSnapshot = ref(buildDefaultProfileSnapshot())
  const aiSuggestions = ref([])
  const assessmentReady = ref(false)
  const masteryChartRef = ref(null)
  let masteryChart = null

  const aiProgress = useAIProgress({
    stages: [
      { at: 0, text: '正在准备分析...' },
      { at: 15, text: '正在读取学习记录...' },
      { at: 30, text: '正在评估能力画像...' },
      { at: 50, text: '正在生成个性化建议...' },
      { at: 75, text: '正在整合分析结果...' },
      { at: 90, text: '即将完成...' }
    ],
    tickInterval: 600
  })

  const username = computed(() => userStore.username || '同学')
  const learnerTags = computed(() => profileSnapshot.value.learnerTagList)
  const abilityData = computed(() => profileSnapshot.value.abilityEntries.map((entry) => ({
    name: entry.abilityName,
    value: entry.scoreValue
  })))
  const masteryData = computed(() => profileSnapshot.value.masteryEntries.map((entry) => ({
    pointId: entry.pointId,
    name: entry.pointName,
    value: entry.masteryPercent
  })))
  const profileSummary = computed(() => profileSnapshot.value.summaryText)
  const profileWeakness = computed(() => profileSnapshot.value.weaknessText)
  const profileStrength = computed(() => profileSnapshot.value.strengthText)
  const aiProgressPercent = computed(() => normalizeNumber(aiProgress.progress.value))
  const aiProgressStageText = computed(() => normalizeText(aiProgress.stageText.value) || '正在准备分析...')
  const noAssessmentDone = computed(() => !abilityData.value.length && !masteryData.value.length && !profileSummary.value)
  const highMasteryCount = computed(() => masteryData.value.filter((item) => item.value >= 80).length)
  const mediumMasteryCount = computed(() => masteryData.value.filter((item) => item.value >= 60 && item.value < 80).length)
  const lowMasteryCount = computed(() => masteryData.value.filter((item) => item.value < 60).length)

  const abilityAverage = computed(() => {
    if (!abilityData.value.length) return 0
    const totalScore = abilityData.value.reduce((sum, item) => sum + item.value, 0)
    return Math.round(totalScore / abilityData.value.length)
  })

  const masteryAverage = computed(() => {
    if (!masteryData.value.length) return 0
    const totalScore = masteryData.value.reduce((sum, item) => sum + item.value, 0)
    return Math.round(totalScore / masteryData.value.length)
  })

  const strongestAbility = computed(() => [...abilityData.value].sort((left, right) => right.value - left.value)[0] || null)
  const weakestAbility = computed(() => [...abilityData.value].sort((left, right) => left.value - right.value)[0] || null)
  const topWeakMasteries = computed(() => [...masteryData.value].sort((left, right) => left.value - right.value).slice(0, 3))
  const learningFocusLabel = computed(() => {
    if (!masteryData.value.length) return '暂无知识追踪数据'
    if (lowMasteryCount.value) return `${lowMasteryCount.value} 个薄弱项待突破`
    if (mediumMasteryCount.value) return `${mediumMasteryCount.value} 个知识点待巩固`
    return '整体掌握稳定'
  })
  const profileCompleteness = computed(() => {
    const abilityScore = abilityData.value.length ? 34 : 0
    const masteryScore = masteryData.value.length ? 42 : 0
    const narrativeScore = profileSummary.value || profileStrength.value || profileWeakness.value ? 24 : 0
    return abilityScore + masteryScore + narrativeScore
  })
  const masteryChartHeight = computed(() => Math.max(220, masteryData.value.length * 34 + 20))
  const masteryViewportHeight = computed(() => Math.min(Math.max(220, masteryData.value.length * 24), 420))

  const resetProfileState = () => {
    profileSnapshot.value = buildDefaultProfileSnapshot()
    aiSuggestions.value = []
    aiLoadFailed.value = false
    assessmentReady.value = false
  }

  const disposeMasteryChart = () => {
    if (masteryChart) {
      masteryChart.dispose()
      masteryChart = null
    }
  }

  const initMasteryChart = () => {
    if (!masteryChartRef.value || !masteryData.value.length) return

    disposeMasteryChart()
    masteryChart = echarts.init(masteryChartRef.value)
    const items = [...masteryData.value].sort((a, b) => a.value - b.value)

    masteryChart.setOption({
      backgroundColor: 'transparent',
      animationDuration: 400,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          const item = params[0]
          return `${item.name}<br/>掌握度：<b>${item.value}%</b>`
        }
      },
      grid: { left: 32, right: 32, top: 12, bottom: 12, containLabel: true },
      xAxis: {
        type: 'value',
        max: 100,
        axisLabel: { formatter: '{value}%', color: '#5a6f68' },
        splitLine: { lineStyle: { color: 'rgba(17, 88, 69, 0.08)' } }
      },
      yAxis: {
        type: 'category',
        data: items.map((item) => item.name),
        axisTick: { show: false },
        axisLine: { show: false },
        axisLabel: { color: '#26453d', width: 220, lineHeight: 18, fontSize: 12, formatter: (axisLabelText) => wrapAxisLabel(axisLabelText) }
      },
      series: [
        {
          type: 'bar',
          barWidth: 16,
          data: items.map((item) => ({
            value: item.value,
            itemStyle: { color: getProgressColor(item.value), borderRadius: [0, 10, 10, 0] }
          })),
          label: { show: true, position: 'right', formatter: '{c}%', color: '#355951', fontSize: 12 }
        }
      ]
    })
  }

  const loadProfileData = async () => {
    loading.value = true
    try {
      if (!courseStore.courseId) {
        resetProfileState()
        disposeMasteryChart()
        ElMessage.warning('请先选择课程')
        return
      }

      const rawProfilePayload = await getProfile(courseStore.courseId)
      if (!rawProfilePayload) {
        resetProfileState()
        disposeMasteryChart()
        return
      }

      profileSnapshot.value = normalizeProfilePayload(rawProfilePayload)
    } catch (error) {
      console.error('获取画像数据失败:', error)
      const status = error?.response?.status || error?.status
      if (status && status !== 404) ElMessage.error('获取画像数据失败，请稍后重试')
    } finally {
      loading.value = false
      if (masteryData.value.length) {
        await nextTick()
        initMasteryChart()
      } else {
        disposeMasteryChart()
      }
    }
  }

  const loadAISuggestions = async () => {
    try {
      if (!courseStore.courseId) {
        aiSuggestions.value = []
        aiLoadFailed.value = false
        assessmentReady.value = false
        return
      }

      const assessmentStatusPayload = await assessmentStore.fetchStatus(courseStore.courseId)
      assessmentReady.value = normalizeAssessmentReadyState(assessmentStatusPayload, courseStore.courseId).ready

      if (!assessmentReady.value) {
        aiSuggestions.value = []
        aiLoadFailed.value = false
        return
      }

      aiLoading.value = true
      aiLoadFailed.value = false
      aiProgress.start()
      aiSuggestions.value = normalizeProfileSuggestionList(await getAIProfileAnalysis(courseStore.courseId))
    } catch (error) {
      aiLoadFailed.value = true
      aiSuggestions.value = []
      console.error('获取 AI 建议失败:', error)
    } finally {
      aiProgress.complete()
      aiLoading.value = false
    }
  }

  const refreshAISuggestions = async () => {
    if (!courseStore.courseId) {
      ElMessage.warning('请先选择课程')
      return
    }

    aiLoading.value = true
    aiProgress.start()
    try {
      aiSuggestions.value = normalizeProfileSuggestionList(await getAIProfileAnalysis(courseStore.courseId, true))
      aiLoadFailed.value = false
      ElMessage.success('AI 建议已刷新')
    } catch (error) {
      console.error('刷新 AI 建议失败:', error)
      ElMessage.error('刷新 AI 建议失败，请稍后重试')
    } finally {
      aiProgress.complete()
      aiLoading.value = false
    }
  }

  const refreshProfile = async () => {
    if (!courseStore.courseId) {
      ElMessage.warning('请先选择课程')
      return
    }

    refreshing.value = true
    try {
      await refreshProfileWithAI(courseStore.courseId)
      await loadProfileData()
      await refreshAISuggestions()
      ElMessage.success('学习画像已刷新')
    } catch (error) {
      console.error('刷新画像失败:', error)
      ElMessage.error('刷新画像失败，请稍后重试')
    } finally {
      refreshing.value = false
    }
  }

  const handleResize = () => {
    if (masteryChart) masteryChart.resize()
  }

  watch(() => courseStore.courseId, (newValue, oldValue) => {
    if (newValue && newValue !== oldValue) {
      void loadProfileData()
      void loadAISuggestions()
    }

    if (!newValue) {
      resetProfileState()
      disposeMasteryChart()
    }
  })

  onMounted(() => {
    void loadProfileData()
    void loadAISuggestions()
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    aiProgress.reset()
    window.removeEventListener('resize', handleResize)
    disposeMasteryChart()
  })

  return {
    abilityAverage,
    abilityData,
    aiLoadFailed,
    aiLoading,
    aiProgressPercent,
    aiProgressStageText,
    aiSuggestions,
    assessmentReady,
    highMasteryCount,
    learnerTags,
    learningFocusLabel,
    loadAISuggestions,
    loading,
    lowMasteryCount,
    masteryAverage,
    masteryChartHeight,
    masteryChartRef,
    masteryData,
    masteryViewportHeight,
    mediumMasteryCount,
    noAssessmentDone,
    profileCompleteness,
    profileStrength,
    profileSummary,
    profileWeakness,
    refreshAISuggestions,
    refreshing,
    refreshProfile,
    strongestAbility,
    topWeakMasteries,
    username,
    weakestAbility
  }
}
