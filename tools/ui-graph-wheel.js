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
  await new Promise(r => setTimeout(r, 3500)); // force 稳定

  const box = await page.evaluate(() => { const r = document.querySelector('.list-panel').getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
  const before = await page.evaluate(() => document.querySelector('canvas').toDataURL().slice(60, 120));

  // 画布中心滚轮放大（deltaY 负值 = 放大）
  await page.mouse.move(box.x + box.w / 2, box.y + box.h / 2);
  await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    const r = canvas.getBoundingClientRect();
    canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: -300, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2, bubbles: true, cancelable: true }));
  });
  await new Promise(r => setTimeout(r, 1200));
  const after = await page.evaluate(() => document.querySelector('canvas').toDataURL().slice(60, 120));
  console.log('滚轮放大 canvas 变化:', before !== after ? '是（缩放生效）' : '未检测到变化');

  // 再缩小
  await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    const r = canvas.getBoundingClientRect();
    canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: 400, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2, bubbles: true, cancelable: true }));
  });
  await new Promise(r => setTimeout(r, 1200));
  const after2 = await page.evaluate(() => document.querySelector('canvas').toDataURL().slice(60, 120));
  console.log('滚轮缩小 canvas 变化:', after2 !== after ? '是' : '未检测到变化');
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
