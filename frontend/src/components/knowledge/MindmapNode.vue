<script setup>
defineOptions({ name: 'MindmapNode' });
defineProps({
  node: { type: Object, required: true },
  depth: { type: Number, default: 0 },
});
</script>

<template>
  <details v-if="node.children && node.children.length" class="mm-branch" :open="depth < 1">
    <summary>{{ node.text }}</summary>
    <ul>
      <li v-for="(child, i) in node.children" :key="i">
        <MindmapNode :node="child" :depth="depth + 1" />
      </li>
    </ul>
  </details>
  <span v-else class="mm-leaf">{{ node.text }}</span>
</template>

<style scoped>
.mm-branch{margin:0}
.mm-branch>summary{list-style:none;cursor:pointer;color:var(--text);font-size:12px;line-height:1.5}
.mm-branch>summary::-webkit-details-marker{display:none}
.mm-branch>summary::before{content:'▸';display:inline-block;margin-right:5px;color:var(--action-primary);transition:transform .15s var(--ease)}
.mm-branch[open]>summary::before{transform:rotate(90deg)}
.mm-branch>ul{margin:2px 0 0 12px;padding:0 0 0 8px;border-left:1px solid var(--border);list-style:none}
.mm-branch>ul>li{margin:2px 0}
.mm-leaf{color:var(--text-muted);font-size:12px;line-height:1.5}
</style>
