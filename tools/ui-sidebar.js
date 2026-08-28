const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 1800));
  const info = await page.evaluate(() => {
    const sidebar = document.querySelector('.sidebar');
    const link = document.querySelector('.sidebar a');
    const active = document.querySelector('.sidebar a.router-link-active');
    const group = document.querySelector('.nav-group');
    const ico = document.querySelector('.sidebar a svg');
    const cs = (el) => getComputedStyle(el);
    return {
      sidebarW: cs(sidebar).width,
      sidebarPad: cs(sidebar).padding,
      linkPad: cs(link).padding,
      linkMargin: cs(link).margin,
      linkGap: cs(link).gap,
      linkFont: cs(link).fontSize,
      icoSize: ico ? ico.getBoundingClientRect().width : null,
      activeBg: active ? cs(active).backgroundImage.slice(0, 70) : null,
      groupPad: group ? cs(group).padding : null,
      groupCount: document.querySelectorAll('.nav-group').length,
      linkCount: document.querySelectorAll('.sidebar a').length,
      sidebarText: sidebar.innerText.replace(/\n/g, ' / '),
    };
  });
  console.log(JSON.stringify(info, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
