(async () => {
  const targets = [
    '/', '/src/main.js', '/src/App.vue', '/src/router/index.js',
    '/src/views/HomeView.vue', '/src/views/KnowledgeView.vue', '/src/views/PracticeView.vue',
    '/src/views/GraphView.vue', '/src/views/QuestionsView.vue', '/src/views/ExamView.vue',
    '/src/views/WrongView.vue', '/src/views/PlanView.vue', '/src/views/StatsView.vue',
    '/src/views/EssayView.vue', '/src/views/SettingsView.vue'
  ];
  let ok = 0, fail = 0;
  for (const t of targets) {
    try {
      const r = await fetch('http://127.0.0.1:5173' + t);
      const body = await r.text();
      if (r.status === 200) { ok++; console.log('OK  ', t); }
      else { fail++; console.log('FAIL', t, body.slice(0, 150).replace(/\n/g, ' ')); }
    } catch (e) { fail++; console.log('ERR ', t, e.message); }
  }
  console.log('== 全量编译:', ok + '/' + (ok + fail), 'OK ==');
})();
