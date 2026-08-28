const puppeteer = require('puppeteer-core');
const fs = require('fs');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1.5 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message.slice(0, 150)));
  const shots = [
    ['home', '/'], ['knowledge', '/knowledge'], ['practice', '/practice'],
    ['graph', '/graph'], ['exam', '/exam'], ['wrong', '/wrong'],
    ['stats', '/stats'], ['essay', '/essay'], ['settings', '/settings']
  ];
  fs.mkdirSync('shots', { recursive: true });
  for (const [name, path] of shots) {
    try {
      await page.goto('http://127.0.0.1:5173' + path, { waitUntil: 'networkidle2', timeout: 25000 });
      await new Promise(r => setTimeout(r, 1200));
      await page.screenshot({ path: 'shots/' + name + '.png' });
      console.log('shot', name, path);
    } catch (e) { console.log('FAIL', name, e.message); }
  }
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
