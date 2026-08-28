const fs = require('fs');
const path = require('path');
const SIMPLE = 'https://mirrors.aliyun.com/pypi/simple/pip/';
(async () => {
  const res = await fetch(SIMPLE);
  const html = await res.text();
  const re = /href="([^"]+pip-([0-9.]+)-py3-none-any\.whl)#sha256=/g;
  let mm; const found = [];
  while ((mm = re.exec(html)) !== null) {
    found.push({ ver: mm[2], rel: mm[1] });
  }
  if (!found.length) throw new Error('no wheel links; html len=' + html.length);
  found.sort((a, b) => {
    const pa = a.ver.split('.').map(Number);
    const pb = b.ver.split('.').map(Number);
    for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
      const d = (pb[i] || 0) - (pa[i] || 0);
      if (d) return d;
    }
    return 0;
  });
  const best = found[0];
  const url = best.rel.startsWith('http') ? best.rel : new URL(best.rel, SIMPLE).href;
  const r = await fetch(url);
  const buf = Buffer.from(await r.arrayBuffer());
  fs.writeFileSync(path.join(__dirname, '..', 'pip.whl'), buf);
  console.log('PIP_WHEEL_OK', 'ver=' + best.ver, url, buf.length);
})();
