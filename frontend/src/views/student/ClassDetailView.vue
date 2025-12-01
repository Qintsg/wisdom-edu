<template>
  <div class="class-detail-view">
    <el-page-header @back="goBack">
      <template #content>
        <span class="page-title">{{ classInfo.name || '班级详情' }}</span>
      </template>
    </el-page-header>

    <el-card v-loading="loading" class="class-info-card" shadow="hover">
      <div class="class-header">
        <div class="class-avatar">{{ (classInfo.name || '班').charAt(0) }}</div>
        <div class="class-info">
          <h2>{{ classInfo.name }}</h2>
          <p>课程：{{ classInfo.courseName }}</p>
        </div>
      </div>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="教师">{{ classInfo.teacherName }}</el-descriptions-item>
        <el-descriptions-item label="学生人数">{{ classInfo.studentCount }} 人</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ classInfo.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="班级状态">
          <el-tag :type="classInfo.status === 'active' ? 'success' : 'info'">
            {{ classInfo.status === 'active' ? '进行中' : '已结束' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="announcements-card" shadow="hover">
      <template #header>
        <span>班级公告</span>
      </template>
      <el-empty v-if="announcements.length === 0" description="暂无公告" />
      <div v-else class="announcement-list">
        <div v-for="item in announcements" :key="item.id" class="announcement-item">
          <div class="announcement-title">{{ item.title }}</div>
          <div class="announcement-content">{{ item.content }}</div>
          <div class="announcement-time">{{ item.createdAt }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 学生端班级详情视图
 */
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getClassDetail } from '@/api/student/class'

const router = useRouter()
const route = useRoute()

const props = defineProps({
  classId: {
    type: String,
    default: ''
  }
})

const loading = ref(false)
const classInfo = ref({
  name: '',
  courseName: '',
  teacherName: '',
  studentCount: 0,
  createdAt: '',
  status: 'active'
})
const announcements = ref([])

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const formatDisplayDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '-' : date.toLocaleDateString('zh-CN')
}

const normalizeAnnouncement = (value, index) => {
  const announcement = value && typeof value === 'object' ? value : {}
  return {
    id: announcement?.['id'] ?? index,
    title: normalizeText(announcement?.['title']) || `公告 ${index + 1}`,
    content: normalizeText(announcement?.['content']) || '-',
    createdAt: formatDisplayDate(announcement?.['created_at'] ?? announcement?.['createdAt'])
  }
}

const normalizeCourseNames = (value) => {
  if (!Array.isArray(value)) return ''
  return value
    .map((course) => normalizeText(course?.['course_name'] ?? course?.['name']))
    .filter((courseName) => courseName.length > 0)
    .join('、')
}

const normalizeClassDetail = (value) => {
  const detail = value && typeof value === 'object' ? value : {}
  const teacherInfo = detail?.['teacher'] && typeof detail['teacher'] === 'object' ? detail['teacher'] : {}

  return {
    classInfo: {
      name: normalizeText(detail?.['class_name'] ?? detail?.['name']) || '班级详情',
      courseName: normalizeText(detail?.['course_name']) || normalizeCourseNames(detail?.['courses']) || '-',
      teacherName: normalizeText(detail?.['teacher_name'] ?? teacherInfo?.['username'] ?? teacherInfo?.['name']) || '-',
      studentCount: Number(detail?.['student_count'] ?? 0),
      createdAt: formatDisplayDate(detail?.['created_at']),
      status: normalizeText(detail?.['status']) || 'active'
    },
    announcements: Array.isArray(detail?.['announcements'])
      ? detail['announcements'].map((announcement, index) => normalizeAnnouncement(announcement, index))
      : []
  }
}

/**
 * 返回上一页
 */
const goBack = () => {
  router.push('/student/classes')
}

/**
 * 加载班级详情
 */
const loadClassDetail = async () => {
  const id = props.classId || route.params['classId']
  if (!id) {
    ElMessage.error('班级ID不存在')
    goBack()
    return
  }

  loading.value = true
  try {
    const detail = normalizeClassDetail(await getClassDetail(id))
    classInfo.value = detail.classInfo
    announcements.value = detail.announcements
  } catch (error) {
    console.error('获取班级详情失败:', error)
    ElMessage.error('获取班级详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadClassDetail()
})
</script>

<style scoped>
.class-detail-view {
  padding: 0;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.class-info-card {
  margin-top: 20px;
}

.class-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.class-avatar {
  width: 64px;
  height: 64px;
  background: var(--primary-color);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  font-weight: 600;
}

.class-info h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}

.class-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.announcements-card {
  margin-top: 20px;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 10px;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.announcement-item:hover {
  background: #ecf5ff;
  border-left-color: var(--el-color-primary, #409eff);
  transform: translateX(4px);
}

.announcement-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.announcement-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
}

.announcement-time {
  font-size: 12px;
  color: #909399;
}
</style>
