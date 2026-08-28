<script setup>
import { onMounted, ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { http } from '../api/client';
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
      <b style="font-size:13px">选择知识点</b>
      <span class="spacer"></span>
      <span class="badge accent">{{ tree.length }} 个知识点</span>
    </div>
    <div class="list-panel" style="padding:6px 8px 10px">
      <p v-if="err" class="badge err" style="margin:8px">{{ err }}</p>
      <p class="muted" style="margin:8px 12px">点选知识点开始练习：做关联题 → 即时判分 → 答错自动进错题本。</p>
      <div v-for="p in tree" :key="p.id" class="tree-row" @click="startWithKp(p.id)">
        <span class="tree-guide" v-for="i in indent(p)" :key="i"></span>
        <span class="tree-dot"></span>
        <span style="flex:1;min-width:0">
          <span class="tcell-main">{{ p.name }}</span>
          <span class="tcell-sub" v-if="p.code"> · {{ p.code }}</span>
        </span>
        <span class="num muted" style="width:44px;text-align:right">{{ Math.round(p.mastery) }}%</span>
        <button class="sm ghost" @click.stop="startWithKp(p.id)">练习</button>
      </div>
    </div>
  </div>

  <!-- 练习中 -->
  <div class="card" v-if="view === 'practice' && session && current">
    <div class="row" style="justify-content:space-between">
      <div>
        <b style="font-size:14px">{{ session.kpName }}</b>
        <span class="badge accent" style="margin-left:8px">{{ qtypeName(current) }}</span>
      </div>
      <span class="badge ok">答对 {{ stats.correct }}/{{ stats.answered }}</span>
    </div>
    <div class="row" style="margin:12px 0 6px">
      <span class="muted num" style="font-size:12px;width:44px">{{ session.idx + 1 }}/{{ session.questions.length }}</span>
      <span class="progress" style="flex:1"><i :style="{ width: ((session.idx + 1) / session.questions.length * 100) + '%' }"></i></span>
    </div>

    <div class="q-box">
      <div class="stem">{{ current.stem }}</div>
      <div v-if="current.items && current.items.length" style="margin-top:10px">
        <div v-for="it in current.items" :key="it.seq" style="margin:6px 0">
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
                 :disabled="!!session.results[current.id]" style="display:none" />
          {{ opt }}
        </label>
      </template>
      <textarea v-else v-model="session.answers[current.id]" rows="5"
                :disabled="!!session.results[current.id]"
                placeholder="在下方作答，交卷后对照参考答案自评" style="width:100%"></textarea>
    </div>

    <div v-if="session.results[current.id]" style="margin-top:12px">
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

    <div class="row" style="justify-content:space-between;margin-top:16px">
      <button class="ghost" :disabled="session.idx === 0" @click="goTo(session.idx - 1)">◀ 上一题</button>
      <div class="row" style="gap:4px">
        <button v-for="(qq, i) in session.questions" :key="qq.id" class="dot-btn"
                :class="{ done: session.results[qq.id] && session.results[qq.id].is_correct, wrong: session.results[qq.id] && !session.results[qq.id].is_correct, cur: i === session.idx }"
                @click="goTo(i)">{{ i + 1 }}</button>
      </div>
      <button v-if="!session.results[current.id]" @click="check" :disabled="!selected()">提交</button>
      <button v-else @click="next">{{ session.idx < session.questions.length - 1 ? '下一题 ▶' : '完成练习' }}</button>
    </div>
  </div>

  <!-- 完成总结 -->
  <div class="card" v-if="view === 'result' && session">
    <h2>练习完成 · {{ session.kpName }}</h2>
    <div class="stat-grid" style="margin:14px 0">
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
        <p style="margin:8px 0">
          我的答案 <span class="badge err">{{ w.answer || '未作答' }}</span>
          正确答案 <span class="badge ok">{{ w.correct_answer }}</span>
        </p>
        <p class="muted" v-if="w.analysis">解析：{{ w.analysis }}</p>
      </div>
    </template>
    <p v-else class="muted">全部答对，太棒了！</p>
    <div class="row" style="margin-top:16px">
      <button @click="restart">再来一次</button>
      <button class="ghost" @click="backToPick">选择其他知识点</button>
    </div>
  </div>
</template>
