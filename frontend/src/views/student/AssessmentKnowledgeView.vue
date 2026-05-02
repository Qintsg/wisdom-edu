<template>
  <div class="assessment-knowledge-view">
    <div class="assessment-layout">
      <!-- 主题目区域 -->
      <div class="question-area">
        <el-card v-loading="loading" class="question-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <span>知识测评</span>
                <el-tag size="small" type="info">{{ questions.length }} 题</el-tag>
                <el-tag size="small" type="warning" v-if="totalScore > 0">总分 {{ totalScore }}</el-tag>
              </div>
              <el-tag type="primary">{{ currentIndex + 1 }} / {{ questions.length || 1 }}</el-tag>
            </div>
          </template>

          <div v-if="questions.length > 0" class="question-content">
            <div class="question-meta">
              <el-tag size="small" type="success">{{ typeLabelMap[currentQuestionType] || '未知题型' }}</el-tag>
              <el-tag size="small" type="warning" v-if="currentQuestion?.score">{{ currentQuestion.score }} 分</el-tag>
              <el-tag size="small" v-if="currentQuestion?.difficulty">难度：{{ difficultyLabel(currentQuestion.difficulty)
              }}</el-tag>
            </div>
            <h3 class="question-title" v-html="displayTitle"></h3>

            <template v-if="['single_choice', 'true_false'].includes(currentQuestionType)">
              <el-radio-group v-model="currentAnswer" class="options-group" :key="currentQuestion?.id">
                <el-radio v-for="option in currentQuestion?.options" :key="`${currentQuestion?.id}-${option.id}`"
                  :value="option.id" class="option-item">
                  <span class="option-letter" v-if="option.letter">{{ option.letter }}.</span>
                  <span>{{ option.label }}</span>
                </el-radio>
              </el-radio-group>
            </template>

            <template v-else-if="currentQuestionType === 'multiple_choice'">
              <el-checkbox-group v-model="currentAnswer" class="options-group" :key="currentQuestion?.id">
                <el-checkbox v-for="option in currentQuestion?.options" :key="`${currentQuestion?.id}-${option.id}`"
                  :value="option.id" class="option-item">
                  <span class="option-letter" v-if="option.letter">{{ option.letter }}.</span>
                  <span>{{ option.label }}</span>
                </el-checkbox>
              </el-checkbox-group>
            </template>

            <template v-else-if="currentQuestionType === 'fill_blank'">
              <el-input v-model="currentAnswer" placeholder="请输入答案" clearable />
            </template>

            <template v-else-if="['short_answer', 'code'].includes(currentQuestionType)">
              <el-input v-model="currentAnswer" type="textarea" :rows="currentQuestionType === 'code' ? 10 : 6"
                placeholder="请输入答案" show-word-limit />
            </template>

            <template v-else>
              <el-alert type="info" :closable="false" title="暂不支持的题型，已为您保留题目内容" />
              <p class="question-title">{{ currentQuestion?.content }}</p>
            </template>
          </div>

          <div v-else class="empty-state">
            <el-empty description="暂无题目" />
          </div>

          <div class="question-footer">
            <div class="footer-actions">
              <el-button :disabled="currentIndex === 0" @click="prevQuestion">
                上一题
              </el-button>

            </div>
            <el-button type="primary" :disabled="!hasAnswer || submitting" :loading="submitting" @click="nextQuestion">
              {{ isLastQuestion ? '提交' : '下一题' }}
            </el-button>
          </div>

          <el-progress :percentage="progressPercent" :stroke-width="8" class="progress-bar" />
        </el-card>
      </div>

      <!-- 答题卡侧栏 -->
      <div class="answer-card-area" v-if="questions.length > 0">
        <el-card shadow="hover" class="answer-card">
          <template #header>
            <div class="card-header">
              <span>答题卡</span>
              <span class="answer-stats">已答: {{ answeredCount }} / {{ questions.length }}</span>
            </div>
          </template>
          <div class="answer-grid">
            <div v-for="(q, index) in questions" :key="q.id || index" class="answer-cell"
              :class="{ active: index === currentIndex, answered: isQuestionAnswered(index) }"
              @click="goToQuestion(index)">
              {{ index + 1 }}
            </div>
          </div>
          <div class="answer-legend">
            <div class="legend-item"><span class="legend-dot active"></span> 当前</div>
            <div class="legend-item"><span class="legend-dot answered"></span> 已答</div>
            <div class="legend-item"><span class="legend-dot"></span> 未答</div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 知识测评视图
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseStore } from '@/stores/course'
import { getKnowledgeAssessment, submitKnowledgeAssessment } from '@/api/student/assessment'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const courseStore = useCourseStore()

const loading = ref(false)
const submitting = ref(false)
const currentIndex = ref(0)
const currentAnswer = ref('')
const answers = ref([])

const questions = ref([])
const typeLabelMap = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题',
  code: '编程题'
}

const difficultyLabel = (level) => {
  if (!level) return '中等'
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[level] || level
}

const normalizeTextAnswer = (answer) => {
  return typeof answer === 'string' ? answer.trim() : ''
}

const normalizeKnowledgeOption = (option, optionIndex) => ({
  id: option?.value ?? option?.['option_id'] ?? option?.label ?? option?.content ?? `opt_${optionIndex + 1}`,
  label: option?.label ?? option?.content ?? option?.text ?? option?.value ?? option?.['option_id'] ?? `选项${optionIndex + 1}`,
  letter: option?.letter ?? String.fromCharCode(65 + optionIndex)
})

const normalizeKnowledgeQuestion = (question, questionIndex) => {
  const normalizedId = question?.['question_id'] ?? question?.id ?? questionIndex
  return {
    id: normalizedId,
    title: question?.title ?? question?.content ?? '未命名题目',
    content: question?.content ?? question?.title ?? '未命名题目',
    score: Number(question?.score || 0),
    difficulty: question?.difficulty ?? '',
    questionType: question?.['question_type'] ?? question?.type ?? 'single_choice',
    options: Array.isArray(question?.options)
      ? question.options.map((option, optionIndex) => normalizeKnowledgeOption(option, optionIndex))
      : []
  }
}

const totalScore = computed(() => {
  return questions.value.reduce((sum, q) => sum + (Number(q.score) || 0), 0)
})

/**
 * 加载知识测评题目
 */
const loadQuestions = async () => {
  const courseId = route.query['course_id'] || courseStore.courseId
  if (!courseId) {
    ElMessage.warning('请先选择课程')
    await router.push('/student/course-select')
    return
  }

  loading.value = true
  try {
    const res = await getKnowledgeAssessment(courseId)
    const receivedQuestions = Array.isArray(res?.['questions'])
      ? res['questions']
      : Array.isArray(res)
        ? res
        : []

    questions.value = receivedQuestions.map((question, questionIndex) => normalizeKnowledgeQuestion(question, questionIndex))

    currentIndex.value = 0
    answers.value = []
    setCurrentAnswerFromSaved()
    if (questions.value.length === 0) {
      ElMessage.info('该课程暂无知识测评题目')
    }
  } catch (error) {
    console.error('获取知识测评题目失败:', error)
    // 根据错误状态码显示不同提示
    if (error.response?.status === 404) {
      ElMessage.info('该课程暂未设置知识测评，请先完成能力评测和习惯问卷')
    } else {
      ElMessage.error('获取题目失败，请刷新重试')
    }
  } finally {
    loading.value = false
  }
}

const currentQuestion = computed(() => questions.value[currentIndex.value])
const currentQuestionType = computed(() => currentQuestion.value?.questionType || 'single_choice')
const isLastQuestion = computed(() => currentIndex.value === questions.value.length - 1)
const progressPercent = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round(((currentIndex.value + 1) / questions.value.length) * 100)
})
const displayTitle = computed(() => currentQuestion.value?.title || currentQuestion.value?.content || '')
const hasAnswer = computed(() => {
  const type = currentQuestionType.value
  if (type === 'multiple_choice') {
    return Array.isArray(currentAnswer.value) && currentAnswer.value.length > 0
  }
  if (['fill_blank', 'short_answer', 'code'].includes(type)) {
    return normalizeTextAnswer(currentAnswer.value).length > 0
  }
  return currentAnswer.value !== '' && currentAnswer.value !== null && currentAnswer.value !== undefined
})

const defaultAnswerByType = (type) => {
  if (type === 'multiple_choice') return []
  return ''
}

const setCurrentAnswerFromSaved = () => {
  const saved = answers.value[currentIndex.value]
  if (saved !== undefined) {
    currentAnswer.value = Array.isArray(saved) ? [...saved] : saved
  } else {
    currentAnswer.value = defaultAnswerByType(currentQuestionType.value)
  }
}

watch(currentQuestion, () => {
  setCurrentAnswerFromSaved()
})

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    setCurrentAnswerFromSaved()
  }
}

/** 跳转到指定题目（答题卡点击） */
const goToQuestion = (index) => {
  // 先保存当前答案
  answers.value[currentIndex.value] = Array.isArray(currentAnswer.value) ? [...currentAnswer.value] : currentAnswer.value
  currentIndex.value = index
  setCurrentAnswerFromSaved()
}

/** 判断指定题目是否已作答 */
const isQuestionAnswered = (index) => {
  const ans = answers.value[index]
  if (ans === undefined || ans === null || ans === '') return false
  if (Array.isArray(ans)) return ans.length > 0
  if (typeof ans === 'string') return normalizeTextAnswer(ans).length > 0
  return true
}

/** 已答题数 */
const answeredCount = computed(() => {
  return questions.value.filter((_, i) => isQuestionAnswered(i)).length
})

const nextQuestion = async () => {
  answers.value[currentIndex.value] = Array.isArray(currentAnswer.value) ? [...currentAnswer.value] : currentAnswer.value
  if (isLastQuestion.value) {
    await submitAnswers()
  } else {
    currentIndex.value++
    setCurrentAnswerFromSaved()
  }
}

/**
 * 提交答案
 */
const submitAnswers = async () => {
  if (submitting.value) return  // 防止重复提交
  const courseId = route.query['course_id'] || courseStore.courseId

  submitting.value = true
  try {
    const submissionData = {
      course_id: courseId,
      answers: questions.value.map((q, index) => ({
        question_id: q.id,
        answer: normalizeAnswerForSubmit(q.questionType, answers.value[index])
      }))
    }
    const result = await submitKnowledgeAssessment(submissionData)
    ElMessage.success('知识测评完成！正在生成学习报告…')
    // 缓存即时评分结果到sessionStorage（不含 feedback_report，异步生成中）
    if (result) {
      try {
        sessionStorage.setItem('assessment_report_data', JSON.stringify(result))
      } catch { /* ignore */ }
    }
    // 跳转到评测报告页，携带 course_id 以支持轮询
    await router.push({
      path: '/student/assessment/report',
      query: { course_id: courseId }
    })
  } catch (error) {
    console.error('提交知识测评失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadQuestions()
})

/**
 * 提交前的答案规整：
 * - 多选始终为数组
 * - 其他题型去掉首尾空白
 */
function normalizeAnswerForSubmit(type, answer) {
  if (type === 'multiple_choice') {
    if (Array.isArray(answer)) return answer
    if (answer === undefined || answer === null || answer === '') return []
    return [answer]
  }
  if (answer === undefined || answer === null) return ''
  if (typeof answer === 'string') return normalizeTextAnswer(answer)
  return answer
}
</script>

<style scoped src="./AssessmentKnowledgeView.css"></style>
