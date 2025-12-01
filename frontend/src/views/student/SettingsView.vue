<template>
  <div class="settings-view" v-loading="loading">
    <el-card class="settings-card" shadow="hover">
      <template #header>
        <span>个人信息</span>
      </template>

      <el-form :model="accountForm" label-width="100px" class="settings-form">
        <el-form-item label="头像">
          <div class="avatar-field">
            <el-avatar :size="64" :src="avatarUrl" class="user-avatar">
              {{ accountForm.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <input ref="avatarInput" type="file" accept="image/*" class="avatar-file-input"
              @change="handleAvatarChange" />
            <el-button size="small" class="avatar-trigger-button" @click="triggerAvatarPicker">更换头像</el-button>
          </div>
        </el-form-item>

        <el-form-item label="用户名">
          <el-input v-model="accountForm.username" placeholder="支持中文、英文、数字和下划线">
            <template #append>
              <el-tooltip content="用户名仅支持中文、英文、数字和下划线" placement="top">
                <el-icon>
                  <InfoFilled />
                </el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="真实姓名">
          <el-input v-model="accountForm.realName" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="学号/工号">
          <el-input v-model="accountForm.studentId" placeholder="请输入学号或工号" />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="accountForm.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="手机号">
          <el-input v-model="accountForm.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveUserInfo" :loading="loading">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" shadow="hover">
      <template #header>
        <span>学习偏好</span>
      </template>

      <el-form :model="preferenceForm" label-width="120px" class="settings-form">
        <el-form-item label="偏好资源">
          <el-select v-model="preferenceForm.preferredResource" style="width: 100%">
            <el-option label="视频" value="video" />
            <el-option label="文档" value="document" />
            <el-option label="练习" value="exercise" />
          </el-select>
        </el-form-item>

        <el-form-item label="学习时段">
          <el-select v-model="preferenceForm.preferredStudyTime" style="width: 100%">
            <el-option label="早上" value="morning" />
            <el-option label="下午" value="afternoon" />
            <el-option label="晚上" value="evening" />
          </el-select>
        </el-form-item>

        <el-form-item label="学习节奏">
          <el-select v-model="preferenceForm.studyPace" style="width: 100%">
            <el-option label="慢节奏" value="slow" />
            <el-option label="适中" value="moderate" />
            <el-option label="快节奏" value="fast" />
            <el-option label="自适应" value="adaptive" />
          </el-select>
        </el-form-item>

        <el-form-item label="学习风格">
          <el-select v-model="preferenceForm.learningStyle" style="width: 100%">
            <el-option label="视觉型" value="visual" />
            <el-option label="听觉型" value="auditory" />
            <el-option label="读写型" value="reading" />
            <el-option label="动手型" value="kinesthetic" />
          </el-select>
        </el-form-item>

        <el-form-item label="每日学习时长">
          <el-select v-model="preferenceForm.studyDuration" style="width: 100%">
            <el-option label="30分钟以内" value="short" />
            <el-option label="30-60分钟" value="medium" />
            <el-option label="60分钟以上" value="long" />
          </el-select>
        </el-form-item>

        <el-form-item label="复习频率">
          <el-select v-model="preferenceForm.reviewFrequency" style="width: 100%">
            <el-option label="每天复习" value="daily" />
            <el-option label="每周复习" value="weekly" />
            <el-option label="按需复习" value="as_needed" />
          </el-select>
        </el-form-item>

        <el-form-item label="接受挑战">
          <el-select v-model="preferenceForm.acceptChallenge" style="width: 100%">
            <el-option label="喜欢挑战" value="yes" />
            <el-option label="适度挑战" value="moderate" />
            <el-option label="偏好简单" value="no" />
          </el-select>
        </el-form-item>

        <el-form-item label="每日目标(分钟)">
          <el-input-number v-model="preferenceForm.dailyGoalMinutes" :min="10" :max="480" :step="10"
            style="width: 100%" />
        </el-form-item>

        <el-form-item label="每周学习天数">
          <el-input-number v-model="preferenceForm.weeklyGoalDays" :min="1" :max="7" :step="1" style="width: 100%" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="savePreferences">保存偏好</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" shadow="hover">
      <template #header>
        <span>修改密码</span>
      </template>

      <el-form :model="passwordForm" label-width="100px" class="settings-form">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>

        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>

        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="savingPassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 个人设置视图
 */
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getUserInfo, updateUserInfo, changePassword as changePasswordApi } from '@/api/auth'
import { getProfile, updateHabitPreference } from '@/api/student/profile'
import { useCourseStore } from '@/stores/course'
import { toBackendAbsoluteUrl } from '@/api/backend'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

// 常量定义
const MIN_PASSWORD_LENGTH = 8

const userStore = useUserStore()
const courseStore = useCourseStore()

// 加载状态
const loading = ref(false)
const savingPassword = ref(false)
const avatarInput = ref(null)
const avatarUrl = ref('')

/**
 * 收敛文本字段，避免模板直接消费动态 payload。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return String(rawValue)
  }
  return ''
}

/**
 * 收敛数值字段，避免偏好表单出现 NaN。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 将任意对象型 payload 收敛为普通对象。
 * @param {unknown} rawValue
 * @returns {Record<string, unknown>}
 */
const normalizeObjectFromPayload = (rawValue) => {
  return rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue)
    ? rawValue
    : {}
}

/**
 * 构造默认账户信息表单。
 * @returns {{ username: string, realName: string, studentId: string, email: string, phone: string }}
 */
const buildDefaultAccountForm = () => ({
  username: '',
  realName: '',
  studentId: '',
  email: '',
  phone: ''
})

/**
 * 构造默认学习偏好表单。
 * @returns {{ preferredResource: string, preferredStudyTime: string, studyPace: string, learningStyle: string, studyDuration: string, reviewFrequency: string, acceptChallenge: string, dailyGoalMinutes: number, weeklyGoalDays: number }}
 */
const buildDefaultPreferenceForm = () => ({
  preferredResource: 'video',
  preferredStudyTime: 'evening',
  studyPace: 'moderate',
  learningStyle: 'visual',
  studyDuration: 'medium',
  reviewFrequency: 'weekly',
  acceptChallenge: 'moderate',
  dailyGoalMinutes: 60,
  weeklyGoalDays: 5
})

/**
 * 将用户信息接口返回映射为内部账户表单。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {{ username: string, realName: string, studentId: string, email: string, phone: string, avatarUrl: string }}
 */
const normalizeUserInfoPayload = (rawPayload) => ({
  username: normalizeText(rawPayload?.username),
  realName: normalizeText(rawPayload?.real_name),
  studentId: normalizeText(rawPayload?.student_id),
  email: normalizeText(rawPayload?.email),
  phone: normalizeText(rawPayload?.phone),
  avatarUrl: toBackendAbsoluteUrl(normalizeText(rawPayload?.avatar))
})

/**
 * 将学习偏好接口返回映射为内部表单。
 * @param {unknown} rawPayload
 * @returns {{ preferredResource: string, preferredStudyTime: string, studyPace: string, learningStyle: string, studyDuration: string, reviewFrequency: string, acceptChallenge: string, dailyGoalMinutes: number, weeklyGoalDays: number }}
 */
const normalizePreferencePayload = (rawPayload) => {
  const preferencePayload = normalizeObjectFromPayload(rawPayload)

  return {
    ...buildDefaultPreferenceForm(),
    preferredResource: normalizeText(preferencePayload.preferred_resource) || 'video',
    preferredStudyTime: normalizeText(preferencePayload.preferred_study_time) || 'evening',
    studyPace: normalizeText(preferencePayload.study_pace) || 'moderate',
    learningStyle: normalizeText(preferencePayload.learning_style) || 'visual',
    studyDuration: normalizeText(preferencePayload.study_duration) || 'medium',
    reviewFrequency: normalizeText(preferencePayload.review_frequency) || 'weekly',
    acceptChallenge: normalizeText(preferencePayload.accept_challenge) || 'moderate',
    dailyGoalMinutes: normalizeNumber(preferencePayload.daily_goal_minutes, 60),
    weeklyGoalDays: normalizeNumber(preferencePayload.weekly_goal_days, 5)
  }
}

// 用户信息表单
const accountForm = reactive(buildDefaultAccountForm())

const preferenceForm = reactive(buildDefaultPreferenceForm())

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const triggerAvatarPicker = () => {
  avatarInput.value?.click()
}

/**
 * 加载用户信息
 */
const loadUserInfo = async () => {
  loading.value = true
  try {
    const userInfoPayload = normalizeUserInfoPayload(await getUserInfo())
    Object.assign(accountForm, {
      username: userInfoPayload.username,
      realName: userInfoPayload.realName,
      studentId: userInfoPayload.studentId,
      email: userInfoPayload.email,
      phone: userInfoPayload.phone
    })
    avatarUrl.value = userInfoPayload.avatarUrl

    if (courseStore.courseId) {
      const profilePayload = await getProfile(courseStore.courseId)
      Object.assign(preferenceForm, normalizePreferencePayload(profilePayload?.habit_preferences))
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 保存用户信息
 */
const saveUserInfo = async () => {
  // 用户名格式校验：仅支持中英文、数字和下划线
  if (accountForm.username && !/^[\w\u4e00-\u9fff]+$/.test(accountForm.username)) {
    ElMessage.warning('用户名仅支持中文、英文、数字和下划线')
    return
  }
  try {
    await updateUserInfo({
      username: accountForm.username,
      real_name: accountForm.realName,
      student_id: accountForm.studentId,
      email: accountForm.email,
      phone: accountForm.phone
    })
    // 同步更新Store中的用户名
    userStore.setUserInfo({ ...userStore.user, username: accountForm.username, real_name: accountForm.realName })
    ElMessage.success('个人信息保存成功')
  } catch (error) {
    console.error('保存用户信息失败:', error)
    ElMessage.error(error?.detail || error?.message || '保存失败，请重试')
  }
}

/**
 * 处理头像文件选择
 */
const handleAvatarChange = async (event) => {
  const selectedFile = event.target.files?.[0]
  if (!selectedFile) return

  // 检查文件类型
  if (!selectedFile.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }

  // 检查文件大小（最大2MB）
  if (selectedFile.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过2MB')
    return
  }

  try {
    const formData = new FormData()
    formData.append('avatar', selectedFile)
    await updateUserInfo(formData, { headers: { 'Content-Type': 'multipart/form-data' } })

    // 本地预览
    const reader = new FileReader()
    reader.onload = (e) => {
      avatarUrl.value = normalizeText(e.target?.result)
    }
    reader.readAsDataURL(selectedFile)

    ElMessage.success('头像更新成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败，请重试')
  }
}

const savePreferences = async () => {
  try {
    await updateHabitPreference({
      preferred_resource: preferenceForm.preferredResource,
      preferred_study_time: preferenceForm.preferredStudyTime,
      study_pace: preferenceForm.studyPace,
      learning_style: preferenceForm.learningStyle,
      study_duration: preferenceForm.studyDuration,
      review_frequency: preferenceForm.reviewFrequency,
      accept_challenge: preferenceForm.acceptChallenge,
      daily_goal_minutes: preferenceForm.dailyGoalMinutes,
      weekly_goal_days: preferenceForm.weeklyGoalDays
    })
    ElMessage.success('学习偏好已更新')
  } catch (error) {
    console.error('更新学习偏好失败:', error)
    ElMessage.error('学习偏好更新失败，请重试')
  }
}

/**
 * 修改密码
 */
const changePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    ElMessage.warning('请填写完整的密码信息')
    return
  }
  if (passwordForm.newPassword.length < MIN_PASSWORD_LENGTH) {
    ElMessage.warning(`新密码长度不能少于${MIN_PASSWORD_LENGTH}个字符`)
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  savingPassword.value = true
  try {
    await changePasswordApi({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    ElMessage.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error(error.message || '修改密码失败，请检查原密码是否正确')
  } finally {
    savingPassword.value = false
  }
}

onMounted(() => {
  void loadUserInfo()
})
</script>

<style scoped>
.settings-view {
  max-width: 800px;
  margin: 0 auto;
}

.settings-card {
  margin-bottom: 20px;
}

.settings-form {
  max-width: 500px;
}

.avatar-field {
  display: flex;
  align-items: center;
}

.avatar-file-input {
  display: none;
}

.avatar-trigger-button {
  margin-left: 16px;
}

.user-avatar {
  background: var(--primary-color);
  color: #fff;
  font-size: 24px;
  font-weight: 600;
}
</style>
