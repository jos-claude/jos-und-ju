// Screenshots der Vorschau (Playwright + SwiftShader).
//   node preview/shoot.js                 # alle Kamera-Presets -> out/shots/<name>.png
//   node preview/shoot.js hero spawn_040  # nur diese
//   <preset>_grau                          # Graustufen-Kontrolle (z. B. spawn_040_grau) + Helligkeit je Material (.json)
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'out', 'shots');
const W = 1600, H = 900;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.bin': 'application/octet-stream', '.png': 'image/png' };

function serve() {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      const u = decodeURIComponent(req.url.split('?')[0]);
      const f = path.join(ROOT, u);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
      if (req.method === 'HEAD') { res.end(); return; }
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const srv = await serve();
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.setDefaultTimeout(900000);
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.log('[browser]', m.text().slice(0, 400)); });
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  const t0 = Date.now();
  await page.goto(`http://127.0.0.1:${port}/preview/index.html?w=${W}&h=${H}&shot=none`, { timeout: 0 }).catch(() => {});
  await page.waitForFunction(() => window.__ready || window.__error || (window.presets && false), null, { timeout: 600000, polling: 500 }).catch(() => {});
  const err = await page.evaluate(() => window.__error);
  if (err) { console.error(err); }
  const all = await page.evaluate(() => window.presets || []);
  let want = process.argv.slice(2).length ? process.argv.slice(2) : [...all, 'spawn_040_grau', 'karte'];
  want = [...want.filter((n) => n !== 'karte'), ...want.filter((n) => n === 'karte')];   // Karte zuletzt (aendert Groesse)
  console.log(`geladen in ${((Date.now() - t0) / 1000).toFixed(1)} s, Stats:`, await page.evaluate(() => window.stats));
  for (const name of want) {
    const t = Date.now();
    if (name === 'karte') {
      await page.setViewportSize({ width: 1800, height: 1800 });
      await page.evaluate(() => window.shotMap(1800));
      await page.screenshot({ path: path.join(OUT, 'karte.png'), timeout: 600000 });
      console.log(`  karte.png (${((Date.now() - t) / 1000).toFixed(1)} s)`);
      continue;
    }
    if (name.endsWith('_grau')) {
      const base = name.slice(0, -5);
      await page.evaluate(() => window.setGray(true));
      await page.evaluate((n) => window.shot(n), base);
      await page.screenshot({ path: path.join(OUT, name + '.png'), timeout: 600000 });
      const st = await page.evaluate(() => window.grayStats());
      await page.evaluate(() => window.setGray(false));
      fs.writeFileSync(path.join(OUT, name + '.json'), JSON.stringify(st, null, 1));
      const g = st.Ground ? st.Ground.mean : null;
      const rows = Object.entries(st).sort((a, b) => b[1].pixels - a[1].pixels)
        .map(([m, v]) => `${m} ${v.mean.toFixed(3)}${g !== null && m !== 'Ground' ? ` (${(v.mean - g >= 0 ? '+' : '') + (v.mean - g).toFixed(3)})` : ''}`);
      console.log(`  ${name}.png  Helligkeit: ${rows.join(', ')}`);
      continue;
    }
    const ms = await page.evaluate((n) => window.shot(n), name);
    await page.screenshot({ path: path.join(OUT, name + '.png'), timeout: 600000 });
    console.log(`  ${name}.png (Render ${(ms / 1000).toFixed(1)} s, gesamt ${((Date.now() - t) / 1000).toFixed(1)} s)`);
  }
  await browser.close();
  srv.close();
})();
