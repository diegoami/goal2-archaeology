// Tests for the reviewer's scratch folder (#311):  node --test tools/harness/review-scratch.test.mjs
//
// /tmp is an 11 GB RAM-backed tmpfs shared with other projects; it hit 100% and a review died of ENOSPC.
// review.mjs now points TMPDIR (TMP, TEMP) at a folder of the run's own on the real disk, removes it when
// the run comes back, keeps it when the run fails, and refuses to start when /tmp AND that disk are short.
// The real review.mjs runs in a throwaway repository with a fake gh (HARNESS_GH_EXE) and a fake OpenCode
// (HARNESS_OPENCODE_EXE), the two seams review.mjs offers for tests (as make-brief.test.mjs does). No model
// is called.

import { test, before, after, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { scratchRoot, rootProblem, spaceProblem, removeScratch, tmpEnv, harnessDir } from './lib/scratch.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(here, '..', '..');
const REVIEW = path.join(here, 'review.mjs');

const FAKE_GH = `
import fs from 'node:fs';
const argv = process.argv.slice(2);
const a = argv.join(' ');
if (a === '--version') process.exit(0);
if (/^pr view \\d+ --json headRefOid/.test(a)) console.log(process.env.FAKE_HEAD);
else if (/^(pr|issue) view \\d+ --json labels/.test(a)) console.log('');
else if (/^pr comment \\d+ --body-file /.test(a)) {
  const f = argv[argv.indexOf('--body-file') + 1];
  fs.writeFileSync(process.env.FAKE_POSTED, fs.readFileSync(f, 'utf8')); // the body file must exist when gh reads it
} else { console.error('fake gh: unexpected ' + a); process.exit(1); }
`;

// A run that records the environment it was given, writes a big-ish file where TMPDIR points (as a reviewer
// would), and answers with a review under the brief's own first line. FAKE_FAIL=1: it exits 1 instead.
const FAKE_OC = `
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
const [cmd, ...rest] = process.argv.slice(2);
const state = process.env.FAKE_STATE;
if (cmd === '--version') console.log('1.18.34');
else if (cmd === 'models') console.log('openai/gpt-5.6-luna');
else if (cmd === 'session') console.log(fs.existsSync(state) ? fs.readFileSync(state, 'utf8') : '[]');
else if (cmd === 'export') console.log(JSON.stringify({ info: { agent: 'reviewer' }, messages: [] }));
else if (cmd === 'run') {
  const title = rest[rest.indexOf('--title') + 1];
  const briefFile = fs.readdirSync(process.cwd()).find((f) => f.startsWith('.harness-brief-'));
  const brief = fs.readFileSync(path.join(process.cwd(), briefFile), 'utf8');
  const t = process.env.TMPDIR;
  fs.writeFileSync(process.env.FAKE_ENV, JSON.stringify({
    TMPDIR: process.env.TMPDIR, TMP: process.env.TMP, TEMP: process.env.TEMP, osTmpdir: os.tmpdir(),
    existed: fs.existsSync(t), brief,
  }));
  fs.writeFileSync(path.join(t, 'copy-of-main.bin'), Buffer.alloc(1 << 20)); // a reviewer's big scratch file
  fs.writeFileSync(state, JSON.stringify([{ id: 'ses_fake', title, directory: process.cwd(), created: Date.now(), updated: Date.now() }]));
  if (process.env.FAKE_FAIL) { console.error('fake model failed'); process.exit(1); }
  const out = [brief.split('\\n')[0], 'approve', 'Final pass done', 'approve'];
  console.log(out.join('\\n'));
} else process.exit(1);
`;

const BRIEF = `T99 review (luna)
You review PR #1. The task file follows.

## Issue #5: a fix
The body. No Done-when lines here.
`;

let tmp; let repo; let head; let base; let rootN = 0;
const git = (...args) => {
  const r = spawnSync('git', args, { cwd: repo, encoding: 'utf8', env: { ...process.env, GIT_AUTHOR_NAME: 't', GIT_AUTHOR_EMAIL: 't@t', GIT_COMMITTER_NAME: 't', GIT_COMMITTER_EMAIL: 't@t' } });
  assert.equal(r.status, 0, r.stderr);
  return r.stdout.trim();
};
// A fresh scratch root per test, under the throwaway directory.
let root; let envFile; let posted; let state;
const review = (extra = {}, args = ['--dry-run']) => spawnSync(process.execPath, [REVIEW, '--pr', '1', '--brief', path.join(tmp, 'brief.md'), ...args], {
  cwd: repo, encoding: 'utf8', env: { ...base, ...extra },
});
const runFolders = () => (fs.existsSync(root) ? fs.readdirSync(root).filter((n) => /^1-review-[0-9a-f]{8}$/.test(n)) : []);

before(() => {
  tmp = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'review-scratch-')));
  const origin = path.join(tmp, 'origin.git');
  repo = path.join(tmp, 'repo');
  spawnSync('git', ['init', '-q', '--bare', origin]);
  spawnSync('git', ['clone', '-q', origin, repo]);
  fs.mkdirSync(path.join(repo, '.opencode', 'agents'), { recursive: true });
  fs.copyFileSync(path.join(REPO, '.opencode', 'agents', 'reviewer.md'), path.join(repo, '.opencode', 'agents', 'reviewer.md'));
  const cfg = JSON.parse(fs.readFileSync(path.join(REPO, 'harness.json'), 'utf8'));
  cfg.jail = { enabled: false };
  fs.writeFileSync(path.join(repo, 'harness.json'), JSON.stringify(cfg));
  fs.writeFileSync(path.join(repo, 'README.md'), 'fixture\n');
  git('add', '-A');
  git('commit', '-q', '-m', 'fixture');
  git('push', '-q', 'origin', 'HEAD:main');
  head = git('rev-parse', 'HEAD');
  spawnSync('git', ['--git-dir', origin, 'update-ref', 'refs/pull/1/head', head]);
  fs.writeFileSync(path.join(tmp, 'gh.mjs'), FAKE_GH);
  fs.writeFileSync(path.join(tmp, 'oc.mjs'), FAKE_OC);
  fs.writeFileSync(path.join(tmp, 'brief.md'), BRIEF);
});
after(() => { fs.rmSync(tmp, { recursive: true, force: true }); });
beforeEach(() => {
  root = path.join(tmp, `scratch-root-${++rootN}`);
  envFile = path.join(tmp, `env-${rootN}.json`);
  posted = path.join(tmp, `posted-${rootN}.md`);
  state = path.join(tmp, `state-${rootN}.json`);
  base = {
    ...process.env, FAKE_HEAD: head, FAKE_STATE: state, FAKE_ENV: envFile, FAKE_POSTED: posted,
    HARNESS_GH_EXE: path.join(tmp, 'gh.mjs'), HARNESS_OPENCODE_EXE: path.join(tmp, 'oc.mjs'),
    HARNESS_OPENCODE_HOME: path.join(tmp, 'ochome'), HARNESS_OPENCODE_AUTH_SOURCE: path.join(tmp, 'none.json'),
    HARNESS_SESSION_FAMILY: 'claude', ANTHROPIC_BASE_URL: '', HARNESS_SCRATCH_ROOT: root,
  };
});

test('DW1: review.mjs sets TMPDIR, TMP and TEMP to a folder of the run under the scratch root, and cleans it when the run comes back', () => {
  const r = review();
  assert.equal(r.status, 0, r.stdout + r.stderr);
  const seen = JSON.parse(fs.readFileSync(envFile, 'utf8'));
  assert.equal(path.dirname(seen.TMPDIR), root);
  assert.match(path.basename(seen.TMPDIR), /^1-review-[0-9a-f]{8}$/);
  assert.equal(seen.TMP, seen.TMPDIR);
  assert.equal(seen.TEMP, seen.TMPDIR);
  assert.equal(seen.osTmpdir, seen.TMPDIR); // what a Node tool in the run calls the temp directory
  assert.equal(seen.existed, true); // created before the model started, so it could write there
  assert.ok(seen.brief.includes(seen.TMPDIR), 'the run\'s rules name the scratch folder');
  assert.match(seen.brief, /never under \/tmp/);
  assert.deepEqual(runFolders(), []); // and removed once the review was read, with its 1 MB file
});

test('DW1: a run that fails keeps its folder (the message names it) and the file in it', () => {
  const r = review({ FAKE_FAIL: '1' });
  assert.equal(r.status, 3, r.stdout + r.stderr);
  const seen = JSON.parse(fs.readFileSync(envFile, 'utf8'));
  assert.deepEqual(runFolders(), [path.basename(seen.TMPDIR)]);
  assert.ok(fs.existsSync(path.join(seen.TMPDIR, 'copy-of-main.bin')));
  assert.ok(r.stdout.includes(`scratch folder kept: ${seen.TMPDIR}`), r.stdout);
});

test('DW2: with /tmp unwritable (TMPDIR of the harness itself unusable) a review completes, posts, and the model still gets its folder', () => {
  // A path below a regular file: neither mkdir nor a write works there, root or not.
  const blocker = path.join(tmp, 'a-file');
  fs.writeFileSync(blocker, 'x');
  const dead = path.join(blocker, 'tmp');
  const r = review({ TMPDIR: dead, TMP: dead, TEMP: dead }, []); // not a dry run: the comment body is written too
  assert.equal(r.status, 0, r.stdout + r.stderr);
  const seen = JSON.parse(fs.readFileSync(envFile, 'utf8'));
  assert.equal(path.dirname(seen.TMPDIR), root); // the model's TMPDIR is the scratch folder, not the dead one
  assert.match(fs.readFileSync(posted, 'utf8'), /T99 review \(luna\)/); // gh read the body file it was given
  assert.ok(fs.existsSync(path.join(root, 'harness-logs')), 'the harness\'s own logs moved to the scratch root');
  assert.deepEqual(runFolders(), []);
});

test('DW2: harnessDir falls back to the scratch root when the temp directory is unwritable or short of room', () => {
  const blocker = path.join(tmp, 'a-file-2');
  fs.writeFileSync(blocker, 'x');
  assert.equal(harnessDir(root, { tmp: path.join(blocker, 'tmp') }), path.join(root, 'harness-logs'));
  const ok = path.join(tmp, 'roomy');
  assert.equal(harnessDir(root, { tmp: ok, free: () => 10 * 1024 * 1024 * 1024 }), path.join(ok, 'harness-opencode'));
  assert.equal(harnessDir(root, { tmp: ok, free: () => 1024 }), path.join(root, 'harness-logs'));
});

test('DW3: both /tmp and the scratch disk short of room refuses the review, naming both, before the model runs', () => {
  const r = review({ HARNESS_MIN_TMP_MB: '99999999999', HARNESS_MIN_SCRATCH_MB: '99999999999' });
  assert.equal(r.status, 1, r.stdout + r.stderr);
  assert.match(r.stderr, /Refused: \/tmp has \d+ MB free \(under 99999999999\) and the scratch folder .* has \d+ MB free \(under 99999999999\)/);
  assert.equal(fs.existsSync(envFile), false); // the model was never started
  assert.deepEqual(runFolders(), []);
});

test('DW3: only one of them short is not a refusal', () => {
  const a = review({ HARNESS_MIN_TMP_MB: '99999999999' });
  assert.equal(a.status, 0, a.stdout + a.stderr);
  const b = review({ HARNESS_MIN_SCRATCH_MB: '99999999999' });
  assert.equal(b.status, 0, b.stdout + b.stderr);
});

test('spaceProblem names which filesystem is short, and treats an unknown one as enough', () => {
  const free = (m) => (p) => m[p];
  const gb = 1024 ** 3;
  const mb = 1024 ** 2;
  assert.equal(spaceProblem({ root: '/r', free: free({ '/tmp': 600 * mb, '/r': 1 * gb }) }), null); // /tmp ok
  assert.equal(spaceProblem({ root: '/r', free: free({ '/tmp': 100 * mb, '/r': 3 * gb }) }), null); // scratch ok
  const both = spaceProblem({ root: '/r', free: free({ '/tmp': 100 * mb, '/r': 1 * gb }) });
  assert.match(both, /\/tmp has 100 MB free \(under 500\)/);
  assert.match(both, /scratch folder \/r has 1024 MB free \(under 2048\)/);
  assert.equal(spaceProblem({ root: '/r', free: free({ '/tmp': 100 * mb, '/r': null }) }), null); // unknown: not a refusal
});

test('the default scratch root is ~/goal2-review-tmp; a dot element in it is refused', () => {
  assert.equal(scratchRoot({ HOME: '/home/x' }), '/home/x/goal2-review-tmp');
  assert.equal(rootProblem('/home/x/goal2-review-tmp'), null);
  assert.match(rootProblem('/home/x/.cache/goal2-review-tmp'), /dot element \(\.cache\)/);
  const r = review({ HARNESS_SCRATCH_ROOT: path.join(tmp, '.hidden', 'root') });
  assert.equal(r.status, 2, r.stdout + r.stderr);
  assert.match(r.stderr, /dot element/);
  assert.equal(fs.existsSync(envFile), false);
});

test('removeScratch removes only a folder directly inside the root, and tmpEnv sets all three variables', () => {
  assert.throws(() => removeScratch('/a/root', '/a/root/x/y'), /Refusing to remove/);
  assert.throws(() => removeScratch('/a/root', '/a'), /Refusing to remove/);
  assert.throws(() => removeScratch('/a/root', '/a/root/../other'), /Refusing to remove/);
  assert.deepEqual(tmpEnv('/d'), { TMPDIR: '/d', TMP: '/d', TEMP: '/d' });
});
