const BASE = '/api';
async function api(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    let msg = 'HTTP ' + res.status;
    try { msg += ' ' + (await res.text()).slice(0, 200); } catch (e) {}
    throw new Error(msg);
  }
  return res.json();
}
export const http = {
  get: (p) => api(p),
  post: (p, body) => api(p, { method: 'POST', body: JSON.stringify(body || {}) }),
};
