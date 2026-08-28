const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5173/graph', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 4000));
  const info = await page.evaluate(() => {
    const wrap = document.querySelector('.graph-wrap');
    const panel = document.querySelector('.list-panel');
    return {
      hasWrap: !!wrap,
      wrapOpacity: wrap ? getComputedStyle(wrap).opacity : null,
      panelHTML: panel ? panel.innerHTML.slice(0, 200) : 'NO PANEL',
      bodyHasWrap: document.body.innerHTML.includes('graph-wrap'),
    };
  });
  console.log(JSON.stringify(info, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
