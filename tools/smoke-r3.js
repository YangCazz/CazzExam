(async () => {
  const J = (o) => JSON.stringify(o);
  const get = async (p) => { const r = await fetch('http://127.0.0.1:8000' + p); return { s: r.status, b: await r.json() }; };
  const post = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  try {
    const st = await get('/api/ai/status');
    console.log('aiStatus', st.s, J(st.b));
    const ge = await post('/api/ai/grade-essay', { attempt_id: 1 });
    console.log('gradeEssay(offline)', ge.s, J(ge.b).slice(0, 150));
    const aw = await post('/api/ai/analyze-wrong', { question_id: 1, user_answer: 'A' });
    console.log('analyzeWrong(offline)', aw.s, J(aw.b).slice(0, 150));
    // 案例题（带小问）+ 论文题
    const cq = await post('/api/questions', { qtype: 'case', subject: 2, stem: '阅读以下系统场景，回答问题。\n[场景] 某电商平台大促期间流量暴增，系统出现响应缓慢与部分服务不可用。',
      answer: '要点1：质量属性——性能(响应时间/吞吐量)、可用性。\n要点2：方案——微服务拆分、缓存、限流降级、负载均衡、监控告警。', analysis: '大促场景核心是性能与可用性。',
      difficulty: 4, source_type: 'self', source_year: null, knowledge_ids: [8, 10],
      items: [{ seq: 1, stem: '指出该场景涉及的两个主要质量属性，并说明理由。', answer: '性能、可用性', score: 10 },
              { seq: 2, stem: '给出至少两种提升性能/可用性的架构手段。', answer: '缓存/限流/降级/集群', score: 15 }] });
    console.log('caseQ', cq.s, J(cq.b));
    const eq = await post('/api/questions', { qtype: 'essay', subject: 3, stem: '论微服务架构的设计与实现\n请围绕微服务架构的拆分原则、服务治理与高可用设计，结合你参与的项目进行论述。',
      answer: '提纲：1 背景与项目介绍 2 微服务拆分原则 3 服务治理(注册发现/熔断限流/网关) 4 高可用设计 5 总结', analysis: '论文需结合亲身项目实践。',
      difficulty: 5, source_type: 'self', source_year: null, knowledge_ids: [10] });
    console.log('essayQ', eq.s, J(eq.b));
    // 案例卷：直接指定题目
    const p = await post('/api/exams/papers', { question_ids: [cq.b.id, eq.b.id], template_id: 2 });
    const pp = await get('/api/exams/papers/' + p.b.id);
    console.log('paper', p.s, 'count=' + p.b.count, 'hasItems=' + (pp.b.questions[0].items.length > 0), 'duration=' + pp.b.duration_min);
    const a = await post('/api/exams/attempts', { paper_id: p.b.id, mode: 'mock' });
    const sub = await post('/api/exams/attempts/' + a.b.id + '/submit', { answers: [
      { question_id: cq.b.id, user_answer: '质量属性：性能与可用性。方案：缓存、限流、集群。' },
      { question_id: eq.b.id, user_answer: '本文结合某电商中台项目……（论文正文）' }] });
    console.log('submit', sub.s, J(sub.b));
    const rep = await get('/api/exams/attempts/' + a.b.id + '/report');
    console.log('report', rep.s, 'subjective=' + rep.b.subjective.length, 'first=' + (rep.b.subjective[0] ? rep.b.subjective[0].qtype : ''));
  } catch (e) { console.log('ERR', e.message); }
})();
