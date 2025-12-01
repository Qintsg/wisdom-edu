<template>
  <div class="forbidden-view">
    <div class="forbidden-content">
      <div class="error-icon">
        <el-icon><Lock /></el-icon>
      </div>
      <div class="error-code">403</div>
      <h1 class="error-title">访问被拒绝</h1>
      <p class="error-desc">抱歉，您没有权限访问此页面</p>
      <div class="error-actions">
        <el-button type="primary" size="large" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button size="large" @click="goBack">
          <el-icon><Back /></el-icon>
          返回上页
        </el-button>
      </div>
    </div>
    
    <!-- 装饰背景 -->
    <div class="decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
    </div>
  </div>
</template>

<script setup>
/**
 * 403 无权限访问组件
 */
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { House, Back, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

/**
 * 返回首页
 */
const goHome = () => {
  if (userStore.isLoggedIn) {
    if (userStore.isAdmin) {
      router.push({ name: 'AdminDashboard' })
    } else if (userStore.isTeacher) {
      router.push({ name: 'TeacherDashboard' })
    } else if (userStore.isStudent) {
      router.push({ name: 'StudentDashboard' })
    } else {
      router.push('/')
    }
  } else {
    router.push('/login')
  }
}

/**
 * 返回上一页
 */
const goBack = () => {
  router.back()
}
</script>

<style scoped>
.forbidden-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe4e4 100%);
  position: relative;
  overflow: hidden;
}

.forbidden-content {
  text-align: center;
  z-index: 1;
}

.error-icon {
  font-size: 80px;
  color: #f56c6c;
  margin-bottom: 20px;
}

.error-code {
  font-size: 120px;
  font-weight: 900;
  background: linear-gradient(135deg, #f56c6c 0%, #c45656 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 20px;
}

.error-title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px;
}

.error-desc {
  font-size: 16px;
  color: #909399;
  margin: 0 0 40px;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.error-actions .el-button {
  padding: 12px 32px;
  border-radius: 8px;
}

/* 装饰元素 */
.decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.1) 0%, rgba(196, 86, 86, 0.1) 100%);
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -100px;
  right: -100px;
}

/* 响应式 */
@media (max-width: 768px) {
  .error-icon {
    font-size: 60px;
  }
  
  .error-code {
    font-size: 80px;
  }
  
  .error-title {
    font-size: 24px;
  }
  
  .error-actions {
    flex-direction: column;
    padding: 0 20px;
  }
}
</style>
