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
  await new Promise(r => setTimeout(r, 2500));
  const info = await page.evaluate(() => {
    // 通过 echarts 实例（挂载在 DOM 上）检查配置
    const el = document.querySelector('.card > div');
    const chart = el && el.__echarts__ ? el.__echarts__ : null;
    if (!chart) return { echarts: false };
    const opt = chart.getOption();
    const s = opt.series && opt.series[0] ? opt.series[0] : null;
    return {
      echarts: true,
      layout: s ? s.layout : null,
      roam: s ? JSON.stringify(s.roam) : null,
      draggable: s ? s.draggable : null,
      scaleLimit: s ? JSON.stringify(s.scaleLimit) : null,
      nodes: opt.series && opt.series[0].data ? opt.series[0].data.length : 0,
      links: opt.series && opt.series[0].links ? opt.series[0].links.length : 0,
    };
  });
  console.log(JSON.stringify(info, null, 1));
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
