<script setup>
import { computed } from 'vue';
import StatCard from '../base/StatCard.vue';
import TrendChart from '../chart/TrendChart.vue';
const props = defineProps({ week: Object, trend: Array, weakKps: Array });
const completed = computed(() => props.week?.completed_tasks || 0);
const avgAccuracy = computed(() => {
  const a = (props.trend || []).filter((d) => d.accuracy != null);
  return a.length ? Math.round(a.reduce((s, d) => s + d.accuracy, 0) / a.length * 100) + '%' : '—';
});
const answered = computed(() => (props.trend || []).reduce((s, d) => s + (d.answered || 0), 0));
const weak = computed(() => (props.weakKps || []).slice(0, 3));
</script>
<template>
  <section class="panel week-review">
    <div class="section-heading"><div><p class="eyebrow">WEEKLY REVIEW</p><h2>本周回顾</h2></div></div>
    <div class="week-grid">
      <div class="week-stats">
        <div class="stat-grid">
          <StatCard label="本周完成" :value="completed" unit="项任务" />
          <StatCard label="近14天正确率" :value="avgAccuracy" />
          <StatCard label="答题量" :value="answered" unit="题" />
        </div>
        <div class="week-trend">
          <p class="week-trend-label">正确率趋势 · 近 14 天</p>
          <TrendChart :data="trend || []" height="220px" />
        </div>
      </div>
      <div class="week-summary">
        <p class="eyebrow">本周小结</p>
        <p class="week-action">{{ week?.action || '暂无本周行动建议。先完成今日任务，再进行一次诊断校准基线。' }}</p>
        <template v-if="weak.length">
          <p class="eyebrow" style="margin-top:20px">待加强</p>
          <div v-for="k in weak" :key="k.id ?? k.name" class="weak-item">
            <span class="weak-name">{{ k.name }}</span>
            <span class="num muted weak-acc">{{ Math.round((k.accuracy ?? 0) * 100) }}%</span>
          </div>
        </template>
        <router-link class="text-link" to="/insights" style="display:inline-block;margin-top:18px">查看完整能力画像 →</router-link>
      </div>
    </div>
  </section>
</template>
<style scoped>
.week-grid { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(260px, .55fr); gap: 22px; }
.week-stats { display: grid; gap: 16px; }
.week-trend-label { margin: 0 0 8px; color: var(--text-muted); font-size: 12px; }
.week-summary { padding-left: 22px; border-left: 1px solid var(--border); }
.week-action { margin: 8px 0 0; color: var(--text-muted); font-size: 13px; line-height: 1.8; }
.weak-item { display: flex; justify-content: space-between; gap: 12px; padding: 8px 0; border-top: 1px solid var(--border); font-size: 12px; }
.weak-name { color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.weak-acc { font-variant-numeric: tabular-nums; }
@media (max-width: 980px) { .week-grid { grid-template-columns: 1fr; } .week-summary { padding-left: 0; border-left: 0; } }
</style>
