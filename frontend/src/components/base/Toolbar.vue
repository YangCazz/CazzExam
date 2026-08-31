<script setup>
defineProps({ count: String });   // 右侧计数，放在 slot name="right" 之前
</script>
<template>
  <div class="toolbar">
    <slot />
    <span class="spacer"></span>
    <slot name="right">
      <span v-if="count" class="badge tone-accent">{{ count }}</span>
    </slot>
  </div>
</template>
