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
  await new Promise(r => setTimeout(r, 6000)); // force 布局 + 3.8s 冻结完成

  const snap = () => page.evaluate(() => document.querySelector('canvas').toDataURL().slice(60, 120));
  const A = await snap();
  await new Promise(r => setTimeout(r, 800));
  const A2 = await snap();
  console.log('冻结后画布静止:', A === A2 ? '是（无动画干扰）' : '否（仍在动）');

  // 滚轮放大
  await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    const r = canvas.getBoundingClientRect();
    canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: -300, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2, bubbles: true, cancelable: true }));
  });
  await new Promise(r => setTimeout(r, 900));
  const B = await snap();
  console.log('滚轮放大:', A !== B ? '缩放生效' : '无变化(仍不生效)');

  // 滚轮缩小
  await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    const r = canvas.getBoundingClientRect();
    canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: 400, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2, bubbles: true, cancelable: true }));
  });
  await new Promise(r => setTimeout(r, 900));
  const C = await snap();
  console.log('滚轮缩小:', B !== C ? '缩放生效' : '无变化');

  // 节点像素覆盖范围检查（是否适配在窗口内）：扫描 canvas 非透明像素分布
  const coverage = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    const data = ctx.getImageData(0, 0, width, height).data;
    let minX = width, maxX = 0, minY = height, maxY = 0, count = 0;
    for (let y = 0; y < height; y += 4) {
      for (let x = 0; x < width; x += 4) {
        const i = (y * width + x) * 4;
        if (data[i + 3] > 30) { if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; count++; }
      }
    }
    return { minX, maxX, minY, maxY, width, height, margin: Math.round(Math.min(minX, minY, width - maxX, height - maxY)) };
  });
  console.log('内容覆盖范围:', JSON.stringify(coverage), '| 最小边距(px):', coverage.margin, coverage.margin > 0 ? '（节点在窗口内 ✓）' : '（贴边或出界）');
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
