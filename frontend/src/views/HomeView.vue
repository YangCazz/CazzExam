<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { http } from '../api/client';
import Card from '../components/base/Card.vue';
import SectionHeading from '../components/base/SectionHeading.vue';
import EmptyState from '../components/base/EmptyState.vue';
import BaseButton from '../components/base/BaseButton.vue';
import Icon from '../components/Icon.vue';
import DashboardHero from '../components/home/DashboardHero.vue';
import TaskCard from '../components/home/TaskCard.vue';
import RiskOverview from '../components/home/RiskOverview.vue';
import WeekReview from '../components/home/WeekReview.vue';

const router = useRouter();
const data = ref(null);          // dashboard
const trend = ref([]);           // /stats/trend
const weakKps = ref([]);         // /plans/today -> weak_kps
const loading = ref(false);      // 启动任务中
const error = ref('');
const done = computed(() => data.value?.week?.completed_tasks || 0);

async function load() {
  error.value = '';
  try { data.value = await http.get('/learning/dashboard'); } catch (e) { error.value = e.message; }
  try { trend.value = await http.get('/stats/trend?days=14'); } catch (_) {}
  try { const p = await http.get('/plans/today'); weakKps.value = p.weak_kps || []; } catch (_) {}
}
async function begin(task) {
  loading.value = true;
  try {
    await http.post(`/learning/tasks/${task.id}/start`);
    const q = `task=${task.id}${task.target_id ? `&kp=${task.target_id}` : ''}`;
    router.push(task.type === 'review' ? `/review?${q}` : task.type === 'material' ? `/essay?${q}` : `/practice?${q}`);
  } finally { loading.value = false; }
}
async function replan(minutes) { await http.post('/learning/tasks/replan', { minutes }); await load(); }
onMounted(load);
</script>
<template>
  <div v-if="error" class="notice error">学习服务暂不可用：{{ error }}</div>
  <template v-else-if="data">
    <DashboardHero :date="data.date" :done="done" :replan="replan" :loading="loading" />

    <div class="overview-grid">
      <Card class="task-panel">
        <SectionHeading eyebrow="NOW" title="当前任务">
          <template #action><span class="muted">按收益排序</span></template>
        </SectionHeading>
        <template v-if="data.tasks.length">
          <TaskCard v-for="(task, i) in data.tasks" :key="task.id" :index="i" :type="task.type"
                    :title="task.title" :reason="task.reason" :hint="task.completion_hint"
                    :minutes="task.estimated_minutes" :status="task.status"
                    :loading="loading" :on-start="() => begin(task)" />
        </template>
        <EmptyState v-else icon="target" title="今天没有待办" description="去做一次诊断，建立下一轮训练计划。" action-text="开始诊断" to="/diagnostic" />
      </Card>

      <aside class="right-rail">
        <RiskOverview :risks="data.risks" />
        <section class="panel next-card">
          <p class="eyebrow">NEXT MILESTONE</p>
          <h3>先完成一轮小诊断</h3>
          <p>用 20 分钟确认三科基线，再让系统推荐后续训练。</p>
          <BaseButton :to="'/diagnostic'" variant="ghost" block icon="target">开始诊断</BaseButton>
        </section>
      </aside>
    </div>

    <WeekReview :week="data.week" :trend="trend" :weak-kps="weakKps" />
  </template>
  <div v-else class="panel loading-state">正在为你计算今日最优学习路径…</div>
</template>
