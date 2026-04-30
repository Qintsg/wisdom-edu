<template>
  <div class="course-select-view">
    <el-container class="main-container">
      <el-header height="auto" class="page-header">
        <div class="header-content">
          <el-icon class="header-icon">
            <Collection />
          </el-icon>
          <h1>选择学习课程</h1>
          <p>请选择您要学习的课程，开启智个性化学习之旅</p>
        </div>
      </el-header>

      <el-main>
        <div v-if="loading" class="loading-container">
          <el-skeleton animated :count="3" class="course-skeleton">
            <template #template>
              <el-skeleton-item variant="rect" style="width: 100%; height: 120px; border-radius: 8px;" />
            </template>
          </el-skeleton>
        </div>

        <div v-else-if="courses.length === 0" class="empty-state">
          <el-empty description="暂无可选课程" :image-size="200">
            <template #description>
              <p>暂无可选课程，请先使用老师提供的邀请码加入班级。</p>
            </template>
            <el-button type="primary" size="large" :loading="joiningClass" @click="showJoinDialog = true">
              加入班级
            </el-button>
          </el-empty>
        </div>

        <el-row v-else :gutter="24" class="course-grid">
          <el-col v-for="course in courses" :key="course.selectionKey" :xs="24" :sm="12" :md="8" :lg="6">
            <div class="course-card-wrapper" :class="{ 'is-selected': isSelected(course) }"
              @click="handleSelectCourse(course)">
              <el-card class="course-card" shadow="hover" :body-style="{ padding: '0px' }">
                <div class="card-cover" :style="getCoverStyle(course)">
                  <div class="course-icon">
                    <el-icon>
                      <Reading />
                    </el-icon>
                  </div>
                  <div v-if="isSelected(course)" class="check-mark">
                    <el-icon>
                      <Check />
                    </el-icon>
                  </div>
                </div>
                <div class="card-content">
                  <h3 class="course-name">{{ course.name }}</h3>
                  <div class="course-meta">
                    <el-tag size="small" effect="plain" type="info">ID: {{ course.id }}</el-tag>
                    <el-tag size="small" effect="plain" v-if="course.classId">班级: {{ course.className }}</el-tag>
                  </div>
                </div>
              </el-card>
            </div>
          </el-col>
        </el-row>
      </el-main>

      <el-footer height="auto" class="page-footer">
        <div class="action-bar">
          <el-button type="primary" size="large" class="submit-btn" :disabled="!selectedCourseKey" :loading="submitting"
            @click="confirmSelect" round>
            确认并进入课程
            <el-icon class="el-icon--right">
              <ArrowRight />
            </el-icon>
          </el-button>
        </div>
      </el-footer>
    </el-container>

    <el-dialog v-model="showJoinDialog" title="加入班级" width="400px" :close-on-click-modal="!joiningClass">
      <el-form :model="joinForm" label-width="80px" @submit.prevent="handleJoinClass">
        <el-form-item label="邀请码">
          <el-input v-model="joinForm.invitationCode" placeholder="请输入班级邀请码" clearable maxlength="20"
            @keyup.enter="handleJoinClass" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :disabled="joiningClass" @click="showJoinDialog = false">取消</el-button>
        <el-button type="primary" :loading="joiningClass" :disabled="!normalizeText(joinForm.invitationCode)"
          @click="handleJoinClass">加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 课程选择视图
 * 优化版本：使用 grid 布局，card 样式，增加视觉交互
 */
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '@/stores/course'
import { getCourses, selectCourse as selectCourseApi } from '@/api/course'
import { joinClass as apiJoinClass } from '@/api/student/class'
import { generateCoverStyle } from '@/utils/courseCover'
import { ElMessage } from 'element-plus'
import { Check, Collection, Reading, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const courseStore = useCourseStore()
const currentCourseId = computed(() => courseStore.courseId)
const currentClassId = computed(() => courseStore.classId)

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeIdentifier = (value, fallback = null) => {
  if (value === null || value === undefined || value === '') return fallback
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue : value
}

const buildCourseSelectionKey = (courseId, classId, index) => {
  return `${normalizeIdentifier(courseId, index)}::${normalizeIdentifier(classId, 'none')}`
}

const normalizeCourseSummary = (value, index) => {
  const course = value && typeof value === 'object' ? value : {}
  const courseId = normalizeIdentifier(course?.['course_id'] ?? course?.['id'], index)
  const classId = normalizeIdentifier(course?.['class_id'] ?? course?.['class_obj_id'])
  return {
    id: courseId,
    name: normalizeText(course?.['course_name'] ?? course?.['name']) || '未命名课程',
    classId,
    className: normalizeText(course?.['class_name'] ?? course?.['class_obj_name']),
    coverUrl: normalizeText(course?.['course_cover'] ?? course?.['cover']),
    teacherName: normalizeText(course?.['teacher_name']),
    selectionKey: buildCourseSelectionKey(courseId, classId, index)
  }
}

const normalizeCourseListResponse = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const rawCourses = Array.isArray(payload?.['courses'])
    ? payload['courses']
    : (Array.isArray(value) ? value : [])
  return {
    items: rawCourses.map((course, index) => normalizeCourseSummary(course, index)),
    currentCourseId: normalizeIdentifier(payload?.['current_course_id'])
  }
}

const findCourseById = (courseIdValue) => courses.value.find(
  (course) => String(course.id) === String(courseIdValue)
)

const findCourseByIdentity = (courseIdValue, classIdValue = null) => {
  const exactCourse = courses.value.find((course) => (
    String(course.id) === String(courseIdValue) &&
    String(course.classId ?? '') === String(classIdValue ?? '')
  ))
  return exactCourse || findCourseById(courseIdValue)
}

const findCourseBySelectionKey = (selectionKey) => courses.value.find(
  (course) => course.selectionKey === selectionKey
)

const getCoverStyle = (course) => generateCoverStyle(course.id, course.name)


// 选中的课程项（课程ID + 班级ID），避免同一课程发布到多个班级时一起高亮。
const selectedCourseKey = ref('')
// 加载状态
const loading = ref(false)
const submitting = ref(false)
const joiningClass = ref(false)
const showJoinDialog = ref(false)
const joinForm = ref({
  invitationCode: ''
})
// 课程列表
const courses = ref([])

/**
 * 判断课程是否被选中
 */
const isSelected = (course) => {
  return selectedCourseKey.value === course.selectionKey
}

/**
 * 加载课程列表
 */
const loadCourses = async () => {
  loading.value = true
  try {
    const courseResponse = await getCourses()
    const courseList = normalizeCourseListResponse(courseResponse)
    courses.value = courseList.items

    const preferredCourseId = currentCourseId.value ?? courseList.currentCourseId
    const restoredCourse = preferredCourseId === null
      ? null
      : findCourseByIdentity(preferredCourseId, currentClassId.value)
    selectedCourseKey.value = restoredCourse ? restoredCourse.selectionKey : ''
  } catch (error) {
    console.error('获取课程列表失败:', error)
    ElMessage.error('获取课程列表失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

const resolveJoinedCourseIdentity = (joinedClass) => {
  const classInfo = joinedClass && typeof joinedClass === 'object' ? joinedClass : {}
  const publishedCourses = Array.isArray(classInfo?.['courses']) ? classInfo['courses'] : []
  const firstPublishedCourse = publishedCourses[0] || {}
  return {
    courseId: normalizeIdentifier(classInfo?.['course_id'] ?? firstPublishedCourse?.['course_id']),
    classId: normalizeIdentifier(classInfo?.['class_id'] ?? classInfo?.['id'])
  }
}

const refreshCoursesAfterJoin = async (joinedClass) => {
  const joinedCourse = resolveJoinedCourseIdentity(joinedClass)
  courseStore.invalidateCoursesCache()
  const refreshedCourses = await courseStore.fetchCourses()
  courses.value = refreshedCourses.map((course, index) => normalizeCourseSummary(course, index))

  const preferredCourse = joinedCourse.courseId === null
    ? null
    : findCourseByIdentity(joinedCourse.courseId, joinedCourse.classId)
  if (preferredCourse) {
    selectedCourseKey.value = preferredCourse.selectionKey
  } else if (!selectedCourseKey.value && courses.value.length) {
    selectedCourseKey.value = courses.value[0].selectionKey
  }
}

const handleJoinClass = async () => {
  const invitationCode = normalizeText(joinForm.value.invitationCode)
  if (!invitationCode) {
    ElMessage.warning('请输入班级邀请码')
    return
  }

  joiningClass.value = true
  try {
    const joinedClass = await apiJoinClass({ code: invitationCode })
    await refreshCoursesAfterJoin(joinedClass)
    showJoinDialog.value = false
    joinForm.value.invitationCode = ''

    if (courses.value.length) {
      ElMessage.success('已加入班级，请选择课程进入学习')
    } else {
      ElMessage.success('已加入班级，待老师发布课程后即可开始学习')
    }
  } catch (error) {
    console.error('加入班级失败:', error)
    if (!error?.handledByInterceptor) {
      ElMessage.error(error?.message || '加入失败，请检查邀请码是否正确')
    }
  } finally {
    joiningClass.value = false
  }
}

/**
 * 选择课程（单选）
 */
const handleSelectCourse = (course) => {
  // 单选逻辑：点击即选中，不允许取消选中（除非选另一个）
  if (selectedCourseKey.value !== course.selectionKey) {
    selectedCourseKey.value = course.selectionKey
  }
}

/**
 * 确认选择
 */
const confirmSelect = async () => {
  if (!selectedCourseKey.value) return

  // 找到选中的课程
  const course = findCourseBySelectionKey(selectedCourseKey.value)
  if (!course) return

  submitting.value = true
  try {
    // 调用API选择课程（后端可能会记录用户选择的上下文）
    await selectCourseApi({
      course_id: course.id,
      class_id: course.classId
    })

    // 保存选中的课程到store
    courseStore.setCurrentCourse({
      course_id: course.id,
      course_name: course.name,
      class_id: course.classId,
      class_name: course.className
    })

    ElMessage.success({
      message: `欢迎进入 ${course.name}`,
      type: 'success',
      duration: 2000
    })

    // 跳转到学生仪表盘
    await router.push('/student/dashboard')

  } catch (error) {
    console.error('选择课程失败:', error)
    ElMessage.error('进入课程失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.course-select-view {
  min-height: 100vh;
  background: var(--bg-page);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 40px;
}

.main-container {
  width: 100%;
  max-width: 1200px;
  background: transparent;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 48px;
  color: var(--accent-cyan);
  background: rgba(14, 165, 164, 0.12);
  padding: 16px;
  border-radius: 50%;
  margin-bottom: 8px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin: 0;
}

.page-header p {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

/* 课程列表 */
.course-grid {
  justify-content: center;
}

.course-card-wrapper {
  margin-bottom: 24px;
  padding: 4px;
  /* Space for border effect */
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.course-card-wrapper:hover {
  transform: translateY(-5px);
}

.course-card-wrapper.is-selected {
  background: var(--primary-color);
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 10px 24px rgba(18, 154, 116, 0.22);
}

.course-card {
  border: none;
  border-radius: 8px;
  overflow: hidden;
  height: 100%;
}

.card-cover {
  height: 140px;
  /* background fallback */
  background: #b9ccc2;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.course-icon {
  font-size: 48px;
  color: #fff;
  opacity: 0.8;
}

.check-mark {
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--success-color);
  color: #fff;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-content {
  padding: 20px;
  text-align: center;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.course-meta {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 按钮 */
.page-footer {
  text-align: center;
  margin-top: 40px;
  padding-bottom: 40px;
}

.submit-btn {
  padding: 12px 60px;
  font-size: 18px;
  height: 50px;
  box-shadow: 0 10px 24px rgba(18, 154, 116, 0.24);
}

/* Loading & Empty */
.loading-container {
  max-width: 800px;
  margin: 0 auto;
}

.course-skeleton {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.empty-state :deep(.el-empty__description) {
  max-width: 420px;
  line-height: 1.7;
}
</style>
