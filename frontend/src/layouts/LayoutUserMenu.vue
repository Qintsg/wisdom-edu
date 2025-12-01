<template>
  <!-- Account menu groups profile actions and role-specific shortcuts behind one stable trigger. -->
  <el-dropdown trigger="click" @command="$emit('command', $event)">
    <div class="user-dropdown">
      <el-avatar v-if="avatarUrl" :size="32" :src="avatarUrl" class="user-avatar" />
      <el-avatar v-else :size="32" class="user-avatar">
        {{ avatarText }}
      </el-avatar>
      <span class="user-name">{{ displayName }}</span>
      <el-icon class="el-icon--right">
        <ArrowDown />
      </el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="profile">
          <el-icon>
            <User />
          </el-icon>
          个人信息
        </el-dropdown-item>
        <el-dropdown-item command="settings">
          <el-icon>
            <Setting />
          </el-icon>
          个人设置
        </el-dropdown-item>
        <el-dropdown-item v-if="userRole === 'admin'" command="system-settings">
          <el-icon>
            <Setting />
          </el-icon>
          系统设置
        </el-dropdown-item>
        <el-dropdown-item divided command="logout">
          <el-icon>
            <SwitchButton />
          </el-icon>
          退出登录
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { ArrowDown, Setting, SwitchButton, User } from '@element-plus/icons-vue'

// The parent decides command handling so this menu stays presentational and reusable.
defineProps({
  avatarUrl: { type: String, default: null },
  avatarText: { type: String, default: '' },
  displayName: { type: String, default: '用户' },
  userRole: { type: String, default: '' }
})

defineEmits(['command'])
</script>

<style scoped>
/* Rounded container keeps the header action visually lightweight next to course switching. */
.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px 6px 10px;
  border-radius: 999px;
  cursor: pointer;
  border: 1px solid var(--border-light);
  background: var(--bg-elevated);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
  transition: all 0.3s;
}

.user-dropdown:hover {
  background: var(--bg-soft-alt);
}

.user-avatar {
  /* Fallback initials need the same emphasis as uploaded avatars. */
  background: var(--primary-color);
  color: #fff;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 700;
}

</style>
