const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new', args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 1500));
  const links = await page.$$('.sidebar a');
  const texts = [];
  for (const l of links) texts.push(await l.evaluate(el => el.textContent.trim()));
  let fail = 0;
  for (const name of ['知识库', '题库', '模拟考试', '错题本', '统计', '论文专项', '设置']) {
    const idx = texts.indexOf(name);
    await links[idx].click();
    await new Promise(r => setTimeout(r, 1500));
    const info = await page.evaluate(() => {
      const main = document.querySelector('.main');
      const view = main.children[1];
      return { url: location.pathname, viewLen: view ? view.innerHTML.length : 0, text: main.innerText.slice(0, 60).replace(/\n/g, ' | ') };
    });
    const ok = info.viewLen > 300;
    if (!ok) fail++;
    console.log((ok ? 'OK    ' : 'BLANK ') + name + ' => ' + info.url + ' len=' + info.viewLen + (ok ? '' : ' | ' + info.text));
  }
  console.log('== 导航测试:', fail === 0 ? '全部正常' : fail + ' 个失败 ==');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
