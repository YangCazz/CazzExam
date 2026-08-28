<script setup>
import { onMounted, ref } from 'vue';
import { http } from '../api/client';
const health = ref(null);
const ai = ref(null);
const err = ref('');
onMounted(async () => {
  try {
    const [h, a] = await Promise.all([http.get('/health'), http.get('/ai/status')]);
    health.value = h; ai.value = a;
  } catch (e) { err.value = e.message; }
});
</script>
<template>
  <div class="card">
    <h2>系统设置</h2>
    <p v-if="err" class="badge err">后端不可达：{{ err }}</p>
    <p v-else-if="health">后端状态：<span class="badge ok">OK</span> · {{ health.app }}</p>
    <h3>AI 网关</h3>
    <p v-if="ai">
      状态：<span class="badge" :class="ai.available ? 'ok' : 'err'">{{ ai.available ? '已配置' : '未配置（离线降级）' }}</span>
      <span class="tag" v-if="ai.base_url">{{ ai.base_url }}</span>
      <span class="tag" v-if="ai.model">{{ ai.model }}</span>
      <span class="muted" v-if="!ai.available"> · {{ ai.hint }}</span>
    </p>
    <p class="muted">配置方式：编辑 backend/app/config.py 中的 ai_base_url / ai_api_key / ai_model（支持 DeepSeek / 通义等 OpenAI 兼容接口），重启后端生效。</p>
    <h3>数据</h3>
    <p class="muted">数据文件：backend/data/study.db（SQLite）。真题导入：docs/import_template.xlsx 模板 → backend/scripts/import_tool.py xlsx2json → import_json.py。</p>
    <div class="row">
      <a href="/api/questions/export" download="questions.json"><button class="ghost">导出题库 JSON（备份/迁移）</button></a>
      <a href="/api/knowledge/graph" download="knowledge-graph.json"><button class="ghost">导出知识图谱 JSON</button></a>
    </div>
  </div>
</template>
