(async () => {
  const J = (o) => JSON.stringify(o);
  const get = async (p) => { const r = await fetch('http://127.0.0.1:8000' + p); return { s: r.status, b: await r.json() }; };
  const post = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  try {
    const tr = await get('/api/knowledge/tree');
    console.log('tree', tr.s, 'nodes=' + tr.b.length);
    const gr = await get('/api/knowledge/graph');
    console.log('graph', gr.s, 'nodes=' + gr.b.nodes.length, 'links=' + gr.b.links.length);
    const qs = await get('/api/questions?limit=200');
    console.log('questions', qs.s, 'count=' + qs.b.length);
    const pg = await post('/api/plans/generate', { exam_date: '2026-11-14' });
    console.log('planGen', pg.s, J(pg.b));
    const pl = await get('/api/plans');
    console.log('plans', pl.s, 'count=' + pl.b.length, pl.b[0] ? pl.b[0].target : '');
  } catch (e) { console.log('ERR', e.message); }
})();
