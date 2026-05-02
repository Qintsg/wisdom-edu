<template>
  <div class="assessment-report-view">
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span>初始评测报告</span>
      </template>
    </el-page-header>

    <!-- 初始加载中（无评分数据时） -->
    <div v-if="loading && !report" style="text-align: center; padding: 60px;">
      <el-icon class="is-loading" :size="32">
        <Loading />
      </el-icon>
      <p style="color: #909399; margin-top: 12px;">正在加载评测报告…</p>
    </div>

    <template v-else-if="report">
      <!-- 总分概览 -->
      <el-card class="score-card" shadow="hover">
        <div class="score-overview">
          <div class="score-circle" :style="{ borderColor: scoreColor }">
            <span class="score-number">{{ report.score }}</span>
            <span class="score-total">/ {{ report.totalScore }}</span>
          </div>
          <div class="score-info">
            <p>答对 <b>{{ report.correctCount }}</b> / {{ report.totalCount }} 题</p>
            <p>正确率 <b>{{ accuracy }}%</b></p>
          </div>
        </div>
      </el-card>

      <!-- AI 反馈报告 - 可能还在异步生成中 -->
      <el-card class="feedback-card" shadow="hover" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span><el-icon>
                <MagicStick />
              </el-icon> AI 学习建议</span>
            <el-tag v-if="generating" type="warning" size="small" effect="plain" style="margin-left: 8px;">
              <el-icon class="is-loading">
                <Loading />
              </el-icon> 生成中…
            </el-tag>
          </div>
        </template>

        <!-- 正在生成中 -->
        <div v-if="generating" class="generating-hint">
          <el-icon class="is-loading" :size="24">
            <Loading />
          </el-icon>
          <div class="generating-text">
            <p class="generating-title">{{ aiProgress.stageText.value }}</p>
            <p class="generating-desc">AI 正在分析你的答题数据，生成学习路径和反馈报告，请稍候（约30~60秒）</p>
            <el-progress :percentage="aiProgress.progress.value" :show-text="true" :stroke-width="6"
              style="margin-top: 12px; max-width: 400px;" />
          </div>
        </div>

        <!-- 生成出错 -->
        <div v-else-if="generationError" class="generation-error">
          <el-alert :title="'部分内容生成失败'" type="warning" :description="generationError" show-icon :closable="false" />
          <el-button type="primary" size="small" style="margin-top: 12px;" @click="retryPoll">重试</el-button>
        </div>

        <!-- 已生成完成 - 展示反馈 -->
        <template v-else-if="feedback">
          <div v-if="feedback.analysis" class="feedback-section">
            <h4>综合分析</h4>
            <p>{{ feedback.analysis }}</p>
          </div>

          <div v-if="feedback.knowledgeGaps.length" class="feedback-section">
            <h4>薄弱知识点</h4>
            <el-tag v-for="(gap, idx) in feedback.knowledgeGaps" :key="idx" type="danger" effect="plain"
              style="margin: 4px;">{{ gap }}</el-tag>
          </div>

          <div v-if="feedback.recommendations?.length" class="feedback-section">
            <h4>改进建议</h4>
            <ul>
              <li v-for="(rec, idx) in feedback.recommendations" :key="idx">{{ rec }}</li>
            </ul>
          </div>

          <div v-if="feedback.nextTasks.length" class="feedback-section">
            <h4>下一步学习任务</h4>
            <ul>
              <li v-for="(task, idx) in feedback.nextTasks" :key="idx">{{ task }}</li>
            </ul>
          </div>

          <div v-if="feedback.encouragementText" class="encouragement">
            {{ feedback.encouragementText }}
          </div>
        </template>

        <!-- 反馈为空但生成已完成 -->
        <div v-else class="feedback-section">
          <p style="color: #909399;">暂无 AI 学习建议</p>
        </div>
      </el-card>

      <!-- 知识点掌握度 -->
      <el-card v-if="masteryItems.length" shadow="hover" style="margin-top: 20px;">
        <template #header><span>知识点掌握度</span></template>
        <div v-for="m in masteryItems" :key="m.id" class="mastery-item">
          <span class="mastery-name">{{ m.name }}</span>
          <el-progress :percentage="Math.round(m.masteryRate * 100)"
            :color="m.masteryRate >= 0.8 ? '#67c23a' : m.masteryRate >= 0.6 ? '#e6a23c' : '#f56c6c'" :stroke-width="16"
            style="flex: 1; margin: 0 12px;" />
          <span class="mastery-value">{{ Math.round(m.masteryRate * 100) }}%</span>
        </div>
      </el-card>

      <!-- 每题详情 -->
      <el-card v-if="questionDetails.length" shadow="hover" style="margin-top: 20px;">
        <template #header><span>答题详情</span></template>
        <el-collapse>
          <el-collapse-item v-for="(q, idx) in questionDetails" :key="q.id" :title="`第 ${idx + 1} 题`" :name="idx">
            <template #title>
              <span>第 {{ idx + 1 }} 题</span>
              <el-tag :type="q.isCorrect ? 'success' : 'danger'" size="small" style="margin-left: 8px;">
                {{ q.isCorrect ? '正确' : '错误' }}
              </el-tag>
            </template>
            <p class="question-content">{{ q.content }}</p>
            <div v-if="q.options?.length" class="option-review">
              <div v-for="(option, optionIdx) in q.options" :key="`${q.id}-${optionIdx}`" class="option-row"
                :class="{ correct: option.isCorrect, selected: option.isSelected }">
                <span class="option-prefix">{{ option.prefix }}</span>
                <span class="option-text">{{ option.label }}</span>
                <el-tag v-if="option.isCorrect" size="small" type="success" effect="plain">正确选项</el-tag>
                <el-tag v-if="option.isSelected" size="small" :type="q.isCorrect ? 'success' : 'warning'"
                  effect="plain">你的选择</el-tag>
              </div>
            </div>
            <p>
              <span class="label">你的答案：</span>
              <span :class="q.isCorrect ? 'correct-answer' : 'wrong-answer'">{{ q.studentAnswerDisplay ||
                formatAnswer(q.studentAnswer) }}</span>
            </p>
            <p>
              <span class="label">正确答案：</span>
              <span class="correct-answer">{{ q.correctAnswerDisplay || formatAnswer(q.correctAnswer) }}</span>
            </p>
            <p v-if="q.analysis" class="analysis">
              <span class="label">解析：</span>{{ q.analysis }}
            </p>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons" style="margin-top: 24px; text-align: center;">
        <el-button type="primary" @click="goToLearningPath" :disabled="generating">
          {{ generating ? '学习路径生成中…' : '开始学习' }}
        </el-button>
        <el-button @click="goBack">返回评测中心</el-button>
      </div>
    </template>

    <el-empty v-else description="暂无评测数据" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseStore } from '@/stores/course'
import { ElMessage } from 'element-plus'
import { MagicStick, Loading } from '@element-plus/icons-vue'
import { getKnowledgeResult } from '@/api/student/assessment'
import { useAIProgress } from '@/composables/useAIProgress'

const router = useRouter()
const route = useRoute()
const courseStore = useCourseStore()

const loading = ref(true)
const reportData = ref(null)
const generating = ref(false)
const generationError = ref(null)
const pollTimer = ref(null)

// --- DEMO_EMBED: 答辩演示伪进度（评测报告场景定制阶段文字） ---
const aiProgress = useAIProgress({
  maxDuration: 180_000,
  stages: [
    { at: 0, text: '正在为你生成个性化学习建议…' },
    { at: 10, text: '正在分析你的答题数据…' },
    { at: 25, text: '知识追踪模型评估中…' },
    { at: 40, text: '正在检测薄弱知识点…' },
    { at: 55, text: '生成学习反馈报告中…' },
    { at: 70, text: '规划后续学习路径…' },
    { at: 85, text: '即将完成，请稍候…' },
  ],
})

// 轮询间隔（DEMO_EMBED: 缩短至 1.5 秒提升演示响应感知；生产环境应恢复 3000）
const POLL_INTERVAL = 1500

// 评测结果结构来自多个后端阶段，先统一成页面内部稳定字段，避免模板散落 snake_case 访问。
const report = computed(() => normalizeReportData(reportData.value))

const feedback = computed(() => report.value?.feedback || null)

const masteryItems = computed(() => report.value?.mastery || [])

const questionDetails = computed(() => report.value?.questionDetails || [])

const accuracy = computed(() => {
  if (!report.value) return 0
  const { correctCount, totalCount } = report.value
  return totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0
})

const scoreColor = computed(() => {
  const pct = accuracy.value
  if (pct >= 80) return '#67c23a'
  if (pct >= 60) return '#e6a23c'
  return '#f56c6c'
})

const formatAnswer = (ans) => {
  if (ans === null || ans === undefined) return '未作答'
  if (typeof ans === 'boolean') return ans ? '正确' : '错误'
  if (Array.isArray(ans)) return ans.join(', ')
  return String(ans)
}

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeStringList = (value) => {
  if (!Array.isArray(value)) return []
  return value
    .map((item) => normalizeText(item))
    .filter((item) => item.length > 0)
}

const normalizeFeedback = (value) => {
  if (!value || typeof value !== 'object') return null
  return {
    analysis: normalizeText(value?.['analysis']),
    knowledgeGaps: normalizeStringList(value?.['knowledge_gaps']),
    recommendations: normalizeStringList(value?.['recommendations']),
    nextTasks: normalizeStringList(value?.['next_tasks']),
    encouragementText: normalizeText(value?.['encouragement'])
  }
}

const normalizeMasteryRate = (value) => {
  const parsedRate = Number(value)
  if (!Number.isFinite(parsedRate)) return 0
  return Math.min(Math.max(parsedRate, 0), 1)
}

const normalizeMasteryItem = (value, index) => {
  const masteryItem = value && typeof value === 'object' ? value : {}
  return {
    id: masteryItem?.['point_id'] ?? masteryItem?.['id'] ?? index,
    name: normalizeText(masteryItem?.['point_name'] ?? masteryItem?.['name']) || `知识点 ${index + 1}`,
    masteryRate: normalizeMasteryRate(masteryItem?.['mastery_rate'])
  }
}

const normalizeQuestionOption = (value, index) => {
  const option = value && typeof value === 'object' ? value : {}
  const rawLabel = option?.['label'] ?? option?.['content'] ?? option?.['value']
  return {
    id: option?.['option_id'] ?? option?.['id'] ?? `${index}`,
    prefix: normalizeText(option?.['letter'] ?? option?.['value']) || String.fromCharCode(65 + (index % 26)),
    label: normalizeText(rawLabel) || `选项 ${index + 1}`,
    isCorrect: Boolean(option?.['is_correct_option'] ?? option?.['is_correct']),
    isSelected: Boolean(option?.['is_student_selected'] ?? option?.['selected'])
  }
}

const normalizeQuestionDetail = (value, index) => {
  const question = value && typeof value === 'object' ? value : {}
  return {
    id: question?.['question_id'] ?? question?.['id'] ?? index,
    content: normalizeText(question?.['content']) || `第 ${index + 1} 题`,
    options: Array.isArray(question?.['options'])
      ? question['options'].map((option, optionIndex) => normalizeQuestionOption(option, optionIndex))
      : [],
    isCorrect: Boolean(question?.['is_correct']),
    studentAnswerDisplay: normalizeText(question?.['student_answer_display']),
    studentAnswer: question?.['student_answer'],
    correctAnswerDisplay: normalizeText(question?.['correct_answer_display']),
    correctAnswer: question?.['correct_answer'],
    analysis: normalizeText(question?.['analysis'])
  }
}

const normalizeReportData = (value) => {
  if (!value || typeof value !== 'object') return null

  const questionDetails = Array.isArray(value?.['question_details'])
    ? value['question_details'].map((question, index) => normalizeQuestionDetail(question, index))
    : []
  const mastery = Array.isArray(value?.['mastery'])
    ? value['mastery'].map((item, index) => normalizeMasteryItem(item, index))
    : []
  const totalCount = Number(value?.['total_count'] ?? questionDetails.length)
  const correctCount = Number(value?.['correct_count'] ?? questionDetails.filter((question) => question.isCorrect).length)
  const totalScore = Number(value?.['total_score'] ?? 100)

  return {
    score: Number(value?.['score'] ?? 0),
    totalScore: Number.isFinite(totalScore) ? totalScore : 100,
    correctCount: Number.isFinite(correctCount) ? correctCount : 0,
    totalCount: Number.isFinite(totalCount) ? totalCount : questionDetails.length,
    feedback: normalizeFeedback(value?.['feedback_report']),
    mastery,
    questionDetails
  }
}

const goBack = () => router.push('/student/assessment')
const goToLearningPath = () => router.push('/student/learning-path')

/**
 * 轮询获取异步生成结果
 */
const startPolling = (courseId) => {
  aiProgress.start() // DEMO_EMBED: 启动伪进度

  const doPoll = async () => {
    // 超时保护依赖 aiProgress 内部 maxDuration
    if (!aiProgress.isRunning.value && aiProgress.progress.value >= 95) {
      stopPolling()
      generating.value = false
      generationError.value = '生成超时，请稍后在此页面刷新查看'
      return
    }

    try {
      const result = await getKnowledgeResult(courseId)
      if (result) {
        // 更新评测数据（掌握度可能被 KT 模型更新）
        reportData.value = { ...reportData.value, ...result }
        generating.value = Boolean(result?.['generating'])

        if (!result?.['generating']) {
          // 生成完成
          stopPolling()
          aiProgress.complete() // DEMO_EMBED: 完成伪进度
          generationError.value = result?.['generation_error'] || null
          if (!result?.['generation_error']) {
            ElMessage.success('学习建议已生成')
          }
        }
      }
    } catch (err) {
      const status = err?.response?.status || err?.status
      if (status === 404) {
        stopPolling()
        generating.value = false
        reportData.value = null
        return
      }
      console.warn('轮询失败:', err)
      // 网络错误不终止轮询，继续重试
    }
  }

  pollTimer.value = setInterval(doPoll, POLL_INTERVAL)
  // 立即执行一次
  doPoll()
}

const stopPolling = () => {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

const retryPoll = () => {
  const courseId = route.query['course_id'] || courseStore.courseId
  if (!courseId) return
  generationError.value = null
  generating.value = true
  startPolling(courseId)
}

onMounted(() => {
  const courseId = route.query['course_id'] || courseStore.courseId

  try {
    // 先从 sessionStorage 读取即时评分结果
    const cached = sessionStorage.getItem('assessment_report_data')
    if (cached) {
      const data = JSON.parse(cached)
      reportData.value = data
      generating.value = Boolean(data?.['generating'])
      sessionStorage.removeItem('assessment_report_data')

      // 如果正在异步生成，启动轮询
      if (data?.['generating'] && courseId) {
        startPolling(courseId)
      }
    } else if (courseId) {
      // 没有缓存数据（页面刷新），直接从API获取
      generating.value = true
      startPolling(courseId)
    } else {
      ElMessage.info('评测数据可能已过期，请重新进行测评')
    }
  } catch {
    ElMessage.error('无法加载评测报告')
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped src="./AssessmentReportView.css"></style>
