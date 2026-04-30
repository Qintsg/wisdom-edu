/**
 * 课程状态存储
 * 使用Composition API风格实现
 * 管理课程列表、当前选中课程和班级信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/api/index'

type CourseIdentifier = number | null

export interface CourseRecord {
  id?: CourseIdentifier
  course_id?: CourseIdentifier
  name?: string
  course_name?: string
  class_id?: CourseIdentifier
  class_obj_id?: CourseIdentifier
  class_name?: string
  class_obj_name?: string
  [key: string]: unknown
}

export interface NormalizedCourse extends CourseRecord {
  course_id: CourseIdentifier
  course_name: string
  class_id: CourseIdentifier
  class_name: string
}

export interface SelectedClassInfo {
  class_id: CourseIdentifier
  class_name: string
}

interface CourseListPayload {
  courses?: CourseRecord[]
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function normalizeIdentifier(value: unknown): CourseIdentifier {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }
  if (typeof value === 'string' && value.trim() !== '') {
    const numericValue = Number(value)
    return Number.isFinite(numericValue) ? numericValue : null
  }
  return null
}

function normalizeText(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

export const useCourseStore = defineStore('course', () => {
  const normalizeCourse = (course: unknown): NormalizedCourse | null => {
    if (!isRecord(course)) return null

    return {
      ...course,
      id: normalizeIdentifier(course.id),
      course_id: normalizeIdentifier(course.course_id ?? course.id),
      name: normalizeText(course.name),
      course_name: normalizeText(course.course_name ?? course.name),
      class_id: normalizeIdentifier(course.class_id ?? course.class_obj_id),
      class_name: normalizeText(course.class_name ?? course.class_obj_name)
    }
  }

  // ==================== 状态定义 ====================

  /** 课程列表 */
  const courses = ref<NormalizedCourse[]>([])
  /** 当前选中的课程 */
  const currentCourse = ref<NormalizedCourse | null>(null)
  /** 当前选中的班级 */
  const currentClass = ref<SelectedClassInfo | null>(null)
  /** 加载状态 */
  const loading = ref(false)
  // DEMO_EMBED: 简易缓存，避免短时间内重复请求课程列表
  let _coursesCacheTime = 0
  const COURSES_CACHE_TTL = 15000 // 15秒缓存有效期

  function invalidateCoursesCache(): void {
    _coursesCacheTime = 0
  }

  // ==================== 计算属性 ====================

  /** 是否已选择课程 */
  const hasCourse = computed(() => !!currentCourse.value)
  /** 当前课程ID */
  const courseId = computed(() => currentCourse.value?.course_id ?? currentCourse.value?.id ?? null)
  /** 当前班级ID */
  const classId = computed(() => currentClass.value?.class_id)
  /** 当前课程名称 */
  const courseName = computed(() => currentCourse.value?.course_name || currentCourse.value?.name || '')
  /** 当前班级名称 */
  const className = computed(() => currentClass.value?.class_name || '')

  // ==================== 方法定义 ====================

  /**
   * 获取课程列表
   * 从服务器获取用户可访问的课程
   * @param {Object} [params] - 查询参数
   * @returns {Promise<Array>} 课程列表
   */
  async function fetchCourses(params: Record<string, unknown> = {}): Promise<NormalizedCourse[]> {
    // DEMO_EMBED: 缓存命中时直接返回，避免冗余请求
    if (_coursesCacheTime && Date.now() - _coursesCacheTime < COURSES_CACHE_TTL && courses.value.length > 0) {
      return courses.value
    }
    loading.value = true
    try {
      const data = await request.get<CourseListPayload | CourseRecord[]>('/api/courses', { params })
      const rawCourses = Array.isArray(data) ? data : data.courses || []
      courses.value = Array.isArray(rawCourses)
        ? rawCourses.map(normalizeCourse).filter((course): course is NormalizedCourse => course !== null)
        : []
      _coursesCacheTime = Date.now() // DEMO_EMBED: 更新缓存时间戳

      // 如果有课程但未选择，默认选择第一个
      if (courses.value.length > 0 && !currentCourse.value) {
        selectCourse(courses.value[0])
      }

      return courses.value
    } catch (error) {
      console.error('获取课程列表失败:', error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 选择课程
   * 设置当前选中的课程并保存到本地存储
   * @param {Object} course - 课程信息
   */
  function selectCourse(course: unknown): void {
    const normalizedCourse = normalizeCourse(course)
    currentCourse.value = normalizedCourse
    currentClass.value = normalizedCourse?.class_id != null ? {
      class_id: normalizedCourse.class_id,
      class_name: normalizedCourse.class_name
    } : null

    // 保存到本地存储
    localStorage.setItem('current_course', JSON.stringify(normalizedCourse))
  }

  /**
   * 选择班级
   * 设置当前选中的班级
   * @param {Object} classInfo - 班级信息
   */
  function selectClass(classInfo: SelectedClassInfo | null): void {
    currentClass.value = classInfo
  }

  /**
   * 清空选择
   * 清除当前选中的课程和班级
   */
  function clearSelection(): void {
    currentCourse.value = null
    currentClass.value = null
    localStorage.removeItem('current_course')
  }

  /**
   * 初始化课程状态
   * 从本地存储恢复上次选中的课程
   */
  function init(): void {
    const saved = localStorage.getItem('current_course')
    if (saved) {
      try {
        const course: unknown = JSON.parse(saved)
        const normalizedCourse = normalizeCourse(course)
        currentCourse.value = normalizedCourse
        if (normalizedCourse?.class_id != null) {
          currentClass.value = {
            class_id: normalizedCourse.class_id,
            class_name: normalizedCourse.class_name
          }
        }
      } catch {
        localStorage.removeItem('current_course')
      }
    }
  }

  /**
   * 更新课程列表中的某个课程
   * @param {Object} updatedCourse - 更新后的课程信息
   */
  function updateCourse(updatedCourse: unknown): void {
    const normalizedCourse = normalizeCourse(updatedCourse)
    if (!normalizedCourse) {
      return
    }

    const index = courses.value.findIndex(c => c.course_id === normalizedCourse?.course_id)
    if (index !== -1) {
      courses.value[index] = { ...courses.value[index], ...normalizedCourse }
      // 如果是当前选中的课程，也更新
      const activeCourse = currentCourse.value
      if (activeCourse && activeCourse.course_id === normalizedCourse.course_id) {
        currentCourse.value = { ...activeCourse, ...normalizedCourse }
        localStorage.setItem('current_course', JSON.stringify(currentCourse.value))
      }
    }
  }

  /**
   * 添加课程到列表
   * @param {Object} course - 新课程信息
   */
  function addCourse(course: unknown): void {
    const normalizedCourse = normalizeCourse(course)
    if (normalizedCourse) {
      courses.value.push(normalizedCourse)
    }
  }

  /**
   * 从列表中移除课程
   * @param {number} courseIdVal - 课程ID
   */
  function removeCourse(courseIdVal: number): void {
    courses.value = courses.value.filter(c => c.course_id !== courseIdVal)
    // 如果删除的是当前选中的课程，清空选择
    if (currentCourse.value?.course_id === courseIdVal) {
      clearSelection()
    }
  }

  /**
   * 设置当前课程（别名方法）
   * 兼容调用 setCurrentCourse 的代码
   * @param {Object} course - 课程信息
   */
  function setCurrentCourse(course: unknown): void {
    selectCourse(course)
  }

  /**
   * 切换课程（别名方法）
   * 兼容调用 switchCourse(courseId, classId) 的代码
   * @param {number} courseIdVal - 课程ID
   * @param {number} [classIdVal] - 班级ID（可选）
   */
  function switchCourse(courseIdVal: number | string, classIdVal?: number | null): void {
    // 从课程列表中查找完整课程对象
    const course = courses.value.find(c => c.course_id === courseIdVal || c.course_id === Number(courseIdVal))
    if (course) {
      selectCourse(course)
    } else {
      // fallback：构建最小课程对象
      selectCourse({ course_id: courseIdVal, class_id: classIdVal })
    }
  }

  /**
   * Ensure a specific course is selected, using route-scoped ids when provided.
   * @param {number|string|null} courseIdVal
   * @returns {Promise<number|null>}
   */
  async function ensureCourse(courseIdVal: number | string | null | undefined): Promise<number | null> {
    const normalizedId = normalizeIdentifier(courseIdVal)
    if (normalizedId !== null && currentCourse.value?.course_id === normalizedId) {
      return normalizedId
    }

    if (!courses.value.length) {
      await fetchCourses()
    }

    const matchedCourse = courses.value.find(course => course.course_id !== null && course.course_id === normalizedId)
    if (matchedCourse) {
      selectCourse(matchedCourse)
      return matchedCourse.course_id
    }

    if (normalizedId !== null) {
      selectCourse({ course_id: normalizedId })
      return normalizedId
    }

    if (currentCourse.value?.course_id) {
      return currentCourse.value.course_id
    }

    await fetchCourses()
    return currentCourse.value?.course_id ?? null
  }

  /**
   * 校验是否已选择课程（供视图层统一调用）
   * @param {string} [hint] - 自定义提示文本
   * @returns {boolean} 是否已选课程
   */
  function requireCourseId(hint?: string): boolean {
    if (!courseId.value) {
      console.warn(hint || '操作需要先选择课程')
      return false
    }
    return true
  }

  return {
    courses,
    currentCourse,
    currentClass,
    loading,
    hasCourse,
    courseId,
    classId,
    courseName,
    className,
    invalidateCoursesCache,
    fetchCourses,
    selectCourse,
    selectClass,
    clearSelection,
    init,
    updateCourse,
    addCourse,
    removeCourse,
    setCurrentCourse,
    switchCourse,
    ensureCourse,
    requireCourseId
  }
})
