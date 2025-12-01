<template>
  <div class="exam-view">
    <el-card class="page-header" shadow="never">
      <h2>在线作业</h2>
      <p>通过作业检验学习成果，获取详细反馈报告</p>
    </el-card>

    <el-tabs v-model="activeTab" class="exam-tabs">
      <el-tab-pane label="待参加" name="pending">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else class="exam-list">
          <el-card v-for="exam in pendingExams" :key="exam.examId" class="exam-card" shadow="hover">
            <div class="exam-content">
              <div class="exam-info">
                <h3>{{ exam.titleText }}</h3>
                <div class="exam-meta">
                  <span><el-icon>
                      <Clock />
                    </el-icon> {{ exam.durationMinutes }} 分钟</span>
                  <span><el-icon>
                      <Document />
                    </el-icon> 总分：{{ exam.totalScore }}</span>
                  <span><el-icon>
                      <Calendar />
                    </el-icon> 截止：{{ exam.deadlineText }}</span>
                </div>
              </div>
              <div class="exam-action">
                <el-button type="primary" @click="startExam(exam)">
                  开始作业
                </el-button>
              </div>
            </div>
          </el-card>

          <el-empty v-if="pendingExams.length === 0" description="暂无待参加的作业" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="已完成" name="completed">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else class="exam-list">
          <el-card v-for="exam in completedExams" :key="exam.examId" class="exam-card" shadow="hover">
            <div class="exam-content">
              <div class="exam-info">
                <h3>{{ exam.titleText }}</h3>
                <div class="exam-meta">
                  <span><el-icon>
                      <Trophy />
                    </el-icon> 得分：{{ exam.score }} / {{ exam.totalScore }}</span>
                  <span>
                    <el-tag :type="exam.passed ? 'success' : 'danger'" size="small">
                      {{ exam.passed ? '通过' : '未通过' }}
                    </el-tag>
                  </span>
                </div>
              </div>
              <div class="exam-action">
                <el-button @click="viewReport(exam)">
                  查看报告
                </el-button>
              </div>
            </div>
          </el-card>

          <el-empty v-if="completedExams.length === 0" description="暂无已完成的作业" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
/**
 * 作业列表视图
 * 展示待参加和已完成的作业列表
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '@/stores/course'
import { getExamList } from '@/api/student/exam'
import { ElMessage } from 'element-plus'
import { Clock, Document, Calendar, Trophy } from '@element-plus/icons-vue'

const router = useRouter()
const courseStore = useCourseStore()

/**
 * 统一文本型动态值，避免页面直接吃 snake_case 动态属性。
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
 * 统一数值型输入，非法值回退为安全默认值。
 */
function normalizeNumber(value, fallback = 0) {
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : fallback
}

/**
 * 统一 ID 与路由片段，兼容数字、字符串与空值。
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
 * 统一列表载荷，保证后续 map/filter 只处理数组。
 */
function normalizeListFromPayload(value) {
  return Array.isArray(value) ? value : []
}

// 加载状态
const loading = ref(true)

// 当前标签页
const activeTab = ref('pending')

// 待参加的作业
const pendingExams = ref([])

// 已完成的作业
const completedExams = ref([])

/**
 * 日期展示需要兼容空值和非法时间字符串。
 */
function formatDate(dateStr) {
  if (!dateStr) return '无截止日期'
  const parsedDate = new Date(dateStr)
  if (Number.isNaN(parsedDate.getTime())) {
    return '无截止日期'
  }
  return parsedDate.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

/**
 * 单个作业先规范化成内部模型，再交给模板和排序逻辑消费。
 */
function normalizeExamSummary(exam) {
  const examId = normalizeIdentifier(exam?.['exam_id'] ?? exam?.['id'])
  const startTime = normalizeText(exam?.['start_time'])
  const endTime = normalizeText(exam?.['end_time'])
  const submittedAt = normalizeText(exam?.['submitted_at'])
  return {
    examId,
    titleText: normalizeText(exam?.['title'], '未命名作业'),
    durationMinutes: Math.max(normalizeNumber(exam?.['duration'], 60), 1),
    totalScore: normalizeNumber(exam?.['total_score'], 0),
    deadlineText: formatDate(endTime),
    startTime,
    endTime,
    isSubmitted: exam?.['submitted'] === true,
    score: normalizeNumber(exam?.['score'], 0),
    passed: exam?.['passed'] === true,
    submittedAt
  }
}

const parseTimestamp = (value, fallback = Number.MAX_SAFE_INTEGER) => {
  const timestamp = value ? new Date(value).getTime() : fallback
  return Number.isFinite(timestamp) ? timestamp : fallback
}

const sortPendingExams = (items) => {
  return [...items].sort((leftItem, rightItem) => {
    return parseTimestamp(leftItem.endTime) - parseTimestamp(rightItem.endTime)
      || parseTimestamp(leftItem.startTime) - parseTimestamp(rightItem.startTime)
      || String(leftItem.titleText || '').localeCompare(String(rightItem.titleText || ''), 'zh-CN')
  })
}

const sortCompletedExams = (items) => {
  return [...items].sort((leftItem, rightItem) => {
    return parseTimestamp(rightItem.submittedAt, 0) - parseTimestamp(leftItem.submittedAt, 0)
      || parseTimestamp(rightItem.endTime, 0) - parseTimestamp(leftItem.endTime, 0)
      || String(leftItem.titleText || '').localeCompare(String(rightItem.titleText || ''), 'zh-CN')
  })
}

/**
 * 加载作业列表
 */
const loadExamList = async () => {
  // 缺少课程ID时不发起请求，避免白屏
  const courseId = normalizeIdentifier(courseStore.courseId)
  if (!courseId) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    // 拦截器已返回 data 本身
    const examListResponse = await getExamList(courseId)
    const examList = normalizeListFromPayload(examListResponse?.['exams']).map((exam) => (
      normalizeExamSummary(exam)
    ))

    // 分离待参加和已完成的考试（backend: submitted 表示已提交）
    pendingExams.value = sortPendingExams(examList
      .filter((exam) => !exam.isSubmitted))

    completedExams.value = sortCompletedExams(examList
      .filter((exam) => exam.isSubmitted))
  } catch (error) {
    console.error('获取作业列表失败:', error)
    ElMessage.error('获取作业列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 开始作业
 */
const startExam = (exam) => {
  router.push(`/student/exam/${exam.examId}`)
}

/**
 * 查看报告
 */
const viewReport = (exam) => {
  router.push(`/student/feedback/${exam.examId}`)
}

onMounted(() => {
  void loadExamList()
})
</script>

<style scoped>
.exam-view {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
  background: var(--bg-hero);
  border: none;
  color: var(--hero-text);
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  opacity: 0.9;
}

.exam-tabs {
  background: rgba(255, 255, 255, 0.88);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
}

.loading-container {
  padding: 20px;
}

.exam-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 0;
}

.exam-card {
  transition: all 0.3s;
}

.exam-card:hover {
  transform: translateY(-2px);
}

.exam-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exam-info {
  flex: 1;
}

.exam-info h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #303133;
}

.exam-desc {
  margin: 0 0 12px;
  font-size: 14px;
  color: #909399;
}

.exam-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: #606266;
}

.exam-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.exam-action {
  margin-left: 24px;
}

/* 响应式 */
@media (max-width: 768px) {
  .exam-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .exam-action {
    margin-left: 0;
    width: 100%;
  }

  .exam-action .el-button {
    width: 100%;
  }
}
</style>
