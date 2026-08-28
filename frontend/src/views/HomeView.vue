<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { http } from '../api/client';
const router = useRouter(); const data = ref(null); const err = ref(''); const loading = ref(false);
const meta = { review: ['到期复习', 'warn'], practice: ['针对练习', 'accent'], material: ['论文素材', 'ok'] };
async function load() { try { data.value = await http.get('/learning/dashboard'); err.value = ''; } catch (e) { err.value = e.message; } }
async function start(t) { loading.value = true; try { await http.post(`/learning/tasks/${t.id}/start`); const query = `task=${t.id}${t.target_id ? '&kp=' + t.target_id : ''}`; router.push(t.type === 'review' ? `/wrong?${query}` : t.type === 'material' ? `/essay?${query}` : `/practice?${query}`); } finally { loading.value = false; } }
async function replan(minutes) { await http.post('/learning/tasks/replan', { minutes }); await load(); }
onMounted(load);
</script>
<template>
  <p v-if="err" class="badge err">后端连接失败：{{ err }}</p>
  <template v-else-if="data">
    <div class="today-head"><div><div class="page-kicker">{{ data.date }} · 本地优先的学习工作台</div><h1>今天先做什么</h1><p class="muted">完成高价值任务；每次训练都会更新下一步建议。</p></div><div class="row"><button class="ghost" @click="replan(15)">15 分钟</button><button class="ghost" @click="replan(30)">30 分钟</button><button @click="replan(60)">重排 60 分钟</button></div></div>
    <div class="dashboard-grid"><section><div v-for="(t,index) in data.tasks" :key="t.id" class="task-card" :class="meta[t.type]?.[1]"><div class="task-index">{{ index + 1 }}</div><div class="task-body"><span class="badge" :class="meta[t.type]?.[1]">{{ meta[t.type]?.[0] }}</span><h2>{{ t.title }}</h2><p>{{ t.reason }}</p><small>{{ t.completion_hint }} · 预计 {{ t.estimated_minutes }} 分钟</small></div><button :disabled="loading" @click="start(t)">{{ t.status === 'in_progress' ? '继续任务' : '开始任务' }}</button></div></section><aside class="risk-panel"><h2>三科风险</h2><div v-for="r in data.risks" :key="r.subject" class="risk-row"><b>{{ r.name }}</b><span class="badge" :class="r.level === '高风险' ? 'err' : r.level === '临界' ? 'warn' : r.level === '安全' ? 'ok' : ''">{{ r.level }}</span><p>{{ r.evidence }}</p></div><router-link to="/stats">查看能力画像 →</router-link></aside></div>
    <div class="card"><h2>本周回顾</h2><p>已完成 {{ data.week.completed_tasks }} 项任务。{{ data.week.action }}</p><router-link to="/plan"><button class="ghost">查看学习计划</button></router-link></div>
  </template><div v-else class="card">正在加载今日学习建议…</div>
</template>
