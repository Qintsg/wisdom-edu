<template>
  <div class="student-profile-view" v-loading="loading" element-loading-text="加载学生画像中...">
    <el-page-header @back="goBack">
      <template #content>
        <span>学生画像 - {{ studentInfo.displayName || '加载中...' }}</span>
      </template>
      <template #extra>
        <el-button type="primary" :icon="Refresh" :loading="refreshing" @click="handleRefreshProfile">
          刷新画像
        </el-button>
      </template>
    </el-page-header>

    <template v-if="!loading">
      <!-- 学生基本信息 -->
      <el-card class="info-card" shadow="hover">
        <div class="student-info-row">
          <el-avatar :size="64" class="student-avatar">
            {{ (studentInfo.displayName || '学').charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="student-meta">
            <h3>{{ studentInfo.displayName || studentInfo.username || '未知学生' }}</h3>
            <div class="meta-tags">
              <el-tag v-if="studentInfo.studentCode" size="small">学号: {{ studentInfo.studentCode }}</el-tag>
              <el-tag type="info" size="small">答题数: {{ answerStats.totalCount || 0 }}</el-tag>
              <el-tag :type="answerStats.accuracyPercentage >= 60 ? 'success' : 'warning'" size="small">
                正确率: {{ answerStats.accuracyPercentage || 0 }}%
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>

      <el-row :gutter="20" class="content-row">
        <!-- 能力雷达图 -->
        <el-col :xs="24" :lg="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <span>能力雷达图</span>
              </div>
            </template>
            <div v-if="abilityData.length">
              <RadarChart :data="abilityData" :max="100" height="280px" color="#667eea" :show-value="true" />
            </div>
            <el-empty v-else description="该学生暂无能力评测数据" :image-size="80" />
          </el-card>
        </el-col>

        <!-- 知识掌握度 -->
        <el-col :xs="24" :lg="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <span>知识掌握度</span>
                <el-tag size="small" type="info">{{ masteryData.length }} 个知识点</el-tag>
              </div>
            </template>
            <div v-if="masteryData.length" class="mastery-list">
              <div v-for="item in masteryData" :key="item.pointId || item.name" class="mastery-item">
                <div class="mastery-label">
                  <span>{{ item.name }}</span>
                  <span>{{ item.value }}%</span>
                </div>
                <el-progress :percentage="item.value" :stroke-width="10" :color="getProgressColor(item.value)" />
              </div>
            </div>
            <el-empty v-else description="该学生暂无知识掌握度数据" :image-size="80" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 画像变化历史 -->
      <el-card shadow="hover" class="learning-card">
        <template #header>
          <div class="card-header">
            <span>画像变化历史</span>
          </div>
        </template>
        <el-timeline v-if="historyRecords.length">
          <el-timeline-item v-for="record in historyRecords" :key="record.recordId" :timestamp="record.timeText"
            placement="top">
            <el-card shadow="never" class="timeline-card">
              <p>{{ record.contentText }}</p>
              <el-tag size="small" type="info">平均掌握度: {{ record.avgMasteryPercent }}%</el-tag>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无画像历史记录" :image-size="60" />
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getStudentProfileDetail } from '@/api/teacher/class'
import RadarChart from '@/components/charts/RadarChart.vue'
import request from '@/api/index'

const router = useRouter()
const route = useRoute()

/**
 * 收敛文本字段，避免模板直接消费动态 payload。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return String(rawValue)
  }
  return ''
}

/**
 * 收敛路由或接口中的标识符。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  return normalizeText(rawValue).trim()
}

/**
 * 收敛数值字段。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 将任意 payload 收敛为对象。
 * @param {unknown} rawValue
 * @returns {Record<string, unknown>}
 */
const normalizeObjectFromPayload = (rawValue) => {
  return rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue)
    ? rawValue
    : {}
}

/**
 * 将任意 payload 收敛为数组。
 * @param {unknown} rawValue
 * @returns {Array<Record<string, unknown>>}
 */
const normalizeListFromPayload = (rawValue) => {
  return Array.isArray(rawValue) ? rawValue : []
}

/**
 * 将掌握度/能力值统一换算为百分比。
 * @param {unknown} rawValue
 * @returns {number}
 */
const normalizePercentValue = (rawValue) => {
  const numericValue = normalizeNumber(rawValue)
  return Math.round((numericValue <= 1 ? numericValue * 100 : numericValue) || 0)
}

const currentStudentId = computed(() => normalizeIdentifier(route.params.studentId))
const currentClassId = computed(() => normalizeIdentifier(route.params.classId ?? route.query.classId))
const currentCourseId = computed(() => normalizeIdentifier(route.query.course_id ?? route.query.courseId))

const loading = ref(true)
const refreshing = ref(false)
const studentInfo = reactive({ userId: '', displayName: '', username: '', studentCode: '' })
const abilityData = ref([])
const masteryData = ref([])
const historyRecords = ref([])
const answerStats = reactive({ totalCount: 0, correctCount: 0, accuracyPercentage: 0 })

const getAbilityName = (key) => {
  const names = {
    // C-WAIS 四维度（新）
    '言语理解': '言语理解', '知觉推理': '知觉推理',
    '工作记忆': '工作记忆', '处理速度': '处理速度',
    // 旧维度兼容
    logical_reasoning: '逻辑推理', memory: '记忆力', analysis: '分析能力',
    innovation: '创新能力', comprehension: '理解能力', application: '应用能力'
  }
  return names[key] || key
}

const getProgressColor = (value) => {
  if (value >= 80) return '#67c23a'
  if (value >= 60) return '#409eff'
  if (value >= 40) return '#e6a23c'
  return '#f56c6c'
}

const normalizeAbilityData = (rawScores) => {
  const scorePayload = normalizeObjectFromPayload(rawScores)

  return Object.entries(scorePayload).map(([abilityKey, abilityValue]) => ({
    name: getAbilityName(abilityKey),
    value: normalizePercentValue(abilityValue)
  }))
}

const normalizeMasteryData = (rawMasteryList) => {
  return normalizeListFromPayload(rawMasteryList).map((rawMasteryItem) => ({
    pointId: normalizeIdentifier(rawMasteryItem.point_id ?? rawMasteryItem.id),
    name: normalizeText(rawMasteryItem.point_name ?? rawMasteryItem.name) || '未知知识点',
    value: normalizePercentValue(rawMasteryItem.mastery_rate ?? rawMasteryItem.mastery ?? rawMasteryItem.value)
  }))
}

const normalizeHistoryRecords = (rawHistoryList) => {
  return normalizeListFromPayload(rawHistoryList).map((rawHistoryItem, historyIndex) => ({
    recordId: normalizeIdentifier(rawHistoryItem.id) || String(historyIndex),
    contentText: normalizeText(rawHistoryItem.update_reason) || '画像更新',
    timeText: formatTime(normalizeText(rawHistoryItem.created_at)),
    avgMasteryPercent: normalizePercentValue(rawHistoryItem.average_mastery)
  }))
}

const loadStudentProfile = async () => {
  loading.value = true
  try {
    if (!currentStudentId.value) {
      ElMessage.warning('缺少学生ID参数')
      return
    }

    const studentProfilePayload = normalizeObjectFromPayload(
      await getStudentProfileDetail(currentClassId.value, currentStudentId.value, currentCourseId.value)
    )
    if (!Object.keys(studentProfilePayload).length) {
      ElMessage.warning('未能获取到学生画像数据')
      return
    }

    studentInfo.userId = normalizeIdentifier(studentProfilePayload.user_id) || currentStudentId.value
    studentInfo.displayName = normalizeText(studentProfilePayload.real_name ?? studentProfilePayload.name ?? studentProfilePayload.username) || '学生'
    studentInfo.username = normalizeText(studentProfilePayload.username)
    studentInfo.studentCode = normalizeText(studentProfilePayload.student_id)

    abilityData.value = normalizeAbilityData(studentProfilePayload.ability_scores)
    masteryData.value = normalizeMasteryData(studentProfilePayload.knowledge_mastery)

    const statsPayload = normalizeObjectFromPayload(studentProfilePayload.answer_stats)
    answerStats.totalCount = normalizeNumber(statsPayload.total)
    answerStats.correctCount = normalizeNumber(statsPayload.correct)
    answerStats.accuracyPercentage = normalizeNumber(statsPayload.accuracy)

    historyRecords.value = normalizeHistoryRecords(studentProfilePayload.profile_history)
  } catch (error) {
    console.error('加载学生画像失败:', error)
    ElMessage.error('加载学生画像失败: ' + (error?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleRefreshProfile = async () => {
  if (!currentCourseId.value) {
    ElMessage.warning('缺少课程ID，无法刷新画像')
    return
  }
  try {
    await ElMessageBox.confirm('将为该学生重新生成学习画像，可能需要一些时间', '确认刷新', { type: 'info' })
    refreshing.value = true
    await request.post(`/api/teacher/students/${currentStudentId.value}/refresh-profile`, { course_id: currentCourseId.value })
    ElMessage.success('画像刷新成功')
    await loadStudentProfile()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('刷新画像失败:', error)
      ElMessage.error('刷新画像失败: ' + (error?.message || '服务暂不可用'))
    }
  } finally {
    refreshing.value = false
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try { return new Date(timeStr).toLocaleString('zh-CN') } catch { return timeStr }
}

const goBack = () => {
  void router.back()
}

onMounted(() => {
  void loadStudentProfile()
})
</script>

<style scoped>
.student-profile-view {
  padding: 0;
}

.info-card {
  margin-top: 20px;
}

.student-info-row {
  display: flex;
  align-items: center;
  gap: 20px;
}

.student-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 24px;
  font-weight: 600;
}

.student-meta h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #303133;
}

.meta-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.content-row {
  margin-top: 20px;
}

.chart-card {
  height: 100%;
  min-height: 320px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.radar-chart {
  height: 260px;
  width: 100%;
}

.mastery-list {
  max-height: 260px;
  overflow-y: auto;
  padding: 4px 0;
}

.mastery-item {
  margin-bottom: 16px;
}

.mastery-item:last-child {
  margin-bottom: 0;
}

.mastery-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
  color: #606266;
}

.learning-card {
  margin-top: 20px;
}

.timeline-card {
  padding: 8px 12px;
}

.timeline-card p {
  margin: 0 0 8px;
  color: #303133;
}

@media (max-width: 768px) {
  .student-info-row {
    flex-direction: column;
    text-align: center;
  }
}
</style>
