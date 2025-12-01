<template>
  <div class="dashboard-view" v-loading="loading">
    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :span="24">
        <el-card class="welcome-card" shadow="hover">
          <div class="welcome-content">
            <div class="welcome-text">
              <h2>欢迎回来，{{ username }}！</h2>
              <p>{{ greeting }}</p>
            </div>
            <div class="welcome-actions">
              <el-button type="primary" @click="goToLearningPath">
                <el-icon>
                  <Guide />
                </el-icon>
                继续学习
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 未选课程提示 -->
    <el-alert v-if="!courseStore.courseId" title="请先选择课程" type="info" show-icon description="请在左上角的课程选择器中选择一门课程以查看学习数据"
      :closable="false" style="margin-top: 20px;" />

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-1" shadow="hover">
          <div class="stat-icon"><el-icon>
              <TrendCharts />
            </el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ learningProgress }}%</div>
            <div class="stat-label">学习进度</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-2" shadow="hover">
          <div class="stat-icon"><el-icon>
              <Checked />
            </el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ masteredPoints }}</div>
            <div class="stat-label">已掌握知识点</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-3" shadow="hover">
          <div class="stat-icon"><el-icon>
              <Timer />
            </el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ studyHours }}h</div>
            <div class="stat-label">本周学习时长</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-4" shadow="hover">
          <div class="stat-icon"><el-icon>
              <Finished />
            </el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ completedTasks }}</div>
            <div class="stat-label">完成任务数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <!-- 学习路径概览 -->
      <el-col :xs="24" :lg="16">
        <el-card class="path-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>学习路径</span>
              <el-button type="primary" link @click="goToLearningPath">查看全部</el-button>
            </div>
          </template>
          <div v-if="learningNodes.length" class="path-content">
            <el-timeline>
              <el-timeline-item v-for="node in learningNodes" :key="node.id"
                :type="node.status === 'completed' ? 'success' : node.status === 'current' ? 'primary' : 'info'"
                :hollow="node.status !== 'completed'">
                <div class="timeline-node">
                  <span class="node-title">{{ node.title }}</span>
                  <el-tag :type="getNodeTagType(node.status)" size="small">
                    {{ getNodeStatusText(node.status) }}
                  </el-tag>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
          <div v-else class="empty-path">
            <el-empty description="暂无学习路径" :image-size="80">
              <template #description>
                <p>完成初始评测后将自动为您生成个性化学习路径</p>
              </template>
              <el-button type="primary" size="small" @click="$router.push('/student/assessment')">
                前往初始评测
              </el-button>
            </el-empty>
          </div>
        </el-card>

        <!-- 待完成作业 -->
        <el-card v-if="pendingExams.length" class="exams-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>待完成作业</span>
              <el-button type="primary" link @click="$router.push('/student/exams')">查看全部</el-button>
            </div>
          </template>
          <div v-for="exam in pendingExams" :key="exam.id" class="exam-item">
            <div class="exam-info">
              <span class="exam-title">{{ exam.title }}</span>
              <el-tag size="small" type="warning">{{ exam.examTypeText }}</el-tag>
            </div>
            <el-button size="small" type="primary" @click="startExam(exam)">
              开始作业
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧栏 -->
      <el-col :xs="24" :lg="8">
        <!-- 快捷入口 -->
        <el-card class="quick-card" shadow="hover">
          <template #header><span>快捷入口</span></template>
          <div class="quick-actions">
            <div class="quick-item" @click="$router.push('/student/knowledge-map')">
              <el-icon>
                <Share />
              </el-icon>
              <span>知识图谱</span>
            </div>
            <div class="quick-item" @click="$router.push('/student/exams')">
              <el-icon>
                <Document />
              </el-icon>
              <span>在线作业</span>
            </div>
            <div class="quick-item" @click="$router.push('/student/profile')">
              <el-icon>
                <User />
              </el-icon>
              <span>学习画像</span>
            </div>
            <div class="quick-item" @click="$router.push('/student/resources')">
              <el-icon>
                <FolderOpened />
              </el-icon>
              <span>课程资源</span>
            </div>
            <div class="quick-item" @click="$router.push('/student/ai-assistant')">
              <el-icon>
                <ChatDotRound />
              </el-icon>
              <span>AI助手</span>
            </div>
          </div>
        </el-card>

        <!-- 最近学习的知识点 -->
        <el-card class="recent-card" shadow="hover">
          <template #header><span>最近学习</span></template>
          <div v-if="recentMastery.length" class="recent-list">
            <div v-for="item in recentMastery" :key="item.name" class="recent-item">
              <span class="recent-name">{{ item.name }}</span>
              <el-progress :percentage="item.value" :stroke-width="6" :color="getProgressColor(item.value)"
                style="flex: 1;" />
            </div>
          </div>
          <el-empty v-else description="暂无学习记录" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 学生仪表盘视图
 * 展示学习概览、进度统计、快捷入口等
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCourseStore } from '@/stores/course'
import { getLearningProgress, getLearningPath } from '@/api/student/learning'
import { getProfile } from '@/api/student/profile'
import {
  Guide, TrendCharts, Checked, Timer, Finished,
  Share, Document, User, FolderOpened, ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const courseStore = useCourseStore()

const loading = ref(true)
const username = computed(() => userStore.username || '同学')

// 动态问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了，注意休息哦'
  if (hour < 12) return '早上好！新的一天，让我们开始学习吧'
  if (hour < 14) return '中午好！午休后继续加油'
  if (hour < 18) return '下午好！保持专注，继续前进'
  return '晚上好！适当学习，注意劳逸结合'
})

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeNumber = (value) => {
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue : 0
}

const normalizeIdentifier = (value, fallback = null) => {
  if (value === null || value === undefined || value === '') return fallback
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue : value
}

const normalizeBoolean = (value) => {
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return value !== 0
  if (typeof value === 'string') {
    const normalizedValue = value.trim().toLowerCase()
    return ['true', '1', 'yes', 'published', 'completed', 'started', 'active'].includes(normalizedValue)
  }
  return false
}

const parseTimestamp = (value) => {
  if (!value) return 0
  const parsedValue = Date.parse(String(value))
  return Number.isNaN(parsedValue) ? 0 : parsedValue
}

const learningProgress = ref(0)
const masteredPoints = ref(0)
const studyHours = ref(0)
const completedTasks = ref(0)
const learningNodes = ref([])
const pendingExams = ref([])
const recentMastery = ref([])

const resolveLearningNodeStatus = (value) => {
  const node = value && typeof value === 'object' ? value : {}
  const rawStatus = normalizeText(node?.['status']).toLowerCase()
  if (normalizeBoolean(node?.['completed']) || rawStatus === 'completed') return 'completed'
  if (normalizeBoolean(node?.['started']) || rawStatus === 'in_progress' || rawStatus === 'active') return 'current'
  return 'pending'
}

const normalizeLearningProgressSummary = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const progressRate = normalizeNumber(payload?.['progress'] ?? payload?.['progress_rate'])
  const studyMinutes = normalizeNumber(payload?.['study_time'] ?? payload?.['studyTime'])
  return {
    progressPercent: Math.round(progressRate * 100),
    studyHours: Math.round(studyMinutes / 60),
    completedTasks: normalizeNumber(payload?.['completed_nodes'] ?? payload?.['completedNodes'])
  }
}

const extractLearningPathNodes = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  if (Array.isArray(payload?.['nodes'])) return payload['nodes']
  if (payload?.['data'] && typeof payload['data'] === 'object' && Array.isArray(payload['data']['nodes'])) {
    return payload['data']['nodes']
  }
  return []
}

const normalizeMasterySummary = (value, index) => {
  const mastery = value && typeof value === 'object' ? value : {}
  return {
    id: normalizeIdentifier(mastery?.['point_id'] ?? mastery?.['id'], index),
    name: normalizeText(mastery?.['point_name'] ?? mastery?.['name']) || '未知',
    masteryRate: normalizeNumber(mastery?.['mastery_rate']),
    updatedAt: normalizeText(mastery?.['updated_at'])
  }
}

const normalizeProfileSummary = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const knowledgeMastery = Array.isArray(payload?.['knowledge_mastery'])
    ? payload['knowledge_mastery'].map((mastery, index) => normalizeMasterySummary(mastery, index))
    : []
  return {
    masteredPointCount: knowledgeMastery.filter((mastery) => mastery.masteryRate >= 0.8).length,
    recentMasteryList: [...knowledgeMastery]
      .sort((leftItem, rightItem) => parseTimestamp(rightItem.updatedAt) - parseTimestamp(leftItem.updatedAt))
      .slice(0, 5)
      .map((mastery) => ({
        name: mastery.name,
        value: Math.round(mastery.masteryRate * 100)
      }))
  }
}

const normalizePendingExamList = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const rawExams = Array.isArray(payload?.['exams']) ? payload['exams'] : []
  return rawExams
    .map((exam, index) => {
      const examItem = exam && typeof exam === 'object' ? exam : {}
      return {
        id: normalizeIdentifier(examItem?.['exam_id'] ?? examItem?.['id'], index),
        title: normalizeText(examItem?.['title']) || '未命名作业',
        examTypeText: normalizeText(examItem?.['exam_type_display'] ?? examItem?.['exam_type']) || '未分类',
        status: normalizeText(examItem?.['status']).toLowerCase(),
        submitted: normalizeBoolean(examItem?.['submitted'])
      }
    })
    .filter((exam) => exam.status === 'published' && !exam.submitted)
    .slice(0, 3)
}

const buildDashboardPathPreview = (nodes) => {
  if (!Array.isArray(nodes) || !nodes.length) {
    return []
  }

  const normalizedNodes = nodes.map((node, index) => ({
    id: normalizeIdentifier(node?.['node_id'] ?? node?.['id'], index),
    title: normalizeText(node?.['knowledge_point_name'] ?? node?.['title']) || `节点${index + 1}`,
    status: resolveLearningNodeStatus(node)
  }))

  const lastCompletedIndex = normalizedNodes.reduce((lastIndex, node, index) => {
    return node.status === 'completed' ? index : lastIndex
  }, -1)

  const startIndex = Math.max(lastCompletedIndex + 1, 0)
  const previewNodes = normalizedNodes.slice(startIndex, startIndex + 5)
  return previewNodes.length ? previewNodes : normalizedNodes.slice(0, 5)
}

const getProgressColor = (value) => {
  if (value >= 80) return '#22a06b'
  if (value >= 60) return 'var(--primary-color)'
  if (value >= 40) return '#dd8f1d'
  return '#d45050'
}

/**
 * 加载仪表盘数据
 */
const loadDashboardData = async () => {
  // 检查课程ID
  if (!courseStore.courseId) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    // 并行加载多个数据（注意：拦截器已返回 data 字段本身）
    const [progressRes, pathRes, profileRes] = await Promise.allSettled([
      getLearningProgress(courseStore.courseId),
      getLearningPath(courseStore.courseId),
      getProfile(courseStore.courseId)
    ])

    // 处理学习进度
    if (progressRes.status === 'fulfilled' && progressRes.value) {
      const progressSummary = normalizeLearningProgressSummary(progressRes.value)
      learningProgress.value = progressSummary.progressPercent
      studyHours.value = progressSummary.studyHours
      completedTasks.value = progressSummary.completedTasks
    }

    // 处理学习路径（仅预览前 5 个节点）
    if (pathRes.status === 'fulfilled' && pathRes.value) {
      const nodes = extractLearningPathNodes(pathRes.value)
      learningNodes.value = buildDashboardPathPreview(nodes)
    }

    // 处理画像数据，统计高掌握度知识点数量
    if (profileRes.status === 'fulfilled' && profileRes.value) {
      const profileSummary = normalizeProfileSummary(profileRes.value)
      masteredPoints.value = profileSummary.masteredPointCount
      recentMastery.value = profileSummary.recentMasteryList
    }

    // 加载待完成考试
    try {
      const { getExamList } = await import('@/api/student/exam')
      const examRes = await getExamList(courseStore.courseId)
      pendingExams.value = normalizePendingExamList(examRes)
    } catch { /* ignore */ }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 跳转到学习路径
 */
const goToLearningPath = () => {
  router.push('/student/learning-path')
}

const startExam = (exam) => {
  router.push(`/student/exam/${exam.id}`)
}

/**
 * 获取节点标签类型
 */
const getNodeTagType = (status) => {
  const types = {
    completed: 'success',
    current: 'primary',
    pending: 'info'
  }
  return types[status] || 'info'
}

/**
 * 获取节点状态文本
 */
const getNodeStatusText = (status) => {
  const texts = {
    completed: '已完成',
    current: '学习中',
    pending: '待学习'
  }
  return texts[status] || '待学习'
}

onMounted(() => {
  loadDashboardData()
})

// 监听课程切换，自动刷新仪表盘数据
watch(() => courseStore.courseId, (newVal, oldVal) => {
  if (newVal && oldVal && newVal !== oldVal) {
    loadDashboardData()
  }
})
</script>

<style scoped>
.dashboard-view {
  padding: 0;
  min-height: 100%;
}

.stats-row {
  margin-top: 20px;
  overflow: hidden;
}

.stats-row .el-col {
  margin-bottom: 16px;
}

.content-row {
  margin-top: var(--section-gap, 24px);
  clear: both;
}

.content-row>.el-col {
  display: flex;
  flex-direction: column;
}

.welcome-card {
  background: var(--bg-hero);
  border: none;
  color: var(--hero-text);
}

.welcome-card :deep(.el-card__body) {
  padding: 24px 32px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
}

.welcome-text p {
  margin: 0;
  opacity: 0.9;
}

.welcome-actions .el-button {
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(109, 146, 125, 0.16);
  color: var(--primary-dark);
}

.welcome-actions .el-button:hover {
  background: #fff;
}

/* 统计卡片 */
.stat-card {
  height: 100%;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  min-height: 76px;
}

.stat-card-1 .stat-icon {
  background: #dce8df;
  color: var(--primary-dark);
}

.stat-card-2 .stat-icon {
  background: #e6f2ea;
  color: var(--success-color);
}

.stat-card-3 .stat-icon {
  background: #f7eddc;
  color: var(--warning-color);
}

.stat-card-4 .stat-icon {
  background: #e7efeb;
  color: var(--primary-color);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.path-content {
  padding: 10px 0;
}

.timeline-node {
  display: flex;
  align-items: center;
  gap: 12px;
}

.node-title {
  font-size: 14px;
  color: #303133;
}

.empty-path {
  padding: 20px 0;
}

/* 待完成考试 */
.exams-card {
  margin-top: 20px;
}

.path-card,
.exams-card,
.quick-card,
.recent-card {
  width: 100%;
}

.path-card :deep(.el-card__body),
.quick-card :deep(.el-card__body),
.recent-card :deep(.el-card__body) {
  height: 100%;
}

.exam-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.exam-item:last-child {
  border-bottom: none;
}

.exam-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.exam-title {
  font-size: 14px;
  color: #303133;
}

/* 快捷入口 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--bg-soft);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-item:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
}

.quick-item .el-icon {
  font-size: 32px;
  color: #129a74;
  margin-bottom: 8px;
}

.quick-item span {
  font-size: 14px;
  color: #606266;
}

/* 最近学习 */
.recent-card {
  margin-top: 20px;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recent-name {
  font-size: 13px;
  color: #606266;
  width: 80px;
  flex-shrink: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .stat-card :deep(.el-card__body) {
    flex-direction: column;
    text-align: center;
  }
}

@media (min-width: 769px) and (max-width: 1199px) {
  .recent-name {
    width: 60px;
  }
}
</style>
