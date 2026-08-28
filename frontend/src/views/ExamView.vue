<script setup>
import { onMounted, ref, reactive, computed, onUnmounted } from 'vue';
import { http } from '../api/client';
const templates = ref([]);
const err = ref('');
const paper = ref(null);
const current = ref(0);
const answers = ref({});
const attemptId = ref(null);
const report = ref(null);
const running = ref(false);
const history = ref([]);
const refOpen = reactive({});
const aiGrade = ref(null);
const timeLeft = ref(0);
const modeLabel = ref('');
let timer = null;

onMounted(async () => {
  try {
    templates.value = await http.get('/exams/templates');
    history.value = await http.get('/exams/attempts');
  } catch (e) { err.value = e.message; }
});
onUnmounted(() => { if (timer) clearInterval(timer); });

const answeredCount = computed(() => Object.keys(answers.value).length);

function fmtTime(s) {
  const m = Math.floor(s / 60), ss = s % 60;
  return String(m).padStart(2, '0') + ':' + String(ss).padStart(2, '0');
}

async function beginPaper(paperInfo, attemptInfo, label) {
  paper.value = await http.get('/exams/papers/' + paperInfo.id);
  attemptId.value = attemptInfo.id;
  current.value = 0; answers.value = {}; report.value = null;
  running.value = true; modeLabel.value = label;
  timeLeft.value = paper.value.duration_min * 60;
  if (timer) clearInterval(timer);
  timer = setInterval(() => {
    timeLeft.value -= 1;
    if (timeLeft.value <= 0) { clearInterval(timer); timer = null; submit(true); }
  }, 1000);
}

function desc(t) {
  return { 1: '75 道单选题，覆盖综合知识全考点；限时作答，自动判分并生成报告。',
           2: '主观案例分析大题（约 5 题），作答后对照参考答案自评或 AI 辅助评分。',
           3: '论文写作，多题选一，结合亲身项目实践论述。' }[t.subject] || '标准试卷，限时全真模拟。';
}

async function start(t) {
  const p = await http.post('/exams/papers', { template_id: t.id });
  const a = await http.post('/exams/attempts', { paper_id: p.id, mode: 'mock' });
  beginPaper(p, a, t.name);
}

async function viewReport(id, label) {
  report.value = await http.get('/exams/attempts/' + id + '/report');
  modeLabel.value = label;
  running.value = false;
}

async function startWrong() {
  const wl = await http.get('/wrong?status=new') || [];
  const ids = wl.slice(0, 50).map(w => w.question_id);
  if (!ids.length) { err.value = '暂无待复习错题'; return; }
  const p = await http.post('/exams/papers', { question_ids: ids });
  const a = await http.post('/exams/attempts', { paper_id: p.id, mode: 'wrong' });
  beginPaper(p, a, '错题重做');
}

async function submit(auto = false) {
  if (!paper.value) return;
  if (timer) { clearInterval(timer); timer = null; }
  if (!auto) {
    const unanswered = paper.value.questions.filter(q => !answers.value[q.id]).length;
    if (unanswered > 0 && !window.confirm('还有 ' + unanswered + ' 题未作答，确定交卷吗？')) { return; }
  }
  const list = paper.value.questions.map(q => ({ question_id: q.id, user_answer: answers.value[q.id] || '' }));
  await http.post('/exams/attempts/' + attemptId.value + '/submit', { answers: list });
  report.value = await http.get('/exams/attempts/' + attemptId.value + '/report');
  running.value = false;
}

function jump(i) { current.value = i; }
const q = computed(() => paper.value ? paper.value.questions[current.value] : null);

async function gradeEssay() {
  aiGrade.value = { message: 'AI 批改中…' };
  try {
    const r = await http.post('/ai/grade-essay', { attempt_id: report.value.attempt_id });
    aiGrade.value = r;
  } catch (e) { aiGrade.value = { message: e.message }; }
}
</script>
<template>
  <div class="card" v-if="!running && !report">
    <h2 style="margin-bottom:4px">选择试卷</h2>
    <p class="muted" style="margin-bottom:14px">按模板限时全真模拟；答错的单选题自动进错题本，交卷后可查看知识点得分率报告。</p>
    <p v-if="err" class="badge err">{{ err }}</p>
    <div class="tpl-grid">
      <div class="tpl-card" v-for="t in templates" :key="t.id">
        <div class="tpl-title">{{ t.name }}</div>
        <div class="tpl-desc">{{ desc(t) }}</div>
        <div class="tpl-meta">
          <span class="tag">限时 {{ t.duration_min }} 分钟</span>
        </div>
        <div class="tpl-actions"><button @click="start(t)">开始考试</button></div>
      </div>
      <div class="tpl-card">
        <div class="tpl-title">错题重做</div>
        <div class="tpl-desc">从错题本待复习队列中抽取题目重做，检验是否真正掌握；答对自动推进复习进度。</div>
        <div class="tpl-actions"><button class="ghost" @click="startWrong">开始重做</button></div>
      </div>
    </div>
    <p class="muted" v-if="!templates.length" style="margin-top:12px">暂无试卷模板，请先确保题库有题。</p>
    <h3 style="margin-top:22px">历史记录</h3>
    <table>
      <tr><th>时间</th><th>模板</th><th>模式</th><th>得分</th><th>已答</th><th></th></tr>
      <tr v-for="h in history" :key="h.id">
        <td>{{ (h.started_at || '').replace('T', ' ').slice(0, 16) }}</td>
        <td>{{ h.template }}</td>
        <td>{{ h.mode }}</td>
        <td>{{ h.score }}</td>
        <td>{{ h.answered }}</td>
        <td><button class="ghost" @click="viewReport(h.id, h.template)">查看报告</button></td>
      </tr>
    </table>
  </div>

  <div class="card" v-if="running && paper">
    <div class="row" style="justify-content:space-between">
      <h2 style="margin:0">{{ modeLabel }} · 第 {{ current + 1 }}/{{ paper.questions.length }} 题</h2>
      <div class="row">
        <span class="badge" :class="timeLeft < 300 ? 'err' : 'ok'">剩余 {{ fmtTime(timeLeft) }}</span>
        <button class="ghost" @click="submit">交卷</button>
      </div>
    </div>
    <div class="row" style="margin:10px 0;flex-wrap:wrap">
      <button v-for="(qq, i) in paper.questions" :key="qq.id" class="ghost"
              :style="{ background: answers[qq.id] !== undefined ? 'rgba(52,211,153,0.25)' : '', margin: '2px' }"
              @click="jump(i)">{{ i + 1 }}</button>
    </div>
    <div class="q-box" v-if="q">
      <div class="stem">{{ q.stem }}</div>
      <div v-if="q.items && q.items.length" style="margin-top:8px">
        <div v-for="it in q.items" :key="it.seq" style="margin:4px 0">
          <b>（{{ it.seq }}）</b> {{ it.stem }} <span class="muted">[{{ it.score }}分]</span>
        </div>
      </div>
      <template v-if="q.qtype === 'choice'">
        <label v-for="opt in q.options" :key="opt" class="opt"
               :class="{ selected: answers[q.id] === opt[0] }">
          <input type="radio" :name="'q' + q.id" :value="opt[0]" v-model="answers[q.id]" style="display:none" />
          {{ opt }}
        </label>
      </template>
      <textarea v-else v-model="answers[q.id]" rows="6" placeholder="主观题作答" style="width:100%"></textarea>
    </div>
    <div class="row" style="margin-top:12px">
      <button class="ghost" :disabled="current === 0" @click="current--">上一题</button>
      <button class="ghost" :disabled="current === paper.questions.length - 1" @click="current++">下一题</button>
      <span class="muted">已答 {{ answeredCount }} 题</span>
    </div>
  </div>

  <div class="card" v-if="report">
    <div class="row" style="justify-content:space-between">
      <h2 style="margin:0">考试报告 · {{ modeLabel }}</h2>
      <router-link to="/wrong"><button class="ghost">去错题本归因</button></router-link>
    </div>
    <p>得分 <b>{{ report.score }}</b> / {{ report.total }} 分（答对 {{ report.correct }} 题）</p>
    <h3>按知识点得分率（升序，薄弱在前）</h3>
    <table>
      <tr><th>知识点</th><th>得分率</th><th>状态</th></tr>
      <tr v-for="b in report.by_knowledge" :key="b.knowledge_id">
        <td>{{ b.name }}</td>
        <td>{{ (b.accuracy * 100).toFixed(0) }}% ({{ b.correct }}/{{ b.total }})</td>
        <td><span class="badge" :class="b.accuracy >= 0.7 ? 'ok' : (b.accuracy >= 0.4 ? 'warn' : 'err')">
          {{ b.accuracy >= 0.7 ? '掌握' : (b.accuracy >= 0.4 ? '待加强' : '薄弱') }}</span></td>
      </tr>
    </table>
    <template v-if="report.wrongs.length">
      <h3>错题回顾（已自动进入错题本）</h3>
      <div class="q-box" v-for="w in report.wrongs" :key="w.question_id">
        <div class="stem">{{ w.stem }}</div>
        <p>你的答案：<span class="badge err">{{ w.user_answer || '未作答' }}</span>
           正确答案：<span class="badge ok">{{ w.correct_answer }}</span></p>
        <p class="muted" v-if="w.analysis">解析：{{ w.analysis }}</p>
      </div>
    </template>
    <template v-if="report.subjective && report.subjective.length">
      <h3>主观题对照（自评 / AI 批改）</h3>
      <div class="q-box" v-for="s in report.subjective" :key="s.question_id">
        <div class="stem">{{ s.stem }}</div>
        <p><b>我的作答：</b><span class="muted">{{ s.user_answer || '未作答' }}</span></p>
        <button class="ghost" @click="refOpen[s.question_id] = !refOpen[s.question_id]">
          {{ refOpen[s.question_id] ? '收起' : '显示参考答案' }}
        </button>
        <div v-if="refOpen[s.question_id]">
          <p><b>参考答案要点：</b>{{ s.reference }}</p>
          <p class="muted" v-if="s.analysis">{{ s.analysis }}</p>
        </div>
      </div>
      <div v-if="aiGrade" style="margin-top:10px">
        <p class="muted">{{ aiGrade.message }}</p>
        <pre v-if="aiGrade.scores" style="background:var(--panel2);padding:10px;border-radius:8px;overflow:auto">{{ JSON.stringify(aiGrade.scores, null, 2) }}</pre>
      </div>
      <button v-if="report.subjective.some(s => s.qtype === 'essay')" @click="gradeEssay">AI 批改论文</button>
    </template>
    <div class="row" style="margin-top:14px">
      <button @click="startWrong">错题重做</button>
      <button class="ghost" @click="report = null; paper = null">返回</button>
    </div>
  </div>
</template>
