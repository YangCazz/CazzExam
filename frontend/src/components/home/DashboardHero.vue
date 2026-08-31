<script setup>
import BaseButton from '../base/BaseButton.vue';
defineProps({ date: String, done: { type: Number, default: 0 }, replan: Function, loading: Boolean });
</script>
<template>
  <section class="command-hero">
    <div>
      <p class="eyebrow">{{ date }} / 今日执行清单</p>
      <h2>把有限时间，投向<em>下一步最值得做的事。</em></h2>
      <p>不是刷得更多，而是用复习、训练和表达形成可验证的能力闭环。</p>
      <div class="time-switch">
        <BaseButton variant="ghost" size="sm" :disabled="loading" @click="replan && replan(15)">15 分钟</BaseButton>
        <BaseButton variant="ghost" size="sm" :disabled="loading" @click="replan && replan(30)">30 分钟</BaseButton>
        <BaseButton size="sm" :disabled="loading" @click="replan && replan(60)">安排 60 分钟</BaseButton>
      </div>
    </div>
    <div class="hero-stat"><b>{{ done }}</b><span>本周完成学习动作</span></div>
  </section>
</template>
