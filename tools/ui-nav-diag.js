const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 1500));

  // 点击"知识库"
  const links = await page.$$('.sidebar a');
  const texts = [];
  for (const l of links) texts.push(await l.evaluate(el => el.textContent.trim()));
  const idx = texts.indexOf('知识库');
  await links[idx].click();

  // 多个时间点采样
  for (const wait of [200, 800, 2500]) {
    await new Promise(r => setTimeout(r, wait));
    const state = await page.evaluate(() => {
      const main = document.querySelector('.main');
      const viewEl = main.children[1]; // topbar 之后的内容容器（transition 包裹）
      let viewChildren = 0, viewHTML = 0, viewOpacity = null, viewTransform = null, viewClass = '';
      if (viewEl) {
        viewChildren = viewEl.children.length;
        viewHTML = viewEl.innerHTML.length;
        const cs = getComputedStyle(viewEl);
        viewOpacity = cs.opacity;
        viewTransform = cs.transform;
        viewClass = viewEl.className;
      }
      return {
        url: location.pathname,
        mainChildren: main.children.length,
        viewChildren, viewHTML, viewOpacity, viewTransform, viewClass,
      };
    });
    console.log('t+' + wait + 'ms:', JSON.stringify(state));
  }
  // 额外：等 3 秒后看最终文本
  await new Promise(r => setTimeout(r, 1000));
  const final = await page.evaluate(() => document.querySelector('.main').innerText.slice(0, 120).replace(/\n/g, ' | '));
  console.log('final text:', final);
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
