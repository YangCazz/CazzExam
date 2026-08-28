<script setup>
import { onMounted, ref } from 'vue';
import { http } from '../api/client';
const stats = ref(null);
const today = ref(null);
const err = ref('');
onMounted(async () => {
  try {
    const [s, t] = await Promise.all([
      http.get('/stats/overview'),
      http.get('/plans/today'),
    ]);
    stats.value = s;
    today.value = t;
  } catch (e) { err.value = e.message; }
});
const accPct = (a) => a == null ? '—' : (a * 100).toFixed(1) + '%';
</script>
<template>
  <p v-if="err" class="badge err" style="margin-bottom:12px">后端连接失败：{{ err }}（请先启动后端）</p>

  <div class="stat-grid">
    <div class="stat-card">
      <div class="stat-label">题库题目</div>
      <div class="stat-value">{{ stats ? stats.total_questions : '…' }}<small> 题</small></div>
    </div>
    <div class="stat-card accent">
      <div class="stat-label">累计作答</div>
      <div class="stat-value">{{ stats ? stats.total_attempts : '…' }}<small> 次</small></div>
    </div>
    <div class="stat-card ok">
      <div class="stat-label">整体正确率</div>
      <div class="stat-value">{{ stats ? accPct(stats.accuracy) : '…' }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">待复习错题</div>
      <div class="stat-value">{{ today ? today.due_reviews : '…' }}<small> 题</small></div>
    </div>
    <div class="stat-card accent">
      <div class="stat-label">薄弱知识点</div>
      <div class="stat-value">{{ today ? today.weak_kps.length : '…' }}<small> 个</small></div>
    </div>
  </div>

  <div class="card" style="margin-top:16px" v-if="today">
    <h2>今日任务 <span class="muted" style="font-weight:400;font-size:12px">（{{ today.date }}）</span></h2>
    <div class="row">
      <router-link to="/wrong" v-if="today.due_reviews > 0">
        <span class="badge err">待复习错题 {{ today.due_reviews }} 题 → 去复习</span>
      </router-link>
      <span class="badge ok" v-else>错题队列已清空</span>
    </div>
    <template v-if="today.weak_kps.length">
      <p style="margin:12px 0 8px"><b style="font-size:13px">薄弱知识点（正确率 &lt; 60%）</b></p>
      <div class="row">
        <router-link v-for="w in today.weak_kps" :key="w.id" :to="'/practice?kp=' + w.id">
          <span class="badge warn">{{ w.name }} · {{ (w.accuracy * 100).toFixed(0) }}%</span>
        </router-link>
      </div>
    </template>
    <p v-else class="muted" style="margin-top:8px">暂无薄弱知识点，保持状态！</p>
  </div>

  <div class="card">
    <h2>使用路径建议</h2>
    <div class="row" style="gap:8px">
      <router-link to="/practice"><span class="badge accent">① 练习模式</span></router-link>
      <router-link to="/exam"><span class="badge accent">② 模拟考试</span></router-link>
      <router-link to="/wrong"><span class="badge accent">③ 错题归因</span></router-link>
      <router-link to="/stats"><span class="badge accent">④ 统计薄弱点</span></router-link>
      <router-link to="/essay"><span class="badge accent">⑤ 论文练笔</span></router-link>
    </div>
    <p class="muted" style="margin-top:12px">
      知识库已内置 55 个知识点与 26 条关联；题库 75 题（单选/案例/论文）可直接开刷。
      真题 PDF 放进来后走 Excel 模板批量导入（docs/import_template.xlsx）。
    </p>
  </div>
</template>
