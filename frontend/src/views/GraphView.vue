<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { http } from '../api/client';
import BaseButton from '../components/base/BaseButton.vue';

const canvas = ref(null); const wrap = ref(null);
const search = ref(''); const info = ref(null); const detail = ref(null); const hover = ref(null); const selected = ref(null);
const showTypes = ref({ related: true, prerequisite: true, contains: true, conflicts: true, backbone: true });
const relNames = { related: '相关', prerequisite: '前置', contains: '包含', conflicts: '冲突', backbone: '主线' };
const relColors = { related: '#637da8', prerequisite: '#c9a13d', contains: '#5b8cff', conflicts: '#cf6a68', backbone: '#7a6bb0' };
const domains = {
  1: { title: '计算机系统基础', short: '系统基础', x: .17, y: .27, color: '#4b86d1' },
  2: { title: '软件工程与项目管理', short: '工程与管理', x: .17, y: .73, color: '#5f78ba' },
  3: { title: '系统架构设计（主线）', short: '架构设计核心', x: .52, y: .50, color: '#7257b7' },
  4: { title: '数学与经济管理', short: '数学与管理', x: .86, y: .17, color: '#4d9a9a' },
  5: { title: '信息安全与可靠性', short: '安全与可靠性', x: .86, y: .50, color: '#c37b5c' },
  6: { title: '专业英语', short: '专业英语', x: .86, y: .84, color: '#5f8f72' },
};
const graph = { nodes: [], links: [], width: 1, height: 1, panX: 0, panY: 0, scale: 1, alpha: .3, launchFrames: 48, raf: 0, dragged: null, panning: false, last: null, moved: false };
const nodeTotal = ref(0); const linkTotal = ref(0);
let ctx; let resizeObserver; let longPressTimer;

const matchedCount = computed(() => { search.value; return nodeTotal.value ? graph.nodes.filter(n => n.name.includes(search.value.trim())).length : 0; });
const visibleLinkCount = computed(() => { linkTotal.value; Object.values(showTypes.value); return graph.links.filter(l => showTypes.value[l.type]).length; });
const overallMastery = computed(() => { nodeTotal.value; if (!graph.nodes.length) return 0; return Math.round(graph.nodes.reduce((sum, n) => sum + (n.mastery || 0), 0) / graph.nodes.length); });
const masteredCount = computed(() => { nodeTotal.value; return graph.nodes.filter(n => (n.mastery || 0) >= 80).length; });
const stageHeight = computed(() => { nodeTotal.value; const largestDomain = Math.max(0, ...Object.keys(domains).map(id => graph.nodes.filter(n => n.domain === Number(id)).length)); return Math.min(900, Math.max(590, 500 + largestDomain * 8)); });
const filteredLinks = () => graph.links.filter(l => showTypes.value[l.type]);
const sameNode = (a, b) => Boolean(a && b && a.id === b.id);
function isFocused(node) { return sameNode(node, selected.value) || sameNode(node, info.value); }
function nodeColor(node) { return isFocused(node) ? '#e7343f' : domains[node.domain]?.color || '#4b86d1'; }
function rgb(hex) { const n = Number.parseInt(hex.slice(1), 16); return { r: n >> 16, g: (n >> 8) & 255, b: n & 255 }; }
function wrapLabel(name) { const atoms = name.match(/（[^）]*）|[A-Za-z0-9/+.-]+|./g) || [name]; const lines = []; let line = ''; atoms.forEach(atom => { const next = line + atom; if (line && next.length > 9) { lines.push(line.trim()); line = atom.trimStart(); } else line = next; }); if (line) lines.push(line.trim()); return lines; }
function domainProgress(id) { const nodes = graph.nodes.filter(n => n.domain === Number(id)); return nodes.length ? Math.round(nodes.reduce((sum, n) => sum + (n.mastery || 0), 0) / nodes.length) : 0; }
function domainGeometry(id) { const nodes = graph.nodes.filter(n => n.domain === Number(id)); const core = Number(id) === 3; const leafCount = Math.max(1, nodes.filter(n => n.parent_id).length); const columns = Math.ceil(Math.sqrt((leafCount + 1) * (core ? 1.15 : 1))); const rows = Math.ceil((leafCount + 1) / columns); return { x: graph.width * domains[id].x, y: graph.height * domains[id].y, columns, rows, cellX: core ? 48 : 45, cellY: core ? 54 : 50, radiusX: Math.max(core ? 168 : 82, columns * (core ? 25 : 24) + 22), radiusY: Math.max(core ? 178 : 72, rows * (core ? 28 : 27) + 22) }; }
function nodeDomain(node, treeById) {
  let current = node; const seen = new Set();
  while (current?.parent_id && !seen.has(current.id)) { seen.add(current.id); current = treeById.get(current.parent_id); }
  return current?.id || 3;
}
function assignDomainTargets() {
  const groups = new Map(); graph.nodes.forEach(n => { const items = groups.get(n.domain) || []; items.push(n); groups.set(n.domain, items); });
  groups.forEach((items, domainId) => {
    const layout = domainGeometry(domainId); const centerX = layout.x; const centerY = layout.y;
    items.sort((a, b) => String(a.code || '').split('.').length - String(b.code || '').split('.').length || String(a.code || '').localeCompare(String(b.code || '')));
    const leaves = items.filter(n => n.parent_id);
    items.forEach(n => { n.targetX = centerX; n.targetY = centerY; });
    leaves.forEach((n, index) => {
      const slot = index >= Math.floor(leaves.length / 2) ? index + 1 : index; const column = slot % layout.columns; const row = Math.floor(slot / layout.columns);
      n.targetX = centerX + (column - (layout.columns - 1) / 2) * layout.cellX; n.targetY = centerY + (row - (layout.rows - 1) / 2) * layout.cellY;
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
  graph.nodes.forEach(n => { n.x = n.targetX + (Math.random() - .5) * 72; n.y = n.targetY + (Math.random() - .5) * 72; });
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
function roundedRectPath(x, y, width, height, radius = 18) { const r = Math.min(radius, width / 2, height / 2); ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + width, y, x + width, y + height, r); ctx.arcTo(x + width, y + height, x, y + height, r); ctx.arcTo(x, y + height, x, y, r); ctx.arcTo(x, y, x + width, y, r); ctx.closePath(); }
function drawDomains() {
  Object.entries(domains).forEach(([id, zone]) => {
    const layout = domainGeometry(id); const { x, y, radiusX, radiusY } = layout; const mastery = domainProgress(id); const left = x - radiusX; const top = y - radiusY; const width = radiusX * 2; const height = radiusY * 2;
    ctx.save(); ctx.globalAlpha = .12; ctx.fillStyle = zone.color; roundedRectPath(left, top, width, height); ctx.fill(); ctx.globalAlpha = 1; ctx.strokeStyle = `${zone.color}55`; ctx.setLineDash([3, 5]); ctx.lineWidth = 1; roundedRectPath(left, top, width, height); ctx.stroke(); ctx.setLineDash([]); ctx.strokeStyle = '#2e9b80'; ctx.lineWidth = 2.5; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(left + 14, top + 10); ctx.lineTo(left + 14 + (width - 28) * mastery / 100, top + 10); ctx.stroke(); ctx.fillStyle = zone.color; ctx.globalAlpha = .82; ctx.font = '600 10px Inter, Microsoft YaHei, sans-serif'; ctx.textAlign = 'left'; ctx.fillText(`${zone.short} · ${mastery}%`, left + 14, top + 26); ctx.restore();
  });
}
function drawMasteryRings(query) {
  graph.nodes.forEach(n => { const mastery = Math.max(0, Math.min(100, n.mastery || 0)); if (!mastery) return; const radius = n.dR + 3; ctx.save(); ctx.globalAlpha = n.dA * (!query || n.name.includes(query) ? .9 : .16); ctx.strokeStyle = mastery >= 80 ? '#16846f' : '#2381d8'; ctx.lineWidth = 2.4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(n.x, n.y, radius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * mastery / 100); ctx.stroke(); ctx.restore(); });
}
function drawLink(link, focus, focusNode, query) {
  const active = !focus || sameNode(link.a, focusNode) || sameNode(link.b, focusNode); const match = !query || (link.a.name.includes(query) && link.b.name.includes(query)); const crossDomain = link.a.domain !== link.b.domain;
  ctx.save(); ctx.globalAlpha = link.dA * (active ? (match ? .74 : .34) : .045) * (crossDomain && !focus ? .4 : 1); ctx.strokeStyle = active && focus ? '#315fba' : '#7ca4da'; ctx.lineWidth = active && focus ? 1.7 : crossDomain ? .7 : .65; ctx.beginPath(); ctx.moveTo(link.a.x, link.a.y);
  if (crossDomain) { const dx = link.b.x - link.a.x; const dy = link.b.y - link.a.y; const distance = Math.hypot(dx, dy) || 1; const bend = Math.min(46, Math.max(16, distance * .1)) * (link.a.domain < link.b.domain ? 1 : -1); ctx.quadraticCurveTo((link.a.x + link.b.x) / 2 - dy / distance * bend, (link.a.y + link.b.y) / 2 + dx / distance * bend, link.b.x, link.b.y); } else ctx.lineTo(link.b.x, link.b.y);
  ctx.stroke(); ctx.restore();
}
function drawFocusedLabel(node) {
  if (!node) return;
  const radius = node.dR; const lines = node.label || [node.name]; const fontSize = lines.length > 2 ? 7.5 : lines.length > 1 ? 9 : 11;
  ctx.save(); ctx.globalAlpha = 1; ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(120,20,25,.35)'; ctx.shadowBlur = 2; ctx.font = `700 ${fontSize}px Inter, Microsoft YaHei, sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; const startY = node.y - (lines.length - 1) * fontSize * .62; lines.forEach((line, index) => ctx.fillText(line, node.x, startY + index * (fontSize + 2))); ctx.restore();
}
function neighborhood(node) { if (!node) return null; const target = graph.nodes.find(n => sameNode(n, node)) || node; const set = new Set([target]); filteredLinks().forEach(l => { if (sameNode(l.a, target)) set.add(l.b); if (sameNode(l.b, target)) set.add(l.a); }); return set; }
function setHighlight(node) {
  const focusNode = node || selected.value || info.value; const connected = neighborhood(focusNode);
  graph.nodes.forEach(n => { const related = connected?.has(n); n.tR = !focusNode ? n.r : sameNode(n, focusNode) ? Math.max(n.r * 1.55, 34) : related ? n.r * 1.14 : n.r * .86; n.tA = !focusNode ? 1 : sameNode(n, focusNode) ? 1 : related ? .94 : .18; });
  graph.links.forEach(l => { l.tA = !focusNode ? 1 : (sameNode(l.a, focusNode) || sameNode(l.b, focusNode)) ? 1 : .12; });
  graph.alpha = focusNode ? .06 : .12;
}
function focusSearch() {
  const query = search.value.trim().toLowerCase(); if (!query) return setHighlight(null);
  const node = graph.nodes.find(n => n.name.toLowerCase().includes(query));
  if (!node) return;
  selected.value = node; hover.value = node; setHighlight(node); graph.nodes.forEach(n => { const keep = sameNode(n, node) || neighborhood(node).has(n); n.tA = keep ? 1 : .24; n.tR = sameNode(n, node) ? n.r * 1.3 : keep ? n.r * 1.1 : n.r * .72; }); graph.links.forEach(l => { l.tA = l.a.tA > .5 && l.b.tA > .5 ? 1 : .12; }); graph.alpha = .3;
}
function render() {
  if (!ctx) return;
  physics(); graph.nodes.forEach(n => { n.dR += (n.tR - n.dR) * .16; n.dA += (n.tA - n.dA) * .14; }); graph.links.forEach(l => { l.dA += (l.tA - l.dA) * .14; }); ctx.clearRect(0, 0, graph.width, graph.height); ctx.save(); ctx.translate(graph.panX, graph.panY); ctx.scale(graph.scale, graph.scale);
  drawDomains();
  const query = search.value.trim(); const focusNode = selected.value || info.value || hover.value; const focus = neighborhood(focusNode); const links = filteredLinks();
  links.forEach(l => drawLink(l, focus, focusNode, query));
  [...graph.nodes].sort((a, b) => a.dR - b.dR).forEach(n => { const matched = !query || n.name.includes(query); const radius = n.dR; const color = rgb(nodeColor(n)); ctx.save(); ctx.globalAlpha = n.dA * (matched ? 1 : .16); const fill = ctx.createRadialGradient(n.x - radius * .28, n.y - radius * .28, 0, n.x, n.y, radius); fill.addColorStop(0, `rgb(${Math.min(255, color.r + 34)},${Math.min(255, color.g + 34)},${Math.min(255, color.b + 34)})`); fill.addColorStop(1, nodeColor(n)); ctx.fillStyle = fill; ctx.beginPath(); ctx.arc(n.x, n.y, radius, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = isFocused(n) ? '#f3c96b' : sameNode(n, hover.value) ? '#fff' : 'rgba(255,255,255,.7)'; ctx.lineWidth = isFocused(n) || sameNode(n, hover.value) ? 2.6 : 1.4; ctx.stroke(); ctx.fillStyle = '#283a55'; ctx.shadowColor = 'rgba(255,255,255,.96)'; ctx.shadowBlur = 3; ctx.font = `600 ${Math.max(9.5, Math.min(11.5, radius * .43))}px Inter, Microsoft YaHei, sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'top'; n.label.forEach((line, index) => ctx.fillText(line, n.x, n.y + radius + 5 + index * 12)); ctx.restore(); });
  drawMasteryRings(query); drawFocusedLabel(selected.value || info.value);
  ctx.restore(); graph.raf = requestAnimationFrame(render);
}
function point(event) { const rect = canvas.value.getBoundingClientRect(); return { x: (event.clientX - rect.left - graph.panX) / graph.scale, y: (event.clientY - rect.top - graph.panY) / graph.scale, sx: event.clientX - rect.left, sy: event.clientY - rect.top }; }
function hit(p) { for (let i = graph.nodes.length - 1; i >= 0; i--) { const n = graph.nodes[i]; if (Math.hypot(n.x - p.x, n.y - p.y) <= n.r + 9) return n; } return null; }
function pointerDown(event) { const p = point(event); graph.dragged = hit(p); graph.panning = !graph.dragged; graph.last = p; graph.moved = false; canvas.value.setPointerCapture?.(event.pointerId); if (graph.dragged) { graph.alpha = .12; if (event.pointerType === 'touch') longPressTimer = setTimeout(() => { if (graph.dragged) select(graph.dragged); }, 500); } }
function pointerMove(event) { const p = point(event); if (graph.dragged) { graph.dragged.x = p.x; graph.dragged.y = p.y; graph.dragged.vx = 0; graph.dragged.vy = 0; graph.moved = true; clearTimeout(longPressTimer); return; } if (graph.panning && graph.last) { graph.panX += p.sx - graph.last.sx; graph.panY += p.sy - graph.last.sy; graph.last = p; graph.moved = true; return; } hover.value = hit(p); if (!selected.value && !info.value) setHighlight(hover.value); }
async function select(node) { if (!node) { info.value = null; detail.value = null; selected.value = null; setHighlight(null); return; } info.value = node; selected.value = node; hover.value = node; detail.value = null; setHighlight(node); try { detail.value = await http.get(`/knowledge/points/${node.id}`); } catch (_) { detail.value = null; } }
function pointerUp(event) { clearTimeout(longPressTimer); const node = graph.dragged; const moved = graph.moved; graph.dragged = null; graph.panning = false; graph.last = null; if (node && !moved) select(node); else if (!node && !moved) select(null); }
function onWheel(event) { event.preventDefault(); const before = point(event); const next = Math.max(.45, Math.min(2.7, graph.scale * (event.deltaY > 0 ? .9 : 1.1))); graph.panX = (event.clientX - canvas.value.getBoundingClientRect().left) - before.x * next; graph.panY = (event.clientY - canvas.value.getBoundingClientRect().top) - before.y * next; graph.scale = next; }
function resetView() { info.value = null; detail.value = null; selected.value = null; hover.value = null; graph.panX = 0; graph.panY = 0; graph.scale = 1; graph.alpha = .3; graph.launchFrames = 48; graph.nodes.forEach((n) => { n.x = n.targetX + (Math.random() - .5) * 72; n.y = n.targetY + (Math.random() - .5) * 72; n.vx = n.vy = 0; n.tR = n.r; n.tA = 1; }); graph.links.forEach(l => { l.tA = 1; }); setHighlight(null); graph.alpha = .3; }
function contextMenu(event) { event.preventDefault(); const node = hit(point(event)); if (node) select(node); }
async function load() { const [data, tree] = await Promise.all([http.get('/knowledge/graph'), http.get('/knowledge/tree')]); initNodes(data, tree); await nextTick(); if (wrap.value) wrap.value.style.height = `${stageHeight.value}px`; resize(); }
function onKeydown(event) { if (event.key === 'Escape' && (info.value || selected.value)) select(null); }
onMounted(async () => { resize(); graph.raf = requestAnimationFrame(render); resizeObserver = new ResizeObserver(resize); resizeObserver.observe(wrap.value); window.addEventListener('keydown', onKeydown); await load(); });
onUnmounted(() => { clearTimeout(longPressTimer); cancelAnimationFrame(graph.raf); resizeObserver?.disconnect(); window.removeEventListener('keydown', onKeydown); });
watch(showTypes, () => { graph.alpha = .18; setHighlight(info.value || selected.value || hover.value); }, { deep: true });
watch(search, query => { const keyword = query.trim().toLowerCase(); const any = !keyword || graph.nodes.some(n => n.name.toLowerCase().includes(keyword)); graph.nodes.forEach(n => { const match = !keyword || n.name.toLowerCase().includes(keyword); n.tA = match ? 1 : .06; n.tR = match ? n.r : n.r * .25; }); graph.links.forEach(l => { l.tA = keyword ? (l.a.tA > .5 && l.b.tA > .5 ? 1 : .02) : 1; }); graph.alpha = any ? .15 : .04; });
</script>

<template>
  <section class="graph-page">
    <div class="atlas-top"><aside class="progress-card"><p>LEARNING PROGRESS</p><strong>{{ overallMastery }}%</strong><span>总体掌握度</span><div><i><em :style="{ width: `${overallMastery}%` }"></em></i><b>{{ masteredCount }}/{{ nodeTotal }} 已掌握</b></div><small>节点外环表示单点掌握进度</small></aside><div class="atlas-main"><div class="graph-head"><div><p class="eyebrow">ARCHITECT CAPABILITY ATLAS</p><h2>架构师能力星图</h2><p>以知识树为坐标：节点越大，越值得优先投入时间</p></div><BaseButton size="sm" variant="ghost" icon="rotate-ccw" @click="resetView">重置视图</BaseButton></div><div class="graph-tools"><label class="map-search"><span>⌕</span><input v-model="search" placeholder="搜索知识点…" @keyup.enter="focusSearch" /></label><div class="map-filters"><label v-for="(label, key) in relNames" :key="key"><input v-model="showTypes[key]" type="checkbox" /><i :style="{ background: relColors[key] }"></i>{{ label }}</label></div><span class="map-count">{{ matchedCount }} 节点 · {{ visibleLinkCount }} 关系</span></div></div></div>
    <div ref="wrap" class="map-stage"><canvas ref="canvas" @pointerdown="pointerDown" @pointermove="pointerMove" @pointerup="pointerUp" @pointerleave="() => { if (!graph.dragged && !graph.panning && !info.value) setHighlight(null) }" @wheel="onWheel" @contextmenu="contextMenu"></canvas><div v-if="hover && !info" class="map-hover" :style="{ left: `${Math.min(graph.width - 160, hover.x * graph.scale + graph.panX + 16)}px`, top: `${Math.min(graph.height - 72, hover.y * graph.scale + graph.panY + 16)}px` }"><b>{{ hover.name }}</b><span>掌握度 {{ Math.round(hover.mastery || 0) }}% · 优先级 {{ Math.round(hover.priority * 100) }}</span></div><aside v-if="info" class="map-detail"><button class="detail-close" aria-label="关闭详情" @click="select(null)">×</button><p class="eyebrow">KNOWLEDGE POINT</p><h3>{{ info.name }}</h3><div class="detail-mastery"><span>掌握度</span><div><i :style="{ width: `${info.mastery || 0}%` }"></i></div><b>{{ Math.round(info.mastery || 0) }}%</b></div><p v-if="detail?.description" class="detail-desc">{{ detail.description }}</p><div v-if="detail" class="detail-meta"><span>学习优先级 {{ Math.round(info.priority * 100) }}</span><span>关联题 {{ detail.questions.length }}</span><span>子节点 {{ detail.children.length }}</span><span>关联点 {{ detail.related.length }}</span></div><div class="detail-actions"><BaseButton :to="`/practice?kp=${info.id}`" size="sm" icon="target">针对练习</BaseButton><BaseButton to="/knowledge" size="sm" variant="ghost" icon="book">查看详情</BaseButton></div></aside><div class="map-corner"><span class="size-key"><i></i><b>节点大小</b> = 主线权重 + 薄弱度 + 关联度</span><span class="name-key">名称始终显示</span></div></div>
  </section>
</template>

<style scoped>
.graph-page{display:grid;gap:14px}.graph-head{display:flex;align-items:end;justify-content:space-between;gap:16px}.graph-head h2{margin:5px 0 7px;font-size:21px;letter-spacing:-.02em}.graph-head p:not(.eyebrow){margin:0;color:var(--text-muted);font-size:12px}.graph-tools{display:flex;align-items:center;gap:12px;min-height:42px}.map-search{display:flex;align-items:center;gap:7px;width:220px;padding:0 10px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface-solid);color:var(--text-faint)}.map-search input{width:100%;padding:8px 0;background:transparent;border:0;box-shadow:none}.map-filters{display:flex;gap:9px;flex-wrap:wrap}.map-filters label{display:inline-flex;align-items:center;gap:5px;color:var(--text-muted);font-size:11px;cursor:pointer}.map-filters input{accent-color:var(--action-primary)}.map-filters i{width:7px;height:7px;border-radius:50%}.map-count{margin-left:auto;color:var(--text-faint);font:11px var(--mono);white-space:nowrap}.map-stage{position:relative;height:640px;overflow:hidden;border:1px solid var(--border);border-radius:var(--radius);background:radial-gradient(circle at 50% 45%,rgba(91,140,255,.055),transparent 48%),var(--ink-900)}.map-stage:before{content:'';position:absolute;inset:0;pointer-events:none;background-image:radial-gradient(rgba(148,163,199,.17) .7px,transparent .7px);background-size:20px 20px;opacity:.32}.map-stage canvas{position:relative;display:block;width:100%;height:100%;cursor:grab;touch-action:none}.map-stage canvas:active{cursor:grabbing}.map-hover{position:absolute;z-index:3;display:grid;gap:3px;min-width:126px;padding:9px 10px;border:1px solid var(--border-strong);border-radius:var(--radius-sm);background:var(--ink-800);box-shadow:var(--shadow);pointer-events:none;font-size:11px}.map-hover span{color:var(--text-muted)}.map-detail{position:absolute;z-index:4;top:14px;right:14px;width:min(292px,calc(100% - 28px));padding:16px;border:1px solid var(--border-strong);border-radius:var(--radius);background:var(--ink-900);box-shadow:var(--shadow)}.map-detail h3{margin:5px 24px 12px 0;font-size:16px}.detail-close{position:absolute;top:9px;right:9px;padding:0;width:24px;height:24px;border:0;background:transparent;color:var(--text-muted);font-size:20px;line-height:1}.detail-close:hover{background:var(--surface-hover);color:var(--text)}.detail-mastery{display:grid;grid-template-columns:auto 1fr auto;gap:7px;align-items:center;color:var(--text-muted);font-size:11px}.detail-mastery>div{height:5px;overflow:hidden;border-radius:4px;background:rgba(148,163,199,.14)}.detail-mastery i{display:block;height:100%;background:var(--action-primary)}.detail-mastery b{color:var(--text);font-size:11px}.detail-desc{margin:13px 0 0;color:var(--text-muted);font-size:12px;line-height:1.65}.detail-meta{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}.detail-meta span{padding:3px 6px;border-radius:4px;background:var(--surface);color:var(--text-muted);font-size:10px}.detail-actions{display:flex;gap:7px}.map-corner{position:absolute;z-index:2;bottom:12px;left:14px;display:flex;gap:10px;color:var(--text-faint);font-size:10px}.map-corner span{display:flex;align-items:center;gap:4px}.map-corner i{width:7px;height:7px;border-radius:50%}.risk{background:var(--risk-high)}.warn{background:var(--status-warning)}.safe{background:var(--status-success)}@media(max-width:820px){.graph-head{align-items:start;flex-direction:column}.graph-tools{align-items:flex-start;flex-wrap:wrap}.map-count{margin-left:0}.map-stage{height:540px}.map-detail{top:auto;right:10px;bottom:10px;width:calc(100% - 20px)}.map-corner{display:none}}@media(max-width:560px){.map-search{width:100%}.map-filters{gap:7px}.map-stage{height:480px}}
/* 博客关键词网络的浅色探索画布：深色应用壳内的独立阅读/探索平面 */
.graph-page{padding:28px 30px 30px;border:1px solid rgba(66,153,225,.18);border-radius:14px;background:#edf3fa;gap:18px}.graph-head{align-items:center;justify-content:center;position:relative;text-align:center}.graph-head h2{color:#2b2d42;font-size:25px;font-weight:650}.graph-head p:not(.eyebrow){color:#4a5568;font-size:13px}.graph-head .eyebrow{color:#637a9e}.graph-head :deep(.base-button){position:absolute;right:0}.graph-tools{justify-content:center;flex-wrap:wrap;gap:13px}.map-search{width:min(400px,100%);padding:0 15px;border:1px solid rgba(66,153,225,.25);border-radius:24px;background:rgba(255,255,255,.86);color:#4b84c8}.map-search input{color:#2d3748}.map-search input::placeholder{color:#8899bb}.map-filters{gap:10px}.map-filters label{color:#4a5568}.map-filters input{accent-color:#4299e1}.map-count{margin-left:0;color:#697a96}.map-stage{height:590px;border-color:rgba(66,153,225,.15);border-radius:12px;background:#f2f7fc}.map-stage:before{background-image:none;opacity:0}.map-hover{border-color:rgba(66,153,225,.25);border-radius:10px;background:rgba(255,255,255,.97);box-shadow:0 6px 20px rgba(32,69,114,.16);color:#2d3748}.map-hover span{color:#4a5568}.map-detail{border-color:rgba(66,153,225,.25);border-radius:10px;background:rgba(255,255,255,.98);box-shadow:0 6px 20px rgba(32,69,114,.16);color:#2d3748}.map-detail .eyebrow{color:#4299e1}.map-detail h3{color:#2b2d42}.detail-close{color:#8899bb}.detail-close:hover{background:#edf3fa;color:#2d3748}.detail-mastery{color:#4a5568}.detail-mastery>div{background:#d9e4f1}.detail-mastery i{background:#4299e1}.detail-mastery b{color:#2d3748}.detail-desc{color:#4a5568}.detail-meta span{background:#eef4fa;color:#59708e}.map-corner{color:#657894}.map-corner .risk{background:#60a5fa}.map-corner .warn{background:#3b82f6}.map-corner .safe{background:#7c3aed}.map-corner .degree-1{background:#60a5fa}.map-corner .degree-3{background:#3b82f6}.map-corner .degree-5{background:#2563eb}.map-corner .degree-7{background:#7c3aed}@media(max-width:820px){.graph-page{padding:22px 16px}.graph-head{align-items:center}.graph-head :deep(.base-button){position:static}.map-stage{height:520px}}@media(max-width:560px){.graph-page{padding:18px 12px}.graph-head h2{font-size:21px}.map-stage{height:460px}}
.map-corner{gap:9px;align-items:center}.map-corner span{gap:5px;padding:5px 7px;border:1px solid rgba(66,153,225,.16);border-radius:6px;background:rgba(255,255,255,.7)}.map-corner i{width:17px;height:17px;border:2px solid #7257b7;border-radius:50%;background:rgba(114,87,183,.25)}.map-corner b{color:#354865}
.atlas-progress{display:flex;align-items:center;justify-content:center;gap:7px;margin-top:10px;color:#61728e;font-size:10px}.atlas-progress b{color:#2d6fb3;font:700 12px var(--mono)}.atlas-progress i{display:block;width:88px;height:5px;overflow:hidden;border-radius:8px;background:#d7e4f2}.atlas-progress em{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#4a9be7,#2e9b80)}.atlas-progress span:last-child{color:#8291a8}
.atlas-top{display:grid;grid-template-columns:220px minmax(0,1fr);gap:18px;align-items:stretch}.progress-card{display:flex;flex-direction:column;justify-content:center;min-height:126px;padding:18px 20px;border:1px solid rgba(66,153,225,.25);border-radius:12px;background:linear-gradient(145deg,#fafdff,#e8f2fb);box-shadow:0 8px 22px rgba(46,90,137,.07)}.progress-card p{margin:0 0 5px;color:#647fa3;font:700 10px var(--mono);letter-spacing:.06em}.progress-card strong{color:#276eaf;font:700 32px/1 var(--mono);letter-spacing:-.06em}.progress-card>span{margin-top:4px;color:#4a627e;font-size:11px}.progress-card>div{display:flex;align-items:center;gap:8px;margin-top:12px}.progress-card i{display:block;flex:1;height:6px;overflow:hidden;border-radius:8px;background:#d5e3f0}.progress-card em{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#4a9be7,#2e9b80)}.progress-card b{color:#57708d;font:600 10px var(--mono);white-space:nowrap}.progress-card small{margin-top:10px;color:#8395ac;font-size:10px}.atlas-main{display:grid;gap:10px;min-width:0;padding:4px 0}.atlas-main .graph-head{align-items:center;justify-content:space-between;text-align:left}.atlas-main .graph-head h2{margin:3px 0 4px}.atlas-main .graph-head :deep(.base-button){position:static}.atlas-main .graph-tools{justify-content:flex-start;min-height:38px}.atlas-main .map-search{width:min(390px,40%)}.atlas-main .map-count{margin-left:auto}@media(max-width:820px){.atlas-top{grid-template-columns:1fr}.progress-card{min-height:0}.atlas-main .graph-head{align-items:center;text-align:center}.atlas-main .graph-tools{justify-content:center}.atlas-main .map-search{width:min(400px,100%)}.atlas-main .map-count{margin-left:0}}
</style>
