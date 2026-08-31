<script setup>
import { onMounted, ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { http } from '../api/client';
import BaseButton from '../components/base/BaseButton.vue';
import Icon from '../components/Icon.vue';
const route = useRoute();
const taskId = Number(route.query.task || 0);
const tree = ref([]);
const err = ref('');
const view = ref('pick');            // pick | practice | result
const session = ref(null);           // { kpId, kpName, questions, idx, answers:{}, results:{} }

function indent(p) { return p.code ? (p.code.split('.').length - 1) : 0; }
async function loadTree() {
  tree.value = await http.get('/knowledge/tree');
}
async function startWithKp(kpId) {
  err.value = '';
  const d = await http.get('/knowledge/points/' + kpId);
  if (!d.questions.length) { err.value = '该知识点暂无关联题目，请先在「题库」录题时关联知识点'; return; }
  const qids = new Set(d.questions.map(x => x.id));
  const all = await http.get('/questions?limit=500');
  const picked = all.filter(q => qids.has(q.id) && (q.qtype === 'choice' || q.qtype === 'case'));
  if (!picked.length) { err.value = '该知识点暂无练习题（单选/案例），请先录入'; return; }
  session.value = { kpId, kpName: d.name, questions: picked, idx: 0, answers: {}, results: {} };
  view.value = 'practice';
}
const current = computed(() => session.value ? session.value.questions[session.value.idx] : null);
const stats = computed(() => {
  if (!session.value) return { answered: 0, correct: 0, wrongs: [] };
  const results = Object.values(session.value.results);
  const answered = results.length;
  const correct = results.filter(r => r.is_correct).length;
  const wrongs = session.value.questions
    .filter(q => session.value.results[q.id] && !session.value.results[q.id].is_correct && q.qtype === 'choice')
    .map(q => ({ question_id: q.id, stem: q.stem, answer: session.value.answers[q.id] || '', ...session.value.results[q.id] }));
  return { answered, correct, wrongs };
});
async function check() {
  if (!current.value || !selected()) return;
  const ans = selected();
  const r = await http.post('/questions/check', { question_id: current.value.id, user_answer: ans });
  session.value.answers[current.value.id] = ans;
  session.value.results[current.value.id] = { is_correct: r.is_correct, correct_answer: r.correct_answer, reference: r.reference, analysis: r.analysis };
}
function selected() { return session.value ? session.value.answers[session.value.questions[session.value.idx].id] : ''; }
function goTo(i) { if (i >= 0 && i < session.value.questions.length) session.value.idx = i; }
function next() {
  if (session.value.idx < session.value.questions.length - 1) { session.value.idx += 1; }
  else { view.value = 'result'; if (taskId) http.post('/learning/tasks/' + taskId + '/complete'); }
}
function restart() { startWithKp(session.value.kpId); }
function backToPick() { view.value = 'pick'; session.value = null; loadTree(); }
const qtypeName = (q) => q.qtype === 'choice' ? '单选题' : '案例分析';
onMounted(async () => {
  await loadTree();
  if (route.query.kp) startWithKp(Number(route.query.kp));
});
</script>
<template>
  <!-- 知识点选择 -->
  <div class="card" v-if="view === 'pick'">
    <div class="toolbar">
      <b class="tb-title">选择知识点</b>
      <span class="spacer"></span>
      <span class="badge accent">{{ tree.length }} 个知识点</span>
    </div>
    <div class="list-panel">
      <p v-if="err" class="badge err err-inline">{{ err }}</p>
      <p class="muted pick-hint">点选知识点开始练习：做关联题 → 即时判分 → 答错自动进错题本。</p>
      <div v-for="p in tree" :key="p.id" class="tree-row" @click="startWithKp(p.id)">
        <span class="tree-guide" v-for="i in indent(p)" :key="i"></span>
        <span class="tree-dot"></span>
        <span class="tcell">
          <span class="tcell-main">{{ p.name }}</span>
          <span class="tcell-sub" v-if="p.code"> · {{ p.code }}</span>
        </span>
        <span class="num muted tree-num">{{ Math.round(p.mastery) }}%</span>
        <BaseButton size="sm" variant="ghost" icon="practice" @click.stop="startWithKp(p.id)">练习</BaseButton>
      </div>
    </div>
  </div>

  <!-- 练习中 -->
  <div class="card" v-if="view === 'practice' && session && current">
    <div class="row q-head">
      <div>
        <b class="kp-name">{{ session.kpName }}</b>
        <span class="badge accent q-badge">{{ qtypeName(current) }}</span>
      </div>
      <span class="badge ok">答对 {{ stats.correct }}/{{ stats.answered }}</span>
    </div>
    <div class="row q-progress-row">
      <span class="muted num q-index">{{ session.idx + 1 }}/{{ session.questions.length }}</span>
      <span class="progress q-progress"><i :style="{ width: ((session.idx + 1) / session.questions.length * 100) + '%' }"></i></span>
    </div>

    <div class="q-box">
      <div class="stem">{{ current.stem }}</div>
      <div v-if="current.items && current.items.length" class="q-items">
        <div v-for="it in current.items" :key="it.seq" class="q-item">
          <b>（{{ it.seq }}）</b> {{ it.stem }} <span class="muted">[{{ it.score }}分]</span>
        </div>
      </div>
      <template v-if="current.qtype === 'choice'">
        <label v-for="opt in current.options" :key="opt" class="opt"
               :class="{
                 selected: selected() === opt[0],
                 'opt-correct': session.results[current.id] && session.results[current.id].correct_answer === opt[0],
                 'opt-wrong': session.results[current.id] && selected() === opt[0] && !session.results[current.id].is_correct
               }">
          <input type="radio" :name="'p' + current.id" :value="opt[0]" v-model="session.answers[current.id]"
                 :disabled="!!session.results[current.id]" class="opt-input" />
          {{ opt }}
        </label>
      </template>
      <textarea v-else v-model="session.answers[current.id]" rows="5" class="answer-input"
                :disabled="!!session.results[current.id]"
                placeholder="在下方作答，交卷后对照参考答案自评"></textarea>
    </div>

    <div v-if="session.results[current.id]" class="answer-result">
      <p>
        <span class="badge" :class="session.results[current.id].is_correct ? 'ok' : 'err'">
          {{ session.results[current.id].is_correct ? '✓ 回答正确' : (session.results[current.id].correct_answer ? '✗ 回答错误' : '主观题 · 请对照参考答案自评') }}
        </span>
        <span v-if="session.results[current.id].correct_answer || session.results[current.id].reference">
          参考答案：<span class="badge ok">{{ session.results[current.id].correct_answer || session.results[current.id].reference }}</span>
        </span>
      </p>
      <p class="muted" v-if="session.results[current.id].analysis">解析：{{ session.results[current.id].analysis }}</p>
      <p class="muted" v-if="session.results[current.id].correct_answer && !session.results[current.id].is_correct">已自动加入错题本，可在「错题本」归因复习。</p>
    </div>

    <div class="row q-foot">
      <BaseButton variant="ghost" :disabled="session.idx === 0" icon="chevron-left" @click="goTo(session.idx - 1)">上一题</BaseButton>
      <div class="row q-dots">
        <button v-for="(qq, i) in session.questions" :key="qq.id" class="dot-btn"
                :class="{ done: session.results[qq.id] && session.results[qq.id].is_correct, wrong: session.results[qq.id] && !session.results[qq.id].is_correct, cur: i === session.idx }"
                @click="goTo(i)">{{ i + 1 }}</button>
      </div>
      <BaseButton v-if="!session.results[current.id]" :disabled="!selected()" @click="check">提交</BaseButton>
      <BaseButton v-else @click="next">{{ session.idx < session.questions.length - 1 ? '下一题' : '完成练习' }}<Icon name="chevron-right" :size="14" /></BaseButton>
    </div>
  </div>

  <!-- 完成总结 -->
  <div class="card" v-if="view === 'result' && session">
    <h2>练习完成 · {{ session.kpName }}</h2>
    <div class="stat-grid result-stats">
      <div class="stat-card">
        <div class="stat-label">答对</div>
        <div class="stat-value">{{ stats.correct }}<small>/{{ stats.answered }}</small></div>
      </div>
      <div class="stat-card ok">
        <div class="stat-label">正确率</div>
        <div class="stat-value">{{ stats.answered ? Math.round(stats.correct / stats.answered * 100) : 0 }}<small>%</small></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">错题</div>
        <div class="stat-value">{{ stats.wrongs.length }}<small> 题</small></div>
      </div>
    </div>
    <template v-if="stats.wrongs.length">
      <h3>错题回顾（已自动加入错题本）</h3>
      <div class="q-box" v-for="w in stats.wrongs" :key="w.question_id">
        <div class="stem">{{ w.stem }}</div>
        <p class="wrong-answer">
          我的答案 <span class="badge err">{{ w.answer || '未作答' }}</span>
          正确答案 <span class="badge ok">{{ w.correct_answer }}</span>
        </p>
        <p class="muted" v-if="w.analysis">解析：{{ w.analysis }}</p>
      </div>
    </template>
    <p v-else class="muted">全部答对，太棒了！</p>
    <div class="row result-actions">
      <BaseButton icon="restart" @click="restart">再来一次</BaseButton>
      <BaseButton variant="ghost" @click="backToPick">选择其他知识点</BaseButton>
    </div>
  </div>
</template>

<style scoped>
/* 原内联样式静默化：布局一律走 scoped 类；进度/掌握度等动态宽度保留 :style 绑定 */
.tb-title { font-size: 13px; }
.list-panel { padding: 6px 8px 10px; }
.err-inline { margin: 8px; }
.pick-hint { margin: 8px 12px; }
.tcell { flex: 1; min-width: 0; }
.tree-num { width: 44px; text-align: right; }
.q-head { justify-content: space-between; }
.kp-name { font-size: 14px; }
.q-badge { margin-left: 8px; }
.q-progress-row { margin: 12px 0 6px; }
.q-index { font-size: 12px; width: 44px; }
.q-progress { flex: 1; }
.q-items { margin-top: 10px; }
.q-item { margin: 6px 0; }
.opt-input { display: none; }
.answer-input { width: 100%; }
.answer-result { margin-top: 12px; }
.q-foot { justify-content: space-between; margin-top: 16px; }
.q-dots { gap: 4px; }
.result-stats { margin: 14px 0; }
.wrong-answer { margin: 8px 0; }
.result-actions { margin-top: 16px; }
</style>
