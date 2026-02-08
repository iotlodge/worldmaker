import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, '..', 'docs', 'screenshots');
mkdirSync(OUT, { recursive: true });

const BASE = 'http://localhost:3000';
const API  = 'http://localhost:8000/api/v1';

async function main() {
  console.log('WorldMaker Screenshot Capture');
  console.log('=============================\n');

  // ── Step 0: Generate ecosystem data ──────────────────────────
  console.log('Generating ecosystem data...');
  try {
    await fetch(`${API}/generate/reset`, { method: 'POST' });
    const res = await fetch(`${API}/generate?size=small&execute_flows=true`, { method: 'POST' });
    const data = await res.json();
    console.log(`  ✓ Generated: ${data.summary?.total_entities ?? '?'} entities\n`);
  } catch (e) {
    console.log(`  ⚠ Could not generate (API may already have data): ${e.message}\n`);
  }

  // Wait for data to settle
  await new Promise(r => setTimeout(r, 2000));

  // ── Launch browser ───────────────────────────────────────────
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await ctx.newPage();

  // Theme toggling helper
  async function setTheme(mode) {
    // The theme toggle button uses aria-label or title
    const btn = page.getByRole('button', { name: new RegExp(mode, 'i') });
    await btn.click().catch(() => {
      // Fallback: try clicking by text content
    });
    await page.waitForTimeout(400);
  }

  // Screenshot helper — captures light and dark versions
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

  // ── 1. Dashboard ─────────────────────────────────────────────
  console.log('\n1. Dashboard...');
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await shot('dashboard', { fullPage: true });

  // ── 2. Enterprise Business View ──────────────────────────────
  console.log('2. Enterprise Business View...');
  await page.goto(`${BASE}/enterprise`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await shot('enterprise', { fullPage: true });

  // ── 3. Enterprise Platform Detail ────────────────────────────
  console.log('3. Enterprise Platform Detail...');
  const firstPlatformCard = page.locator('a[href^="/enterprise/"]').first();
  await firstPlatformCard.click();
  await page.waitForTimeout(1500);
  await shot('enterprise-detail', { fullPage: true });

  // ── 4. Products ──────────────────────────────────────────────
  console.log('4. Products...');
  await page.goto(`${BASE}/products`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('products');

  // ── 5. Platforms ─────────────────────────────────────────────
  console.log('5. Platforms...');
  await page.goto(`${BASE}/platforms`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('platforms');

  // ── 6. Services ──────────────────────────────────────────────
  console.log('6. Services...');
  await page.goto(`${BASE}/services`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('services');

  // ── 7. Service Detail ────────────────────────────────────────
  console.log('7. Service Detail...');
  const firstServiceLink = page.locator('a[href^="/services/"]').first();
  await firstServiceLink.click().catch(() => {});
  await page.waitForTimeout(1500);
  await shot('service-detail', { fullPage: true });

  // ── 8. Microservices ─────────────────────────────────────────
  console.log('8. Microservices...');
  await page.goto(`${BASE}/microservices`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('microservices');

  // ── 9. Code Viewer ───────────────────────────────────────────
  console.log('9. Code Viewer...');
  // Click the first "repo" link to navigate to code viewer
  const repoLink = page.locator('a[href*="/code"]').first();
  await repoLink.click().catch(async () => {
    // Fallback: navigate directly to first microservice code page
    const msLink = page.locator('a[href^="/microservices/"]').first();
    const href = await msLink.getAttribute('href');
    if (href) await page.goto(`${BASE}${href}/code`, { waitUntil: 'networkidle' });
  });
  await page.waitForTimeout(1500);
  // Click the first file in the file list to show code
  const fileBtn = page.locator('button').filter({ hasText: /handler|main|Dockerfile/i }).first();
  await fileBtn.click().catch(() => {});
  await page.waitForTimeout(1000);
  await shot('code-viewer');

  // ── 10. Flows ────────────────────────────────────────────────
  console.log('10. Flows...');
  await page.goto(`${BASE}/flows`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('flows');

  // ── 11. Flow Detail ──────────────────────────────────────────
  console.log('11. Flow Detail...');
  const firstFlowLink = page.locator('a[href^="/flows/"]').first();
  await firstFlowLink.click().catch(() => {});
  await page.waitForTimeout(1500);
  await shot('flow-detail', { fullPage: true });

  // ── 12. Observability ────────────────────────────────────────
  console.log('12. Observability...');
  await page.goto(`${BASE}/observability`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('observability');

  // ── 13. Trace Detail ─────────────────────────────────────────
  console.log('13. Trace Detail...');
  const firstTrace = page.locator('a[href^="/observability/"]').first();
  await firstTrace.click().catch(() => {});
  await page.waitForTimeout(1500);
  // Click a span to show detail panel
  const spanBtn = page.locator('button').filter({ hasText: /Service.*\d+ms/ }).nth(2);
  await spanBtn.click().catch(() => {});
  await page.waitForTimeout(500);
  await shot('trace-detail');

  // ── 14. Risk Surface ─────────────────────────────────────────
  console.log('14. Risk Surface...');
  await page.goto(`${BASE}/risk-surface`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('risk-surface', { fullPage: true });

  // ── 15. Issue Discovery ──────────────────────────────────────
  console.log('15. Issue Discovery...');
  await page.goto(`${BASE}/issues`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('issues');

  // ── 16. Dependencies ─────────────────────────────────────────
  console.log('16. Dependencies...');
  await page.goto(`${BASE}/dependencies`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  // Try to select a service for visualization
  const depServiceBtn = page.locator('button').filter({ hasText: /Service/i }).first();
  await depServiceBtn.click().catch(() => {});
  await page.waitForTimeout(1500);
  await shot('dependencies');

  // ── 17. Attributes ───────────────────────────────────────────
  console.log('17. Attributes...');
  await page.goto(`${BASE}/attributes`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('attributes');

  // ── 18. Generator ────────────────────────────────────────────
  console.log('18. Generator...');
  await page.goto(`${BASE}/generator`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('generator');

  // ── 19. API Reference ────────────────────────────────────────
  console.log('19. API Reference...');
  await page.goto(`${BASE}/api-reference`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await shot('api-reference');

  await browser.close();
  console.log(`\nDone! ${19 * 2} screenshots saved to docs/screenshots/`);
}

main().catch(e => { console.error(e); process.exit(1); });
