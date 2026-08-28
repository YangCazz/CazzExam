<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import * as echarts from 'echarts';
import { http } from '../api/client';
const overview = ref(null);
const elTrend = ref(null);
const elPie = ref(null);
const elBar = ref(null);
const err = ref('');
let charts = [];

const DARK_TOOLTIP = { backgroundColor: 'rgba(13, 18, 32, 0.95)', borderColor: '#2c3a5c', textStyle: { color: '#e7edf8' } };
function init(dom) { const c = echarts.init(dom); charts.push(c); return c; }

function renderTrend(data) {
  const c = init(elTrend.value);
  c.setOption({
    tooltip: { trigger: 'axis', ...DARK_TOOLTIP },
    legend: { data: ['答题数', '正确率'], textStyle: { color: '#8b9ab9' } },
    grid: { left: 50, right: 50 },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)), axisLabel: { color: '#8b9ab9' } },
    yAxis: [
      { type: 'value', name: '答题数', axisLabel: { color: '#8b9ab9' } },
      { type: 'value', name: '正确率', max: 1, axisLabel: { color: '#8b9ab9', formatter: v => (v * 100) + '%' } },
    ],
    series: [
      { name: '答题数', type: 'bar', data: data.map(d => d.answered), itemStyle: { color: '#5b8cff' } },
      { name: '正确率', type: 'line', yAxisIndex: 1, data: data.map(d => d.accuracy ?? null), smooth: true, itemStyle: { color: '#34d399' } },
    ],
  });
}

function renderPie(data) {
  const c = init(elPie.value);
  c.setOption({
    tooltip: { trigger: 'item', ...DARK_TOOLTIP },
    series: [{
      type: 'pie', radius: '60%',
      data: data.map(d => ({ name: d.error_type, value: d.count })),
      label: { color: '#e7edf8' },
      itemStyle: { borderColor: '#121a2c', borderWidth: 2 },
    }],
  });
}

function renderBar(kps) {
  const c = init(elBar.value);
  const weak = kps.filter(k => k.accuracy != null).sort((a, b) => a.accuracy - b.accuracy).slice(0, 10);
  c.setOption({
    tooltip: { trigger: 'axis', ...DARK_TOOLTIP },
    grid: { left: 140, right: 40 },
    xAxis: { type: 'value', max: 1, axisLabel: { color: '#8b9ab9', formatter: v => (v * 100) + '%' } },
    yAxis: { type: 'category', data: weak.map(k => k.name).reverse(), axisLabel: { color: '#8b9ab9' } },
    series: [{
      type: 'bar',
      data: weak.map(k => k.accuracy).reverse(),
      itemStyle: { color: p => p.value < 0.4 ? '#f87171' : (p.value < 0.7 ? '#fbbf24' : '#34d399') },
    }],
  });
}

onMounted(async () => {
  try {
    const [ov, tr, ed, ks] = await Promise.all([
      http.get('/stats/overview'), http.get('/stats/trend'),
      http.get('/stats/error-dist'), http.get('/stats/knowledge'),
    ]);
    overview.value = ov;
    renderTrend(tr); renderPie(ed); renderBar(ks);
  } catch (e) { err.value = e.message; }
});
onUnmounted(() => { charts.forEach(c => c.dispose()); charts = []; });
</script>
<template>
  <div class="card">
    <h2>统计画像</h2>
    <p v-if="err" class="badge err">{{ err }}</p>
    <p v-else-if="overview" class="muted">
      题目 {{ overview.total_questions }} · 作答 {{ overview.total_attempts }} 次 ·
      累计答题 {{ overview.total_answers }} · 正确率
      {{ overview.accuracy == null ? '—' : (overview.accuracy * 100).toFixed(1) + '%' }}
    </p>
  </div>
  <div class="card">
    <h2>近 14 天学习趋势</h2>
    <div ref="elTrend" style="height:280px"></div>
  </div>
  <div class="row" style="align-items:stretch">
    <div class="card" style="flex:1;min-width:280px">
      <h2>错因分布</h2>
      <div ref="elPie" style="height:260px"></div>
    </div>
    <div class="card" style="flex:2;min-width:380px">
      <h2>薄弱知识点 Top10（得分率最低）</h2>
      <div ref="elBar" style="height:280px"></div>
    </div>
  </div>
</template>