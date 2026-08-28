(async () => {
  const J = (o) => JSON.stringify(o);
  const get = async (p) => { const r = await fetch('http://127.0.0.1:8000' + p); return { s: r.status, b: await r.json() }; };
  const post = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  const put = async (p, b) => { const r = await fetch('http://127.0.0.1:8000' + p, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b || {}) }); return { s: r.status, b: await r.json() }; };
  try {
    const q = await get('/api/wrong/queue');
    console.log('queue', q.s, 'count=' + q.b.length, q.b[0] ? 'hasQ=' + !!q.b[0].question : '');
    const s = await get('/api/wrong/summary');
    console.log('summary', s.s, J(s.b));
    const u = await put('/api/wrong/1', { error_type: '审题失误', reflection: '当时没看清“不属于”二字。' });
    console.log('attribution', u.s, J(u.b));
    const rv = await post('/api/wrong/1/review', { quality: 5 });
    console.log('review5', rv.s, J(rv.b));
    const rv2 = await post('/api/wrong/2/review', { quality: 0 });
    console.log('review0', rv2.s, J(rv2.b));
    const td = await get('/api/stats/trend');
    console.log('trend', td.s, 'days=' + td.b.length, J(td.b[td.b.length - 1]));
    const ed = await get('/api/stats/error-dist');
    console.log('errorDist', ed.s, J(ed.b));
  } catch (e) { console.log('ERR', e.message); }
})();
