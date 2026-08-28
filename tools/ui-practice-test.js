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
  await page.goto('http://127.0.0.1:5173/practice', { waitUntil: 'networkidle2', timeout: 25000 });
  await new Promise(r => setTimeout(r, 1500));

  // 找"架构风格"知识点行
  const rows = await page.$$('.tree-row');
  let target = -1;
  for (let i = 0; i < rows.length; i++) {
    const t = await rows[i].evaluate(el => el.innerText);
    if (t.includes('架构风格')) { target = i; break; }
  }
  console.log('目标行(架构风格):', target);
  if (target === -1) { console.log('未找到'); await browser.close(); return; }
  await rows[target].click();
  await new Promise(r => setTimeout(r, 1500));
  const entered = await page.evaluate(() => !!document.querySelector('.q-box'));
  console.log('进入练习:', entered);

  // 选第一选项并提交
  const opts = await page.$$('.opt');
  console.log('选项数:', opts.length);
  await opts[0].click();
  await new Promise(r => setTimeout(r, 300));
  const submitBtn = await page.evaluateHandle(() => [...document.querySelectorAll('button')].find(b => b.textContent.trim() === '提交'));
  await submitBtn.asElement().click();
  await new Promise(r => setTimeout(r, 1200));
  const fb = await page.evaluate(() => {
    const m = document.querySelector('.main');
    const badge = m.querySelector('.badge.err, .badge.ok');
    return { hasColor: !!m.querySelector('.opt-correct, .opt-wrong'), badge: badge ? badge.textContent.trim() : '' };
  });
  console.log('提交反馈:', JSON.stringify(fb));

  // 下一题
  const nextBtn = await page.evaluateHandle(() => [...document.querySelectorAll('button')].find(b => b.textContent.includes('下一题')));
  await nextBtn.asElement().click();
  await new Promise(r => setTimeout(r, 800));
  console.log('进度:', await page.evaluate(() => document.querySelector('.num').textContent.trim()));

  // 答题卡
  console.log('答题卡数量:', (await page.$$('.dot-btn')).length);
  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
