<script setup>
import { computed } from 'vue';
import Icon from '../Icon.vue';
import BaseButton from './BaseButton.vue';
const props = defineProps({
  // 状态图标：传 lucide 名（如 target）则渲染为线性图标，否则按 emoji/文字回退显示
  icon: { type: String, default: 'target' },
  title: String, description: String,
  actionText: String, to: [String, Object],
});
const isLucide = computed(() => /^[a-z][a-z0-9-]*$/.test(props.icon));
</script>
<template>
  <div class="empty">
    <div class="empty-ico">
      <Icon v-if="isLucide" :name="icon" :size="26" :stroke-width="1.5" />
      <span v-else>{{ icon }}</span>
    </div>
    <h2 v-if="title">{{ title }}</h2>
    <p v-if="description">{{ description }}</p>
    <div v-if="actionText" class="empty-action">
      <BaseButton :to="to" variant="ghost">{{ actionText }}<Icon name="arrow-right" :size="14" /></BaseButton>
    </div>
  </div>
</template>
<style scoped>
.empty { text-align: center; padding: 36px 0; color: var(--text-faint); font-size: 13px; }
.empty .empty-ico { font-size: 30px; margin-bottom: 8px; opacity: .7; }
.empty .empty-ico .ico { color: var(--text-faint); }
.empty h2 { font-size: 20px; margin: 0 0 8px; color: var(--text); }
.empty p { margin: 0 auto; max-width: 420px; color: var(--text-muted); line-height: 1.7; }
.empty .empty-action { margin-top: 18px; }
</style>
