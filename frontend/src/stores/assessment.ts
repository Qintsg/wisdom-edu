/**
 * 测评状态存储
 * 使用Composition API风格实现
 * 管理初始测评的状态、题目和答案
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getAssessmentStatus,
  getAbilityAssessment,
  submitAbilityAssessment,
  getHabitSurvey,
  submitHabitSurvey,
  getKnowledgeAssessment,
  submitKnowledgeAssessment,
  generateProfile,
  type AssessmentAnswerPayload,
  type AssessmentQuestion,
  type AssessmentQuestionResponse,
  type AssessmentStatusPayload
} from '@/api/student/assessment'

type AssessmentStage = 'ability' | 'habit' | 'knowledge'
type AssessmentStageValue = AssessmentStage | ''
type AssessmentAnswerMap = Record<string, string>

export const useAssessmentStore = defineStore('assessment', () => {
  // ==================== 状态定义 ====================

  /** 测评状态对象 */
  const status = ref<AssessmentStatusPayload | null>(null)
  /** 当前测评类型：ability/habit/knowledge */
  const currentType = ref<AssessmentStageValue>('')
  /** 当前测评的题目列表 */
  const questions = ref<AssessmentQuestion[]>([])
  /** 答案映射 { questionId: answer } */
  const answers = ref<AssessmentAnswerMap>({})
  /** 当前题目索引 */
  const currentIndex = ref(0)
  /** 加载状态 */
  const loading = ref(false)
  /** 提交状态 */
  const submitting = ref(false)
  // DEMO_EMBED: 简易缓存，避免短时间内重复请求测评状态
  let _statusCacheTime = 0
  let _statusCacheCourseId: number | null = null
  const STATUS_CACHE_TTL = 10000 // 10秒缓存有效期

  // ==================== 计算属性 ====================

  /** 是否需要完成能力评测 */
  const needsAbility = computed(() => !status.value?.ability_completed)
  /** 是否需要完成习惯问卷 */
  const needsHabit = computed(() => !status.value?.habit_completed)
  /** 是否需要完成知识测评 */
  const needsKnowledge = computed(() => !status.value?.knowledge_completed)
  /** 是否全部完成 */
  const allCompleted = computed(() =>
    status.value?.ability_completed &&
    status.value?.habit_completed &&
    status.value?.knowledge_completed
  )
  /** 当前答题进度百分比 */
  const progress = computed(() => {
    if (questions.value.length === 0) return 0
    return Math.round((Object.keys(answers.value).length / questions.value.length) * 100)
  })
  /** 当前题目对象 */
  const currentQuestion = computed<AssessmentQuestion | undefined>(() => questions.value[currentIndex.value])
  /** 是否为第一题 */
  const isFirstQuestion = computed(() => currentIndex.value === 0)
  /** 是否为最后一题 */
  const isLastQuestion = computed(() => currentIndex.value === questions.value.length - 1)
  /** 总题目数 */
  const totalQuestions = computed(() => questions.value.length)
  /** 已回答题目数 */
  const answeredCount = computed(() => Object.keys(answers.value).length)

  // ==================== 方法定义 ====================

  /**
   * 获取测评状态
   * @param {number} [courseId] - 课程ID，用于获取知识测评状态
   * @returns {Promise<Object|null>} 测评状态
   */
  async function fetchStatus(courseId?: number | null): Promise<AssessmentStatusPayload | null> {
    // DEMO_EMBED: 同一课程短时间内缓存命中直接返回
    if (
      _statusCacheTime &&
      _statusCacheCourseId === courseId &&
      Date.now() - _statusCacheTime < STATUS_CACHE_TTL &&
      status.value
    ) {
      return status.value
    }
    loading.value = true
    try {
      const data = await getAssessmentStatus(courseId)
      status.value = data
      _statusCacheTime = Date.now() // DEMO_EMBED
      _statusCacheCourseId = courseId ?? null // DEMO_EMBED
      return data
    } catch (error) {
      console.error('获取测评状态失败:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 开始测评
   * @param {string} type - 测评类型：ability/habit/knowledge
   * @param {number} [courseId] - 课程ID（知识测评必需）
   * @returns {Promise<boolean>} 是否成功获取题目
   */
  async function startAssessment(type: AssessmentStage, courseId?: number | null): Promise<boolean> {
    const assessmentFetcher: Record<AssessmentStage, () => Promise<AssessmentQuestionResponse | AssessmentQuestion[]>> = {
      ability: () => getAbilityAssessment(),
      habit: () => getHabitSurvey(),
      knowledge: () => getKnowledgeAssessment(courseId)
    }

    const fetcher = assessmentFetcher[type]

    loading.value = true
    currentType.value = type
    answers.value = {}
    currentIndex.value = 0

    try {
      const data = await fetcher()
      questions.value = Array.isArray(data) ? data : data.questions || []
      return true
    } catch (error) {
      console.error('获取测评题目失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 设置答案
   * @param {number} questionId - 题目ID
   * @param {string} answer - 答案
   */
  function setAnswer(questionId: number, answer: string): void {
    answers.value[String(questionId)] = answer
  }

  /**
   * 获取答案
   * @param {number} questionId - 题目ID
   * @returns {string|undefined} 答案
   */
  function getAnswer(questionId: number): string | undefined {
    return answers.value[String(questionId)]
  }

  /**
   * 上一题
   */
  function prevQuestion(): void {
    if (currentIndex.value > 0) {
      currentIndex.value--
    }
  }

  /**
   * 下一题
   */
  function nextQuestion(): void {
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
    }
  }

  /**
   * 跳转到指定题目
   * @param {number} index - 题目索引
   */
  function goToQuestion(index: number): void {
    if (index >= 0 && index < questions.value.length) {
      currentIndex.value = index
    }
  }

  /**
   * 提交测评
   * @param {number} [courseId] - 课程ID（知识测评必需）
   * @returns {Promise<Object>} 提交结果
   */
  async function submit(courseId?: number | null): Promise<unknown> {
    // 构造答案数组，使用基数10确保十进制解析
    const answerArray: AssessmentAnswerPayload[] = Object.entries(answers.value).map(([questionId, answer]) => ({
      question_id: parseInt(questionId, 10),
      answer
    }))

    const submitAssessmentMap: Record<AssessmentStage, () => Promise<unknown>> = {
      ability: () => submitAbilityAssessment({ answers: answerArray }),
      habit: () => submitHabitSurvey({ responses: answerArray }),
      knowledge: () => submitKnowledgeAssessment({
        course_id: courseId,
        answers: answerArray
      })
    }

    if (!currentType.value) {
      throw new Error('测评类型不能为空')
    }

    const submitAssessment = submitAssessmentMap[currentType.value]

    if (!submitAssessment) {
      throw new Error(`未知的测评类型: ${currentType.value}`)
    }

    submitting.value = true

    try {
      const result = await submitAssessment()

      // 更新状态
      await fetchStatus(courseId)

      return result
    } catch (error) {
      console.error('提交测评失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  /**
   * 生成学习者画像
   * @param {number} courseId - 课程ID
   * @returns {Promise<Object>} 生成结果
   */
  async function generateLearnerProfile(courseId: number): Promise<unknown> {
    loading.value = true
    try {
      return await generateProfile(courseId)
    } catch (error) {
      console.error('生成画像失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置测评状态
   * 清除当前测评的所有临时数据
   */
  function reset(): void {
    currentType.value = ''
    questions.value = []
    answers.value = {}
    currentIndex.value = 0
  }

  /**
   * 检查是否可以提交
   * @returns {boolean} 是否所有题目都已回答
   */
  function canSubmit(): boolean {
    return Object.keys(answers.value).length === questions.value.length
  }

  /**
   * 获取未回答的题目索引列表
   * @returns {Array<number>} 未回答题目的索引
   */
  function getUnansweredIndices(): number[] {
    return questions.value
      .map((question, index) => ({ index, id: question.question_id ?? question.id }))
      .filter(({ id }) => id == null || !answers.value[String(id)])
      .map(({ index }) => index)
  }

  return {
    status,
    currentType,
    questions,
    answers,
    currentIndex,
    loading,
    submitting,
    needsAbility,
    needsHabit,
    needsKnowledge,
    allCompleted,
    progress,
    currentQuestion,
    isFirstQuestion,
    isLastQuestion,
    totalQuestions,
    answeredCount,
    fetchStatus,
    startAssessment,
    setAnswer,
    getAnswer,
    prevQuestion,
    nextQuestion,
    goToQuestion,
    submit,
    generateLearnerProfile,
    reset,
    canSubmit,
    getUnansweredIndices
  }
})
