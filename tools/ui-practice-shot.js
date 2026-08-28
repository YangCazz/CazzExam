const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1.5 });
  await page.goto('http://127.0.0.1:5173/practice', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 1400));
  await page.screenshot({ path: 'shots/practice-pick.png' });
  // 进入练习并截图
  const rows = await page.$$('.tree-row');
  let target = -1;
  for (let i = 0; i < rows.length; i++) {
    const t = await rows[i].evaluate(el => el.innerText);
    if (t.includes('架构风格')) { target = i; break; }
  }
  await rows[target].click();
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: 'shots/practice-quiz.png' });
  console.log('practice shots saved');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
