#!/usr/bin/env node
// e2e-evidence runner: interprets a testplan.json and produces per-step
// evidence — screenshots with the target element highlighted, a video and a
// Playwright trace per case, plus a machine-readable results.json.
//
// Usage:
//   node runner.mjs --plan e2e/testplan.json --out e2e/results [--cases TC001,TC003] [--headed] [--timeout 10000]
//
// Exit codes: 0 = run completed (even with failing cases), 2 = infra error
// (plan missing, app unreachable, missing env var referenced by the plan).

import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const VIEWPORT = { width: 1280, height: 800 };

function parseArgs(argv) {
  const args = { headed: false, timeout: 10000 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--plan') args.plan = argv[++i];
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--cases') args.cases = argv[++i].split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--base-url') args.baseUrl = argv[++i];
    else if (a === '--timeout') args.timeout = Number(argv[++i]);
    else if (a === '--headed') args.headed = true;
    else fail(`Unknown argument: ${a}`);
  }
  if (!args.plan) fail('Missing --plan <path to testplan.json>');
  if (!args.out) fail('Missing --out <results directory>');
  return args;
}

function fail(msg) {
  console.error(`e2e-evidence: ${msg}`);
  process.exit(2);
}

function substEnv(value, caseId) {
  return String(value).replace(/\{\{ENV:([A-Za-z0-9_]+)\}\}/g, (_, name) => {
    const v = process.env[name];
    if (v === undefined) throw Object.assign(new Error(`Missing environment variable ${name} (referenced by ${caseId})`), { infra: true });
    return v;
  });
}

function resolveUrl(u, baseUrl) {
  if (/^https?:\/\//i.test(u)) return u;
  return new URL(u, baseUrl).toString();
}

function describeStep(step) {
  switch (step.action) {
    case 'navigate': return `Navigate to ${step.url}`;
    case 'fill': return `Fill '${step.value}' into ${step.selector}`;
    case 'click': return `Click ${step.selector}`;
    case 'select': return `Select '${step.value}' in ${step.selector}`;
    case 'press': return step.selector ? `Press '${step.value}' on ${step.selector}` : `Press '${step.value}'`;
    case 'wait': return step.selector ? `Wait for ${step.selector}` : `Wait ${step.ms} ms`;
    case 'assert':
      if (step.kind === 'visible') return `Verify that ${step.selector} is visible`;
      if (step.kind === 'text') return `Verify that ${step.selector} contains '${step.value}'`;
      if (step.kind === 'url') return `Verify that the URL contains '${step.value}'`;
      if (step.kind === 'count') return `Verify that ${step.selector} has ${step.value} matches`;
      return `Verify ${step.kind}`;
    default: return step.action;
  }
}

async function withHighlight(locator, timeout, fn) {
  const handle = await locator.elementHandle({ timeout }).catch(() => null);
  if (handle) {
    await handle.evaluate((el) => {
      window.__e2e_prev = { el, outline: el.style.outline, offset: el.style.outlineOffset };
      el.style.outline = '3px solid #22c55e';
      el.style.outlineOffset = '2px';
      const r = el.getBoundingClientRect();
      const b = document.createElement('div');
      b.id = '__e2e_badge';
      b.textContent = 'Current';
      Object.assign(b.style, {
        position: 'fixed',
        left: `${Math.max(Math.min(r.right - 60, window.innerWidth - 80), 8)}px`,
        top: `${Math.max(r.top - 28, 4)}px`,
        background: '#22c55e',
        color: '#052e16',
        font: '600 12px system-ui, sans-serif',
        padding: '3px 10px',
        borderRadius: '999px',
        zIndex: 2147483647,
        pointerEvents: 'none',
      });
      document.body.appendChild(b);
    }).catch(() => {});
  }
  try {
    return await fn();
  } finally {
    if (handle) {
      await handle.evaluate((el) => {
        document.getElementById('__e2e_badge')?.remove();
        const p = window.__e2e_prev;
        if (p && p.el === el) { el.style.outline = p.outline; el.style.outlineOffset = p.offset; }
        delete window.__e2e_prev;
      }).catch(() => {});
      await handle.dispose().catch(() => {});
    }
  }
}

async function runStep(page, step, ctx) {
  const { timeout, shot, baseUrl, caseId } = ctx;
  const locator = step.selector ? page.locator(step.selector).first() : null;
  const screenshots = [];

  switch (step.action) {
    case 'navigate': {
      await page.goto(resolveUrl(substEnv(step.url, caseId), baseUrl), { timeout, waitUntil: 'load' });
      screenshots.push(await shot(`step-${pad(step.n)}`));
      break;
    }
    case 'fill': {
      await locator.fill(substEnv(step.value, caseId), { timeout });
      await withHighlight(locator, timeout, async () => {
        screenshots.push(await shot(`step-${pad(step.n)}`));
      });
      break;
    }
    case 'select': {
      await locator.selectOption(substEnv(step.value, caseId), { timeout });
      await withHighlight(locator, timeout, async () => {
        screenshots.push(await shot(`step-${pad(step.n)}`));
      });
      break;
    }
    case 'click': {
      // Pre-click screenshot with the target highlighted, then the click, then
      // a post-click screenshot once the page settles (clicks often navigate).
      await locator.waitFor({ state: 'visible', timeout });
      await withHighlight(locator, timeout, async () => {
        screenshots.push(await shot(`step-${pad(step.n)}-target`));
      });
      await locator.click({ timeout });
      await page.waitForLoadState('load', { timeout }).catch(() => {});
      screenshots.push(await shot(`step-${pad(step.n)}`));
      break;
    }
    case 'press': {
      const key = substEnv(step.value, caseId);
      if (locator) await locator.press(key, { timeout });
      else await page.keyboard.press(key);
      screenshots.push(await shot(`step-${pad(step.n)}`));
      break;
    }
    case 'wait': {
      if (step.selector) await locator.waitFor({ state: 'visible', timeout: step.ms ?? timeout });
      else await page.waitForTimeout(step.ms ?? 1000);
      screenshots.push(await shot(`step-${pad(step.n)}`));
      break;
    }
    case 'assert': {
      const kind = step.kind ?? 'visible';
      if (kind === 'visible') {
        await locator.waitFor({ state: 'visible', timeout });
        await withHighlight(locator, timeout, async () => {
          screenshots.push(await shot(`step-${pad(step.n)}`));
        });
      } else if (kind === 'text') {
        const expected = substEnv(step.value, caseId);
        await locator.waitFor({ state: 'visible', timeout });
        const text = (await locator.textContent({ timeout })) ?? '';
        if (!text.includes(expected)) {
          throw new Error(`Text assertion failed: expected '${expected}' within ${step.selector}, got '${text.trim().slice(0, 200)}'`);
        }
        await withHighlight(locator, timeout, async () => {
          screenshots.push(await shot(`step-${pad(step.n)}`));
        });
      } else if (kind === 'url') {
        const expected = substEnv(step.value, caseId);
        const deadline = Date.now() + timeout;
        while (!page.url().includes(expected)) {
          if (Date.now() > deadline) throw new Error(`URL assertion failed: expected URL to contain '${expected}', got '${page.url()}'`);
          await page.waitForTimeout(100);
        }
        screenshots.push(await shot(`step-${pad(step.n)}`));
      } else if (kind === 'count') {
        const expected = Number(step.value);
        const deadline = Date.now() + timeout;
        let count = await page.locator(step.selector).count();
        while (count !== expected) {
          if (Date.now() > deadline) throw new Error(`Count assertion failed: expected ${expected} matches of ${step.selector}, got ${count}`);
          await page.waitForTimeout(100);
          count = await page.locator(step.selector).count();
        }
        screenshots.push(await shot(`step-${pad(step.n)}`));
      } else {
        throw new Error(`Unknown assert kind '${kind}'`);
      }
      break;
    }
    default:
      throw new Error(`Unknown action '${step.action}'`);
  }
  return screenshots;
}

const pad = (n) => String(n).padStart(2, '0');

async function runCase(browser, tc, ctx) {
  const { runDir, baseUrl, timeout } = ctx;
  const caseDir = path.join(runDir, tc.id);
  fs.mkdirSync(caseDir, { recursive: true });

  const context = await browser.newContext({
    viewport: VIEWPORT,
    recordVideo: { dir: caseDir, size: VIEWPORT },
  });
  await context.tracing.start({ screenshots: true, snapshots: true });
  const page = await context.newPage();

  // Auto-accept native dialogs (alert/confirm/prompt) so a step's click
  // isn't silently blocked — Playwright dismisses unhandled dialogs by
  // default, which would make confirm() return false and prompt() return
  // null, tripping any client-side guard that checks for that. prompt()
  // dialogs get a fixed default value since the generic action schema has
  // no per-step way to parameterize dialog input yet.
  page.on('dialog', async (dialog) => {
    try {
      if (dialog.type() === 'prompt') {
        await dialog.accept('e2e test note');
      } else {
        await dialog.accept();
      }
    } catch {
      // Dialog may already be handled/dismissed by a race with page navigation — ignore.
    }
  });

  const shot = async (name) => {
    const rel = `${tc.id}/${name}.png`;
    await page.screenshot({ path: path.join(runDir, rel) }).catch(() => {});
    return rel;
  };

  const result = { id: tc.id, title: tc.title, requirement: tc.requirement ?? '', status: 'passed', durationMs: 0, video: null, trace: null, steps: [] };
  const t0 = Date.now();
  let failed = false;

  for (const step of tc.steps) {
    const rec = {
      n: step.n,
      action: step.action,
      kind: step.kind,
      selector: step.selector,
      value: step.value, // template form on purpose — never the substituted secret
      url: step.url,
      description: describeStep(step),
      status: 'passed',
      durationMs: 0,
      screenshots: [],
    };
    if (failed) {
      rec.status = 'skipped';
      result.steps.push(rec);
      continue;
    }
    const s0 = Date.now();
    try {
      rec.screenshots = await runStep(page, step, { timeout, shot, baseUrl, caseId: tc.id });
    } catch (err) {
      if (err.infra) throw err;
      rec.status = 'failed';
      rec.error = String(err.message ?? err).split('\nCall log:')[0].trim();
      rec.screenshots.push(await shot(`step-${pad(step.n)}-error`));
      const domPath = path.join(runDir, tc.id, `step-${pad(step.n)}-dom.html`);
      await page.content().then((html) => fs.writeFileSync(domPath, html)).catch(() => {});
      rec.dom = `${tc.id}/step-${pad(step.n)}-dom.html`;
      failed = true;
      result.status = 'failed';
    }
    rec.durationMs = Date.now() - s0;
    result.steps.push(rec);
  }

  await context.tracing.stop({ path: path.join(caseDir, 'trace.zip') }).catch(() => {});
  result.trace = `${tc.id}/trace.zip`;
  const video = page.video();
  await context.close();
  if (video) {
    try {
      const vp = await video.path();
      const target = path.join(caseDir, 'video.webm');
      fs.renameSync(vp, target);
      result.video = `${tc.id}/video.webm`;
    } catch { /* video may be unavailable if the context died early */ }
  }
  result.durationMs = Date.now() - t0;
  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!fs.existsSync(args.plan)) fail(`Plan not found: ${args.plan}`);
  const plan = JSON.parse(fs.readFileSync(args.plan, 'utf8'));
  const baseUrl = args.baseUrl ?? plan.baseUrl;
  if (!baseUrl) fail('No baseUrl in plan and no --base-url given');

  let cases = plan.cases ?? [];
  if (args.cases) {
    const want = new Set(args.cases);
    cases = cases.filter((c) => want.has(c.id));
    const missing = [...want].filter((id) => !cases.some((c) => c.id === id));
    if (missing.length) fail(`Cases not in plan: ${missing.join(', ')}`);
  }
  if (!cases.length) fail('No cases to run');

  try {
    const res = await fetch(baseUrl, { signal: AbortSignal.timeout(5000) });
    void res;
  } catch {
    fail(`App is not reachable at ${baseUrl} — start your local server first`);
  }

  const runId = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19) + '-' + Math.random().toString(36).slice(2, 6);
  const runDir = path.join(args.out, runId);
  fs.mkdirSync(runDir, { recursive: true });

  const browser = await chromium.launch({ headless: !args.headed });
  const results = {
    runId,
    project: plan.project ?? '',
    baseUrl,
    startedAt: new Date().toISOString(),
    finishedAt: null,
    cases: [],
  };

  console.log(`e2e-evidence run ${runId} — ${cases.length} case(s) against ${baseUrl}\n`);
  for (const tc of cases) {
    process.stdout.write(`  ${tc.id} ${tc.title} ... `);
    try {
      const r = await runCase(browser, tc, { runDir, baseUrl, timeout: args.timeout });
      results.cases.push(r);
      console.log(r.status === 'passed' ? 'PASS' : 'FAIL');
    } catch (err) {
      if (err.infra) { await browser.close(); fail(err.message); }
      results.cases.push({ id: tc.id, title: tc.title, status: 'failed', durationMs: 0, steps: [], error: String(err.message ?? err) });
      console.log('ERROR');
    }
  }
  await browser.close();

  results.finishedAt = new Date().toISOString();
  fs.writeFileSync(path.join(runDir, 'results.json'), JSON.stringify(results, null, 2));

  const passed = results.cases.filter((c) => c.status === 'passed').length;
  console.log(`\n${passed}/${results.cases.length} passed · evidence in ${runDir}`);
  console.log(`RUN_DIR=${runDir}`);
}

main().catch((err) => fail(err.stack ?? String(err)));
