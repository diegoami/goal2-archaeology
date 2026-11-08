# T128: pre-match pool selection

[confirmed: original listing DEA6–DFDC and DDCB–DE24; main task #701] DEA6 now implements the original current-pool DBFA gate, retained pool index/scroll and existing swaps/re-sorts. DDCB is the inseparable36-instruction ret2 leaf explicitly released by main763a5f74 after the real-helper control exposed its absence. DBFA/DC7E and assistant policy are unchanged. F031 remains proposed/unreviewed V1; these isolated frames do not resolve its C29 or establish a natural season/UI journey.

Validation:41 focused tests passed in48.434s with no skips (`controls-final-v1.log`):

- 15 DEA6 original-backed cases: first/empty mark, both swap directions, pool pairs/same-entry, both C1E sorts, finals/tour refusals and current-squad bypass of DBFA despite a retained pool mark.
- 6 standalone DDCB cases: manager/base/scroll/cursor,16-bit wrap, ret2 and complete memory/register effects.
- 5 gate/index/scroll/swap/mark falsifiers detected.
- 4 code-free sealed exact primitive cases, with positive Unicorn/GOAL.EXE denial.
- 5 separate real registered-helper sealed cases, also with positive denial. These exercise actual DBFA/DDCB/DE27/DE51/swap/sort ports, not the isolated primitive oracle.

The original executes in CPython/Unicorn. Every new candidate executes in a verified PyPy3.11 child through the trusted local pickle4 protocol. Native records come from the hash-verified existing E006 input; parent/cursor/window/empty-slot fields are explicitly synthetic. No asset bytes or complete guest-memory payloads enter public logs or Git.

The exact primitive comparison checks all1,114,112 bytes (`Machine.MEM_SIZE`, including HMA) and ALL16 final registers. Every original helper-entry full memory/ALL16 is compared before its original effects are replayed privately, isolating the primitive body from unrelated existing helper scratch behavior. Both complete write traces and original helper-entry snapshots are retained in ignored `.cache/t128-private-traces/*.pickle.gz`; public records bind their SHA-256. This oracle replay is **not** the real-helper closure proof. That separate control compares complete gameplay/caller record fingerprints, RNG and caller ABI; it does not claim a new full-scratch-register proof of previously accepted helpers.

[designed: main e97ac60f, `docs/requests/701-order-boundary.md`] Ordered byte writes are compared outside exactly the original-measured lowest stack while writing through caller returned SP. Prover's push detection is reused; no padding or enlarged interval. Caller mark/index/scroll and squad/pool records are explicitly outside it. Full final/helper memory has **no value mask**, including every dead-stack byte. This is the established live-write proof boundary, not instruction-by-instruction write fidelity.

Red-before evidence:11tests/15 new pool errors on the bounded T123b guard; the later standalone DDCB control failed6 missing-entry cases. Retained calibration failures include the overbroad raw instruction-order check (also fails unchanged accepted within-twenty code), missing DDCB real-helper run, and a verifier-only1MiB literal corrected to the existing MEM_SIZE constant. None is relabelled as a pass. Old within-twenty bodies/assertions remain identical; obsolete pool-refusal cases became the new positive matrix, while all C1F no-write assertions remain. The exact selection registry inventory adds DDCB. Only the now-stale DEA6 annotation was updated; pinned Ghidra regeneration changed one generated comment and annotations pass.

Reproduce focused tests after sourcing `.cache/cloud.env` through a registered `tools/heavy.sh` job:

```sh
python3 -B -m unittest tests.test_port_pre_match_swap tests.test_port_pool_swap tests.test_port_selection tests.test_port_assistant -v
```

Verify receipts and retained private traces without engine execution (choose a fresh output path):

```sh
python3 -B experiments/E040-route-fixture-writes/out/T128/verify.py --out /tmp/t128-verification.json
```

The source digests bind exercised files even when a job starts from a committed base with uncommitted implementation. Final-head verification rechecks these digests. Failed/calibration outputs are immutable. No Match/API/UI/worker change, full suite, reviewer or merge was performed by this implementer; required full suites remain CI-owned.

Model: Codex GPT-6 family; exact variant unavailable.
