<script setup>
defineProps({
  icon: { type: String, default: '📝' },
  title: String, description: String,
  actionText: String, to: [String, Object],
});
</script>
<template>
  <div class="empty">
    <div class="empty-ico">{{ icon }}</div>
    <h2 v-if="title">{{ title }}</h2>
    <p v-if="description">{{ description }}</p>
    <div v-if="actionText" class="empty-action">
      <component :is="to ? 'router-link' : 'button'" :to="to" class="btn">{{ actionText }}</component>
    </div>
  </div>
</template>
<style scoped>
.empty { text-align: center; padding: 36px 0; color: var(--text-faint); font-size: 13px; }
.empty .empty-ico { font-size: 30px; margin-bottom: 8px; opacity: .6; }
.empty h2 { font-size: 20px; margin: 0 0 8px; color: var(--text); }
.empty p { margin: 0 auto; max-width: 420px; color: var(--text-muted); line-height: 1.7; }
.empty .empty-action { margin-top: 18px; }
</style>
