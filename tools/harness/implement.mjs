#!/usr/bin/env node
// Runs one task's (or one fix's) implementer on OpenCode, in a worktree this script creates.
//
//   node tools/harness/implement.mjs --task T07 --slug calendar --issue 12 --brief brief.md [--model NAME]
//   node tools/harness/implement.mjs --fix 34 --slug save-path --brief brief.md
//     [--model NAME]         a harness.json key, or any OpenCode id the user names: provider/model[@variant]
//     [--session ses_...]    resume that session in the kept worktree (needs --model); the brief is
//                            then the short "continue where you stopped" message
//     [--total-timeout-sec N] [--idle-timeout-sec N]   override harness.json's limits for this run
//     [--copy local.ini]...  untracked files copied from the main checkout into the worktree
//     [--env KEY=VALUE]...   environment for the run
//   node tools/harness/implement.mjs --self-test   (the reset's save, on a throwaway repository)
//
// The main session fills the brief (the task file pasted in full, plus review URLs on a rework
// round). This script creates or resumes the branch and worktree, runs OpenCode watched, and checks
// the handover: a PR exists, the worktree is clean, pushed and detached.
//
// The model is the one the user chose, passed as --model (CLAUDE.md "Choosing models: the user
// decides", the owner, 2026-10-11). Without --model the script still runs harness.json's
// implementer.chain, which the main session no longer relies on. Runs use the scripts' own
// OpenCode data directory, and a model OpenCode does not list there exits 3 before anything is
// billed. With a longer chain, the next model runs
// only on an infrastructure failure, and only when the failed run left nothing behind (no new
// commit locally or on origin, no new PR), judged against the state before the first attempt, so a
// resumed rework branch can still fall back. An implementer that stops and reports has NOT failed:
// its run exits 0 and is never retried; this script then exits 1 at "no open PR".
//
// When an attempt fails and left nothing behind, the reset between attempts first saves the
// worktree's uncommitted changes (staged, unstaged and untracked) to
// <workRoot>/<name>.<model key>.<UTC time>.unsaved.patch, created exclusively (lib/unsaved.mjs,
// #87). The exit 1 and exit 3 messages name every patch the run saved.
//
// Exit 0: PR open. Exit 1: the main session decides (read the log). Exit 3: OpenCode unavailable;
// fall back to a Claude implementer.

import fs from 'node:fs';
import path from 'node:path';
import { runOpenCodeWatched, resolveOpenCode, OpenCodeInfraError, keyProblem, isResumable, lookupSession } from './lib/opencode.mjs';
import { runChain } from './lib/chain.mjs';
import { resetWorktree, selfTest as unsavedSelfTest } from './lib/unsaved.mjs';
import { namedModel, selfTest as namedSelfTest } from './lib/named.mjs';
import { matchSession } from './lib/opencode.mjs';
import { resumeSelfTest } from './lib/resume-selftest.mjs';
import {
  sh, requireTools, repoPaths, loadConfig, parseArgs, envWith, ensureAgent, ocArgs, prepareOpenCode, watchLine,
} from './lib/common.mjs';

const say = (s) => console.log(s);
const die = (code, s) => { console.error(s); process.exit(code); };

const a = parseArgs(process.argv.slice(2), { flags: ['self-test'], repeatable: ['copy', 'env'] });
// --self-test: the reset's save on a throwaway repository (lib/unsaved.mjs), a named model's id
// and family (lib/named.mjs), and a resumed session found by id; no OpenCode or gh.
if (a['self-test']) {
  const failures = [...unsavedSelfTest(), ...namedSelfTest(), ...sessionSelfTest(), ...await resumeSelfTest()];
  for (const f of failures) console.error(`FAIL ${f}`);
  say(`self-test: ${failures.length ? `${failures.length} checks failed` : 'all checks passed'}`);
  process.exit(failures.length ? 1 : 0);
}
if (!a.task === !a.fix) die(2, 'Give exactly one of --task T<nn> or --fix <issue>.');
if (a.task && !/^T\d{2,3}$/.test(a.task)) die(2, `--task must look like T07; got ${a.task}`);
if (!a.slug || !a.brief) die(2, '--slug and --brief are required.');
if (!fs.existsSync(a.brief)) die(2, `Brief not found: ${a.brief}`);
if (a.session && !/^ses_\w+$/.test(a.session)) die(2, `--session takes an OpenCode session id (ses_...); got ${a.session}`);
if (a.session && !a.model) die(2, '--session resumes on the model the user names: give --model too.');
const seconds = (k) => {
  if (a[k] === undefined) return null;
  const n = Number(a[k]);
  if (!Number.isInteger(n) || n <= 0) die(2, `--${k} takes a positive number of seconds; got ${a[k]}`);
  return n;
};
const totalSec = seconds('total-timeout-sec');
const idleSec = seconds('idle-timeout-sec');

let opencode;
try { opencode = resolveOpenCode(); } catch (e) {
  if (e instanceof OpenCodeInfraError) die(3, `OpenCode unavailable: ${e.message} Fall back to a Claude implementer (see harness.json).`);
  throw e;
}
requireTools('git', 'gh');

const top0 = sh('git', ['rev-parse', '--show-toplevel']);
const config = loadConfig(top0);
const { top, commonDir, mainRoot, workRoot } = repoPaths(config);
const impl = config.implementer;
const chain = a.model ? [a.model] : impl.chain;
for (const m of chain) {
  let model;
  try { model = namedModel(m, config.models); } catch (e) { die(2, e.message); }
  if (!model) die(2, `Unknown model ${m}: give a harness.json key (${Object.keys(config.models).join(', ')}) or an OpenCode id, provider/model[@variant].`);
  config.models[m] = model;
}
const fallback = `Fall back to a Claude implementer (${impl.claudeFallback ?? 'sonnet'}).`;
const pre = await prepareOpenCode({ opencode, chain, models: config.models, env: envWith(a.env), cwd: top, log: say });
for (const p of pre.problems) say(p);
if (!pre.usable.length) die(3, `OpenCode unavailable: ${pre.problems.join('; ')}. ${fallback}`);

const name = a.task ?? `fix-${a.fix}`;
const branch = a.task ? `task/${a.task}-${a.slug}` : `fix/${a.fix}-${a.slug}`;
const issue = a.issue ?? a.fix;
const worktree = path.join(workRoot, name);
const logFile = path.join(workRoot, `${name}.implementer.log`);
fs.mkdirSync(workRoot, { recursive: true });
// A resumed session continues in the worktree it ran in, kept as it stopped (rule 13).
if (a.session && !fs.existsSync(worktree)) die(2, `--session ${a.session} resumes in the kept worktree ${worktree}, which does not exist.`);
// ... and only a session of that worktree, checked before anything changes or runs (Sol's R2, PR 114).
if (a.session) {
  const found = await lookupSession(opencode, { workDir: fs.realpathSync(worktree), title: '', startedMs: 0, env: pre.env, sessionId: a.session, timeoutMs: 60_000 });
  if (!found.session) die(2, `--session ${a.session}: ${found.miss}. Nothing was run.`);
}

// 1. The worktree and branch: resume a pushed branch, otherwise start from origin/main and push.
sh('git', ['-C', top, 'fetch', '-q', 'origin']);
const remoteHas = sh('git', ['-C', top, 'ls-remote', '--heads', 'origin', branch]);
if (fs.existsSync(worktree)) {
  if (sh('git', ['-C', worktree, 'rev-parse', '--abbrev-ref', 'HEAD']) !== branch) sh('git', ['-C', worktree, 'checkout', '-q', branch]);
} else if (remoteHas) {
  sh('git', ['-C', top, 'worktree', 'add', worktree, branch]);
} else {
  sh('git', ['-C', top, 'worktree', 'add', '-b', branch, worktree, 'origin/main']);
  sh('git', ['-C', worktree, 'push', '-q', '-u', 'origin', branch]);
}
if (remoteHas) sh('git', ['-C', worktree, 'merge', '-q', '--ff-only', `origin/${branch}`]);
// A copied file's folder may be untracked or ignored, so absent from a fresh worktree (#90). A
// path that leaves the main checkout or the worktree is refused (Luna's R1 on PR 91). A
// symlinked path component on the source or the destination side that escapes either root is
// refused too: the lexical check above is fooled by a tracked symlink whose target is outside,
// but mkdirSync and copyFileSync follow symlinks, so the script would otherwise create the
// destination outside the worktree (Luna's R2 on PR 91, both sides).
for (const f of a.copy) {
  // 1. Lexical gate (cheap, no I/O): the path leaves the checkout or the worktree lexically.
  // Required (not best-effort) so a swap with the realpath gate changes the error text on
  // the path-escape tests: `../newdir/escaped.sav` would otherwise hit ENOENT and emit
  // "cannot resolve" instead of the lexical "inside the checkout" — Luna's R3 on round 5.
  const lexInside = (root) => { const r = path.relative(root, path.resolve(root, f)); return r && !r.startsWith('..') && !path.isAbsolute(r); };
  if (!lexInside(mainRoot) || !lexInside(worktree)) die(2, `--copy takes a path inside the checkout; got ${f}`);
  // 2. Source-side realpath: a tracked symlink whose target escapes the checkout would
  // otherwise let copyFileSync read or write outside (the file's path through the symlink).
  // Required so the source-side gate is provably exercised by the source-side test —
  // removing it leaves the dest-side walk to catch, which is not what the test claims to prove.
  let realF;
  try { realF = fs.realpathSync(path.resolve(mainRoot, f)); }
  catch (e) { die(2, `--copy: cannot resolve ${f}: ${e.code ?? e.message}`); }
  const rel = path.relative(mainRoot, realF);
  if (rel === '' || rel.startsWith('..') || path.isAbsolute(rel)) die(2, `--copy takes a path inside the checkout; got ${f}`);
  // 3. Destination-side realpath: walk up from dest (not just dirname(dest), because dest
  // itself can be a tracked symlink to outside — copyFileSync would write to it) and refuse
  // if any existing component is a symlink whose target lands outside the worktree. Walk
  // past non-existent intermediates — mkdirSync's recursive option would otherwise follow an
  // ancestor's symlink and create the directory outside the worktree (Luna's R1 on round 4
  // and R1 on round 5).
  const dest = path.join(worktree, rel);
  for (let cur = dest; cur !== worktree; cur = path.dirname(cur)) {
    if (!cur.startsWith(worktree + path.sep)) break;
    let lstat;
    try { lstat = fs.lstatSync(cur); } catch { continue; }   // cur doesn't exist yet, walk up
    if (!lstat.isSymbolicLink()) break;                     // regular file/dir; safe
    const realCur = (() => { try { return fs.realpathSync(cur); } catch { return cur; } })();
    const r = path.relative(worktree, realCur);
    if (r === '' || r.startsWith('..') || path.isAbsolute(r)) die(2, `--copy: destination path escapes the worktree via a symlink; got ${f}`);
    break;                                                  // symlink inside worktree; safe
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(realF, dest);
}
ensureAgent({ top, commonDir, worktree, agent: impl.agent });
say(`worktree: ${worktree} on ${branch}`);

// 2. The run.
const prompt = `${fs.readFileSync(a.brief, 'utf8')}

---
RUN RULES (from tools/harness/implement.mjs; they override the brief where they conflict):
- Your worktree is ${worktree} on branch ${branch}, already created and pushed. Never run
  git worktree. Pass git -C "${worktree}" explicitly.
- Everything else in the brief is binding: Owns, Done when, the PR body, the detach, the report.
- The PR body's "Closes #${issue}" is the only place a closing keyword may precede #<n>.
- Never read, write or redirect to any path outside your worktree: no /tmp, no home directory, no
  git internals (in a worktree, .git points into the main checkout). Scratch files and any TMPDIR go
  in a folder inside the worktree, which you never commit (add files by name, never git add -A), and
  which you delete before your last commit. A test that needs a TMPDIR outside every checkout is
  run by the main session, not by you. (L57)
- Commit and push after each step, so a run that ends early keeps its work. (L57)
`;
const openPr = () => sh('gh', ['pr', 'list', '--head', branch, '--state', 'open', '--json', 'number', '--jq', '.[0].number'], { cwd: top, allowFail: true });
const originSha = () => sh('git', ['-C', top, 'rev-parse', `origin/${branch}`], { allowFail: true });
const startSha = sh('git', ['-C', worktree, 'rev-parse', 'HEAD']);
const startRemote = originSha();
const startPr = openPr();
fs.writeFileSync(logFile, '');

// The implementer runs on the agent copied into its worktree, so it must not inherit the reviewer's
// settings (review.mjs, L34) from a session that ran a review: OPENCODE_DISABLE_PROJECT_CONFIG would
// hide that agent, and OPENCODE_CONFIG_DIR would put another in its place.
const { OPENCODE_CONFIG_DIR: _dir, OPENCODE_DISABLE_PROJECT_CONFIG: _off, ...implementEnv } = pre.env;

const patches = [];        // the unsaved-work patches this run's resets wrote (#87)
let attemptModel = null;   // the chain key of the attempt whose work a reset saves
const result = await runChain({
  chain: pre.usable,
  log: say,
  attempt: async (m) => {
    attemptModel = m;
    const model = config.models[m];
    const watch = watchLine(m, model);
    if (watch) say(watch);
    let reason = null;
    let output;
    let sessionId = a.session ?? null;
    try {
      const run = await runOpenCodeWatched({
        args: ocArgs(worktree, impl.agent, model), prompt, workDir: worktree, title: `${name}-${m}`,
        sessionId: a.session ?? null,
        startupTimeoutMs: impl.startupTimeoutSec * 1000, idleTimeoutMs: (idleSec ?? impl.idleTimeoutSec) * 1000,
        totalTimeoutMs: (totalSec ?? impl.totalTimeoutSec) * 1000, opencode, env: implementEnv, log: say,
      });
      output = run.output;
      sessionId = run.sessionId ?? sessionId;
      // OpenCode's own error stream on a failed run, never the model's output (Luna's R1, round 2).
      if (run.exitCode !== 0) reason = keyProblem(run.stderr, model.id, implementEnv.XDG_DATA_HOME) ?? `exit ${run.exitCode}`;
      else if (run.agentFallback) reason = 'fell back to the default agent';
      else if (run.permissionRejected) reason = `permission rejected: ${run.permissionRejected}${run.permissionHint ? `; ${run.permissionHint}` : ''}`;
    } catch (e) {
      if (!(e instanceof OpenCodeInfraError)) throw e;
      reason = e.reason;
      output = e.message;
      sessionId = e.sessionId ?? sessionId;
    }
    fs.appendFileSync(logFile, `=== ${m} (${model.id}): ${reason ? `failed: ${reason}` : 'ran'} ===\n${watch ? `${watch}\n` : ''}${output}\n`);
    // Stopped by our own limit, or a resumed run: the worktree stays as it stopped, to be resumed in
    // its own session (rule 13), never reset or handed to another model (rule 7; Sol's R5 on PR 114).
    if (reason) return { ok: false, reason, stop: Boolean(a.session) || isResumable(reason), sessionId };
    return { ok: true, value: output };
  },
  leftWork: async () => {
    sh('git', ['-C', top, 'fetch', '-q', 'origin']);
    const pr = openPr();
    return sh('git', ['-C', worktree, 'rev-parse', 'HEAD']) !== startSha
      || originSha() !== startRemote || (pr && pr !== startPr);
  },
  // Before the hard reset destroys it, the failed attempt's uncommitted work goes to a patch
  // (lib/unsaved.mjs, #87), so a run that a rejected tool call ended is not lost.
  reset: async () => {
    patches.push(...resetWorktree({ worktree, startSha, workRoot, name, model: attemptModel, log: say }));
  },
});

say(`run log: ${logFile}`);
// Every exit after the chain names the patches its resets saved (#87; Sol's R3 on PR 100).
const saved = patches.length ? ` Unsaved work was saved before the reset: ${patches.join(', ')}.` : '';
const reasons = result.failures.map((f) => `${f.name}: ${f.reason}`).join('; ');
if (!result.ok && result.stopped) {
  const again = `node tools/harness/implement.mjs ${a.task ? `--task ${a.task}` : `--fix ${a.fix}`} --slug ${a.slug}${a.issue ? ` --issue ${a.issue}` : ''} --model ${result.failures[0].name}`;
  die(1, `The run stopped (${reasons}); its worktree ${worktree} is kept as it stopped.${saved} `
    + (result.sessionId ? `Resume: ${again} --session ${result.sessionId} --brief <a short "continue where you stopped" brief> --total-timeout-sec <longer>`
      : 'No session id was recorded: read the log, then decide with the user.'));
}
if (!result.ok) {
  if (result.leftWork) die(1, `The run failed (${reasons}) after committing, pushing or opening a PR on ${branch}; not retrying. The main session decides.${saved}`);
  die(3, `OpenCode unavailable: ${result.sameCause ? `same failure twice: ${result.sameCause} (${reasons})` : reasons}. ${fallback}${saved}`);
}
if (reasons) say(`fell back: ${reasons}`);
// The reviewer must not be this model's family: pass it to review.mjs as --exclude.
say(`implemented by: ${result.name} (${config.models[result.name].id})`);

// 3. The handover: a PR, and a clean, pushed, detached worktree.
sh('git', ['-C', top, 'fetch', '-q', 'origin']);
const pr = sh('gh', ['pr', 'list', '--head', branch, '--state', 'open', '--json', 'number,url', '--jq', '.[0].url'], { cwd: top, allowFail: true });
if (sh('git', ['-C', worktree, 'status', '--porcelain'])) console.warn(`warning: uncommitted changes remain in ${worktree}`);
if (sh('git', ['-C', worktree, 'rev-parse', 'HEAD']) !== originSha()) console.warn(`warning: ${worktree}'s HEAD is not pushed to origin/${branch}`);
sh('git', ['-C', worktree, 'checkout', '-q', '--detach']);
say('--- tail of the run ---');
say(result.value.split(/\r?\n/).slice(-40).join('\n'));
if (!pr) die(1, `No open PR for ${branch}. Read ${logFile}: an implementer that stopped and reported is not a failure.${saved}`);
say(`PR: ${pr}`);

// A resumed run finds its session by id, whatever its title or age, and only in its own directory.
function sessionSelfTest() {
  const failures = [];
  const ok = (what, cond) => { if (!cond) failures.push(what); };
  const dir = fs.realpathSync(process.cwd());
  const old = { id: 'ses_old', title: 'T35-glm-abc', directory: dir, created: 1000, updated: 2000 };
  const other = { id: 'ses_else', title: 'T35-glm-abc', directory: '/nowhere/else', created: 1000, updated: 2000 };
  ok('resume finds the session by id', matchSession([other, old], { workDir: dir, title: 'T35-new-xyz', startedMs: 9e12, sessionId: 'ses_old' }).session === old);
  ok('resume refuses the id in another directory', matchSession([other], { workDir: dir, title: 'x', startedMs: 0, sessionId: 'ses_else' }).session === null);
  ok('resume misses an absent id', matchSession([old], { workDir: dir, title: 'x', startedMs: 0, sessionId: 'ses_none' }).session === null);
  ok('a new run still needs a session created after it started', matchSession([old], { workDir: dir, title: old.title, startedMs: 9e12 }).session === null);
  ok('a new run finds its titled session', matchSession([old], { workDir: dir, title: old.title, startedMs: 0 }).session === old);
  return failures;
}
