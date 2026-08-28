const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const zipFile = path.join(root, 'python-embed.zip');
const pipWheel = path.join(root, 'pip.whl');
const getPip = path.join(root, 'get-pip.py');

const PY_ZIP = 'https://mirrors.huaweicloud.com/python/3.12.10/python-3.12.10-embed-amd64.zip';
const PY_ZIP_ALT = 'https://registry.npmmirror.com/-/binary/python/3.12.10/python-3.12.10-embed-amd64.zip';
const GETPIP = 'https://bootstrap.pypa.io/get-pip.py';
const SIMPLE = 'https://mirrors.huaweicloud.com/pypi/web/simple/pip/';

async function download(url, dest) {
  const res = await fetch(url);
  if (!res.ok) throw new Error('HTTP ' + res.status + ' ' + url);
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(dest, buf);
  return buf.length;
}

(async () => {
  try {
    const n = await download(PY_ZIP, zipFile);
    console.log('PY_ZIP_OK', n);
  } catch (e) {
    console.log('PY_ZIP_MAIN_FAIL', e.message);
    const n = await download(PY_ZIP_ALT, zipFile);
    console.log('PY_ZIP_ALT_OK', n);
  }
  try {
    const n = await download(GETPIP, getPip);
    console.log('GETPIP_OK', n);
  } catch (e) {
    console.log('GETPIP_FAIL', e.message);
    const res = await fetch(SIMPLE);
    const html = await res.text();
    const m = html.match(/href="([^"]*pip-[0-9.]+-py3-none-any\.whl)"/g);
    if (!m) throw new Error('no pip wheel link found');
    const last = m[m.length - 1].match(/href="([^"]+)"/)[1];
    const url = last.startsWith('http') ? last : new URL(last, SIMPLE).href;
    const n = await download(url, pipWheel);
    console.log('PIP_WHEEL_OK', n, url);
  }
  console.log('SETUP_DOWNLOAD_DONE');
})();
