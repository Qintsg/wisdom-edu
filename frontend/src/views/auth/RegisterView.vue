<template>
  <div class="register-view">
    <h2 class="form-title">创建新账号</h2>
    <p class="form-desc">注册账号，加入自适应学习系统</p>

    <el-form ref="formRef" :model="form" :rules="rules" class="register-form" @submit.prevent="handleRegister">
      <!-- 用户名 -->
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" size="large" :prefix-icon="User" clearable />
      </el-form-item>

      <!-- 邮箱 -->
      <el-form-item prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱（选填）" size="large" :prefix-icon="Message" clearable />
      </el-form-item>

      <!-- 密码 -->
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码（至少8位，包含大写字母和数字）" size="large"
          :prefix-icon="Lock" show-password />
      </el-form-item>

      <!-- 确认密码 -->
      <el-form-item prop="confirmPassword">
        <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" size="large" :prefix-icon="Lock"
          show-password />
      </el-form-item>

      <!-- 角色选择 -->
      <el-form-item prop="role">
        <div class="role-selector">
          <div v-for="role in roles" :key="role.value" :class="['role-card', { active: form.role === role.value }]"
            @click="form.role = role.value">
            <el-icon class="role-icon">
              <component :is="role.icon" />
            </el-icon>
            <span class="role-label">{{ role.label }}</span>
          </div>
        </div>
      </el-form-item>

      <!-- 激活码（教师/管理员需要） -->
      <el-form-item v-if="needActivationCode" prop="activation_code">
        <el-input v-model="form.activation_code" placeholder="请输入激活码" size="large" :prefix-icon="Key" />
      </el-form-item>

      <!-- 注册按钮 -->
      <el-form-item>
        <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleRegister">
          {{ loading ? '注册中...' : '注 册' }}
        </el-button>
      </el-form-item>

      <!-- 登录链接 -->
      <div class="form-footer">
        <span>已有账号？</span>
        <router-link to="/login" class="login-link">立即登录</router-link>
      </div>
    </el-form>
  </div>
</template>

<script setup>
/**
 * 注册视图组件
 * 提供用户注册功能
 */
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Key, Reading, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const formRef = ref(null)

// 加载状态
const loading = ref(false)

// 角色列表
const roles = [
  { value: 'student', label: '学生', icon: Reading },
  { value: 'teacher', label: '教师', icon: UserFilled }
]

// 表单数据
const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'student',
  activation_code: ''
})

// 是否需要激活码
const needActivationCode = computed(() => {
  return ['teacher', 'admin'].includes(form.role)
})

// 密码验证
const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 8) {
    callback(new Error('密码长度至少8位'))
  } else if (!/[A-Z]/.test(value)) {
    callback(new Error('密码必须包含大写字母'))
  } else if (!/[0-9]/.test(value)) {
    callback(new Error('密码必须包含数字'))
  } else {
    callback()
  }
}

// 确认密码验证
const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择身份', trigger: 'change' }
  ],
  activation_code: [
    { required: true, message: '教师/管理员需要激活码', trigger: 'blur' }
  ]
}

/**
 * 处理注册
 */
const handleRegister = async () => {
  // 验证表单
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    // 构建注册数据
    const registerData = {
      username: form.username,
      password: form.password,
      role: form.role
    }

    if (form.email) {
      registerData.email = form.email
    }

    if (needActivationCode.value) {
      registerData.activation_code = form.activation_code
    }

    // 调用注册API
    await userStore.register(registerData)
    ElMessage.success('注册成功，欢迎加入！')

    // 根据角色跳转到对应页面
    if (userStore.isAdmin) {
      await router.push({ name: 'AdminDashboard' })
    } else if (userStore.isTeacher) {
      await router.push({ name: 'TeacherDashboard' })
    } else if (userStore.isStudent) {
      await router.push({ name: 'StudentDashboard' })
    } else {
      await router.push('/')
    }
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error(error.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-view {
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
  margin: 0 0 24px;
}

.register-form {
  width: 100%;
}

.register-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.register-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(20, 184, 166, 0.12);
}

.register-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(20, 184, 166, 0.2);
}

/* 角色选择器 */
.role-selector {
  width: 100%;
  display: flex;
  gap: 16px;
}

.role-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.role-card:hover {
  border-color: var(--accent-cyan);
  background: rgba(20, 184, 166, 0.06);
}

.role-card.active {
  border-color: var(--accent-cyan);
  background: rgba(109, 146, 125, 0.12);
  box-shadow: 0 10px 18px rgba(78, 111, 93, 0.08);
}

.role-icon {
  font-size: 28px;
  color: #909399;
  margin-bottom: 8px;
  transition: color 0.3s;
}

.role-card.active .role-icon {
  color: var(--accent-cyan);
}

.role-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.role-card.active .role-label {
  color: var(--accent-cyan);
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

.login-link {
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

.login-link:hover {
  background: rgba(109, 146, 125, 0.14);
  border-color: rgba(78, 111, 93, 0.36);
}
</style>
