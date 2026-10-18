// Tests for the heavy-job lock (#318):  node --test tools/harness/heavy.test.mjs
//
// tools/harness/heavy.sh lets N heavy jobs (default 2) run at a time across every agent, review and
// worktree, queues the rest first come first served, and tells the queued job how many are ahead. The
// real script runs here, in a throwaway lock folder (HARNESS_HEAVY_DIR); no model is called. The last
// two tests run lib/opencode.mjs's idle watch against a fake OpenCode whose command waits in the real
// queue: the idle limit must not count that wait.

import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { runOpenCodeWatched } from './lib/opencode.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(here, '..', '..');
const HEAVY = path.join(here, 'heavy.sh');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let tmp; let seq = 0;
before(() => { tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'heavy-test-')); });
after(() => { fs.rmSync(tmp, { recursive: true, force: true }); });
// one lock folder per test, so tests never queue behind one another
const lockEnv = (extra = {}) => ({
  ...process.env, HARNESS_HEAVY_DIR: path.join(tmp, `locks-${++seq}`), HARNESS_HEAVY_SLOTS: '2', HARNESS_HEAVY_POLL: '0.1',
  HARNESS_HEAVY_HELD: '', ...extra,
});

// A job: heavy.sh <name> -- sh -c 'echo started; sleep S; echo ended'. Resolves with the times (ms) at which
// the parent saw "started" and the process end, its stderr and its exit code.
function job(env, name, seconds, { weight = 1, command } = {}) {
  const t0 = Date.now();
  const args = [...(weight > 1 ? ['--weight', String(weight)] : []), name, '--', ...(command ?? ['sh', '-c', `echo started; sleep ${seconds}; echo ended`])];
  const child = spawn(HEAVY, args, { env, stdio: ['ignore', 'pipe', 'pipe'] });
  const j = { child, t0, started: null, ended: null, stderr: '', stdout: '', code: undefined };
  j.startedP = new Promise((res) => { j.markStarted = res; });
  child.stdout.on('data', (d) => {
    j.stdout += d;
    if (j.started === null && /started/.test(j.stdout)) { j.started = Date.now(); j.markStarted(); }
  });
  child.stderr.on('data', (d) => { j.stderr += d; });
  j.done = new Promise((res) => child.on('close', (code) => { j.code = code; j.ended = Date.now(); res(j); }));
  return j;
}

test('DW1: three jobs, two slots: the third waits ("waiting for a slot (0 ahead)") and runs when one ends', async () => {
  const env = lockEnv();
  const a = job(env, 'a', 1.5);
  await a.startedP;
  const b = job(env, 'b', 1.5);
  await b.startedP;
  const c = job(env, 'c', 0.2);
  await Promise.all([a.done, b.done, c.done]);
  assert.equal(a.code, 0); assert.equal(b.code, 0); assert.equal(c.code, 0);
  // the first two ran at the same time ...
  assert.ok(b.started < a.ended, 'b started before a ended');
  // ... the third did not start until one of them ended, and then did
  assert.ok(c.started >= Math.min(a.ended, b.ended) - 50, `c started ${Math.min(a.ended, b.ended) - c.started} ms before a slot freed`);
  assert.match(c.stderr, /heavy: c: waiting for a slot \(0 ahead\)/);
  assert.match(c.stderr, /heavy: c: got slot [01] after \d+ s/);
  assert.doesNotMatch(a.stderr + b.stderr, /waiting/);
});

test('DW1b: the queue is first come first served, and says how many are ahead', async () => {
  const env = lockEnv({ HARNESS_HEAVY_SLOTS: '1' });
  const jobs = [];
  for (let i = 1; i <= 4; i++) { jobs.push(job(env, `j${i}`, 1.5)); await sleep(250); }
  await Promise.all(jobs.map((j) => j.done));
  const starts = jobs.map((j) => j.started);
  assert.deepEqual([...starts].sort((x, y) => x - y), starts, 'started in the order they were submitted');
  for (let i = 1; i < 4; i++) assert.ok(jobs[i].started >= jobs[i - 1].ended - 50, `j${i + 1} waited for j${i}`);
  assert.equal(jobs[0].stderr, '');
  assert.match(jobs[1].stderr, /waiting for a slot \(0 ahead\)/);
  assert.match(jobs[2].stderr, /waiting for a slot \(1 ahead\)/);
  assert.match(jobs[3].stderr, /waiting for a slot \(2 ahead\)/);
});

test('the command runs in place: its exit status, stdout and arguments come through', async () => {
  const env = lockEnv();
  const r = spawnSync(HEAVY, ['x', '--', 'sh', '-c', 'echo "got $1"; exit 7', 'sh', 'two words'], { env, encoding: 'utf8' });
  assert.equal(r.status, 7);
  assert.equal(r.stdout, 'got two words\n');
});

test('a job started inside a heavy job runs at once and takes no slot (no deadlock on a full machine)', async () => {
  const env = lockEnv({ HARNESS_HEAVY_SLOTS: '1' });
  const r = spawnSync(HEAVY, ['outer', '--', HEAVY, 'inner', '--', 'echo', 'inner ran'], { env, encoding: 'utf8', timeout: 10_000 });
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout, 'inner ran\n');
  assert.doesNotMatch(r.stderr, /waiting/);
});

test('--weight 2 holds both slots: another job waits for it; a weight over the slots is refused', async () => {
  const env = lockEnv();
  const w = job(env, 'w', 1.2, { weight: 2 });
  await w.startedP;
  const x = job(env, 'x', 0.1);
  await Promise.all([w.done, x.done]);
  assert.ok(x.started >= w.ended - 50, 'x waited for the weight-2 job');
  assert.match(x.stderr, /waiting for a slot/);
  const r = spawnSync(HEAVY, ['--weight', '3', 'y', '--', 'true'], { env: lockEnv(), encoding: 'utf8' });
  assert.equal(r.status, 2);
  assert.match(r.stderr, /--weight 3 is more than the 2 slots/);
});

test('a job killed with SIGKILL frees its slot', async () => {
  const env = lockEnv({ HARNESS_HEAVY_SLOTS: '1' });
  const a = job(env, 'victim', 0, { command: ['sh', '-c', 'echo started; exec sleep 30'] });
  await a.startedP;
  const b = job(env, 'next', 0.1);
  await sleep(500);
  assert.equal(b.started, null, 'next is queued while the slot is held');
  a.child.kill('SIGKILL'); // heavy.sh exec'd into sh, then sleep: the process is the holder
  await b.done;
  assert.equal(b.code, 0);
  assert.ok(b.started !== null);
});

test('a queued job killed with SIGKILL leaves no entry that blocks the one behind it', async () => {
  const env = lockEnv({ HARNESS_HEAVY_SLOTS: '1', HARNESS_HEAVY_STALE_SEC: '0' });
  const holder = job(env, 'holder', 2.5);
  await holder.startedP;
  const dead = job(env, 'dead', 0.1);
  await sleep(400);
  dead.child.kill('SIGKILL');
  await dead.done;
  await sleep(1200); // an entry younger than the stale limit (whole seconds) is kept
  const behind = job(env, 'behind', 0.1);
  await sleep(300);
  assert.match(behind.stderr, /waiting for a slot \(0 ahead\)/, 'the dead entry is not counted ahead');
  await Promise.all([holder.done, behind.done]);
  assert.equal(behind.code, 0);
});

test('while it waits it touches $HARNESS_HEAVY_QUEUE_FILE (review.mjs\'s idle clock reads it)', async () => {
  const queue = path.join(tmp, 'queue-file');
  fs.writeFileSync(queue, '');
  const old = new Date(Date.now() - 3_600_000);
  fs.utimesSync(queue, old, old);
  const env = lockEnv({ HARNESS_HEAVY_SLOTS: '1', HARNESS_HEAVY_QUEUE_FILE: queue });
  const a = job(env, 'a', 1);
  await a.startedP;
  const b = job(env, 'b', 0.1);
  await sleep(500);
  assert.ok(Date.now() - fs.statSync(queue).mtimeMs < 1000, 'touched within the last second');
  await Promise.all([a.done, b.done]);
});

test('the number of slots comes from harness.json (heavy.slots), default 2; --status shows the slots', () => {
  const mk = (cfg) => {
    const root = fs.mkdtempSync(path.join(tmp, 'tree-'));
    fs.mkdirSync(path.join(root, 'tools', 'harness'), { recursive: true });
    fs.copyFileSync(HEAVY, path.join(root, 'tools', 'harness', 'heavy.sh'));
    fs.chmodSync(path.join(root, 'tools', 'harness', 'heavy.sh'), 0o755);
    if (cfg) fs.writeFileSync(path.join(root, 'harness.json'), JSON.stringify(cfg));
    return path.join(root, 'tools', 'harness', 'heavy.sh');
  };
  const env = (extra) => { const e = lockEnv(extra); delete e.HARNESS_HEAVY_SLOTS; return e; };
  const status = (script) => spawnSync(script, ['--status'], { env: env(), encoding: 'utf8' }).stdout;
  assert.match(status(mk({ heavy: { slots: 3 } })), /0 of 3 slots busy/);
  assert.match(status(mk({})), /0 of 2 slots busy/);
  assert.match(status(mk(null)), /0 of 2 slots busy/);
  assert.match(status(mk({ heavy: { slots: 4 } })), /slot 3: free/);
  assert.match(status(HEAVY), new RegExp(`0 of ${JSON.parse(fs.readFileSync(path.join(REPO, 'harness.json'), 'utf8')).heavy.slots} slots busy`));
  const bad = spawnSync(HEAVY, ['--slots', 'x', 'a', '--', 'true'], { env: env(), encoding: 'utf8' });
  assert.equal(bad.status, 2);
});

// ---- the idle limit does not count the queue ----------------------------------------------------------------
// A fake OpenCode: `run` writes its session once (updated = now, never again) and then runs a command through
// the real heavy.sh behind a slot another job holds for HOLD seconds; the idle limit is 2 s.
const FAKE_OC = `
import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
const [cmd, ...rest] = process.argv.slice(2);
const state = process.env.FAKE_STATE;
if (cmd === '--version') console.log('1.18.34');
else if (cmd === 'session') console.log(fs.existsSync(state) ? fs.readFileSync(state, 'utf8') : '[]');
else if (cmd === 'export') console.log(JSON.stringify({ info: { agent: 'reviewer' }, messages: [] }));
else if (cmd === 'run') {
  const title = rest[rest.indexOf('--title') + 1];
  fs.writeFileSync(state, JSON.stringify([{ id: 'ses_fake', title, directory: process.cwd(), created: Date.now(), updated: Date.now() }]));
  spawnSync(process.env.HEAVY_SH, ['reviewer-suite', '--', 'true'], { stdio: 'inherit', env: process.env });
  console.log('review done');
} else process.exit(1);
`;

async function idleRun(withQueueFile) {
  const env = lockEnv({ HARNESS_HEAVY_SLOTS: '1' });
  const work = fs.mkdtempSync(path.join(tmp, 'work-'));
  const oc = path.join(work, 'oc.mjs');
  fs.writeFileSync(oc, FAKE_OC);
  const queueFile = path.join(work, 'queue-file');
  fs.writeFileSync(queueFile, '');
  const runEnv = { ...env, FAKE_STATE: path.join(work, 'state.json'), HEAVY_SH: HEAVY, HARNESS_HEAVY_QUEUE_FILE: queueFile };
  const holder = job(env, 'holder', 4.5); // holds the only slot for 4.5 s, longer than the 2 s idle limit
  await holder.startedP;
  try {
    return await runOpenCodeWatched({
      args: ['run'], prompt: 'brief', workDir: work, title: 'idle-test', opencode: { exe: process.execPath, prefix: [oc] },
      startupTimeoutMs: 20_000, totalTimeoutMs: 60_000, idleTimeoutMs: 2000, pollMs: 200, logDir: work, env: runEnv,
      ...(withQueueFile ? { queueFile } : {}),
    });
  } finally { await holder.done; }
}

test('DW2: without the queue file a command queued longer than the idle limit is killed as idle', async () => {
  await assert.rejects(idleRun(false), /session idle for 2 s/);
});

test('DW2: with the queue file the same wait is not idleness, and the run comes back', async () => {
  const r = await idleRun(true);
  assert.equal(r.exitCode, 0);
  assert.match(r.stdout, /review done/);
  assert.match(r.stderr, /heavy: reviewer-suite: waiting for a slot \(0 ahead\)/);
});
