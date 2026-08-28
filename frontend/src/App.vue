<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Icon from './components/Icon.vue';
const route = useRoute();
const pageMeta = computed(() => {
  const map = {
    '/': { title: '学习总览', sub: '今日任务与学习数据一览' },
    '/knowledge': { title: '知识库', sub: '章-节-知识点 · 点击查看详情与关联' },
    '/practice': { title: '练习模式', sub: '知识点 → 关联例题 → 即时反馈' },
    '/graph': { title: '知识图谱', sub: '知识点串联 · 薄弱点自动标红' },
    '/questions': { title: '题库', sub: '录入 · 检索 · 批量导入' },
    '/exam': { title: '模拟考试', sub: '三科限时全真模拟 · 自动判分' },
    '/wrong': { title: '错题本', sub: '错因归因 · 反思 · SM-2 间隔复习' },
    '/plan': { title: '学习计划', sub: '按 2026-11 考试日期倒推' },
    '/stats': { title: '统计画像', sub: '趋势 · 错因分布 · 薄弱知识点' },
    '/essay': { title: '论文专项', sub: '限时写作 · 素材库 · ADR · AI 批改' },
    '/settings': { title: '设置', sub: 'AI 网关 · 数据导出 · 系统信息' },
  };
  return map[route.path] || { title: '', sub: '' };
});
const daysLeft = computed(() => {
  const target = new Date('2026-11-14T00:00:00');
  const now = new Date();
  return Math.max(0, Math.ceil((target - now) / 86400000));
});
const groups = [
  { label: '学习', items: [['/', 'home', '总览'], ['/knowledge', 'book', '知识库'], ['/practice', 'target', '练习模式'], ['/graph', 'network', '知识图谱']] },
  { label: '考试与数据', items: [['/questions', 'database', '题库'], ['/exam', 'exam', '模拟考试'], ['/wrong', 'wrong', '错题本'], ['/stats', 'chart', '统计']] },
  { label: '写作与系统', items: [['/plan', 'calendar', '学习计划'], ['/essay', 'essay', '论文专项'], ['/settings', 'gear', '设置']] },
];
</script>
<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-logo">📚</div>
        <div>
          <div class="brand-title">软考·架构师备考</div>
          <div class="brand-sub">2026 · 系统架构设计师</div>
        </div>
      </div>
      <template v-for="g in groups" :key="g.label">
        <div class="nav-group">{{ g.label }}</div>
        <router-link v-for="[path, icon, label] in g.items" :key="path" :to="path">
          <Icon :name="icon" class="nav-ico" />
          <span>{{ label }}</span>
        </router-link>
      </template>
      <div class="sidebar-foot">数据本地存储 · 自动备份</div>
    </aside>
    <main class="main">
      <header class="topbar">
        <div>
          <div class="page-title">{{ pageMeta.title }}</div>
          <div class="page-sub">{{ pageMeta.sub }}</div>
        </div>
        <div class="page-actions">
          <span class="badge accent">距 2026-11 考试 · {{ daysLeft }} 天</span>
        </div>
      </header>
      <router-view v-slot="{ Component }">
        <transition name="fade">
          <component :is="Component" :key="route.fullPath" />
        </transition>
      </router-view>
    </main>
  </div>
</template>
