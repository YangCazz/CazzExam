const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('[pageerror] ' + e.message.slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push('[' + m.type() + '] ' + m.text().slice(0, 200)); });
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 2000));
  const dump = await page.evaluate(() => {
    const sb = document.querySelector('.sidebar');
    return {
      sidebarExists: !!sb,
      sidebarHTML: sb ? sb.innerHTML.slice(0, 900) : 'NONE',
      navLinks: document.querySelectorAll('.sidebar a').length,
      svgCount: document.querySelectorAll('.sidebar svg').length,
      activeClass: !!document.querySelector('.sidebar a.router-link-active'),
    };
  });
  console.log(JSON.stringify(dump, null, 1));
  console.log('ERRORS:', errors.length ? errors.join('\n') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
