<script setup>
import { onMounted, ref } from 'vue';
import { http } from '../api/client';
const list = ref([]);
const form = ref({ target: '', phase: '模拟' });
const examDate = ref('2026-11-14');
const genMsg = ref('');
const err = ref('');
async function load() {
  try { list.value = await http.get('/plans'); err.value = ''; }
  catch (e) { err.value = e.message; }
}
onMounted(load);
async function add() {
  if (!form.value.target) return;
  await http.post('/plans', form.value);
  form.value = { target: '', phase: '模拟' };
  load();
}
async function generate() {
  genMsg.value = '生成中…';
  try {
    const r = await http.post('/plans/generate', { exam_date: examDate.value });
    genMsg.value = '已生成 ' + r.created + ' 个阶段（共 ' + r.total_days + ' 天，考试日 ' + r.exam_date + '）';
    load();
  } catch (e) { genMsg.value = '失败：' + e.message; }
}
const phaseBadge = { 基础学习: 'accent', 真题精练: 'warn', 套卷模拟: 'ok', 错题冲刺: 'err' };
</script>
<template>
  <div class="card">
    <div class="toolbar">
      <b style="font-size:13px">四阶段计划</b>
      <span class="spacer"></span>
      <input type="date" v-model="examDate" style="width:150px" />
      <button class="sm" @click="generate">按考试日期自动生成</button>
    </div>
    <div class="list-panel" style="padding:0 14px 8px">
      <p v-if="genMsg" class="muted" style="margin:10px 0">{{ genMsg }}</p>
      <p v-if="err" class="badge err" style="margin:10px 0">{{ err }}</p>
      <table>
        <thead><tr><th style="width:110px">日期</th><th style="width:110px">阶段</th><th>任务</th><th style="width:86px">状态</th></tr></thead>
        <tbody>
          <tr v-for="p in list" :key="p.id">
            <td class="num muted">{{ (p.date || '').slice(0, 10) }}</td>
            <td><span class="badge" :class="phaseBadge[p.phase] || 'accent'">{{ p.phase }}</span></td>
            <td>{{ p.target }}</td>
            <td><span class="badge" :class="p.done ? 'ok' : 'warn'">{{ p.done ? '已完成' : '待完成' }}</span></td>
          </tr>
        </tbody>
      </table>
      <div class="empty" v-if="!list.length">还没有计划，点击上方按钮按考试日期自动生成。</div>
    </div>
  </div>
  <div class="card">
    <h2>添加任务</h2>
    <div class="row">
      <input v-model="form.target" placeholder="任务内容" style="flex:1" />
      <select v-model="form.phase"><option value="基础">基础</option><option value="精练">精练</option><option value="模拟">模拟</option><option value="冲刺">冲刺</option></select>
      <button @click="add">添加</button>
    </div>
  </div>
</template>
