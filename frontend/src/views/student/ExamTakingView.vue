<template>
  <div class="exam-taking-view" v-loading.fullscreen.lock="loading || submitting"
    :element-loading-text="submitting ? '正在提交作业，成绩已同步计算，AI 报告将稍后补齐...' : '正在加载作业...'">
    <!-- 作业信息栏 (吸顶) -->
    <div class="exam-header-wrapper">
      <el-card class="exam-header" shadow="always" :body-style="{ padding: '15px 20px' }">
        <div class="header-content">
          <div class="exam-title">
            <el-icon class="icon">
              <Document />
            </el-icon>
            <h2>{{ examInfo.titleText }}</h2>
          </div>
          <div class="timer-wrapper" :class="{ 'urgent': remainingTime < 300 }">
            <el-icon>
              <Timer />
            </el-icon>
            <span class="timer-text">{{ formatTime(remainingTime) }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <div class="exam-container">
      <el-row :gutter="24">
        <!-- 题目区域 -->
        <el-col :xs="24" :lg="18">
          <el-card class="question-card" shadow="never" v-if="currentQuestion">
            <template #header>
              <div class="card-header">
                <span class="question-index">
                  Question {{ currentIndex + 1 }}
                  <span class="total">/ {{ questions.length }}</span>
                </span>
                <el-tag :type="currentQuestion?.questionTagType" effect="dark">
                  {{ currentQuestion?.questionTypeText }}
                </el-tag>
                <div class="score-tag">
                  分值: {{ currentQuestion?.score }}分
                </div>
              </div>
            </template>

            <div class="question-content">
              <div class="question-stem">
                {{ currentQuestion?.stem }}
              </div>

              <div class="answer-area">
                <!-- 单选题 -->
                <el-radio-group v-if="currentQuestion?.answerMode === 'singleChoice'" v-model="answers[currentIndex]"
                  class="options-group">
                  <el-radio v-for="option in currentQuestion?.optionList" :key="option.optionValue"
                    :value="option.optionValue" class="option-item" border>
                    <span class="option-label">{{ option.optionLabel }}.</span>
                    <span class="option-content">{{ option.optionContent }}</span>
                  </el-radio>
                </el-radio-group>

                <!-- 多选题 -->
                <el-checkbox-group v-else-if="currentQuestion?.answerMode === 'multipleChoice'"
                  v-model="answers[currentIndex]" class="options-group">
                  <el-checkbox v-for="option in currentQuestion?.optionList" :key="option.optionValue"
                    :value="option.optionValue" class="option-item" border>
                    <span class="option-label">{{ option.optionLabel }}.</span>
                    <span class="option-content">{{ option.optionContent }}</span>
                  </el-checkbox>
                </el-checkbox-group>

                <!-- 判断题 -->
                <el-radio-group v-else-if="currentQuestion?.answerMode === 'trueFalse'" v-model="answers[currentIndex]"
                  class="options-group">
                  <el-radio value="true" class="option-item" border>正确</el-radio>
                  <el-radio value="false" class="option-item" border>错误</el-radio>
                </el-radio-group>

                <!-- 填空题 -->
                <el-input v-else-if="currentQuestion?.answerMode === 'fillBlank'" v-model="answers[currentIndex]"
                  placeholder="请输入答案" class="fill-input" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />

                <!-- 简答题 -->
                <el-input v-else-if="currentQuestion?.answerMode === 'shortAnswer'" v-model="answers[currentIndex]"
                  type="textarea" :rows="6" placeholder="请输入答案解析" class="fill-input" />

                <!-- 默认按单选容错处理 -->
                <el-radio-group v-else v-model="answers[currentIndex]" class="options-group">
                  <el-radio v-for="option in currentQuestion?.optionList" :key="option.optionValue"
                    :value="option.optionValue" class="option-item" border>
                    {{ option.optionContent }}
                  </el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="question-footer">
              <el-button-group>
                <el-button :disabled="currentIndex === 0" @click="prevQuestion" :icon="ArrowLeft">
                  上一道题
                </el-button>
                <el-button type="primary" @click="nextQuestion">
                  {{ isLastQuestion ? '交卷' : '下一道题' }}
                  <el-icon v-if="!isLastQuestion" class="el-icon--right">
                    <ArrowRight />
                  </el-icon>
                </el-button>
              </el-button-group>

              <div class="progress-info">
                已答: {{ respondedCount }} / {{ questions.length }}
              </div>
            </div>
          </el-card>

          <el-empty v-else-if="loadError" :description="loadError">
            <el-button type="primary" @click="loadExamData">重新加载</el-button>
          </el-empty>

          <el-empty v-else description="暂无题目" />
        </el-col>

        <!-- 答题卡 (侧边固定) -->
        <el-col :xs="24" :lg="6" class="sidebar-col">
          <div class="sidebar-wrapper">
            <el-card class="answer-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span>答题卡</span>
                  <el-button type="primary" link :loading="submitting" :disabled="submitting" @click="submitExam">
                    提交作业
                  </el-button>
                </div>
              </template>

              <div class="answer-grid">
                <div v-for="(q, index) in questions" :key="q.questionId" class="answer-cell" :class="{
                  'is-answered': isAnswered(index),
                  'is-current': index === currentIndex
                }" @click="goToQuestion(index)">
                  {{ index + 1 }}
                </div>
              </div>

              <div class="answer-legend">
                <div class="legend-item"><span class="dot is-current"></span>当前</div>
                <div class="legend-item"><span class="dot is-answered"></span>已答</div>
                <div class="legend-item"><span class="dot"></span>未答</div>
              </div>
            </el-card>

            <!-- 作业说明或其他信息 -->
            <el-card class="info-card" shadow="never" style="margin-top: 15px;">
              <div class="info-text">
                <el-icon>
                  <InfoFilled />
                </el-icon>
                作答期间请勿切换页面或刷新，系统会自动保存您的答题进度。
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
/**
 * 作业进行中视图
 * 功能：题目展示、答题交互、倒计时、进度保存、提交
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Document, ArrowLeft, ArrowRight, InfoFilled } from '@element-plus/icons-vue'
import { getExamDetail, submitExam as apiSubmitExam } from '@/api/student/exam'
import { submitNodeExam } from '@/api/student/learning'
import { useCourseStore } from '@/stores/course'

const router = useRouter()
const route = useRoute()
const courseStore = useCourseStore()

/**
 * 统一文本型动态输入，避免模板和脚本直接消费未知结构。
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
 * 统一数值型输入，非法值回退到安全默认值。
 */
function normalizeNumber(value, fallback = 0) {
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : fallback
}

/**
 * 统一路由参数和对象标识，兼容数组与空值场景。
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
 * 统一列表载荷，避免后续 map/filter 直接碰撞未知类型。
 */
function normalizeListFromPayload(value) {
  return Array.isArray(value) ? value : []
}

const loading = ref(true)
const submitting = ref(false)
const loadError = ref('')
const examId = normalizeIdentifier(route.params['examId'])
const nodeId = normalizeIdentifier(route.query['nodeId']) // 学习路径节点ID，用于更新节点状态

/**
 * 把后端题型别名统一为前端内部枚举，页面只消费这一层。
 */
function normalizeQuestionType(type, optionCount = 0) {
  const normalizedType = normalizeText(type).toLowerCase()
  const questionTypeMap = {
    single: 'singleChoice',
    single_choice: 'singleChoice',
    multiple: 'multipleChoice',
    multiple_choice: 'multipleChoice',
    true_false: 'trueFalse',
    judge: 'trueFalse',
    fill_blank: 'fillBlank',
    fill: 'fillBlank',
    short_answer: 'shortAnswer',
    essay: 'shortAnswer'
  }
  if (questionTypeMap[normalizedType]) {
    return questionTypeMap[normalizedType]
  }
  return optionCount > 0 ? 'singleChoice' : 'shortAnswer'
}

// 作业信息
function buildDefaultExamInfo(targetExamId = '') {
  return {
    examId: targetExamId,
    titleText: 'Loading...',
    durationMinutes: 60
  }
}

const examInfo = ref(buildDefaultExamInfo(examId))

// 剩余时间（秒）
const remainingTime = ref(0)
let timer = null

// 当前题目索引
const currentIndex = ref(0)

// 答案数组
const answers = ref([])

// 题目列表
const questions = ref([])

// 存储Keys
const STORAGE_KEY_PREFIX = 'exam_progress_'
const answersKey = `${STORAGE_KEY_PREFIX}${examId}_answers`
const timeKey = `${STORAGE_KEY_PREFIX}${examId}_time`

// 监听答案变化，自动保存
watch(answers, (newAnswers) => {
  localStorage.setItem(answersKey, JSON.stringify(newAnswers))
}, { deep: true })

/**
 * 获取题目类型标签颜色
 */
function getQuestionTagType(type) {
  const types = {
    singleChoice: 'info',
    multipleChoice: 'warning',
    trueFalse: 'success',
    fillBlank: 'info',
    shortAnswer: 'danger'
  }
  return types[type] || 'info'
}

/**
 * 获取题目类型名称
 */
function getQuestionTypeName(type) {
  const names = {
    singleChoice: '单选',
    multipleChoice: '多选',
    trueFalse: '判断',
    fillBlank: '填空',
    shortAnswer: '简答'
  }
  return names[type] || '未知'
}

/**
 * 统一选项对象，兼容 value/label/content/text 等多种后端键名。
 */
function normalizeQuestionOption(option, optionIndex) {
  const fallbackLabel = String.fromCharCode(65 + (optionIndex % 26))
  const primitiveOption = typeof option === 'string' || typeof option === 'number'
    ? String(option)
    : ''
  const optionValue = normalizeText(
    option?.['value'] ?? option?.['label'] ?? primitiveOption,
    fallbackLabel
  )
  const optionContent = normalizeText(
    option?.['content'] ?? option?.['text'] ?? primitiveOption,
    optionValue
  )
  return {
    optionValue,
    optionLabel: optionValue,
    optionContent
  }
}

/**
 * 单题规范化后补齐模板需要的显示字段和答题模式。
 */
function normalizeExamQuestion(question, questionIndex) {
  const optionList = normalizeListFromPayload(question?.['options']).map((option, optionIndex) => (
    normalizeQuestionOption(option, optionIndex)
  ))
  const answerMode = normalizeQuestionType(question?.['type'] ?? question?.['question_type'], optionList.length)
  return {
    questionId: normalizeIdentifier(question?.['question_id'] ?? question?.['id'], String(questionIndex + 1)),
    stem: normalizeText(question?.['content'] ?? question?.['title'], `题目 ${questionIndex + 1}`),
    answerMode,
    questionTypeText: getQuestionTypeName(answerMode),
    questionTagType: getQuestionTagType(answerMode),
    score: normalizeNumber(question?.['score'], 0),
    optionList
  }
}

/**
 * 考试详情标准化后，页面只依赖 titleText/durationMinutes/questions 等内部字段。
 */
function normalizeExamDetail(payload, fallbackExamId = '') {
  const normalizedQuestions = normalizeListFromPayload(payload?.['questions']).map((question, questionIndex) => (
    normalizeExamQuestion(question, questionIndex)
  ))
  return {
    examId: normalizeIdentifier(payload?.['exam_id'] ?? payload?.['id'], fallbackExamId),
    titleText: normalizeText(payload?.['title'], '作业'),
    durationMinutes: Math.max(normalizeNumber(payload?.['duration'], 60), 1),
    questions: normalizedQuestions
  }
}

/**
 * 多选题保留数组占位，其余题型默认用空字符串即可。
 */
function createEmptyAnswer(question) {
  return question?.answerMode === 'multipleChoice' ? [] : ''
}

/**
 * 提交接口与反馈接口共用 exam_id 路由，统一从多形态结果中提取它。
 */
function normalizeFeedbackRouteId(payload, fallbackExamId = '') {
  if (payload && typeof payload !== 'object') {
    return normalizeIdentifier(payload, fallbackExamId)
  }
  const feedbackReport = payload && typeof payload === 'object'
    ? payload['feedback_report']
    : null
  return normalizeIdentifier(
    feedbackReport?.['exam_id']
    ?? feedbackReport?.['report_id']
    ?? payload?.['exam_id']
    ?? payload?.['report_id'],
    fallbackExamId
  )
}

/**
 * 判断题目是否已作答
 */
const isAnswered = (index) => {
  const answer = answers.value[index]
  if (Array.isArray(answer)) {
    return answer.length > 0
  }
  return answer !== '' && answer !== null && answer !== undefined
}

const respondedCount = computed(() => {
  return answers.value.filter((_, idx) => isAnswered(idx)).length
})

// 当前题目
const currentQuestion = computed(() => questions.value[currentIndex.value])

// 是否是最后一道题
const isLastQuestion = computed(() => currentIndex.value === questions.value.length - 1)

/**
 * 格式化时间
 */
const formatTime = (seconds) => {
  if (seconds < 0) return '00:00:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

/**
 * 加载此作业的本地进度
 */
const restoreProgress = () => {
  try {
    const savedAnswers = localStorage.getItem(answersKey)
    if (savedAnswers) {
      const parsed = JSON.parse(savedAnswers)
      if (Array.isArray(parsed) && parsed.length === questions.value.length) {
        answers.value = parsed
        // ElMessage.info('已恢复上次答题进度')
      }
    }

    const savedTime = localStorage.getItem(timeKey)
    if (savedTime) {
      const t = parseInt(savedTime, 10)
      if (!isNaN(t) && t > 0 && t < remainingTime.value) {
        remainingTime.value = t
      }
    }
  } catch (e) {
    console.error('恢复进度失败', e)
  }
}

/**
 * 清除本地进度
 */
const clearProgress = () => {
  localStorage.removeItem(answersKey)
  localStorage.removeItem(timeKey)
}

/**
 * 加载作业数据
 */
const loadExamData = async () => {
  loading.value = true
  loadError.value = ''
  try {
    if (!examId) {
      throw new Error('missing-exam-id')
    }

    const examDetail = normalizeExamDetail(await getExamDetail(examId), examId)

    examInfo.value = {
      examId: examDetail.examId,
      titleText: examDetail.titleText,
      durationMinutes: examDetail.durationMinutes
    }

    questions.value = examDetail.questions
    currentIndex.value = 0

    if (answers.value.length !== questions.value.length) {
      answers.value = questions.value.map((question) => createEmptyAnswer(question))
    }

    // 初始设置时间，后面会尝试从localStorage覆盖
    remainingTime.value = examInfo.value.durationMinutes * 60

    // 尝试恢复进度
    restoreProgress()

    // 启动计时器
    startTimer()

  } catch (error) {
    console.error('加载考试数据失败:', error)
    loadError.value = '加载作业数据失败，请返回重试'
    ElMessage.error('加载作业数据失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

/**
 * 启动作业计时器
 */
const startTimer = () => {
  if (timer) clearInterval(timer)

  timer = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
      // 每5秒保存一次时间
      if (remainingTime.value % 5 === 0) {
        localStorage.setItem(timeKey, remainingTime.value.toString())
      }
    } else {
      clearInterval(timer)
      ElMessage.warning('作答时间到，系统正在自动提交...')
      forceSubmitExam()
    }
  }, 1000)
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const nextQuestion = () => {
  if (isLastQuestion.value) {
    submitExam()
  } else {
    currentIndex.value++
  }
}

const goToQuestion = (index) => {
  currentIndex.value = index
}

const buildAnswersDict = () => {
  const answersDict = {}
  questions.value.forEach((q, i) => {
    const answer = answers.value[i]
    if (answer !== '' && answer !== undefined && answer !== null &&
      !(Array.isArray(answer) && answer.length === 0)) {
      answersDict[q.questionId] = answer
    }
  })
  return answersDict
}

const navigateToFeedback = async (payload = {}) => {
  const feedbackId = normalizeFeedbackRouteId(payload, examInfo.value.examId)
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
  await router.replace({
    name: 'FeedbackReport',
    params: { reportId: String(feedbackId) }
  })
}

const submitExam = async () => {
  try {
    const unanswered = questions.value.length - respondedCount.value
    const msg = unanswered > 0
      ? `已答 ${respondedCount.value} 道题，还有 ${unanswered} 道题未作答。确定要提交作业吗？提交后不可修改。`
      : `已答完全部 ${questions.value.length} 道题。确定要提交作业吗？提交后不可修改。`
    await ElMessageBox.confirm(
      msg,
      '提交确认',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '检查一下',
        type: unanswered > 0 ? 'warning' : 'info'
      }
    )

    submitting.value = true
    const submitData = {
      answers: buildAnswersDict(),
      course_id: courseStore.courseId
    }

    const result = await apiSubmitExam(examInfo.value.examId, submitData)

    // 如果是学习路径节点测验，同时提交节点测验结果以更新节点状态
    if (nodeId) {
      try {
        await submitNodeExam(nodeId, examInfo.value.examId, submitData)
      } catch (e) {
        console.warn('节点测验状态更新失败:', e)
      }
    }

    clearProgress() // 提交成功清除缓存
    ElMessage.success('作业提交成功！')
    await navigateToFeedback(result)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error('提交失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const forceSubmitExam = async () => {
  submitting.value = true
  try {
    const submitData = {
      answers: buildAnswersDict(),
      course_id: courseStore.courseId
    }
    const result = await apiSubmitExam(examInfo.value.examId, submitData)

    // 如果是学习路径节点测验，同时提交节点测验结果
    if (nodeId) {
      try {
        await submitNodeExam(nodeId, examInfo.value.examId, submitData)
      } catch (e) {
        console.warn('节点测验状态更新失败:', e)
      }
    }

    clearProgress()
    ElMessage.success('作业已自动提交！')
    await navigateToFeedback(result)
  } catch (error) {
    console.error('自动提交失败:', error)
    ElMessage.error('自动提交失败，请联系老师')
  } finally {
    submitting.value = false
  }
}

// 阻止页面刷新/关闭
const handleBeforeUnload = (e) => {
  if (remainingTime.value > 0 && !submitting.value) {
    e.preventDefault()
    e.returnValue = ''
    return ''
  }
}

onMounted(() => {
  window.addEventListener('beforeunload', handleBeforeUnload)
  void loadExamData()
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.exam-taking-view {
  min-height: 100vh;
  background: var(--bg-page);
  padding-bottom: 40px;
}

.exam-header-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  margin-bottom: 20px;
  background: transparent;
  /* 遮挡下方内容 */
}

.exam-header {
  border-radius: 0 0 24px 24px;
  border-top: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(18px);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exam-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.exam-title .icon {
  font-size: 24px;
  color: var(--primary-color);
}

.exam-title h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.timer-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: rgba(18, 154, 116, 0.1);
  padding: 6px 16px;
  border-radius: 999px;
  color: var(--primary-color);
  font-weight: bold;
  font-size: 18px;
  transition: all 0.3s;
}

.timer-wrapper.urgent {
  background-color: #fef0f0;
  color: #f56c6c;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }

  50% {
    opacity: 0.8;
  }

  100% {
    opacity: 1;
  }
}

.exam-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

.question-card {
  min-height: 500px;
  display: flex;
  flex-direction: column;
  border-radius: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-index {
  font-size: 18px;
  font-weight: 600;
}

.question-index .total {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.score-tag {
  color: #909399;
  font-size: 13px;
}

.question-content {
  padding: 18px 0 8px;
  flex: 1;
}

.question-stem {
  font-size: 18px;
  line-height: 1.8;
  color: var(--text-primary);
  margin: 0 auto 28px;
  font-weight: 700;
  max-width: 760px;
  text-align: center;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.option-item {
  margin: 0 !important;
  width: 100%;
  height: auto;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  white-space: normal;
  border-radius: 16px;
  border-color: rgba(18, 154, 116, 0.1) !important;
  background: rgba(255, 255, 255, 0.92);
}

.option-item :deep(.el-radio__label),
.option-item :deep(.el-checkbox__label) {
  display: flex;
  align-items: flex-start;
  line-height: 1.4;
  white-space: normal;
  flex: 1;
}

.option-label {
  font-weight: bold;
  margin-right: 8px;
  min-width: 20px;
}

.option-content {
  color: var(--text-regular);
}

.fill-input {
  max-width: 100%;
}

.question-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-info {
  font-size: 13px;
  color: #909399;
}

/* 侧边栏 */
.sidebar-col {
  /* 在大屏下吸顶 */
}

@media (min-width: 1200px) {
  .sidebar-wrapper {
    position: sticky;
    top: 100px;
    /* exam-header height + margin */
  }
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.answer-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.2s;
}

.answer-cell:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.answer-cell.is-answered {
  background-color: #f0f9eb;
  border-color: #67c23a;
  color: #67c23a;
}

.answer-cell.is-current {
  background-color: rgba(18, 154, 116, 0.1);
  border-color: var(--primary-color);
  color: var(--primary-color);
  font-weight: bold;
  box-shadow: 0 0 0 1px rgba(18, 154, 116, 0.35);
}

.answer-cell.is-answered.is-current {
  background-color: #f0f9eb;
  border-color: #409eff;
  /* Selected takes precedence for border */
  color: #67c23a;
}

.answer-legend {
  display: flex;
  justify-content: space-around;
  font-size: 12px;
  color: #909399;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #dcdfe6;
}

.dot.is-answered {
  background-color: #67c23a;
}

.dot.is-current {
  background-color: #409eff;
}

.info-text {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  display: flex;
  gap: 6px;
}
</style>
