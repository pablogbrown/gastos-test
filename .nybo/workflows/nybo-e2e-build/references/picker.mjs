#!/usr/bin/env node
// e2e-evidence element picker: opens a headed browser on the target URL with a
// select-mode overlay. Every click while select mode is ON captures a stable
// selector (data-testid > id > role+name > name attr > css path) and appends it
// to the output JSON. Close the browser (or Ctrl+C) to finish.
//
// The picker-overlay.js it injects ships alongside this script in the same
// references/ directory.
//
// Usage: node picker.mjs --url http://localhost:5173 --out e2e/picked.json [--headless]

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const here = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const args = { headless: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--url') args.url = argv[++i];
    else if (argv[i] === '--out') args.out = argv[++i];
    else if (argv[i] === '--headless') args.headless = true;
  }
  if (!args.url || !args.out) {
    console.error('e2e-evidence: usage: picker.mjs --url <url> --out <picked.json> [--headless]');
    process.exit(2);
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
const picks = [];
let finished = false;

function save() {
  fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true });
  fs.writeFileSync(args.out, JSON.stringify(picks, null, 2));
}

function finish(browser) {
  if (finished) return;
  finished = true;
  save();
  console.log(`\n${picks.length} element(s) picked → ${args.out}`);
  console.log(`PICKED=${args.out}`);
  browser?.close().catch(() => {});
  process.exit(0);
}

const browser = await chromium.launch({ headless: args.headless });
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });

await context.exposeBinding('__e2e_pick', (_source, payload) => {
  picks.push(payload);
  save();
  console.log(`  picked: ${payload.selector}`);
});
await context.addInitScript({ path: path.join(here, 'picker-overlay.js') });

const page = await context.newPage();
page.on('close', () => finish(browser));
browser.on('disconnected', () => finish(null));
process.on('SIGINT', () => finish(browser));

await page.goto(args.url);
console.log(`e2e-evidence picker on ${args.url}`);
console.log('Select mode is ON — click elements to capture selectors; close the browser when done.');

// Keep the process alive until the browser goes away.
await new Promise(() => {});
