<script setup>
// 统一面板表面。父组件可用 class 透传（inheritAttrs），如 <Card class="risk-card">。
defineProps({ as: { type: String, default: 'section' } });
</script>
<template>
  <component :is="as" class="panel"><slot /></component>
</template>
