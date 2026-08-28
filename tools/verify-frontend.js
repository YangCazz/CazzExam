(async () => {
  try {
    const page = await fetch('http://127.0.0.1:5173/');
    const html = await page.text();
    console.log('page', page.status, 'hasAppDiv=' + html.includes('id="app"'), 'len=' + html.length);
    const h = await fetch('http://127.0.0.1:5173/api/health');
    console.log('proxy /api/health', h.status, JSON.stringify(await h.json()));
  } catch (e) { console.log('ERR', e.message); }
})();
