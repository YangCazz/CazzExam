const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push('[console] ' + m.text().slice(0, 200)); });
  page.on('pageerror', e => errors.push('[pageerror] ' + e.message.slice(0, 200)));
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 1500));
  const links = await page.$$('.sidebar a');
  const texts = [];
  for (const l of links) texts.push(await l.evaluate(el => el.textContent.trim()));
  let fail = 0;
  for (const name of texts) {
    const target = texts.indexOf(name);
    try {
      await links[target].click();
      await new Promise(r => setTimeout(r, 1400));
      const info = await page.evaluate(() => {
        const main = document.querySelector('.main');
        return { url: location.pathname, cards: document.querySelectorAll('.main .card').length, text: main.innerText.slice(0, 55).replace(/\n/g, ' | ') };
      });
      const ok = info.cards > 0;
      if (!ok) fail++;
      console.log((ok ? 'OK    ' : 'BLANK ') + name.padEnd(5) + ' => ' + info.url + ' cards=' + info.cards + (ok ? '' : ' | ' + info.text));
    } catch (e) { fail++; console.log('CLICKERR', name, e.message); }
  }
  console.log('ERRORS:', errors.length ? '\n' + errors.join('\n') : 'none');
  console.log('== UI 测试:', fail === 0 ? '全部页面正常 (' + texts.length + '/' + texts.length + ')' : fail + ' 个页面异常 ==');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
