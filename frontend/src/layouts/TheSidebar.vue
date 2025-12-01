<template>
  <!-- Sidebar reads its structure from the user store so role changes update navigation centrally. -->
  <el-scrollbar wrap-class="scrollbar-wrapper">
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapse"
      :unique-opened="false"
      :collapse-transition="false"
      mode="vertical"
      router
    >
      <template v-for="item in menuList" :key="item.index">
        <el-sub-menu v-if="item.children && item.children.length > 0" :index="item.index">
          <template #title>
            <el-icon v-if="item.icon">
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.title }}</span>
          </template>
          <el-menu-item v-for="child in item.children" :key="child.index" :index="child.index">
            <template #title>
              <el-icon v-if="child.icon">
                <component :is="child.icon" />
              </el-icon>
              <span>{{ child.title }}</span>
            </template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item v-else :index="item.index">
          <el-icon v-if="item.icon">
            <component :is="item.icon" />
          </el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </template>
    </el-menu>
  </el-scrollbar>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

defineProps({
  isCollapse: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const userStore = useUserStore()

// Route path drives the active state because menu indexes already mirror router records.
const menuList = computed(() => userStore.menu)
const activeMenu = computed(() => route.path)
</script>

<style scoped>
/* Remove the stock menu chrome so the sidebar can inherit the shell's custom surface styling. */
.sidebar-menu {
  border-right: none;
  background-color: transparent;
  padding: 16px 12px 20px;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  min-height: 46px;
  margin-bottom: 6px;
  border-radius: 16px !important;
  color: var(--sidebar-text) !important;
  font-weight: 600;
  transition: all 0.28s ease;
}

.sidebar-menu :deep(.el-menu-item .el-icon),
.sidebar-menu :deep(.el-sub-menu__title .el-icon) {
  color: var(--sidebar-icon) !important;
  transition: color 0.28s ease, transform 0.28s ease;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  /* Elevated active state makes the current workspace destination scan quickly. */
  color: var(--sidebar-active-text) !important;
  background: var(--sidebar-active-bg) !important;
  box-shadow: 0 12px 24px rgba(15, 108, 189, 0.24);
}

.sidebar-menu :deep(.el-menu-item.is-active .el-icon) {
  color: var(--sidebar-active-text) !important;
  transform: scale(1.04);
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--sidebar-hover-bg) !important;
  color: var(--sidebar-text) !important;
  transform: translateX(2px);
}

.sidebar-menu :deep(.el-menu-item:hover .el-icon),
.sidebar-menu :deep(.el-sub-menu__title:hover .el-icon) {
  color: var(--sidebar-icon) !important;
}

.sidebar-menu :deep(.el-sub-menu .el-menu) {
  /* Nested menu background creates a clear second level without adding extra separators. */
  background-color: var(--sidebar-submenu-bg) !important;
  border: 1px solid var(--border-light);
  border-radius: 18px;
  margin: 4px 0 10px;
  padding: 6px;
}

.sidebar-menu.el-menu--collapse :deep(.el-sub-menu__title),
.sidebar-menu.el-menu--collapse :deep(.el-menu-item) {
  /* Collapsed mode centers icons on the actual collapsed menu root, not a nonexistent child wrapper. */
  justify-content: center;
  width: 100%;
  min-width: 0;
  padding-inline: 0 !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-tooltip__trigger),
.sidebar-menu.el-menu--collapse :deep(.el-menu-tooltip__trigger) {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item .el-icon),
.sidebar-menu.el-menu--collapse :deep(.el-sub-menu__title .el-icon) {
  margin: 0 !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item:hover),
.sidebar-menu.el-menu--collapse :deep(.el-sub-menu__title:hover) {
  transform: none;
}

.sidebar-menu :deep(.el-sub-menu__icon-arrow) {
  color: var(--sidebar-text-muted) !important;
}

:deep(.el-scrollbar__view) {
  height: 100%;
}
</style>
