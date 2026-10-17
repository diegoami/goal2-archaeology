# T297: the evidence for the CI tiers (issue #297)

All measured on 2026-10-17; none is edited after it is committed.

- `before-20261017.txt`, `before-20261017-jobs.json`: `python3 tools/ci_minutes.py --days 30` before the
  change (counts, billed minutes by job and by day; the raw per-job rows).
- `module-times-local-20261017.txt`: seconds per `tests/test_*.py` on the author's machine (all tools present).
- `ci-module-times-20261017.txt`: seconds per unit-test module on GitHub's runner, from the per-test timestamps
  of run 39031916644 (the full suite on this PR's first working push).
- `trace_deps.py`, `slow-module-deps-20261017.json`: the repository paths each slow module opened or executed,
  recorded with an audit hook; `tests/test_ci_gate.py` requires every one of them to classify as `full`.
