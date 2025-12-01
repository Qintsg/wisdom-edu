<template>
  <!-- 班级详情视图 -->
  <div class="class-detail-view">
    <el-page-header @back="goBack">
      <template #content>{{ classInfo.name }}</template>
    </el-page-header>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :lg="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>学生列表</span>
              <el-button type="primary" size="small" @click="handleGenerateCode">生成邀请码</el-button>
            </div>
          </template>
          <el-table :data="students" style="width: 100%" v-loading="loading">
            <el-table-column label="学生" min-width="180">
              <template #default="{ row }">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <el-avatar :size="32"
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; font-size: 14px;">
                    {{ (row.realName || row.name || '学').charAt(0) }}
                  </el-avatar>
                  <div>
                    <div style="font-weight: 600;">{{ row.realName || row.name }}</div>
                    <div style="font-size: 12px; color: #909399;">{{ row.username }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="studentId" label="学号" width="120" />
            <el-table-column prop="enrolledAt" label="加入时间" width="160" />

          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="hover">
          <template #header>班级统计</template>
          <div class="stats-list">
            <div class="stat-item"><span>学生总数</span><strong>{{ stats.totalStudents }}</strong></div>
            <div class="stat-item"><span>平均进度</span><strong>{{ stats.avgProgress }}%</strong></div>
            <div class="stat-item"><span>本周活跃</span><strong>{{ stats.weeklyActive }}</strong></div>
          </div>
        </el-card>

        <!-- 邀请码展示区 -->
        <el-card v-if="currentInviteCode" shadow="hover" style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span>当前邀请码</span>
              <el-button type="danger" link size="small" @click="currentInviteCode = ''">关闭</el-button>
            </div>
          </template>
          <div style="text-align: center; padding: 16px 0;">
            <div style="font-size: 28px; font-weight: bold; letter-spacing: 4px; color: #409eff; margin-bottom: 12px;">
              {{ currentInviteCode }}
            </div>
            <el-button size="small" @click="copyInviteCode">复制邀请码</el-button>
          </div>
        </el-card>

        <!-- 班级公告管理 -->
        <el-card shadow="hover" style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span>班级公告</span>
              <el-button type="primary" size="small" @click="showAnnouncementDialog()">发布公告</el-button>
            </div>
          </template>
          <div v-if="announcementsLoading" style="padding: 12px;">
            <el-skeleton :rows="2" animated />
          </div>
          <el-empty v-else-if="!announcements.length" description="暂无公告" :image-size="60" />
          <div v-else class="announcement-list">
            <div v-for="item in announcements" :key="item.id" class="announcement-item">
              <div class="announcement-header">
                <strong>{{ item.title }}</strong>
                <div class="announcement-actions">
                  <el-button type="primary" link size="small" @click="showAnnouncementDialog(item)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="handleDeleteAnnouncement(item.id)">删除</el-button>
                </div>
              </div>
              <p class="announcement-content">{{ item.content }}</p>
              <span class="announcement-time">{{ item.createdAt }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 公告编辑对话框 -->
    <el-dialog v-model="announcementDialogVisible" :title="editingAnnouncement ? '编辑公告' : '发布公告'" width="500px">
      <el-form :model="announcementForm" label-width="70px">
        <el-form-item label="标题">
          <el-input v-model="announcementForm.title" placeholder="请输入公告标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="announcementForm.content" type="textarea" :rows="5" placeholder="请输入公告内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="announcementDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAnnouncement" :loading="announcementSubmitting">
          {{ editingAnnouncement ? '保存' : '发布' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 班级详情视图
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getClassDetail, getClassStudents, generateInvitation,
  getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement
} from '@/api/teacher/class'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const classInfo = reactive({ id: route.params['classId'], name: '' })
const students = ref([])
const stats = reactive({
  totalStudents: 0,
  avgProgress: 0,
  weeklyActive: 0
})

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeAnnouncement = (value, index) => {
  const announcement = value && typeof value === 'object' ? value : {}
  return {
    id: announcement?.['id'] ?? index,
    title: normalizeText(announcement?.['title']) || `公告 ${index + 1}`,
    content: normalizeText(announcement?.['content']) || '-',
    createdAt: formatTime(announcement?.['created_at'] ?? announcement?.['createdAt'])
  }
}

const normalizeStudent = (value, index) => {
  const student = value && typeof value === 'object' ? value : {}
  return {
    id: student?.['user_id'] ?? student?.['id'] ?? index,
    name: normalizeText(student?.['real_name'] ?? student?.['username'] ?? student?.['name']) || '未知',
    realName: normalizeText(student?.['real_name']),
    username: normalizeText(student?.['username']),
    studentId: normalizeText(student?.['student_id']),
    enrolledAt: formatTime(student?.['enrolled_at'])
  }
}

const normalizeStudentResponse = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const rawStudents = Array.isArray(payload?.['students'])
    ? payload['students']
    : Array.isArray(value)
      ? value
      : []
  const normalizedStudents = rawStudents.map((student, index) => normalizeStudent(student, index))
  return {
    students: normalizedStudents,
    weeklyActive: Number(payload?.['weekly_active'] ?? normalizedStudents.length)
  }
}

const normalizeClassDetail = (value, classId) => {
  const detail = value && typeof value === 'object' ? value : {}
  return {
    id: classId,
    name: normalizeText(detail?.['class_name'] ?? detail?.['name']) || '班级',
    courses: Array.isArray(detail?.['courses']) ? detail['courses'] : []
  }
}

/**
 * 加载班级详情
 */
const loadClassDetail = async () => {
  loading.value = true
  try {
    const classId = route.params['classId']
    const [detailRes, studentsRes] = await Promise.allSettled([
      getClassDetail(classId),
      getClassStudents(classId)
    ])

    if (detailRes.status === 'fulfilled') {
      const detail = normalizeClassDetail(detailRes.value, classId)
      classInfo.id = detail.id
      classInfo.name = detail.name
      classCourses.value = detail.courses
    }

    if (studentsRes.status === 'fulfilled') {
      const studentData = normalizeStudentResponse(studentsRes.value)
      students.value = studentData.students

      stats.totalStudents = students.value.length
      stats.avgProgress = 0
      stats.weeklyActive = Number.isFinite(studentData.weeklyActive)
        ? studentData.weeklyActive
        : students.value.length
    }
  } catch (error) {
    console.error('加载班级详情失败:', error)
    ElMessage.error('加载班级详情失败')
  } finally {
    loading.value = false
  }
}

// 当前邀请码
const currentInviteCode = ref('')

/**
 * 生成邀请码
 */
const handleGenerateCode = async () => {
  try {
    const res = await generateInvitation({ class_id: classInfo.id })
    currentInviteCode.value = normalizeText(res?.code || res?.['invite_code'])
    ElMessage.success('邀请码已生成')
  } catch (error) {
    console.error('生成邀请码失败:', error)
    ElMessage.error('生成邀请码失败')
  }
}

/**
 * 复制邀请码
 */
const copyInviteCode = () => {
  navigator.clipboard.writeText(currentInviteCode.value).then(() => {
    ElMessage.success('邀请码已复制到剪贴板')
  }).catch(() => {
    ElMessage.info(`请手动复制：${currentInviteCode.value}`)
  })
}

/**
 * 格式化时间
 */
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000 / 60)
  if (diff < 60) return `${diff}分钟前`
  if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
  return `${Math.floor(diff / 1440)}天前`
}

const goBack = () => router.push('/teacher/classes')

// 存储班级课程列表
const classCourses = ref([])

// ============ 公告管理 ============
const announcements = ref([])
const announcementsLoading = ref(false)
const announcementDialogVisible = ref(false)
const announcementSubmitting = ref(false)
const editingAnnouncement = ref(null)
const announcementForm = reactive({ title: '', content: '' })

const loadAnnouncements = async () => {
  announcementsLoading.value = true
  try {
    const res = await getAnnouncements(classInfo.id)
    announcements.value = Array.isArray(res?.['announcements'])
      ? res['announcements'].map((announcement, index) => normalizeAnnouncement(announcement, index))
      : []
  } catch (e) {
    console.error('加载公告失败:', e)
  } finally {
    announcementsLoading.value = false
  }
}

const showAnnouncementDialog = (item = null) => {
  editingAnnouncement.value = item
  announcementForm.title = item?.title || ''
  announcementForm.content = item?.content || ''
  announcementDialogVisible.value = true
}

const submitAnnouncement = async () => {
  const normalizedTitle = normalizeText(announcementForm.title)
  if (!normalizedTitle) {
    ElMessage.warning('请输入公告标题')
    return
  }
  const normalizedContent = normalizeText(announcementForm.content)
  if (!normalizedContent) {
    ElMessage.warning('请输入公告内容')
    return
  }
  announcementSubmitting.value = true
  try {
    if (editingAnnouncement.value) {
      await updateAnnouncement(editingAnnouncement.value.id, {
        title: normalizedTitle,
        content: normalizedContent
      })
      ElMessage.success('公告已更新')
    } else {
      await createAnnouncement(classInfo.id, {
        title: normalizedTitle,
        content: normalizedContent
      })
      ElMessage.success('公告已发布')
    }
    announcementDialogVisible.value = false
    await loadAnnouncements()
  } catch (e) {
    console.error('提交公告失败:', e)
    ElMessage.error('操作失败')
  } finally {
    announcementSubmitting.value = false
  }
}

const handleDeleteAnnouncement = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该公告？', '提示', { type: 'warning' })
    await deleteAnnouncement(id)
    ElMessage.success('公告已删除')
    await loadAnnouncements()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除公告失败:', e)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadClassDetail()
  loadAnnouncements()
})
</script>

<style scoped>
.content-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-item strong {
  color: #409eff;
  font-size: 18px;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.announcement-item {
  padding: 12px;
  border-radius: 8px;
  background: #f9f9fb;
  border: 1px solid #ebeef5;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.announcement-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 6px;
  white-space: pre-line;
}

.announcement-time {
  color: #909399;
  font-size: 12px;
}
</style>
