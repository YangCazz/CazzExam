(async () => {
  const targets = ['/', '/src/views/PlanView.vue', '/src/views/HomeView.vue'];
  for (const t of targets) {
    try {
      const r = await fetch('http://127.0.0.1:5173' + t);
      const body = await r.text();
      console.log(t, r.status, r.status === 200 ? 'OK len=' + body.length : body.slice(0, 300));
    } catch (e) { console.log(t, 'FAIL', e.message); }
  }
})();
