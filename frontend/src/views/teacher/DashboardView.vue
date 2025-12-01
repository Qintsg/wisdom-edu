<template>
  <div class="dashboard-view">
    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :span="24">
        <el-card class="welcome-card" shadow="hover">
          <div class="welcome-content">
            <div class="welcome-text">
              <h2>欢迎回来，{{ username }}老师！</h2>
              <p>今天有 {{ pendingTasks.exams }} 份待开始的作业</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon>
              <User />
            </el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.studentCount }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <el-icon>
              <Reading />
            </el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.courseCount }}</div>
            <div class="stat-label">课程数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon>
              <School />
            </el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.classCount }}</div>
            <div class="stat-label">班级数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon>
              <Document />
            </el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.questionCount }}</div>
            <div class="stat-label">题库题目</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :lg="14">
        <el-card shadow="hover">
          <template #header>
            <span>近期作业</span>
          </template>
          <el-table :data="recentExams" style="width: 100%" empty-text="暂无作业数据">
            <el-table-column prop="name" label="作业名称" min-width="120" />
            <el-table-column prop="className" label="班级" min-width="80" />
            <el-table-column prop="date" label="日期" min-width="90" />
            <el-table-column prop="statusText" label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.statusTagType" size="small">
                  {{ row.statusText }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="hover">
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="router.push('/teacher/exams')">
              <div class="action-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon>
                  <Document />
                </el-icon>
              </div>
              <span class="action-label">作业管理</span>
            </div>
            <div class="action-item" @click="router.push('/teacher/classes')">
              <div class="action-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <el-icon>
                  <School />
                </el-icon>
              </div>
              <span class="action-label">班级管理</span>
            </div>
            <div class="action-item" @click="router.push('/teacher/resources')">
              <div class="action-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon>
                  <Reading />
                </el-icon>
              </div>
              <span class="action-label">资源管理</span>
            </div>
            <div class="action-item" @click="router.push('/teacher/knowledge')">
              <div class="action-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <el-icon>
                  <DataAnalysis />
                </el-icon>
              </div>
              <span class="action-label">知识图谱</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
/**
 * 教师端仪表盘视图
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useCourseStore } from '@/stores/course'
import { User, Reading, School, Document, DataAnalysis } from '@element-plus/icons-vue'
import { getMyClasses } from '@/api/teacher/class'
import { getMyCourses } from '@/api/teacher/course'
import { getExams } from '@/api/teacher/exam'
import { getQuestions } from '@/api/teacher/question'

// 常量定义
const DASHBOARD_VISIBLE_EXAM_COUNT = 5
const DASHBOARD_EXAMS_FETCH_SIZE = 20
const DASHBOARD_QUESTIONS_PAGE_SIZE = 1

const router = useRouter()
const userStore = useUserStore()
const courseStore = useCourseStore()
const username = computed(() => userStore.username || '教师')
const loading = ref(false)

const buildDefaultStats = () => ({
  studentCount: 0,
  courseCount: 0,
  classCount: 0,
  questionCount: 0
})

const buildDefaultPendingTasks = () => ({ homework: 0, exams: 0 })

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeNumber = (value, fallback = 0) => {
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : fallback
}

const normalizeIdentifier = (value) => {
  const normalizedText = normalizeText(value)
  if (!normalizedText) return null
  const parsedValue = Number(normalizedText)
  return Number.isFinite(parsedValue) ? parsedValue : normalizedText
}

const normalizeListFromPayload = (value, key, mapper) => {
  const payload = value && typeof value === 'object' ? value : {}
  const sourceList = Array.isArray(payload?.[key])
    ? payload[key]
    : Array.isArray(value)
      ? value
      : []
  return sourceList.map((item, index) => mapper(item, index))
}

const normalizePaginatedList = (value, key, mapper) => {
  const items = normalizeListFromPayload(value, key, mapper)
  const payload = value && typeof value === 'object' ? value : {}
  return {
    items,
    total: normalizeNumber(payload?.['total'], items.length)
  }
}

const normalizeClassSummary = (value, index) => {
  const classItem = value && typeof value === 'object' ? value : {}
  return {
    id: normalizeIdentifier(classItem?.['class_id'] ?? classItem?.['id']) ?? index,
    name: normalizeText(classItem?.['class_name'] ?? classItem?.['name']) || `班级 ${index + 1}`,
    studentCount: normalizeNumber(classItem?.['student_count'] ?? classItem?.['studentCount'])
  }
}

const normalizeCourseSummary = (value, index) => {
  const courseItem = value && typeof value === 'object' ? value : {}
  return {
    id: normalizeIdentifier(courseItem?.['course_id'] ?? courseItem?.['id']) ?? index,
    name: normalizeText(courseItem?.['course_name'] ?? courseItem?.['name']) || `课程 ${index + 1}`
  }
}

const mapExamStatus = (value) => {
  if (value === 'finished' || value === 'ended') {
    return { text: '已结束', tagType: 'info', isPending: false }
  }
  if (value === 'ongoing' || value === 'active') {
    return { text: '进行中', tagType: 'warning', isPending: false }
  }
  return { text: '待开始', tagType: 'success', isPending: true }
}

const normalizeRecentExamSummary = (value, index, classNameById) => {
  const exam = value && typeof value === 'object' ? value : {}
  const statusMeta = mapExamStatus(normalizeText(exam?.['status']))
  const targetClassId = normalizeIdentifier(exam?.['target_class'] ?? exam?.['class_id'])
  return {
    id: normalizeIdentifier(exam?.['exam_id'] ?? exam?.['id']) ?? index,
    name: normalizeText(exam?.['title'] ?? exam?.['exam_name'] ?? exam?.['name']) || `作业 ${index + 1}`,
    className: normalizeText(exam?.['class_name']) || (targetClassId !== null ? classNameById.get(String(targetClassId)) || '-' : '-'),
    date: formatDate(exam?.['start_time'] ?? exam?.['created_at']),
    statusText: statusMeta.text,
    statusTagType: statusMeta.tagType,
    isPending: statusMeta.isPending
  }
}

// 统计数据
const stats = ref(buildDefaultStats())

const recentExams = ref([])
const pendingTasks = ref(buildDefaultPendingTasks())

/**
 * 加载仪表盘数据
 */
const loadDashboardData = async () => {
  loading.value = true
  try {
    stats.value = buildDefaultStats()
    recentExams.value = []
    pendingTasks.value = buildDefaultPendingTasks()

    // 先获取班级和课程
    const [classesResult, coursesResult] = await Promise.allSettled([
      getMyClasses(),
      getMyCourses()
    ])

    const normalizedClasses = classesResult.status === 'fulfilled'
      ? normalizeListFromPayload(classesResult.value, 'classes', (classItem, index) => normalizeClassSummary(classItem, index))
      : []
    const normalizedCourses = coursesResult.status === 'fulfilled'
      ? normalizeListFromPayload(coursesResult.value, 'courses', (courseItem, index) => normalizeCourseSummary(courseItem, index))
      : []

    const classNameById = new Map(normalizedClasses.map((classItem) => [String(classItem.id), classItem.name]))

    stats.value.classCount = normalizedClasses.length
    stats.value.studentCount = normalizedClasses.reduce((totalStudentCount, classItem) => totalStudentCount + classItem.studentCount, 0)
    stats.value.courseCount = normalizedCourses.length

    const activeCourseId = normalizeIdentifier(courseStore.courseId) ?? (normalizedCourses.length > 0 ? normalizedCourses[0].id : null)

    // 只有有课程ID时才查询考试和题目
    if (activeCourseId) {
      const [examsResult, questionsResult] = await Promise.allSettled([
        getExams(activeCourseId, { page: 1, page_size: DASHBOARD_EXAMS_FETCH_SIZE, size: DASHBOARD_EXAMS_FETCH_SIZE }),
        getQuestions({ course_id: activeCourseId, page: 1, page_size: DASHBOARD_QUESTIONS_PAGE_SIZE, size: DASHBOARD_QUESTIONS_PAGE_SIZE })
      ])

      if (examsResult.status === 'fulfilled') {
        const examList = normalizePaginatedList(
          examsResult.value,
          'exams',
          (exam, index) => normalizeRecentExamSummary(exam, index, classNameById)
        )
        recentExams.value = examList.items.slice(0, DASHBOARD_VISIBLE_EXAM_COUNT)
        pendingTasks.value.exams = examList.items.filter((exam) => exam.isPending).length
      }

      if (questionsResult.status === 'fulfilled') {
        const questionList = normalizePaginatedList(questionsResult.value, 'questions', (question) => question)
        stats.value.questionCount = questionList.total
      }
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error('加载仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const parsedDate = new Date(dateStr)
  return Number.isNaN(parsedDate.getTime()) ? '-' : parsedDate.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadDashboardData()
})

// 课程切换时重新加载数据
watch(() => courseStore.courseId, (newId, oldId) => {
  if (newId !== oldId) {
    loadDashboardData()
  }
})
</script>
<style scoped>
.dashboard-view {
  padding: 0;
}

.stats-row,
.content-row {
  margin-top: 20px;
}

.welcome-card {
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5f8a 100%);
  border: none;
  color: #fff;
}

.welcome-text h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.welcome-text p {
  margin: 0;
  opacity: 0.9;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 18px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.action-item:hover {
  background: #e8f4fd;
  transform: translateY(-2px);
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
}

.action-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .welcome-text h2 {
    font-size: 18px;
  }

  .stat-card :deep(.el-card__body) {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }

  .stat-value {
    font-size: 22px;
  }
}
</style>
