<template>
  <!-- Only render the trigger when course context exists, avoiding an empty header affordance. -->
  <el-dropdown
    v-if="visible && currentCourse"
    trigger="click"
    @command="$emit('change', $event)"
  >
    <span class="course-selector">
      <el-icon>
        <Reading />
      </el-icon>
      <span class="course-name">{{ currentCourse.course_name }}</span>
      <el-icon class="el-icon--right">
        <ArrowDown />
      </el-icon>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="course in courses"
          :key="course.course_id"
          :command="course"
          :class="{ 'is-active': course.course_id === currentCourse?.course_id }"
        >
          {{ course.course_name }}
        </el-dropdown-item>
        <el-dropdown-item v-if="userRole === 'student'" divided command="switch">
          <el-icon>
            <Switch />
          </el-icon>
          切换课程
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { ArrowDown, Reading, Switch } from '@element-plus/icons-vue'

// The command payload is either a full course object or the student-only "switch" sentinel action.
defineProps({
  visible: { type: Boolean, default: false },
  currentCourse: { type: Object, default: null },
  courses: { type: Array, default: () => [] },
  userRole: { type: String, default: '' }
})

defineEmits(['change'])
</script>

<style scoped>
/* Pill styling helps the current course read like navigational context rather than a plain button. */
.course-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  cursor: pointer;
  color: var(--text-regular);
  background: rgba(15, 108, 189, 0.08);
  border: 1px solid rgba(15, 108, 189, 0.12);
  transition: all 0.3s;
}

.course-selector:hover {
  background: rgba(15, 108, 189, 0.12);
  color: var(--primary-color);
}

.course-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
