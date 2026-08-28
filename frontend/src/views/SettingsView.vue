<script setup>
import { onMounted, ref } from 'vue';
import { http } from '../api/client';
const profile = ref({ certification: '系统架构设计师', target_date: '', weekly_minutes: 240, timezone: 'Asia/Shanghai' });
const health = ref(null); const ai = ref(null); const msg = ref(''); const err = ref('');
async function load() { try { const [p,h,a] = await Promise.all([http.get('/learning/profile'),http.get('/health'),http.get('/ai/status')]); profile.value=p;health.value=h;ai.value=a; } catch(e){err.value=e.message;} }
async function save(){ try{ await http.put('/learning/profile',profile.value);msg.value='设置已保存。今天未开始的任务会在你下次重排时按新时长调整。'; }catch(e){err.value=e.message;} }
onMounted(load);
</script>
<template>
  <div class="card"><h2>目标与考试</h2><p class="muted">设置仅保存在本机，用于生成学习节奏；未设置考试日期也可以正常学习。</p><div class="settings-grid"><label>备考资格<input v-model="profile.certification" /></label><label>目标考试日期<input type="date" v-model="profile.target_date" /></label><label>每周可用时间（分钟）<input type="number" min="30" max="2400" v-model.number="profile.weekly_minutes" /></label></div><button @click="save">保存设置</button><p v-if="msg" class="badge ok">{{ msg }}</p><p v-if="err" class="badge err">{{ err }}</p></div>
  <div class="card"><h2>本地数据与备份</h2><p class="muted">学习记录保存在 <code>backend/data/study.db</code>。恢复备份会覆盖当前数据，请先另行备份。</p><div class="row"><a href="/api/questions/export" download="questions.json"><button class="ghost">导出题库 JSON</button></a><a href="/api/knowledge/graph" download="knowledge-graph.json"><button class="ghost">导出知识图谱</button></a></div></div>
  <div class="card"><h2>AI 与隐私</h2><p v-if="ai">状态：<span class="badge" :class="ai.available?'ok':'warn'">{{ ai.available?'已配置':'未配置（离线可用）' }}</span> <span class="muted">AI 只在你主动发起批改时调用，核心练习和复盘不依赖 AI。</span></p><p v-if="health" class="muted">本地后端：{{ health.app }} · 运行正常</p></div>
</template>
