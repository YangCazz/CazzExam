<script setup>
import { onMounted, ref, computed } from 'vue';
import { http } from '../api/client';
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
  <div class="card">
    <div class="toolbar">
      <b style="font-size:13px">章-节-知识点</b>
      <span class="spacer"></span>
      <span class="badge accent">{{ points.length }} 个知识点</span>
    </div>
    <div class="list-panel" style="padding:6px 8px 10px">
      <p v-if="err" class="badge err" style="margin:8px">{{ err }}</p>
      <div v-for="p in points" :key="p.id" class="tree-row"
           :class="{ active: selected && selected.id === p.id }" @click="select(p)">
        <span class="tree-guide" v-for="i in indent(p)" :key="i"></span>
        <span class="tree-dot"></span>
        <span style="flex:1;min-width:0">
          <span class="tcell-main">{{ p.name }}</span>
          <span class="tcell-sub" v-if="p.code"> · {{ subjects[p.subject] }}</span>
        </span>
        <span class="progress" :class="masteryClass(p.mastery)" style="width:88px"><i :style="{ width: p.mastery + '%' }"></i></span>
        <span class="num muted" style="width:40px;text-align:right">{{ Math.round(p.mastery) }}%</span>
      </div>
      <div class="empty" v-if="!points.length && !err">还没有知识点，用下方表单添加</div>
    </div>
  </div>

  <div class="card" v-if="detail">
    <div class="row" style="justify-content:space-between">
      <h2 style="margin:0">{{ detail.name }} <span class="muted" style="font-weight:400;font-size:12px">{{ detail.code }}</span></h2>
      <div class="row">
        <span class="badge accent">{{ subjects[detail.subject] }}</span>
        <router-link :to="'/practice?kp=' + detail.id"><button class="sm">练习本知识点</button></router-link>
      </div>
    </div>
    <div class="row" style="margin:12px 0 4px">
      <span class="muted" style="font-size:12px">掌握度</span>
      <span class="progress" :class="masteryClass(detail.mastery)" style="width:220px"><i :style="{ width: detail.mastery + '%' }"></i></span>
      <b class="num">{{ Math.round(detail.mastery) }}%</b>
    </div>
    <div class="divider"></div>
    <p style="margin:8px 0 6px"><b style="font-size:13px">定义 / 说明</b></p>
    <textarea v-model="editDesc" rows="2" style="width:100%"></textarea>
    <button class="sm ghost" style="margin-top:6px" @click="saveField('description')">保存说明</button>
    <p style="margin:14px 0 6px"><b style="font-size:13px">要点 / 易错点备忘</b></p>
    <textarea v-model="editMemo" rows="3" style="width:100%"></textarea>
    <button class="sm ghost" style="margin-top:6px" @click="saveField('memo')">保存备忘</button>

    <template v-if="detail.children.length">
      <p style="margin-top:14px"><b style="font-size:13px">子节点</b></p>
      <div class="row"><span class="tag" v-for="c in detail.children" :key="c.id">{{ c.name }}</span></div>
    </template>
    <template v-if="detail.related.length">
      <p style="margin-top:14px"><b style="font-size:13px">关联知识点（串联）</b></p>
      <div class="row"><span class="tag" v-for="(r, i) in detail.related" :key="i">{{ nameMap[r.id] || r.id }}（{{ relNames[r.type] || r.type }}）</span></div>
    </template>
    <template v-if="detail.questions.length">
      <p style="margin-top:14px"><b style="font-size:13px">关联题目（{{ detail.questions.length }}）</b></p>
      <table>
        <thead><tr><th style="width:50px">ID</th><th style="width:80px">题型</th><th>题干</th></tr></thead>
        <tbody>
          <tr v-for="q in detail.questions" :key="q.id">
            <td class="num muted">{{ q.id }}</td>
            <td><span class="badge accent">{{ q.qtype }}</span></td>
            <td class="stem-clamp">{{ q.stem }}</td>
          </tr>
        </tbody>
      </table>
    </template>
    <p v-else class="muted" style="margin-top:14px">还没有关联题目——在「题库」录题时填写知识点 ID 即可关联。</p>
  </div>

  <div class="card">
    <h2>新增知识点</h2>
    <div class="row">
      <input v-model="form.name" placeholder="名称（必填）" />
      <input v-model="form.code" placeholder="编号，如 3.2.1" style="width:110px" />
      <select v-model.number="form.subject">
        <option :value="1">综合知识</option><option :value="2">案例分析</option><option :value="3">论文</option>
      </select>
      <select v-model.number="form.parent_id" style="max-width:200px">
        <option :value="null">（无父级）</option>
        <option v-for="p in points" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <button @click="add">添加</button>
    </div>
  </div>
</template>
