const fs = require('fs');
const path = require('path');
const candidates = [
  'https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip',
  'https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip',
  'https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip'
];
const root = path.join(__dirname, '..');
const zipFile = path.join(root, 'python-embed.zip');
const pipFile = path.join(root, 'get-pip.py');
async function headOk(url){ try { const r = await fetch(url, { method:'HEAD', redirect:'follow' }); return r.ok; } catch { return false; } }
(async () => {
  let chosen = null;
  for (const c of candidates) { if (await headOk(c)) { chosen = c; break; } }
  if (!chosen) { console.error('NO_CANDIDATE'); process.exit(2); }
  console.log('DOWNLOADING', chosen);
  const res = await fetch(chosen);
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(zipFile, buf);
  console.log('ZIP_SAVED', zipFile, buf.length);
  const pr = await fetch('https://bootstrap.pypa.io/get-pip.py');
  const pb = Buffer.from(await pr.arrayBuffer());
  fs.writeFileSync(pipFile, pb);
  console.log('PIP_SAVED', pipFile, pb.length);
  console.log('DONE');
})();
