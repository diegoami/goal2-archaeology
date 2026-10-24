# Bounded penalty/free-kick search and evidence limit (#400, T90)

**No new role3/4 or E062/EC60 input is delivered by this collection.** The four cases
remain unavailable and [#400](https://github.com/diegoami/goal2-archaeology/issues/400)
stays open. T88's corner/CF3A/E19F and T89's goal-kick/CF3A inputs remain unchanged.
This report records the complete bounded negative result, not coverage for an unvisited role.
It introduces no new game-rule finding or evidence-level promotion.

## Complete private records and verification

The owner's [private T90 folder](https://drive.google.com/drive/folders/1F1Snos-EHzAHsorAU-3tnaWMCd5rCqgI)
is `goal2drive:goal2-archaeology/400-penalty-free-kick-20261024/`.
[delivery.json](../../notes/400-last/delivery.json) lists every package's full SHA-256,
private path, size and readback location. Original files, machine states and frozen replay
runtime source are retained privately; no original-byte payload enters Git or a public release.

```sh
rclone copy goal2drive:goal2-archaeology/400-penalty-free-kick-20261024 .cache/400-last/readback
unzip -n .cache/400-last/readback/t90-first-probes-private.zip -d .
unzip -n .cache/400-last/readback/t90-more-probes-private.zip -d .
unzip -n .cache/400-last/readback/t90-final-probes-private.zip -d .
unzip -n .cache/400-last/readback/t90-multiplayer-search-private.zip -d .
python3 notes/400-last/verify.py
```

The verifier is read-only: it executes no guest. It checks the source and collector pins,
all942 observations' saved-state bytes, native loader/key records, ordinary squad/position
changes, watched-mode flags, replay inputs, existing-source searches, and actual private
download hashes. The recipe requires no archive copy at a collector-only local path.

## Source choice, bounds and original keys

Static-first reading used F026/F027/F030 and named CC7B, 4DA9, 6ECF, 6F3E, E022,
EA09, DEA6 and the original position editor4952, then their original listings. Role3 is
the managed penalty selector through 6D4E/6EEF; role4 is the shooting-range free-kick
selector through 6D4E/6F92. Ordinary free kicks, shootout order and goal-kick-style restarts
do not establish those roles. No CPU was placed at either routine to manufacture a case.

All native source files are the existing original E031 saves in the merged T84 inventory.
Each source was hash-verified before launch and loaded by the original DOS loader on
worktree-local drives. Every collector was committed/hashed and archived before execution;
all raw attempts remain unchanged and were committed before this delivery analysis.
Operational status and cost updates were posted as collection progressed.

| Native attempt | Selected existing source and actual original decisions | Active collector time / observations |
| --- | --- | --- |
| G1D-r1 | Next Holland–Luxembourg qualifier; existing eleven. | 85.471s /127 |
| G4B-r1 | Next World Cup group fixture against Germany; existing eleven. | 78.664s /114 |
| G3C-r1 | Existing4-3-3 before Belgium; original squad keys replace injured395 with2612 and exhausted2748 with2614. Both swaps retain the same20-player multiset. | 117.578s /172 |
| G1A-r1 | Existing first friendly against Eire; two original R keys move Gullit390 from position11 to13. No direct position write. | 78.897s /114 |
| G2B-r1 | Existing3-5-2 and soft centre-forward against Yugoslavia; no squad changes. | 67.640s /95 |
| G3A-r1 | Existing next friendly against Italy, selected from the recorded defender hardness fields. | 71.949s /103 |
| G1C-r1 | Existing next friendly against Albania, selected from the recorded defender hardness fields. | 84.347s /123 |

Each native attempt had a **240-second/first-managed-fixture bound** and stopped at full time
without retaining a target. No subsequent round or multi-year campaign was played.
All native ending states retain watched-mode flags9A3E/9A3F equal0; this was not a quick-engine
search that silently bypassed managed taker selection. Already supplied corner/goal-kick
choices were accepted with original Enter, not advertised as new evidence.

Runtime: DOSBox-X2024.03.01, private Xvfb, raw XTEST keys/nohost mapper,
`cycles=fixed 8000`, `machine=svga_s3`, `memsize=16`, `core=auto`, `cputype=auto`.
DOS date/time10/24/2026 12:00:00 was explicit (readback11:59:59); every key/timing and
actual CPU observation is retained. Original Right keys change speed and Insert disables
replays when needed. No guest field, fixture, RNG seed or routine entry was edited by the collector.

G3C waited1227s for a shared heavy slot before its bounded execution. Waiting time is separate
from the active collection figures above. No other job or active checkout was altered.

## Read-only source searches and hypothesis limits

- [record-search-r1.json](../../notes/400-last/record-search-r1.json) checks477 existing
  decoded run records for a managed `select PENALTY/FREE KICK taker` caption: no match.
  This is a text search, not proof that every old savestate was retained or every prompt recorded.
- [source-assessment-r1.json](../../notes/400-last/source-assessment-r1.json) records the17
  original saves' pending fixtures, positions and injured starters, with source hashes.
- [foul-gate-assessment-r1.json](../../notes/400-last/foul-gate-assessment-r1.json) reads
  intrinsic hardness and saved tactic fields for14 next-fixture sources. F027's4DA9 gate
  motivates harder challengers/softer holders as a hypothesis. No RNG value was selected,
  simulated, swept or edited, and no incident probability was claimed from these fields.
- Saved lineups are only hypotheses: original computer setup can select another keeper.
  [observed-starting-keepers-r1.json](../../notes/400-last/observed-starting-keepers-r1.json)
  reads the actual native captain states after setup. For example, G1A's saved keeper has
  hardness16, but the actual starting keeper152 has15. The actual machine fields are authoritative.
- [retained-target-scan-r1.json](../../notes/400-last/retained-target-scan-r1.json) independently
  inspects all848 native snapshots' captions and stack bytes for a missed role3/4 candidate,
  including the6D74 parent/6EEF-or6F92 origin combination: no candidate. This bounds retained
  data; it does not claim an event could never occur between observations.
- [multiplayer-save-search-r1.json](../../notes/400-last/multiplayer-save-search-r1.json)
  found no multi-manager candidate among five distinct original-sized files in the existing
  cache/scratch/keep search. Those are search candidates, not newly certified genuine play inputs.

## Exact-CPU replay research method

To reduce collection cost, a research collector used the existing frozen goal2 Core keyboard
services from commit5061474420b842ee98a4a1e4c9c2673c0764b1f2. **No goal2 source file was edited.**
Runtime file fingerprints and collector source/hash precede each attempt. This is a collector
method, not a desktop/core recovery implementation or a proposed re-vendor.

uc-r1 imports the genuine native G1A-r1 step34 captain state, SHA-256
`6731809257089157904884a54148f6f71b87a3073aaa9d433479744ba8844915`, at its actual
saved **214B:1E3E** CPU. It does not call `Core.start/boot`, unwind BIOS frames, reconstruct
registers or move the CPU to an entry point. Before any guest instruction, every CPU register
and all non-video memory are asserted equal to the saved state. The native Vga component's own
4000 text-page bytes are mapped into physical video RAM, as part of loading the original
hardware state; no player, country, fixture or RNG field is altered. Forward original execution
naturally reaches the captain poll at **0791:CC54**.

The host labels already-evidenced roles2/5 as `evidence-taker` so existing Core key services can
accept original Enter there. The label adapter changes no guest bytes or game routines, and
does **not** recognize new roles3/4. A new target would stop at its actual unsupported original
poll. The verifier reads the actual role/caller bytes of every alias-labelled observation and
requires role2 or5; a host label alone is not treated as evidence.

uc-r1 uses original pause/squad/R keys to move Gullit390 from13 to8, aiming for the forward
dribbling branch of F026. Position8 is right midfield in this game; it is not mislabelled as a
central-midfield state. Opening his original T-tactics dialog reaches an unsupported host
classification at214B:157C. The abort, exact memory/register capture and all48 observations
are retained unchanged (3.519s). No goal2 dialog recovery was implemented to hide it.

The preceding **before-T** genuine core input at uc-r1 step46 has SHA-256
`068a47729a3b1822ae6d3df7777eb99880bbcf74315e22098869ccaeac29ad28`.
uc-r2 loads it with identical CPU/memory and uses ordinary **Escape**, **End**, **Enter**
instead of opening T. A zero-instruction preflight shows existing effective push-forward is on
and quick-pass is off (keep ball), so no tactic edit was needed. Original keys resume the same
fixture and select fastest speed. It reaches the original full-time announcement at minute92
in **29.531s**, with **46 observations /4637 complete live-frame advances**, and no target.
All original keys and the implicit no-key advances are reproducible from the pinned collector.

uc-r2 waited2037s for a shared slot. The four-slot queue freed before the owner's narrowly
scoped extra-slot approval arrived; **no extra slot was used**. Both replay inputs, actual raw
`.ucstate` snapshots, core saves and the unchanged runtime source are private in the archives.
Raw snapshots are not relabelled as native DOSBox saves.

## Four unavailable cases and next evidence needed

| Case | Exact current limit / cheaper existing assumption |
| --- | --- |
| CC7B role3 penalty | No retained managed penalty selector in these seven native fixtures or the same-fixture replay. Shootout ordering is a different route. Keep F030's conditional role3 contract static-only. |
| CC7B role4 free kick | No retained shooting-range selector. An ordinary free-kick count is insufficient. Keep F030's conditional role4 contract static-only. |
| E022/E062 no player | T89's17-save/12-core-input inventory had no empty managed slot. The reviewed initialization/swap/retirement paths provide no cheap source of one from those full inputs. Keep the conditional caller contract. |
| EA09/EC60 vacancy | No actual vacancy input while earlier eleven checks pass. The scoped [vacancy-path reading](../../notes/400-last/vacancy-path-reading.md) is not an exhaustive reachability proof. No zero entry is manufactured. Keep the conditional caller contract. |

This collection limit does not justify removing a handler or claiming the four waits cannot
occur. Further progress needs a genuinely closer before-foul/vacancy input or another explicitly
graded controlled trial. No rolling fixture/seed sweep or fresh campaign is started here.
The private negative inputs are not advertised as new taker/warning coverage or manager-only
completion. **#400 remains open.** T88/T89's actual supplied inputs remain the positive evidence;
extra-time, injury recovery and all desktop implementation stay with goal2.

The §14 consumer issue is linked on PR414/#400 before merge. Its docs-only register/handover
branch follows upstream merge so rows cite merged evidence; goal2 reviews/merges that branch.
