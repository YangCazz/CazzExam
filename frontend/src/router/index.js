import { createRouter, createWebHistory } from 'vue-router';
const routes = [
  { path: '/', component: () => import('../views/HomeView.vue') }, { path: '/diagnostic', component: () => import('../views/DiagnosticView.vue') }, { path: '/weekly', component: () => import('../views/PlanView.vue') },
  { path: '/knowledge', component: () => import('../views/KnowledgeView.vue') }, { path: '/practice', component: () => import('../views/PracticeView.vue') }, { path: '/case', component: () => import('../views/CaseView.vue') },
  { path: '/essay', component: () => import('../views/EssayView.vue') }, { path: '/exam', component: () => import('../views/ExamView.vue') }, { path: '/review', component: () => import('../views/WrongView.vue') },
  { path: '/insights', component: () => import('../views/StatsView.vue') }, { path: '/content', component: () => import('../views/QuestionsView.vue') }, { path: '/settings', component: () => import('../views/SettingsView.vue') },
  { path: '/graph', component: () => import('../views/GraphView.vue') }, { path: '/questions', redirect: '/content' }, { path: '/wrong', redirect: '/review' }, { path: '/plan', redirect: '/weekly' }, { path: '/stats', redirect: '/insights' },
];
export default createRouter({ history: createWebHistory(), routes });
