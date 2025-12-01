/**
 * 课程相关组合式函数
 * 提供课程选择、课程信息等功能
 */
import { computed, watch } from 'vue'
import { useCourseStore, type NormalizedCourse } from '@/stores/course'
import { ElMessage } from 'element-plus'

/**
 * 使用课程功能
 */
export function useCourse() {
  const courseStore = useCourseStore()

  // ========== 计算属性 ==========

  // 课程列表
  const courses = computed(() => courseStore.courses)

  // 当前选中的课程
  const currentCourse = computed(() => courseStore.currentCourse)

  // 当前课程ID
  const courseId = computed(() => courseStore.courseId)

  // 当前课程名称
  const courseName = computed(() => courseStore.courseName)

  // 当前选中的班级
  const currentClass = computed(() => courseStore.currentClass)

  // 当前班级ID
  const classId = computed(() => courseStore.classId)

  // 是否有选中课程
  const hasCourse = computed(() => courseStore.hasCourse)

  // 是否正在加载
  const loading = computed(() => courseStore.loading)

  // ========== 方法 ==========

  /**
   * 获取课程列表
   * @returns {Promise<Array>}
   */
  const fetchCourses = async (): Promise<NormalizedCourse[]> => {
    try {
      return await courseStore.fetchCourses()
    } catch (error) {
      ElMessage.error('获取课程列表失败')
      return []
    }
  }

  /**
   * 选择课程
   * @param {Object} course - 课程对象
   */
  const selectCourse = (course: NormalizedCourse | null) => {
    if (!course) {
      ElMessage.warning('请选择有效的课程')
      return
    }
    courseStore.selectCourse(course)
    ElMessage.success(`已切换到课程: ${course.course_name}`)
  }

  /**
   * 根据ID选择课程
   * @param {number} id - 课程ID
   */
  const selectCourseById = (id: number | null) => {
    const course = courses.value.find(c => c.course_id === id)
    if (course) {
      selectCourse(course)
    } else {
      ElMessage.warning('未找到指定课程')
    }
  }

  /**
   * 清除选择
   */
  const clearSelection = (): void => {
    courseStore.clearSelection()
  }

  /**
   * 初始化课程
   */
  const initCourse = async (): Promise<void> => {
    courseStore.init()
    if (courses.value.length === 0) {
      await fetchCourses()
    }
  }

  /**
   * 确保有选中的课程
   * @returns {boolean}
   */
  const ensureCourse = (): boolean => {
    if (!hasCourse.value) {
      ElMessage.warning('请先选择一个课程')
      return false
    }
    return true
  }

  /**
   * 创建课程选择器的选项
   */
  const courseOptions = computed(() =>
    courses.value.map(course => ({
      value: course.course_id,
      label: course.course_name,
      ...course
    }))
  )

  return {
    // 状态
    courses,
    currentCourse,
    courseId,
    courseName,
    currentClass,
    classId,
    hasCourse,
    loading,
    courseOptions,
    // 方法
    fetchCourses,
    selectCourse,
    selectCourseById,
    clearSelection,
    initCourse,
    ensureCourse
  }
}

/**
 * 课程选择监听器
 * 用于监听课程变化并执行回调
 * @param {Function} callback - 课程变化时的回调函数
 */
export function useCourseWatcher(callback: (courseId: number) => void) {
  const { courseId, hasCourse } = useCourse()

  watch(
    courseId,
    (newId, oldId) => {
      if (newId && newId !== oldId) {
        callback(newId)
      }
    },
    { immediate: true }
  )

  return { courseId, hasCourse }
}
