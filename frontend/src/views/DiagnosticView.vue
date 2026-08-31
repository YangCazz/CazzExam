<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { http } from '../api/client';
const router = useRouter(); const risks = ref([]); const started = ref(false);
const tracks = [
  ['综合知识', '20 分钟 · 15 道关键概念题', '用小样本找出优先知识域', '/practice'],
  ['案例分析', '25 分钟 · 1 道结构化拆题', '验证“读题—要点—表达”链路', '/case'],
  ['论文表达', '15 分钟 · 事实卡速写', '建立可复用的项目事实资产', '/essay'],
];
onMounted(async () => { try { risks.value = (await http.get('/learning/dashboard')).risks; } catch (_) {} });
function enter(path) { started.value = true; router.push(path); }
</script>
<template>
  <section class="diagnostic-intro"><div><p class="eyebrow">BASELINE / 约 60 分钟</p><h2>别凭感觉安排三科。<br><em>先拿到第一组证据。</em></h2><p>诊断不追求覆盖全部大纲，只用于确定当前最值得投入的一小段训练。</p></div><div class="diagnostic-rule"><span>诊断原则</span><b>先做，再看答案</b><p>结果用于调整计划，不做排名。</p></div></section>
  <section class="track-list"><article v-for="([title, time, desc, path], i) in tracks" :key="title" class="diagnostic-track"><span>0{{ i + 1 }}</span><div><p class="eyebrow">{{ time }}</p><h3>{{ title }}</h3><p>{{ desc }}</p></div><button @click="enter(path)">{{ started ? '继续' : '进入' }} →</button></article></section>
  <section class="panel diagnostic-evidence"><div><p class="eyebrow">已有信号</p><h2>现有学习记录</h2></div><div v-if="risks.length" class="evidence-grid"><div v-for="r in risks" :key="r.subject"><b>{{ r.name }}</b><span>{{ r.level }}</span><p>{{ r.evidence }}</p></div></div><p v-else class="muted">完成第一轮训练后，这里会显示基于作答记录的能力信号。</p></section>
</template>
