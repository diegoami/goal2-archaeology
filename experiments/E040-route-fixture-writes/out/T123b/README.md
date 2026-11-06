# T123b bounded pre-match squad swap evidence

Static first: named `seg_0791_12.c` DEA6, then all DEA6–DFDC instructions in `code/seg_0791_22.asm`. They establish the two Enter stages, retained pane words in DE27/DE51 calls, clearing parent fields before swap, the real re-sort calls and DF30's 16-bit target wrap from printed 1230C to existing 230C. Original-backed runs corroborate frames, ordered caller-visible writes and real re-sort effects. No source routine is replaced by a strength/sort/action stub.

Entry `selection.PORTS.entries['0791:DEA6']`, `ret 2`, takes the original E44F parent BP as its sole near argument. Parent fields: country +6, mark -1, side -3, current pane -5, marked pane -7, marked index -9, marked scroll -11. Cursor is DS:0C1B. Supported: C1F clear, current pane1, active mark's pane1; C1E=0 uses real 1771:52CC, nonzero C1E uses real near0791:230C. Unsupported pool involvement or in-match mode raises PortError before any memory write. A stale marked pane while mark is inactive is overwritten by the first successful mark. This adds no legal-eleven choice or product-facing selection policy.

`baseline/unit-red.log` records every initial behavioral test failing on the unmodified runtime. `baseline-final-v2` runs the exact final eight-test module against archived unchanged `33fc2c8d` code. The only change to old `test_port_selection.py` is the main-authorized additive DEA6 return entry/count name; its nine existing ABI entries and all behavior assertions remain. `unit-v3` includes actual retained-pane helper-frame, wrapped return-site and live post-sort-read checks.

`raw-v2` compares ten isolated cases on native published records, with explicit hash-only synthetic parent/empty-slot edits. C1E1 inputs come from real original F1F6/A4A1 execution stopped at ED8A pre-match menu; C1E0 starts from the native published source. Every helper/re-sort remains original in this proof. Prover compares ordered LIVE/caller-visible writes and guest-call/frame effects; independent runs also match complete final memory (dead frames included) and ALLREGS. Intermediate dead-stack stores follow the established Regs/Prover coalescing protocol, not an ISA-level chronology claim. Actual original re-sort calls and post-sort live squad reads are retained. Private raw-v1 constructor-field calibration was not published: `raw-v1-private.json` records its preserved private location/hashes; sanitized v2 contains only field-edit before/after hashes.

`sealed-v1` runs actual PortMachine calls with real existing helpers only and fresh-process positive Unicorn import/GOAL.EXE read denial. It compares complete canonical state and records/RNG/parent fields to the unported original, except dead helper locals at **SS9000:2000 inclusive to SS9000:3000 exclusive**. All caller locals are outside that range. Six unsupported cases preserve every body-entry memory byte, including all records and RNG. `falsifiers-v1` catches both omitted word-swap and omitted parent-mark-clear variants for both re-sorts.

`natural-v1` is a retained failed harness calibration: a fixture label used nonexistent Match.fixture instead of opts[index], failing before the first port body. `natural-v2` is a new T123b proof on the accepted T124t round1 checkpoint, not a resumption of old-source T124t execution. It restores the complete register/waiting-key context from the immutable receipt, runs original RouteMatch's actual key policy, installs/proves only DEA6 on each actual Match machine, and retains all key logs, genuine E44F BP chains, both mark-stage entries/results, subsequent stages and private checkpoint digests. The automatic legal-eleven choice remains solely T124t's comparison harness. Full public sealed route/keyboard context remains T123's parent work.

## Accepted receipt index

`final-audit/index.json` audits ten raw cases, sixteen sealed cases (six unsupported), four caught falsifiers, two natural DEA6 calls during nine managed matches, the following stage3/4 transitions and six normalization controls. It checks every source/receipt hash. The final exact eight-test command passes (`final-audit/unit.log`); the combined new/existing selection run passes all25 (`unit-v3/unit.log`), and all eight new tests fail on archived unchanged33fc runtime (`baseline-final-v2/unit-red.log`). Annotation checks and pinned Ghidra/JDK regeneration pass; the three decompiler warnings are unchanged baseline functions.

The new natural proof's complete private checkpoint digests **and all sixteen CPU registers plus waiting_key** match accepted T124t after each of rounds2,3,4. Match results, complete team choices/key sequences and stage counters match exactly. The actual swap is fixture847, country16, C1E1/C1F0; genuine E44F parentBP16016 returns through E99C, with mark0→1 then1→0 and `ret 2` restoring SP+4. The first entry's inactive stale marked-pane value is deliberately ignored, as the original does; the active marked pane becomes1. Subsequent stage work resumes from the new T123b round2 checkpoint with waiting_key13 and complete CPU context restored. This is stronger than a synthetic parent-only test, while remaining a bounded leaf proof rather than T123's complete sealed outer-route delivery.

Normalization excludes only dead helper locals at physical SS9000:2000..2FFF in the focused sealed family; parent fields at SS9000:4000 and all records/RNG remain compared. The audit falsifies parent-mark/RNG mutations and both exclusion boundaries, while confirming only the two inside-bound controls are ignored. Raw comparisons also match final dead-frame bytes. No ISA-level intermediate dead-stack chronology is claimed.

Reproduce with fresh exclusive output names in a new tracked T123b batch directory:

```sh
tools/heavy.sh t123b-unit -- python3 -B -m unittest tests.test_port_pre_match_swap tests.test_port_selection -v
tools/heavy.sh t123b-raw -- python3 -B experiments/E040-route-fixture-writes/out/T123b/prove.py --out NEW-raw.jsonl
tools/heavy.sh t123b-sealed -- python3 -B experiments/E040-route-fixture-writes/out/T123b/sealed.py --out NEW-sealed.jsonl
tools/heavy.sh t123b-natural -- python3 -B experiments/E040-route-fixture-writes/out/T123b/continuation.py --out NEW-natural.jsonl
tools/heavy.sh t123b-audit -- python3 -B experiments/E040-route-fixture-writes/out/T123b/verify.py --out NEW-index.json
python3 tools/static/check_annotations.py
```

Full suites/gates remain CI work. Private memory components/checkpoints and the unpublished unsanitized calibration source/receipts remain ignored, with hashes and restoration locations recorded; they never enter git.
