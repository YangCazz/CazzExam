<script setup>
// 状态胶囊：text 必填（状态必须配文字），tone ok|warn|err|accent|neutral。
defineProps({
  tone: { type: String, default: 'neutral' },
  text: { type: String, required: true },
});
</script>
<template>
  <span class="badge" :class="'tone-' + tone">{{ text }}</span>
</template>
<style scoped>
.badge.tone-ok { background: var(--ok-dim); color: var(--status-success); border: 1px solid rgba(77,178,129,.26); }
.badge.tone-warn { background: var(--warn-dim); color: var(--status-warning); border: 1px solid rgba(201,161,61,.26); }
.badge.tone-err { background: var(--err-dim); color: var(--risk-high); border: 1px solid rgba(207,106,104,.26); }
.badge.tone-accent { background: var(--action-soft); color: var(--action-primary-hover); border: 1px solid rgba(91,140,255,.24); }
.badge.tone-neutral { background: var(--surface); color: var(--text-muted); border: 1px solid var(--border); }
</style>
