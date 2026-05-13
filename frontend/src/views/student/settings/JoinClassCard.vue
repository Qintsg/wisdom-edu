<template>
  <el-card class="settings-card" shadow="hover">
    <template #header>
      <span>加入班级</span>
    </template>

    <el-form :model="joinClassForm" label-width="100px" class="settings-form" @submit.prevent="joinClassByInvitation">
      <el-form-item label="邀请码">
        <el-input v-model="joinClassForm.invitationCode" placeholder="请输入班级邀请码" clearable maxlength="20"
          @keyup.enter="joinClassByInvitation" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="joiningClass" :disabled="!normalizeText(joinClassForm.invitationCode)"
          @click="joinClassByInvitation">加入班级</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
/**
 * 学生设置页的班级邀请码加入卡片。
 */
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { joinClass as apiJoinClass } from '@/api/student/class'
import { useCourseStore } from '@/stores/course'
import { useUserStore } from '@/stores/user'

const courseStore = useCourseStore()
const userStore = useUserStore()
const joiningClass = ref(false)
const joinClassForm = reactive({
  invitationCode: ''
})

const normalizeText = (rawValue) => {
  if (rawValue === null || rawValue === undefined) return ''
  return String(rawValue).trim()
}

const refreshLearningContext = async () => {
  courseStore.invalidateCoursesCache()
  await Promise.allSettled([
    userStore.fetchUserInfo(),
    courseStore.fetchCourses()
  ])
}

const joinClassByInvitation = async () => {
  const invitationCode = normalizeText(joinClassForm.invitationCode)
  if (!invitationCode) {
    ElMessage.warning('请输入班级邀请码')
    return
  }

  joiningClass.value = true
  try {
    const joinedClass = await apiJoinClass({ code: invitationCode })
    const joinedClassName = normalizeText(joinedClass?.class_name ?? joinedClass?.name)
    joinClassForm.invitationCode = ''
    await refreshLearningContext()
    ElMessage.success(joinedClassName ? `已加入${joinedClassName}` : '加入班级成功')
  } catch (error) {
    console.error('加入班级失败:', error)
    if (!error?.handledByInterceptor) {
      ElMessage.error(error?.message || '加入失败，请检查邀请码是否正确')
    }
  } finally {
    joiningClass.value = false
  }
}
</script>

<style scoped>
.settings-card {
  margin-bottom: 20px;
}

.settings-form {
  max-width: 500px;
}
</style>
