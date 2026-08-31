<script setup>
import { onMounted, onUnmounted, ref, computed, watch } from 'vue';
import * as echarts from 'echarts';
import { http } from '../api/client';
import { chartTheme } from '../utils/chartTheme';
import BaseButton from '../components/base/BaseButton.vue';
const t = chartTheme();
const el = ref(null);
const raw = ref({ nodes: [], links: [] });
const info = ref(null);
const detail = ref(null);
const search = ref('');
const showTypes = ref({ related: true, prerequisite: true, contains: true, conflicts: true, backbone: true });
const relNames = { related: '相关', prerequisite: '前置', contains: '包含', conflicts: '冲突', backbone: '主线' };
const fixedIds = new Set();
const nodePositions = new Map();   // name -> [x, y]（最终为屏幕坐标）
const matchedCount = ref(0);
const visibleLinkCount = computed(() => buildLinks().length);
const ready = ref(false);
let pollStart = 0;
let freezeAttempts = 0;
let chart = null;
let pollTimer = null;
let lastBox = null;
let stableCount = 0;

function buildNodes() {
  const kw = search.value.trim();
  const matched = kw ? raw.value.nodes.filter(n => n.name.includes(kw)).map(n => n.id) : null;
  matchedCount.value = matched ? matched.length : raw.value.nodes.length;
  return raw.value.nodes.map(n => {
    const pos = nodePositions.get(n.name);
    const isMatch = !matched || matched.includes(n.id);
    return {
      id: n.id, name: n.name,
      x: pos ? pos[0] : undefined,
      y: pos ? pos[1] : undefined,
      symbolSize: 18 + Math.min(n.mastery || 0, 100) / 10,
      fixed: (fixedIds.has(n.id) || pos) ? true : undefined,
      itemStyle: { color: t.nodeColor(n.mastery), opacity: isMatch ? 1 : 0.12 },
      label: { show: isMatch, fontSize: 11, color: matched && matched.includes(n.id) ? '#ffffff' : t.label },
      emphasis: { itemStyle: { borderColor: '#fff', borderWidth: 1 } },
    };
  });
}
function buildLinks() {
  const typeSet = new Set(Object.keys(showTypes.value).filter(k => showTypes.value[k]));
  return raw.value.links.filter(l => typeSet.has(l.type)).map(l => ({
    source: l.source, target: l.target,
    label: { show: true, formatter: relNames[l.type] || l.type, fontSize: 9, color: t.textMuted },
  }));
}
function buildOption(extra = {}) {
  return {
    textStyle: { color: t.label },
    tooltip: {
      formatter: (p) => p.dataType === 'node' ? p.data.name : '',
      confine: true, ...t.tooltip,
    },
    series: [{
      type: 'graph',
      layout: nodePositions.size ? 'none' : 'force',
      roam: true,
      draggable: true,
      scaleLimit: { min: 0.25, max: 4 },
      label: { show: true, fontSize: 11 },
      data: buildNodes(),
      links: buildLinks(),
      lineStyle: { color: t.line, width: 1, opacity: 0.55 },
      force: { repulsion: 320, edgeLength: 100, gravity: 0.1 },
      emphasis: { focus: 'adjacency', lineStyle: { width: 2, opacity: 1 } },
      ...extra,
    }],
  };
}
function render() {
  if (!chart) return;
  chart.setOption(buildOption());
  if (nodePositions.size === 0 && !ready.value) scheduleFreeze();
}
function readLayoutPts() {
  const model = chart.getModel().getSeriesByIndex(0);
  const data = model ? model.getData() : null;
  if (!data) return null;
  const pts = [];
  data.each((idx) => {
    const name = data.getName(idx);
    const layout = data.getItemLayout(idx);
    let x, y;
    if (Array.isArray(layout)) { x = layout[0]; y = layout[1]; }
    else if (layout) { x = layout.x; y = layout.y; }
    if (typeof x === 'number' && typeof y === 'number' && name) {
      pts.push({ name, x, y });
    }
  });
  return pts.length >= 2 ? pts : null;
}
// 轮询等待 force 收敛（带超时兜底：后台/节流环境下动画不推进也能冻结）
function pollLayout() {
  if (!chart) return;
  if (Date.now() - pollStart > 6000) { freezeFit(); return; }
  const pts = readLayoutPts();
  if (!pts) { pollTimer = setTimeout(pollLayout, 500); return; }
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const box = { w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
  if (lastBox && box.w > 10) {
    const dx = Math.abs(box.w - lastBox.w) / lastBox.w;
    const dy = Math.abs(box.h - lastBox.h) / lastBox.h;
    if (dx < 0.015 && dy < 0.015) stableCount++;
    else stableCount = 0;
    if (stableCount >= 2) { freezeFit(); return; }
  }
  lastBox = box;
  pollTimer = setTimeout(pollLayout, 500);
}
function scheduleFreeze() {
  if (pollTimer) clearTimeout(pollTimer);
  lastBox = null; stableCount = 0;
  pollStart = Date.now();
  pollTimer = setTimeout(pollLayout, 500);
}
// 冻结：把节点坐标线性重映射到画布屏幕坐标（舒适区填满，天然在窗口内）
function freezeFit() {
  if (!chart) return;
  freezeAttempts++;
  try {
  const pts = readLayoutPts();
  if (!pts) {
    // 读不到坐标：最多重试 5 次后放弃（保持 force 布局直接显示，绝不空白）
    if (freezeAttempts < 5) { pollTimer = setTimeout(freezeFit, 500); return; }
    ready.value = true;
    return;
  }
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const w = (maxX - minX) || 1, h = (maxY - minY) || 1;
  const W = chart.getWidth(), H = chart.getHeight();
  const pad = 100;
  const scale = Math.min((W - pad * 2) / w, (H - pad * 2) / h, 1.6, 1);
  const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
  for (const p of pts) {
    const nx = (p.x - cx) * scale + W / 2;
    const ny = (p.y - cy) * scale + H / 2;
    nodePositions.set(p.name, [nx, ny]);
  }
  chart.setOption(buildOption({ layout: 'none' }));
  ready.value = true;
  } catch (e) {
    console.error('[graph] freeze error', e);
    ready.value = true;
  }
}
function bindEvents() {
  chart.on('click', (p) => {
    if (p.dataType === 'node') selectNode(p.data);
    else { info.value = null; detail.value = null; }
  });
  chart.on('dragend', (p) => {
    if (p.dataType === 'node' && p.data) {
      fixedIds.add(p.data.id);
      try {
        const model = chart.getModel().getSeriesByIndex(0);
        const data = model ? model.getData() : null;
        if (data) {
          data.each((idx) => {
            if (data.getName(idx) === p.data.name) {
              const l = data.getItemLayout(idx);
              if (Array.isArray(l)) nodePositions.set(p.data.name, [l[0], l[1]]);
            }
          });
        }
      } catch (e) { /* ignore */ }
    }
  });
}
async function selectNode(node) {
  info.value = { id: node.id, name: node.name, mastery: node.mastery || 0 };
  detail.value = null;
  try { detail.value = await http.get('/knowledge/points/' + node.id); }
  catch (e) { detail.value = null; }
}
function resetView() {
  if (!chart) return;
  chart.dispose();
  chart = echarts.init(el.value);
  bindEvents();
  render();
}
function initChart() {
  chart = echarts.init(el.value);
  bindEvents();
  render();
}
onMounted(async () => {
  raw.value = await http.get('/knowledge/graph');
  initChart();
  window.addEventListener('resize', () => chart && chart.resize());
});
watch(showTypes, render, { deep: true });
watch(search, render);
onUnmounted(() => { if (pollTimer) clearTimeout(pollTimer); if (chart) chart.dispose(); });
</script>
<template>
  <div class="card">
    <div class="toolbar">
      <input v-model="search" placeholder="搜索知识点…" class="w210" />
      <span class="spacer"></span>
      <label v-for="(label, key) in relNames" :key="key" class="rel-filter">
        <input type="checkbox" v-model="showTypes[key]" /> {{ label }}
      </label>
      <span class="badge accent">{{ matchedCount }} 节点 · {{ visibleLinkCount }} 边</span>
      <BaseButton size="sm" variant="ghost" @click="resetView">重置视图</BaseButton>
    </div>
    <div class="list-panel graph-panel">
      <div class="graph-wrap" :class="{ ready }">
        <div ref="el" class="graph-canvas"></div>
      </div>
      <div v-if="info" class="graph-side">
        <div class="row between">
          <b class="side-title">{{ info.name }}</b>
          <BaseButton size="sm" variant="ghost" icon="x-circle" aria-label="关闭" @click="info = null; detail = null"></BaseButton>
        </div>
        <div class="row side-mastery">
          <span class="muted muted-sm">掌握度</span>
          <span class="progress side-progress" :class="info.mastery < 40 ? 'err' : (info.mastery < 70 ? 'warn' : '')">
            <i :style="{ width: info.mastery + '%' }"></i>
          </span>
          <b class="num side-pct">{{ Math.round(info.mastery) }}%</b>
        </div>
        <p class="muted side-desc" v-if="detail && detail.description">{{ detail.description }}</p>
        <div class="row side-tags" v-if="detail">
          <span class="tag">关联题 {{ detail.questions.length }}</span>
          <span class="tag">子节点 {{ detail.children.length }}</span>
        </div>
        <div class="row">
          <BaseButton :to="'/practice?kp=' + info.id" size="sm" icon="target">练习本知识点</BaseButton>
          <BaseButton :to="'/knowledge'" size="sm" variant="ghost" icon="book">知识点库</BaseButton>
        </div>
      </div>
    </div>
    <p class="muted graph-hint">
      拖拽节点可固定位置 · 滚轮缩放 · 空白处拖拽平移画布 · 悬停高亮关联 · 点击节点查看详情
    </p>
  </div>
</template>

<style scoped>
/* 原内联样式静默化：布局/宽度一律 scoped 类；掌握度进度等动态宽度保留 :style 绑定 */
.w210 { width: 210px; }
.rel-filter { font-size: 12px; color: var(--text-muted); cursor: pointer; display: inline-flex; align-items: center; gap: 4px; }
.graph-panel { position: relative; padding: 0; }
.graph-wrap { height: 620px; width: 100%; }
.graph-canvas { height: 620px; width: 100%; }
.between { justify-content: space-between; }
.side-title { font-size: 14px; }
.side-mastery { margin: 10px 0; }
.muted-sm { font-size: 12px; }
.side-progress { flex: 1; }
.side-pct { font-size: 13px; }
.side-desc { font-size: 12px; margin: 8px 0; line-height: 1.7; }
.side-tags { margin: 8px 0; }
.graph-hint { padding: 10px 14px 2px; font-size: 12px; }
</style>
