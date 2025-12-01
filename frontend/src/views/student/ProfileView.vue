<template>
  <div class="profile-view">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="15" animated />
    </div>

    <template v-else>
      <!-- Empty state appears only when the student has not produced any usable profile signals yet. -->
      <el-alert v-if="noAssessmentDone" type="info" :closable="false" class="empty-alert">
        <template #title>
          <span>您尚未完成初始评测，暂无画像数据</span>
        </template>
        <template #default>
          <p>完成能力测评和知识测评后，系统将为您生成个性化学习画像。</p>
          <el-button type="primary" size="small" @click="$router.push('/student/assessment')">
            前往测评中心
          </el-button>
        </template>
      </el-alert>

      <!-- Header collects identity, learner tags, and the manual refresh entry point. -->
      <el-card class="profile-header" shadow="hover">
        <div class="header-content">
          <el-avatar :size="80" class="user-avatar">
            {{ username.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-info">
            <h2>{{ username }} 的学习画像</h2>
            <p>基于学习数据、评测结果与知识追踪生成的个性化画像。</p>
            <div class="tags">
              <el-tag v-for="tag in learnerTags" :key="tag">{{ tag }}</el-tag>
            </div>
          </div>
          <el-button :icon="Refresh" type="primary" class="refresh-btn" :loading="refreshing" @click="refreshProfile">
            刷新画像
          </el-button>
        </div>
      </el-card>

      <div class="profile-overview-grid">
        <!-- Ability radar prefers the compact chart because dimensions are fixed and comparable. -->
        <el-card class="ability-card" shadow="hover">
          <template #header>
            <span>能力画像</span>
          </template>
          <div v-if="abilityData.length" class="ability-chart-wrapper">
            <RadarChart :data="abilityData" :max="100" height="270px" color="#6d927d" :show-value="true" />
          </div>
          <div v-else class="chart-placeholder">
            <el-icon>
              <DataAnalysis />
            </el-icon>
            <p>暂无能力数据，请先完成能力测评。</p>
            <el-button type="primary" size="small" @click="$router.push('/student/assessment/ability')">
              前往能力测评
            </el-button>
          </div>
        </el-card>

        <!-- Mastery area uses a scroll container so long knowledge lists keep readable labels. -->
        <el-card class="mastery-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>知识掌握度</span>
              <span class="mastery-meta">{{ masteryData.length }} 个知识点</span>
            </div>
          </template>

          <div v-if="masteryData.length" class="mastery-panel">
            <div class="mastery-summary">
              <div class="mastery-stat">
                <strong>{{ highMasteryCount }}</strong>
                <span>高掌握</span>
              </div>
              <div class="mastery-stat">
                <strong>{{ mediumMasteryCount }}</strong>
                <span>待巩固</span>
              </div>
              <div class="mastery-stat warning">
                <strong>{{ lowMasteryCount }}</strong>
                <span>薄弱项</span>
              </div>
            </div>

            <div class="mastery-chart-scroller" :style="{ maxHeight: masteryViewportHeight + 'px' }">
              <div ref="masteryChartRef" :style="{ height: masteryChartHeight + 'px', width: '100%' }"></div>
            </div>
          </div>

          <div v-else class="chart-placeholder">
            <el-icon>
              <DataAnalysis />
            </el-icon>
            <p>暂无知识数据，请先完成知识测评。</p>
            <el-button type="primary" size="small" @click="$router.push('/student/assessment/knowledge')">
              前往知识测评
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- Summary text is optional because some courses only return structured chart data. -->
      <el-card v-if="profileSummary || profileWeakness || profileStrength" class="summary-card" shadow="hover">
        <template #header>
          <span>画像总结</span>
        </template>
        <p v-if="profileSummary" class="summary-text">{{ profileSummary }}</p>
        <div v-if="profileStrength" class="summary-block">
          <el-tag type="success" effect="plain" size="small">学习优势</el-tag>
          <p class="summary-strength">{{ profileStrength }}</p>
        </div>
        <div v-if="profileWeakness" class="summary-block">
          <el-tag type="warning" effect="plain" size="small">薄弱环节</el-tag>
          <p class="summary-weakness">{{ profileWeakness }}</p>
        </div>
      </el-card>

      <!-- AI advice is intentionally isolated from the base profile so stale suggestions can retry safely. -->
      <el-card class="ai-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon>
                <MagicStick />
              </el-icon> AI 学习建议</span>
            <el-button v-if="assessmentReady" :icon="Refresh" text :loading="aiLoading" @click="refreshAISuggestions">
              刷新 AI 建议
            </el-button>
          </div>
        </template>
        <div v-if="!assessmentReady" class="chart-placeholder ai-placeholder">
          <el-icon>
            <DataAnalysis />
          </el-icon>
          <p>请先完成初始测评，系统才会生成 AI 学习建议。</p>
          <el-button type="primary" size="small" @click="$router.push('/student/assessment')">
            前往测评中心
          </el-button>
        </div>
        <div v-else-if="aiLoading" class="ai-loading">
          <el-progress :percentage="aiProgressPercent" :stroke-width="10" :show-text="true" status="" />
          <p class="ai-progress-stage">{{ aiProgressStageText }}</p>
        </div>
        <div v-else class="ai-content">
          <template v-if="aiLoadFailed">
            <el-alert type="warning" :closable="false" title="获取 AI 学习建议失败" show-icon />
            <div class="retry-row">
              <el-button type="primary" size="small" @click="loadAISuggestions">
                重新获取
              </el-button>
            </div>
          </template>
          <template v-else>
            <!-- Suggestions are rendered as a merged flat list because the API may split them across fields. -->
            <p>系统基于当前画像，推荐以下学习动作：</p>
            <ul>
              <li v-for="(suggestion, index) in aiSuggestions" :key="index">{{ suggestion }}</li>
            </ul>
            <el-empty v-if="!aiSuggestions.length" description="暂无学习建议" />
          </template>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { DataAnalysis, MagicStick, Refresh } from '@element-plus/icons-vue'
import RadarChart from '@/components/charts/RadarChart.vue'
import { getAIProfileAnalysis } from '@/api/student/ai'
import { getProfile, refreshProfileWithAI } from '@/api/student/profile'
import { useAIProgress } from '@/composables/useAIProgress'
import { useAssessmentStore } from '@/stores/assessment'
import { useCourseStore } from '@/stores/course'
import { useUserStore } from '@/stores/user'

/**
 * 统一收敛文本字段，避免模板和图表逻辑直接消费动态 payload。
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
 * 统一收敛数值字段，避免图表渲染出现 NaN。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 统一收敛布尔字段，兼容后端可能返回的字符串与数字。
 * @param {unknown} rawValue
 * @param {boolean} fallbackValue
 * @returns {boolean}
 */
const normalizeBoolean = (rawValue, fallbackValue = false) => {
  if (typeof rawValue === 'boolean') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return rawValue !== 0
  }
  if (typeof rawValue === 'string') {
    if (rawValue === 'true' || rawValue === '1') {
      return true
    }
    if (rawValue === 'false' || rawValue === '0') {
      return false
    }
  }
  return fallbackValue
}

/**
 * 将任意 payload 收敛为对象数组。
 * @param {unknown} rawValue
 * @returns {Array<Record<string, unknown>>}
 */
const normalizeListFromPayload = (rawValue) => {
  return Array.isArray(rawValue) ? rawValue : []
}

/**
 * 收敛任意对象 payload。
 * @param {unknown} rawValue
 * @returns {Record<string, unknown>}
 */
const normalizeObjectFromPayload = (rawValue) => {
  return rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue) ? rawValue : {}
}

/**
 * 将文本或文本数组统一收敛为字符串列表。
 * @param {unknown} rawValue
 * @returns {string[]}
 */
const normalizeTextList = (rawValue) => {
  if (Array.isArray(rawValue)) {
    return rawValue
      .map((item) => normalizeText(item).trim())
      .filter(Boolean)
  }

  const singleText = normalizeText(rawValue).trim()
  return singleText ? [singleText] : []
}

/**
 * 收敛百分比，兼容 0-1 与 0-100 两种后端表示。
 * @param {unknown} rawValue
 * @returns {number}
 */
const normalizePercentageValue = (rawValue) => {
  const parsedValue = normalizeNumber(rawValue)
  const percentageValue = parsedValue <= 1 ? parsedValue * 100 : parsedValue
  return Math.max(0, Math.min(100, Math.round(percentageValue)))
}

/**
 * @typedef {Object} AbilityMetricModel
 * @property {string} abilityName
 * @property {number} scoreValue
 */

/**
 * @typedef {Object} KnowledgeMasteryModel
 * @property {string} pointId
 * @property {string} pointName
 * @property {number} masteryPercent
 */

/**
 * @typedef {Object} ProfileSnapshotModel
 * @property {string[]} learnerTagList
 * @property {AbilityMetricModel[]} abilityEntries
 * @property {KnowledgeMasteryModel[]} masteryEntries
 * @property {string} summaryText
 * @property {string} weaknessText
 * @property {string} strengthText
 */

/**
 * 构造默认画像模型，保证页面始终只消费稳定字段。
 * @returns {ProfileSnapshotModel}
 */
const buildDefaultProfileSnapshot = () => ({
  learnerTagList: [],
  abilityEntries: [],
  masteryEntries: [],
  summaryText: '',
  weaknessText: '',
  strengthText: ''
})

const userStore = useUserStore()
const courseStore = useCourseStore()
const assessmentStore = useAssessmentStore()

// Page-level loading and retry states.
const loading = ref(true)
const aiLoading = ref(false)
const refreshing = ref(false)
const aiLoadFailed = ref(false)

// Profile sections stay separate so each card can degrade gracefully on partial data.
const profileSnapshot = ref(buildDefaultProfileSnapshot())
const aiSuggestions = ref([])
const assessmentReady = ref(false)

// ---- AI 伪造加载进度 (DEFENSE_DEMO_PROGRESS) ----
const aiProgress = useAIProgress({
  stages: [
    { at: 0, text: '正在准备分析...' },
    { at: 15, text: '正在读取学习记录...' },
    { at: 30, text: '正在评估能力画像...' },
    { at: 50, text: '正在生成个性化建议...' },
    { at: 75, text: '正在整合分析结果...' },
    { at: 90, text: '即将完成...' }
  ],
  tickInterval: 600,
})
// ---- END DEFENSE_DEMO_PROGRESS ----

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

// The empty-state banner waits until all profile sections are empty, not just one chart.
const noAssessmentDone = computed(() => !abilityData.value.length && !masteryData.value.length && !profileSummary.value)

// Mastery buckets drive both summary chips and color expectations in the bar chart.
const highMasteryCount = computed(() => masteryData.value.filter((item) => item.value >= 80).length)
const mediumMasteryCount = computed(() => masteryData.value.filter((item) => item.value >= 60 && item.value < 80).length)
const lowMasteryCount = computed(() => masteryData.value.filter((item) => item.value < 60).length)

// ECharts is kept outside Vue reactivity and resized manually.
const masteryChartRef = ref(null)
let masteryChart = null

// Chart height expands with data volume, while the viewport keeps the card from becoming too tall.
const masteryChartHeight = computed(() => Math.max(220, masteryData.value.length * 34 + 20))
const masteryViewportHeight = computed(() => Math.min(Math.max(220, masteryData.value.length * 24), 420))

// Axis labels wrap every 10 characters so dense Chinese labels stay readable in a narrow column.
function wrapAxisLabel(label) {
  const text = String(label || '')
  if (text.length <= 10) return text
  const segments = []
  for (let index = 0; index < text.length; index += 10) {
    segments.push(text.slice(index, index + 10))
  }
  return segments.join('\n')
}

// Backend ability keys mix localized names and internal codes, so normalize once here.
function getAbilityName(key) {
  const names = {
    '言语理解': '言语理解',
    '工作记忆': '工作记忆',
    '知觉推理': '知觉推理',
    '处理速度': '处理速度',
    logical_reasoning: '逻辑推理',
    memory: '记忆能力',
    analysis: '分析能力',
    innovation: '创新能力',
    comprehension: '理解能力',
    application: '应用能力'
  }
  return names[key] || key
}

/**
 * 收敛单条能力分值。
 * @param {string} rawKey
 * @param {unknown} rawValue
 * @returns {AbilityMetricModel}
 */
function normalizeAbilityEntry(rawKey, rawValue) {
  return {
    abilityName: getAbilityName(normalizeText(rawKey) || '综合能力'),
    scoreValue: normalizePercentageValue(rawValue)
  }
}

/**
 * 收敛单条知识掌握度。
 * @param {Record<string, unknown> | null | undefined} rawItem
 * @returns {KnowledgeMasteryModel}
 */
function normalizeKnowledgeMasteryEntry(rawItem) {
  return {
    pointId: normalizeText(rawItem?.point_id),
    pointName: normalizeText(rawItem?.point_name ?? rawItem?.name) || '未命名知识点',
    masteryPercent: normalizePercentageValue(rawItem?.mastery_rate)
  }
}

/**
 * 收敛画像主接口响应。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {ProfileSnapshotModel}
 */
function normalizeProfilePayload(rawPayload) {
  const abilityScoreMap = normalizeObjectFromPayload(rawPayload?.ability_scores)
  const strengthText = normalizeTextList(rawPayload?.strength).join('；')
  const weaknessText = normalizeTextList(rawPayload?.weakness).join('；')

  return {
    ...buildDefaultProfileSnapshot(),
    learnerTagList: normalizeTextList(rawPayload?.learner_tags),
    abilityEntries: Object.entries(abilityScoreMap)
      .filter(([, rawScore]) => rawScore != null)
      .map(([abilityKey, rawScore]) => normalizeAbilityEntry(abilityKey, rawScore)),
    masteryEntries: normalizeListFromPayload(rawPayload?.knowledge_mastery)
      .map((rawItem) => normalizeKnowledgeMasteryEntry(rawItem)),
    summaryText: normalizeText(rawPayload?.profile_summary),
    weaknessText,
    strengthText
  }
}

/**
 * 合并 AI 建议响应中的多种旧字段。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {string[]}
 */
function normalizeProfileSuggestionList(rawPayload) {
  const mergedSuggestions = [
    ...normalizeTextList(rawPayload?.suggestion),
    ...normalizeTextList(rawPayload?.recommendations),
    ...normalizeTextList(rawPayload?.suggestions)
  ]

  return [...new Set(mergedSuggestions)]
}

/**
 * 收敛测评完成状态，避免页面直接读取 courses/ability_done 等动态字段。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @param {number | string | null | undefined} activeCourseId
 * @returns {{ ready: boolean }}
 */
function normalizeAssessmentReadyState(rawPayload, activeCourseId) {
  const normalizedCourseId = normalizeNumber(activeCourseId, 0)
  const courseStatusList = normalizeListFromPayload(rawPayload?.courses)
  const activeCourseStatus = courseStatusList.find((courseStatus) => {
    return normalizeNumber(courseStatus?.course_id, 0) === normalizedCourseId
  })

  const abilityDone = normalizeBoolean(rawPayload?.ability_done ?? rawPayload?.ability_completed)
  const courseKnowledgeDone = activeCourseStatus
    ? normalizeBoolean(activeCourseStatus?.knowledge_done ?? activeCourseStatus?.knowledge_completed)
    : normalizeBoolean(rawPayload?.knowledge_done ?? rawPayload?.knowledge_completed)

  return {
    ready: abilityDone && courseKnowledgeDone
  }
}

/**
 * 重置画像与建议状态，防止切课后残留旧课程内容。
 */
function resetProfileState() {
  profileSnapshot.value = buildDefaultProfileSnapshot()
  aiSuggestions.value = []
  aiLoadFailed.value = false
  assessmentReady.value = false
}

// Shared thresholds keep chart colors aligned with mastery summary semantics.
function getProgressColor(scoreValue) {
  if (scoreValue >= 80) return '#22a06b'
  if (scoreValue >= 60) return '#6d927d'
  if (scoreValue >= 40) return '#dd8f1d'
  return '#d45050'
}

function disposeMasteryChart() {
  if (masteryChart) {
    masteryChart.dispose()
    masteryChart = null
  }
}

function initMasteryChart() {
  if (!masteryChartRef.value || !masteryData.value.length) {
    return
  }

  // Dispose before init to avoid duplicate canvases after course switches or refreshes.
  disposeMasteryChart()

  masteryChart = echarts.init(masteryChartRef.value)

  // Lowest-to-highest ordering makes weak areas appear first in the student scan path.
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
    grid: {
      left: 32,
      right: 32,
      top: 12,
      bottom: 12,
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%',
        color: '#5a6f68'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(17, 88, 69, 0.08)'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: items.map((item) => item.name),
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: {
        color: '#26453d',
        width: 220,
        lineHeight: 18,
        fontSize: 12,
        formatter: (axisLabelText) => wrapAxisLabel(axisLabelText)
      }
    },
    series: [
      {
        type: 'bar',
        barWidth: 16,
        data: items.map((item) => ({
          value: item.value,
          itemStyle: {
            color: getProgressColor(item.value),
            borderRadius: [0, 10, 10, 0]
          }
        })),
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          color: '#355951',
          fontSize: 12
        }
      }
    ]
  })
}

async function loadProfileData() {
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
    if (status && status !== 404) {
      ElMessage.error('获取画像数据失败，请稍后重试')
    }
  } finally {
    loading.value = false
    if (masteryData.value.length) {
      // Wait for the scroll container to render before creating the chart instance.
      await nextTick()
      initMasteryChart()
    } else {
      disposeMasteryChart()
    }
  }
}

async function loadAISuggestions() {
  try {
    if (!courseStore.courseId) {
      aiSuggestions.value = []
      aiLoadFailed.value = false
      assessmentReady.value = false
      return
    }

    // Assessment completion is checked first so the AI panel can show the correct gate state.
    const assessmentStatusPayload = await assessmentStore.fetchStatus(courseStore.courseId)
    assessmentReady.value = normalizeAssessmentReadyState(
      assessmentStatusPayload,
      courseStore.courseId
    ).ready

    if (!assessmentReady.value) {
      aiSuggestions.value = []
      aiLoadFailed.value = false
      return
    }

    aiLoading.value = true
    aiLoadFailed.value = false
    aiProgress.start()
    aiSuggestions.value = normalizeProfileSuggestionList(
      await getAIProfileAnalysis(courseStore.courseId)
    )
  } catch (error) {
    aiLoadFailed.value = true
    aiSuggestions.value = []
    console.error('获取 AI 建议失败:', error)
  } finally {
    aiProgress.complete()
    aiLoading.value = false
  }
}

async function refreshAISuggestions() {
  if (!courseStore.courseId) {
    ElMessage.warning('请先选择课程')
    return
  }

  aiLoading.value = true
  aiProgress.start()
  try {
    aiSuggestions.value = normalizeProfileSuggestionList(
      await getAIProfileAnalysis(courseStore.courseId, true)
    )
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

async function refreshProfile() {
  if (!courseStore.courseId) {
    ElMessage.warning('请先选择课程')
    return
  }

  refreshing.value = true
  try {
    // Full refresh pulls both the profile summary and the downstream AI recommendations back into sync.
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

function handleResize() {
  if (masteryChart) {
    masteryChart.resize()
  }
}

watch(() => courseStore.courseId, (newValue, oldValue) => {
  if (newValue && newValue !== oldValue) {
    // Course changes invalidate both charts and AI advice because all profile data is course-scoped.
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
  // Explicit disposal prevents hidden ECharts instances from surviving route changes.
  disposeMasteryChart()
})
</script>

<style scoped>
/* The page reads top-down: identity, charts, summary, then actionable AI advice. */
.profile-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-container {
  padding: 20px;
}

.empty-alert p {
  margin: 8px 0 12px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-avatar {
  background: var(--primary-color);
  color: #fff;
  font-size: 32px;
  font-weight: 700;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  margin: 0 0 8px;
  font-size: 28px;
}

.user-info p {
  margin: 0 0 14px;
  opacity: 0.92;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.refresh-btn {
  flex-shrink: 0;
}

.profile-overview-grid {
  /* Two-column balance gives the denser mastery chart slightly more room than the radar card. */
  display: grid;
  grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
  gap: 20px;
  align-items: start;
}

.ability-card,
.mastery-card,
.summary-card,
.ai-card {
  width: 100%;
}

.ability-chart-wrapper {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  text-align: center;
}

.chart-placeholder .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.summary-text {
  margin: 0;
  white-space: pre-line;
  color: var(--text-regular);
  line-height: 1.8;
  overflow-wrap: anywhere;
}

.summary-block {
  margin-top: 14px;
}

.summary-strength,
.summary-weakness {
  margin: 8px 0 0;
  line-height: 1.7;
  overflow-wrap: anywhere;
}

.summary-strength {
  color: var(--success-color);
}

.summary-weakness {
  color: var(--warning-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.mastery-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

.mastery-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mastery-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.mastery-stat {
  padding: 14px 12px;
  border-radius: 16px;
  background: var(--bg-soft);
  text-align: center;
}

.mastery-stat.warning {
  background: rgba(184, 141, 71, 0.14);
}

.mastery-stat strong {
  display: block;
  font-size: 26px;
  color: var(--text-primary);
}

.mastery-stat span {
  font-size: 13px;
  color: var(--text-secondary);
}

.mastery-chart-scroller {
  /* Long mastery lists scroll inside the card instead of pushing the full page excessively tall. */
  overflow: auto;
  padding-right: 8px;
  border-radius: 16px;
}

.ai-content p {
  margin: 0 0 12px;
  color: var(--text-regular);
  line-height: 1.8;
  overflow-wrap: anywhere;
}

.ai-content ul {
  margin: 0;
  padding-left: 20px;
}

.ai-content li {
  margin-bottom: 10px;
  color: var(--text-primary);
  line-height: 1.7;
  overflow-wrap: anywhere;
}

.ai-loading {
  padding: 16px 0;
}

.ai-progress-stage {
  margin-top: 10px;
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
  animation: stage-fade 0.5s ease;
}

@keyframes stage-fade {
  from {
    opacity: 0.4;
  }

  to {
    opacity: 1;
  }
}

.ai-placeholder {
  min-height: 180px;
}

.retry-row {
  margin-top: 12px;
  text-align: center;
}

@media (max-width: 1200px) {
  .profile-overview-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {

  /* Small screens stack summary stats vertically so labels do not fight for width. */
  .header-content {
    flex-direction: column;
    text-align: center;
  }

  .mastery-summary {
    grid-template-columns: 1fr;
  }
}
</style>
