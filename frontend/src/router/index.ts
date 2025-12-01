/**
 * 路由配置文件
 * 整合所有路由模块，创建路由实例
 */
import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards'

import authRoutes from './routes/auth'
import studentRoutes from './routes/student'
import teacherRoutes from './routes/teacher'
import adminRoutes from './routes/admin'

const DefaultLayout = () => import('@/layouts/DefaultLayout.vue')
const AuthLayout = () => import('@/layouts/AuthLayout.vue')
const EmptyLayout = () => import('@/layouts/EmptyLayout.vue')

const NotFoundView = () => import('@/views/common/NotFoundView.vue')
const ForbiddenView = () => import('@/views/common/ForbiddenView.vue')

/**
 * 基础路由配置
 * 包含根路由、错误页面等
 */
const baseRoutes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: ForbiddenView,
    meta: {
      title: '无权限访问',
      layout: 'empty'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
    meta: {
      title: '页面不存在',
      layout: 'empty'
    }
  }
]

/**
 * 使用布局组件包装路由
 * @param {Array|Object} routes - 路由配置
 * @param {string} layoutType - 布局类型
 * @returns {Object} 包装后的路由配置
 */
const wrapWithLayout = (routes, layoutType) => {
  const layouts = {
    default: DefaultLayout,
    auth: AuthLayout,
    empty: EmptyLayout
  }

  const layoutComponent = layouts[layoutType] || layouts.default

  if (Array.isArray(routes)) {
    return {
      path: '/',
      component: layoutComponent,
      children: routes
    }
  }

  return {
    ...routes,
    component: layoutComponent
  }
}

/**
 * 组装所有路由
 */
const routes = [
  // 基础路由
  ...baseRoutes,

  // 认证页面路由（使用AuthLayout）
  wrapWithLayout(authRoutes, 'auth'),

  // 学生端路由（使用DefaultLayout）
  wrapWithLayout(studentRoutes, 'default'),

  // 教师端路由（使用DefaultLayout）
  wrapWithLayout(teacherRoutes, 'default'),

  // 管理端路由（使用DefaultLayout）
  wrapWithLayout(adminRoutes, 'default')
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
  // 滚动行为：页面切换时滚动到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

setupRouterGuards(router)

export default router
