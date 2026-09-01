<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { http } from '../api/client';
import BaseButton from '../components/base/BaseButton.vue';

const canvas = ref(null); const wrap = ref(null);
const search = ref(''); const info = ref(null); const detail = ref(null); const hover = ref(null);
const showTypes = ref({ related: true, prerequisite: true, contains: true, conflicts: true, backbone: true });
const relNames = { related: '相关', prerequisite: '前置', contains: '包含', conflicts: '冲突', backbone: '主线' };
const relColors = { related: '#637da8', prerequisite: '#c9a13d', contains: '#5b8cff', conflicts: '#cf6a68', backbone: '#7a6bb0' };
const domains = {
  1: { title: '计算机系统基础', short: '系统基础', x: .18, y: .29, color: '#4b86d1' },
  2: { title: '软件工程与项目管理', short: '工程与管理', x: .19, y: .74, color: '#5f78ba' },
  3: { title: '系统架构设计（主线）', short: '架构设计核心', x: .52, y: .50, color: '#7257b7' },
  4: { title: '数学与经济管理', short: '数学与管理', x: .83, y: .22, color: '#4d9a9a' },
  5: { title: '信息安全与可靠性', short: '安全与可靠性', x: .83, y: .54, color: '#c37b5c' },
  6: { title: '专业英语', short: '专业英语', x: .83, y: .80, color: '#5f8f72' },
};
const graph = { nodes: [], links: [], width: 1, height: 1, panX: 0, panY: 0, scale: 1, alpha: .3, launchFrames: 48, raf: 0, dragged: null, panning: false, last: null, moved: false };
const nodeTotal = ref(0); const linkTotal = ref(0);
let ctx; let resizeObserver; let longPressTimer;

const matchedCount = computed(() => { search.value; return nodeTotal.value ? graph.nodes.filter(n => n.name.includes(search.value.trim())).length : 0; });
const visibleLinkCount = computed(() => { linkTotal.value; Object.values(showTypes.value); return graph.links.filter(l => showTypes.value[l.type]).length; });
const filteredLinks = () => graph.links.filter(l => showTypes.value[l.type]);
function nodeColor(node) { return domains[node.domain]?.color || '#4b86d1'; }
function rgb(hex) { const n = Number.parseInt(hex.slice(1), 16); return { r: n >> 16, g: (n >> 8) & 255, b: n & 255 }; }
function wrapLabel(name) { const chunks = []; for (let i = 0; i < name.length; i += 8) chunks.push(name.slice(i, i + 8)); return chunks; }
function nodeDomain(node, treeById) {
  let current = node; const seen = new Set();
  while (current?.parent_id && !seen.has(current.id)) { seen.add(current.id); current = treeById.get(current.parent_id); }
  return current?.id || 3;
}
function assignDomainTargets() {
  const groups = new Map(); graph.nodes.forEach(n => { const items = groups.get(n.domain) || []; items.push(n); groups.set(n.domain, items); });
  groups.forEach((items, domainId) => {
    const zone = domains[domainId] || domains[3]; const centerX = graph.width * zone.x; const centerY = graph.height * zone.y; const core = Number(domainId) === 3;
    items.sort((a, b) => String(a.code || '').split('.').length - String(b.code || '').split('.').length || String(a.code || '').localeCompare(String(b.code || '')));
    const leaves = items.filter(n => n.parent_id);
    items.forEach(n => { n.targetX = centerX; n.targetY = centerY; });
    leaves.forEach((n, index) => {
      const ring = index < 8 ? 1 : 2; const offset = ring === 1 ? 0 : 8; const count = ring === 1 ? Math.min(8, leaves.length) : Math.max(1, leaves.length - 8);
      const radius = (core ? 66 : 54) * ring; const angle = -Math.PI / 2 + (index - offset) / count * Math.PI * 2 + Number(domainId) * .19;
      n.targetX = centerX + Math.cos(angle) * radius; n.targetY = centerY + Math.sin(angle) * radius;
    });
  });
}
function initNodes(data, tree = []) {
  const treeById = new Map(tree.map(n => [n.id, n]));
  const rawNodes = data.nodes.map(n => ({ ...n, ...treeById.get(n.id) }));
  const rawDegree = new Map(rawNodes.map(n => [n.id, 0])); data.links.forEach(l => { rawDegree.set(l.source, (rawDegree.get(l.source) || 0) + 1); rawDegree.set(l.target, (rawDegree.get(l.target) || 0) + 1); });
  const maxDegree = Math.max(1, ...rawDegree.values());
  graph.nodes = rawNodes.map((n, index) => {
    const domain = nodeDomain(n, treeById); const degree = rawDegree.get(n.id) || 0;
    const hierarchy = !n.parent_id ? (n.id === 3 ? 1 : .68) : String(n.code || '').split('.').length === 2 ? .38 : .12;
    const priority = Math.min(1, .44 * hierarchy + .34 * (1 - Math.min(100, n.mastery || 0) / 100) + .22 * (degree / maxDegree));
    const r = Math.round(9 + priority * 19); const label = wrapLabel(n.name); const footprint = r + 9 + label.length * 6;
    return { ...n, domain, degree, priority, label, footprint, x: graph.width / 2 + (Math.random() - .5) * graph.width * .7, y: graph.height / 2 + (Math.random() - .5) * graph.height * .7, vx: 0, vy: 0, r, dR: r, tR: r, dA: 1, tA: 1, order: index };
  });
  const byId = new Map(graph.nodes.map(n => [n.id, n]));
  graph.links = data.links.map(l => ({ ...l, a: byId.get(l.source), b: byId.get(l.target), dA: 1, tA: 1 })).filter(l => l.a && l.b);
  assignDomainTargets();
  nodeTotal.value = graph.nodes.length; linkTotal.value = graph.links.length;
  graph.panX = 0; graph.panY = 0; graph.scale = 1; graph.alpha = .3; graph.launchFrames = 48;
}
function resize() {
  if (!canvas.value || !wrap.value) return;
  const box = wrap.value.getBoundingClientRect(); const ratio = window.devicePixelRatio || 1;
  graph.width = Math.max(280, box.width); graph.height = Math.max(360, box.height);
  canvas.value.width = graph.width * ratio; canvas.value.height = graph.height * ratio;
  canvas.value.style.width = `${graph.width}px`; canvas.value.style.height = `${graph.height}px`;
  ctx = canvas.value.getContext('2d'); ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  if (!graph.nodes.length) return;
  graph.nodes.forEach((n, i) => { if (!Number.isFinite(n.x)) { n.x = graph.width / 2 + (i % 5 - 2) * 90; n.y = graph.height / 2 + (i % 4 - 2) * 75; } });
  assignDomainTargets();
}
function physics() {
  const nodes = graph.nodes; const links = filteredLinks(); const a = graph.alpha;
  if (a > .002 && !graph.dragged) {
    const launching = graph.launchFrames-- > 0; const pull = launching ? .014 : .011;
    nodes.forEach(n => { n.vx *= .55; n.vy *= .55; n.vx += ((n.targetX ?? graph.width / 2) - n.x) * pull * a; n.vy += ((n.targetY ?? graph.height / 2) - n.y) * pull * a; });
    for (let iteration = 0; iteration < 3; iteration++) for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
      const p = nodes[i], q = nodes[j]; let dx = q.x - p.x, dy = q.y - p.y; const distance = Math.hypot(dx, dy) || .01; const minimum = p.footprint + q.footprint + 3;
      if (distance < minimum) { const force = (minimum - distance) * .4 * a; dx /= distance; dy /= distance; p.vx -= dx * force; p.vy -= dy * force; q.vx += dx * force; q.vy += dy * force; }
    }
    links.forEach(l => { const dx = l.b.x - l.a.x, dy = l.b.y - l.a.y; const distance = Math.hypot(dx, dy) || .01; const ideal = l.a.footprint + l.b.footprint + (l.a.domain === l.b.domain ? 12 : 42); const force = (distance - ideal) * .0025 * a; l.a.vx += dx / distance * force; l.a.vy += dy / distance * force; l.b.vx -= dx / distance * force; l.b.vy -= dy / distance * force; });
    let maxSpeed = 0; nodes.forEach(n => { n.x = Math.max(n.r, Math.min(graph.width - n.r, n.x + n.vx)); n.y = Math.max(n.r, Math.min(graph.height - n.r, n.y + n.vy)); maxSpeed = Math.max(maxSpeed, Math.abs(n.vx), Math.abs(n.vy)); });
    if (maxSpeed < .12) graph.alpha += (.002 - graph.alpha) * .005;
  }
}
function drawDomains() {
  Object.entries(domains).forEach(([id, zone]) => {
    const x = graph.width * zone.x; const y = graph.height * zone.y; const core = Number(id) === 3;
    ctx.save(); ctx.globalAlpha = .12; ctx.fillStyle = zone.color; ctx.beginPath(); ctx.arc(x, y, core ? 152 : 105, 0, Math.PI * 2); ctx.fill(); ctx.globalAlpha = 1; ctx.strokeStyle = `${zone.color}55`; ctx.setLineDash([3, 5]); ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(x, y, core ? 152 : 105, 0, Math.PI * 2); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle = zone.color; ctx.globalAlpha = .72; ctx.font = '600 10px Inter, Microsoft YaHei, sans-serif'; ctx.textAlign = 'center'; ctx.fillText(zone.short, x, y - (core ? 160 : 113)); ctx.restore();
  });
}
function neighborhood(node) { if (!node) return null; const set = new Set([node]); filteredLinks().forEach(l => { if (l.a === node) set.add(l.b); if (l.b === node) set.add(l.a); }); return set; }
function setHighlight(node) {
  hover.value = node;
  const connected = neighborhood(node);
  graph.nodes.forEach(n => { const active = !node || connected.has(n); n.tR = node ? (active ? n.r * 1.15 : n.r * .78) : n.r; n.tA = active ? 1 : .15; });
  graph.links.forEach(l => { l.tA = !node || (l.a === node || l.b === node) ? 1 : .06; });
  graph.alpha = node ? .06 : .12;
}
function focusSearch() {
  const query = search.value.trim().toLowerCase(); if (!query) return setHighlight(null);
  const node = graph.nodes.find(n => n.name.toLowerCase().includes(query));
  if (!node) return;
  setHighlight(node); graph.nodes.forEach(n => { const keep = n === node || neighborhood(node).has(n); n.tA = keep ? 1 : .06; n.tR = n === node ? n.r * 1.3 : n.r * .3; }); graph.links.forEach(l => { l.tA = l.a.tA > .5 && l.b.tA > .5 ? 1 : .02; }); graph.alpha = .3;
}
function render() {
  if (!ctx) return;
  physics(); graph.nodes.forEach(n => { n.dR += (n.tR - n.dR) * .16; n.dA += (n.tA - n.dA) * .14; }); graph.links.forEach(l => { l.dA += (l.tA - l.dA) * .14; }); ctx.clearRect(0, 0, graph.width, graph.height); ctx.save(); ctx.translate(graph.panX, graph.panY); ctx.scale(graph.scale, graph.scale);
  drawDomains();
  const query = search.value.trim(); const focus = neighborhood(hover.value || info.value); const links = filteredLinks();
  links.forEach(l => { const active = !focus || l.a === hover.value || l.b === hover.value || l.a === info.value || l.b === info.value; const match = !query || (l.a.name.includes(query) && l.b.name.includes(query)); ctx.save(); ctx.globalAlpha = l.dA * (active ? (match ? .74 : .34) : .045); ctx.strokeStyle = active && focus ? '#315fba' : '#7ca4da'; ctx.lineWidth = active && focus ? 1.7 : .65; ctx.beginPath(); ctx.moveTo(l.a.x, l.a.y); ctx.lineTo(l.b.x, l.b.y); ctx.stroke(); ctx.restore(); });
  [...graph.nodes].sort((a, b) => a.dR - b.dR).forEach(n => { const matched = !query || n.name.includes(query); const active = !focus || focus.has(n); const radius = n.dR; const color = rgb(nodeColor(n)); ctx.save(); ctx.globalAlpha = n.dA * (matched && active ? 1 : (query ? .1 : .16)); const fill = ctx.createRadialGradient(n.x - radius * .28, n.y - radius * .28, 0, n.x, n.y, radius); fill.addColorStop(0, `rgb(${Math.min(255, color.r + 34)},${Math.min(255, color.g + 34)},${Math.min(255, color.b + 34)})`); fill.addColorStop(1, nodeColor(n)); ctx.fillStyle = fill; ctx.beginPath(); ctx.arc(n.x, n.y, radius, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = info.value === n ? '#f3c96b' : hover.value === n ? '#fff' : 'rgba(255,255,255,.7)'; ctx.lineWidth = info.value === n || hover.value === n ? 2.6 : 1.4; ctx.stroke(); ctx.fillStyle = '#283a55'; ctx.shadowColor = 'rgba(255,255,255,.96)'; ctx.shadowBlur = 3; ctx.font = `600 ${Math.max(9.5, Math.min(11.5, radius * .43))}px Inter, Microsoft YaHei, sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'top'; n.label.forEach((line, index) => ctx.fillText(line, n.x, n.y + radius + 5 + index * 12)); ctx.restore(); });
  ctx.restore(); graph.raf = requestAnimationFrame(render);
}
function point(event) { const rect = canvas.value.getBoundingClientRect(); return { x: (event.clientX - rect.left - graph.panX) / graph.scale, y: (event.clientY - rect.top - graph.panY) / graph.scale, sx: event.clientX - rect.left, sy: event.clientY - rect.top }; }
function hit(p) { for (let i = graph.nodes.length - 1; i >= 0; i--) { const n = graph.nodes[i]; if (Math.hypot(n.x - p.x, n.y - p.y) <= n.r + 9) return n; } return null; }
function pointerDown(event) { const p = point(event); graph.dragged = hit(p); graph.panning = !graph.dragged; graph.last = p; graph.moved = false; canvas.value.setPointerCapture?.(event.pointerId); if (graph.dragged) { graph.alpha = .12; if (event.pointerType === 'touch') longPressTimer = setTimeout(() => { if (graph.dragged) select(graph.dragged); }, 500); } }
function pointerMove(event) { const p = point(event); if (graph.dragged) { graph.dragged.x = p.x; graph.dragged.y = p.y; graph.dragged.vx = 0; graph.dragged.vy = 0; graph.moved = true; clearTimeout(longPressTimer); return; } if (graph.panning && graph.last) { graph.panX += p.sx - graph.last.sx; graph.panY += p.sy - graph.last.sy; graph.last = p; graph.moved = true; return; } if (!info.value) setHighlight(hit(p)); }
async function select(node) { if (!node) { info.value = null; detail.value = null; setHighlight(null); return; } info.value = node; detail.value = null; setHighlight(node); try { detail.value = await http.get(`/knowledge/points/${node.id}`); } catch (_) { detail.value = null; } }
function pointerUp(event) { clearTimeout(longPressTimer); const node = graph.dragged; const moved = graph.moved; graph.dragged = null; graph.panning = false; graph.last = null; if (node && !moved && !info.value) setHighlight(node); else if (!node && !moved && !info.value) setHighlight(null); }
function onWheel(event) { event.preventDefault(); const before = point(event); const next = Math.max(.45, Math.min(2.7, graph.scale * (event.deltaY > 0 ? .9 : 1.1))); graph.panX = (event.clientX - canvas.value.getBoundingClientRect().left) - before.x * next; graph.panY = (event.clientY - canvas.value.getBoundingClientRect().top) - before.y * next; graph.scale = next; }
function resetView() { info.value = null; detail.value = null; graph.panX = 0; graph.panY = 0; graph.scale = 1; graph.alpha = .3; graph.launchFrames = 48; graph.nodes.forEach((n) => { n.x = graph.width / 2 + (Math.random() - .5) * graph.width * .7; n.y = graph.height / 2 + (Math.random() - .5) * graph.height * .7; n.vx = n.vy = 0; n.tR = n.r; n.tA = 1; }); graph.links.forEach(l => { l.tA = 1; }); setHighlight(null); graph.alpha = .3; }
function contextMenu(event) { event.preventDefault(); const node = hit(point(event)); if (node) select(node); }
async function load() { const [data, tree] = await Promise.all([http.get('/knowledge/graph'), http.get('/knowledge/tree')]); initNodes(data, tree); await nextTick(); resize(); }
function onKeydown(event) { if (event.key === 'Escape' && info.value) select(null); }
onMounted(async () => { resize(); graph.raf = requestAnimationFrame(render); resizeObserver = new ResizeObserver(resize); resizeObserver.observe(wrap.value); window.addEventListener('keydown', onKeydown); await load(); });
onUnmounted(() => { clearTimeout(longPressTimer); cancelAnimationFrame(graph.raf); resizeObserver?.disconnect(); window.removeEventListener('keydown', onKeydown); });
watch(showTypes, () => { graph.alpha = .18; setHighlight(info.value || hover.value); }, { deep: true });
watch(search, query => { const keyword = query.trim().toLowerCase(); const any = !keyword || graph.nodes.some(n => n.name.toLowerCase().includes(keyword)); graph.nodes.forEach(n => { const match = !keyword || n.name.toLowerCase().includes(keyword); n.tA = match ? 1 : .06; n.tR = match ? n.r : n.r * .25; }); graph.links.forEach(l => { l.tA = keyword ? (l.a.tA > .5 && l.b.tA > .5 ? 1 : .02) : 1; }); graph.alpha = any ? .15 : .04; });
</script>

<template>
  <section class="graph-page">
    <div class="graph-head"><div><p class="eyebrow">ARCHITECT CAPABILITY ATLAS</p><h2>架构师能力星图</h2><p>以知识树为坐标：节点越大，越值得优先投入时间</p></div><BaseButton size="sm" variant="ghost" icon="rotate-ccw" @click="resetView">重置视图</BaseButton></div>
    <div class="graph-tools"><label class="map-search"><span>⌕</span><input v-model="search" placeholder="搜索知识点…" @keyup.enter="focusSearch" /></label><div class="map-filters"><label v-for="(label, key) in relNames" :key="key"><input v-model="showTypes[key]" type="checkbox" /><i :style="{ background: relColors[key] }"></i>{{ label }}</label></div><span class="map-count">{{ matchedCount }} 节点 · {{ visibleLinkCount }} 关系</span></div>
    <div ref="wrap" class="map-stage"><canvas ref="canvas" @pointerdown="pointerDown" @pointermove="pointerMove" @pointerup="pointerUp" @pointerleave="() => { if (!graph.dragged && !graph.panning && !info.value) setHighlight(null) }" @wheel="onWheel" @contextmenu="contextMenu"></canvas><div v-if="hover && !info" class="map-hover" :style="{ left: `${Math.min(graph.width - 160, hover.x * graph.scale + graph.panX + 16)}px`, top: `${Math.min(graph.height - 72, hover.y * graph.scale + graph.panY + 16)}px` }"><b>{{ hover.name }}</b><span>掌握度 {{ Math.round(hover.mastery || 0) }}% · 优先级 {{ Math.round(hover.priority * 100) }}</span></div><aside v-if="info" class="map-detail"><button class="detail-close" aria-label="关闭详情" @click="select(null)">×</button><p class="eyebrow">KNOWLEDGE POINT</p><h3>{{ info.name }}</h3><div class="detail-mastery"><span>掌握度</span><div><i :style="{ width: `${info.mastery || 0}%` }"></i></div><b>{{ Math.round(info.mastery || 0) }}%</b></div><p v-if="detail?.description" class="detail-desc">{{ detail.description }}</p><div v-if="detail" class="detail-meta"><span>学习优先级 {{ Math.round(info.priority * 100) }}</span><span>关联题 {{ detail.questions.length }}</span><span>子节点 {{ detail.children.length }}</span><span>关联点 {{ detail.related.length }}</span></div><div class="detail-actions"><BaseButton :to="`/practice?kp=${info.id}`" size="sm" icon="target">针对练习</BaseButton><BaseButton to="/knowledge" size="sm" variant="ghost" icon="book">查看详情</BaseButton></div></aside><div class="map-corner"><span class="size-key"><i></i><b>节点大小</b> = 主线权重 + 薄弱度 + 关联度</span><span class="name-key">名称始终显示</span></div></div>
  </section>
</template>

<style scoped>
.graph-page{display:grid;gap:14px}.graph-head{display:flex;align-items:end;justify-content:space-between;gap:16px}.graph-head h2{margin:5px 0 7px;font-size:21px;letter-spacing:-.02em}.graph-head p:not(.eyebrow){margin:0;color:var(--text-muted);font-size:12px}.graph-tools{display:flex;align-items:center;gap:12px;min-height:42px}.map-search{display:flex;align-items:center;gap:7px;width:220px;padding:0 10px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface-solid);color:var(--text-faint)}.map-search input{width:100%;padding:8px 0;background:transparent;border:0;box-shadow:none}.map-filters{display:flex;gap:9px;flex-wrap:wrap}.map-filters label{display:inline-flex;align-items:center;gap:5px;color:var(--text-muted);font-size:11px;cursor:pointer}.map-filters input{accent-color:var(--action-primary)}.map-filters i{width:7px;height:7px;border-radius:50%}.map-count{margin-left:auto;color:var(--text-faint);font:11px var(--mono);white-space:nowrap}.map-stage{position:relative;height:640px;overflow:hidden;border:1px solid var(--border);border-radius:var(--radius);background:radial-gradient(circle at 50% 45%,rgba(91,140,255,.055),transparent 48%),var(--ink-900)}.map-stage:before{content:'';position:absolute;inset:0;pointer-events:none;background-image:radial-gradient(rgba(148,163,199,.17) .7px,transparent .7px);background-size:20px 20px;opacity:.32}.map-stage canvas{position:relative;display:block;width:100%;height:100%;cursor:grab;touch-action:none}.map-stage canvas:active{cursor:grabbing}.map-hover{position:absolute;z-index:3;display:grid;gap:3px;min-width:126px;padding:9px 10px;border:1px solid var(--border-strong);border-radius:var(--radius-sm);background:var(--ink-800);box-shadow:var(--shadow);pointer-events:none;font-size:11px}.map-hover span{color:var(--text-muted)}.map-detail{position:absolute;z-index:4;top:14px;right:14px;width:min(292px,calc(100% - 28px));padding:16px;border:1px solid var(--border-strong);border-radius:var(--radius);background:var(--ink-900);box-shadow:var(--shadow)}.map-detail h3{margin:5px 24px 12px 0;font-size:16px}.detail-close{position:absolute;top:9px;right:9px;padding:0;width:24px;height:24px;border:0;background:transparent;color:var(--text-muted);font-size:20px;line-height:1}.detail-close:hover{background:var(--surface-hover);color:var(--text)}.detail-mastery{display:grid;grid-template-columns:auto 1fr auto;gap:7px;align-items:center;color:var(--text-muted);font-size:11px}.detail-mastery>div{height:5px;overflow:hidden;border-radius:4px;background:rgba(148,163,199,.14)}.detail-mastery i{display:block;height:100%;background:var(--action-primary)}.detail-mastery b{color:var(--text);font-size:11px}.detail-desc{margin:13px 0 0;color:var(--text-muted);font-size:12px;line-height:1.65}.detail-meta{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}.detail-meta span{padding:3px 6px;border-radius:4px;background:var(--surface);color:var(--text-muted);font-size:10px}.detail-actions{display:flex;gap:7px}.map-corner{position:absolute;z-index:2;bottom:12px;left:14px;display:flex;gap:10px;color:var(--text-faint);font-size:10px}.map-corner span{display:flex;align-items:center;gap:4px}.map-corner i{width:7px;height:7px;border-radius:50%}.risk{background:var(--risk-high)}.warn{background:var(--status-warning)}.safe{background:var(--status-success)}@media(max-width:820px){.graph-head{align-items:start;flex-direction:column}.graph-tools{align-items:flex-start;flex-wrap:wrap}.map-count{margin-left:0}.map-stage{height:540px}.map-detail{top:auto;right:10px;bottom:10px;width:calc(100% - 20px)}.map-corner{display:none}}@media(max-width:560px){.map-search{width:100%}.map-filters{gap:7px}.map-stage{height:480px}}
/* 博客关键词网络的浅色探索画布：深色应用壳内的独立阅读/探索平面 */
.graph-page{padding:28px 30px 30px;border:1px solid rgba(66,153,225,.18);border-radius:14px;background:#edf3fa;gap:18px}.graph-head{align-items:center;justify-content:center;position:relative;text-align:center}.graph-head h2{color:#2b2d42;font-size:25px;font-weight:650}.graph-head p:not(.eyebrow){color:#4a5568;font-size:13px}.graph-head .eyebrow{color:#637a9e}.graph-head :deep(.base-button){position:absolute;right:0}.graph-tools{justify-content:center;flex-wrap:wrap;gap:13px}.map-search{width:min(400px,100%);padding:0 15px;border:1px solid rgba(66,153,225,.25);border-radius:24px;background:rgba(255,255,255,.86);color:#4b84c8}.map-search input{color:#2d3748}.map-search input::placeholder{color:#8899bb}.map-filters{gap:10px}.map-filters label{color:#4a5568}.map-filters input{accent-color:#4299e1}.map-count{margin-left:0;color:#697a96}.map-stage{height:590px;border-color:rgba(66,153,225,.15);border-radius:12px;background:#f2f7fc}.map-stage:before{background-image:none;opacity:0}.map-hover{border-color:rgba(66,153,225,.25);border-radius:10px;background:rgba(255,255,255,.97);box-shadow:0 6px 20px rgba(32,69,114,.16);color:#2d3748}.map-hover span{color:#4a5568}.map-detail{border-color:rgba(66,153,225,.25);border-radius:10px;background:rgba(255,255,255,.98);box-shadow:0 6px 20px rgba(32,69,114,.16);color:#2d3748}.map-detail .eyebrow{color:#4299e1}.map-detail h3{color:#2b2d42}.detail-close{color:#8899bb}.detail-close:hover{background:#edf3fa;color:#2d3748}.detail-mastery{color:#4a5568}.detail-mastery>div{background:#d9e4f1}.detail-mastery i{background:#4299e1}.detail-mastery b{color:#2d3748}.detail-desc{color:#4a5568}.detail-meta span{background:#eef4fa;color:#59708e}.map-corner{color:#657894}.map-corner .risk{background:#60a5fa}.map-corner .warn{background:#3b82f6}.map-corner .safe{background:#7c3aed}.map-corner .degree-1{background:#60a5fa}.map-corner .degree-3{background:#3b82f6}.map-corner .degree-5{background:#2563eb}.map-corner .degree-7{background:#7c3aed}@media(max-width:820px){.graph-page{padding:22px 16px}.graph-head{align-items:center}.graph-head :deep(.base-button){position:static}.map-stage{height:520px}}@media(max-width:560px){.graph-page{padding:18px 12px}.graph-head h2{font-size:21px}.map-stage{height:460px}}
.map-corner{gap:9px;align-items:center}.map-corner span{gap:5px;padding:5px 7px;border:1px solid rgba(66,153,225,.16);border-radius:6px;background:rgba(255,255,255,.7)}.map-corner i{width:17px;height:17px;border:2px solid #7257b7;border-radius:50%;background:rgba(114,87,183,.25)}.map-corner b{color:#354865}
</style>
