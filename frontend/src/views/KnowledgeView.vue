<script setup>
import { onMounted, ref, computed } from 'vue';
import { http } from '../api/client';
import BaseButton from '../components/base/BaseButton.vue';
import KnowledgeCard from '../components/knowledge/KnowledgeCard.vue';
const points = ref([]);
const selected = ref(null);
const detail = ref(null);
const err = ref('');
const editDesc = ref('');
const editMemo = ref('');
const form = ref({ name: '', code: '', parent_id: null, subject: 1 });
const subjects = { 0: '通用', 1: '综合知识', 2: '案例分析', 3: '论文' };
const relNames = { prerequisite: '前置', related: '相关', contains: '包含', conflicts: '冲突', backbone: '主线' };
const nameMap = computed(() => {
  const m = {};
  for (const p of points.value) m[p.id] = p.name;
  return m;
});
async function load() {
  try { points.value = await http.get('/knowledge/tree'); err.value = ''; }
  catch (e) { err.value = e.message; }
}
onMounted(load);
async function select(p) {
  selected.value = p;
  detail.value = await http.get('/knowledge/points/' + p.id);
  editDesc.value = detail.value.description || '';
  editMemo.value = detail.value.memo || '';
}
async function saveField(field) {
  await http.put('/knowledge/points/' + selected.value.id, { [field]: field === 'description' ? editDesc.value : editMemo.value });
  detail.value[field] = field === 'description' ? editDesc.value : editMemo.value;
  load();
}
function indent(p) { return p.code ? (p.code.split('.').length - 1) : 0; }
async function add() {
  if (!form.value.name) return;
  await http.post('/knowledge/points', form.value);
  form.value = { name: '', code: '', parent_id: null, subject: 1 };
  load();
}
function masteryClass(m) { return m < 40 ? 'err' : (m < 70 ? 'warn' : ''); }
</script>
<template>
  <div class="knowledge-layout">
    <div class="card list-col">
    <div class="toolbar">
      <b class="tb-title">章-节-知识点</b>
      <span class="spacer"></span>
      <span class="badge accent">{{ points.length }} 个知识点</span>
    </div>
    <div class="list-panel">
      <p v-if="err" class="badge err err-inline">{{ err }}</p>
      <div v-for="p in points" :key="p.id" class="tree-row"
           :class="{ active: selected && selected.id === p.id }" @click="select(p)">
        <span class="tree-guide" v-for="i in indent(p)" :key="i"></span>
        <span class="tree-dot"></span>
        <span class="tcell">
          <span class="tcell-main">{{ p.name }}</span>
          <span class="tcell-sub" v-if="p.code"> · {{ subjects[p.subject] }}</span>
        </span>
        <span class="progress tree-progress" :class="masteryClass(p.mastery)"><i :style="{ width: p.mastery + '%' }"></i></span>
        <span class="num muted tree-num">{{ Math.round(p.mastery) }}%</span>
      </div>
      <div class="empty" v-if="!points.length && !err">还没有知识点，用下方表单添加</div>
    </div>
  </div>

    <div class="card detail-col" v-if="detail">
    <div class="row detail-head">
      <h2 class="detail-title">{{ detail.name }} <span class="muted detail-code">{{ detail.code }}</span></h2>
      <div class="row">
        <span class="badge accent">{{ subjects[detail.subject] }}</span>
        <BaseButton :to="'/practice?kp=' + detail.id" size="sm" icon="target">练习本知识点</BaseButton>
      </div>
    </div>
    <div class="row mastery-row">
      <span class="muted muted-sm">掌握度</span>
      <span class="progress mastery-bar" :class="masteryClass(detail.mastery)"><i :style="{ width: detail.mastery + '%' }"></i></span>
      <b class="num">{{ Math.round(detail.mastery) }}%</b>
    </div>
    <div class="divider"></div>
    <p class="field-head"><b>定义 / 说明</b></p>
    <textarea v-model="editDesc" rows="2" class="field-input"></textarea>
    <BaseButton size="sm" variant="ghost" class="field-save" @click="saveField('description')">保存说明</BaseButton>
    <p class="sub-head"><b>要点 / 易错点备忘</b></p>
    <textarea v-model="editMemo" rows="3" class="field-input"></textarea>
    <BaseButton size="sm" variant="ghost" class="field-save" @click="saveField('memo')">保存备忘</BaseButton>

    <div class="divider"></div>
    <p class="sub-block"><b>速查卡</b><span v-if="detail.card" class="badge accent kcard-badge">已归一化脑图</span></p>
    <KnowledgeCard v-if="detail.card" :card="detail.card" />
    <p v-else class="muted sub-block">该知识点暂无速查卡（仅部分来自脑图的知识点已归一化）。</p>

    <template v-if="detail.children.length">
      <p class="sub-block"><b>子节点</b></p>
      <div class="row"><span class="tag" v-for="c in detail.children" :key="c.id">{{ c.name }}</span></div>
    </template>
    <template v-if="detail.related.length">
      <p class="sub-block"><b>关联知识点（串联）</b></p>
      <div class="row"><span class="tag" v-for="(r, i) in detail.related" :key="i">{{ nameMap[r.id] || r.id }}（{{ relNames[r.type] || r.type }}）</span></div>
    </template>
    <template v-if="detail.questions.length">
      <p class="sub-block"><b>关联题目（{{ detail.questions.length }}）</b></p>
      <table>
        <thead><tr><th class="col-id">ID</th><th class="col-qtype">题型</th><th>题干</th></tr></thead>
        <tbody>
          <tr v-for="q in detail.questions" :key="q.id">
            <td class="num muted">{{ q.id }}</td>
            <td><span class="badge accent">{{ q.qtype }}</span></td>
            <td class="stem-clamp">{{ q.stem }}</td>
          </tr>
        </tbody>
      </table>
    </template>
    <p v-else class="muted sub-block">还没有关联题目——在「题库」录题时填写知识点 ID 即可关联。</p>
    </div>
  </div>

  <div class="card">
    <h2>新增知识点</h2>
    <div class="row">
      <input v-model="form.name" placeholder="名称（必填）" />
      <input v-model="form.code" placeholder="编号，如 3.2.1" class="code-input" />
      <select v-model.number="form.subject">
        <option :value="1">综合知识</option><option :value="2">案例分析</option><option :value="3">论文</option>
      </select>
      <select v-model.number="form.parent_id" class="parent-select">
        <option :value="null">（无父级）</option>
        <option v-for="p in points" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <BaseButton @click="add">添加</BaseButton>
    </div>
  </div>
</template>

<style scoped>
/* 原内联样式的静默化：布局一律走 scoped 类，动态宽度（进度填充）保留 :style 绑定 */
.tb-title { font-size: 13px; }
.list-panel { padding: 6px 8px 10px; }
.err-inline { margin: 8px; }
.tcell { flex: 1; min-width: 0; }
.tree-progress { width: 88px; }
.tree-num { width: 40px; text-align: right; }
.detail-head { justify-content: space-between; }
.detail-title { margin: 0; }
.detail-code { font-weight: 400; font-size: 12px; }
.mastery-row { margin: 12px 0 4px; }
.mastery-bar { width: 220px; }
.muted-sm { font-size: 12px; }
.field-head { margin: 8px 0 6px; }
.field-head b, .sub-head b, .sub-block b { font-size: 13px; }
.field-input { width: 100%; }
.field-save { margin-top: 6px; }
.sub-head { margin: 14px 0 6px; }
.sub-block { margin-top: 14px; }
.code-input { width: 110px; }
.parent-select { max-width: 200px; }
.col-id { width: 50px; }
.col-qtype { width: 80px; }
.kcard-badge { margin-left: 8px; }
/* 知识点库页：左列表 / 右详情两栏 */
.knowledge-layout { display: grid; grid-template-columns: minmax(0, 372px) minmax(0, 1fr); gap: 14px; align-items: start; }
.list-col { max-height: calc(100vh - 220px); overflow-y: auto; }
.detail-col { max-height: calc(100vh - 220px); overflow-y: auto; }
@media (max-width: 900px) {
  .knowledge-layout { grid-template-columns: 1fr; }
  .list-col { max-height: 40vh; }
  .detail-col { max-height: none; }
}
</style>
