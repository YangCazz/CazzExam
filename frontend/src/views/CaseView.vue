<script setup>
import { ref } from 'vue';
import BaseButton from '../components/base/BaseButton.vue';
import Icon from '../components/Icon.vue';
const stage = ref(0); const notes = ref('');
const prompts = ['我从题干中识别到的约束、角色和冲突：', '可得分的架构策略 / 设计要点：', '我的作答结构（先结论，再说明依据）：'];
function next() { stage.value = Math.min(3, stage.value + 1); }
</script>
<template>
  <section class="case-hero"><div><p class="eyebrow">CASE LAB / 结构化表达</p><h2>案例题不是背答案，<em>是把证据组织成答案。</em></h2><p>先标出题干证据，再列要点，最后对照参考答案复盘。</p></div><div class="case-steps"><span v-for="(n, i) in ['读题', '拆解', '作答', '复盘']" :key="n" :class="{ active: stage === i, done: stage > i }">{{ i + 1 }} {{ n }}</span></div></section>
  <section class="case-layout"><article class="panel case-source"><p class="eyebrow">练习画布</p><h3>{{ stage < 3 ? prompts[stage] : '复盘：下次更快地识别什么？' }}</h3><textarea v-model="notes" rows="12" placeholder="在这里写下你的思考。答案不会自动展示，先完成自己的推理。"></textarea><div class="row end"><BaseButton variant="ghost" @click="notes = ''">清空</BaseButton><BaseButton @click="next">{{ stage === 3 ? '保存为复盘' : '下一步' }}<Icon :name="stage === 3 ? 'check-circle' : 'arrow-right'" :size="14" /></BaseButton></div></article><aside class="panel scoring-guide"><p class="eyebrow">得分检查</p><h3>一份可评分答案应包含</h3><ol><li>结论直接回应问题</li><li>每个要点都有题干依据</li><li>技术词与场景相匹配</li><li>表达有层次、可检索</li></ol><p class="muted">下一版将接入案例题库与逐点自评；当前可先用此画布训练输出结构。</p></aside></section>
</template>
