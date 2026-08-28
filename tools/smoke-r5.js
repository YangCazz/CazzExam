(async () => {
  const J = (o) => JSON.stringify(o);
  const get = async (p) => { const r = await fetch('http://127.0.0.1:8000' + p); return { s: r.status, b: await r.json() }; };
  const post = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  try {
    const tr = await get('/api/knowledge/tree');
    console.log('tree', tr.s, 'nodes=' + tr.b.length);
    const gr = await get('/api/knowledge/graph');
    console.log('graph', gr.s, 'nodes=' + gr.b.nodes.length, 'links=' + gr.b.links.length);
    // 找一道 架构风格(3.1) 的题答错，验证掌握度回写
    const qs = await get('/api/questions?qtype=choice&limit=200');
    const q = qs.b.find(x => x.stem.includes('仓库风格以数据为中心')) || qs.b[0];
    const p = await post('/api/exams/papers', { question_ids: [q.id] });
    const a = await post('/api/exams/attempts', { paper_id: p.b.id, mode: 'mock' });
    const wrongAns = q.id === qs.b[0].id && qs.b[0].stem.includes('仓库风格') ? 'A' : 'C';
    await post('/api/exams/attempts/' + a.b.id + '/submit', { answers: [{ question_id: q.id, user_answer: wrongAns }] });
    const d = await get('/api/knowledge/points/7');
    console.log('mastery(架构风格 kp)', d.s, 'mastery=' + d.b.mastery);
    const hist = await get('/api/exams/attempts');
    console.log('history', hist.s, 'count=' + hist.b.length, hist.b[0] ? J(hist.b[0]).slice(0, 120) : '');
  } catch (e) { console.log('ERR', e.message); }
})();
