<script setup>
import RiskRing from './RiskRing.vue';
defineProps({ risks: Array, loading: Boolean });
const dotClass = (level) => (level === '高风险' ? 'red' : level === '临界' ? 'amber' : level === '安全' ? 'jade' : '');
</script>
<template>
  <section class="panel risk-card">
    <div class="section-heading">
      <div><p class="eyebrow">SIGNALS</p><h2>备考风险概览</h2></div>
      <router-link to="/insights">查看画像</router-link>
    </div>
    <div v-if="loading" class="loading-state">正在评估三科基线…</div>
    <template v-else>
      <div class="risk-rings">
        <RiskRing v-for="r in risks" :key="'ring-' + r.subject" :name="r.name" :value="r.accuracy" :level="r.level" :answered="r.answered" />
      </div>
      <div class="risk-signals">
        <div v-for="r in risks" :key="'sig-' + r.subject" class="signal-row">
          <span :class="['signal-dot', dotClass(r.level)]"></span>
          <div><b>{{ r.name }}</b><p>{{ r.evidence }}</p></div>
          <span class="risk-level">{{ r.level }}</span>
        </div>
      </div>
    </template>
  </section>
</template>
<style scoped>
.risk-rings { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 6px 0 2px; border-bottom: 1px solid var(--border); }
.risk-signals { display: grid; gap: 2px; }
@media (max-width: 700px) { .risk-rings { gap: 4px; } }
</style>
