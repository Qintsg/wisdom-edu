<template>
  <div class="settings-view">
    <el-card class="page-header" shadow="never">
      <h2>个人设置</h2>
    </el-card>

    <el-card shadow="hover" class="settings-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <el-form :model="accountForm" label-width="100px" class="settings-form">
            <el-form-item label="用户名">
              <el-input v-model="accountForm.username" disabled />
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="accountForm.displayName" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="accountForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="accountForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saveLoading" @click="saveInfo">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="课程配置" name="course">
          <el-alert v-if="!selectedCourseId" type="info" :closable="false" style="margin-bottom: 16px;">
            请先在顶部选择一门课程以配置其参数
          </el-alert>
          <template v-else>
            <el-form :model="courseConfigForm" label-width="140px" class="settings-form" v-loading="configLoading">
              <el-divider content-position="left">作业设置</el-divider>
              <el-form-item label="作业及格分">
                <el-input-number v-model="courseConfigForm.exam_pass_score" :min="0" :max="100" :step="5" />
              </el-form-item>
              <el-form-item label="作答时长(分钟)">
                <el-input-number v-model="courseConfigForm.exam_duration" :min="5" :max="300" :step="5" />
              </el-form-item>
              <el-form-item label="允许重做">
                <el-switch v-model="courseConfigForm.allow_retake" />
              </el-form-item>
              <el-form-item v-if="courseConfigForm.allow_retake" label="最大重做次数">
                <el-input-number v-model="courseConfigForm.max_retake_times" :min="1" :max="10" />
              </el-form-item>
              <el-form-item label="提交后显示答案">
                <el-switch v-model="courseConfigForm.show_answer_after_exam" />
              </el-form-item>

              <el-divider content-position="left">课程管理</el-divider>
              <el-form-item label="资源审核">
                <el-switch v-model="courseConfigForm.resource_approval" />
                <span style="margin-left: 8px; color: #909399; font-size: 12px;">开启后学生上传资源需审核</span>
              </el-form-item>
              <el-form-item label="自动发布作业">
                <el-switch v-model="courseConfigForm.auto_publish_exam" />
              </el-form-item>
              <el-form-item label="允许迟交">
                <el-switch v-model="courseConfigForm.allow_late_submission" />
              </el-form-item>
              <el-form-item label="初始评测题数">
                <el-input-number v-model="courseConfigForm.initial_assessment_count" :min="5" :max="50" :step="5" />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" :loading="configSaving" @click="saveCourseConfig">保存配置</el-button>
              </el-form-item>
            </el-form>
          </template>
        </el-tab-pane>

        <el-tab-pane label="修改密码" name="password">
          <el-form :model="passwordForm" label-width="100px" class="settings-form">
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入当前密码" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码（至少8位）" show-password />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="passwordLoading" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 教师端 - 个人设置视图
 * 管理教师个人信息、课程配置和密码修改
 */
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getUserInfo, updateUserInfo, changePassword as apiChangePassword } from '@/api/auth'
import { getCourseSettings, updateCourseSettings } from '@/api/teacher/settings'
import { useCourseStore } from '@/stores/course'

const courseStore = useCourseStore()

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
 * 构造默认账户表单。
 * @returns {{ username: string, displayName: string, email: string, phone: string }}
 */
const buildDefaultAccountForm = () => ({
  username: '',
  displayName: '',
  email: '',
  phone: ''
})

/**
 * 将用户信息接口返回收敛为教师设置页内部模型。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {{ username: string, displayName: string, email: string, phone: string }}
 */
const normalizeUserInfoPayload = (rawPayload) => ({
  username: normalizeText(rawPayload?.username),
  displayName: normalizeText(rawPayload?.real_name ?? rawPayload?.name),
  email: normalizeText(rawPayload?.email),
  phone: normalizeText(rawPayload?.phone)
})

// 当前标签
const activeTab = ref('info')

// 加载状态
const saveLoading = ref(false)
const passwordLoading = ref(false)
const configLoading = ref(false)
const configSaving = ref(false)

// 当前选中的课程ID
const selectedCourseId = ref(courseStore.courseId || null)

// 基本信息表单
const accountForm = reactive(buildDefaultAccountForm())

// 课程配置表单
const courseConfigForm = reactive({
  exam_pass_score: 60,
  exam_duration: 60,
  allow_retake: true,
  max_retake_times: 3,
  resource_approval: false,
  auto_publish_exam: false,
  show_answer_after_exam: true,
  allow_late_submission: false,
  initial_assessment_count: 10
})

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

/**
 * 加载用户信息
 */
const loadUserInfo = async () => {
  try {
    Object.assign(accountForm, normalizeUserInfoPayload(await getUserInfo()))
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

/**
 * 加载课程配置
 */
const loadCourseConfig = async () => {
  if (!selectedCourseId.value) return
  configLoading.value = true
  try {
    const data = await getCourseSettings(selectedCourseId.value)
    if (data) {
      Object.keys(courseConfigForm).forEach(key => {
        if (data[key] !== undefined) courseConfigForm[key] = data[key]
      })
    }
  } catch (error) {
    console.error('加载课程配置失败:', error)
  } finally {
    configLoading.value = false
  }
}

/**
 * 保存课程配置
 */
const saveCourseConfig = async () => {
  if (!selectedCourseId.value) return
  configSaving.value = true
  try {
    await updateCourseSettings(selectedCourseId.value, { ...courseConfigForm })
    ElMessage.success('课程配置保存成功')
  } catch (error) {
    console.error('保存课程配置失败:', error)
    ElMessage.error('保存失败')
  } finally {
    configSaving.value = false
  }
}

// 监听课程变化
watch(() => courseStore.courseId, (newVal) => {
  selectedCourseId.value = newVal
  if (newVal && activeTab.value === 'course') {
    void loadCourseConfig()
  }
})

// 切换到课程配置tab时加载
watch(activeTab, (tab) => {
  if (tab === 'course' && selectedCourseId.value) {
    void loadCourseConfig()
  }
})

/**
 * 保存基本信息
 */
const saveInfo = async () => {
  saveLoading.value = true
  try {
    await updateUserInfo({
      real_name: accountForm.displayName,
      email: accountForm.email,
      phone: accountForm.phone
    })
    ElMessage.success('信息保存成功')
  } catch (error) {
    console.error('保存信息失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

/**
 * 修改密码
 */
const changePassword = async () => {
  if (!passwordForm.oldPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.newPassword || passwordForm.newPassword.length < 8) {
    ElMessage.warning('新密码至少需要8位')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  passwordLoading.value = true
  try {
    await apiChangePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    ElMessage.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  void loadUserInfo()
})
</script>

<style scoped>
.settings-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.settings-card {
  max-width: 700px;
}

.settings-form {
  padding: 20px 0;
}
</style>
