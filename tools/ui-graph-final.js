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
  await new Promise(r => setTimeout(r, 4500));
  const snap = () => page.evaluate(() => document.querySelector('canvas').toDataURL().slice(60, 120));
  const A = await snap();
  // 搜索（触发 render，节点不应重排）
  await page.type('input[placeholder*="搜索"]', '微服务');
  await new Promise(r => setTimeout(r, 1000));
  const B = await snap();
  // 清空搜索
  await page.click('input[placeholder*="搜索"]', { clickCount: 3 });
  await page.keyboard.press('Backspace');
  await new Promise(r => setTimeout(r, 1000));
  const C = await snap();
  // 位置保持判断：搜索期间只应改变透明度/标签，不应整体重排（粗粒度对比）
  const b = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    const d = ctx.getImageData(0, 0, width, height).data;
    let minX = width, maxX = 0, minY = height, maxY = 0;
    for (let y = 0; y < height; y += 4) for (let x = 0; x < width; x += 4) {
      const i = (y * width + x) * 4;
      if (d[i + 3] > 30) { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; }
    }
    return { minX, maxX, minY, maxY, margin: Math.min(minX, minY, width - maxX, height - maxY) };
  });
  console.log('搜索后覆盖:', JSON.stringify(b), '| 边距:', b.margin, b.margin > 30 ? '（仍在窗口内 ✓）' : '（异常）');
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
