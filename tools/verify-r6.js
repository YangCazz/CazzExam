(async () => {
  const targets = ['/', '/src/views/PracticeView.vue', '/src/views/KnowledgeView.vue', '/src/router/index.js'];
  for (const t of targets) {
    try {
      const r = await fetch('http://127.0.0.1:5173' + t);
      const body = await r.text();
      console.log(t, r.status, r.status === 200 ? 'OK len=' + body.length : body.slice(0, 300));
    } catch (e) { console.log(t, 'FAIL', e.message); }
  }
})();
