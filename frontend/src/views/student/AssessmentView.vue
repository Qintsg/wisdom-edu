<template>
  <div class="assessment-view" v-loading="loading">
    <el-card class="page-header" shadow="never">
      <h2>初始测评中心</h2>
      <p v-if="!profileGenerated">完成初始测评，帮助系统了解您的学习状况，生成个性化学习路径</p>
      <p v-else>您的学习画像已生成。您可以重新进行能力评测或修改学习偏好。</p>
    </el-card>

    <!-- 画像已生成提示 -->
    <el-alert v-if="profileGenerated" type="success" :closable="false" show-icon title="学习画像已生成"
      style="margin-bottom: 20px;">
      <template #default>
        <div class="assessment-alert-actions">
          <span>您可以前往「学习画像」页面查看详细分析，也可以重新评测或修改偏好来更新画像。</span>
          <el-button type="primary" plain size="small" @click="viewAssessmentReport">
            查看评测报告
          </el-button>
        </div>
      </template>
    </el-alert>

    <el-row :gutter="20" class="assessment-cards">
      <!-- 能力评测卡片 -->
      <el-col :xs="24" :sm="profileGenerated ? 12 : 8">
        <el-card class="assessment-card" :class="{ completed: abilityCompleted }" shadow="hover">
          <div class="card-icon ability-icon">
            <el-icon>
              <TrendCharts />
            </el-icon>
          </div>
          <h3>能力评测</h3>
          <p>评估您的学习能力和认知水平</p>
          <div class="card-status">
            <el-tag :type="abilityCompleted ? 'success' : 'info'">
              {{ abilityCompleted ? '已完成' : '未完成' }}
            </el-tag>
          </div>
          <el-button type="primary" @click="$router.push('/student/assessment/ability')">
            {{ abilityCompleted ? '重新评测' : '开始评测' }}
          </el-button>
        </el-card>
      </el-col>

      <!-- 习惯问卷卡片 -->
      <el-col :xs="24" :sm="profileGenerated ? 12 : 8">
        <el-card class="assessment-card" :class="{ completed: habitCompleted }" shadow="hover">
          <div class="card-icon habit-icon">
            <el-icon>
              <Document />
            </el-icon>
          </div>
          <h3>习惯问卷</h3>
          <p>了解您的学习习惯和偏好</p>
          <div class="card-status">
            <el-tag :type="habitCompleted ? 'success' : 'info'">
              {{ habitCompleted ? '已完成' : '未完成' }}
            </el-tag>
          </div>
          <el-button type="primary" @click="$router.push('/student/assessment/habit')">
            {{ habitCompleted ? '修改偏好' : '开始问卷' }}
          </el-button>
        </el-card>
      </el-col>

      <!-- 知识测评卡片 - 画像生成后隐藏 -->
      <el-col v-if="!profileGenerated" :xs="24" :sm="8">
        <el-card class="assessment-card" :class="{ completed: knowledgeCompleted }" shadow="hover">
          <div class="card-icon knowledge-icon">
            <el-icon>
              <Reading />
            </el-icon>
          </div>
          <h3>知识测评</h3>
          <p>测试您当前课程的知识水平（按课程独立）</p>
          <div class="card-status">
            <el-tag :type="knowledgeCompleted ? 'success' : 'info'">
              {{ knowledgeCompleted ? '已完成' : '未完成' }}
            </el-tag>
          </div>
          <el-button type="primary" :disabled="knowledgeCompleted"
            @click="$router.push('/student/assessment/knowledge')">
            {{ knowledgeCompleted ? '已完成' : '开始测评' }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 生成画像按钮 - 画像生成后隐藏 -->
    <el-card v-if="allCompleted && !profileGenerated" class="generate-card" shadow="hover">
      <div class="generate-content">
        <el-icon class="generate-icon">
          <Checked />
        </el-icon>
        <h3>恭喜！您已完成所有初始测评</h3>
        <p>点击下方按钮生成您的专属学习画像</p>
        <el-button type="primary" size="large" :loading="generating" :disabled="generating" @click="generateProfile">
          {{ generating ? '正在生成画像...' : '生成学习画像' }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 测评中心视图
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '@/stores/course'
import { getAssessmentStatus, generateProfile as apiGenerateProfile } from '@/api/student/assessment'
import { ElMessage, ElLoading } from 'element-plus'
import { TrendCharts, Document, Reading, Checked } from '@element-plus/icons-vue'

const router = useRouter()
const courseStore = useCourseStore()

const loading = ref(false)
const generating = ref(false)

// 测评完成状态
const abilityCompleted = ref(false)
const habitCompleted = ref(false)
const knowledgeCompleted = ref(false)
const profileGenerated = ref(false)

// 是否全部完成
const allCompleted = computed(() => {
  return abilityCompleted.value && habitCompleted.value && knowledgeCompleted.value
})

const normalizeCourseAssessmentStatus = (value) => {
  const courseStatus = value && typeof value === 'object' ? value : {}
  return {
    courseId: courseStatus?.['course_id'] ?? courseStatus?.['id'] ?? null,
    knowledgeCompleted: Boolean(courseStatus?.['knowledge_done']),
    profileGenerated: Boolean(courseStatus?.['profile_generated'])
  }
}

const normalizeAssessmentStatus = (value) => {
  const status = value && typeof value === 'object' ? value : {}
  return {
    abilityCompleted: Boolean(status?.['ability_done'] || status?.['ability_completed'] || status?.['ability']),
    habitCompleted: Boolean(status?.['habit_done'] || status?.['habit_completed'] || status?.['habit']),
    courses: Array.isArray(status?.['courses'])
      ? status['courses'].map((course) => normalizeCourseAssessmentStatus(course))
      : []
  }
}

/**
 * 加载测评状态
 */
const loadAssessmentStatus = async () => {
  loading.value = true
  try {
    const courseId = courseStore.courseId
    const status = normalizeAssessmentStatus(await getAssessmentStatus(courseId))

    abilityCompleted.value = status.abilityCompleted
    habitCompleted.value = status.habitCompleted
    knowledgeCompleted.value = false
    profileGenerated.value = false

    // 知识测评是课程维度：优先匹配当前课程
    if (status.courses.length > 0 && courseId) {
      const currentCourse = status.courses.find((course) => Number(course.courseId) === Number(courseId))
      knowledgeCompleted.value = currentCourse?.knowledgeCompleted || false
      profileGenerated.value = currentCourse?.profileGenerated || false
    }
  } catch (error) {
    console.error('获取测评状态失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 生成学习画像
 */
const generateProfile = async () => {
  generating.value = true
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在基于您的测评数据生成学习画像，请稍候...',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  try {
    const courseId = courseStore.courseId
    await apiGenerateProfile(courseId)
    loadingInstance.close()
    ElMessage.success('学习画像生成成功！')
    await router.push('/student/profile')
  } catch (error) {
    console.error('生成画像失败:', error)
    loadingInstance.close()
    ElMessage.error('生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

const viewAssessmentReport = () => {
  router.push({
    path: '/student/assessment/report',
    query: {
      course_id: courseStore.courseId
    }
  })
}

onMounted(() => {
  loadAssessmentStatus()
})
</script>

<style scoped>
.assessment-view {
  padding: 0;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  opacity: 0.9;
}

.assessment-cards {
  margin-bottom: 20px;
}

.assessment-alert-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
}

.assessment-alert-actions span {
  flex: 1;
  line-height: 1.7;
}

.assessment-card {
  text-align: center;
  padding: 20px 0;
  transition: all 0.3s;
}

.assessment-card.completed {
  opacity: 0.8;
}

.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 28px;
  color: #fff;
}

.ability-icon {
  background: var(--primary-color);
}

.habit-icon {
  background: #7da18d;
}

.knowledge-icon {
  background: var(--warning-color);
}

.assessment-card h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #303133;
}

.assessment-card p {
  margin: 0 0 16px;
  font-size: 14px;
  color: #909399;
}

.card-status {
  margin-bottom: 16px;
}

.generate-card {
  text-align: center;
}

.generate-content {
  padding: 40px 0;
}

.generate-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 16px;
}

.generate-content h3 {
  margin: 0 0 8px;
  font-size: 20px;
  color: #303133;
}

.generate-content p {
  margin: 0 0 24px;
  color: #909399;
}

@media (max-width: 768px) {
  .assessment-alert-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
