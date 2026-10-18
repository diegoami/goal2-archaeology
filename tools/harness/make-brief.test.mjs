// Tests for make-brief.mjs (#180):  node --test tools/harness/make-brief.test.mjs
//
// The acceptance is review.mjs's own: the real review.mjs --dry-run runs in a throwaway repository with a
// fake gh (HARNESS_GH_EXE) and a fake OpenCode (HARNESS_OPENCODE_EXE), the two seams review.mjs offers for
// tests. The fake model records the brief it was handed, so the test also sees what the reviewer would read.

import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { buildBrief, checkBrief } from './make-brief.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(here, '..', '..');
const MAKE = path.join(here, 'make-brief.mjs');
const REVIEW = path.join(here, 'review.mjs');
const OTHER = 'a'.repeat(40); // some earlier head, full

const FAKE_GH = `
import fs from 'node:fs';
const a = process.argv.slice(2).join(' ');
if (a === '--version') process.exit(0);
// FAKE_OLD_UNTIL=N: the first N reads of the head answer FAKE_OLD_HEAD (GitHub not yet showing the push).
if (/^pr view \\d+ --json headRefOid/.test(a)) {
  let head = process.env.FAKE_HEAD;
  if (process.env.FAKE_OLD_UNTIL) {
    const f = process.env.FAKE_COUNT;
    const n = fs.existsSync(f) ? Number(fs.readFileSync(f, 'utf8')) : 0;
    fs.writeFileSync(f, String(n + 1));
    if (n < Number(process.env.FAKE_OLD_UNTIL)) head = process.env.FAKE_OLD_HEAD;
  }
  console.log(head);
} else if (/^pr view \\d+ --json headRefName/.test(a)) console.log(process.env.FAKE_BRANCH ?? 'no-such-branch');
else if (/^(pr|issue) view \\d+ --json labels/.test(a)) console.log('');
else if (/^issue view \\d+ --json title,body/.test(a)) console.log(JSON.stringify({ title: 'a fix', body: 'The body.\\n\\n**Done when:**\\n1. it works\\n2. it is tested\\n' }));
else { console.error('fake gh: unexpected ' + a); process.exit(1); }
`;

// Enough of OpenCode 1.18 for review.mjs: --version, models, session list, export, and a run that reads the
// brief file it is pointed at, copies it to FAKE_SEEN, and answers with a review under the brief's own first line.
const FAKE_OC = `
import fs from 'node:fs';
import path from 'node:path';
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
  fs.writeFileSync(process.env.FAKE_SEEN, brief);
  fs.writeFileSync(state, JSON.stringify([{ id: 'ses_fake', title, directory: process.cwd(), created: Date.now(), updated: Date.now() }]));
  const n = Number((/The task has (\\d+) Done-when/.exec(brief) ?? [])[1] ?? 0);
  const out = [brief.split('\\n')[0], 'approve', ...Array.from({ length: n }, (_, i) => 'DW' + (i + 1) + ': ran x → ok'), 'Final pass done', 'approve'];
  console.log(out.join('\\n'));
} else process.exit(1);
`;

const TASK = `# T99 a fixture task

- **Issue**: #5
- **Scope**: nothing, with a <placeholder-looking> word in it that is the task's own.
- **Done when**:
  1. the first thing passes
  2. the second thing passes
`;

let tmp; let repo; let head; let env; let seen;
const run = (exe, args, opts = {}) => spawnSync(process.execPath, [exe, ...args], { cwd: repo, env, encoding: 'utf8', ...opts });
const git = (...args) => {
  const r = spawnSync('git', args, { cwd: repo, encoding: 'utf8', env: { ...process.env, GIT_AUTHOR_NAME: 't', GIT_AUTHOR_EMAIL: 't@t', GIT_COMMITTER_NAME: 't', GIT_COMMITTER_EMAIL: 't@t' } });
  assert.equal(r.status, 0, r.stderr);
  return r.stdout.trim();
};
const make = (extra, out) => run(MAKE, ['--pr', '1', '--issue', '5', '--reviewer', 'luna', '--out', out, ...extra]);
const dry = (brief) => run(REVIEW, ['--pr', '1', '--brief', brief, '--dry-run']);

before(() => {
  tmp = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'make-brief-')));
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
  fs.writeFileSync(path.join(tmp, 'T99.md'), TASK);
  seen = path.join(tmp, 'seen.md');
  env = {
    ...process.env, FAKE_HEAD: head, FAKE_STATE: path.join(tmp, 'state.json'), FAKE_SEEN: seen,
    HARNESS_GH_EXE: path.join(tmp, 'gh.mjs'), HARNESS_OPENCODE_EXE: path.join(tmp, 'oc.mjs'),
    HARNESS_OPENCODE_HOME: path.join(tmp, 'ochome'), HARNESS_OPENCODE_AUTH_SOURCE: path.join(tmp, 'none.json'),
    HARNESS_SESSION_FAMILY: 'claude', ANTHROPIC_BASE_URL: '',
  };
});
after(() => { fs.rmSync(tmp, { recursive: true, force: true }); });

test('DW1: a brief for a fixture PR is accepted by review.mjs --dry-run (exit 0), and the model reads it', () => {
  const out = path.join(tmp, 'ok.md');
  const m = make(['--task', path.join(tmp, 'T99.md'), '--round', '2', '--sample', 'F40 seeds 1-5, 2 of O8, 2 of S', '--caveat', `an earlier head was ${OTHER.slice(0, 10)}`, '--protects', 'the fixture guard'], out);
  assert.equal(m.status, 0, m.stderr);
  const text = fs.readFileSync(out, 'utf8');
  assert.equal(text.split('\n')[0], 'T99 review (luna)');
  assert.match(text, new RegExp(`You review PR #1 at ${head}`));
  assert.match(text, /This is review round 2\.\nSample for this round: F40 seeds 1-5, 2 of O8, 2 of S\n/);
  assert.match(text, /# T99 a fixture task[\s\S]*the second thing passes/); // the task, in full
  assert.match(text, /## Blocking means[\s\S]*the fixture guard[\s\S]*## Report every blocking finding/);
  assert.doesNotMatch(text, /<name it|<project-specific/);
  const r = dry(out);
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /dry run: would post/);
  assert.match(r.stdout, /DW2: ran x/); // the two Done-when lines of the pasted task were counted
  const model = fs.readFileSync(seen, 'utf8'); // what the model was handed: the header first, the head named
  assert.equal(model.split('\n')[0], 'T99 review (luna)');
  assert.ok(model.includes(head));
});

test('DW1: without --task the issue body is pasted, and review.mjs accepts that brief too', () => {
  const out = path.join(tmp, 'issue.md');
  const m = make(['--protects', 'the fixture guard'], out);
  assert.equal(m.status, 0, m.stderr);
  const text = fs.readFileSync(out, 'utf8');
  assert.equal(text.split('\n')[0], 'fix #5 review (luna)');
  assert.match(text, /## Issue #5: a fix\n\nThe body\./);
  assert.equal(dry(out).status, 0);
});

test('DW2: the header on a second line is refused, by checkBrief and by review.mjs', () => {
  const good = path.join(tmp, 'ok.md');
  const lines = fs.readFileSync(good, 'utf8').split('\n');
  const bad = ['Round 2 of the review.', ...lines].join('\n');
  assert.throws(() => checkBrief(bad, head), /first line must be the review header/);
  const withCaveat = lines.join('\n').replace('T99 review (luna)', 'T99 review (luna) round 2, a caveat');
  assert.throws(() => checkBrief(withCaveat, head), /first line must be the review header/);
  const file = path.join(tmp, 'second-line.md');
  fs.writeFileSync(file, bad);
  const r = dry(file);
  assert.equal(r.status, 2);
  assert.match(r.stderr, /first line must be the review header/);
});

test('DW2: a placeholder left is refused, and nothing is written', () => {
  const out = path.join(tmp, 'placeholder.md');
  const m = make(['--task', path.join(tmp, 'T99.md')], out); // no --protects
  assert.equal(m.status, 2);
  assert.match(m.stderr, /placeholder remains: <name it/);
  assert.equal(fs.existsSync(out), false);
  const o = { header: 'T99 review (luna)', pr: 1, head, pasted: TASK, processMd: fs.readFileSync(path.join(REPO, 'docs', 'process.md'), 'utf8'), reviewBriefMd: fs.readFileSync(path.join(REPO, 'docs', 'review-brief.md'), 'utf8') };
  const built = buildBrief({ ...o, protects: 'x', blocking4: 'a <left over> item' });
  assert.throws(() => checkBrief(built.text, head, built.generated), /placeholder remains: <left over>/);
  const clean = buildBrief({ ...o, protects: 'x' });
  checkBrief(clean.text, head, clean.generated); // the same without it passes
  // a `<` in the task's own pasted text is not a placeholder (TASK has one)
  assert.match(clean.text, /<placeholder-looking>/);
});

test('DW2: a second full SHA is refused, by make-brief and by review.mjs', () => {
  const out = path.join(tmp, 'sha.md');
  const m = make(['--task', path.join(tmp, 'T99.md'), '--protects', 'x', '--caveat', `the head was at ${OTHER} before`], out);
  assert.equal(m.status, 2);
  assert.match(m.stderr, /another full commit SHA/);
  assert.equal(fs.existsSync(out), false);
  // the same brief written by hand, naming the other commit as the one to review, is what review.mjs refuses
  const text = fs.readFileSync(path.join(tmp, 'ok.md'), 'utf8').replace('Caveat:', `Caveat: review the work at ${OTHER}.`);
  assert.throws(() => checkBrief(text, head, text.split(/^# T99/m)[0]), /another full commit SHA/);
  const file = path.join(tmp, 'stale.md');
  fs.writeFileSync(file, text);
  const r = dry(file);
  assert.equal(r.status, 2);
  assert.match(r.stderr, /names a+ as the commit to review/);
});

// One test per guard of checkBrief, each on input only that guard rejects (its message is unique to it), so
// that deleting one guard fails its test. briefTargets (review.mjs's reader) sees only "at|HEAD is|HEAD: <sha>"
// before the task title, so the guard for any other full SHA is reached with an unqualified one.
const base = () => fs.readFileSync(path.join(tmp, 'ok.md'), 'utf8');
const headPart = (t) => t.split(/^# T99/m)[0];
const check = (t) => checkBrief(t, head, headPart(t));

test('guard: the header repeated below line 1 is refused', () => {
  const t = base().replace('This is review round 2.', 'T99 review (luna)');
  assert.throws(() => check(t), /header appears again below line 1/);
});

test('guard: a brief that does not name the head as the commit to review is refused', () => {
  const t = base().replaceAll(head, 'abcdef0123');
  assert.throws(() => check(t), /does not name the PR's head/);
});

test('guard: another full SHA named as the commit to review is refused', () => {
  const t = base().replace('Caveat:', `Caveat: review the work at ${OTHER}.`);
  assert.throws(() => check(t), /another full commit SHA/);
});

test('guard: an unqualified second full SHA in the head part is refused (briefTargets does not see it)', () => {
  const t = base().replace('Caveat:', `Caveat: the earlier head ${OTHER} was fine.`);
  assert.deepEqual([...new Set(headPart(t).match(/\b[0-9a-f]{40}\b/g))].sort(), [OTHER, head].sort());
  assert.throws(() => check(t), /second full SHA/);
  const out = path.join(tmp, 'sha2.md');
  const m = make(['--task', path.join(tmp, 'T99.md'), '--protects', 'x', '--caveat', `the earlier head ${OTHER} was fine`], out);
  assert.equal(m.status, 2);
  assert.match(m.stderr, /second full SHA/);
  assert.equal(fs.existsSync(out), false);
  // a short head is fine
  assert.equal(make(['--task', path.join(tmp, 'T99.md'), '--protects', 'x', '--caveat', `the earlier head ${OTHER.slice(0, 10)}`], out).status, 0);
});

test('guard: the command line is checked (nothing written)', () => {
  const out = path.join(tmp, 'args.md');
  const T = path.join(tmp, 'T99.md');
  const refuse = (argv, re, o = {}) => {
    const r = spawnSync(process.execPath, [MAKE, ...argv], { cwd: repo, env: { ...env, ...o }, encoding: 'utf8' });
    assert.equal(r.status, 2, argv.join(' '));
    assert.match(r.stderr, re);
    assert.equal(fs.existsSync(out), false);
  };
  const std = ['--pr', '1', '--issue', '5', '--reviewer', 'luna', '--protects', 'x', '--out', out, '--task', T];
  refuse(['--pr', '1', '--issue', '5', '--protects', 'x', '--out', out], /--reviewer is required/);
  refuse(['--pr', 'x', '--issue', '5', '--reviewer', 'luna', '--protects', 'x', '--out', out], /--pr takes a number/);
  refuse([...std, '--round', '0'], /--round takes a positive number/);
  refuse([...std.slice(0, -1), path.join(tmp, 'notatask.md')], /--task takes docs\/tasks\/T<nn>\.md/);
  fs.writeFileSync(path.join(tmp, 'T98.md'), 'no title line here\n');
  refuse([...std.slice(0, -1), path.join(tmp, 'T98.md')], /has no "# T<nn>" title line/);
  refuse(std, /head SHA could not be read/, { FAKE_HEAD: 'not-a-sha' });
});

// #234: a brief written seconds after a push named the head GitHub still showed, and review.mjs refused it.
// The fake gh answers the old head for the first reads, then the pushed one; the PR's branch is the fixture's
// local branch, so make-brief must wait for the pushed head and name it.
test('#234: make-brief waits until GitHub shows the local branch head, then names that head', () => {
  const out = path.join(tmp, 'race.md');
  const count = path.join(tmp, 'count.txt');
  fs.rmSync(count, { force: true });
  const e = { ...env, FAKE_BRANCH: git('branch', '--show-current'), FAKE_OLD_HEAD: OTHER, FAKE_OLD_UNTIL: '3', FAKE_COUNT: count, HARNESS_HEAD_POLL_SEC: '0.05', HARNESS_HEAD_WAIT_SEC: '30' };
  const r = spawnSync(process.execPath, [MAKE, '--pr', '1', '--issue', '5', '--reviewer', 'luna', '--protects', 'x', '--out', out], { cwd: repo, env: e, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stderr, /waited .* for GitHub to show the pushed head/);
  assert.ok(Number(fs.readFileSync(count, 'utf8')) >= 4); // polled past the three stale answers
  const text = fs.readFileSync(out, 'utf8');
  assert.match(text, new RegExp(`You review PR #1 at ${head}`));
  assert.doesNotMatch(text, new RegExp(OTHER));
  assert.equal(dry(out).status, 0); // and review.mjs accepts it
});

test('#234: GitHub never showing the local head writes nothing (exit 2)', () => {
  const out = path.join(tmp, 'never.md');
  const e = { ...env, FAKE_BRANCH: git('branch', '--show-current'), FAKE_OLD_HEAD: OTHER, FAKE_OLD_UNTIL: '1000000', FAKE_COUNT: path.join(tmp, 'count2.txt'), HARNESS_HEAD_POLL_SEC: '0.05', HARNESS_HEAD_WAIT_SEC: '0.3' };
  const r = spawnSync(process.execPath, [MAKE, '--pr', '1', '--issue', '5', '--reviewer', 'luna', '--protects', 'x', '--out', out], { cwd: repo, env: e, encoding: 'utf8' });
  assert.equal(r.status, 2);
  assert.match(r.stderr, /still shows the PR's head as a{40}/);
  assert.equal(fs.existsSync(out), false);
});

test('#234: no local branch, or a local branch behind GitHub, uses GitHub\'s head without waiting and says so', () => {
  const out = path.join(tmp, 'nolocal.md');
  const std = ['--pr', '1', '--issue', '5', '--reviewer', 'luna', '--protects', 'x', '--out', out];
  const none = spawnSync(process.execPath, [MAKE, ...std], { cwd: repo, env, encoding: 'utf8' }); // FAKE_BRANCH unset
  assert.equal(none.status, 0, none.stderr);
  assert.match(none.stderr, /no local branch of the PR/);
  git('branch', 'behind', head);
  git('checkout', '-q', '-b', 'ahead');
  fs.writeFileSync(path.join(repo, 'x.txt'), 'x\n');
  git('add', '-A');
  git('commit', '-q', '-m', 'ahead');
  const ahead = git('rev-parse', 'HEAD');
  const e = { ...env, FAKE_BRANCH: 'behind', FAKE_HEAD: ahead, HARNESS_HEAD_WAIT_SEC: '0' };
  const behind = spawnSync(process.execPath, [MAKE, ...std], { cwd: repo, env: e, encoding: 'utf8' });
  assert.equal(behind.status, 0, behind.stderr);
  assert.match(behind.stderr, /local branch is behind/);
  assert.match(fs.readFileSync(out, 'utf8'), new RegExp(`at ${ahead}`));
});

// #319 (the owner, 2026-10-18): a rework round re-runs a seeded sample, and the brief states it.
test('#319: the Rework rounds section is pasted in every brief, and a rework round names its sample', () => {
  const o = { header: 'T99 review (luna)', pr: 1, head, pasted: TASK, protects: 'x', processMd: fs.readFileSync(path.join(REPO, 'docs', 'process.md'), 'utf8'), reviewBriefMd: fs.readFileSync(path.join(REPO, 'docs', 'review-brief.md'), 'utf8') };
  const first = buildBrief(o);
  assert.match(first.text, /\n## Rework rounds: what you re-run/);
  assert.match(first.text, /sha256 against the\nimplementer's manifest/);
  assert.doesNotMatch(first.text, /^Sample for this round: /m);
  const one = buildBrief({ ...o, round: '1' });
  assert.doesNotMatch(one.text, /^Sample for this round: /m);
  const r2 = buildBrief({ ...o, round: '2', sample: 'F40 seeds 1-5' });
  assert.match(r2.text, /This is review round 2\.\nSample for this round: F40 seeds 1-5\n/);
  checkBrief(r2.text, head, r2.generated);
  assert.throws(() => buildBrief({ ...o, round: '2' }), /rework round: --sample TEXT is required/);
  assert.throws(() => buildBrief({ ...o, round: '3', sample: '' }), /--sample TEXT is required/);
  assert.throws(() => buildBrief({ ...o, sample: 'F40 seeds 1-5' }), /--sample belongs to a rework round/);
  assert.throws(() => buildBrief({ ...o, round: '1', sample: 'F40 seeds 1-5' }), /--sample belongs to a rework round/);
  // through the command: nothing is written without the sample
  const out = path.join(tmp, 'nosample.md');
  const m = make(['--task', path.join(tmp, 'T99.md'), '--protects', 'x', '--round', '2'], out);
  assert.equal(m.status, 2);
  assert.match(m.stderr, /--sample TEXT is required/);
  assert.equal(fs.existsSync(out), false);
  // the template without the section is refused
  assert.throws(() => buildBrief({ ...o, reviewBriefMd: o.reviewBriefMd.replace('## Rework rounds', '## Something else') }), /three sections/);
});
