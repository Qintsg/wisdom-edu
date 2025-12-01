<template>
  <!-- Standard content card with an optional descriptive header to keep admin pages visually aligned. -->
  <el-card class="section-card" shadow="hover">
    <template v-if="title || $slots.header" #header>
      <div class="section-card__header">
        <div>
          <h3 v-if="title" class="section-card__title">{{ title }}</h3>
          <p v-if="description" class="section-card__description">{{ description }}</p>
        </div>
        <slot name="header" />
      </div>
    </template>
    <slot />
  </el-card>
</template>

<script setup>
// Title and description cover the common header case; a slot handles custom controls when needed.
defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' }
})
</script>

<style scoped>
/* Header keeps summary text and injected actions separated without forcing a fixed layout. */
.section-card__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.section-card__title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-card__description {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
