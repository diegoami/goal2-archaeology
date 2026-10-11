// End-to-end checks of a resumed run (Sol's R2 and R4-R7 on PR 114), on a throwaway repository with
// a fake OpenCode and a fake gh (HARNESS_OPENCODE_EXE, HARNESS_GH_EXE): no model, no network.
//   - the runner refuses a session of another directory before anything runs (R2);
//   - a resumed session's idle clock starts with the run, not with its old `updated` time (R7);
//   - implement.mjs keeps a worktree its idle limit stopped (R5), forwards --session to the run
//     (R6) and refuses a session of another worktree before running (R2);
//   - review.mjs keeps a review worktree its idle limit stopped and resumes it with --session (R4).
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { runOpenCodeWatched, OpenCodeInfraError } from './opencode.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));

const FAKE_OPENCODE = `import fs from 'node:fs'; import path from 'node:path';
const dir = process.env.FAKE_DIR; const argv = process.argv.slice(2);
const sfile = path.join(dir, 'sessions.json');
const sessions = () => (fs.existsSync(sfile) ? JSON.parse(fs.readFileSync(sfile, 'utf8')) : []);
const opt = (k) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : null; };
if (argv[0] === '--version') { console.log('1.18.34'); process.exit(0); }
if (argv[0] === 'models') { console.log('fake/fake-1\\nfake/other-1'); process.exit(0); }
if (argv[0] === 'session') { console.log(JSON.stringify(sessions())); process.exit(0); }
if (argv[0] === 'export') { console.log(JSON.stringify({ info: { agent: argv.includes('--agent') ? null : process.env.FAKE_AGENT }, messages: [] })); process.exit(0); }
if (argv[0] === 'run') {
  fs.appendFileSync(path.join(dir, 'runs.jsonl'), JSON.stringify(argv) + '\\n');
  fs.appendFileSync(path.join(dir, 'foo.txt'), (process.env.FOO ?? '') + '\\n');
  const wd = fs.realpathSync(opt('--dir'));
  const sid = opt('--session');
  if (!sid) {
    const s = sessions(); const now = Date.now();
    s.push({ id: 'ses_fake' + s.length, title: opt('--title'), directory: wd, created: now, updated: now });
    fs.writeFileSync(sfile, JSON.stringify(s));
    fs.writeFileSync(path.join(wd, 'wip.txt'), 'uncommitted\\n');
    setTimeout(() => {}, 600000);
  } else {
    fs.writeFileSync(path.join(wd, 'resumed.txt'), sid);
    setTimeout(() => { process.stdout.write(process.env.FAKE_OUTPUT || 'done\\n'); process.exit(0); }, Number(process.env.FAKE_RESUME_MS || 0));
  }
}
`;
const FAKE_GH = `const a = process.argv.slice(2);
if (a[0] === 'pr' && a[1] === 'view' && a.includes('headRefOid')) console.log(process.env.FAKE_HEAD);
process.exit(0);
`;

export async function resumeSelfTest() {
  const failures = [];
  const ok = (what, cond) => { if (!cond) failures.push(what); };
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'resume-selftest-')));
  const fake = path.join(root, 'fake');
  fs.mkdirSync(fake);
  const ocExe = path.join(root, 'opencode.mjs');
  const ghExe = path.join(root, 'gh.mjs');
  fs.writeFileSync(ocExe, FAKE_OPENCODE);
  fs.writeFileSync(ghExe, FAKE_GH);
  const env = {
    ...process.env, FAKE_DIR: fake, HARNESS_OPENCODE_EXE: ocExe, HARNESS_GH_EXE: ghExe,
    HARNESS_OPENCODE_HOME: path.join(root, 'oc'), HARNESS_QUOTA_URL: 'http://127.0.0.1:9',
    GIT_AUTHOR_NAME: 't', GIT_AUTHOR_EMAIL: 't@invalid', GIT_COMMITTER_NAME: 't', GIT_COMMITTER_EMAIL: 't@invalid',
  };
  const runs = () => (fs.existsSync(path.join(fake, 'runs.jsonl'))
    ? fs.readFileSync(path.join(fake, 'runs.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l)) : []);
  const lastFoo = () => fs.readFileSync(path.join(fake, 'foo.txt'), 'utf8').split('\n').at(-2);
  const setSessions = (list) => fs.writeFileSync(path.join(fake, 'sessions.json'), JSON.stringify(list));
  const sessions = () => JSON.parse(fs.readFileSync(path.join(fake, 'sessions.json'), 'utf8'));
  const opencode = { exe: process.execPath, prefix: [ocExe] };
  try {
    // 1. The runner, directly.
    const wd = path.join(root, 'wd');
    fs.mkdirSync(wd);
    setSessions([{ id: 'ses_old', title: 'old', directory: wd, created: 1000, updated: 1000 },
      { id: 'ses_far', title: 'far', directory: path.join(root, 'elsewhere'), created: 1000, updated: 1000 }]);
    let refused = null;
    try {
      await runOpenCodeWatched({ args: ['run', '--dir', wd], prompt: 'p', workDir: wd, title: 't', sessionId: 'ses_far', opencode, env, logDir: path.join(root, 'logs') });
    } catch (e) { refused = e; }
    ok('runner: a session of another directory is refused (R2)', refused instanceof OpenCodeInfraError && refused.reason === 'session not resumable');
    ok('runner: nothing runs for a refused session (R2)', runs().length === 0);
    let run = null;
    try {
      run = await runOpenCodeWatched({
        args: ['run', '--dir', wd], prompt: 'p', workDir: wd, title: 't', sessionId: 'ses_old', opencode,
        env: { ...env, FAKE_RESUME_MS: '1500' }, logDir: path.join(root, 'logs'), pollMs: 200, idleTimeoutMs: 2500, totalTimeoutMs: 20000,
      });
    } catch (e) { run = e; }
    ok('runner: an old resumed session is not idle at once (R7)', run && run.exitCode === 0);
    const last = runs().at(-1) ?? [];
    ok('runner: --session reaches opencode run', last[last.indexOf('--session') + 1] === 'ses_old');
    ok('runner: a resumed run sets no new title', !last.includes('--title'));

    // 2. implement.mjs and review.mjs, end to end.
    const origin = path.join(root, 'origin.git');
    const repo = path.join(root, 'repo');
    const git = (cwd, ...args) => {
      const r = spawnSync('git', args, { cwd, env, encoding: 'utf8' });
      if (r.status !== 0) throw new Error(`git ${args.join(' ')}: ${r.stderr}`);
      return r.stdout.trim();
    };
    git(root, 'init', '-q', '--bare', origin);
    git(root, 'init', '-q', '-b', 'main', repo);
    git(repo, 'config', 'commit.gpgsign', 'false');
    fs.writeFileSync(path.join(repo, 'harness.json'), JSON.stringify({
      worktreeRoot: '../work',
      models: { fake: { id: 'fake/fake-1', family: 'fakeimpl' }, rev: { id: 'fake/other-1', family: 'fakerev' } },
      implementer: { agent: 'implementer', chain: ['fake'], startupTimeoutSec: 30, idleTimeoutSec: 3, totalTimeoutSec: 120 },
      reviewer: { agent: 'reviewer', chain: ['rev'], claudeFallback: null, startupTimeoutSec: 30, idleTimeoutSec: 3, totalTimeoutSec: 120 },
      jail: { enabled: false },
    }));
    fs.mkdirSync(path.join(repo, '.opencode', 'agents'), { recursive: true });
    for (const ag of ['implementer', 'reviewer']) fs.writeFileSync(path.join(repo, '.opencode', 'agents', `${ag}.md`), `---\ndescription: ${ag}\n---\n`);
    git(repo, 'add', '-A');
    git(repo, 'commit', '-q', '-m', 'init');
    git(repo, 'remote', 'add', 'origin', origin);
    git(repo, 'push', '-q', 'origin', 'main');
    const brief = path.join(root, 'brief.md');
    fs.writeFileSync(brief, 'Do the task.\n');
    const node = (script, args, extra = {}) => spawnSync(process.execPath, [path.join(here, '..', script), ...args],
      { cwd: repo, env: { ...env, ...extra }, encoding: 'utf8', timeout: 120000 });
    // The resumed runs are made by the printed `Resume:` command itself (Sol's R1 on PR 114, round 2),
    // its <placeholders> filled in, never by the test's own argument arrays: what the user would run.
    const printed = (out) => {
      const line = out.split('\n').find((l) => l.includes('Resume: '))?.split('Resume: ')[1] ?? '';
      const toks = [...line.matchAll(/'((?:[^']|'\\'')*)'|(\S+)/g)].map((m) => (m[1] ?? m[2]).replace(/'\\''/g, "'"));
      return { line, script: toks[1], args: toks.slice(2).map((t) => (t === '<longer>' ? '120' : t === '<continue-brief-file>' ? brief : t)) };
    };
    const nodeAt = (script, args, extra = {}) => spawnSync(process.execPath, [path.join(here, '..', '..', '..', script), ...args],
      { cwd: repo, env: { ...env, ...extra }, encoding: 'utf8', timeout: 120000 });
    const implArgs = ['--task', 'T01', '--slug', 'x', '--brief', brief, '--model', 'fake'];
    const tree = path.join(root, 'work', 'T01');

    setSessions([]);
    const before = runs().length;
    const r1 = node('implement.mjs', [...implArgs, '--env', 'FOO=bar'], { FAKE_AGENT: 'implementer' });
    const out1 = `${r1.stdout}\n${r1.stderr}`;
    ok('implement: an idle-stopped run exits 1', r1.status === 1);
    const rp1 = printed(out1);
    ok('implement: an idle-stopped run names its resume command', /Resume: .*--session ses_fake0/.test(out1));
    ok('implement: the resume command keeps the original --env (R1)', /--env FOO=bar\b/.test(rp1.line));
    ok('implement: the resume command asks for a brief and a longer limit', /--brief <[^>]+>/.test(rp1.line) && /--total-timeout-sec <longer>/.test(rp1.line));
    ok('implement: an idle-stopped worktree keeps its uncommitted work (R5)', fs.existsSync(path.join(tree, 'wip.txt')));

    setSessions([...sessions(), { id: 'ses_other', title: 'o', directory: path.join(root, 'elsewhere'), created: 1, updated: 1 }]);
    const n2 = runs().length;
    const r2 = node('implement.mjs', [...implArgs, '--session', 'ses_other'], { FAKE_AGENT: 'implementer' });
    ok('implement: a session of another worktree is refused with exit 2 (R2)', r2.status === 2);
    ok('implement: nothing runs for a refused session (R2)', runs().length === n2);

    const r3 = nodeAt(rp1.script, rp1.args, { FAKE_AGENT: 'implementer' });
    const l3 = runs().at(-1) ?? [];
    ok('implement: --session reaches opencode run (R6)', runs().length === n2 + 1 && l3[l3.indexOf('--session') + 1] === 'ses_fake0');
    const resumed = path.join(tree, 'resumed.txt');
    ok('implement: the resumed run ran in the kept worktree', fs.existsSync(resumed) && fs.readFileSync(resumed, 'utf8') === 'ses_fake0');
    ok('implement: the resumed run still gets the original --env (R1)', lastFoo() === 'bar');
    ok('implement: the resumed run kept the earlier work', fs.existsSync(path.join(tree, 'wip.txt')));
    ok('implement: the resumed run ended at "no open PR"', r3.status === 1 && /No open PR/.test(r3.stderr));
    ok('implement: the first run started fresh', runs()[before] && !runs()[before].includes('--session'));

    // review.mjs: a PR head at refs/pull/7/head.
    git(repo, 'checkout', '-q', '-b', 'pr7');
    fs.writeFileSync(path.join(repo, 'change.txt'), 'x\n');
    git(repo, 'add', 'change.txt');
    git(repo, 'commit', '-q', '-m', 'change');
    const head = git(repo, 'rev-parse', 'HEAD');
    git(repo, 'push', '-q', 'origin', 'HEAD:refs/pull/7/head');
    git(repo, 'checkout', '-q', 'main');
    const rbrief = path.join(root, 'review-brief.md');
    fs.writeFileSync(rbrief, 'PR7 review (rev)\nReview it.\n');
    const revArgs = ['--pr', '7', '--brief', rbrief, '--reviewer', 'rev', '--exclude', 'fakeimpl', '--dry-run', '--done-when', '0'];
    const rv1 = node('review.mjs', [...revArgs, '--env', 'FOO=bar'], { FAKE_AGENT: 'reviewer', FAKE_HEAD: head });
    const outR = `${rv1.stdout}\n${rv1.stderr}`;
    const rp2 = printed(outR);
    const kept = outR.match(/--worktree (\S+)/)?.[1];
    const sid = outR.match(/--session (ses_\w+)/)?.[1];
    ok('review: the resume command keeps --dry-run, --exclude and --done-when (R1)',
      /--dry-run\b/.test(rp2.line) && /--exclude fakeimpl\b/.test(rp2.line) && /--done-when 0\b/.test(rp2.line));
    ok('review: an idle-stopped review exits 3 with its resume command', rv1.status === 3 && kept && sid);
    ok('review: an idle-stopped review keeps its worktree (R4)', Boolean(kept) && fs.existsSync(kept));
    const review = 'PR7 review (rev)\nrework\nR1 - change.txt:1, blocking\nFinal pass done\nrework\n';
    const rv2 = kept && sid ? nodeAt(rp2.script, rp2.args, { FAKE_AGENT: 'reviewer', FAKE_HEAD: head, FAKE_OUTPUT: review }) : null;
    const lr = runs().at(-1) ?? [];
    ok('review: --session resumes the kept review (R4)', rv2?.status === 0 && lr[lr.indexOf('--session') + 1] === sid);
    ok('review: the resumed review is read and planned', /^PR7 review \(rev\)$/m.test(rv2?.stdout ?? '') && /dry run: would post the above/.test(rv2?.stdout ?? ''));
    ok('review: the resumed review still gets the original --env (R1)', lastFoo() === 'bar');
    ok('review: the resumed review is still a dry run, never posted (R1)', !/posted:/.test(`${rv2?.stdout}\n${rv2?.stderr}`));
    ok('review: the resumed tree is removed once done', Boolean(kept) && !fs.existsSync(kept));
    if (failures.length) failures.push(`(resume self-test logs: implement ${r1.status}/${r3.status}, review ${rv1.status}/${rv2?.status}; ${(rv2?.stderr || rv1.stderr || r3.stderr).slice(-400)})`);
  } finally {
    if (!failures.length) fs.rmSync(root, { recursive: true, force: true });
    else failures.push(`kept for diagnosis: ${root}`);
  }
  return failures;
}
