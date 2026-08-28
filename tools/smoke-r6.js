(async () => {
  const J = (o) => JSON.stringify(o);
  const get = async (p) => { const r = await fetch('http://127.0.0.1:8000' + p); return { s: r.status, b: await r.json() }; };
  const post = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  try {
    const qs = await get('/api/questions?qtype=choice&limit=500');
    console.log('choice questions:', qs.b.length, '| has options:', qs.b[0] ? qs.b[0].options.length : 'n/a');
    // 练习判分：正确
    const q = qs.b.find(x => x.stem.includes('LRU 页面置换'));
    const ok = await post('/api/questions/check', { question_id: q.id, user_answer: 'A' });
    console.log('check correct:', ok.s, J(ok.b));
    // 练习判分：错误 → 自动错题
    const bad = await post('/api/questions/check', { question_id: q.id, user_answer: 'B' });
    console.log('check wrong:', bad.s, 'is_correct=' + bad.b.is_correct, 'analysis?=' + !!bad.b.analysis);
    const wl = await get('/api/wrong/queue');
    console.log('wrong auto added:', wl.s, 'count=' + wl.b.length);
  } catch (e) { console.log('ERR', e.message); }
})();
