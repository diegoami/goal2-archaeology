# Independent substitution request and timed opportunity (#695)

Model: inherited Codex GPT-6 family; exact variant unavailable. Base:
4fe3a973e22c2f7fa37475bfed2b6b5a71db8f08. Scope is the two facade/key-plan files,
new focused tests/proof tools and API/evidence documentation. No goal2 checkout,
vendor files, port bodies, task definitions, full suite, reviewer or merge.

The accepted API shape is `substitution_control=True`; an ordinary paused
`answer(request_substitution=True|False, edit_only=True)` executes real E44F
keys, idempotently, and returns authoritative request state before Play.
`substitution_opportunity` then exposes actual original timeout/keeper state;
`opportunity="accept"|"dismiss"|"timeout"` supplies Enter/Esc/no key. Only a real
original menu entry yields the separate legal substitution decision, where a
newly chosen pair can be confirmed edit-only. No direct latch store or fake pair.

The facade's historical `keeper_unavailable` label at a legacy notice read
neararg+2 (side). To retain default streams it remains historical in that profile.
The new profile correctly reads neararg+4 (keeper). Side1/keeper0 is explicitly
separate from side0/keeper1. The old measurement records are not rewritten.

`static-v1.md`, `notice-template-v1.py/json` record the named/raw E44F/8062/7FCF/
CC2E reading and packed-screen decode. Actual bounded probes confirm poll counts
and rendered row attributes. Ordinary400polls×10nominalms; keeper1000×10. Raw
original Esc and timeout skip an ordinary menu; an unavailable keeper forces it.
The desired UIEsc-to-accept is owner-designed adaptation, and any blinking
headline is distinct from original0x70 headline/no blink plus0x8D blinking hint.
No guessed measured two-second timeout, permanent mandatory notice or centered
modal is claimed original behavior.

Natural original/port whole-match recipes in `proof-v2.py` cover request→real
stoppage→accept→choose/swap→Play, desired-state repeats, cancel, zero-budget
refusal, rawEsc dismissal and timeout. Pause acknowledgements retain exact
clock/RNG/score/all20 player records/squad order/budget. Cancel and zero runs have
no request-caused opportunity. Dismiss/timeout resumes with the latch still set,
then a real subsequent pause/cancel clears it. Each recipe finishes the match.
`composite-v1.py` additionally requests live_players=True and checks every
20-record ordered packet against its actual guest bytes at every decision.
Complete event fields are compared without stripping player_records.

Original/PyPy port pairs compare full physical memory, complete events, draw
stream, all DS/ranges, key transcript and boundary/timeout counters. Every result
field is compared too; the sole cross-backend difference is existing `ports`
execution metadata. No event field or memory byte is masked. Same-backend
checkpoint replays retain exact full results including metadata, events, physical
memory, keys, boundaries and waits. `legacy-v1.py` proves actual old queued-pair
clients still work: default vs explicitFalse is exact and matches the exported
pre-change runtime in complete results/events/RNG/physical memory.

Prepared keeper evidence is deliberately separate from natural proofs. Common
original8062entry memory/all16regs is captured after a real request, with genuine
managed endpoint0 or1. Fresh original/PortMachine execution at this ABI boundary
has no active parent-coroutine/save-resume claim. For the keeper branch only,
one disclosed player energy byte is0 in the COMMON input before any callee local
is captured. It is not a natural injury, complete keeper replacement or production
state edit. Actual8062/7FCF runs to the forced menu or function return, retaining
all original menu reordering/effects and comparing complete endpoints/timer/keys/
RNG/memory/regs without normalization. No request latch is injected.

Earlier controls are immutable calibrations: before-v1 has an invalid helper
import; before-v2 is the initial8-test red baseline and before-v3 verifies all9
final tests red against exported old code. Initial proof-v1 rejected observer
kwargs/replayed the wrong generator and its first delay count included later
prompt waits. V2 fixes only those producer mechanics. Keeper-v1's post-capture SS
flag edit cannot change a suspended Python coroutine's cached local and is not
valid original/port input equivalence. Keeper-v2 wrongly assumed ED8A would not
reorder the squad; original ED8A calls resort_pitch_and_bench. Keeper-v3 preserves
those effects but starts each backend from its own prefix, exposing inherited
entry scratch/stack differences. These are not production bugs and are not hidden
by a mask. Only the shared-original-frame supplement is final keeper ABI evidence.
Primary natural request acknowledgements retain their order/record invariants.

Runtime adoption pins (only these facade files changed):

- runtime/original_match/match.py: e949159c9cc77f4d195bc9b150c67dfd913ba447417375122bc58db1bca97f92
- runtime/original_match/screens.py: 8ce9b0d6c4c9f75da469c728a9ed03787e413aeb5f98693ba38c914ed36d143e

Downstream adoption is main's deliberate byte-identical vendor/provenance update.
It must preserve false cancellation through any truth-value filtering, opt in
explicitly, validate the required boolean/notice data at the packet boundary and
retain every unrelated exact match/career assertion. This PR makes no UI change.
Raw game/record/memory/save bytes remain in ignored .cache/fix695; public receipts
carry hashes/counts, literal key codes and declared control metadata only.


Final comparison: `comparison-v2.json`, produced by `compare-v2.py`, validates
private full outputs without republishing them. It passes6full natural pairs,
2within-backend exact replay comparisons,2actual legacy/pre-change comparisons,
2shared-original-input bounded controls and the existing request-not-set omission.
The composite profile validates37decisions×20records=740records per backend.
The final focused controls pass30/30; all9new controls fail on immutable old code.
`acceptance-v1.json` binds current source/public evidence/private artifact hashes.
`verify-v1.py` is static; `--private` also verifies retained original artifacts.

Focused reproduction (source `.cache/cloud.env`; one registered heavy job/selector,
unique immutable output/private stem; no full unit suite or local gate):

```bash
PYTHONPATH=runtime python3 -m unittest tests.test_substitution_control_695 tests.test_stopped_edit_663 tests.test_live_player_records_682 tests.test_original_match.ScreenDriverTests -v
tools/heavy.sh fix695-repeat-original -- .cache/venv/bin/python -B experiments/E036-match-port/out/fix695/proof-v2.py --engine original --case request --out /tmp/fix695-original-repeat-request.json
tools/heavy.sh fix695-repeat-port -- /home/diego/.local/bin/pypy3.11 -B experiments/E036-match-port/out/fix695/proof-v2.py --engine port --case request --out /tmp/fix695-port-repeat-request.json
python3 experiments/E036-match-port/out/fix695/verify-v1.py --private
python3 experiments/E036-match-port/out/fix695/compare-v2.py --out /tmp/fix695-independent-comparison.json
```

Other fixed recipes use `--case cancel`, `zero`, `dismiss`, `timeout`; checkpoint
request adds `--checkpoint`. The paired live snapshot profile uses composite-v1.py
with the same request selector. The legacy reference archive is recreated with
`git archive4fe3a973:runtime` semantics (ordinary exported files, no checkout or
worktree); legacy-v1.py's --runtime takes that runtime folder. The prepared frame
producer capture-frame-v1.py writes original bytes only under the ignored path;
shared-frame-v1.py consumes its receipt in a bounded fresh-machine ABIcontrol.
No benchmark/season, natural keeper injury, active-parent resume or generalized
frame API is claimed by that supplementary harness.
