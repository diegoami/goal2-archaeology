#!/usr/bin/env node
// Native deletion controls for the OpenCode 2 operand guard (#262; after goal2 PR 178's
// check-opencode-guard-controls.mjs, but on a scratch copy: the tracked files are never edited).
//
//   node tools/harness/check-opencode-guard-controls.mjs --out <dir>
//
// For each control, tools/harness and the reviewer agent file are copied to a scratch folder, one guard
// line is removed there, and the copy's tools/harness/probe-opencode-guard.mjs runs against the real
// 2.0.28 binary with its loopback fake provider (no provider contacted, nothing billed). The probe must
// then FAIL on the named assertion: without the guard, v2 lets `cat <outside file>` run. Logs and a
// results.json go to a new native-controls-* folder of --out.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const outIndex = process.argv.indexOf('--out');
assert(outIndex > 0 && process.argv[outIndex + 1], '--out DIRECTORY is required');
const parent = path.resolve(process.argv[outIndex + 1]); fs.mkdirSync(parent, { recursive: true });
const root = fs.mkdtempSync(path.join(parent, 'native-controls-'));
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const cases = [
  { name: 'operand-loss', file: 'tools/harness/opencode-guard/scanner.mjs', before: 'directories.add(isDirectory ? absolute : path.dirname(absolute));', after: ';', assertion: 'external-cat must be rejected' },
  { name: 'approval-loss', file: 'tools/harness/opencode-guard/guard.mjs', before: "if (!matches || scanned.outcome !== 'allow') {", after: 'if (false) {', assertion: 'external-cat must be rejected' },
];
const results = [];
for (const item of cases) {
  const copy = fs.mkdtempSync(path.join(os.homedir(), `harness-guard-control-${item.name}-`)); // not /tmp: it is granted
  try {
    fs.cpSync(path.join(repo, 'tools', 'harness'), path.join(copy, 'tools', 'harness'), { recursive: true });
    fs.mkdirSync(path.join(copy, '.opencode', 'agents'), { recursive: true });
    fs.copyFileSync(path.join(repo, '.opencode', 'agents', 'reviewer.md'), path.join(copy, '.opencode', 'agents', 'reviewer.md'));
    const target = path.join(copy, item.file); const saved = fs.readFileSync(target, 'utf8');
    assert(saved.includes(item.before), `${item.name}: mutation target must exist`);
    fs.writeFileSync(target, saved.replace(item.before, item.after));
    const directory = path.join(root, item.name); fs.mkdirSync(directory);
    const result = spawnSync(process.execPath, [path.join(copy, 'tools/harness/probe-opencode-guard.mjs'), '--out', directory], { encoding: 'utf8', timeout: 240000, maxBuffer: 5e6 });
    fs.writeFileSync(path.join(directory, 'stdout.log'), result.stdout || '');
    fs.writeFileSync(path.join(directory, 'stderr.log'), result.stderr || '');
    const output = (result.stdout || '') + (result.stderr || '');
    assert.equal(result.status, 1, `${item.name}: the probe must fail without the guard line`);
    assert(output.includes(item.assertion), `${item.name}: intended native assertion`);
    assert(!/MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND|timed out/.test(output), `${item.name}: behavioural failure required`);
    results.push({ name: item.name, status: result.status, assertion: item.assertion, externalModelCalls: 0 });
  } finally { fs.rmSync(copy, { recursive: true, force: true }); }
}
fs.writeFileSync(path.join(root, 'results.json'), JSON.stringify(results, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ root, results }));
