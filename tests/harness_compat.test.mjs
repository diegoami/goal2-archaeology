import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { resolveOpenCode } from '../tools/harness/lib/opencode.mjs';
import { sessionFamily } from '../tools/harness/lib/common.mjs';

function fixture(t, version = 'opencode v2.0.3') {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-compat-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const binary = (name, ver) => {
    const file = path.join(dir, name);
    fs.writeFileSync(file, `#!${process.execPath}\nconsole.log(${JSON.stringify(ver)});\n`, { mode: 0o755 });
    return file;
  };
  const exe = binary('opencode', version);
  return { dir, binary, exe, env: { PATH: dir, HOME: dir } };
}
const unix = { skip: process.platform === 'win32' };
test('v2 selects verified opencode.bak without adding v2 flags', unix, (t) => {
  const f = fixture(t);
  const backup = f.binary('opencode.bak', '1.18.34');
  assert.deepEqual(resolveOpenCode(f.env), { exe: backup, prefix: [] });
});
test('v1 stays selected even when a backup exists', unix, (t) => {
  const f = fixture(t, '1.18.34'); f.binary('opencode.bak', '1.18.32');
  assert.equal(resolveOpenCode(f.env).exe, f.exe);
});
test('incompatible backup is skipped for versioned 1.x backup', unix, (t) => {
  const f = fixture(t); f.binary('opencode.bak', '2.1.0');
  const backup = f.binary('opencode.1.18.32.bak', '1.18.32');
  assert.equal(resolveOpenCode(f.env).exe, backup);
});
test('v2 without a compatible backup stops with actionable error', unix, (t) => {
  const f = fixture(t); f.binary('opencode.bak', 'garbage');
  assert.throws(() => resolveOpenCode(f.env), /no working 1.x opencode.bak/);
});
test('explicit executable pin remains authoritative', unix, (t) => {
  const f = fixture(t); f.binary('opencode.bak', '1.18.34');
  assert.equal(resolveOpenCode({ ...f.env, HARNESS_OPENCODE_EXE: f.exe }).exe, f.exe);
});
test('Codex family detection prevents OpenAI reviews, with explicit override first', () => {
  assert.equal(sessionFamily({ CODEX_THREAD_ID: 'thread', ANTHROPIC_BASE_URL: 'https://api.z.ai/api/anthropic' }), 'openai');
  assert.equal(sessionFamily({ CODEX_CI: '1' }), 'openai');
  assert.equal(sessionFamily({ CODEX_THREAD_ID: 'thread', HARNESS_SESSION_FAMILY: 'glm' }), 'glm');
  assert.equal(sessionFamily({}), 'claude');
  assert.equal(sessionFamily({ ANTHROPIC_BASE_URL: 'https://api.z.ai/api/anthropic' }), 'glm');
  assert.equal(sessionFamily({ ANTHROPIC_BASE_URL: 'https://unknown.example' }), null);
});

// #303: harness.lock pins every copied file that is not adapted; a pinned line whose file differs
// is a defect (four were stale on main, found by the #264 implementer). The lock's own verify line
// is `grep -E '^[0-9a-f]{64}  ' harness.lock | sha256sum -c --quiet`; this is the same check.
const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const sha = (data) => crypto.createHash('sha256').update(data).digest('hex');
function lockMismatches(lockText, root) {
  const bad = [];
  for (const line of lockText.split('\n')) {
    const m = /^([0-9a-f]{64}) {2}(.+)$/.exec(line);
    if (!m) continue;
    const file = path.join(root, m[2]);
    if (!fs.existsSync(file)) bad.push(`${m[2]}: missing`);
    else if (sha(fs.readFileSync(file)) !== m[1]) bad.push(`${m[2]}: hash differs`);
  }
  return bad;
}
test('every pinned line of harness.lock matches its file (an intended change is an adapt line)', () => {
  const lock = fs.readFileSync(path.join(REPO, 'harness.lock'), 'utf8');
  assert.ok(lock.split('\n').filter((l) => /^[0-9a-f]{64} {2}/.test(l)).length >= 10, 'the lock should still pin its unchanged copied files (a parse that finds none checks nothing)');
  assert.deepEqual(lockMismatches(lock, REPO), []);
});
test('the lock check reports a wrong hash and a missing file, and skips adapt lines', (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-lock-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  fs.writeFileSync(path.join(dir, 'a.txt'), 'one\n');
  fs.writeFileSync(path.join(dir, 'b.txt'), 'two\n');
  assert.deepEqual(lockMismatches(`${sha('one\n')}  a.txt\n${sha('two\n')}  b.txt\n`, dir), []);
  assert.deepEqual(lockMismatches(`${sha('one\n')}  a.txt\n${sha('other\n')}  b.txt\n`, dir), ['b.txt: hash differs']);
  assert.deepEqual(lockMismatches(`${sha('one\n')}  gone.txt\n`, dir), ['gone.txt: missing']);
  assert.deepEqual(lockMismatches('adapt b.txt  (changed on purpose)\n', dir), []);
});
