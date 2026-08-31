<script setup>
import { computed } from 'vue';
const props = defineProps({
  label: String, value: [String, Number], unit: String, caption: String,
  delta: String,   // 如 '+2h'，自动取色 up/down
  tone: String,    // accent | ok | warn | err
  icon: String,
});
const deltaDir = computed(() => {
  if (!props.delta) return '';
  return props.delta[0] === '+' ? 'up' : props.delta[0] === '-' ? 'down' : 'flat';
});
</script>
<template>
  <div class="stat-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}<small v-if="unit"> {{ unit }}</small></div>
    <div v-if="caption" class="stat-caption">{{ caption }}</div>
    <div v-if="delta" class="stat-delta" :class="deltaDir">{{ delta }}</div>
  </div>
</template>
<style scoped>
.stat-card { position: relative; }
.stat-caption { font-size: 11px; color: var(--text-faint); margin-top: 4px; }
.stat-delta { font-size: 11px; margin-top: 4px; font-variant-numeric: tabular-nums; }
.stat-delta.up { color: var(--status-success); }
.stat-delta.down { color: var(--risk-high); }
.stat-delta.flat { color: var(--text-muted); }
</style>
