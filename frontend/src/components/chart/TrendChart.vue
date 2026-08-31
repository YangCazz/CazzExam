<script setup>
import { computed } from 'vue';
import ChartPanel from './ChartPanel.vue';
import { chartTheme } from '../../utils/chartTheme';
const props = defineProps({
  data: Array,                                 // [{ date, answered, correct, accuracy|null }]
  height: { type: String, default: '240px' },
});
const option = computed(() => {
  const t = chartTheme();
  const days = props.data || [];
  return {
    grid: { left: 6, right: 14, top: 24, bottom: 6, containLabel: true },
    tooltip: { trigger: 'axis', ...t.tooltip, valueFormatter: (v) => (v == null ? '无数据' : v + '%') },
    xAxis: {
      type: 'category', boundaryGap: false,
      data: days.map((d) => d.date.slice(5)),
      axisLine: { lineStyle: { color: t.border } },
      axisTick: { show: false },
      axisLabel: { color: t.textMuted, fontSize: 10 },
    },
    yAxis: {
      type: 'value', max: 100,
      axisLabel: { color: t.textMuted, formatter: '{value}%', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(148,163,199,.07)' } },
    },
    series: [{
      name: '正确率', type: 'line', smooth: true, symbol: 'circle', symbolSize: 5,
      data: days.map((d) => (d.accuracy == null ? null : Math.round(d.accuracy * 100))),
      connectNulls: true,
      lineStyle: { color: t.series.primary, width: 2 },
      itemStyle: { color: t.series.primary },
      areaStyle: { color: 'rgba(91,140,255,.08)' },
    }],
  };
});
</script>
<template>
  <ChartPanel :option="option" :height="height" />
</template>
