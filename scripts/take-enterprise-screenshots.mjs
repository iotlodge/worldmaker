import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, '..', 'docs', 'screenshots');
mkdirSync(OUT, { recursive: true });

const BASE = 'http://localhost:3000';

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await ctx.newPage();

  async function setTheme(mode) {
    const btn = page.getByRole('button', { name: `Switch to ${mode} mode` });
    await btn.click().catch(() => {});
    await page.waitForTimeout(400);
  }

  async function shot(name, opts = {}) {
    const fp = opts.fullPage ?? false;
    for (const theme of ['light', 'dark']) {
      await setTheme(theme.charAt(0).toUpperCase() + theme.slice(1));
      await page.screenshot({
        path: join(OUT, `${name}-${theme}.png`),
        fullPage: fp,
        type: 'png',
      });
      console.log(`  ✓ ${name}-${theme}.png`);
    }
  }

  // ── Enterprise Business View (9 platform cards) ─────────────────────
  console.log('Enterprise Business View...');
  await page.goto(`${BASE}/enterprise`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await shot('enterprise', { fullPage: true });

  // ── Enterprise Platform Detail ──────────────────────────────────────
  // Click the first platform card (Product Management)
  console.log('Enterprise Platform Detail...');
  const firstCard = page.locator('a[href^="/enterprise/"]').first();
  await firstCard.click();
  await page.waitForTimeout(1500);
  await shot('enterprise-detail', { fullPage: true });

  // ── Microservices page ──────────────────────────────────────────────
  console.log('Microservices...');
  await page.goto(`${BASE}/microservices`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('microservices');

  // ── Updated Dashboard (with Enterprise card) ────────────────────────
  console.log('Dashboard (updated)...');
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await shot('dashboard', { fullPage: true });

  await browser.close();
  console.log('\nDone! Enterprise screenshots saved to docs/screenshots/');
}

main().catch(e => { console.error(e); process.exit(1); });
