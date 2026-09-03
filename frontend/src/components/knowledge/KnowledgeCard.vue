<script setup>
import MindmapNode from './MindmapNode.vue';

defineProps({
  card: { type: Object, default: null },
});

function label(text) {
  return (text || '')
    .split('\n')
    .filter(Boolean)
    .join(' / ');
}
</script>

<template>
  <div v-if="card" class="kcard">
    <p v-if="card.title" class="kcard-title">{{ card.title }}</p>
    <div v-if="card.blocks && card.blocks.length" class="kcard-blocks">
      <template v-for="(block, b) in card.blocks" :key="b">
        <!-- 思维导图树 -->
        <div v-if="block.type === 'mindmap'" class="kb-block mm">
          <div class="mm-root">{{ block.root.text }}</div>
          <ul class="mm-tree">
            <li v-for="(child, i) in block.root.children" :key="i">
              <MindmapNode :node="child" :depth="0" />
            </li>
          </ul>
        </div>

        <!-- 关系边列表 -->
        <div v-else-if="block.type === 'graph' && block.edges.length" class="kb-block">
          <ul class="eg">
            <li v-for="(e, i) in block.edges" :key="i">
              <span class="eg-from">{{ label(e.from_label) }}</span>
              <span class="eg-arrow">{{ e.label ? `—${e.label}→` : '→' }}</span>
              <span class="eg-to">{{ label(e.to_label) }}</span>
            </li>
          </ul>
        </div>

        <!-- 表格 -->
        <div v-else-if="block.type === 'table'" class="kb-block">
          <table class="kb-table">
            <thead>
              <tr><th v-for="(h, i) in block.headers" :key="i">{{ h }}</th></tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in block.rows" :key="i">
                <td v-for="(cell, j) in row" :key="j">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 速记口诀 -->
        <div v-else-if="block.type === 'mnemonic'" class="kb-block">
          <dl class="mmemo">
            <template v-for="(item, i) in block.items" :key="i">
              <dt>{{ item.term }}</dt>
              <dd>{{ item.text }}</dd>
            </template>
          </dl>
        </div>

        <!-- 纯文本 -->
        <pre v-else-if="block.type === 'text'" class="kb-text">{{ block.content }}</pre>
      </template>
    </div>
    <footer v-if="card.source" class="kcard-foot">
      {{ card.source.repo }} · {{ card.source.license }}
      <a v-if="card.source.url" :href="card.source.url" target="_blank" rel="noopener">来源 ↗</a>
    </footer>
  </div>
</template>

<style scoped>
.kcard{display:grid;gap:10px;margin-top:12px;padding-top:12px;border-top:1px solid var(--border)}
.kcard-title{color:var(--text);font-size:12px;font-weight:650;letter-spacing:.01em}
.kcard-blocks{display:grid;gap:11px}
.kb-block{display:grid;gap:6px}
.mm-root{color:var(--action-primary);font-size:12px;font-weight:650}
.mm-tree{list-style:none;margin:0;padding:0}
.mm-tree>li{margin:3px 0}
.eg{list-style:none;margin:0;padding:0;display:grid;gap:5px}
.eg li{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px;color:var(--text-muted);font-size:11px;line-height:1.4}
.eg-from{color:var(--text);font-weight:600}
.eg-arrow{color:var(--action-primary);font-size:10px;white-space:nowrap}
.eg-to{color:var(--text)}
.kb-table{border-collapse:collapse;width:100%;font-size:11px}
.kb-table th{background:var(--surface);color:var(--text-muted);text-align:left;font-weight:600}
.kb-table th,.kb-table td{padding:5px 7px;border:1px solid var(--border-strong)}
.kb-table td{color:var(--text-muted);font-variant-numeric:tabular-nums}
.mmemo{margin:0;display:grid;gap:5px}
.mmemo dt{color:var(--text);font-size:12px;font-weight:650}
.mmemo dd{margin:0;color:var(--text-muted);font-size:11px;line-height:1.5}
.kb-text{margin:0;padding:8px 9px;border-radius:var(--radius-sm);background:var(--surface-inset);color:var(--text-muted);font:11px/1.55 var(--mono);white-space:pre-wrap}
.kcard-foot{color:var(--text-faint);font-size:10px}
.kcard-foot a{margin-left:6px;color:var(--text-muted)}
.kcard-foot a:hover{color:var(--action-primary)}
</style>
