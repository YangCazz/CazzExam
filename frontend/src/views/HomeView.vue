<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { http } from '../api/client';
const router = useRouter(); const data = ref(); const loading = ref(false); const error = ref('');
const labels = { review: ['复习队列', 'amber'], practice: ['针对训练', 'blue'], material: ['论文资产', 'jade'] };
const done = computed(() => data.value?.week?.completed_tasks || 0);
async function load() { try { data.value = await http.get('/learning/dashboard'); error.value = ''; } catch (e) { error.value = e.message; } }
async function begin(task) { loading.value = true; try { await http.post(`/learning/tasks/${task.id}/start`); const q = `task=${task.id}${task.target_id ? `&kp=${task.target_id}` : ''}`; router.push(task.type === 'review' ? `/review?${q}` : task.type === 'material' ? `/essay?${q}` : `/practice?${q}`); } finally { loading.value = false; } }
async function replan(minutes) { await http.post('/learning/tasks/replan', { minutes }); await load(); }
onMounted(load);
</script>
<template>
  <div v-if="error" class="notice error">学习服务暂不可用：{{ error }}</div>
  <template v-else-if="data">
    <section v-motion :initial="{ opacity: 0, y: 16 }" :enter="{ opacity: 1, y: 0, transition: { duration: 420 } }" class="command-hero"><div><p class="eyebrow">{{ data.date }} / 今日执行清单</p><h2>把有限时间，投向<br><em>下一步最值得做的事。</em></h2><p>不是刷得更多，而是用复习、训练和表达形成可验证的能力闭环。</p><div class="time-switch"><button class="ghost" @click="replan(15)">15 分钟</button><button class="ghost" @click="replan(30)">30 分钟</button><button @click="replan(60)">安排 60 分钟</button></div></div><div class="hero-orbit"><span>本周完成</span><b>{{ done }}</b><small>项学习动作</small><i></i></div></section>
    <div v-motion :initial="{ opacity: 0, y: 18 }" :enter="{ opacity: 1, y: 0, transition: { delay: 110, duration: 440 } }" class="overview-grid">
      <section class="panel task-panel"><div class="section-heading"><div><p class="eyebrow">NOW</p><h2>当前任务</h2></div><span class="muted">按收益排序</span></div>
        <article v-for="(task, index) in data.tasks" :key="task.id" class="priority-task"><span class="task-number">0{{ index + 1 }}</span><div class="task-copy"><span class="type-pill" :class="labels[task.type]?.[1]">{{ labels[task.type]?.[0] || '学习任务' }}</span><h3>{{ task.title }}</h3><p>{{ task.reason }}</p><small>{{ task.completion_hint }} · {{ task.estimated_minutes }} 分钟</small></div><button :disabled="loading" @click="begin(task)">{{ task.status === 'in_progress' ? '继续' : '开始' }} <span>→</span></button></article>
        <div v-if="!data.tasks.length" class="empty-state">今天没有待办。去做一次诊断，建立下一轮训练计划。</div>
      </section>
      <aside class="right-rail"><section class="panel risk-card"><div class="section-heading"><div><p class="eyebrow">SIGNALS</p><h2>三科风险</h2></div><router-link to="/insights">查看画像</router-link></div><div v-for="risk in data.risks" :key="risk.subject" class="signal-row"><span :class="['signal-dot', risk.level === '高风险' ? 'red' : risk.level === '临界' ? 'amber' : 'jade']"></span><div><b>{{ risk.name }}</b><p>{{ risk.evidence }}</p></div><span class="risk-level">{{ risk.level }}</span></div></section>
      <section class="panel next-card"><p class="eyebrow">NEXT MILESTONE</p><h3>先完成一轮小诊断</h3><p>用 20 分钟确认三科基线，再让系统推荐后续训练。</p><router-link class="text-link" to="/diagnostic">开始诊断 →</router-link></section></aside>
    </div>
  </template>
  <div v-else class="panel loading-state">正在为你计算今日最优学习路径…</div>
</template>
