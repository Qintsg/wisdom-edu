<template>
  <el-container class="default-layout">
    <el-aside :width="isCollapsed ? '72px' : '252px'" class="layout-sidebar glass-sidebar">
      <div class="sidebar-logo" :class="{ 'is-collapsed': isCollapsed }" @click="goHome">
        <img src="/images/logo.svg" alt="Logo" class="logo-image" />
        <transition name="fade">
          <span v-show="!isCollapsed" class="logo-text">{{ systemTitle }}</span>
        </transition>
      </div>

      <TheSidebar :is-collapse="isCollapsed" />
    </el-aside>

    <el-container class="layout-main-container">
      <div class="layout-ambient" aria-hidden="true">
        <span class="ambient-orb ambient-orb--primary" />
        <span class="ambient-orb ambient-orb--accent" />
      </div>

      <el-header class="layout-header glass-header">
        <div class="header-left">
          <el-icon class="collapse-trigger" @click="toggleCollapse">
            <Expand v-if="isCollapsed" />
            <Fold v-else />
          </el-icon>

          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="homeRoute">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPageTitle">
              {{ currentPageTitle }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <LayoutCourseSwitcher :visible="showCourseSelector" :current-course="currentCourse" :courses="courses"
            :user-role="userRole" @change="handleCourseChange" />

          <LayoutUserMenu :avatar-url="avatarUrl" :avatar-text="avatarText" :display-name="displayName"
            :user-role="userRole" @command="handleUserCommand" />
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component, route: viewRoute }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="resolveRouteKey(viewRoute)" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
/**
 * 默认布局组件
 * 适用于学生端、教师端、管理端
 * 包含侧边栏导航、顶部栏、面包屑、用户菜单等
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCourseStore } from '@/stores/course'
import { selectCourse as selectCourseApi } from '@/api/course'
import TheSidebar from './TheSidebar.vue'
import LayoutCourseSwitcher from './LayoutCourseSwitcher.vue'
import LayoutUserMenu from './LayoutUserMenu.vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { toBackendAbsoluteUrl } from '@/api/backend'
import {
  Expand,
  Fold
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const courseStore = useCourseStore()

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeUserProfile = (value) => {
  const userInfo = value && typeof value === 'object' ? value : {}
  const displayName = normalizeText(userInfo?.['real_name'] ?? userInfo?.['username']) || '用户'
  return {
    displayName,
    avatar: normalizeText(userInfo?.['avatar']),
    username: normalizeText(userInfo?.['username']) || displayName
  }
}

const normalizeCourseSummary = (value) => {
  const courseInfo = value && typeof value === 'object' ? value : {}
  return {
    courseId: courseInfo?.['course_id'] ?? courseInfo?.['id'] ?? null,
    classId: courseInfo?.['class_id'] ?? courseInfo?.['classId'] ?? null,
    courseName: normalizeText(courseInfo?.['course_name'] ?? courseInfo?.['name']),
    className: normalizeText(courseInfo?.['class_name'] ?? courseInfo?.['className'])
  }
}

const resolveRouteKey = (value) => {
  const routeInfo = value && typeof value === 'object' ? value : {}
  return normalizeText(routeInfo?.['fullPath'] ?? routeInfo?.['path'] ?? routeInfo?.['name']) || homeRoute.value
}

const isCollapsed = ref(localStorage.getItem('sidebar_collapsed') === 'true')
const userRole = computed(() => userStore.userRole)

const currentUserProfile = computed(() => normalizeUserProfile(userStore.user))
const displayName = computed(() => currentUserProfile.value.displayName)
const avatarUrl = computed(() => {
  const rawAvatar = currentUserProfile.value.avatar
  if (!rawAvatar) return null
  return toBackendAbsoluteUrl(rawAvatar)
})

const avatarText = computed(() => {
  const name = displayName.value
  return name.charAt(0).toUpperCase()
})

const showCourseSelector = computed(() => {
  return ['student', 'teacher'].includes(userRole.value)
})

const currentCourse = computed(() => courseStore.currentCourse)
const courses = computed(() => courseStore.courses)
const systemTitle = computed(() => {
  const titles = {
    student: '自适应学习',
    teacher: '教师端',
    admin: '管理后台'
  }
  return titles[userRole.value] || '自适应学习'
})

const homeRoute = computed(() => {
  const homes = {
    student: '/student/dashboard',
    teacher: '/teacher/dashboard',
    admin: '/admin/dashboard'
  }
  return homes[userRole.value] || '/'
})

const currentPageTitle = computed(() => normalizeText(route?.['meta']?.['title']))

onMounted(async () => {
  await userStore.fetchMenu()
})

/**
 * 切换侧边栏折叠状态
 */
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebar_collapsed', isCollapsed.value)
}

const handleResize = () => {
  if (window.innerWidth < 992 && !isCollapsed.value) {
    isCollapsed.value = true
  }
}
onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

/**
 * 返回首页
 */
const goHome = () => {
  void router.push(homeRoute.value)
}

/**
 * 处理课程切换
 * @param {Object|string} command - 课程对象或命令
 */
const handleCourseChange = async (command) => {
  if (command === 'switch') {
    await router.push({ name: 'CourseSelect' })
  } else {
    const selectedCourse = normalizeCourseSummary(command)
    if (!selectedCourse.courseId) return

    try {
      const selectedCourseResponse = normalizeCourseSummary(await selectCourseApi({
        course_id: selectedCourse.courseId,
        class_id: selectedCourse.classId
      }))
      courseStore.setCurrentCourse({
        course_id: selectedCourseResponse.courseId || selectedCourse.courseId,
        course_name: selectedCourseResponse.courseName || selectedCourse.courseName,
        class_id: selectedCourseResponse.classId || selectedCourse.classId,
        class_name: selectedCourseResponse.className || selectedCourse.className
      })
      ElMessage.success(`已切换到课程：${selectedCourseResponse.courseName || selectedCourse.courseName}`)
    } catch (error) {
      console.error('切换课程失败:', error)
      ElMessage.error('切换课程失败，请稍后重试')
    }
  }
}

/**
 * 处理用户菜单命令
 * @param {string} command - 菜单命令
 */
const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      if (userRole.value === 'student') {
        await router.push({ name: 'StudentProfile' })
      } else if (userRole.value === 'teacher') {
        await router.push({ name: 'TeacherSettings' })
      } else if (userRole.value === 'admin') {
        await router.push({ name: 'AdminSettings' })
      }
      break
    case 'settings':
      if (userRole.value === 'student') {
        await router.push({ name: 'StudentSettings' })
      } else if (userRole.value === 'teacher') {
        await router.push({ name: 'TeacherSettings' })
      } else if (userRole.value === 'admin') {
        await router.push({ name: 'AdminSettings' })
      }
      break
    case 'system-settings':
      if (userRole.value === 'admin') {
        await router.push({ name: 'AdminSettings' })
      }
      break
    case 'logout':
      await handleLogout()
      break
  }
}

/**
 * 处理退出登录
 */
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出确认',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 先退出登录并跳转，避免当前页面在卸载前响应课程清空导致额外警告
    userStore.logout()

    ElMessage.success('已退出登录')
    setTimeout(() => {
      courseStore.clearSelection()
    }, 0)
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  if (showCourseSelector.value) {
    void courseStore.fetchCourses()
  }
})

watch(
  () => resolveRouteKey(route),
  () => {
    if (showCourseSelector.value && (!courses.value.length || !currentCourse.value)) {
      void courseStore.fetchCourses()
    }
  }
)
</script>

<style scoped>
.default-layout {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.layout-sidebar {
  position: relative;
  background: var(--sidebar-surface);
  transition: width 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--sidebar-border);
  box-shadow: 16px 0 34px rgba(37, 59, 49, 0.06);
}

.sidebar-logo {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  padding: 0 18px;
  background: rgba(255, 255, 255, 0.72);
  border-bottom: 1px solid var(--sidebar-border);
  cursor: pointer;
  transition: background 0.3s, transform 0.3s;
}

.sidebar-logo.is-collapsed {
  justify-content: center;
  gap: 0;
  padding: 0;
}

.sidebar-logo:hover {
  background: rgba(255, 255, 255, 0.9);
}

.logo-image {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 14px;
  box-shadow: 0 12px 24px rgba(7, 43, 34, 0.14);
  background: rgba(255, 255, 255, 0.76);
  padding: 4px;
}

.logo-text {
  font-size: 16px;
  font-weight: 800;
  color: var(--sidebar-text);
  white-space: nowrap;
  letter-spacing: 0.04em;
}

.menu-scrollbar {
  flex: 1;
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
  padding: 12px 8px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 252px;
}

/* 菜单项样式优化 */
:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  margin: 2px 0;
  border-radius: 8px;
  transition: all 0.3s;
  font-size: 14px;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.06) !important;
}

:deep(.el-menu-item.is-active) {
  background: var(--sidebar-active-bg) !important;
  color: var(--sidebar-active-text) !important;
  box-shadow: 0 8px 18px rgba(109, 146, 125, 0.18);
}

/* 主容器 */
.layout-main-container {
  position: relative;
  flex-direction: column;
  overflow: hidden;
}

.layout-ambient {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.ambient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(10px);
  opacity: 0.45;
}

.ambient-orb--primary {
  width: 280px;
  height: 280px;
  top: -80px;
  right: -80px;
  background: radial-gradient(circle, rgba(91, 157, 237, 0.26), transparent 72%);
}

.ambient-orb--accent {
  width: 260px;
  height: 260px;
  bottom: -120px;
  left: -80px;
  background: radial-gradient(circle, rgba(15, 108, 189, 0.18), transparent 74%);
}

/* 顶部栏 */
.layout-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 18px 18px 0;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.58);
  border-radius: 24px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(18px);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-trigger {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 10px;
  border-radius: 14px;
  transition: all 0.3s;
  background: rgba(15, 108, 189, 0.08);
}

.collapse-trigger:hover {
  color: var(--primary-color);
  background: rgba(15, 108, 189, 0.12);
}

.breadcrumb {
  font-size: 14px;
}

.breadcrumb :deep(.el-breadcrumb__item) {
  .el-breadcrumb__inner {
    color: #606266;
    font-weight: 500;
  }

  &:last-child .el-breadcrumb__inner {
    color: #303133;
    font-weight: 600;
  }
}

.breadcrumb :deep(.el-breadcrumb__separator) {
  color: #909399;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 内容区 */
.layout-main {
  position: relative;
  background: var(--bg-page);
  padding: calc(var(--page-padding, 24px) - 4px) var(--page-padding, 24px) var(--page-padding, 24px);
  overflow-y: auto;
}

.layout-main::before {
  content: '';
  position: absolute;
  inset: 12px 18px 18px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.3);
  pointer-events: none;
}

/* 页面切换动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Logo文字渐变动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 下拉菜单激活项 */
:deep(.el-dropdown-menu__item.is-active) {
  color: var(--primary-color);
  background: rgba(109, 146, 125, 0.08);
}
</style>
