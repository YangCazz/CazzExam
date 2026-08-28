(async () => {
  const get = async (p) => { const r = await fetch('http://127.0.0.1:8000' + p); return { s: r.status, b: await r.json() }; };
  const post = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  try {
    const qs = await get('/api/questions?qtype=choice&limit=200');
    const q = qs.b.find(x => x.stem === '以下哪种架构风格以数据为中心，所有构件通过共享数据仓库交互？');
    if (!q) { console.log('seeded q NOT FOUND'); return; }
    const detail = await get('/api/questions/' + q.id);
    const correct = JSON.parse(detail.b.answer);   // 正确答案字符串
    console.log('q', q.id, 'answer=', correct, 'kp_ids=', JSON.stringify(detail.b.knowledge_ids));
    const before = {};
    for (const kid of detail.b.knowledge_ids) { before[kid] = (await get('/api/knowledge/points/' + kid)).b.mastery; }
    console.log('before mastery:', JSON.stringify(before));
    // 答对一次
    const p = await post('/api/exams/papers', { question_ids: [q.id] });
    const a = await post('/api/exams/attempts', { paper_id: p.b.id, mode: 'mock' });
    const r = await post('/api/exams/attempts/' + a.b.id + '/submit', { answers: [{ question_id: q.id, user_answer: correct }] });
    console.log('submit result:', JSON.stringify(r.b));
    const after = {};
    for (const kid of detail.b.knowledge_ids) { after[kid] = (await get('/api/knowledge/points/' + kid)).b.mastery; }
    console.log('after mastery:', JSON.stringify(after), '(正确率提升即验证通过)');
  } catch (e) { console.log('ERR', e.message); }
})();
