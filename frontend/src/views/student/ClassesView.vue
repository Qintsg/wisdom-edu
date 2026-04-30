<template>
  <div class="classes-view" v-loading="loading">
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <div>
          <h2>我的班级</h2>
          <p>管理您加入的班级，参与班级学习活动</p>
        </div>
        <el-button type="primary" @click="showJoinDialog = true">
          <el-icon>
            <Plus />
          </el-icon>
          加入班级
        </el-button>
      </div>
    </el-card>

    <div class="classes-list">
      <el-row :gutter="20">
        <el-col v-for="cls in classes" :key="cls.id" :xs="24" :sm="12" :lg="8">
          <el-card class="class-card" shadow="hover">
            <div class="class-header">
              <div class="class-avatar">
                {{ cls.name ? cls.name.charAt(0) : '?' }}
              </div>
              <div class="class-info" style="margin-left: 15px;">
                <h3 style="margin: 0 0 5px 0;">{{ cls.name }}</h3>
                <p style="margin: 0; color: #666;">{{ cls.courseName }}</p>
              </div>
            </div>
            <div class="class-meta"
              style="margin-top: 15px; display: flex; justify-content: space-between; color: #999; font-size: 13px;">
              <span><el-icon>
                  <User />
                </el-icon> {{ cls.studentCount }} 名学生</span>
              <span><el-icon>
                  <UserFilled />
                </el-icon> 教师：{{ cls.teacherName }}</span>
            </div>
            <div class="class-actions"
              style="margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px; display: flex; justify-content: flex-end;">
              <el-button type="primary" link @click="viewClass(cls)">
                进入班级
              </el-button>
              <el-button type="danger" link @click="leaveClass(cls)">
                退出班级
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="classes.length === 0" description="您还未加入任何班级">
        <el-button type="primary" @click="showJoinDialog = true">使用邀请码加入班级</el-button>
      </el-empty>
    </div>

    <!-- 加入班级对话框 -->
    <el-dialog v-model="showJoinDialog" title="加入班级" width="400px" :close-on-click-modal="!joining">
      <el-form :model="joinForm" label-width="80px" @submit.prevent="joinClass">
        <el-form-item label="邀请码">
          <el-input v-model="joinForm.invitationCode" placeholder="请输入班级邀请码" clearable maxlength="20"
            @keyup.enter="joinClass" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :disabled="joining" @click="showJoinDialog = false">取消</el-button>
        <el-button type="primary" :loading="joining" :disabled="!normalizeText(joinForm.invitationCode)"
          @click="joinClass">加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 班级列表视图
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, UserFilled } from '@element-plus/icons-vue'
import { getClassList, joinClass as apiJoinClass, leaveClass as apiLeaveClass } from '@/api/student/class'
import { useCourseStore } from '@/stores/course'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const courseStore = useCourseStore()
const userStore = useUserStore()
const loading = ref(false)
const joining = ref(false)

// 班级列表
const classes = ref([])

// 加入班级对话框
const showJoinDialog = ref(false)
const joinForm = reactive({
  invitationCode: ''
})

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeClassSummary = (value, index) => {
  const classItem = value && typeof value === 'object' ? value : {}
  const studentCount = Number(classItem?.['student_count'])
  const publishedCourses = Array.isArray(classItem?.['courses']) ? classItem['courses'] : []
  const publishedCourseNames = publishedCourses
    .map(courseItem => normalizeText(courseItem?.['course_name'] ?? courseItem?.['name']))
    .filter(Boolean)
  return {
    id: classItem?.['class_id'] ?? classItem?.['id'] ?? index,
    name: normalizeText(classItem?.['class_name'] ?? classItem?.['name']) || '未命名班级',
    courseName: normalizeText(classItem?.['course_name']) || publishedCourseNames.join('、') || '未关联课程',
    studentCount: Number.isFinite(studentCount) ? studentCount : 0,
    teacherName: normalizeText(classItem?.['teacher_username'] ?? classItem?.['teacher_name'] ?? classItem?.['teacher']) || '未分配'
  }
}

const normalizeClassList = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const rawClasses = Array.isArray(payload?.['classes'])
    ? payload['classes']
    : Array.isArray(value)
      ? value
      : []
  return rawClasses.map((classItem, index) => normalizeClassSummary(classItem, index))
}

/**
 * 加载班级列表
 */
const loadClasses = async () => {
  loading.value = true
  try {
    classes.value = normalizeClassList(await getClassList())
  } catch (error) {
    console.error('获取班级列表失败:', error)
    ElMessage.error('获取班级列表失败')
  } finally {
    loading.value = false
  }
}

const refreshLearningContext = async () => {
  courseStore.invalidateCoursesCache()
  await Promise.allSettled([
    userStore.fetchUserInfo(),
    courseStore.fetchCourses()
  ])
}

/**
 * 查看班级
 */
const viewClass = (cls) => {
  router.push(`/student/classes/${cls.id}`)
}

/**
 * 加入班级
 */
const joinClass = async () => {
  const invitationCode = normalizeText(joinForm.invitationCode)
  if (!invitationCode) {
    ElMessage.warning('请输入邀请码')
    return
  }

  joining.value = true
  try {
    const joinedClass = await apiJoinClass({ code: invitationCode })
    const joinedClassName = normalizeText(joinedClass?.['class_name'] ?? joinedClass?.['name'])
    ElMessage.success(joinedClassName ? `已加入${joinedClassName}` : '加入班级成功！')
    showJoinDialog.value = false
    joinForm.invitationCode = ''
    await Promise.all([loadClasses(), refreshLearningContext()])
  } catch (error) {
    console.error('加入班级失败:', error)
    if (!error?.handledByInterceptor) {
      ElMessage.error(error?.message || '加入失败，请检查邀请码是否正确')
    }
  } finally {
    joining.value = false
  }
}

/**
 * 退出班级
 */
const leaveClass = async (cls) => {
  try {
    await ElMessageBox.confirm(
      `确定要退出班级"${cls.name}"吗？`,
      '退出确认',
      { type: 'warning' }
    )

    await apiLeaveClass(cls.id)
    classes.value = classes.value.filter(c => c.id !== cls.id)
    if (String(courseStore.classId || '') === String(cls.id)) {
      courseStore.clearSelection()
    }
    await refreshLearningContext()
    ElMessage.success('已退出班级')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退出班级失败:', error)
      ElMessage.error('退出失败，请稍后重试')
    }
  }
}

onMounted(() => {
  loadClasses()
})
</script>

<style scoped>
.classes-view {
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  opacity: 0.9;
}

/* 班级卡片 */
.class-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.class-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.class-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.class-avatar {
  width: 48px;
  height: 48px;
  background: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  font-weight: 600;
}

.class-info h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #303133;
}

.class-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.class-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 16px;
}

.class-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.class-actions {
  display: flex;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}
</style>
