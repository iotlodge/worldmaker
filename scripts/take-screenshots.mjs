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

  // 1. Dashboard
  console.log('Dashboard...');
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await shot('dashboard', { fullPage: true });

  // 1b. Enterprise Business View
  console.log('Enterprise Business View...');
  await page.goto(`${BASE}/enterprise`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await shot('enterprise', { fullPage: true });

  // 1c. Enterprise Platform Detail (click first platform card)
  console.log('Enterprise Platform Detail...');
  const firstPlatformCard = page.locator('a[href^="/enterprise/"]').first();
  await firstPlatformCard.click();
  await page.waitForTimeout(1500);
  await shot('enterprise-detail', { fullPage: true });

  // 1d. Microservices
  console.log('Microservices...');
  await page.goto(`${BASE}/microservices`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('microservices');

  // 2. Risk Surface
  console.log('Risk Surface...');
  await page.goto(`${BASE}/risk-surface`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('risk-surface', { fullPage: true });

  // 3. Issue Discovery
  console.log('Issue Discovery...');
  await page.goto(`${BASE}/issues`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('issues');

  // 4. Observability list
  console.log('Observability...');
  await page.goto(`${BASE}/observability`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('observability');

  // 5. Trace detail — click the first trace row
  console.log('Trace Detail...');
  const firstTrace = page.locator('a[href^="/observability/"]').first();
  await firstTrace.click();
  await page.waitForTimeout(1500);
  // Click a span to show detail panel
  const spanBtn = page.locator('button').filter({ hasText: /Service.*\d+ms/ }).nth(2);
  await spanBtn.click().catch(() => {});
  await page.waitForTimeout(500);
  await shot('trace-detail');

  // 6. Services
  console.log('Services...');
  await page.goto(`${BASE}/services`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('services');

  // 7. Dependencies — select AuthService
  console.log('Dependencies...');
  await page.goto(`${BASE}/dependencies`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  const authBtn = page.getByRole('button', { name: /AuthService/i }).first();
  await authBtn.click().catch(() => {});
  await page.waitForTimeout(1500);
  await shot('dependencies');

  // 8. API Reference
  console.log('API Reference...');
  await page.goto(`${BASE}/api-reference`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('api-reference');

  await browser.close();
  console.log('\nDone! Screenshots saved to docs/screenshots/');
}

main().catch(e => { console.error(e); process.exit(1); });
