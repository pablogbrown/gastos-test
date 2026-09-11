#!/usr/bin/env node
// Generates the 3-panel evidence dashboard (index.html) inside a run directory.
//
// The report.html template it renders ships alongside this script in the same
// references/ directory.
//
// Usage: node report.mjs --run e2e/results/<run-id> [--plan e2e/testplan.json]

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--run') args.run = argv[++i];
    else if (argv[i] === '--plan') args.plan = argv[++i];
  }
  if (!args.run) { console.error('e2e-evidence: missing --run <run directory>'); process.exit(2); }
  return args;
}

const args = parseArgs(process.argv.slice(2));
const resultsPath = path.join(args.run, 'results.json');
if (!fs.existsSync(resultsPath)) { console.error(`e2e-evidence: no results.json in ${args.run}`); process.exit(2); }

const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));
const plan = args.plan && fs.existsSync(args.plan) ? JSON.parse(fs.readFileSync(args.plan, 'utf8')) : null;

const template = fs.readFileSync(path.join(here, 'report.html'), 'utf8');
// </script> inside the embedded JSON would terminate the data block early.
const data = JSON.stringify({ results, plan }).replace(/</g, '\\u003c');
const html = template.replace('/*__DATA__*/', data);

const out = path.join(args.run, 'index.html');
fs.writeFileSync(out, html);
console.log(`REPORT=${out}`);
