// readReview's header recovery (#258): a complete review whose header differs from the brief's only
// in punctuation is kept and flagged, never dropped as "no review", and the tolerance weakens none of
// the strict path's protections. The mutation tests at the end rebuild chain.mjs with its tolerance
// made too loose and show that the identity and verdict cases then fail.
//   node --test tools/harness/chain.test.mjs

import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import * as chain from './lib/chain.mjs';
import { planPost } from './lib/post.mjs';

const SHA = '0123456789abcdef0123456789abcdef01234567';
const OTHER = 'fedcba9876543210fedcba9876543210fedcba98';
// Malpaco T32 / PR #135: the brief's header ended in '.', the model's did not.
const H = `T32 review (MiniMax M3), PR #135 at ${SHA}.`;
const head = (h = H.slice(0, -1)) => h;
const body = (verdict = 'approve', close = verdict) => `${verdict}\n\nWorktree: /w/pr135\n\n`
  + 'DW1: ran npm test → 12 pass\nDW2: ran node tools/check.mjs → PASS\nDW3: ran grep -c x a.js → 1\n\n'
  + `R1: none blocking.\n\nFinal pass done\n${close}`;
// The completed review's shape: a "Final pass done" line before the header, the header without
// its final period, a full approve with three Done-when accounts and no blocking finding.
const MALPACO = `Final pass done\n${head()}\n${body()}`;

const read = (out, opts, header = H) => chain.readReview(out, header, opts);

// Each case: what readReview must return. `group` names the protection a mutation must break.
const CASES = [
  {
    name: 'the punctuation-differing complete review is recovered, flagged, whole', group: 'regression',
    out: MALPACO, opts: { doneWhen: 3 },
    check: (r) => r.kind === 'flagged' && r.review === MALPACO && r.recovered === 'approve'
      && r.note.includes('header differs') && r.note.includes('all 3 Done-when lines accounted for'),
  },
  {
    name: 'the same review with the exact header reads as ok', group: 'regression',
    out: `Final pass done\n${H}\n${body()}`,
    check: (r) => r.kind === 'ok' && r.verdict === 'approve',
  },
  {
    name: 'spacing, case and "PR 135" for "PR #135" are recovered too', group: 'regression',
    out: `**t32 review  (minimax m3) - PR 135 at ${SHA}**\n${body()}`,
    check: (r) => r.kind === 'flagged' && r.recovered === 'approve',
  },
  { name: 'a wrong task is no review', group: 'identity', out: `T33 review (MiniMax M3), PR #135 at ${SHA}\n${body()}`, check: (r) => r.kind === 'none' },
  { name: 'a wrong PR is no review', group: 'identity', out: `T32 review (MiniMax M3), PR #136 at ${SHA}\n${body()}`, check: (r) => r.kind === 'none' },
  { name: 'a PR number with an extra digit is no review', group: 'identity', out: `T32 review (MiniMax M3), PR #1350 at ${SHA}\n${body()}`, check: (r) => r.kind === 'none' },
  { name: 'a wrong commit is no review', group: 'identity', out: `T32 review (MiniMax M3), PR #135 at ${OTHER}\n${body()}`, check: (r) => r.kind === 'none' },
  { name: 'a short commit is no review', group: 'identity', out: `T32 review (MiniMax M3), PR #135 at ${SHA.slice(0, 10)}\n${body()}`, check: (r) => r.kind === 'none' },
  { name: 'another reviewer is no review', group: 'identity', out: `T32 review (Luna), PR #135 at ${SHA}\n${body()}`, check: (r) => r.kind === 'none' },
  {
    name: 'a reviewer whose name extends the brief\'s is no review', group: 'identity',
    header: 'T32 review (mm).', out: `T32 review (mm3)\n${body()}`, check: (r) => r.kind === 'none',
  },
  {
    name: 'a task whose id extends the brief\'s is no review', group: 'identity',
    header: 'T32 review (mm).', out: `T320 review (mm)\n${body()}`, check: (r) => r.kind === 'none',
  },
  {
    name: 'two recovered reviews are ambiguous', group: 'ambiguity',
    out: `${head()}\n${body('rework')}\n\n${head()}\n${body()}`,
    check: (r) => r.kind === 'flagged' && r.note.includes('ambiguous: 2 header-like lines'),
  },
  {
    name: 'an exact header followed by a header-like line is ambiguous', group: 'ambiguity',
    out: `${H}\n${body('rework')}\n\n${head()}\n${body()}`,
    check: (r) => r.kind === 'flagged' && r.note.startsWith('ambiguous'),
  },
  {
    name: 'opening and closing verdicts that differ stay flagged as such', group: 'verdict',
    out: `${head()}\n${body('approve', 'rework')}`,
    check: (r) => r.kind === 'flagged' && r.recovered === null && r.note.includes('verdicts differ: opens "approve", closes "rework"'),
  },
  {
    name: 'an unreadable verdict stays flagged as such', group: 'verdict',
    out: `${head()}\nlooks good\n\nR1: fine.\n\napprove`,
    check: (r) => r.kind === 'flagged' && r.recovered === null && r.note.includes('verdict unreadable'),
  },
  {
    name: 'a truncated review stays flagged as cut off', group: 'truncated',
    out: `${head()}\napprove\n\nDW1: ran npm test → 12 pass\n\nR1: the loop in`,
    check: (r) => r.kind === 'flagged' && r.recovered === null && r.note.includes('may be cut off'),
  },
  {
    name: 'a finding after the verdict stays flagged as such', group: 'finding-after',
    out: `${head()}\n${body()}\nR2: c.js:1 crashes (blocking)`,
    check: (r) => r.kind === 'flagged' && r.recovered === null && r.note.includes('a finding after the closing verdict'),
  },
  {
    name: 'a missing Done-when account is named', group: 'done-when',
    out: `${head()}\n${body().replace(/DW2:[^\n]*\n/, '')}`, opts: { doneWhen: 3 },
    check: (r) => r.kind === 'flagged' && r.note.includes('no DW line for 2'),
  },
  {
    name: 'a Done-when not run is named', group: 'done-when',
    out: `${head()}\n${body().replace(/DW3:[^\n]*/, 'DW3: not run — no display')}`, opts: { doneWhen: 3 },
    check: (r) => r.kind === 'flagged' && r.note.includes('Done-when 3 not run'),
  },
];

for (const c of CASES) {
  test(c.name, () => {
    const r = read(c.out, c.opts, c.header);
    assert.ok(c.check(r), JSON.stringify(r, null, 1));
  });
}

test('a recovered review is posted under a note, unlabelled, exit 4: never acted on', () => {
  for (const c of CASES.filter((x) => x.group !== 'identity' && !x.name.includes('exact header reads'))) {
    const plan = planPost({ read: read(c.out, c.opts, c.header), header: c.header ?? H, doneWhen: 3, source: 't', signature: 's' });
    assert.equal(plan.label, null, c.name);
    assert.equal(plan.code, 4, c.name);
  }
});

test('make-brief refuses a header with punctuation or the commit after the reviewer', async () => {
  // Its header is short and canonical, "T32 review (minimax)"; the PR and commit go on other lines.
  const { checkBrief } = await import('./make-brief.mjs');
  for (const h of ['T32 review (minimax).', `T32 review (minimax), PR #135 at ${SHA}`]) {
    assert.throws(() => checkBrief(`${h}\nYou review PR #135 at ${SHA}.`, SHA), /first line must be the review header/, h);
  }
  assert.doesNotThrow(() => checkBrief(`T32 review (minimax)\nYou review PR #135 at ${SHA}.`, SHA));
});

// The tolerance made too loose: chain.mjs rebuilt with one change, imported from a temporary file.
const SRC = fs.readFileSync(fileURLToPath(new URL('./lib/chain.mjs', import.meta.url)), 'utf8');
async function mutated(from, to) {
  assert.equal(SRC.split(from).length, 2, `the mutation target is in chain.mjs exactly once: ${from}`);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'chain-mutant-'));
  const file = path.join(dir, 'chain.mjs');
  fs.writeFileSync(file, SRC.replace(from, () => to));
  try { return await import(pathToFileURL(file).href); } finally { fs.rmSync(dir, { recursive: true, force: true }); }
}
const failing = (mod, group) => CASES.filter((c) => c.group === group)
  .filter((c) => !c.check(mod.readReview(c.out, c.header ?? H, c.opts))).map((c) => c.name);

const MUTANTS = [
  { group: 'identity', what: 'any text between the header\'s tokens',
    from: "tokens.map(esc).join('[^A-Za-z0-9]+')", to: "tokens.map(esc).join('.*?')" },
  { group: 'identity', what: 'only the task id and "review" compared',
    from: 'const tokens = header.match(/[A-Za-z0-9]+/g) ?? [];', to: 'const tokens = (header.match(/[A-Za-z0-9]+/g) ?? []).slice(0, 2);' },
  { group: 'identity', what: 'no bound after the last token',
    from: "join('[^A-Za-z0-9]+')}(?![A-Za-z0-9])`", to: "join('[^A-Za-z0-9]+')}`" },
  { group: 'verdict', what: 'the reader\'s own problem dropped from the note',
    from: 'if (r.kind !== \'ok\') notes.push(r.note);', to: '' },
  { group: 'verdict', what: 'the recovered verdict taken from the opening line whatever the reader found',
    from: "recovered: r.kind === 'ok' ? r.verdict : null", to: 'recovered: \'approve\'' },
];
for (const m of MUTANTS) {
  test(`too loose (${m.what}): the ${m.group} cases fail`, async () => {
    const mod = await mutated(m.from, m.to);
    assert.ok(failing(mod, m.group).length > 0, `no ${m.group} case failed with the mutation`);
  });
}
