#!/usr/bin/env node
// Switches the defaults in harness.json (the roster is the owner's to change, 2026-10-11), with the
// checks a hand edit skips. The /switch-model skill says when and how.
//
//   node tools/harness/switch-model.mjs --show
//   node tools/harness/switch-model.mjs --role implementer --model sonnet|opus|haiku|fable|<model id>|session [--dry-run]
//   node tools/harness/switch-model.mjs --role reviewer --model PROVIDER/ID
//     [--variant high] [--name NAME] [--family FAMILY] [--probe] [--dry-run] [--force]
//   node tools/harness/switch-model.mjs --ask on|off [--dry-run]
//   node tools/harness/switch-model.mjs --review-kind fix|research --model NAME [--probe] [--dry-run]
//   node tools/harness/switch-model.mjs --block FAMILY-OR-ID-FRAGMENT | --unblock ... [--dry-run]
//
// The implementer is the `implementer` subagent spawned inside Claude Code on a Claude Code alias
// or a model id the session's provider serves (Opus spawns Sonnet; under Z.AI `sonnet` is GLM-5.3
// Flash), or `session`: the main session implements directly where the provider cannot spawn one.
// Both run through the session's Anthropic environment, so no OpenCode check applies and the
// family is the session's (lib/common.mjs sessionFamily, printed by --show).
// The reviewer is an OpenCode model:
// 1. OpenCode must list the id in the scripts' own data directory (as review.mjs checks before
//    every run): an unknown id or a missing login exits 3 with the command that fixes it.
// 2. Unless --variant is given, the effort is high for a light model and low (else medium, else its
//    lowest) for a heavy one, from the efforts OpenCode offers (L54); max is refused (L27). The
//    family comes from the id unless given; the session's family and the blocked list are refused.
// 3. --probe sends a one-word prompt through the watched runner at that variant, in a throwaway
//    git directory under the work root. It is one small billed call, and a failure stops the switch.
// 4. reviewer.default becomes this model; other models stay for an explicit --reviewer.
// --block adds a family ("deepseek") or an id fragment to harness.json's blocked list, which
// review.mjs and this script refuse; --unblock removes it. --dry-run prints and writes nothing.
//
// --ask on|off sets dispatch.ask and --review-kind KIND --model NAME sets dispatch.reviewerByKind[KIND]
// (rule 2a); NAME is a registered harness.json name and gets the reviewer checks (not blocked, not the
// session's family), with the OpenCode probe only under --probe. --show prints the dispatch line.
//
// Exit 0: switched (or shown, or a dry run). Exit 1: refused. Exit 2: usage. Exit 3: OpenCode, the
// login or the probe failed; nothing written.

import fs from 'node:fs';
import path from 'node:path';
import { randomBytes } from 'node:crypto';
import { runOpenCodeWatched, resolveOpenCode, OpenCodeInfraError, modelVariants } from './lib/opencode.mjs';
import { planSwitch, planBlock, planDispatch, showRoles, defaultVariant } from './lib/switch.mjs';
import { sh, repoPaths, loadConfig, parseArgs, prepareOpenCode, sessionFamily } from './lib/common.mjs';

const say = (s) => console.log(s);
const die = (code, s) => { console.error(s); process.exit(code); };

const a = parseArgs(process.argv.slice(2), { flags: ['show', 'probe', 'dry-run', 'force'] });
const top = sh('git', ['rev-parse', '--show-toplevel']);
const file = path.join(top, 'harness.json');
const config = loadConfig(top);
const own = sessionFamily();
if (a.show) { say(showRoles(config, { sessionFamily: own })); process.exit(0); }
const write = (next, before, after) => {
  say(`before: ${before}`);
  say(`after:  ${after}`);
  if (a['dry-run']) { say('dry run: harness.json not written.'); process.exit(0); }
  fs.writeFileSync(file, `${JSON.stringify(next, null, 2)}\n`);
  say(`written: ${path.relative(process.cwd(), file) || file}. Commit it on main with the reason for the change (L25).`);
};
// One small billed call at the entry's variant, in a throwaway repository; a failure exits 3.
async function probe(name, entry, opencode, env) {
  const { workRoot } = repoPaths(config);
  const dir = path.join(workRoot, `probe-${randomBytes(4).toString('hex')}`);
  fs.mkdirSync(dir, { recursive: true });
  sh('git', ['init', '-q', dir]);
  let failure = null;
  try {
    const args = ['run', '--dir', dir, '--model', entry.id, ...(entry.variant ? ['--variant', entry.variant] : [])];
    // v2 (#262) needs the exact selection and a trusted agent: the reviewer of this checkout, in the
    // probe's own empty repository; v1 runs the command line as before.
    const run = await runOpenCodeWatched({
      args, model: entry, agent: 'reviewer', agentFile: path.join(top, '.opencode', 'agents', 'reviewer.md'),
      prompt: 'Reply with the single word PONG and nothing else.', workDir: dir, title: `probe-${name}`,
      startupTimeoutMs: 120_000, idleTimeoutMs: 120_000, totalTimeoutMs: 300_000, pollMs: 2_000,
      opencode, env, log: () => {},
    });
    if (run.exitCode !== 0 || !/PONG/i.test(run.reviewText ?? run.stdout)) {
      failure = `probe failed (exit ${run.exitCode}): ${run.output.split(/\r?\n/).slice(-5).join(' | ')}`;
    } else say(`probe: ${entry.id} answered PONG in ${run.seconds} s`);
  } catch (e) {
    if (!(e instanceof OpenCodeInfraError)) throw e;
    failure = `probe failed: ${e.reason}`;
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });       // before any exit: process.exit skips finally
  }
  if (failure) die(3, `${failure}. Nothing written.`);
}

if (a.block || a.unblock) {
  if (a.model || a.role) die(2, '--block/--unblock go alone.');
  let plan;
  try { plan = planBlock(config, { block: a.block, unblock: a.unblock }); } catch (e) { die(/^Refused/.test(e.message) ? 1 : 2, e.message); }
  write(plan.config, plan.before, plan.after);
  process.exit(0);
}
if (a.ask !== undefined || a['review-kind'] !== undefined) {
  if (a.role) die(2, '--ask and --review-kind go without --role.');
  if (a['review-kind'] !== undefined && !a.model) die(2, '--review-kind needs --model NAME.');
  if (a['review-kind'] === undefined && (a.model || a.probe)) die(2, '--model and --probe go with --review-kind.');
  let plan;
  try { plan = planDispatch(config, { ask: a.ask, reviewKind: a['review-kind'], model: a.model, sessionFamily: own }); } catch (e) { die(/^Refused/.test(e.message) ? 1 : 2, e.message); }
  if (a.probe) {
    let opencode;
    try { opencode = resolveOpenCode(); } catch (e) {
      if (e instanceof OpenCodeInfraError) die(3, `OpenCode unavailable: ${e.message} Nothing written.`);
      throw e;
    }
    const models = { [plan.name]: plan.entry };
    const pre = await prepareOpenCode({ opencode, chain: [plan.name], models, env: process.env, cwd: top, log: say });
    if (!pre.usable.length) die(3, `${pre.problems.join('; ')}. Nothing written.`);
    await probe(plan.name, plan.entry, opencode, pre.env);
  }
  write(plan.config, plan.before, plan.after);
  process.exit(0);
}
if (!a.role || !a.model) die(2, 'Usage: switch-model.mjs --role implementer|reviewer --model ... [--probe] [--dry-run], --block X, --unblock X, --ask on|off, --review-kind fix|research --model NAME, or --show');
if (a.role === 'implementer') {
  let plan;
  try { plan = planSwitch(config, { role: 'implementer', id: a.model, sessionFamily: own }); } catch (e) { die(/^Refused/.test(e.message) ? 1 : 2, e.message); }
  write(plan.config, plan.before, plan.after);
  process.exit(0);
}
if (!own) die(1, `The session's family cannot be told from ANTHROPIC_BASE_URL=${process.env.ANTHROPIC_BASE_URL}: set HARNESS_SESSION_FAMILY, so the reviewer can be kept out of it.`);

let plan;
try {
  plan = planSwitch(config, {
    role: a.role, id: a.model, variant: a.variant ?? defaultVariant(a.model, null), name: a.name, family: a.family, force: a.force, sessionFamily: own,
  });
} catch (e) { die(/^Refused/.test(e.message) ? 1 : 2, e.message); }
say(`${a.role}: ${plan.name} = ${plan.entry.id} (${plan.entry.variant ?? 'no variant'}, family ${plan.entry.family})`);

let opencode;
try { opencode = resolveOpenCode(); } catch (e) {
  if (e instanceof OpenCodeInfraError) die(3, `OpenCode unavailable: ${e.message} Nothing written.`);
  throw e;
}
const models = { [plan.name]: plan.entry };
const pre = await prepareOpenCode({ opencode, chain: [plan.name], models, env: process.env, cwd: top, log: say });
if (!pre.usable.length) die(3, `${pre.problems.join('; ')}. Nothing written.`);
say(`listed: ${plan.entry.id}`);
// The default effort, from what OpenCode offers for this model (L54).
if (!a.variant) {
  const offered = await modelVariants(opencode, plan.entry.id, { env: pre.env, cwd: top });
  const v = defaultVariant(plan.entry.id, offered);
  if (v !== plan.entry.variant) {
    plan = planSwitch(config, { role: a.role, id: a.model, variant: v, name: a.name, family: a.family, force: a.force, sessionFamily: own });
    say(`${a.role}: ${plan.name} = ${plan.entry.id} (${plan.entry.variant}, family ${plan.entry.family}): the lowest effort it offers (L54)`);
  }
}

if (a.probe) await probe(plan.name, plan.entry, opencode, pre.env);

write(plan.config, plan.before, plan.after);
