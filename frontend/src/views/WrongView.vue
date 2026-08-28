<script setup>
import { onMounted, ref, reactive, computed } from 'vue';
import { http } from '../api/client';
const tab = ref('queue');
const queue = ref([]);
const all = ref([]);
const mastered = ref([]);
const summary = ref({ by_status: {} });
const showAns = reactive({});
const forms = reactive({});
const err = ref('');

const errorTypes = ['知识性错误', '理解偏差', '审题失误', '方法错误', '其他'];
const statusNames = { new: '待复习', reviewing: '复习中', mastered: '已掌握' };

async function load() {
  try {
    const [q, s] = await Promise.all([http.get('/wrong/queue'), http.get('/wrong/summary')]);
    queue.value = q; summary.value = s;
    for (const w of q) {
      if (!forms[w.id]) forms[w.id] = { error_type: w.error_type, reflection: w.reflection };
    }
    err.value = '';
  } catch (e) { err.value = e.message; }
}
async function loadTab() {
  try {
    if (tab.value === 'all') all.value = await http.get('/wrong');
    if (tab.value === 'mastered') mastered.value = await http.get('/wrong?status=mastered');
  } catch (e) { err.value = e.message; }
}
onMounted(() => { load(); loadTab(); });

async function saveAttribution(w) {
  const f = forms[w.id];
  await http.put('/wrong/' + w.id, { error_type: f.error_type, reflection: f.reflection });
  load();
}
async function review(w, quality) {
  await http.post('/wrong/' + w.id + '/review', { quality });
  load();
}
async function switchTab(t) { tab.value = t; loadTab(); }
const queueCount = computed(() => queue.value.length);
</script>
<template>
  <div class="card">
    <div class="row" style="justify-content:space-between">
      <h2 style="margin:0">错题本</h2>
      <div class="row">
        <span class="badge err">待复习 {{ summary.by_status.new || 0 }}</span>
        <span class="badge warn">复习中 {{ summary.by_status.reviewing || 0 }}</span>
        <span class="badge ok">已掌握 {{ summary.by_status.mastered || 0 }}</span>
      </div>
    </div>
    <div class="row" style="margin:10px 0">
      <button :class="tab === 'queue' ? '' : 'ghost'" @click="switchTab('queue')">复习队列 ({{ queueCount }})</button>
      <button :class="tab === 'all' ? '' : 'ghost'" @click="switchTab('all')">全部错题</button>
      <button :class="tab === 'mastered' ? '' : 'ghost'" @click="switchTab('mastered')">已掌握</button>
    </div>
    <p v-if="err" class="badge err">{{ err }}</p>
  </div>

  <!-- 复习队列 -->
  <template v-if="tab === 'queue'">
    <div class="card" v-for="w in queue" :key="w.id">
      <div class="q-box" v-if="w.question">
        <div class="stem">{{ w.question.stem }}</div>
        <template v-if="w.question.qtype === 'choice'">
          <div v-for="opt in w.question.options" :key="opt" class="opt">{{ opt }}</div>
        </template>
        <div class="row" style="margin-top:8px">
          <span class="tag" v-for="k in w.question.knowledge" :key="k.id">{{ k.name }}</span>
          <button class="ghost" @click="showAns[w.id] = !showAns[w.id]">{{ showAns[w.id] ? '隐藏答案' : '查看答案' }}</button>
        </div>
        <div v-if="showAns[w.id]" style="margin-top:8px">
          <p>正确答案：<span class="badge ok">{{ w.question.answer }}</span></p>
          <p class="muted" v-if="w.question.analysis">解析：{{ w.question.analysis }}</p>
        </div>
      </div>
      <!-- 归因向导 -->
      <div style="margin-top:10px">
        <b>错因归因（反思三问：当时怎么想的 / 正确思路 / 下次怎么避免）</b>
        <div class="row">
          <select v-for="et in errorTypes" :key="et" :value="et" style="display:none"></select>
          <select v-model="forms[w.id].error_type">
            <option v-for="et in errorTypes" :key="et" :value="et">{{ et }}</option>
          </select>
          <textarea v-model="forms[w.id].reflection" rows="2" placeholder="写反思…" style="flex:1"></textarea>
          <button @click="saveAttribution(w)">保存归因</button>
        </div>
        <div class="row" style="margin-top:8px">
          <span class="muted">自评回忆质量：</span>
          <button class="ghost" @click="review(w, 0)">忘了(0)</button>
          <button class="ghost" @click="review(w, 3)">模糊(3)</button>
          <button @click="review(w, 5)">记住了(5)</button>
        </div>
      </div>
    </div>
    <div class="card" v-if="!queue.length && !err">
      <p class="muted">复习队列为空，太棒了！去「模拟考试」继续刷题吧。</p>
    </div>
  </template>

  <!-- 全部/已掌握 -->
  <template v-else>
    <div class="card">
      <table>
        <tr><th>ID</th><th>题目ID</th><th>错因</th><th>状态</th><th>重复次数</th><th>下次复习</th><th>反思</th></tr>
        <tr v-for="w in (tab === 'all' ? all : mastered)" :key="w.id">
          <td>{{ w.id }}</td><td>{{ w.question_id }}</td>
          <td>{{ w.error_type || '未归因' }}</td>
          <td>{{ statusNames[w.status] || w.status }}</td>
          <td>{{ w.repetition }}</td>
          <td>{{ w.next_review_at ? w.next_review_at.slice(0, 10) : '—' }}</td>
          <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ w.reflection || '—' }}</td>
        </tr>
      </table>
    </div>
  </template>
</template>
