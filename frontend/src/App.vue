<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import AppSidebar from './components/shell/AppSidebar.vue';
import PageHeader from './components/shell/PageHeader.vue';
import CommandPalette from './components/CommandPalette.vue';
import { http } from './api/client';

const route = useRoute();
const profile = ref({ certification: '系统架构设计师', target_date: '' });
const pageMeta = computed(() => ({
  '/': ['学习总览', '从最有价值的一步开始'], '/diagnostic': ['学习诊断', '用一次小样本校准学习起点'], '/weekly': ['节奏规划', '围绕本周可投入时间排布任务'],
  '/knowledge': ['知识地图', '把大纲、薄弱点和训练串成一张图'], '/practice': ['综合练习', '选择一个知识点，完成一段刻意训练'], '/case': ['案例工作台', '拆题、列要点、复盘得分证据'],
  '/essay': ['论文工作台', '素材、项目事实与限时表达'], '/exam': ['模拟考试', '在完整约束下验证阶段能力'], '/review': ['复习队列', '先回忆，再核对，再安排下一次'],
  '/insights': ['能力画像', '以证据识别下一轮训练重点'], '/content': ['内容工作台', '题目、知识点与导入质量治理'], '/settings': ['偏好与数据', '目标、隐私和本地数据控制'],
}[route.path] || ['', '']));
const eyebrow = computed(() => `学习操作系统 / ${profile.value.certification}`);
const daysLeft = computed(() => !profile.value.target_date ? '未设置' : Math.max(0, Math.ceil((new Date(profile.value.target_date) - new Date()) / 86400000)));
const groups = [
  { label: '行动台', items: [['/', 'home', '学习总览'], ['/diagnostic', 'target', '学习诊断'], ['/weekly', 'calendar', '节奏规划']] },
  { label: '学习与训练', items: [['/knowledge', 'network', '知识地图'], ['/practice', 'book', '综合练习'], ['/case', 'case', '案例工作台'], ['/essay', 'essay', '论文工作台'], ['/exam', 'exam', '模拟考试']] },
  { label: '复盘与资产', items: [['/review', 'wrong', '复习队列'], ['/insights', 'chart', '能力画像']] },
  { label: '内容与设置', items: [['/content', 'database', '内容工作台'], ['/settings', 'gear', '偏好与数据']] },
];
const paletteOpen = ref(false);
const paletteItems = computed(() => groups.flatMap(group => group.items.map(([path, icon, label]) => ({ path, icon, label, group: group.label }))));
function onShortcut(event) { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); paletteOpen.value = !paletteOpen.value; } }
onMounted(async () => { window.addEventListener('keydown', onShortcut); try { profile.value = await http.get('/learning/profile'); } catch (_) {} });
onBeforeUnmount(() => window.removeEventListener('keydown', onShortcut));
</script>

<template>
  <div class="workbench-shell">
    <AppSidebar :groups="groups" :profile="profile" />
    <main class="workbench-main">
      <PageHeader :eyebrow="eyebrow" :title="pageMeta[0]" :subtitle="pageMeta[1]">
        <template #actions>
          <button class="command-trigger" title="快速导航 (Ctrl K)" @click="paletteOpen = true"><span>⌕</span> 快速导航 <kbd>⌘ K</kbd></button>
          <router-link to="/settings" class="deadline-chip"><span>目标日</span><b>{{ daysLeft === '未设置' ? '待设置' : `还有 ${daysLeft} 天` }}</b></router-link>
        </template>
      </PageHeader>
      <router-view :key="route.fullPath" />
    </main>
    <CommandPalette :open="paletteOpen" :items="paletteItems" @close="paletteOpen = false" />
  </div>
</template>
