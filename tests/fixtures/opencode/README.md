# OpenCode protocol fixtures (#262)

`v2-live/run-*` are nonbilling captures of the installed OpenCode 2.0.28 (binary SHA-256
`20d305d0140bfe04df7264a4ecb014402b74b6ac0a0f6456ee07ef3325fb4a85`) made by
`node tools/harness/probe-opencode.mjs --out tests/fixtures/opencode/v2-live`. Each run's
`manifest.json` records every file's SHA-256, the binary's and the probe's. No prompt was sent: the
only session is one the probe created empty in a throwaway data directory, and its export shows zero
cost and zero tokens. Model and agent registries are projected to whitelisted fields (their request
settings can hold provider keys); the full responses are kept as hashes only. Never edit a capture;
make a new run.

- `run-3Ai73R`: the complete capture the tests read.
- `run-EFh0VF`: the first, partial run. It stopped on its own assertion and is kept because its
  `old-commands.json` is the one record of the 1.18 lookup `session list --format json -n 20`
  succeeding on v2: through the managed background service (`serve --service`), which that command
  starts when none runs. The probe no longer runs it.

The same binary, driven by the harness itself (each folder's JSON names the binary, policy and guard
hashes; none sent a prompt to a provider):

- `preflight-q4Sij9` (`node tools/harness/preflight-opencode.mjs --out tests/fixtures/opencode/v2-live`):
  the review transport up to generation: the guard staged and active (`plugins.json`), this checkout's
  reviewer translated and loaded as `profile.json` (v2's defaults first, then our rules), the selected
  MiniMax-M3 `thinking` advertised, catalogue parity, an owned empty session exported with zero usage,
  peeked privately, interrupted as a no-op, and an unrelated private server's session unchanged.
  `preflight-a5ERJV` repeats it with `location.json`: run from this git worktree, v2's project
  directory (the inside root of its file checks and of the guard) is the worktree itself; the main
  checkout appears only as `canonical`.
- `native-complete-*`, `native-reject-*`, `native-cancel-*`
  (`node tools/harness/probe-opencode-guard.mjs [--complete|--active-cancel] --out …`): real review
  sessions whose only model is a deterministic fake provider on 127.0.0.1 (zero tokens; no provider
  contacted). `complete`: a clean review comes back through `run --server`, its final text read from the
  export. `reject`: outside-file reads (plain, quoted, nested, relative, /proc) are rejected by the guard,
  `/etc/hostname` and `git push` by the native denies, while worktree, /tmp, ~/goal2-review-tmp and
  /etc/timezone reads return their contents. `cancel`: the idle limit interrupts a live tool, its worker
  dies, and an unrelated session on the same database survives. `native-cancel-vCgTPG` is the first
  cancel run, kept: the cancellation passed, then the probe stopped on a missing usage record, which
  opencode-workflow.mjs now takes from the session info when the export is refused.
- Round 2 (PR 332, Sol's R1 and R2), after the scanner evaluates every word statically:
  `native-reject-jDKeDo` adds `"cat" <outside file>` (R1), `cat "<outside dir>"/secret.txt` (R2),
  `c""at <outside file>`, `cat '<outside dir>'/secret.txt` and a `$(…)` operand, all rejected, while
  `"cat" inside.txt` returns its contents; `native-complete-pfrsd0` and `native-controls-bQt6x6` repeat
  the clean run and the controls on the new scanner.
- Round 3 (Sol's R1): `native-reject-E2Xw3B` adds `$'cat\0junk' <outside file>`, rejected.
- `native-controls-7CuxTr` (`node tools/harness/check-opencode-guard-controls.mjs --out …`): the same
  rejection probe on a scratch copy with one guard line removed: v2 then returns `OUTSIDE_SENTINEL`
  to `cat <outside file>`, so the probe fails on "external-cat must be rejected".

The other files are synthetic and schema-shaped (ported from goal2's T72a fixtures): they are not
observed model or tool execution and carry no billed usage. `tests/opencode_protocol.test.mjs` gives
them the live capture's session id and directory before use.

- `v2-synthetic-export.json`, `v1-synthetic-export.json`: a complete assistant turn with two text
  segments, reasoning, a rejected and a completed tool call, in each major's layout (v1: `info`/`parts`
  and `state.error` as a string; v2: flat messages with `content` and structured errors).
- `v1-actual-metadata-step-projection.json`: goal2's read-only projection of real v1 assistant and
  step metadata (step-start/step-finish, optional total tokens); read as given.
- `v2-synthetic-idle.json`: an Idle message shaped from the installed schema.
- `synthetic-permissions.json`: a v2 permission request list.
