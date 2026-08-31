<script setup>
import { computed } from 'vue';
const props = defineProps({
  value: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  tone: { type: String, default: 'primary' },  // primary | success | warning | danger | neutral
  showLabel: Boolean, label: String,
  minWidth: String, flex: Boolean,
});
const pct = computed(() => Math.max(0, Math.min(100, (props.value / props.max) * 100)));
</script>
<template>
  <div class="ui-progress-wrap" :style="flex ? { flex: 1 } : {}">
    <div class="ui-progress" :class="'tone-' + tone" :style="minWidth ? { minWidth } : {}">
      <i :style="{ width: pct + '%' }"></i>
    </div>
    <span v-if="showLabel" class="ui-progress-label">{{ label || Math.round(pct) + '%' }}</span>
  </div>
</template>
<style scoped>
.ui-progress-wrap { display: inline-flex; align-items: center; gap: 8px; min-width: 70px; }
.ui-progress { height: 6px; border-radius: 3px; background: var(--surface); overflow: hidden; flex: 1; }
.ui-progress > i { display: block; height: 100%; border-radius: 3px; background: var(--action-primary); transition: width .3s var(--ease); }
.tone-success > i { background: var(--status-success); }
.tone-warning > i { background: var(--status-warning); }
.tone-danger > i { background: var(--risk-high); }
.tone-neutral > i { background: var(--text-faint); }
.ui-progress-label { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
</style>
