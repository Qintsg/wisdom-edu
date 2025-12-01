<script setup>
/**
 * 主应用组件
 * 提供全局配置和根路由视图
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 根据当前路由判断是否需要显示布局过渡动画
const transitionName = computed(() => {
  return route.meta.transition || 'fade'
})
</script>

<template>
  <el-config-provider>
    <router-view v-slot="{ Component }">
      <transition :name="transitionName" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </el-config-provider>
</template>

<style>
/* 全局过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑动过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>
