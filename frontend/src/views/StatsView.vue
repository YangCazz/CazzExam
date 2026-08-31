<script setup>
import { onMounted, ref } from 'vue';
import { http } from '../api/client';
import Card from '../components/base/Card.vue';
import SectionHeading from '../components/base/SectionHeading.vue';
import EmptyState from '../components/base/EmptyState.vue';
import ChartPanel from '../components/chart/ChartPanel.vue';
import { chartTheme } from '../utils/chartTheme';

const overview = ref(null);
const trend = ref([]);
const errorDist = ref([]);
const kps = ref([]);
const err = ref('');

onMounted(async () => {
  try {
    const [ov, tr, ed, ks] = await Promise.all([
      http.get('/stats/overview'), http.get('/stats/trend'),
      http.get('/stats/error-dist'), http.get('/stats/knowledge'),
    ]);
    overview.value = ov; trend.value = tr; errorDist.value = ed; kps.value = ks;
  } catch (e) { err.value = e.message; }
});

const weakKps = () => kps.value.filter(k => k.accuracy != null).sort((a, b) => a.accuracy - b.accuracy).slice(0, 10);

function trendOption() {
  const t = chartTheme();
  return {
    grid: { left: 50, right: 50, top: 30, bottom: 8 },
    tooltip: { trigger: 'axis', ...t.tooltip },
    legend: { top: 0, data: ['答题数', '正确率'], textStyle: { color: t.textMuted } },
    xAxis: { type: 'category', data: trend.value.map(d => d.date.slice(5)), axisLabel: { color: t.textMuted, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: '答题数', axisLabel: { color: t.textMuted, fontSize: 10 } },
      { type: 'value', name: '正确率', max: 1, axisLabel: { color: t.textMuted, fontSize: 10, formatter: v => (v * 100) + '%' }, splitLine: { show: false } },
    ],
    series: [
      { name: '答题数', type: 'bar', data: trend.value.map(d => d.answered), itemStyle: { color: t.series.primary, borderRadius: [3, 3, 0, 0] } },
      { name: '正确率', type: 'line', yAxisIndex: 1, data: trend.value.map(d => d.accuracy ?? null), smooth: true, connectNulls: true, itemStyle: { color: t.series.success }, lineStyle: { color: t.series.success, width: 2 } },
    ],
  };
}
function pieOption() {
  const t = chartTheme();
  return {
    tooltip: { trigger: 'item', ...t.tooltip },
    series: [{
      type: 'pie', radius: ['42%', '68%'],
      data: errorDist.value.map(d => ({ name: d.error_type, value: d.count })),
      label: { color: t.textMuted },
      itemStyle: { borderColor: t.surface, borderWidth: 2 },
    }],
  };
}
function barOption() {
  const t = chartTheme();
  const weak = weakKps();
  return {
    grid: { left: 140, right: 40 },
    tooltip: { trigger: 'axis', ...t.tooltip },
    xAxis: { type: 'value', max: 1, axisLabel: { color: t.textMuted, formatter: v => (v * 100) + '%' } },
    yAxis: { type: 'category', data: weak.map(k => k.name).reverse(), axisLabel: { color: t.textMuted, fontSize: 10 } },
    series: [{
      type: 'bar',
      data: weak.map(k => k.accuracy).reverse(),
      itemStyle: { color: p => t.statusColor(p.value) },
    }],
  };
}
</script>
<template>
  <div v-if="err" class="notice error">统计服务暂不可用：{{ err }}</div>
  <template v-else-if="overview">
    <Card class="overview-card">
      <SectionHeading eyebrow="INSIGHTS" title="能力画像" subtitle="以证据识别下一轮训练重点" />
      <p class="overview-line muted">
        题目 {{ overview.total_questions }} · 作答 {{ overview.total_attempts }} 次 ·
        累计答题 {{ overview.total_answers }} · 总体正确率
        <b>{{ overview.accuracy == null ? '—' : (overview.accuracy * 100).toFixed(1) + '%' }}</b>
      </p>
    </Card>

    <Card>
      <SectionHeading eyebrow="TREND" title="近 14 天学习趋势" />
      <ChartPanel v-if="trend.length" :option="trendOption()" height="280px" />
      <EmptyState v-else icon="📈" title="暂无答题数据" description="完成一些练习后，这里会呈现你的正确率变化。" />
    </Card>

    <div class="row" style="align-items:stretch">
      <Card class="stats-col" style="flex:1;min-width:280px">
        <SectionHeading eyebrow="ERRORS" title="错因分布" />
        <ChartPanel v-if="errorDist.length" :option="pieOption()" height="260px" />
        <EmptyState v-else icon="🧩" title="暂无错因数据" />
      </Card>
      <Card class="stats-col" style="flex:2;min-width:380px">
        <SectionHeading eyebrow="WEAKEST" title="薄弱知识点 Top10" subtitle="得分率最低" />
        <ChartPanel v-if="weakKps().length" :option="barOption()" height="280px" />
        <EmptyState v-else icon="🎯" title="暂无知识点得分数据" />
      </Card>
    </div>
  </template>
  <Card v-else class="loading-state">正在汇总学习证据…</Card>
</template>
<style scoped>
.overview-line { margin: 0; font-size: 13px; line-height: 1.8; }
.overview-line b { color: var(--text); }
</style>
