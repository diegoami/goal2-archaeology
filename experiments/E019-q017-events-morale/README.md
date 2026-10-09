# E019 Q017 events-morale README

- **Task**: T33 (#107)
- **Question**: Q017 (Q05.7–Q05.9), do injuries, cards and friendlies
  change confidence, and how does team morale follow.
- **Hypothesis**: a booked or injured player loses confidence; team
  morale moves with the mean confidence. Static route: as Q016 (the
  writers outside F019's result rule, at `DS:7CC5` and at the foul
  dispatch `7EEF`; the team aggregate `DS:9B5A` computed by
  `1771:13D0`; the watched save/restore `9B07[side*20+slot]`).
- **Artifact**: `goal2-a949da2f` (the same set F019 used; shared raw
  inspection).
- **Max intervention**: I1 (the E017/E018 read-style probes; a
  Unicorn harness emulating one original routine at a time).
- **Confidence**: static-derived; arithmetic checked against original
  guest code by hand from the listing bytes (R1's reproduction
  `[128, 0, ..., 0]` returns 5946, matching the reviewer's Unicorn
  run of the original listing bytes).

## Method

Static first (U32, CLAUDE.md rule 22). Read the named view
`static/goal-exe/named/` first: `seg_0791_05.c` (record_goal 6443,
after_goal 65FE), `seg_0791_06.c` (the foul dispatch 7EEF, the
booking 798D, the sending-off 7B77, the injury 7D56, the live-form
helper 7CC5, the table-draw 261A), `seg_0791_09.c` (B7FA
result-updater already covered by F019), `seg_1771_01.c`
(`1771:13D0` the team-aggregate routine) and `seg_1771_02.c`
(157D draw_team_panel, the only reader of `DS:9B5A`).
Cross-checked against the raw `decompiled/` output and the capstone
`code/` listing, where Ghidra's set-membership and signed
arithmetic are misleading.

The complete direct player `+0xC` reader/writer inventory (F019's
result rule + this task's event writers) is in `notes.md`. The
whole-picture claim: outside F019's result rule, `7CC5` is the only
direct player `+0xC` writer and `DS:9B5A` is the only team
aggregate the listing stores. The foul dispatch's `0791:261A` is
a 255-element pre-shuffled draw table, **not** a tick counter (R5).

`runtime/model/morale.py` extends F019 with the event types and the
team aggregate:

- `event_clamp(before, delta, persist)` — the `7CC5` operation on a
  single player byte: writes `clamp(s8(before) + delta, 1, 255)` to
  the player and, when `persist` is True, also writes
  `min(32, s8(new)) & 0xFF` to `DS:9B07[side*20+slot]`. Each named
  helper (`injure`, `send_off`, `scorer`, `team_reaction`) is a
  fixed pair of `delta, persist`.
- `injure(before)`, `send_off(before)` — `delta=-2, persist=True`.
- `scorer(before, morale_delta)`, `team_reaction(before,
  morale_delta)` — `delta=morale_delta`, `persist=True/False`
  respectively.
- `team_panel_morale(morales)` — `max(1, ((6 + Σ_i min(32,
  s8(+0xC[i])) for the 11 available starters) & 0xFFFF) // 11)`,
  with each starter's contribution clamped only to `min(32, s8(...))`
  (no lower clamp — a -128 player byte contributes -128). The
  accumulator wraps mod 0x10000 on each add (matching the `add
  word ptr [0x9B5A], ax` at `code/seg_1771_02.asm:1067`); the
  divide-by-11 is the 16-bit unsigned divide (`div cx` at line
  1093). The aggregate is recomputed at every panel render by
  `1771:13D0` and never persisted into the country record.

`experiments/E019-q017-events-morale/check_morale.py` replays every
probe by player word; the checker compares the model's output to
both the listing-derived `expected_*` and `got_*` per case, and
rejects mismatches, missing fields, and records that lack a
`player_word` (R1, R2, R3). The probe generator
(`probe_literal.py`) does NOT import `runtime.model.morale`; both
`expected_*` and `got_*` are listing-derived (hand-traced from
`code/seg_0791_13.asm:484..548` and
`code/seg_1771_02.asm:1001..1126`). Every case carries a
`player_word` (single 16-bit int for adjust) or `player_words`
(list of 11 16-bit ints for panel). `python3 -m unittest -v
tests.test_model_morale` runs 33 literal tests;
`tests.test_check_morale` runs 19 negative tests. The mutation
sweep (`mutations_morale.py`) shifts each of the 9 numeric
constants by `+1` and `-1`, deletes each of the 5 named helpers,
and reruns the unit suite in a fresh subprocess; **23/23 mutants
killed**.

## Records

Probes (none kept incomplete; nothing superseded):

| Probe | Cases | Routines exercised |
| --- | --- | --- |
| `probe-literal-001.json` | 22 | `0791:7CC5` with the named event deltas (13 cases) and `1771:13D0` over the 11 available starters (9 cases), including the 0/32 and `+0xC = 128` signed-byte edges; every `expected_*` is hand-traced from the listing (R4) |

The brief's 6-run budget is **not spent** on DOSBox matches here:
the listing settles every claim this task asks for. The Unicorn
harness (`probe_adjust_form.py`) remains as a diagnostic for a
reviewer who can wire in a savestate asset; it does not produce
retained comparisons because Unicorn 2.1.4 trips on a later routine
call inside the engine, and the listing-only probe covers the
arithmetic byte for byte.

## Scripts

```
python3 experiments/E019-q017-events-morale/check_morale.py
python3 -m unittest -v tests.test_model_morale
python3 -m unittest -v tests.test_check_morale
python3 experiments/E019-q017-events-morale/mutations_morale.py
python3 tools/static/check_annotations.py
python3 -m unittest discover -s tests
python3 -m unittest discover -s tests/static
python3 tools/check_links.py
```
