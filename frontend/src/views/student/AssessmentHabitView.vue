<template>
  <div class="assessment-habit-view">
    <el-card v-loading="loading" class="question-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>学习习惯问卷</span>
          <el-tag type="primary">{{ currentIndex + 1 }} / {{ questions.length || 1 }}</el-tag>
        </div>
      </template>

      <div v-if="questions.length > 0" class="question-content">
        <h3 class="question-title">{{ currentQuestion?.text || currentQuestion?.title || currentQuestion?.content }}
        </h3>
        <el-radio-group v-model="currentAnswer" class="options-group">
          <el-radio v-for="option in currentQuestion?.options" :key="option.id" :value="option.id" class="option-item">
            {{ option.label }}
          </el-radio>
        </el-radio-group>
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
        <el-button type="primary" :disabled="!currentAnswer" :loading="submitting" @click="nextQuestion">
          {{ isLastQuestion ? '提交' : '下一题' }}
        </el-button>
      </div>

      <el-progress :percentage="progressPercent" :stroke-width="8" class="progress-bar" />
    </el-card>
  </div>
</template>

<script setup>
/**
 * 习惯问卷视图
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHabitSurvey, submitHabitSurvey, getAssessmentStatus } from '@/api/student/assessment'
import { useCourseStore } from '@/stores/course'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const courseStore = useCourseStore()

const loading = ref(false)
const submitting = ref(false)
const currentIndex = ref(0)
const currentAnswer = ref('')
const answers = ref([])

const questions = ref([])

const normalizeHabitOption = (option) => ({
  id: option?.value ?? option?.['option_id'] ?? '',
  label: option?.label ?? option?.content ?? '未命名选项'
})

const normalizeHabitQuestion = (question) => ({
  id: question?.['question_id'] ?? question?.id ?? null,
  text: question?.text ?? question?.title ?? question?.content ?? '未命名题目',
  title: question?.title ?? question?.text ?? question?.content ?? '未命名题目',
  content: question?.content ?? question?.title ?? question?.text ?? '未命名题目',
  options: Array.isArray(question?.options) ? question.options.map(normalizeHabitOption) : []
})

/**
 * 加载习惯问卷题目
 */
const loadQuestions = async () => {
  loading.value = true
  try {
    const courseId = courseStore.courseId
    if (!courseId) {
      ElMessage.warning('请先选择课程')
      await router.push('/student/course-select')
      return
    }

    // 检查是否已完成习惯问卷
    try {
      const status = await getAssessmentStatus(courseId)
      if (status?.['habit_done'] || status?.['habit_completed']) {
        await ElMessageBox.confirm(
          '您已经完成过习惯问卷。重新填写将覆盖之前的结果，是否继续？',
          '提示',
          { confirmButtonText: '重新填写', cancelButtonText: '返回', type: 'warning' }
        )
        // confirm resolved, continue loading
      }
    } catch (err) {
      if (err === 'cancel') {
        await router.push('/student/assessment')
        return
      }
      // 检查状态失败不影响继续
    }

    const res = await getHabitSurvey(courseId)
    const rawQuestions = Array.isArray(res)
      ? res
      : Array.isArray(res?.['questions'])
        ? res['questions']
        : []
    questions.value = rawQuestions.map(normalizeHabitQuestion)
  } catch (error) {
    console.error('获取习惯问卷题目失败:', error)
    ElMessage.error('获取题目失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

const currentQuestion = computed(() => questions.value[currentIndex.value])
const isLastQuestion = computed(() => currentIndex.value === questions.value.length - 1)
const progressPercent = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round(((currentIndex.value + 1) / questions.value.length) * 100)
})

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    currentAnswer.value = answers.value[currentIndex.value] || ''
  }
}

const nextQuestion = async () => {
  answers.value[currentIndex.value] = currentAnswer.value
  if (isLastQuestion.value) {
    await submitAnswers()
  } else {
    currentIndex.value++
    currentAnswer.value = answers.value[currentIndex.value] || ''
  }
}

/**
 * 提交答案
 */
const submitAnswers = async () => {
  submitting.value = true
  try {
    const courseId = courseStore.courseId
    const submissionData = {
      course_id: courseId,
      responses: questions.value.map((q, index) => ({
        question_id: q.id,
        answer: answers.value[index] || ''
      }))
    }
    await submitHabitSurvey(submissionData)
    ElMessage.success('习惯问卷完成！')
    await router.push('/student/assessment')
  } catch (error) {
    console.error('提交习惯问卷失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadQuestions()
})
</script>

<style scoped>
.assessment-habit-view {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-content {
  padding: 20px 0;
}

.question-title {
  font-size: 18px;
  color: #303133;
  margin: 0 0 24px;
  line-height: 1.6;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-item {
  padding: 16px 20px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s;
  margin: 0;
}

.option-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.question-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.footer-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.progress-bar {
  margin-top: 20px;
}
</style>
