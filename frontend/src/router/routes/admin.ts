/**
 * 管理端路由配置
 * 所有路由路径以 /admin 为前缀
 */

// 懒加载管理端页面组件
const DashboardView = () => import('@/views/admin/DashboardView.vue')
const UserManageView = () => import('@/views/admin/UserManageView.vue')
const ActivationCodeView = () => import('@/views/admin/ActivationCodeView.vue')
const LogView = () => import('@/views/admin/LogView.vue')
const CourseManageView = () => import('@/views/admin/CourseManageView.vue')
const ClassManageView = () => import('@/views/admin/ClassManageView.vue')
const SettingsView = () => import('@/views/admin/SettingsView.vue')

/**
 * 管理端路由配置
 * meta.requiresAuth: 需要登录认证
 * meta.role: 需要的用户角色
 * meta.title: 页面标题
 */
export default {
  path: '/admin',
  name: 'Admin',
  redirect: '/admin/dashboard',
  meta: {
    requiresAuth: true,
    role: 'admin',
    layout: 'default'
  },
  children: [
    {
      path: 'dashboard',
      name: 'AdminDashboard',
      component: DashboardView,
      meta: {
        title: '控制台',
        icon: 'DataBoard'
      }
    },
    {
      path: 'users',
      name: 'UserManage',
      component: UserManageView,
      meta: {
        title: '用户管理',
        icon: 'User'
      }
    },
    {
      path: 'courses',
      name: 'AdminCourseManage',
      component: CourseManageView,
      meta: {
        title: '课程管理',
        icon: 'Reading'
      }
    },
    {
      path: 'classes',
      name: 'AdminClassManage',
      component: ClassManageView,
      meta: {
        title: '班级管理',
        icon: 'School'
      }
    },
    {
      path: 'activation-codes',
      name: 'ActivationCode',
      component: ActivationCodeView,
      meta: {
        title: '激活码管理',
        icon: 'Key'
      }
    },
    {
      path: 'logs',
      name: 'SystemLog',
      component: LogView,
      meta: {
        title: '系统日志',
        icon: 'Document'
      }
    },
    {
      path: 'settings',
      name: 'AdminSettings',
      component: SettingsView,
      meta: {
        title: '系统设置',
        icon: 'Setting'
      }
    }
  ]
}
