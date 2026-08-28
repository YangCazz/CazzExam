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
  const info = await page.evaluate(() => {
    const cs = (el) => el ? getComputedStyle(el) : null;
    const body = cs(document.body);
    const stat = document.querySelector('.stat-card');
    const nav = document.querySelector('.sidebar nav a');
    const ico = document.querySelector('.sidebar nav a svg');
    const topbar = document.querySelector('.topbar');
    return {
      bodyBg: body ? body.backgroundColor : null,
      bodyGradient: body ? body.backgroundImage.slice(0, 60) : null,
      sidebarW: document.querySelector('.sidebar') ? getComputedStyle(document.querySelector('.sidebar')).width : null,
      statGrid: getComputedStyle(document.querySelector('.stat-grid')).display,
      statCount: document.querySelectorAll('.stat-card').length,
      statRadius: stat ? cs(stat).borderRadius : null,
      navIcons: document.querySelectorAll('.sidebar nav svg').length,
      navActive: document.querySelector('.sidebar nav a.router-link-active') ? getComputedStyle(document.querySelector('.sidebar nav a.router-link-active')).backgroundImage.slice(0, 60) : null,
      topbarTitle: topbar ? topbar.innerText.slice(0, 40) : null,
      pageText: document.querySelector('.main').innerText.slice(0, 80).replace(/\n/g, ' | '),
    };
  });
  console.log(JSON.stringify(info, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
