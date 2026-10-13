#!/usr/bin/env node
// Writes a review brief that review.mjs accepts (#180). The brief was assembled by hand with sed from
// docs/review-brief.md and the task text, and one launch was refused for a first line that was not
// the header (PRs 176 and 179).
//
//   node tools/harness/make-brief.mjs --pr N --issue N [--task docs/tasks/T<nn>.md] --reviewer NAME
//     [--round K] [--caveat TEXT]... [--protects TEXT] [--blocking4 TEXT] --out FILE
//
// The brief is: the header alone on line 1 ("T47 review (luna)", or "fix #175 review (luna)" without
// --task); the round and the caveats after it, never on it; the PR's head SHA, full (and no other
// commit's full SHA where review.mjs reads: write earlier heads short); the numbered block of
// docs/process.md section 5; the task file, or the issue's title and body, pasted in full; and the two
// sections of docs/review-brief.md with "Blocking means" filled from --protects and --blocking4.
// --protects has no default: without it the placeholder remains and nothing is written. Nothing is
// written if the brief fails checkBrief: the reader review.mjs uses (lib/chain.mjs briefTargets) must
// find only the head, and no `<...>` placeholder may remain outside the pasted text.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { briefTargets, doneWhenCount } from './lib/chain.mjs';
import { sh, parseArgs } from './lib/common.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const HEADER_RE = /^(?:T\d+[a-z]*|fix #\d+) review \([^()\s][^()]*\)$/;
const ANY_HEADER = /^(?:T\d+[a-z]*|fix #\d+) review \(/;
const FULL_SHA = /\b[0-9a-fA-F]{40}\b/g;
// The reviewer's own instructions in the block use these as templates; they are not placeholders.
const TEMPLATE_WORDS = /DW<k>|<command>|<result>|<reason>/g;
const PLACEHOLDER = /<[A-Za-z][^<>]*>/; // may span lines, as "<name it: ...>" does
const MARK = '\u0000PASTED\u0000';

const fail = (msg) => { throw new Error(msg); };

// The numbered block: the first ```text fence under "## 5." of docs/process.md.
export function processBlock(processMd) {
  const m = /^## 5\. The reviewer brief\s*\n+```text\n([\s\S]*?)\n```/m.exec(processMd);
  if (!m) fail('docs/process.md section 5 has no ```text block: make-brief.mjs cannot read it.');
  return m[1].split('\n');
}

// The two sections of docs/review-brief.md: its first ```text fence.
export function briefSections(reviewBriefMd) {
  const m = /```text\n([\s\S]*?)\n```/.exec(reviewBriefMd);
  if (!m || !/^## Blocking means$/m.test(m[1]) || !/^## Report every blocking finding/m.test(m[1])) {
    fail('docs/review-brief.md has no ```text block with both sections: make-brief.mjs cannot read it.');
  }
  return m[1];
}

const once = (text, re, to, what) => {
  if (!re.test(text)) fail(`make-brief.mjs expected ${what} in the template and did not find it (the template changed?).`);
  return text.replace(re, () => to);
};

// o: { header, pr, head, round, caveats, protects, blocking4, pasted, processMd, reviewBriefMd }
// Returns { text, generated }: `generated` is the brief with the pasted text left out.
export function buildBrief(o) {
  const lines = processBlock(o.processMd);
  const intro = [`You review PR #${o.pr} at ${o.head}. You did not write it. The task file follows.`];
  if (o.round) intro.push(`This is review round ${o.round}.`);
  for (const c of o.caveats ?? []) intro.push(`Caveat: ${c}`);
  let block = lines.slice(1).join('\n');
  block = once(block, /^You review PR #<n> at <sha>\. You did not write it\. The task file follows\.$/m, intro.join('\n'), 'the "You review PR" line');
  block = once(block, /HEAD is <sha>/, `HEAD is ${o.head}`, '"HEAD is <sha>"');
  block = once(block, /<project classes>/, 'constants with no evidence, a status written into a document', '"<project classes>"');
  block = once(block, /^6\. <docs\/review-brief\.md[^\n]*$/m,
    '6. Blocking means, and the one-pass rule: the two sections at the end of this brief, in full (L47, L49).', 'item 6');
  let sections = briefSections(o.reviewBriefMd);
  if (o.protects) sections = once(sections, /<name it:[\s\S]*?>/, o.protects, '"<name it: ...>"');
  sections = once(sections, /<project-specific items:[\s\S]*?>/,
    o.blocking4 ?? 'a constant with no evidence, a test that passes with the behaviour deleted, a status written into a document',
    '"<project-specific items: ...>"');
  const generated = `${o.header}\n${block}\n\n${MARK}\n\n${sections}`;
  return { text: generated.replace(MARK, () => o.pasted.replace(/\s+$/, '')), generated: generated.replace(MARK, '') };
}

// Throws unless review.mjs would accept `text` for a PR at `head`. `generated` is the brief without the
// pasted task or issue text, where a `<` is the task's own and not a placeholder.
export function checkBrief(text, head, generated = text) {
  const all = text.split(/\r?\n/);
  if (!HEADER_RE.test(all[0])) fail(`The first line must be the review header alone, e.g. "T07 review (luna)" or "fix #175 review (luna)"; got: ${all[0]}`);
  const again = all.slice(1).find((l) => ANY_HEADER.test(l));
  if (again) fail(`The header appears again below line 1: ${again}`);
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
  for (const k of ['pr', 'issue', 'reviewer', 'out']) if (!a[k]) fail(`--${k} is required.`);
  for (const k of ['pr', 'issue']) if (!/^\d+$/.test(a[k])) fail(`--${k} takes a number; got ${a[k]}`);
  if (a.round !== undefined && !/^[1-9]\d*$/.test(a.round)) fail(`--round takes a positive number; got ${a.round}`);
  const head = sh('gh', ['pr', 'view', a.pr, '--json', 'headRefOid', '--jq', '.headRefOid']).toLowerCase();
  if (!/^[0-9a-f]{40}$/.test(head)) fail(`PR ${a.pr}'s head SHA could not be read from gh; got: ${head}`);
  let id; let pasted;
  if (a.task) {
    const m = /^(T\d+[a-z]*)\.md$/.exec(path.basename(a.task));
    if (!m) fail(`--task takes docs/tasks/T<nn>.md; got ${a.task}`);
    id = m[1];
    pasted = fs.readFileSync(a.task, 'utf8');
    if (!/^# T\d+/m.test(pasted)) fail(`${a.task} has no "# T<nn>" title line: review.mjs reads only the lines before it.`);
  } else {
    id = `fix #${a.issue}`;
    const j = JSON.parse(sh('gh', ['issue', 'view', a.issue, '--json', 'title,body']));
    pasted = `## Issue #${a.issue}: ${j.title}\n\n${j.body}`;
  }
  const processMd = fs.readFileSync(path.join(ROOT, 'docs', 'process.md'), 'utf8');
  const reviewBriefMd = fs.readFileSync(path.join(ROOT, 'docs', 'review-brief.md'), 'utf8');
  const { text, generated } = buildBrief({
    header: `${id} review (${a.reviewer})`, pr: a.pr, head, round: a.round, caveats: a.caveat,
    protects: a.protects, blocking4: a.blocking4, pasted, processMd, reviewBriefMd,
  });
  checkBrief(text, head, generated);
  fs.writeFileSync(a.out, text.endsWith('\n') ? text : `${text}\n`);
  console.log(`wrote ${a.out}: ${id} review (${a.reviewer}), PR ${a.pr} at ${head}; ${doneWhenCount(text)} Done-when line(s) counted (pass review.mjs --done-when K if that is wrong).`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try { main(); } catch (e) { console.error(`make-brief: ${e.message}`); process.exit(2); }
}
