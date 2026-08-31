<script setup>
import { computed, nextTick, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
const props = defineProps({ open: Boolean, items: { type: Array, default: () => [] } });
const emit = defineEmits(['close']); const router = useRouter(); const query = ref(''); const input = ref(null);
const results = computed(() => props.items.filter(item => item.label.includes(query.value.trim()) || item.group.includes(query.value.trim())).slice(0, 8));
watch(() => props.open, async visible => { if (visible) { query.value = ''; await nextTick(); input.value?.focus(); } });
function go(item) { router.push(item.path); emit('close'); }
function keydown(e) { if (e.key === 'Escape') emit('close'); if (e.key === 'Enter' && results.value[0]) go(results.value[0]); }
</script>
<template>
  <teleport to="body"><div v-if="open" class="command-backdrop" @mousedown.self="emit('close')"><section v-motion :initial="{ opacity: 0, y: -12, scale: .98 }" :enter="{ opacity: 1, y: 0, scale: 1, transition: { duration: 180 } }" class="command-palette" role="dialog" aria-modal="true" aria-label="快速导航"><div class="command-input"><span>⌕</span><input ref="input" v-model="query" placeholder="搜索页面或动作…" @keydown="keydown" /><kbd>ESC</kbd></div><div class="command-results"><button v-for="item in results" :key="item.path" @click="go(item)"><span><small>{{ item.group }}</small><b>{{ item.label }}</b></span><i>↵</i></button><p v-if="!results.length">没有匹配项</p></div><footer><span>↑↓ 选择</span><span>↵ 打开</span><span>⌘K 关闭</span></footer></section></div></teleport>
</template>
