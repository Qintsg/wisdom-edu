<template>
  <div class="empty-layout">
    <router-view v-slot="{ Component, route }">
      <transition name="empty-fade" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
/**
 * 空布局组件
 * 用于404页面、403页面等不需要任何布局的页面
 * 特点：全屏显示，无额外装饰
 */
</script>

<style scoped>
.empty-layout {
  min-height: 100vh;
  width: 100%;
  background: #f5f7fa;
}

/* 页面切换动画 */
.empty-fade-enter-active,
.empty-fade-leave-active {
  transition: opacity 0.3s ease;
}

.empty-fade-enter-from,
.empty-fade-leave-to {
  opacity: 0;
}
</style>
