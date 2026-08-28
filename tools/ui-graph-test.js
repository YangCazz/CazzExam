const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const errors = [];
  page.on('pageerror', e => errors.push('[pageerror] ' + e.message.slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error') errors.push('[console] ' + m.text().slice(0, 150)); });
  await page.goto('http://127.0.0.1:5173/graph', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 3000)); // force 布局稳定

  // 配置检查
  const cfg = await page.evaluate(() => {
    const chartEl = document.querySelector('.list-panel > div');
    const chart = chartEl && chartEl.__echarts__;
    if (!chart) return { hasChart: false };
    const s = chart.getOption().series[0];
    return { hasChart: true, layout: s.layout, roam: JSON.stringify(s.roam), draggable: s.draggable, nodes: s.data.length, links: s.links.length };
  });
  console.log('配置:', JSON.stringify(cfg));

  // 拖拽平移测试（画布右下空白区）
  const before = await page.evaluate(() => document.querySelector('canvas').toDataURL().slice(80, 130));
  const box = await page.evaluate(() => { const r = document.querySelector('.list-panel').getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
  await page.mouse.move(box.x + box.w - 70, box.y + box.h - 70);
  await page.mouse.down();
  await page.mouse.move(box.x + box.w - 220, box.y + box.h - 140, { steps: 10 });
  await page.mouse.up();
  await new Promise(r => setTimeout(r, 1000));
  const after = await page.evaluate(() => document.querySelector('canvas').toDataURL().slice(80, 130));
  console.log('拖拽平移生效:', before !== after ? '是（画布内容已变化）' : '未检测到变化');

  // 搜索框交互
  await page.type('input[placeholder*="搜索"]', '微服务');
  await new Promise(r => setTimeout(r, 800));
  const searchState = await page.evaluate(() => document.querySelector('.toolbar .badge') ? document.querySelector('.toolbar .badge').textContent.trim() : 'n/a');
  console.log('搜索后计数:', searchState);
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
