const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  const logs = [];
  page.on('console', m => { const t = m.text(); if (t.includes('[freeze]')) logs.push(t); });
  await page.goto('http://127.0.0.1:5173/graph', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 4000));
  console.log('freeze logs:', logs.length ? logs.join(' | ') : '（freezeFit 未执行或无坐标）');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
