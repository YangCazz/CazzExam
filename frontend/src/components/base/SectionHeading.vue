<script setup>
defineProps({ eyebrow: String, title: String, subtitle: String });
</script>
<template>
  <div class="section-heading">
    <div>
      <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
      <h2 v-if="title">{{ title }}</h2>
      <p v-if="subtitle" class="topbar-sub">{{ subtitle }}</p>
    </div>
    <slot name="action"></slot>
  </div>
</template>
