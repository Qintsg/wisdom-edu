/**
 * 用户状态存储
 * 使用Composition API风格实现
 * 管理用户登录状态、认证信息和用户数据
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getUserInfo, updateUserInfo, logout as logoutApi } from '@/api/auth'
import { getMenu } from '@/api/common'
import { resetTokenRefreshState, setLoggingOut } from '@/api'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // ==================== 帮助函数 ====================

  /** 
   * 获取当前激活的存储（Local或Session）
   * 优先检查localStorage，如果不存在Token则检查sessionStorage
   * 默认返回localStorage以便写入
   */
  const getStorage = () => {
    if (localStorage.getItem('access_token')) return localStorage
    if (sessionStorage.getItem('access_token')) return sessionStorage
    return localStorage
  }

  // ==================== 状态定义 ====================

  const activeStorage = getStorage()

  /** 访问令牌 */
  const token = ref(activeStorage.getItem('access_token') || activeStorage.getItem('token') || '')
  /** 刷新令牌 */
  const refreshToken = ref(activeStorage.getItem('refresh_token') || '')
  /** 用户信息对象 */
  const user = ref(JSON.parse(activeStorage.getItem('userInfo') || 'null'))
  /** 动态菜单 */
  const menu = ref([])
  /** 加载状态 */
  const loading = ref(false)

  /**
   * 清除认证相关的持久化数据
   * 同时覆盖 localStorage 与 sessionStorage，避免切换记住我策略后残留旧会话。
   */
  const clearPersistedAuthState = () => {
    const authStorageKeys = ['access_token', 'token', 'refresh_token', 'userInfo']
    authStorageKeys.forEach(key => {
      localStorage.removeItem(key)
      sessionStorage.removeItem(key)
    })
  }

  /**
   * 将登录/注册接口响应收敛为统一的会话模型
   * 兼容新旧字段名，避免在多个入口重复拼装 access、refresh 与 userInfo。
   */
  const buildSessionPayload = (authResponse) => {
    const authData = authResponse && typeof authResponse === 'object' ? authResponse : {}
    return {
      accessToken: authData.access || authData.token || '',
      refreshTokenValue: authData.refresh || authData.refresh_token || '',
      userInfo: authData.user || {
        user_id: authData.user_id,
        username: authData.username,
        role: authData.role
      }
    }
  }

  /**
   * 应用认证成功后的会话数据
   * 统一同步 store 与浏览器存储，并返回角色供调用方完成后续路由跳转。
   */
  const applySessionPayload = (authResponse, storage) => {
    const sessionPayload = buildSessionPayload(authResponse)

    token.value = sessionPayload.accessToken
    refreshToken.value = sessionPayload.refreshTokenValue

    clearPersistedAuthState()

    storage.setItem('access_token', sessionPayload.accessToken)
    storage.setItem('token', sessionPayload.accessToken)
    if (sessionPayload.refreshTokenValue) {
      storage.setItem('refresh_token', sessionPayload.refreshTokenValue)
    }

    user.value = sessionPayload.userInfo
    storage.setItem('userInfo', JSON.stringify(sessionPayload.userInfo))

    return sessionPayload.userInfo.role
  }

  // ==================== 计算属性 ====================

  /** 是否已登录 */
  const isLoggedIn = computed(() => !!token.value)
  /** 是否为学生角色 */
  const isStudent = computed(() => user.value?.role === 'student')
  /** 是否为教师角色 */
  const isTeacher = computed(() => user.value?.role === 'teacher')
  /** 是否为管理员角色 */
  const isAdmin = computed(() => user.value?.role === 'admin')
  /** 用户角色标识 */
  const userRole = computed(() => user.value?.role || '')
  /** 用户ID */
  const userId = computed(() => user.value?.user_id)
  /** 用户名（优先显示真实姓名） */
  const username = computed(() => user.value?.real_name || user.value?.username)

  // ==================== 方法定义 ====================

  /**
   * 用户登录
   * @param {Object} credentials - 登录凭证对象
   * @param {string} credentials.username - 用户名
   * @param {string} credentials.password - 密码
   * @param {boolean} [credentials.rememberMe] - 是否记住登录（默认为false，通过sessionStorage）
   * @returns {Promise<string>} 登录成功返回用户角色
   * @throws {Error} 登录失败时抛出错误
   */
  async function login(credentials) {
    loading.value = true
    try {
      const data = await loginApi({ username: credentials.username, password: credentials.password }) as any

      // 登录成功后重置Token刷新状态
      resetTokenRefreshState()

      // 决定存储位置
      const storage = credentials.rememberMe ? localStorage : sessionStorage

      return applySessionPayload(data, storage)
    } catch (error) {
      console.error('登录失败:', error)
      throw error  // 抛出错误让调用方处理
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户注册
   * @param {Object} registerData - 注册信息
   * @returns {Promise<string>} 注册成功返回用户角色
   */
  async function register(registerData) {
    loading.value = true
    try {
      const data = await registerApi(registerData) as any
      resetTokenRefreshState()

      // 注册默认使用 localStorage，或者可以根据需求调整
      const storage = localStorage

      return applySessionPayload(data, storage)
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   * 调用API将refresh token加入黑名单，然后清除本地状态
   */
  function logout() {
    setLoggingOut(true)

    // 先调用API使refresh token失效（不等待结果，避免阻塞退出）
    logoutApi().catch(() => { })

    token.value = ''
    refreshToken.value = ''
    user.value = null

    // 清除两边的存储
    const keys = ['access_token', 'token', 'refresh_token', 'userInfo', 'current_course', 'currentCourse']
    keys.forEach(key => {
      localStorage.removeItem(key)
      sessionStorage.removeItem(key)
    })

    void router.push('/login')
  }

  /**
   * 获取用户信息
   * 根据Token从服务器获取用户详细信息
   * @returns {Promise<Object|null>} 用户信息或null
   */
  async function fetchUserInfo() {
    if (!token.value) return null

    try {
      const data = await getUserInfo()
      user.value = data

      // 更新当前使用的存储中的用户信息
      const storage = getStorage()
      storage.setItem('userInfo', JSON.stringify(data))

      return data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取失败（如Token失效），可能需要Logout，但这取决于业务
      // logout() 
      return null
    }
  }

  /**
   * 更新用户信息
   * @param {Object} data - 要更新的字段
   * @returns {Promise<Object>} 更新结果
   */
  async function updateProfile(data) {
    try {
      const result = await updateUserInfo(data)
      user.value = { ...user.value, ...data }

      // 更新当前使用的存储
      const storage = getStorage()
      storage.setItem('userInfo', JSON.stringify(user.value))

      return result
    } catch (error) {
      console.error('更新用户信息失败:', error)
      throw error
    }
  }

  /**
   * 设置认证Token (手动设置)
   */
  function setToken(accessToken, refresh = '') {
    token.value = accessToken
    refreshToken.value = refresh
    // 默认存local
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('token', accessToken)
    if (refresh) {
      localStorage.setItem('refresh_token', refresh)
    }
  }

  /**
   * 设置用户信息 (手动设置)
   */
  function setUserInfo(info) {
    user.value = info
    getStorage().setItem('userInfo', JSON.stringify(info))
  }

  /**
   * 获取动态菜单
   * 根据用户角色从后端获取菜单配置
   */
  async function fetchMenu() {
    try {
      const res = await getMenu() as any
      // 后端返回 {menu: [...], role: '...'}, 拦截器自动提取data
      menu.value = (res && res.menu) ? res.menu : (Array.isArray(res) ? res : [])
    } catch (e) {
      console.error('获取菜单失败:', e)
      menu.value = []
    }
  }

  /**
   * 初始化用户状态
   * 应用启动时调用，尝试从Storage恢复并验证
   */
  async function init() {
    const storage = getStorage()
    // 重新从Storage读取以确保一致性 (虽然由于ref引用可能已经是新的)
    const storedToken = storage.getItem('access_token') || storage.getItem('token')

    if (storedToken) {
      token.value = storedToken
      refreshToken.value = storage.getItem('refresh_token') || ''
      try {
        const storedUser = JSON.parse(storage.getItem('userInfo') || 'null')
        if (storedUser) {
          user.value = storedUser
        }
      } catch (e) {
        console.error('Failed to parse user info', e)
      }

      // 如果有Token但没有用户详情，或者想要更新最新的用户详情
      if (!user.value) {
        await fetchUserInfo()
      }
    }
  }

  // 这里的init并不会自动调用，而在main.js或App.vue中调用比较合适
  // 但为了兼容旧代码，可以在这里同步执行一次简单的状态恢复
  // 注意：Pinia store setup函数在store被use时执行
  // 简单的同步恢复已经通过 `const token = ref(...)` 完成了

  return {
    token,
    refreshToken,
    user,
    menu,
    loading,
    isLoggedIn,
    isStudent,
    isTeacher,
    isAdmin,
    userRole,
    userId,
    username,
    login,
    register,
    logout,
    fetchUserInfo,
    updateProfile,
    fetchMenu,
    setToken,
    setUserInfo,
    init
  }
})
