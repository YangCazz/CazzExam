<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import * as echarts from 'echarts';
const props = defineProps({ option: Object, height: { type: String, default: '280px' } });
const el = ref(null);
let chart = null;
function resize() { chart && chart.resize(); }
onMounted(() => {
  chart = echarts.init(el.value);
  chart.setOption(props.option);
  window.addEventListener('resize', resize);
});
onBeforeUnmount(() => { window.removeEventListener('resize', resize); chart && chart.dispose(); chart = null; });
watch(() => props.option, (o) => { if (o && chart) chart.setOption(o, true); }, { deep: true });
</script>
<template>
  <div ref="el" :style="{ height, width: '100%' }"></div>
</template>
