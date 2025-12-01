<template>
  <!-- Settings are grouped by administrator intent so simple system toggles stay easy to scan. -->
  <div class="settings-view">
    <el-card class="settings-card" shadow="hover">
      <template #header>
        <span>基本设置</span>
      </template>
      <el-form :model="basicSettings" label-width="120px" style="max-width: 600px;">
        <el-form-item label="系统名称">
          <el-input v-model="basicSettings.siteName" />
        </el-form-item>
        <el-form-item label="系统描述">
          <el-input v-model="basicSettings.siteDesc" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="联系邮箱">
          <el-input v-model="basicSettings.contactEmail" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveBasic">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" shadow="hover">
      <template #header>
        <span>安全设置</span>
      </template>
      <el-form :model="securitySettings" label-width="120px" style="max-width: 600px;">
        <el-form-item label="允许注册">
          <el-switch v-model="securitySettings.allowRegister" />
        </el-form-item>
        <el-form-item label="登录验证码">
          <el-switch v-model="securitySettings.loginCaptcha" />
        </el-form-item>
        <el-form-item label="密码强度要求">
          <el-select v-model="securitySettings.passwordStrength" style="width: 200px;">
            <el-option label="低（6位以上）" value="low" />
            <el-option label="中（8位+数字）" value="medium" />
            <el-option label="高（8位+大写+数字）" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSecurity">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" shadow="hover">
      <template #header>
        <span>数据管理</span>
      </template>
      <div class="data-actions">
        <el-button @click="backupData">备份数据</el-button>
        <el-button type="warning" @click="clearCache">清除缓存</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

// Local reactive state keeps the demo form editable even before backend persistence is wired in.
const basicSettings = reactive({
  siteName: '自适应学习系统',
  siteDesc: '知识图谱驱动的个性化自适应学习系统',
  contactEmail: 'admin@wisdom-edu.com'
})

const securitySettings = reactive({
  allowRegister: true,
  loginCaptcha: false,
  passwordStrength: 'high'
})

// Feedback is intentionally immediate because these actions currently represent placeholder admin flows.
const saveBasic = () => ElMessage.success('基本设置已保存')
const saveSecurity = () => ElMessage.success('安全设置已保存')
const backupData = () => ElMessage.success('数据备份已开始')
const clearCache = () => ElMessage.success('缓存已清除')
</script>

<style scoped>
/* Constrain width so long form labels remain readable on large admin dashboards. */
.settings-view {
  max-width: 900px;
}

.settings-card {
  margin-bottom: 20px;
}

.data-actions {
  display: flex;
  gap: 12px;
}
</style>
