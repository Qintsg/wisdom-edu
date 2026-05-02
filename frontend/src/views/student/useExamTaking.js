import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExamDetail, submitExam as apiSubmitExam } from '@/api/student/exam'
import { submitNodeExam } from '@/api/student/learning'
import { useCourseStore } from '@/stores/course'
import {
  buildDefaultExamInfo,
  createEmptyAnswer,
  formatTime,
  normalizeExamDetail,
  normalizeFeedbackRouteId,
  normalizeIdentifier
} from './examTakingModels'

const storageKeyPrefix = 'exam_progress_'

export function useExamTaking() {
  const router = useRouter()
  const route = useRoute()
  const courseStore = useCourseStore()
  const loading = ref(true)
  const submitting = ref(false)
  const loadError = ref('')
  const examId = normalizeIdentifier(route.params['examId'])
  const nodeId = normalizeIdentifier(route.query['nodeId'])
  const examInfo = ref(buildDefaultExamInfo(examId))
  const remainingTime = ref(0)
  const currentIndex = ref(0)
  const answers = ref([])
  const questions = ref([])
  const answersKey = `${storageKeyPrefix}${examId}_answers`
  const timeKey = `${storageKeyPrefix}${examId}_time`
  let timer = null

  const isAnswered = (index) => {
    const answer = answers.value[index]
    if (Array.isArray(answer)) return answer.length > 0
    return answer !== '' && answer !== null && answer !== undefined
  }

  const respondedCount = computed(() => answers.value.filter((_, idx) => isAnswered(idx)).length)
  const currentQuestion = computed(() => questions.value[currentIndex.value])
  const isLastQuestion = computed(() => currentIndex.value === questions.value.length - 1)

  watch(answers, (newAnswers) => {
    localStorage.setItem(answersKey, JSON.stringify(newAnswers))
  }, { deep: true })

  const restoreProgress = () => {
    try {
      const savedAnswers = localStorage.getItem(answersKey)
      if (savedAnswers) {
        const parsed = JSON.parse(savedAnswers)
        if (Array.isArray(parsed) && parsed.length === questions.value.length) answers.value = parsed
      }

      const savedTime = localStorage.getItem(timeKey)
      if (savedTime) {
        const restoredTime = parseInt(savedTime, 10)
        if (!isNaN(restoredTime) && restoredTime > 0 && restoredTime < remainingTime.value) {
          remainingTime.value = restoredTime
        }
      }
    } catch (error) {
      console.error('恢复进度失败', error)
    }
  }

  const clearProgress = () => {
    localStorage.removeItem(answersKey)
    localStorage.removeItem(timeKey)
  }

  const loadExamData = async () => {
    loading.value = true
    loadError.value = ''
    try {
      if (!examId) throw new Error('missing-exam-id')

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

      remainingTime.value = examInfo.value.durationMinutes * 60
      restoreProgress()
      startTimer()
    } catch (error) {
      console.error('加载考试数据失败:', error)
      loadError.value = '加载作业数据失败，请返回重试'
      ElMessage.error('加载作业数据失败，请刷新重试')
    } finally {
      loading.value = false
    }
  }

  const startTimer = () => {
    if (timer) clearInterval(timer)

    timer = setInterval(() => {
      if (remainingTime.value > 0) {
        remainingTime.value--
        if (remainingTime.value % 5 === 0) localStorage.setItem(timeKey, remainingTime.value.toString())
      } else {
        clearInterval(timer)
        ElMessage.warning('作答时间到，系统正在自动提交...')
        forceSubmitExam()
      }
    }, 1000)
  }

  const prevQuestion = () => {
    if (currentIndex.value > 0) currentIndex.value--
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
    questions.value.forEach((question, index) => {
      const answer = answers.value[index]
      if (answer !== '' && answer !== undefined && answer !== null && !(Array.isArray(answer) && answer.length === 0)) {
        answersDict[question.questionId] = answer
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

  const submitCurrentAnswers = async () => {
    const submitData = {
      answers: buildAnswersDict(),
      course_id: courseStore.courseId
    }
    const result = await apiSubmitExam(examInfo.value.examId, submitData)

    if (nodeId) {
      try {
        await submitNodeExam(nodeId, examInfo.value.examId, submitData)
      } catch (error) {
        console.warn('节点测验状态更新失败:', error)
      }
    }

    clearProgress()
    return result
  }

  const submitExam = async () => {
    try {
      const unanswered = questions.value.length - respondedCount.value
      const message = unanswered > 0
        ? `已答 ${respondedCount.value} 道题，还有 ${unanswered} 道题未作答。确定要提交作业吗？提交后不可修改。`
        : `已答完全部 ${questions.value.length} 道题。确定要提交作业吗？提交后不可修改。`
      await ElMessageBox.confirm(message, '提交确认', {
        confirmButtonText: '确定提交',
        cancelButtonText: '检查一下',
        type: unanswered > 0 ? 'warning' : 'info'
      })

      submitting.value = true
      const result = await submitCurrentAnswers()
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
      const result = await submitCurrentAnswers()
      ElMessage.success('作业已自动提交！')
      await navigateToFeedback(result)
    } catch (error) {
      console.error('自动提交失败:', error)
      ElMessage.error('自动提交失败，请联系老师')
    } finally {
      submitting.value = false
    }
  }

  const handleBeforeUnload = (event) => {
    if (remainingTime.value > 0 && !submitting.value) {
      event.preventDefault()
      event.returnValue = ''
      return ''
    }
    return undefined
  }

  onMounted(() => {
    window.addEventListener('beforeunload', handleBeforeUnload)
    void loadExamData()
  })

  onUnmounted(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload)
    if (timer) clearInterval(timer)
  })

  return {
    answers,
    currentIndex,
    currentQuestion,
    examInfo,
    formatTime,
    goToQuestion,
    isAnswered,
    isLastQuestion,
    loadError,
    loadExamData,
    loading,
    nextQuestion,
    prevQuestion,
    questions,
    remainingTime,
    respondedCount,
    submitExam,
    submitting
  }
}
