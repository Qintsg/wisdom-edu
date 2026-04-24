<template>
  <!-- Compact login form keeps the recovery and registration paths visible without leaving the page. -->
  <div class="login-view">
    <h2 class="form-title">欢迎回来</h2>
    <p class="form-desc">登录您的账号，开启个性化学习之旅</p>

    <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @submit.prevent="handleLogin">
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" size="large" :prefix-icon="User" clearable />
      </el-form-item>

      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" :prefix-icon="Lock"
          show-password @keyup.enter="handleLogin" />
      </el-form-item>

      <el-form-item>
        <div class="form-options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <a href="javascript:;" class="forgot-link" @click="ElMessage.info('请联系管理员重置密码')">忘记密码？</a>
        </div>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleLogin">
          {{ loading ? '登录中...' : '登 录' }}
        </el-button>
      </el-form-item>

      <div class="form-footer">
        <span>还没有账号？</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { extractApiErrorMessage, isApiErrorHandled } from '@/api'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

// Remember-me travels with the login payload so persistence policy stays owned by the auth store.
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  // Reuse Element Plus form validation so keyboard submit and button click share one path.
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login({ ...form, rememberMe: rememberMe.value })
    ElMessage.success('登录成功，欢迎回来！')

    // Prefer an intercepted redirect, then fall back to the first dashboard that matches the signed-in role.
    const redirect = route.query.redirect
    if (redirect && typeof redirect === 'string') {
      await router.push(redirect)
    } else if (userStore.isAdmin) {
      await router.push({ name: 'AdminDashboard' })
    } else if (userStore.isTeacher) {
      await router.push({ name: 'TeacherDashboard' })
    } else if (userStore.isStudent) {
      await router.push({ name: 'StudentDashboard' })
    } else {
      await router.push('/')
    }
  } catch (error) {
    // Surface backend auth feedback while still logging the raw error for local diagnosis.
    console.error('登录失败:', error)
    if (!isApiErrorHandled(error)) {
      ElMessage.error(extractApiErrorMessage(error, '登录失败，请检查用户名和密码'))
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  width: 100%;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.form-desc {
  font-size: 14px;
  color: #909399;
  margin: 0 0 32px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(20, 184, 166, 0.12);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 2px 12px rgba(20, 184, 166, 0.2);
}

.form-options {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-link {
  color: var(--accent-cyan);
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s;
}

.forgot-link:hover {
  color: var(--primary-color);
}

.submit-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 14px;
  background: rgba(109, 146, 125, 0.1) !important;
  border: 1px solid rgba(78, 111, 93, 0.34) !important;
  color: var(--primary-dark) !important;
  box-shadow: 0 10px 20px rgba(78, 111, 93, 0.08);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-1px);
  background: rgba(109, 146, 125, 0.16) !important;
  border-color: rgba(78, 111, 93, 0.5) !important;
  box-shadow: 0 14px 24px rgba(78, 111, 93, 0.12);
}

.submit-btn:active {
  transform: translateY(0);
}

.form-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 16px;
}

.register-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  margin-left: 10px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(109, 146, 125, 0.18);
  background: rgba(109, 146, 125, 0.08);
  color: var(--primary-dark);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.register-link:hover {
  background: rgba(109, 146, 125, 0.14);
  border-color: rgba(78, 111, 93, 0.36);
}
</style>
