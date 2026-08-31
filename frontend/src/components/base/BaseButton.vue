<script setup>
import { computed } from 'vue';
import Icon from '../Icon.vue';
const props = defineProps({
  to: { type: [String, Object], default: null },        // 传入则渲染为 <router-link>
  variant: { type: String, default: 'primary' },        // primary | ghost | danger | subtle
  size: { type: String, default: 'md' },                // sm | md
  disabled: Boolean, loading: Boolean, block: Boolean,
  icon: { type: String, default: '' },
  iconSize: { type: Number, default: 16 },
});
const tag = computed(() => (props.to ? 'router-link' : 'button'));
const cls = computed(() => [
  'btn',
  ...(props.variant !== 'primary' ? [props.variant] : []),
  ...(props.size !== 'md' ? [props.size] : []),
  { 'is-block': props.block, 'is-loading': props.loading },
]);
</script>
<template>
  <component :is="tag" :to="to" :class="cls" :disabled="tag === 'button' && (disabled || loading)" :aria-busy="loading">
    <span v-if="loading" class="btn-spinner" aria-hidden="true"></span>
    <Icon v-else-if="icon" :name="icon" :size="iconSize" />
    <slot />
  </component>
</template>
<style scoped>
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; text-align: center; }
.btn.subtle { background: var(--surface); border-color: var(--border); color: var(--text-muted); }
.btn.subtle:hover { background: var(--surface-hover); color: var(--text); }
.is-block { width: 100%; }
.btn-spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.4); border-top-color: #fff; border-radius: 50%; animation: btn-spin .7s linear infinite; }
@keyframes btn-spin { to { transform: rotate(360deg) } }
</style>
