<template>
  <div class="profile-view">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="15" animated />
    </div>

    <template v-else>
      <!-- Empty state appears only when the student has not produced any usable profile signals yet. -->
      <div v-if="noAssessmentDone" class="assessment-empty-card">
        <div class="empty-orbit" aria-hidden="true" />
        <div>
          <p class="empty-eyebrow">Profile signals needed</p>
          <h3>完成初始测评后，画像会变得可解释</h3>
          <p>系统会结合能力测评、知识测评和学习轨迹生成画像，而不是只展示静态标签。</p>
        </div>
        <el-button type="primary" @click="$router.push('/student/assessment')">
          前往测评中心
        </el-button>
      </div>

      <!-- Header collects identity, learner tags, and the manual refresh entry point. -->
      <section class="profile-hero">
        <div class="hero-ambient" aria-hidden="true" />
        <div class="hero-main">
          <el-avatar :size="86" class="user-avatar">
            {{ username.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-info">
            <p class="hero-eyebrow">Learner Profile</p>
            <h2>{{ username }} 的学习画像</h2>
            <p>基于学习数据、评测结果与知识追踪生成的个性化画像。</p>
            <div class="tags">
              <el-tag v-for="tag in learnerTags" :key="tag" effect="plain">{{ tag }}</el-tag>
              <el-tag v-if="!learnerTags.length" type="info" effect="plain">等待更多学习信号</el-tag>
            </div>
          </div>
        </div>
        <div class="hero-side">
          <div class="profile-score-card">
            <span>画像完整度</span>
            <strong>{{ profileCompleteness }}%</strong>
            <el-progress :percentage="profileCompleteness" :stroke-width="8" :show-text="false" />
          </div>
          <el-button :icon="Refresh" type="primary" class="refresh-btn" :loading="refreshing" @click="refreshProfile">
            刷新画像
          </el-button>
        </div>
      </section>

      <div class="metric-strip">
        <div class="metric-card">
          <span>能力均分</span>
          <strong>{{ abilityAverage }}%</strong>
          <em>{{ strongestAbility?.name || '暂无能力数据' }}</em>
        </div>
        <div class="metric-card">
          <span>掌握均值</span>
          <strong>{{ masteryAverage }}%</strong>
          <em>{{ learningFocusLabel }}</em>
        </div>
        <div class="metric-card accent">
          <span>AI 建议</span>
          <strong>{{ aiSuggestions.length }}</strong>
          <em>{{ assessmentReady ? '可持续刷新' : '完成测评后生成' }}</em>
        </div>
      </div>

      <div class="profile-overview-grid">
        <!-- Ability radar prefers the compact chart because dimensions are fixed and comparable. -->
        <el-card class="ability-card" shadow="hover">
          <template #header>
            <div class="card-header stacked">
              <div>
                <span class="card-eyebrow">Ability radar</span>
                <strong>能力画像</strong>
              </div>
              <el-tag v-if="abilityData.length" type="success" effect="plain">{{ abilityData.length }} 项能力</el-tag>
            </div>
          </template>
          <div v-if="abilityData.length" class="ability-chart-wrapper">
            <RadarChart :data="abilityData" :max="100" height="270px" color="#6d927d" :show-value="true" />
          </div>
          <div v-if="abilityData.length" class="ability-insights">
            <div class="insight-pill strong">
              <span>优势能力</span>
              <strong>{{ strongestAbility?.name }}</strong>
              <em>{{ strongestAbility?.value }}%</em>
            </div>
            <div class="insight-pill focus">
              <span>优先提升</span>
              <strong>{{ weakestAbility?.name }}</strong>
              <em>{{ weakestAbility?.value }}%</em>
            </div>
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
            <div class="card-header stacked">
              <div>
                <span class="card-eyebrow">Knowledge map</span>
                <strong>知识掌握度</strong>
              </div>
              <span class="mastery-meta">{{ masteryData.length }} 个知识点</span>
            </div>
          </template>

          <div v-if="masteryData.length" class="mastery-panel">
            <div class="mastery-pulse">
              <div>
                <span>整体掌握均值</span>
                <strong>{{ masteryAverage }}%</strong>
              </div>
              <el-progress :percentage="masteryAverage" :stroke-width="12" :show-text="false" />
            </div>

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

            <div v-if="topWeakMasteries.length" class="focus-cluster">
              <span>优先突破</span>
              <el-tag v-for="item in topWeakMasteries" :key="item.pointId || item.name" type="warning" effect="plain">
                {{ item.name }} · {{ item.value }}%
              </el-tag>
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
          <div class="card-header stacked">
            <div>
              <span class="card-eyebrow">Interpretation</span>
              <strong>画像总结</strong>
            </div>
          </div>
        </template>
        <div class="summary-layout" :class="{ 'single-summary': !(profileStrength || profileWeakness) }">
          <p v-if="profileSummary" class="summary-text">{{ profileSummary }}</p>
          <div v-if="profileStrength || profileWeakness" class="summary-lenses">
            <div v-if="profileStrength" class="summary-block strength-block">
              <el-tag type="success" effect="plain" size="small">学习优势</el-tag>
              <p class="summary-strength">{{ profileStrength }}</p>
            </div>
            <div v-if="profileWeakness" class="summary-block weakness-block">
              <el-tag type="warning" effect="plain" size="small">薄弱环节</el-tag>
              <p class="summary-weakness">{{ profileWeakness }}</p>
            </div>
          </div>
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
            <p class="ai-lead">系统基于当前画像，推荐以下学习动作：</p>
            <div v-if="aiSuggestions.length" class="suggestion-grid">
              <article v-for="(suggestion, index) in aiSuggestions" :key="index" class="suggestion-card">
                <span>{{ String(index + 1).padStart(2, '0') }}</span>
                <p>{{ suggestion }}</p>
              </article>
            </div>
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

const strongestAbility = computed(() => {
  return [...abilityData.value].sort((left, right) => right.value - left.value)[0] || null
})

const weakestAbility = computed(() => {
  return [...abilityData.value].sort((left, right) => left.value - right.value)[0] || null
})

const topWeakMasteries = computed(() => {
  return [...masteryData.value]
    .sort((left, right) => left.value - right.value)
    .slice(0, 3)
})

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
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.profile-view::before {
  content: '';
  position: absolute;
  inset: -18px -16px auto;
  height: 260px;
  pointer-events: none;
  background:
    radial-gradient(circle at 14% 18%, rgba(15, 108, 189, 0.16), transparent 30%),
    radial-gradient(circle at 78% 6%, rgba(16, 124, 16, 0.12), transparent 28%);
  filter: blur(4px);
  z-index: 0;
}

.profile-view > * {
  position: relative;
  z-index: 1;
}

.loading-container {
  padding: 20px;
}

.assessment-empty-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 22px;
  border: 1px solid rgba(15, 108, 189, 0.16);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 18px 44px rgba(15, 58, 104, 0.08);
  backdrop-filter: blur(14px);
}

.empty-orbit {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(255, 255, 255, 0.92) 0 34%, transparent 36%),
    conic-gradient(from 120deg, #0f6cbd, #107c10, #f1a10a, #0f6cbd);
  box-shadow: 0 14px 30px rgba(15, 108, 189, 0.2);
}

.empty-eyebrow {
  margin: 0 0 4px;
  color: var(--primary-color);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.assessment-empty-card h3 {
  margin: 0 0 6px;
  color: var(--text-primary);
  font-size: 18px;
}

.assessment-empty-card p:not(.empty-eyebrow) {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.profile-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: 24px;
  overflow: hidden;
  padding: 28px;
  border: 1px solid rgba(15, 108, 189, 0.12);
  border-radius: 30px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(240, 247, 255, 0.82)),
    radial-gradient(circle at 90% 20%, rgba(91, 157, 237, 0.3), transparent 34%);
  box-shadow: 0 24px 64px rgba(15, 58, 104, 0.12);
}

.hero-ambient {
  position: absolute;
  width: 300px;
  height: 300px;
  right: -110px;
  top: -130px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(15, 108, 189, 0.18), transparent 64%);
}

.hero-main {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-avatar {
  flex-shrink: 0;
  background:
    linear-gradient(135deg, rgba(15, 108, 189, 0.95), rgba(16, 124, 16, 0.85));
  color: #fff;
  font-size: 34px;
  font-weight: 800;
  box-shadow: 0 18px 34px rgba(15, 108, 189, 0.24);
}

.user-info {
  flex: 1;
}

.user-info h2 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 30px;
  line-height: 1.16;
}

.user-info p {
  margin: 0 0 14px;
  max-width: 680px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.hero-eyebrow {
  margin: 0 0 8px !important;
  color: var(--primary-color) !important;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.refresh-btn {
  flex-shrink: 0;
}

.hero-side {
  display: grid;
  align-content: space-between;
  gap: 14px;
}

.profile-score-card {
  padding: 18px;
  border: 1px solid rgba(15, 108, 189, 0.1);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.profile-score-card span {
  display: block;
  color: var(--text-secondary);
  font-size: 13px;
}

.profile-score-card strong {
  display: block;
  margin: 6px 0 12px;
  color: var(--text-primary);
  font-size: 34px;
  line-height: 1;
}

.metric-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.metric-card {
  position: relative;
  overflow: hidden;
  padding: 18px 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 14px 34px rgba(15, 58, 104, 0.08);
}

.metric-card::after {
  content: '';
  position: absolute;
  right: -34px;
  bottom: -44px;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  background: rgba(15, 108, 189, 0.08);
}

.metric-card.accent::after {
  background: rgba(16, 124, 16, 0.12);
}

.metric-card span,
.metric-card em {
  display: block;
  color: var(--text-secondary);
  font-size: 13px;
  font-style: normal;
}

.metric-card strong {
  display: block;
  margin: 6px 0 4px;
  color: var(--text-primary);
  font-size: 32px;
  line-height: 1.1;
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

.ability-card :deep(.el-card__body),
.mastery-card :deep(.el-card__body),
.summary-card :deep(.el-card__body),
.ai-card :deep(.el-card__body) {
  padding: 22px;
}

.ability-chart-wrapper {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ability-insights {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 10px;
}

.insight-pill {
  padding: 14px;
  border-radius: 18px;
  background: var(--bg-soft-alt);
}

.insight-pill.strong {
  background: rgba(16, 124, 16, 0.1);
}

.insight-pill.focus {
  background: rgba(241, 161, 10, 0.12);
}

.insight-pill span,
.insight-pill em {
  display: block;
  color: var(--text-secondary);
  font-size: 12px;
  font-style: normal;
}

.insight-pill strong {
  display: block;
  margin: 4px 0;
  color: var(--text-primary);
  font-size: 16px;
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

.summary-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
  gap: 18px;
  align-items: start;
}

.summary-layout.single-summary {
  grid-template-columns: 1fr;
}

.summary-text {
  margin: 0;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(15, 108, 189, 0.08), rgba(255, 255, 255, 0.62));
  white-space: pre-line;
  color: var(--text-regular);
  line-height: 1.8;
  overflow-wrap: anywhere;
}

.summary-lenses {
  display: grid;
  gap: 12px;
}

.summary-block {
  padding: 16px;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(255, 255, 255, 0.68);
}

.strength-block {
  box-shadow: inset 4px 0 0 rgba(16, 124, 16, 0.45);
}

.weakness-block {
  box-shadow: inset 4px 0 0 rgba(241, 161, 10, 0.55);
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

.card-header.stacked strong {
  display: block;
  color: var(--text-primary);
  font-size: 17px;
}

.card-eyebrow {
  display: block;
  margin-bottom: 2px;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
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

.mastery-pulse {
  display: grid;
  grid-template-columns: 136px minmax(0, 1fr);
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(15, 108, 189, 0.08), rgba(16, 124, 16, 0.08));
}

.mastery-pulse span {
  color: var(--text-secondary);
  font-size: 12px;
}

.mastery-pulse strong {
  display: block;
  color: var(--text-primary);
  font-size: 30px;
  line-height: 1.1;
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

.focus-cluster {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(255, 244, 206, 0.42);
}

.focus-cluster > span {
  color: var(--warning-color);
  font-size: 13px;
  font-weight: 700;
}

.mastery-chart-scroller {
  /* Long mastery lists scroll inside the card instead of pushing the full page excessively tall. */
  overflow: auto;
  padding-right: 8px;
  border-radius: 16px;
}

.ai-content .ai-lead {
  margin: 0 0 12px;
  color: var(--text-regular);
  line-height: 1.8;
  overflow-wrap: anywhere;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.suggestion-card {
  position: relative;
  overflow: hidden;
  min-height: 108px;
  padding: 16px 16px 16px 52px;
  border: 1px solid rgba(15, 108, 189, 0.1);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.7);
}

.suggestion-card span {
  position: absolute;
  left: 14px;
  top: 14px;
  color: rgba(15, 108, 189, 0.28);
  font-size: 24px;
  font-weight: 900;
  line-height: 1;
}

.suggestion-card p {
  margin: 0;
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

  .profile-hero,
  .summary-layout {
    grid-template-columns: 1fr;
  }

  .hero-side {
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: end;
  }
}

@media (max-width: 768px) {

  /* Small screens stack summary stats vertically so labels do not fight for width. */
  .assessment-empty-card,
  .hero-main,
  .hero-side {
    flex-direction: column;
    text-align: center;
  }

  .assessment-empty-card,
  .profile-hero,
  .hero-side,
  .metric-strip,
  .ability-insights,
  .mastery-pulse,
  .suggestion-grid {
    grid-template-columns: 1fr;
  }

  .profile-hero {
    padding: 22px;
  }

  .hero-main {
    display: flex;
  }

  .profile-score-card,
  .refresh-btn {
    width: 100%;
  }

  .mastery-summary {
    grid-template-columns: 1fr;
  }
}
</style>
