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
          <el-empty description="暂无可选课程" :image-size="200" />
        </div>

        <el-row v-else :gutter="24" class="course-grid">
          <el-col v-for="course in courses" :key="course.id" :xs="24" :sm="12" :md="8" :lg="6">
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
          <el-button type="primary" size="large" class="submit-btn" :disabled="!selectedCourseId" :loading="submitting"
            @click="confirmSelect" round>
            确认并进入课程
            <el-icon class="el-icon--right">
              <ArrowRight />
            </el-icon>
          </el-button>
        </div>
      </el-footer>
    </el-container>
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
import { generateCoverStyle } from '@/utils/courseCover'
import { ElMessage } from 'element-plus'
import { Check, Collection, Reading, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const courseStore = useCourseStore()
const currentCourseId = computed(() => courseStore.courseId)

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeIdentifier = (value, fallback = null) => {
  if (value === null || value === undefined || value === '') return fallback
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue : value
}

const normalizeCourseSummary = (value, index) => {
  const course = value && typeof value === 'object' ? value : {}
  return {
    id: normalizeIdentifier(course?.['course_id'] ?? course?.['id'], index),
    name: normalizeText(course?.['course_name'] ?? course?.['name']) || '未命名课程',
    classId: normalizeIdentifier(course?.['class_id'] ?? course?.['class_obj_id']),
    className: normalizeText(course?.['class_name'] ?? course?.['class_obj_name']),
    coverUrl: normalizeText(course?.['course_cover'] ?? course?.['cover']),
    teacherName: normalizeText(course?.['teacher_name'])
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

const getCoverStyle = (course) => generateCoverStyle(course.id, course.name)


// 选中的课程ID（单选）
const selectedCourseId = ref(null)
// 加载状态
const loading = ref(false)
const submitting = ref(false)
// 课程列表
const courses = ref([])

/**
 * 判断课程是否被选中
 */
const isSelected = (course) => {
  return String(selectedCourseId.value) === String(course.id)
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
    const restoredCourse = preferredCourseId === null ? null : findCourseById(preferredCourseId)
    selectedCourseId.value = restoredCourse ? restoredCourse.id : null
  } catch (error) {
    console.error('获取课程列表失败:', error)
    ElMessage.error('获取课程列表失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

/**
 * 选择课程（单选）
 */
const handleSelectCourse = (course) => {
  // 单选逻辑：点击即选中，不允许取消选中（除非选另一个）
  if (String(selectedCourseId.value) !== String(course.id)) {
    selectedCourseId.value = course.id
  }
}

/**
 * 确认选择
 */
const confirmSelect = async () => {
  if (!selectedCourseId.value) return

  // 找到选中的课程
  const course = findCourseById(selectedCourseId.value)
  if (!course) return

  submitting.value = true
  try {
    // 调用API选择课程（后端可能会记录用户选择的上下文）
    await selectCourseApi({
      course_id: selectedCourseId.value,
      class_id: course.classId
    })

    // 保存选中的课程到store
    courseStore.setCurrentCourse({
      course_id: selectedCourseId.value,
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
</style>
