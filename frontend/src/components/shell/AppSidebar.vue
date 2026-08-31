<script setup>
import Icon from '../Icon.vue';
defineProps({ groups: Array, profile: Object });
</script>
<template>
  <aside class="workbench-nav">
    <router-link class="workbench-brand" to="/">
      <span class="brand-mark">SA</span>
      <span><strong>架构备考工作台</strong><small>LOCAL STUDY SYSTEM</small></span>
    </router-link>
    <nav v-for="g in groups" :key="g.label" class="nav-section">
      <span class="nav-label">{{ g.label }}</span>
      <router-link v-for="[path, icon, label] in g.items" :key="path" :to="path">
        <Icon :name="icon" :size="17" /><span>{{ label }}</span>
      </router-link>
    </nav>
    <div class="nav-profile"><span class="presence-dot"></span><div><b>{{ profile.certification }}</b><small>数据仅存储在本机</small></div></div>
  </aside>
</template>
