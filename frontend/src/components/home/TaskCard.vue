<script setup>
import { computed } from 'vue';
import BaseButton from '../base/BaseButton.vue';
import Icon from '../Icon.vue';
const props = defineProps({
  index: Number, type: { type: String, default: 'practice' },
  title: String, reason: String, hint: String, minutes: Number,
  status: { type: String, default: 'todo' }, loading: Boolean, disabled: Boolean,
  onStart: Function,
});
const meta = computed(() => ({
  review:   { label: '复习队列', tone: 'tone-recall',    icon: 'wrong' },
  case:     { label: '案例分析', tone: 'tone-case',      icon: 'case' },
  material: { label: '论文素材', tone: 'tone-material',  icon: 'essay' },
  practice: { label: '针对训练', tone: 'tone-practice',  icon: 'target' },
}[props.type] || { label: '学习任务', tone: 'tone-practice', icon: 'target' }));
const num = computed(() => String(props.index + 1).padStart(2, '0'));
</script>
<template>
  <article class="task-card" :class="meta.tone">
    <span class="task-index">{{ num }}</span>
    <div class="task-body">
      <span class="type-pill" :class="meta.tone">{{ meta.label }}</span>
      <h3>{{ title }}</h3>
      <p class="task-reason"><b>依据</b> {{ reason }}</p>
      <div class="task-meta"><span v-if="hint">{{ hint }}</span><span class="task-minutes">{{ minutes }} 分钟</span></div>
    </div>
    <BaseButton :loading="loading" :disabled="disabled" @click="onStart && onStart()">
      {{ status === 'in_progress' ? '继续' : '开始' }}<Icon name="arrow-right" :size="14" />
    </BaseButton>
  </article>
</template>
<style scoped>
.task-card { display: flex; gap: 16px; align-items: center; padding: 16px 0; border-top: 1px solid var(--border); border-left: 2px solid transparent; padding-left: 12px; border-radius: 4px; transition: background .2s var(--ease); }
.task-card:hover { background: var(--surface); }
.task-card.tone-recall { border-left-color: var(--kpi-recall); }
.task-card.tone-case { border-left-color: var(--kpi-case); }
.task-card.tone-material { border-left-color: var(--kpi-material); }
.task-card.tone-practice { border-left-color: var(--kpi-practice); }
.task-index { color: var(--text-faint); font: 700 15px var(--mono); }
.task-body { flex: 1; min-width: 0; }
.type-pill.tone-recall { background: var(--warn-dim); color: var(--kpi-recall); }
.type-pill.tone-case { background: var(--action-secondary-soft); color: var(--action-secondary); }
.type-pill.tone-material { background: var(--ok-dim); color: var(--status-success); }
.type-pill.tone-practice { background: var(--action-soft); color: var(--action-primary-hover); }
.task-body h3 { margin: 7px 0 4px; font-size: 15px; color: var(--text); }
.task-reason { margin: 0; color: var(--text-muted); font-size: 12px; line-height: 1.6; }
.task-reason b { color: var(--text-faint); font-weight: 600; }
.task-meta { display: flex; gap: 12px; margin-top: 5px; color: var(--text-faint); font-size: 12px; }
.task-minutes { white-space: nowrap; }
</style>
