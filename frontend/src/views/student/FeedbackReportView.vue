<template>
  <div class="feedback-report-view">
    <!-- Page-level navigation keeps the report in the homework flow. -->
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span>作业反馈报告</span>
      </template>
    </el-page-header>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="15" animated />
    </div>

    <template v-else>
      <!-- Score overview stays visible even while the AI report is still polling. -->
      <el-card class="score-card" shadow="hover">
        <div class="score-content">
          <div class="score-circle">
            <el-progress type="circle" :percentage="scorePercent" :width="152" :stroke-width="12" :color="scoreColor">
              <template #default>
                <div class="score-text">
                  <span class="score-value">{{ examResult.score }}</span>
                  <span class="score-unit">/ {{ examResult.totalScore }}</span>
                </div>
              </template>
            </el-progress>
          </div>
          <div class="score-info">
            <h2>{{ examResult.titleText }}</h2>
            <div class="score-stats">
              <div class="stat-item">
                <span class="stat-label">答对题数</span>
                <span class="stat-value correct">{{ examResult.correctCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">错误题数</span>
                <span class="stat-value wrong">{{ examResult.wrongCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">正确率</span>
                <span class="stat-value">{{ examResult.accuracy }}%</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">结果</span>
                <span class="stat-value" :class="examResult.passed ? 'correct' : 'wrong'">
                  {{ examResult.passed ? '通过' : '未通过' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="analysis-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon>
                <MagicStick />
              </el-icon> AI 智能分析</span>
            <el-tag :type="statusTagType" effect="plain">{{ statusLabel }}</el-tag>
          </div>
        </template>

        <div class="analysis-content">
          <!-- Status alert changes first so the student immediately knows whether to wait or retry. -->
          <el-alert v-if="feedbackStatus === 'pending'" :title="aiAnalysis.summary || '成绩已生成，AI 报告正在生成中...'" type="info"
            :closable="false" show-icon />
          <el-alert v-else-if="feedbackStatus === 'failed'" title="AI 报告生成失败，可以重新获取" type="warning" :closable="false"
            show-icon />
          <el-alert v-else :title="aiAnalysis.summary || '暂无分析摘要'" type="info" :closable="false" show-icon />

          <!-- Pending state keeps the page useful while background generation finishes. -->
          <div v-if="feedbackStatus === 'pending'" class="ai-pending">
            <el-progress :percentage="aiProgressPercent" :stroke-width="10" :show-text="true" status="" />
            <p class="ai-progress-stage">{{ aiProgressStageText }}</p>
          </div>

          <!-- Failed state exposes a single retry action instead of stale partial content. -->
          <div v-else-if="feedbackStatus === 'failed'" class="ai-retry">
            <el-button type="primary" size="small" :loading="aiRetrying" @click="retryAIFeedback">
              重新获取 AI 分析
            </el-button>
          </div>

          <template v-else>
            <!-- Each section is rendered independently because the backend may omit some fields. -->
            <div v-if="aiAnalysis.analysis" class="feedback-section">
              <h4>综合分析</h4>
              <p>{{ aiAnalysis.analysis }}</p>
            </div>

            <div v-if="aiAnalysis.knowledgeGaps.length" class="feedback-section">
              <h4>薄弱知识点</h4>
              <div class="tag-group">
                <el-tag v-for="(gap, index) in aiAnalysis.knowledgeGaps" :key="`gap-${index}`" type="warning"
                  effect="plain">
                  {{ gap }}
                </el-tag>
              </div>
            </div>

            <div v-if="aiAnalysis.suggestions.length" class="feedback-section">
              <h4>改进建议</h4>
              <ul>
                <li v-for="(suggestion, index) in aiAnalysis.suggestions" :key="`suggestion-${index}`">
                  {{ suggestion }}
                </li>
              </ul>
            </div>

            <!-- Task items may arrive as plain strings or richer objects, so the template normalizes both. -->
            <div v-if="aiAnalysis.nextTasks.length" class="feedback-section">
              <h4>下一步学习任务</h4>
              <ul>
                <li v-for="(task, index) in aiAnalysis.nextTasks" :key="`task-${index}`">
                  {{ typeof task === 'string' ? task : task.description || task.title || JSON.stringify(task) }}
                </li>
              </ul>
            </div>

            <!-- Mastery change cards expose before/after percentages without forcing chart reading. -->
            <div v-if="masteryChanges.length" class="feedback-section">
              <h4>知识掌握度变化</h4>
              <div class="mastery-change-list">
                <div v-for="item in masteryChanges" :key="item.knowledgePointId" class="mastery-change-item">
                  <span>{{ item.knowledgePointName }}</span>
                  <strong>{{ Math.round((item.masteryBefore || 0) * 100) }}% -> {{ Math.round((item.masteryAfter || 0) *
                    100) }}%</strong>
                </div>
              </div>
            </div>

            <!-- Duplicate conclusion text is hidden in script to avoid repeating the same sentence. -->
            <div v-if="displayConclusion" class="conclusion-section">
              <p>{{ displayConclusion }}</p>
            </div>
          </template>
        </div>
      </el-card>

      <el-card class="detail-card" shadow="hover">
        <template #header>
          <span>答题详情</span>
        </template>

        <el-collapse>
          <!-- Question review stays expanded per item so the student can inspect mistakes selectively. -->
          <el-collapse-item v-for="(question, index) in questionDetails" :key="question.questionId" :name="index">
            <template #title>
              <span>第 {{ index + 1 }} 题</span>
              <el-tag :type="question.isCorrect ? 'success' : 'danger'" size="small" class="title-tag">
                {{ question.isCorrect ? '正确' : '错误' }}
              </el-tag>
            </template>

            <p class="question-content">{{ question.contentText }}</p>

            <!-- Option styling highlights both correctness and the student's own selection path. -->
            <div v-if="question.optionList.length" class="option-review">
              <div v-for="option in question.optionList" :key="`${question.questionId}-${option.optionKey}`"
                class="option-row" :class="{ correct: option.isCorrectOption, selected: option.isStudentSelected }">
                <span class="option-prefix">{{ option.optionPrefix }}</span>
                <span class="option-text">{{ option.optionText }}</span>
                <el-tag v-if="option.isCorrectOption" size="small" type="success" effect="plain">正确选项</el-tag>
                <el-tag v-if="option.isStudentSelected" size="small" :type="question.isCorrect ? 'success' : 'warning'"
                  effect="plain">
                  你的选择
                </el-tag>
              </div>
            </div>

            <p>
              <span class="label">你的答案：</span>
              <span :class="question.isCorrect ? 'correct-answer' : 'wrong-answer'">
                {{ question.studentAnswerText || formatAnswer(question.studentAnswer) }}
              </span>
            </p>
            <p>
              <span class="label">正确答案：</span>
              <span class="correct-answer">
                {{ question.correctAnswerText || formatAnswer(question.correctAnswer) }}
              </span>
            </p>
            <p v-if="question.analysisText" class="analysis-note">
              <span class="label">解析：</span>{{ question.analysisText }}
            </p>
          </el-collapse-item>
        </el-collapse>

        <el-empty v-if="!questionDetails.length" description="暂无答题详情" />
      </el-card>

      <!-- Action bar keeps the likely next decisions grouped at the bottom of the report. -->
      <div class="action-bar">
        <el-button @click="goBack" size="large">返回作业列表</el-button>
        <el-button v-if="!examResult.passed" type="warning" size="large" @click="retryExam">
          再做一次
        </el-button>
        <el-button type="primary" size="large" @click="goToLearningPath">
          继续学习
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { generateFeedback, getExamResult, getFeedback } from '@/api/student/exam'

const router = useRouter()
const route = useRoute()

/**
 * 统一文本型动态字段，避免模板和逻辑直接消费未知结构。
 */
function normalizeText(value, fallback = '') {
  if (Array.isArray(value)) {
    return normalizeText(value[0], fallback)
  }
  if (typeof value === 'string') {
    const trimmedValue = value.trim()
    return trimmedValue || fallback
  }
  if (typeof value === 'number') {
    return String(value)
  }
  return fallback
}

/**
 * 统一数值型字段，非法值回退到安全默认值。
 */
function normalizeNumber(value, fallback = 0) {
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : fallback
}

/**
 * 统一路由参数与对象标识，兼容字符串、数字与数组值。
 */
function normalizeIdentifier(value, fallback = '') {
  if (Array.isArray(value)) {
    return normalizeIdentifier(value[0], fallback)
  }
  if (value === null || value === undefined) {
    return fallback
  }
  const normalizedValue = String(value).trim()
  return normalizedValue || fallback
}

/**
 * 统一数组载荷，保证 map/filter 只作用于数组本身。
 */
function normalizeListFromPayload(value) {
  return Array.isArray(value) ? value : []
}

const reportId = normalizeIdentifier(route.params['reportId'])

// Page-level request and retry states.
const loading = ref(true)
const aiRetrying = ref(false)

// Review payload shown directly in the report body.
const questionDetails = ref([])
const masteryChanges = ref([])

// AI report generation state is polled independently from exam scoring.
const feedbackStatus = ref('pending')
const pollAttempts = ref(0)
const pollTimer = ref(null)
const maxPollAttempts = 60

// ---- AI 伪造加载进度 (DEFENSE_DEMO_PROGRESS) ----
const aiProgressPercent = ref(0)
const aiProgressStageText = ref('正在准备分析环境...')
let aiProgressTimer = null
let aiProgressStageIdx = 0
const AI_PROGRESS_STAGES = [
  { at: 0, text: '正在准备分析环境...' },
  { at: 12, text: '正在解析答题数据...' },
  { at: 28, text: '正在评估知识掌握度...' },
  { at: 45, text: '正在生成个性化建议...' },
  { at: 65, text: '正在整合分析报告...' },
  { at: 82, text: '正在优化报告内容...' },
  { at: 92, text: '即将完成，请稍候...' }
]

function startAIProgress() {
  stopAIProgress()
  aiProgressPercent.value = 0
  aiProgressStageIdx = 0
  aiProgressStageText.value = AI_PROGRESS_STAGES[0].text
  aiProgressTimer = window.setInterval(() => {
    // 每次随机增加 1~4，上限 95
    aiProgressPercent.value = Math.min(aiProgressPercent.value + Math.floor(Math.random() * 4) + 1, 95)
    // 按阈值切换阶段文本
    while (aiProgressStageIdx < AI_PROGRESS_STAGES.length - 1 && aiProgressPercent.value >= AI_PROGRESS_STAGES[aiProgressStageIdx + 1].at) {
      aiProgressStageIdx++
    }
    aiProgressStageText.value = AI_PROGRESS_STAGES[aiProgressStageIdx].text
  }, 800)
}

function finishAIProgress() {
  stopAIProgress()
  aiProgressPercent.value = 100
  aiProgressStageText.value = 'AI 报告已生成'
}

function stopAIProgress() {
  if (aiProgressTimer) {
    window.clearInterval(aiProgressTimer)
    aiProgressTimer = null
  }
}
// ---- END DEFENSE_DEMO_PROGRESS ----

// Scorecard state is normalized from several backend response shapes.
function buildDefaultExamResult(targetReportId = '') {
  return {
    reportId: targetReportId,
    titleText: '',
    score: 0,
    totalScore: 100,
    correctCount: 0,
    wrongCount: 0,
    accuracy: 0,
    passed: false
  }
}

const examResult = ref(buildDefaultExamResult(reportId))

// AI analysis fields are flattened into stable arrays so the template can render defensively.
function buildDefaultAiAnalysis() {
  return {
    summary: '',
    analysis: '',
    knowledgeGaps: [],
    suggestions: [],
    nextTasks: [],
    conclusion: ''
  }
}

const aiAnalysis = ref(buildDefaultAiAnalysis())

/**
 * 选项回顾区统一成固定字段，模板不再直接读取 snake_case。
 */
function normalizeReviewOption(option, optionIndex) {
  const fallbackPrefix = String.fromCharCode(65 + (optionIndex % 26))
  const optionPrefix = normalizeText(
    option?.['letter'] ?? option?.['value'] ?? option?.['label'],
    fallbackPrefix
  )
  const optionText = normalizeText(
    option?.['label'] ?? option?.['content'] ?? option?.['value'],
    optionPrefix
  )
  return {
    optionKey: `${optionPrefix}-${optionIndex}`,
    optionPrefix,
    optionText,
    isCorrectOption: option?.['is_correct_option'] === true,
    isStudentSelected: option?.['is_student_selected'] === true
  }
}

/**
 * 单题回顾统一后，题目详情模板只依赖内部 camelCase 字段。
 */
function normalizeQuestionDetail(question, questionIndex) {
  return {
    questionId: normalizeIdentifier(question?.['question_id'], String(questionIndex + 1)),
    contentText: normalizeText(question?.['content'], `第 ${questionIndex + 1} 题`),
    isCorrect: question?.['is_correct'] === true,
    studentAnswer: question?.['student_answer'],
    correctAnswer: question?.['correct_answer'],
    studentAnswerText: normalizeText(question?.['student_answer_display']),
    correctAnswerText: normalizeText(question?.['correct_answer_display']),
    analysisText: normalizeText(question?.['analysis']),
    optionList: normalizeListFromPayload(question?.['options']).map((option, optionIndex) => (
      normalizeReviewOption(option, optionIndex)
    ))
  }
}

/**
 * 结果接口可能返回 question_details 或 questions，两种都收敛到同一结构。
 */
function normalizeQuestionDetails(resultData) {
  const detailedQuestionList = normalizeListFromPayload(resultData?.['question_details'])
  const fallbackQuestionList = normalizeListFromPayload(resultData?.['questions'])
  const questionList = detailedQuestionList.length > 0 ? detailedQuestionList : fallbackQuestionList
  return questionList.map((question, questionIndex) => normalizeQuestionDetail(question, questionIndex))
}

/**
 * 作业结果概览统一成内部模型，方便分数卡片和按钮逻辑复用。
 */
function normalizeExamResultPayload(resultData, targetReportId = '') {
  const normalizedQuestionDetails = normalizeQuestionDetails(resultData)
  const correctCount = Math.max(
    0,
    normalizeNumber(
      resultData?.['correct_count'],
      normalizedQuestionDetails.filter((item) => item.isCorrect).length
    )
  )
  const totalCount = Math.max(
    0,
    normalizeNumber(resultData?.['total_count'], normalizedQuestionDetails.length)
  )
  const accuracy = normalizeNumber(
    resultData?.['accuracy'],
    totalCount ? Math.round((correctCount / totalCount) * 1000) / 10 : 0
  )

  return {
    examResult: {
      reportId: targetReportId,
      titleText: normalizeText(resultData?.['exam_title'], '作业反馈'),
      score: normalizeNumber(resultData?.['score'], 0),
      totalScore: Math.max(normalizeNumber(resultData?.['total_score'], 100), 1),
      correctCount,
      wrongCount: Math.max(totalCount - correctCount, 0),
      accuracy,
      passed: resultData?.['passed'] === true
    },
    questionDetails: normalizedQuestionDetails
  }
}

/**
 * 任务建议可能是字符串或对象，统一成单行展示文本。
 */
function normalizeTaskText(task) {
  if (typeof task === 'string') {
    return normalizeText(task)
  }
  if (task && typeof task === 'object') {
    const preferredText = normalizeText(task['description'] ?? task['title'] ?? task['content'])
    return preferredText || JSON.stringify(task)
  }
  return ''
}

/**
 * 掌握度变化统一为 camelCase，模板展示 before/after 时更稳定。
 */
function normalizeMasteryChange(item, itemIndex) {
  return {
    knowledgePointId: normalizeIdentifier(item?.['knowledge_point_id'], String(itemIndex + 1)),
    knowledgePointName: normalizeText(item?.['knowledge_point_name'], `知识点 ${itemIndex + 1}`),
    masteryBefore: normalizeNumber(item?.['mastery_before'], 0),
    masteryAfter: normalizeNumber(item?.['mastery_after'], 0)
  }
}

/**
 * AI 报告接口统一成内部状态对象，减少页面上的条件分支噪音。
 */
function normalizeAiFeedbackPayload(feedbackData) {
  const overview = feedbackData && typeof feedbackData === 'object' && feedbackData['overview'] && typeof feedbackData['overview'] === 'object'
    ? feedbackData['overview']
    : {}
  const normalizedStatus = normalizeText(feedbackData?.['status'], 'completed') || 'completed'

  return {
    status: normalizedStatus,
    pollIntervalMs: Math.max(normalizeNumber(feedbackData?.['poll_interval_ms'], 2000), 500),
    analysis: {
      summary: normalizeText(
        feedbackData?.['summary'] ?? overview['summary'],
        normalizedStatus === 'pending' ? '成绩已生成，AI 报告正在生成中...' : '暂无分析摘要'
      ),
      analysis: normalizeText(feedbackData?.['analysis']),
      knowledgeGaps: normalizeListFromPayload(feedbackData?.['knowledge_gaps'] ?? overview['knowledge_gaps'])
        .map((item) => normalizeText(item))
        .filter(Boolean),
      suggestions: normalizeListFromPayload(feedbackData?.['recommendations'])
        .map((item) => normalizeTaskText(item))
        .filter(Boolean),
      nextTasks: normalizeListFromPayload(feedbackData?.['next_tasks'])
        .map((item) => normalizeTaskText(item))
        .filter(Boolean),
      conclusion: normalizeText(feedbackData?.['conclusion'])
    },
    masteryChanges: normalizeListFromPayload(feedbackData?.['mastery_changes'])
      .map((item, itemIndex) => normalizeMasteryChange(item, itemIndex))
  }
}

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

// The circle progress always stays within 0-100 even if the API total score changes.
const scorePercent = computed(() => {
  const totalScore = examResult.value.totalScore || 100
  return Math.min(Math.round((Number(examResult.value.score || 0) / totalScore) * 100), 100)
})

// Color thresholds mirror the pass/fail tone used elsewhere in the student UI.
const scoreColor = computed(() => {
  const percentage = scorePercent.value
  if (percentage >= 90) return '#22a06b'
  if (percentage >= 70) return '#129a74'
  if (percentage >= 60) return '#dd8f1d'
  return '#d45050'
})

// Some responses repeat summary and conclusion verbatim, so only unique conclusions are shown.
const displayConclusion = computed(() => {
  const conclusion = (aiAnalysis.value.conclusion || '').trim()
  const summary = (aiAnalysis.value.summary || '').trim()
  const analysis = (aiAnalysis.value.analysis || '').trim()
  if (!conclusion || conclusion === summary || conclusion === analysis) {
    return ''
  }
  return conclusion
})

function clearPollTimer() {
  if (pollTimer.value) {
    window.clearTimeout(pollTimer.value)
    pollTimer.value = null
  }
}

// Polling uses setTimeout instead of setInterval so each request waits for the previous one to finish.
function schedulePoll(delay = 2000) {
  clearPollTimer()
  if (feedbackStatus.value !== 'pending' || pollAttempts.value >= maxPollAttempts) {
    return
  }
  pollTimer.value = window.setTimeout(async () => {
    pollAttempts.value += 1
    await loadAIFeedback(reportId)
  }, delay)
}

// Answer formatting unifies primitive, array, and object payloads from different question types.
function formatAnswer(answer) {
  if (answer === null || answer === undefined || answer === '') return '未作答'
  if (typeof answer === 'boolean') return answer ? '正确' : '错误'
  if (Array.isArray(answer)) return answer.join('、')
  if (typeof answer === 'object') {
    if (Array.isArray(answer.answers)) return answer.answers.join('、')
    if (answer.answer !== undefined) return String(answer.answer)
  }
  return String(answer)
}

async function loadFeedbackReport() {
  loading.value = true
  try {
    if (!reportId) {
      throw new Error('missing-report-id')
    }

    const normalizedResult = normalizeExamResultPayload(await getExamResult(reportId), reportId)
    questionDetails.value = normalizedResult.questionDetails
    examResult.value = normalizedResult.examResult
  } catch (error) {
    console.error('获取反馈报告失败:', error)
    ElMessage.error('获取反馈报告失败')
  } finally {
    loading.value = false
  }

  if (!reportId) {
    return
  }
  pollAttempts.value = 0
  await loadAIFeedback(reportId)
}

async function loadAIFeedback(examId = reportId) {
  try {
    const normalizedExamId = normalizeIdentifier(examId, reportId)
    if (!normalizedExamId) {
      throw new Error('missing-report-id')
    }

    const normalizedFeedback = normalizeAiFeedbackPayload(await getFeedback(normalizedExamId))
    feedbackStatus.value = normalizedFeedback.status
    aiAnalysis.value = normalizedFeedback.analysis
    masteryChanges.value = normalizedFeedback.masteryChanges

    // Poll only while generation is still running; every terminal state clears the timer.
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
    if (!reportId) {
      throw new Error('missing-report-id')
    }

    // Force refresh tells the backend to enqueue a brand-new AI report.
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
</script>

<style scoped>
/* The view stacks score, analysis, detail, and next-step sections as one reading flow. */
.feedback-report-view {
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-container {
  padding: 20px;
}

.score-card {
  /* Soft hero styling separates the outcome summary from the denser review content. */
  background: var(--bg-hero-soft) !important;
}

.score-content {
  display: flex;
  align-items: center;
  gap: 36px;
}

.score-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.score-value {
  font-size: 34px;
  font-weight: 800;
  color: var(--text-primary);
}

.score-unit {
  font-size: 14px;
  color: var(--text-secondary);
}

.score-info {
  flex: 1;
}

.score-info h2 {
  margin: 0 0 18px;
  font-size: 26px;
  color: var(--text-primary);
}

.score-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.stat-item {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(18, 154, 116, 0.08);
}

.stat-label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.correct {
  color: var(--success-color);
}

.stat-value.wrong {
  color: var(--danger-color);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.ai-pending {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-pending p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.ai-retry {
  display: flex;
  justify-content: flex-start;
}

.feedback-section h4 {
  margin: 0 0 10px;
  font-size: 16px;
  color: var(--text-primary);
}

.feedback-section p,
.feedback-section li {
  margin: 0;
  line-height: 1.8;
  color: var(--text-regular);
}

.feedback-section ul {
  margin: 0;
  padding-left: 20px;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.mastery-change-list {
  display: grid;
  gap: 10px;
}

.mastery-change-item {
  /* Before/after values need wide spacing so changes scan like a mini diff. */
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(17, 88, 69, 0.06);
}

.mastery-change-item strong {
  color: var(--text-primary);
}

.conclusion-section {
  padding: 14px 16px;
  border-radius: 16px;
  background: var(--bg-soft);
  border: 1px solid rgba(18, 154, 116, 0.08);
}

.conclusion-section p {
  margin: 0;
  line-height: 1.8;
  color: var(--text-primary);
}

.question-content {
  margin: 0 0 12px;
  line-height: 1.8;
  color: var(--text-primary);
}

.option-review {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--bg-soft);
}

.option-row.correct {
  border: 1px solid rgba(34, 160, 107, 0.24);
}

.option-row.selected {
  box-shadow: inset 0 0 0 1px rgba(212, 80, 80, 0.16);
}

.option-prefix {
  font-weight: 700;
  color: var(--text-primary);
}

.option-text {
  flex: 1;
  min-width: 200px;
  line-height: 1.7;
  color: var(--text-regular);
}

.label {
  font-weight: 600;
  color: var(--text-secondary);
}

.correct-answer {
  color: var(--success-color);
}

.wrong-answer {
  color: var(--danger-color);
}

.analysis-note {
  margin-top: 8px;
}

.title-tag {
  margin-left: 12px;
}

.ai-progress-stage {
  margin-top: 12px;
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

.action-bar {
  /* Desktop keeps actions right-aligned; mobile collapses them into a simple stack. */
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 960px) {
  .score-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .score-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .score-stats {
    grid-template-columns: 1fr;
  }

  .action-bar {
    flex-direction: column;
  }
}
</style>
