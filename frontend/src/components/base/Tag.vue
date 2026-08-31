<script setup>
defineProps({
  tone: { type: String, default: 'neutral' },  // neutral | accent | success | warning | danger | violet
  text: String,
});
</script>
<template>
  <span class="tag" :class="'tone-' + tone"><slot>{{ text }}</slot></span>
</template>
<style scoped>
.tag.tone-accent { background: var(--action-soft); color: var(--action-primary-hover); border-color: rgba(91,140,255,.24); }
.tag.tone-success { background: var(--ok-dim); color: var(--status-success); border-color: rgba(77,178,129,.26); }
.tag.tone-warning { background: var(--warn-dim); color: var(--status-warning); border-color: rgba(201,161,61,.26); }
.tag.tone-danger { background: var(--err-dim); color: var(--risk-high); border-color: rgba(207,106,104,.26); }
.tag.tone-violet { background: var(--action-secondary-soft); color: var(--action-secondary); border-color: rgba(122,107,176,.26); }
</style>
