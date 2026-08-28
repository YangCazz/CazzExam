import { createRouter, createWebHistory } from 'vue-router';
const routes = [
  { path: '/', component: () => import('../views/HomeView.vue') },
  { path: '/knowledge', component: () => import('../views/KnowledgeView.vue') },
  { path: '/practice', component: () => import('../views/PracticeView.vue') },
  { path: '/graph', component: () => import('../views/GraphView.vue') },
  { path: '/questions', component: () => import('../views/QuestionsView.vue') },
  { path: '/exam', component: () => import('../views/ExamView.vue') },
  { path: '/wrong', component: () => import('../views/WrongView.vue') },
  { path: '/plan', component: () => import('../views/PlanView.vue') },
  { path: '/stats', component: () => import('../views/StatsView.vue') },
  { path: '/essay', component: () => import('../views/EssayView.vue') },
  { path: '/settings', component: () => import('../views/SettingsView.vue') },
];
export default createRouter({ history: createWebHistory(), routes });
