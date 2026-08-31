<script setup>
import { onMounted, ref, reactive, onUnmounted } from 'vue';
import { http } from '../api/client';
const tab = ref('essays');
const essays = ref([]);
const mats = ref([]);
const adrs = ref([]);
const writing = ref(null);
const draft = ref('');
const timeLeft = ref(0);
const wordCount = ref(0);
const attemptId = ref(null);
const aiGrade = ref(null);
const showRef = ref(false);
const matForm = reactive({ category: '项目经历', title: '', content: '', tags: '' });
const err = ref('');
let timer = null;

onMounted(async () => {
  try {
    const [es, ma, ad] = await Promise.all([
      http.get('/questions?qtype=essay&limit=100'),
      http.get('/essay/materials'),
      http.get('/essay/adr'),
    ]);
    essays.value = es; mats.value = ma; adrs.value = ad;
  } catch (e) { err.value = e.message; }
});
onUnmounted(() => { if (timer) clearInterval(timer); });

function fmtTime(s) {
  const m = Math.floor(s / 60), ss = s % 60;
  return String(m).padStart(2, '0') + ':' + String(ss).padStart(2, '0');
}

async function startWrite(e) {
  writing.value = e; draft.value = ''; showRef.value = false; aiGrade.value = null;
  const p = await http.post('/exams/papers', { question_ids: [e.id], template_id: 3 });
  const a = await http.post('/exams/attempts', { paper_id: p.id, mode: 'mock' });
  attemptId.value = a.id;
  timeLeft.value = 120 * 60;
  if (timer) clearInterval(timer);
  timer = setInterval(() => {
    timeLeft.value -= 1;
    if (timeLeft.value <= 0) { clearInterval(timer); timer = null; submit(); }
  }, 1000);
}
async function submit() {
  if (timer) { clearInterval(timer); timer = null; }
  await http.post('/exams/attempts/' + attemptId.value + '/submit', { answers: [{ question_id: writing.value.id, user_answer: draft.value }] });
  aiGrade.value = { message: '已交卷（字数 ' + wordCount.value + '）。点击「AI 批改论文」获得分档评分。' };
}
async function grade() {
  aiGrade.value = { message: 'AI 批改中…' };
  try {
    const r = await http.post('/ai/grade-essay', { attempt_id: attemptId.value });
    aiGrade.value = r;
  } catch (e) { aiGrade.value = { message: e.message }; }
}
function onInput() { wordCount.value = draft.value.replace(/\s/g, '').length; }
async function addMat() {
  if (!matForm.title) return;
  await http.post('/essay/materials', { ...matForm });
  matForm.title = ''; matForm.content = ''; matForm.tags = '';
  mats.value = await http.get('/essay/materials');
}
</script>
<template>
  <div class="card">
    <div class="row" style="justify-content:space-between">
      <h2 style="margin:0">论文专项</h2>
      <div class="row">
        <button :class="tab === 'essays' ? '' : 'ghost'" @click="tab = 'essays'">论文真题与写作</button>
        <button :class="tab === 'mats' ? '' : 'ghost'" @click="tab = 'mats'">素材库</button>
        <button :class="tab === 'adr' ? '' : 'ghost'" @click="tab = 'adr'">ADR 记录</button>
      </div>
    </div>
    <p v-if="err" class="badge err">{{ err }}</p>
  </div>

  <!-- 论文真题与限时写作 -->
  <template v-if="tab === 'essays'">
    <div class="card" v-if="!writing">
      <h2>论文真题库（点击开始限时写作，120 分钟）</h2>
      <div style="margin-top:8px">
        <div v-for="e in essays" :key="e.id" class="tree-row" @click="startWrite(e)">
          <span class="tree-dot"></span>
          <span style="flex:1;min-width:0">
            <span class="tcell-main">{{ (e.stem || '').split('\n')[0] }}</span>
            <span class="tcell-sub" v-if="(e.stem || '').includes('\n')">{{ e.stem.split('\n').slice(1).join(' ') }}</span>
          </span>
          <span class="tag" v-if="e.source_year">{{ e.source_year }}</span>
          <button class="sm ghost" @click.stop="startWrite(e)">开始写作</button>
        </div>
        <div class="empty" v-if="!essays.length">暂无论文真题。在「题库」录 qtype=essay 的题目即可出现。</div>
      </div>
    </div>

    <div class="card" v-if="writing">
      <div class="row" style="justify-content:space-between">
        <h2 style="margin:0">{{ writing.stem }}</h2>
        <div class="row">
          <span class="badge" :class="timeLeft < 1800 ? 'err' : 'ok'">剩余 {{ fmtTime(timeLeft) }}</span>
          <span class="badge warn">字数 {{ wordCount }}</span>
          <button class="ghost" @click="submit">交卷</button>
        </div>
      </div>
      <textarea v-model="draft" rows="18" @input="onInput" placeholder="在此撰写论文（建议 2500 字以上，结合亲身项目实践）" style="width:100%;font-size:14px;line-height:1.8"></textarea>
      <div class="row" style="margin-top:10px">
        <button class="ghost" @click="showRef = !showRef">{{ showRef ? '隐藏' : '查看' }}参考提纲</button>
        <button @click="grade" :disabled="!attemptId">AI 批改论文</button>
      </div>
      <div v-if="showRef" class="muted" style="margin-top:8px">{{ writing.analysis || writing.answer || '（题库未录入参考提纲）' }}</div>
      <div v-if="aiGrade" style="margin-top:10px">
        <p class="muted">{{ aiGrade.message }}</p>
        <pre v-if="aiGrade.scores" class="ai-pre">{{ JSON.stringify(aiGrade.scores, null, 2) }}</pre>
      </div>
    </div>
  </template>

  <!-- 素材库 -->
  <template v-else-if="tab === 'mats'">
    <div class="card">
      <h2>个人素材库（项目经历 / 架构决策 / 技术点 / 范文）</h2>
      <table>
        <tr><th>分类</th><th>标题</th><th>标签</th></tr>
        <tr v-for="m in mats" :key="m.id"><td>{{ m.category }}</td><td>{{ m.title }}</td><td>{{ m.tags }}</td></tr>
      </table>
      <div class="row" style="margin-top:12px">
        <select v-model="matForm.category"><option>项目经历</option><option>架构决策</option><option>技术点</option><option>范文</option></select>
        <input v-model="matForm.title" placeholder="标题" style="flex:1" />
        <input v-model="matForm.tags" placeholder="标签(逗号分隔)" style="width:200px" />
        <button @click="addMat">保存素材</button>
      </div>
      <div><textarea v-model="matForm.content" rows="3" placeholder="内容（写作时可引用）" style="width:100%"></textarea></div>
      <p class="muted">提示：每完成一个模块/架构决策，就补一条素材——这是论文的弹药库。</p>
    </div>
  </template>

  <!-- ADR -->
  <template v-else>
    <div class="card">
      <h2>架构决策记录（ADR）</h2>
      <table>
        <tr><th>标题</th><th>状态</th><th>日期</th></tr>
        <tr v-for="a in adrs" :key="a.id"><td>{{ a.title }}</td><td>{{ a.status }}</td><td>{{ (a.date || '').slice(0, 10) }}</td></tr>
      </table>
      <p class="muted">ADR 是论文「论架构风格选型 / 论系统设计」的直接素材。完整记录见 docs 设计文档附录。</p>
    </div>
  </template>
</template>
<style scoped>
.ai-pre { background: var(--surface-inset); padding: 10px; border-radius: 8px; overflow: auto; }
</style>
