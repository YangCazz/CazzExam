<script setup>
defineProps({ eyebrow: String, title: String, subtitle: String });
</script>
<template>
  <header class="workbench-topbar">
    <div>
      <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
      <h1 v-if="title">{{ title }}</h1>
      <p v-if="subtitle" class="topbar-sub">{{ subtitle }}</p>
    </div>
    <div class="topbar-actions"><slot name="actions"></slot></div>
  </header>
</template>
