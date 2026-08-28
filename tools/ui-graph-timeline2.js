const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message.slice(0, 150)));
  await page.goto('http://127.0.0.1:5173/graph', { waitUntil: 'networkidle2', timeout: 25000 });
  for (const t of [1000, 2500, 3500, 5000]) {
    await new Promise(r => setTimeout(r, t - (arguments.callee._last || 0)));
    arguments.callee._last = t;
    const s = await page.evaluate(() => {
      const wrap = document.querySelector('.graph-wrap');
      const canvas = document.querySelector('canvas');
      let cov = null;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        const { width, height } = canvas;
        const d = ctx.getImageData(0, 0, width, height).data;
        let minX = width, maxX = 0, minY = height, maxY = 0;
        for (let y = 0; y < height; y += 4) for (let x = 0; x < width; x += 4) {
          const i = (y * width + x) * 4;
          if (d[i + 3] > 30) { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; }
        }
        cov = { m: Math.min(minX, minY, width - maxX, height - maxY), span: Math.max(maxX - minX, maxY - minY) };
      }
      return { opacity: wrap ? getComputedStyle(wrap).opacity : 'n/a', cov };
    });
    console.log('t=' + t + 'ms opacity=' + s.opacity + (s.cov ? ' margin=' + s.cov.m + ' span=' + s.cov.span : ''));
  }
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
