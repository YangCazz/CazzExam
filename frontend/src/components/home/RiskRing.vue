<script setup>
import { computed } from 'vue';
const props = defineProps({
  name: String,
  value: { type: Number, default: null },   // 0–1 正确率；null=数据不足
  level: String, answered: Number,
});
const pct = computed(() => (props.value == null ? 0 : Math.round(props.value * 100)));
const color = computed(() => {
  if (props.value == null) return 'var(--text-faint)';
  if (props.value < 0.5) return 'var(--risk-high)';
  if (props.value < 0.7) return 'var(--status-warning)';
  return 'var(--status-success)';
});
const ring = 2 * Math.PI * 42;
</script>
<template>
  <div class="risk-ring">
    <div class="ring-box">
      <svg viewBox="0 0 100 100" class="ring-svg">
        <circle cx="50" cy="50" r="42" fill="none" stroke="var(--surface)" stroke-width="8" />
        <circle v-if="value != null" cx="50" cy="50" r="42" fill="none"
                :stroke="color" stroke-width="8" stroke-linecap="round"
                :stroke-dasharray="`${ring}`" :stroke-dashoffset="`${ring * (1 - pct / 100)}`"
                transform="rotate(-90 50 50)" style="transition: stroke-dashoffset .6s var(--ease)" />
      </svg>
      <div class="ring-center"><b :style="{ color }">{{ value == null ? '—' : pct + '%' }}</b></div>
    </div>
    <div class="ring-meta"><span class="ring-name">{{ name }}</span><span class="ring-level">{{ value == null ? '数据不足' : level }}</span></div>
  </div>
</template>
<style scoped>
.risk-ring { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.ring-box { position: relative; width: 88px; height: 88px; }
.ring-svg { width: 100%; height: 100%; transform: rotate(0deg); }
.ring-center { position: absolute; inset: 0; display: grid; place-items: center; }
.ring-center b { font-size: 20px; font-variant-numeric: tabular-nums; }
.ring-meta { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.ring-name { font-size: 12px; color: var(--text-muted); }
.ring-level { font-size: 10.5px; color: var(--text-faint); }
</style>
