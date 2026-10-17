# T297: the evidence for the CI tiers (issue #297)

All measured on 2026-10-17; none is edited after it is committed.

- `before-20261017.txt`, `before-20261017-jobs.json`: `python3 tools/ci_minutes.py --days 30` before the
  change (counts, billed minutes by job and by day; the raw per-job rows).
- `module-times-local-20261017.txt`: seconds per `tests/test_*.py` on the author's machine (all tools present).
- `ci-module-times-20261017.txt`: seconds per unit-test module on GitHub's runner, from the per-test timestamps
  of run 39031916644 (the full suite on this PR's first working push).
- `trace_deps.py`, `slow-module-deps-20261017.json`: the repository paths each slow module opened or executed,
  recorded with an audit hook (`PYTHONPYCACHEPREFIX=<empty dir> python3 notes/T297/trace_deps.py <root>
  tests/<module>.py <out.json>`: an empty cache prefix makes Python open the sources, not stale .pyc files);
  `tests/test_ci_gate.py` requires every one of them to oblige that module.
- `replay-20261017.txt`: `python3 tools/ci_minutes.py --days 30 --replay-since 2026-10-12`, the "before" table
  again plus what the 66 PRs of the last six days would have billed under the obligations.
- `after-20261017.txt`: the same command once the change is on this PR. The 30-day API totals cannot move
  until the change is merged and new runs accumulate, so the comparison is `replay-20261017.txt` and the
  measured runs.
- `runs-20261017.md`: the real runs on PR 298 (and a throwaway PR 299) with the tier each chose, wall time
  and billed minutes.
