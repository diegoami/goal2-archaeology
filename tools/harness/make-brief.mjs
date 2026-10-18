#!/usr/bin/env node
// Writes a review brief that review.mjs accepts (#180). The brief was assembled by hand with sed from
// docs/review-brief.md and the task text, and one launch was refused for a first line that was not
// the header (PRs 176 and 179).
//
//   node tools/harness/make-brief.mjs --pr N --issue N|none [--task docs/tasks/T<nn>.md | --header NAME]
//     --reviewer NAME [--round K [--sample TEXT]] [--caveat TEXT]... [--protects TEXT] [--blocking4 TEXT] --out FILE
//
// The brief is: the header alone on line 1 ("T47 review (luna)", or "fix #175 review (luna)" without
// --task, or "NAME review (luna)" with --header NAME); the round and the caveats after it, never on it; the PR's head SHA, full (and no other
// commit's full SHA where review.mjs reads: write earlier heads short); the numbered block of
// docs/process.md section 5; the task file, or the issue's title and body, pasted in full; and the three
// sections of docs/review-brief.md with "Blocking means" filled from --protects and --blocking4.
// --protects has no default: without it the placeholder remains and nothing is written.
// A full SHA in the pasted text other than the PR's head is shortened to 10 characters, and the output says how
// many (an issue body quoting a commit made the brief refused, #314); the head's own SHA is left as written.
// A review with no task file and no issue (a planning or backlog PR): --issue none and --header NAME
// ("backlog" gives "backlog review (luna)"); the PR's title and body are pasted in place of the task or the
// issue, and review.mjs is run with --issue none (no label is applied). --header is refused with --task.
// A text argument that must carry content (--protects, --blocking4, --sample, --caveat, --reviewer, --task,
// --out) is trimmed and refused when empty or only whitespace, in buildBrief and again in checkBrief (#324).
// Rework rounds (the owner, 2026-10-18, #319; docs/review-brief.md "Rework rounds"): from --round 2 the
// brief names the seeded sample to re-run in place of a full family run, so --sample is required there and
// refused in a first review. The "Rework rounds" section itself is always pasted.
//
// The head comes from GitHub, and never ahead of it: a brief written seconds after a push named the old head
// and review.mjs refused it (#234). When the PR's branch exists locally and GitHub's head is not yet the
// local head, make-brief polls gh (HARNESS_HEAD_WAIT_SEC, default 120; every HARNESS_HEAD_POLL_SEC, default 5)
// until they agree, and writes nothing if they never do. A local branch that is an ancestor of GitHub's head
// (stale, not unpushed) or no local branch at all: GitHub's head is used, and the output says so.
//
// Nothing is written if the brief fails checkBrief: the reader review.mjs uses (lib/chain.mjs briefTargets) must
// find only the head, and no `<...>` placeholder may remain outside the pasted text.

import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { briefTargets, doneWhenCount } from './lib/chain.mjs';
import { sh, parseArgs } from './lib/common.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const HEADER_NAME = /^[A-Za-z0-9][A-Za-z0-9 ._#-]{0,39}$/; // --header NAME: one short line, no parentheses
const HEADER_RE = /^[A-Za-z0-9][A-Za-z0-9 ._#-]* review \([^()\s][^()]*\)$/;
const ANY_HEADER = /^(?:T\d+[a-z]*|fix #\d+) review \(/;
const FULL_SHA = /\b[0-9a-fA-F]{40}\b/g;
// The reviewer's own instructions in the block use these as templates; they are not placeholders.
const TEMPLATE_WORDS = /DW<k>|<command>|<result>|<reason>/g;
const PLACEHOLDER = /<[A-Za-z][^<>]*>/; // may span lines, as "<name it: ...>" does
const MARK = '\u0000PASTED\u0000';

const fail = (msg) => { throw new Error(msg); };

// A text argument given as empty or whitespace carries nothing: refused, never passed on as if it did.
export function content(name, v) {
  if (v === undefined) return undefined;
  const t = typeof v === 'string' ? v.trim() : '';
  if (!t) fail(`--${name} must carry text: it is empty or only whitespace.`);
  return t;
}

// Every full SHA in `text` other than `head` becomes its first 10 characters. Returns { text, shortened }.
export function shortenShas(text, head) {
  const h = String(head).toLowerCase();
  const shortened = [];
  const out = String(text).replace(FULL_SHA, (s) => {
    if (s.toLowerCase() === h) return s;
    if (!shortened.includes(s.slice(0, 10))) shortened.push(s.slice(0, 10));
    return s.slice(0, 10);
  });
  return { text: out, shortened };
}

const sleepMs =(ms) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);

// readHead(): GitHub's head now. localHead: the local branch's head, or null. isBehind(local, remote): true
// when `local` is an ancestor of `remote`. Returns { head, note }; throws if GitHub never shows localHead.
export function resolveHead({ readHead, localHead, isBehind = () => false, waitMs = 120000, pollMs = 5000, sleep = sleepMs, now = Date.now }) {
  let head = readHead();
  if (!localHead) return { head, note: 'no local branch of the PR: the head is the one GitHub shows' };
  const start = now();
  let waited = false;
  while (head !== localHead) {
    if (isBehind(localHead, head)) return { head, note: `the local branch is behind GitHub's head: the head is the one GitHub shows` };
    if (now() - start >= waitMs) {
      fail(`GitHub still shows the PR's head as ${head}, not the local branch's ${localHead}, after ${Math.round(waitMs / 1000)} s: push the branch, or wait and run again (nothing written).`);
    }
    waited = true;
    sleep(pollMs);
    head = readHead();
  }
  return { head, note: waited ? `waited ${Math.round((now() - start) / 1000)} s for GitHub to show the pushed head` : '' };
}

// The numbered block: the first ```text fence under "## 5." of docs/process.md.
export function processBlock(processMd) {
  const m = /^## 5\. The reviewer brief\s*\n+```text\n([\s\S]*?)\n```/m.exec(processMd);
  if (!m) fail('docs/process.md section 5 has no ```text block: make-brief.mjs cannot read it.');
  return m[1].split('\n');
}

// The three sections of docs/review-brief.md: its first ```text fence.
export function briefSections(reviewBriefMd) {
  const m = /```text\n([\s\S]*?)\n```/.exec(reviewBriefMd);
  if (!m || !/^## Blocking means$/m.test(m[1]) || !/^## Report every blocking finding/m.test(m[1]) || !/^## Rework rounds/m.test(m[1])) {
    fail('docs/review-brief.md has no ```text block with its three sections: make-brief.mjs cannot read it.');
  }
  return m[1];
}

const once = (text, re, to, what) => {
  if (!re.test(text)) fail(`make-brief.mjs expected ${what} in the template and did not find it (the template changed?).`);
  return text.replace(re, () => to);
};

// o: { header, pr, head, round, caveats, protects, blocking4, pasted, processMd, reviewBriefMd }
// Returns { text, generated, shortened }: `generated` is the brief with the pasted text left out; `shortened`
// lists the full SHAs (10 characters each) cut short in the pasted text.
export function buildBrief(o) {
  const lines = processBlock(o.processMd);
  const sample = content('sample', o.sample);
  const protects = content('protects', o.protects);
  const blocking4 = content('blocking4', o.blocking4);
  const caveats = (o.caveats ?? []).map((c) => content('caveat', c));
  const intro = [`You review PR #${o.pr} at ${o.head}. You did not write it. The task file follows.`];
  if (o.round) intro.push(`This is review round ${o.round}.`);
  const rework = Number(o.round) >= 2;
  if (rework && !sample) fail(`Round ${o.round} is a rework round: --sample TEXT is required (the seeded sample to re-run in place of a full family run; docs/review-brief.md "Rework rounds").`);
  if (!rework && sample) fail('--sample belongs to a rework round (--round 2 or later); the first review re-runs every Done-when line.');
  if (rework) intro.push(`Sample for this round: ${sample}`);
  for (const c of caveats) intro.push(`Caveat: ${c}`);
  let block = lines.slice(1).join('\n');
  block = once(block, /^You review PR #<n> at <sha>\. You did not write it\. The task file follows\.$/m, intro.join('\n'), 'the "You review PR" line');
  block = once(block, /HEAD is <sha>/, `HEAD is ${o.head}`, '"HEAD is <sha>"');
  block = once(block, /<project classes>/, 'constants with no evidence, a status written into a document', '"<project classes>"');
  block = once(block, /^6\. <docs\/review-brief\.md[^\n]*$/m,
    '6. Blocking means, the one-pass rule and the rework-round rule: the three sections at the end of this brief, in full (L47, L49, #319).', 'item 6');
  let sections = briefSections(o.reviewBriefMd);
  if (protects) sections = once(sections, /<name it:[\s\S]*?>/, protects, '"<name it: ...>"');
  sections = once(sections, /<project-specific items:[\s\S]*?>/,
    blocking4 ?? 'a constant with no evidence, a test that passes with the behaviour deleted, a status written into a document',
    '"<project-specific items: ...>"');
  const generated = `${o.header}\n${block}\n\n${MARK}\n\n${sections}`;
  const { text: pasted, shortened } = shortenShas(o.pasted, o.head);
  return { text: generated.replace(MARK, () => pasted.replace(/\s+$/, '')), generated: generated.replace(MARK, ''), shortened };
}

// Throws unless review.mjs would accept `text` for a PR at `head`. `generated` is the brief without the
// pasted task or issue text, where a `<` is the task's own and not a placeholder.
export function checkBrief(text, head, generated = text) {
  const all = text.split(/\r?\n/);
  if (!HEADER_RE.test(all[0])) fail(`The first line must be the review header alone, e.g. "T07 review (luna)" or "fix #175 review (luna)"; got: ${all[0]}`);
  const again = all.slice(1).find((l) => ANY_HEADER.test(l) || l === all[0]);
  if (again) fail(`The header appears again below line 1: ${again}`);
  const headPart = text.split(/^#\s+T\d+\b|^## Issue #\d+:|^## PR #\d+:/m)[0];
  const round = Number(/^This is review round (\d+)\.$/m.exec(headPart)?.[1] ?? 1);
  if (round >= 2 && !/^Sample for this round: \S/m.test(headPart)) fail(`Round ${round} is a rework round: the brief must carry "Sample for this round:" followed by text.`);
  if (/^Sample for this round:\s*$/m.test(headPart)) fail('The "Sample for this round:" line is empty.');
  if (/^Caveat:\s*$/m.test(headPart)) fail('A "Caveat:" line is empty.');
  if (/^2\. What this task protects can be got past:\s*[.\n]/m.test(text)) fail('"What this task protects" names nothing: --protects is empty.');
  const left = PLACEHOLDER.exec(generated.replace(TEMPLATE_WORDS, ''))?.[0].replace(/\s+/g, ' ');
  if (left) fail(`A placeholder remains: ${left.slice(0, 70)} (give --protects, or the flag it belongs to)`);
  const h = head.toLowerCase();
  const targets = [...new Set(briefTargets(text))];
  if (!targets.includes(h)) fail(`The brief does not name the PR's head ${head} as the commit to review.`);
  if (targets.some((t) => t !== h)) fail(`The brief names another full commit SHA as the one to review (${targets.find((t) => t !== h)}): write earlier heads short (10 characters); review.mjs refuses it.`);
  const part = text.split(/^#\s+T\d+\b/m)[0];
  const second = [...new Set((part.match(FULL_SHA) ?? []).map((s) => s.toLowerCase()))].find((s) => s !== h);
  if (second) fail(`A second full SHA (${second}) is in the brief's head part: write earlier heads short (10 characters).`);
}

function main() {
  const a = parseArgs(process.argv.slice(2), { repeatable: ['caveat'] });
  for (const k of ['pr', 'issue', 'reviewer', 'out']) if (!a[k]) fail(`--${k} is required (--issue none for a PR with no issue).`);
  for (const k of ['reviewer', 'out', 'task', 'header', 'protects', 'blocking4', 'sample']) content(k, a[k]);
  for (const c of a.caveat) content('caveat', c);
  const noIssue = a.issue === 'none';
  if (!/^\d+$/.test(a.pr)) fail(`--pr takes a number; got ${a.pr}`);
  if (!noIssue && !/^\d+$/.test(a.issue)) fail(`--issue takes a number, or none; got ${a.issue}`);
  if (a.header !== undefined && a.task) fail('--header names a brief with no task file: it cannot be given with --task.');
  if (a.header !== undefined && !HEADER_NAME.test(a.header.trim())) fail(`--header takes a short name (letters, digits, space, . _ # -, at most 40, no parentheses); got ${a.header}`);
  if (noIssue && !a.task && a.header === undefined) fail('--issue none needs --header NAME (or --task): the header has no issue number to name.');
  if (a.round !== undefined && !/^[1-9]\d*$/.test(a.round)) fail(`--round takes a positive number; got ${a.round}`);
  const readHead = () => sh('gh', ['pr', 'view', a.pr, '--json', 'headRefOid', '--jq', '.headRefOid']).toLowerCase();
  const branch = sh('gh', ['pr', 'view', a.pr, '--json', 'headRefName', '--jq', '.headRefName'], { allowFail: true });
  const local = branch ? sh('git', ['rev-parse', '--verify', '--quiet', `refs/heads/${branch}^{commit}`], { allowFail: true }).toLowerCase() : '';
  const isBehind = (l, r) => /^[0-9a-f]{40}$/.test(r) && spawnSync('git', ['merge-base', '--is-ancestor', l, r]).status === 0;
  const secs = (v, d) => (v !== undefined && v !== '' && Number.isFinite(Number(v)) ? Number(v) : d);
  const { head, note } = resolveHead({
    readHead, localHead: /^[0-9a-f]{40}$/.test(local) ? local : null, isBehind,
    waitMs: secs(process.env.HARNESS_HEAD_WAIT_SEC, 120) * 1000, pollMs: secs(process.env.HARNESS_HEAD_POLL_SEC, 5) * 1000,
  });
  if (note) console.error(`make-brief: ${note}.`);
  if (!/^[0-9a-f]{40}$/.test(head)) fail(`PR ${a.pr}'s head SHA could not be read from gh; got: ${head}`);
  let id; let pasted;
  if (a.task) {
    const m = /^(T\d+[a-z]*)\.md$/.exec(path.basename(a.task));
    if (!m) fail(`--task takes docs/tasks/T<nn>.md; got ${a.task}`);
    id = m[1];
    pasted = fs.readFileSync(a.task, 'utf8');
    if (!/^# T\d+/m.test(pasted)) fail(`${a.task} has no "# T<nn>" title line: review.mjs reads only the lines before it.`);
  } else if (noIssue) {
    id = a.header.trim();
    const j = JSON.parse(sh('gh', ['pr', 'view', a.pr, '--json', 'title,body']));
    pasted = `## PR #${a.pr}: ${j.title}\n\n${j.body}`;
  } else {
    id = a.header !== undefined ? a.header.trim() : `fix #${a.issue}`;
    const j = JSON.parse(sh('gh', ['issue', 'view', a.issue, '--json', 'title,body']));
    pasted = `## Issue #${a.issue}: ${j.title}\n\n${j.body}`;
  }
  const processMd = fs.readFileSync(path.join(ROOT, 'docs', 'process.md'), 'utf8');
  const reviewBriefMd = fs.readFileSync(path.join(ROOT, 'docs', 'review-brief.md'), 'utf8');
  const { text, generated, shortened } = buildBrief({
    header: `${id} review (${a.reviewer})`, pr: a.pr, head, round: a.round, sample: a.sample, caveats: a.caveat,
    protects: a.protects, blocking4: a.blocking4, pasted, processMd, reviewBriefMd,
  });
  checkBrief(text, head, generated);
  if (shortened.length) console.error(`make-brief: shortened ${shortened.length} full SHA(s) in the pasted text to 10 characters (only the PR's head stays full): ${shortened.join(', ')}.`);
  fs.writeFileSync(a.out, text.endsWith('\n') ? text : `${text}\n`);
  console.log(`wrote ${a.out}: ${id} review (${a.reviewer}), PR ${a.pr} at ${head}; ${doneWhenCount(text)} Done-when line(s) counted (pass review.mjs --done-when K if that is wrong).`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try { main(); } catch (e) { console.error(`make-brief: ${e.message}`); process.exit(2); }
}
