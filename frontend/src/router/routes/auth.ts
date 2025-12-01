/**
 * 认证相关路由配置
 * 包含登录、注册等不需要认证的页面
 */

// 懒加载认证页面组件
const LoginView = () => import('@/views/auth/LoginView.vue')
const RegisterView = () => import('@/views/auth/RegisterView.vue')

/**
 * 认证路由配置
 * meta.guest: 标记为游客页面，已登录用户访问会重定向
 * meta.layout: 指定使用的布局组件
 */
export default [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      title: '登录',
      guest: true,
      layout: 'auth'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: {
      title: '注册',
      guest: true,
      layout: 'auth'
    }
  }
]
