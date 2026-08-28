(async () => {
  const targets = ['/', '/src/views/KnowledgeView.vue', '/src/views/GraphView.vue', '/src/views/ExamView.vue', '/src/router/index.js'];
  for (const t of targets) {
    try {
      const r = await fetch('http://127.0.0.1:5173' + t);
      const body = await r.text();
      const ok = r.status === 200;
      console.log(t, r.status, ok ? 'OK len=' + body.length : body.slice(0, 300));
    } catch (e) { console.log(t, 'FAIL', e.message); }
  }
})();
