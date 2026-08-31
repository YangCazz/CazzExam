<script setup>
import { onMounted, ref } from 'vue';
import { http } from '../api/client';
import BaseButton from '../components/base/BaseButton.vue';
const data = ref(); const minutes = ref(240); const saving = ref(false);
async function load() { try { data.value = await http.get('/learning/dashboard'); minutes.value = data.value.profile.weekly_minutes; } catch (_) {} }
async function update() { saving.value = true; try { await http.put('/learning/profile', { weekly_minutes: Number(minutes.value) }); await http.post('/learning/tasks/replan', { minutes: Math.round(Number(minutes.value) / 5) }); await load(); } finally { saving.value = false; } }
onMounted(load);
</script>
<template>
  <section class="planning-hero"><div><p class="eyebrow">WEEKLY RHYTHM</p><h2>计划应该适配你的生活，<br><em>不是让你追赶一张表。</em></h2><p>设置真实的每周可用时间，系统会将复习优先级转成今天能完成的动作。</p></div><div class="time-budget"><label>本周可投入时间</label><div><input v-model.number="minutes" type="number" min="60" step="30" /><b>分钟</b></div><BaseButton :loading="saving" icon="restart" @click="update">更新节奏</BaseButton></div></section>
  <section v-if="data" class="weekly-columns"><div class="panel"><p class="eyebrow">THIS WEEK</p><h2>本周的学习承诺</h2><div class="commitment"><b>{{ data.week.completed_tasks }}</b><span>已完成动作</span></div><p>{{ data.week.action }}</p><div class="week-meter"><i :style="{ width: Math.min(100, data.week.completed_tasks * 20) + '%' }"></i></div></div><div class="panel"><p class="eyebrow">RULES</p><h2>调度规则</h2><ul class="plain-list"><li><span>01</span> 到期复习优先于新增练习</li><li><span>02</span> 风险最高的科目获得下一个练习位</li><li><span>03</span> 没有学习证据时，先做小诊断</li></ul></div></section>
  <section class="panel"><p class="eyebrow">WEEKLY REVIEW</p><h2>周末回顾模板</h2><div class="review-prompts"><div><b>保留</b><p>这周哪种学习动作真正有效？</p></div><div><b>停止</b><p>什么事情花了时间却没有留下证据？</p></div><div><b>调整</b><p>下周要优先解决哪个具体问题？</p></div></div></section>
  <div v-if="!data" class="panel loading-state">正在读取你的学习节奏…</div>
</template>
