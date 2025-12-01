<template>
  <!-- Shared page intro block: title on the left, optional CTA slot on the right. -->
  <section class="page-hero">
    <div class="hero-copy">
      <p v-if="eyebrow" class="hero-eyebrow">{{ eyebrow }}</p>
      <h1 class="hero-title">{{ title }}</h1>
      <p v-if="description" class="hero-description">{{ description }}</p>
      <slot name="meta" />
    </div>
    <div v-if="$slots.actions" class="hero-actions">
      <slot name="actions" />
    </div>
  </section>
</template>

<script setup>
// Keep the API intentionally small so pages can reuse the hero without layout-specific props.
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>

<style scoped>
/* Soft gradient and generous radius give dashboard pages a consistent entry section. */
.page-hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  padding: 28px;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.72), transparent 38%),
    linear-gradient(135deg, rgba(223, 233, 226, 0.95), rgba(241, 246, 242, 0.98));
  box-shadow: var(--hero-shadow);
}

.hero-copy {
  display: grid;
  gap: 8px;
}

.hero-eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.hero-title {
  margin: 0;
  font-size: 28px;
  line-height: 1.15;
  font-weight: 800;
  color: var(--hero-text);
}

.hero-description {
  margin: 0;
  max-width: 720px;
  font-size: 14px;
  color: var(--text-regular);
}

.hero-actions {
  /* Actions stay inline on wide screens, then naturally wrap beneath the copy on mobile. */
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .page-hero {
    padding: 20px;
    flex-direction: column;
  }

  .hero-title {
    font-size: 22px;
  }
}
</style>
