<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { get, type Concept, type ConceptSummary, type Qualification, type Collection } from './api'
const current = ref(location.hash.slice(1) || '/'), draft = ref(''), qualification = ref('')
const concepts = ref<ConceptSummary[]>([]), concept = ref<Concept | null>(null), qualifications = ref<Qualification[]>([])
const loading = ref(true), error = ref(''), version = ref(''), qualificationError = ref(false)
const heading = ref<HTMLElement | null>(null)
function parseRoute(hash: string) {
 const [path, query] = hash.split('?')
 const params = new URLSearchParams(query)
 return { path: path || '/', q: params.get('q') || '', qualification: params.get('qualification') || '' }
}
const route = computed(() => parseRoute(current.value))
const reading = computed(() => route.value.path.startsWith('/concept/'))
const isMap = computed(() => route.value.path === '/map')
const contextQuery = computed(() => { const p = new URLSearchParams(); if (route.value.q) p.set('q', route.value.q); if (route.value.qualification) p.set('qualification', route.value.qualification); return p.size ? '?' + p : '' })
const exploreHref = computed(() => '#/' + contextQuery.value)
const conceptHref = (slug: string) => '#/concept/' + encodeURIComponent(slug) + contextQuery.value
let controller: AbortController | null = null
const positions = new Map<string, number>()
let lastRoute = current.value
function syncRoute() { positions.set(lastRoute, window.scrollY); current.value = location.hash.slice(1) || '/'; lastRoute = current.value }
async function loadQualifications() { qualificationError.value = false; try { qualifications.value = (await get<Collection<Qualification>>('qualifications')).items } catch { qualificationError.value = true } }
async function load() {
 controller?.abort(); const own = new AbortController(); controller = own
 loading.value = true; error.value = ''; concept.value = null; concepts.value = []
 try {
  if (reading.value) { const slug = route.value.path.slice('/concept/'.length); if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) throw new Error('这个概念暂未收录。'); concept.value = await get<Concept>('concepts/' + slug, own.signal); version.value = concept.value.content_version; document.title = concept.value.title + ' · CazzExam' }
  else if (route.value.path === '/' || isMap.value) { const p = new URLSearchParams(); if (route.value.q) p.set('q', route.value.q); if (route.value.qualification) p.set('qualification', route.value.qualification); const result = await get<Collection<ConceptSummary>>('concepts?' + p, own.signal); concepts.value = result.items; version.value = result.content_version; document.title = (isMap.value ? '知识地图' : '探索知识') + ' · CazzExam' }
  else { error.value = '这个页面不存在。你可以回到探索。' }
 } catch (e) { if (own.signal.aborted) return; error.value = e instanceof Error && e.name !== 'TypeError' ? e.message : '知识库暂时无法读取，请检查服务是否启动。' }
 finally { if (!own.signal.aborted) { loading.value = false; await nextTick(); heading.value?.focus({preventScroll:true}); window.scrollTo(0, positions.get(current.value) ?? 0) } }
}
function setRoute(path: string, q: string, lens: string) {
 const params = new URLSearchParams()
 if (q) params.set('q', q)
 if (lens) params.set('qualification', lens)
 const hash = '#' + path + (params.size ? '?' + params : '')
 if (location.hash !== hash) { location.hash = hash; return true }
 return false
}
function search() {
 if (!setRoute(isMap.value ? '/map' : '/', draft.value.trim(), qualification.value)) {
  draft.value = route.value.q
  load()
 }
}
function selectPerspective() { setRoute(route.value.path, route.value.q, qualification.value) }
function clearPerspective() { setRoute(route.value.path, route.value.q, '') }
function clearSearch() { setRoute(isMap.value ? '/map' : '/', '', '') }
function syncFields() {
 draft.value = route.value.q
 qualification.value = route.value.qualification
}
watch(current, (_, previous) => {
 syncFields()
 // The detail API returns every mapping for a concept. Keep the rendered
 // article (including an open mapping and focus) across lens-only history.
 if (reading.value && parseRoute(previous).path === route.value.path) return
 load()
})
onMounted(() => { syncFields(); window.addEventListener('hashchange', syncRoute); loadQualifications(); load() })
onUnmounted(() => { window.removeEventListener('hashchange', syncRoute); controller?.abort() })
const visibleMappings = computed(() => concept.value?.mappings.filter(m => !route.value.qualification || m.qualification === route.value.qualification) || [])
</script>

<template>
 <a class="skip" href="#main" @click.prevent="heading?.focus()">跳到正文</a>
 <div class="shell">
  <aside class="sidebar">
   <a class="brand" href="#/" aria-label="CazzExam 首页"><span class="brandmark" aria-hidden="true">⬡</span>CazzExam<span class="beta">NEXT</span></a>
   <nav aria-label="主要导航"><a :href="exploreHref" :aria-current="!isMap ? 'page' : undefined"><span aria-hidden="true">⌕</span>探索</a><a :href="'#/map' + contextQuery" :aria-current="isMap ? 'page' : undefined"><span aria-hidden="true">◇</span>知识地图</a></nav>
   <div class="side-note"><span class="line-art" aria-hidden="true">◇</span><p>知识之间，<br>总有新的连接。</p><small>自由探索 · 原创内容样例</small></div>
  </aside>
  <div class="workspace">
   <header class="topbar"><span class="mobile-brand">⬡ CazzExam</span><label class="perspective">学习视角 <select v-model="qualification" @change="selectPerspective" :disabled="qualificationError"><option value="">自由探索 · 全部</option><option v-for="item in qualifications" :value="item.id" :key="item.id">{{item.name}}{{item.has_content ? '' : ' · 尚无内容'}}</option><option v-if="qualification && !qualifications.some(q => q.id === qualification)" :value="qualification">未知视角 · 请重新选择</option></select></label><span class="quiet top-note">从好奇心出发，不必赶进度</span></header>
   <div v-if="qualificationError" class="notice" role="alert">考试视角暂未加载。<button @click="loadQualifications">重试加载</button></div>
   <main id="main" :aria-busy="loading">
    <template v-if="!reading">
     <section class="hero"><span class="eyebrow">{{isMap ? 'CONNECTED IDEAS' : 'A SPACE TO UNDERSTAND'}}</span><h1 ref="heading" tabindex="-1">{{isMap ? '沿着联系，继续探索' : '从一个问题开始'}}</h1><p>理解知识，发现联系。让一个答案，带来新的问题。</p>
      <form class="search" @submit.prevent="search" role="search"><span aria-hidden="true">⌕</span><input aria-label="搜索问题、概念或主题" v-model="draft" maxlength="120" placeholder="搜索问题、概念或主题，例如：一致性"><button type="submit" class="primary">搜索 <span aria-hidden="true">→</span></button></form>
      <p class="search-hint">标题、别名和关键词检索，不是 AI 问答。</p>
     </section>
    </template>
    <div v-if="loading" class="state" role="status">正在展开知识库…</div>
    <div v-else-if="error" class="state" role="alert"><h2 ref="heading" tabindex="-1">暂时没能打开</h2><p>{{error}}</p><button @click="load" class="primary">重试</button> <a :href="exploreHref">返回探索</a></div>
    <template v-else-if="reading && concept">
     <div class="reading-head"><a :href="exploreHref" class="back">← 返回探索{{route.q ? '结果' : ''}}</a><h1 ref="heading" tabindex="-1">{{concept.title}}</h1><p class="lede">{{concept.summary}}</p><span class="pill">{{concept.source_label}}</span></div>
     <div class="reading-grid">
      <article><section v-for="(section, index) in concept.sections" :key="index" class="prose"><h2>{{section.heading}}</h2><p>{{section.body}}</p></section><footer class="source">内容版本 {{concept.content_version}} · 本站原创讲解样例，不是官方试题或考纲原文。</footer></article>
      <aside class="related"><h2>关联探索</h2><p class="quiet">理解一个概念，也看见它的边界。</p><a v-for="relation in concept.relations" :key="relation.slug" :href="conceptHref(relation.slug)" class="relation"><span class="pill">{{relation.kind}}</span><h3>{{relation.title}} <span aria-hidden="true">↗</span></h3><p>{{relation.reason}}</p></a><p v-if="!concept.relations.length">暂未收录关联概念。</p>
       <details class="mapping"><summary>考试视角与内容说明</summary><p>这里展示编辑标记的主题相关性，不等同于已核验的官方考纲覆盖。</p><div v-for="mapping in visibleMappings" :key="mapping.qualification"><strong>{{qualifications.find(q => q.id === mapping.qualification)?.name || mapping.qualification}}</strong><p>{{mapping.label}} · {{mapping.evidence_status === "editorial_topic" ? "编辑主题关联，未核考纲" : mapping.evidence_status}}</p><a v-if="mapping.source_url" :href="mapping.source_url" target="_blank" rel="noopener noreferrer">查看参考来源 ↗</a></div><p v-if="!visibleMappings.length">此视角暂无已记录的主题映射；概念仍可自由阅读。</p></details>
      </aside>
     </div>
    </template>
    <template v-else-if="!reading">
     <div v-if="!concepts.length" class="state"><h2>还没有找到这个方向</h2><p>试试更短的关键词<span v-if="route.qualification">，或取消考试视角后继续搜索</span>。没有结果不代表这个知识不重要。</p><button v-if="route.qualification" @click="clearPerspective" class="primary">取消考试视角</button> <button @click="clearSearch" :class="{ primary: !route.qualification }">查看全部概念</button></div>
     <template v-else>
      <section v-if="!route.q && !route.qualification && !isMap" class="feature"><div><span class="eyebrow">✦ 好奇问题</span><h2>为什么系统拆分之后<br>反而更复杂？</h2><p>边界让团队更独立，也让一次调用跨过网络。<br>从拆分出发，看看一致性、故障与协作之间的联系。</p><a :href="conceptHref('service-decomposition')" class="primary">展开阅读 →</a></div><div class="diagram" aria-label="一个系统拆分为相互连接的服务"><div class="cube big">系统</div><span class="connector">→</span><div class="nodes"><span class="cube">服务</span><span class="cube">数据</span><span class="cube">消息</span></div></div></section>
      <section class="results"><div class="section-title"><h2>{{isMap ? '概念的入口' : route.q ? '搜索结果' : '主题探索'}}</h2><span class="quiet">{{concepts.length}} 个原创概念</span></div><p v-if="isMap" class="quiet">打开任一概念，沿着有解释的关系继续阅读。首版以可访问的列表呈现，而非拖拽图谱。</p><div class="cards"><a v-for="(item,index) in concepts" :key="item.id" :href="conceptHref(item.slug)" class="concept-card"><span class="card-index">{{String(index+1).padStart(2,'0')}} / CONCEPT</span><h3>{{item.title}}</h3><p>{{item.summary}}</p><div class="card-bottom"><span>{{item.match_reason || '原创讲解 · 关联阅读'}}</span><span class="round-arrow" aria-hidden="true">↗</span></div></a></div></section>
     </template>
     <p class="source">{{version ? '内容版本 ' + version + ' · ' : ''}}小规模原创知识样例，不承诺覆盖全部考纲。收藏、笔记与练习尚未开放。</p>
    </template>
   </main>
  </div>
 </div>
 <nav class="mobile-nav" aria-label="手机导航"><a :href="exploreHref" :aria-current="!isMap ? 'page' : undefined">⌕ 探索</a><a :href="'#/map' + contextQuery" :aria-current="isMap ? 'page' : undefined">◇ 知识地图</a></nav>
</template>
