# E019 Q017 events-morale README

- **Task**: T33 (#107)
- **Question**: Q017 (Q05.7–Q05.9), do injuries, cards and friendlies change confidence, and how does team morale follow.
- **Hypothesis**: a booked or injured player loses confidence; team morale moves with the mean confidence. Static route: as Q016 (the writers outside F019's result rule, at `DS:7CC5` and at the foul dispatch `7EEF`; the team aggregate `DS:9B5A` computed by `1771:13D0`; the watched save/restore `9B07[side*20+slot]`).
- **Artifact**: `goal2-a949da2f` (the same set F019 used; shared raw inspection).
- **Max intervention**: I1 (the E017/E018 read-style probes; a Unicorn harness emulating one original routine at a time).
- **Confidence**: static-derived; arithmetic checked against original guest code on one or two cases per routine.

## Method

Static first (U32, CLAUDE.md rule 22). Read the named view `static/goal-exe/named/` first: `seg_0791_05.c` (record_goal 6443, after_goal 65FE), `seg_0791_06.c` (the foul dispatch 7EEF, the booking 798D, the sending-off 7B77, the injury 7D56, the live-form helper 7CC5), `seg_0791_09.c` (B7FA result-updater already covered by F019), `seg_1771_01.c` (`1771:13D0` the team-aggregate routine). Cross-checked against the raw `decompiled/` output and the capstone `code/` listing, where Ghidra's set-membership and signed arithmetic are misleading.

The complete direct player `+0xC` reader/writer inventory (the F019 set + the event writers this task adds) is in `notes.md`. The whole-picture claim: outside F019's result rule, `7CC5` is the only direct player `+0xC` writer and `DS:9B5A` is the only team-aggregate the listing stores.

`runtime/model/morale.py` extends F019 with three event types and the team aggregate:
- `injure`, `book`, `send_off`: write `+0xC := clamp(s8(+0xC) + delta, 1, 255)` and, when the writer's flag is non-zero, `DS:9B07[side*20+slot] := min(32, s8(new))`. Each is a named, clamped delta — not a fixed-constant substitution.
- `team_panel_morale`: `DS:9B5A = (6 + Σ_i min(32, max(0, s8(+0xC[i]))) for i in 1..11) // 11`, with `+0xC[i]` the i-th available starter's signed byte (a player is `available` when `1771:3216` returns 0 — energy > 0, and `+0x10` bits 8, 6, 3 clear). This is **transient**: it is recomputed every time the panel renders, by `1771:13D0`, and never persisted into the country record. There is no other team-morale byte.
- `event_clamp(byte, delta, persist)`: the `7CC5` operation on a single player byte.

`experiments/E019-q017-events-morale/check_morale.py` replays every probe by player word and exits non-zero on empty.

Corroboration: original-routine Unicorn probes for `7CC5` (one routine call, six event inputs) and `1771:13D0` (one routine call, eight aggregate inputs); no DOSBox run was needed for the listing-derived claims.

## Records

Probes (none kept incomplete; nothing superseded):

| Probe | Cases | Routines exercised |
| --- | --- | --- |
| `adjust-player-form-probe-001.json` | 6 | `0791:7CC5` with the named event deltas and one boundary per clamp |
| `team-morale-probe-001.json` | 8 | `1771:13D0` over the 11 available starters, including the 0/32 and `+0xC = 128` edges |

## Scripts

```
python3 experiments/E019-q017-events-morale/check_morale.py
python3 -m unittest -v tests.test_model_morale
python3 tools/static/check_annotations.py
python3 -m unittest discover -s tests
python3 -m unittest discover -s tests/static
python3 tools/check_links.py
```