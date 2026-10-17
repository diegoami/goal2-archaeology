# T304: the emulator tests in CI (issue #304)

Measured on 2026-10-17 on GitHub's runner; none of these files is edited after it is committed.

- `deps-test_emul_match-20261017.json`: the repository paths `tests/test_emul_match.py` opened or executed
  (`PYTHONPYCACHEPREFIX=<empty dir> python3 notes/T297/trace_deps.py . tests/test_emul_match.py <out>`);
  `tests/test_ci_gate.py` requires every one of them to oblige that module (`SLOW_DEPS`).
- `ci-run-39044831537-*`: the PR's first run (the CI definition changed, so every module was named): the
  result lines of the three emulator modules (`-emul-test-lines.txt`; a test whose guest prints a WARNING
  shows its `ok` on a later line), the totals (`-summary.txt`: `Ran 1334 tests in 777.581s`, `OK (skipped=39)`,
  none of the 39 an emulator test), seconds per module (`ci-module-times-20261017.txt`) and the steps
  (`ci-steps-39044831537.txt`, checks job 859 s).
- `ci-run-39046016344-emul-test-lines.txt`, `ci-module-times-fast-tier-20261017.txt`, `ci-steps-39046016344.txt`:
  the next push (the fast tier: no slow module named): `test_emul_watched` and `test_emul_skip_ret` run, checks
  job 202 s.
- `ci-steps-39033020879-fast-tier-before.txt`: the same tier before the change (PR 298's run, 171 s).

## What the three tests do in CI now

| module | runs in CI | needs |
|---|---|---|
| `test_emul_skip_ret` (1 test, 0.1 s) | yes, every code PR | unicorn |
| `test_emul_watched` (6 tests, 21 s) | yes, every code PR | unicorn and the E011-r0001 half-time savestate (a release asset, `gh release download` with the job's token, 3 of the 6 read it; it is cached under `.cache/dl`) |
| `test_emul_match` (66 tests, 376 s) | yes, when the PR touches what it reads (or on a CI-file change, a manual run, a nightly run with code landed) | unicorn and the E011-r0001 watchstart savestate (same way) |

None of the three needs the E006-r0001 reference image (`test_original_match` and three tests of
`test_e036_family` do, and still skip in CI: "unicorn or the E006-r0001 image (.cache/dl) missing"; the image
was not fetched, see the PR). No test of the three skipped in either run.

## What it adds

- Code tier (every code PR): unit step 85 s -> 121 s (+36 s): `test_emul_watched` 21 s, `test_asset_cache`
  9 s (it skipped without unicorn), the rest is smaller. The checks job went 171 s -> 202 s, 3 -> 4
  billed minutes in these two runs (the pip step is 1 s with the cache; the apt step varies
  from run to run).
- `test_emul_match`: 376 s on the runner (187 s on the author's machine); one test,
  `RealGuestTests.test_the_gate_falsifier_is_not_reached_by_e011`, is 361 s of it. It runs only when a PR touches
  `runtime/emul/`, `runtime/driver/`, `runtime/model/`, `experiments/E021-m0-whole-match/`, `runs/E011/`,
  `static/goal-exe/code/` or its own files; a full run (CI-file change, manual run, nightly with code landed)
  went from about 430 s to 859 s (8 -> 15 billed minutes).
