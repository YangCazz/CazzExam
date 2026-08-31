<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { http } from '../api/client';
import BaseButton from '../components/base/BaseButton.vue';
import Icon from '../components/Icon.vue';
const queue = ref([]); const summary = ref({ by_status: {} }); const active = ref(0); const revealed = ref(false); const reflection = ref(''); const errorType = ref('理解偏差'); const error = ref('');
const current = computed(() => queue.value[active.value]);
async function load() { try { const [q, s] = await Promise.all([http.get('/wrong/queue'), http.get('/wrong/summary')]); queue.value = q; summary.value = s; active.value = 0; revealed.value = false; } catch (e) { error.value = e.message; } }
async function grade(quality) { const w = current.value; if (!w) return; await http.put(`/wrong/${w.id}`, { error_type: errorType.value, reflection: reflection.value }); await http.post(`/wrong/${w.id}/review`, { quality }); reflection.value = ''; await load(); }
onMounted(load);
</script>
<template>
  <section class="review-header"><div><p class="eyebrow">SPACED REVIEW / {{ queue.length }} ITEMS</p><h2>先回忆，<em>再获得反馈。</em></h2><p>把“看懂了解析”变成一次可以被验证的主动提取。</p></div><div class="review-stats"><span>待复习 <b>{{ summary.by_status.new || 0 }}</b></span><span>巩固中 <b>{{ summary.by_status.reviewing || 0 }}</b></span><span>已掌握 <b>{{ summary.by_status.mastered || 0 }}</b></span></div></section>
  <section v-if="current" class="review-layout"><article class="panel recall-card"><div class="recall-top"><span class="type-pill amber">待回忆</span><span>第 {{ active + 1 }} / {{ queue.length }} 题</span></div><p class="question-stem">{{ current.question?.stem }}</p><div v-if="current.question?.qtype === 'choice'" class="recall-options"><span v-for="opt in current.question.options" :key="opt">{{ opt }}</span></div><textarea v-model="reflection" rows="4" placeholder="不要急着看答案：先写下你认为的答案或解题依据。"></textarea><div v-if="!revealed" class="row end"><BaseButton @click="revealed = true">我已完成回忆，查看反馈<Icon name="arrow-right" :size="14" /></BaseButton></div><div v-else class="answer-reveal"><p>参考答案 <b>{{ current.question?.answer }}</b></p><p class="muted">{{ current.question?.analysis || '此题暂无解析，请记录自己的正确思路。' }}</p></div></article>
    <aside class="panel review-decision"><p class="eyebrow">DECISION</p><h3>这次回忆的质量？</h3><p>评价的是“无需提示能否提取”，不是做题时的感觉。</p><label>主要错因<select v-model="errorType"><option>知识性错误</option><option>理解偏差</option><option>审题失误</option><option>方法错误</option><option>其他</option></select></label><BaseButton variant="ghost" :disabled="!revealed" @click="grade(0)">没想起来 · 明天再见</BaseButton><BaseButton variant="ghost" :disabled="!revealed" @click="grade(3)">模糊但可恢复 · 稍后复习</BaseButton><BaseButton :disabled="!revealed" @click="grade(5)">清楚回忆 · 拉长间隔</BaseButton></aside></section>
  <section v-else class="panel empty-review"><p class="eyebrow">INBOX ZERO</p><h2>当前没有到期复习。</h2><p>下一次练习中答错的题目会自动进入此处，按间隔重复安排。</p><BaseButton :to="'/practice'" icon="target">去做一段针对训练</BaseButton></section>
  <p v-if="error" class="notice error">{{ error }}</p>
</template>
