<script setup>
import { onMounted, ref } from 'vue';
import { http } from '../api/client';
const list = ref([]);
const err = ref('');
const f = ref({ qtype: '', subject: '' });
const form = ref({ qtype: 'choice', subject: 1, stem: '', options: '', answer: '', analysis: '', source_year: null, source_type: 'self', knowledge_ids: '' });
const qtypes = { choice: '单选', case: '案例', essay: '论文' };
const subjects = { 1: '综合知识', 2: '案例分析', 3: '论文' };
async function load() {
  try {
    let q = '?limit=200';
    if (f.value.qtype) q += '&qtype=' + f.value.qtype;
    if (f.value.subject) q += '&subject=' + f.value.subject;
    list.value = await http.get('/questions' + q);
    err.value = '';
  } catch (e) { err.value = e.message; }
}
onMounted(load);
async function add() {
  const payload = { ...form.value };
  payload.options = form.value.options ? form.value.options.split('\n').filter(Boolean) : [];
  payload.knowledge_ids = form.value.knowledge_ids ? form.value.knowledge_ids.split(',').map(Number) : [];
  payload.answer = form.value.answer;
  payload.source_year = form.value.source_year ? Number(form.value.source_year) : null;
  await http.post('/questions', payload);
  form.value = { qtype: 'choice', subject: 1, stem: '', options: '', answer: '', analysis: '', source_year: null, source_type: 'self', knowledge_ids: '' };
  load();
}
function qtypeBadge(qt) { return { choice: 'accent', case: 'warn', essay: 'ok' }[qt] || ''; }
</script>
<template>
  <div class="card">
    <div class="toolbar">
      <select v-model="f.qtype" style="width:110px"><option value="">全部题型</option><option value="choice">单选</option><option value="case">案例</option><option value="essay">论文</option></select>
      <select v-model="f.subject" style="width:130px"><option value="">全部科目</option><option value="1">综合知识</option><option value="2">案例分析</option><option value="3">论文</option></select>
      <button class="ghost sm" @click="load">查询</button>
      <span class="spacer"></span>
      <span class="badge accent">{{ list.length }} 题</span>
    </div>
    <div class="list-panel" style="padding:0 14px 8px">
      <p v-if="err" class="badge err" style="margin:10px 0">{{ err }}</p>
      <table>
        <thead><tr><th style="width:52px">ID</th><th style="width:84px">题型</th><th>题干</th><th style="width:96px">科目</th><th style="width:64px">难度</th><th style="width:70px">年份</th><th style="width:80px">来源</th></tr></thead>
        <tbody>
          <tr v-for="q in list" :key="q.id">
            <td class="num muted">{{ q.id }}</td>
            <td><span class="badge" :class="qtypeBadge(q.qtype)">{{ qtypes[q.qtype] || q.qtype }}</span></td>
            <td class="stem-clamp">{{ q.stem }}</td>
            <td class="muted">{{ subjects[q.subject] || q.subject }}</td>
            <td class="num">{{ q.difficulty }}</td>
            <td class="num muted">{{ q.source_year || '—' }}</td>
            <td><span class="tag">{{ q.source_type }}</span></td>
          </tr>
        </tbody>
      </table>
      <div class="empty" v-if="!list.length && !err">暂无题目，用下方表单录入或用「批量导入」。</div>
    </div>
  </div>

  <div class="card">
    <h2>新增题目</h2>
    <div class="row">
      <select v-model="form.qtype"><option value="choice">单选</option><option value="case">案例</option><option value="essay">论文</option></select>
      <select v-model.number="form.subject"><option :value="1">综合知识</option><option :value="2">案例分析</option><option :value="3">论文</option></select>
      <input v-model="form.source_year" placeholder="真题年份(可选)" style="width:120px" />
      <input v-model="form.knowledge_ids" placeholder="知识点ID(逗号分隔)" style="width:180px" />
    </div>
    <div><textarea v-model="form.stem" rows="3" placeholder="题干" style="width:100%"></textarea></div>
    <div v-if="form.qtype === 'choice'"><textarea v-model="form.options" rows="3" placeholder="选项，每行一个（A. xxx / B. xxx …）" style="width:100%"></textarea></div>
    <div><textarea v-model="form.answer" rows="1" placeholder="答案（单选填选项字母；案例/论文填参考答案要点）" style="width:100%"></textarea></div>
    <div><textarea v-model="form.analysis" rows="2" placeholder="解析" style="width:100%"></textarea></div>
    <button @click="add">保存题目</button>
  </div>
</template>
