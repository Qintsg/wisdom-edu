/**
 * 路由守卫配置
 * 处理权限验证、登录检查、角色权限等
 */
import { useUserStore } from '@/stores/user'
import { useCourseStore } from '@/stores/course'
import { ElMessage } from 'element-plus'

/**
 * 角色与首页路由映射
 */
const roleHomeMap = {
  student: 'StudentDashboard',
  teacher: 'TeacherDashboard',
  admin: 'AdminDashboard'
}

/**
 * 检查用户是否具有所需角色权限
 * @param {Object} userStore - 用户状态存储
 * @param {string} requiredRole - 所需角色
 * @returns {boolean} 是否具有权限
 */
const hasRolePermission = (userStore, requiredRole) => {
  if (!requiredRole) return true

  const userRole = userStore.userRole

  // 管理员拥有所有权限
  if (userRole === 'admin') return true

  // 检查角色匹配
  return userRole === requiredRole
}

/**
 * 获取用户登录后的默认跳转路由
 * @param {Object} userStore - 用户状态存储
 * @returns {string|null} 路由名称
 */
const getDefaultRouteForUser = (userStore) => {
  const role = userStore.userRole
  return roleHomeMap[role] || null
}

/**
 * 检查是否需要跳过课程选择检查
 * @param {Object} to - 目标路由
 * @returns {boolean}
 */
const shouldSkipCourseCheck = (to) => {
  // 检查路由及其匹配的父路由中是否有跳过课程检查的标记
  return to.matched.some(record => record.meta.skipCourseCheck)
}

/**
 * 设置页面标题
 * @param {Object} to - 目标路由
 */
const setPageTitle = (to) => {
  const baseTitle = '自适应学习系统'
  const pageTitle = to.meta.title
  document.title = pageTitle ? `${pageTitle} - ${baseTitle}` : baseTitle
}

/**
 * 注册路由守卫
 * @param {Object} router - Vue Router实例
 */
export function setupRouterGuards(router) {
  // 全局前置守卫
  router.beforeEach(async (to) => {
    setPageTitle(to)

    const userStore = useUserStore()
    const courseStore = useCourseStore()

    // 确保用户状态已恢复（尤其是刷新页面后）
    if (userStore.token && !userStore.user) {
      await userStore.fetchUserInfo()
    }

    // 检查是否需要认证
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
    const isGuestRoute = to.matched.some(record => record.meta.guest)

    // 未登录用户访问需要认证的页面
    if (requiresAuth && !userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      return {
        name: 'Login',
        query: { redirect: to.fullPath }  // 保存原目标路径，登录后跳转
      }
    }

    // 已登录用户访问游客页面（登录、注册等）
    if (isGuestRoute && userStore.isLoggedIn) {
      const defaultRoute = getDefaultRouteForUser(userStore)
      if (defaultRoute) {
        return { name: defaultRoute }
      }
    }

    // 检查角色权限
    const requiredRole = to.matched.find(record => record.meta.role)?.meta.role
    if (requiredRole && !hasRolePermission(userStore, requiredRole)) {
      ElMessage.error('没有访问权限')
      return { name: 'Forbidden' }
    }

    // 学生端：检查是否已选择课程（除了课程选择页和设置页）
    if (userStore.isStudent &&
      to.path.startsWith('/student') &&
      !shouldSkipCourseCheck(to)) {
      // 确保从localStorage恢复课程状态
      if (!courseStore.hasCourse) {
        courseStore.init()
      }
      if (!courseStore.hasCourse) {
        return { name: 'CourseSelect' }
      }
    }

    return true
  })

  // 全局后置守卫
  router.afterEach(() => {
    // 可以在这里添加页面访问统计、NProgress结束等
    // 滚动到页面顶部
    window.scrollTo(0, 0)
  })

  // 全局错误处理
  router.onError((error) => {
    console.error('路由错误:', error)
    ElMessage.error('页面加载失败，请刷新重试')
  })
}

/**
 * 导出角色首页映射供其他模块使用
 */
export { roleHomeMap, getDefaultRouteForUser }
