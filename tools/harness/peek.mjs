#!/usr/bin/env node
// #262: ported from diegoami/goal2 PR 178 (squash e0cab8b). The OpenCode 2 half of tools/harness/peek.sh,
// which execs it when the CLI reports 2.x (a 1.x CLI keeps peek.sh's own v1 reader).
//
//   node tools/harness/peek.mjs ses_XXXX|<run.json>|<run log> [-n 20]
//
// The target resolves to the run's retained receipt (run.json): a bare session id through the receipt
// index of the v2 runs, a run log through its "session ses_… started" line. A finished run is read from
// its retained export.json; a running one through a private `session export --standalone` against that
// run's own data directory, never the shared background service.
import { resolveOpenCode } from './lib/opencode.mjs';
import { findReceipt, peekRecord, renderPeek } from './lib/opencode-peek.mjs';

try {
  const [target, ...args] = process.argv.slice(2);
  if (!target) throw new Error('usage: peek.sh ses_ID|run.json|run.log [-n N]');
  const n = args.includes('-n') ? Number(args[args.indexOf('-n') + 1]) : 20;
  if (!Number.isSafeInteger(n) || n < 1) throw new Error('-n must be a positive number');
  const env = process.env.OPENCODE_BIN ? { ...process.env, HARNESS_OPENCODE_EXE: process.env.OPENCODE_BIN } : process.env;
  const cmd = resolveOpenCode(env);
  const receipt = findReceipt(target);
  if (!receipt.record) throw new Error(`no retained v2 run receipt names ${receipt.sessionID}: a run of the 1.x CLI is read with HARNESS_OPENCODE_EXE (or OPENCODE_BIN) set to that 1.x binary`);
  console.log(renderPeek(await peekRecord(cmd, receipt), 2, n));
} catch (e) { console.error(`peek: ${e.message}`); process.exitCode = 1; }
