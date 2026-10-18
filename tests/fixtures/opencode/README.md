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
