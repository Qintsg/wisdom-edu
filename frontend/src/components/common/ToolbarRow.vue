<template>
  <!-- Two-zone toolbar container for filters on the left and secondary actions on the right. -->
  <div class="toolbar-row">
    <div class="toolbar-row__start">
      <slot name="start" />
    </div>
    <div class="toolbar-row__end">
      <slot name="end" />
    </div>
  </div>
</template>

<style scoped>
/* Wrap aggressively so narrow screens keep controls usable instead of overflowing horizontally. */
.toolbar-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.toolbar-row__start,
.toolbar-row__end {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
