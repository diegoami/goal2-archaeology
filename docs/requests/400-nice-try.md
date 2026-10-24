# Original-key E022 / E19F “Nice try” input (#400)

T88's supplemental bounded replay supplies the **actual E19F warning**, alongside the
[corner/CF3A delivery](400-remaining-inputs.md). This uses the closer genuine T114 input
identified in [the newer #400 comment](https://github.com/diegoami/goal2-archaeology/issues/400#issuecomment-6383885926).
The raw attempt was committed at `d86a132f` before this interpretation. No goal2 code was edited.

## Inputs and private provenance

The [same private delivery folder](https://drive.google.com/drive/folders/1a9afcTH1f_tFDgJ1OOgbH7Bzfy_gea0h)
holds these files. Full locations/readback paths and frame fields are also in
[delivery.json](../../notes/400-remaining/delivery.json), under `nice_try`.

| Input | Full SHA-256 | Meaning |
| --- | --- | --- |
| `t88-eeea2f27f96f4812-before-nice-try.g2core` | `eeea2f27f96f481248f2fb2377990e7923f6b2fc7e80422ef8d6e5ddcfb20e8f` | Genuine original state immediately before the second Enter. |
| `t88-feb8fa6edbdbc5b6-nice-try-actual-read.ucstate` | `feb8fa6edbdbc5b6663f49d88303421903216ae98a5e2f60d730864e0edad401` | Actual stopped original machine at the warning's key read. |
| `t88-ee0c00a59111bc8d-E19F-private-attempt.zip` | `ee0c00a59111bc8d732532be1bcb89ff4a8d455494b1824eb800b64d70f26a10` | All 17 raw observations, intermediate core/machine inputs, unchanged runtime source and original T114 provenance records. |

Preceding source: `g13-fc5b0f392a66334c-stoppage-positions.g2core`, SHA-256
`fc5b0f392a66334c3395605d0113d56f67788c7b4a7b4b176364fb028ce119e2`, already at
`goal2drive:g13-fc5b0f392a66334c-stoppage-positions.g2core` and copied unchanged into the new private
package. Its existing provenance is goal2 `docs/evidence/T114/artifacts.json` and the private
`goal2-keep/G13-eleven-preflight-20261023/index.json`: T108's genuine stoppage, original Enter and
ordinary R/C position controls. Original source producer pin: `be991542f0d70bfc919770cb17ab7c892d862e58`.
The new replay does not reconstruct that source or change the sent-off flag.

The **replay runtime** is separately pinned to goal2 commit
`5061474420b842ee98a4a1e4c9c2673c0764b1f2`, copied through `git archive` into this research
worktree's private cache. It was not imported from a mutable active checkout. Collector
commit `26cc7ca466203e1eb5852905afa5ccc518780718`, SHA-256
`bcc878b5c8eae9d3ec44d2568bf3acbe32827e773998316ce839662318de77bc`, and the core module
hashes were recorded before replay in `core-r1/source.json`. Runtime settings, CPU and key history
are inherited unchanged by `Core.load`; no date, seed, fixture, instruction budget or guest
state setting was changed. The collector uses only normal `Core.load/press/save` and read-only
observations. Keyboard answers use that unchanged runtime's ordinary keyboard service.
The supplemental [runtime readback](../../notes/400-remaining/core-runtime-readback.json)
records the interpreter/Unicorn versions and the actual inherited budget, date/time and seeds;
it is explicitly distinguished from the immutable pre-attempt source record.

## Original keys and caller proof

Cost H/S: 120-second bound, **1.139 s actual**, 15 keys, no match/campaign run.
From the original T114 match menu:

1. **Space** opens the managed squad.
2. **Home**, **Down ×10** highlights squad slot 11, sent-off player **125** (status **0x20**).
3. **Enter** marks him as the outgoing player.
4. **Down** highlights available bench slot 12, player **132** (status **0**, energy **1**).
   Step 16 keeps the complete preceding `.g2core` input at original read **0791:E61F**.
5. **Enter** reaches the original **“Nice try  PRESS ANY KEY”** message. No synthetic incident
   or unavailable incoming player is involved. The original squad and remaining-substitution
   counters are unchanged by the refusal.

At step 17 the actual CPU is **214B:08DD**, immediately before the normal original key read;
the top of its saved stack returns **214B:098A**. Live parent frames return
**214B:054E → 214B:1793 → 0791:E19F**. The E022 frame next returns near to **E693**;
its static link points to E44F. The managed country is **7 (Denmark)**, cursor slot **12**,
minute **43**, substitutions left **2/2**, and the eleven is retained in the manifest. These fields are read from the actual machine,
not inferred from the screen or a stale stack scan. No taker role is claimed by this warning.

The unchanged runtime raises **UnknownScreen** for this genuine warning. Thus `core-r1/record.json`
honestly retains `status: aborted` and the original exception. It is a **successful evidence capture
at an unsupported original wait**, not a successful core/UI recovery. No raw record was rewritten
to hide that stop. The after-state is explicitly a `.ucstate` ZIP containing actual `memory.bin`
and `registers.json` (`load` plus CPU registers); it is **not** relabelled as a `.g2core` or native
DOSBox save. The preceding `.g2core` is the direct consumer reproduction input.

## Reproduce and verify

Fetch the private folder and extract both attempt packages as described in the corner delivery,
then run `python3 notes/400-remaining/verify.py`. It performs read-only checks on all native and
core records, original frame chains, source pins, input hashes and actual Drive readback bytes.
The runtime source needed for this replay is retained in the E19F package.

Using that unchanged pinned core:

```python
from pathlib import Path
from goal2.core import Core
core = Core.load(Path("t88-eeea2f27f96f4812-before-nice-try.g2core").read_bytes())
core.press(13)  # original Enter; raises UnknownScreen with the actual original Nice try message
```

The private raw machine capture can also be inspected or restored exactly through the existing
Unicorn `Machine` snapshot interface (`memory`, `regs`, `load`). Do not move its CPU to a routine
entry or manufacture a new status bit. Consumer recovery/desktop implementation belongs to goal2.

Upload and readback must match the full hashes above. The parent #400 remains open for
roles **3/4/5**, **E062 “no player”**, and **EC60 vacancy**; this new evidence replaces only the
earlier collection limit for **E19F**. Findings F029/F030 keep their existing status.
