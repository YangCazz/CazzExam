(async () => {
  const J = (o) => JSON.stringify(o);
  const get = async (p) => { const r = await fetch('http://127.0.0.1:8000' + p); return { s: r.status, b: await r.json() }; };
  const post = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  try {
    const ex = await get('/api/questions/export');
    console.log('export', ex.s, 'count=' + ex.b.count, 'first=' + J(ex.b.questions[0]).slice(0, 80));
    const cs = await get('/api/questions?qtype=case&limit=50');
    const cq = cs.b[0];
    const chk = await post('/api/questions/check', { question_id: cq.id, user_answer: '我的案例作答……' });
    console.log('case check:', chk.s, 'is_correct=' + chk.b.is_correct, 'hasReference=' + !!chk.b.reference, 'hasItemsInList=' + (cs.b[0].options !== undefined));
  } catch (e) { console.log('ERR', e.message); }
})();
