<template>
  <div class="auth-layout">
    <!-- 左侧品牌区域 -->
    <div class="auth-brand">
      <div class="brand-background">
        <div class="bg-shape shape-1"></div>
        <div class="bg-shape shape-2"></div>
        <div class="bg-shape shape-3"></div>
      </div>
      <div class="brand-content">
        <div class="brand-logo" @click="goHome">
          <img src="/images/logo.svg" alt="Logo" class="auth-logo" />
          <h1 class="brand-title">自适应学习系统</h1>
        </div>
        <p class="brand-subtitle">知识图谱驱动的个性化自适应学习系统</p>
        <div class="brand-features">
          <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div><strong>知识图谱</strong><br><span>可视化知识结构，精准定位薄弱点</span></div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div><strong>个性化路径</strong><br><span>AI 规划最优学习路径</span></div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <div><strong>智能辅导</strong><br><span>AI 助手实时答疑解惑</span></div>
          </div>
        </div>
      </div>
      <div class="brand-footer">
        <p>© {{ currentYear }} 自适应学习系统</p>
      </div>
    </div>

    <!-- 右侧表单区域 -->
    <div class="auth-form-area">
      <div class="form-container">
        <router-view v-slot="{ Component, route }">
          <transition name="auth-fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentYear = computed(() => new Date().getFullYear())
const goHome = () => router.push('/')
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
}

/* 左侧品牌区 */
.auth-brand {
  flex: 0 0 45%;
  background: #e6eee8;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 48px;
  position: relative;
  overflow: hidden;
}

.brand-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(109, 146, 125, 0.1);
  animation: float 20s infinite ease-in-out;
}

.shape-1 {
  width: 350px;
  height: 350px;
  top: -80px;
  left: -80px;
}

.shape-2 {
  width: 250px;
  height: 250px;
  bottom: -40px;
  right: -40px;
  animation-delay: -5s;
}

.shape-3 {
  width: 180px;
  height: 180px;
  top: 50%;
  left: 55%;
  animation-delay: -10s;
}

@keyframes float {

  0%,
  100% {
    transform: translate(0, 0) rotate(0deg);
  }

  25% {
    transform: translate(20px, -20px) rotate(5deg);
  }

  50% {
    transform: translate(-10px, 20px) rotate(-5deg);
  }

  75% {
    transform: translate(-20px, -10px) rotate(3deg);
  }
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: var(--hero-text);
}

.brand-logo {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: transform 0.3s;
}

.brand-logo:hover {
  transform: scale(1.05);
}

.auth-logo {
  width: 52px;
  height: 52px;
  filter: drop-shadow(0 4px 8px rgba(37, 59, 49, 0.12));
}

.brand-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
}

.brand-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 14px 0 0;
}

.brand-features {
  margin-top: 48px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  color: var(--text-regular);
  font-size: 14px;
  line-height: 1.5;
}

.feature-icon {
  font-size: 28px;
  flex-shrink: 0;
  margin-top: 2px;
}

.feature-item strong {
  font-size: 15px;
  color: var(--text-primary);
}

.feature-item span {
  font-size: 13px;
  color: var(--text-secondary);
}

.brand-footer {
  position: absolute;
  bottom: 24px;
  left: 0;
  right: 0;
  text-align: center;
  z-index: 1;
}

.brand-footer p {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

/* 右侧表单区 */
.auth-form-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  padding: 48px;
  overflow-y: auto;
}

.form-container {
  width: 100%;
  max-width: 420px;
}

/* 页面切换动画 */
.auth-fade-enter-active,
.auth-fade-leave-active {
  transition: all 0.3s ease;
}

.auth-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.auth-fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* 响应式：平板及以下 */
@media (max-width: 900px) {
  .auth-layout {
    flex-direction: column;
  }

  .auth-brand {
    flex: 0 0 auto;
    padding: 32px 24px;
  }

  .brand-features {
    display: none;
  }

  .brand-footer {
    display: none;
  }

  .auth-form-area {
    padding: 32px 20px;
  }
}

@media (max-width: 480px) {
  .auth-brand {
    padding: 24px 16px;
  }

  .brand-title {
    font-size: 24px;
  }

  .auth-logo {
    width: 40px;
    height: 40px;
  }

  .auth-form-area {
    padding: 24px 16px;
  }
}
</style>
