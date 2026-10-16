# E034 the original-match kit for competitive fixtures: notes and provenance

Made for issue 252 (extend the kit of issue 250, PR 251, to competitive fixtures: extra time, the penalty
shoot-out, the substitution budget, the post-match consequences). No DOSBox-X run was made: every match is the
original's own code under Unicorn (Python 3.12, Unicorn 2.1.4), from images fetched by SHA-256 (E006-r0001, the
kit's reference; E031's shoot-out state `3ea57029...`, release play-the-game-states). Nothing of the original is in
the tree. Every writer refuses an existing output; nothing in `out/` is deleted or overwritten.

## 1. Static first: what a competitive fixture runs (named view, listing)

- **play_match `0791:F098`** (named `seg_0791_12.c`): after the 90 minutes it stores the score in the fixture's
  word +0 and the result byte +3 (2 level, else whether team 1 won). If `DS:7C36` (the fixture's kind in the decider
  set `DS:693A` = {4, 8..203}, F023 section 9) and level: `9B0C` and `9B5B` (extra time's halves), the score stored
  again, and, still level, `penalty_shootout A10A`, after which +3 := whether team 1 is ahead in the score bytes.
- **Extra time** (`seg_0791_16.asm:440-492`): `9B0C` writes `DS:831B := 0x1F`, `DS:831F := 0x59` (the minute, 89, at
  `9B15`), `DS:8326 := 0`, `DS:8319 := 0x0F`, `DS:831D := 0`, calls `2B0F(0x3E)`, sets `DS:9B41 = 1` and, with a
  human side (`DS:80FD`), the team menu `ED8A` (returns to `9B42`), then a half (`983F`). `9B5B` does the same menu
  (returns to `9B70`) and half without touching the clock. Both menus were already in the kit's table as context
  `extra_time`; the kit now tells them apart (`half` 1 or 2).
- **The shoot-out** (`seg_0791_08.c`, listing `seg_0791_16.asm`): `A10A` saves the speed byte, `0C0B` raises it,
  `2929` clears the pitch records' state bytes, "penalty shoot out" waits a key (`214B:04F8` at `A132`, the kit's
  message read), each side's takers: `9B93` by hand for a managed side (the screen of E031's C48b: Up/Down over the
  eleven, Enter adds the highlighted one, Esc undoes; its `214B:1560` read at `9D62`; it skips the ones taken and
  the unavailable, `1771:3216`; it needs as many picks as there are available players, `[bp-4]`; after each pick it
  pushes a Down key back, `9E5B`), `9ED3` for a computer side (slots 1..11 sorted by `278A(pitch, 0xC)`, the derived
  penalty skill). Then kicks alternate from `DS:831A`'s side: `A006` kicks entry `[bp-0x1E+side]` of the side's
  takers (`[bp-0x1A+12 side]`, pitch slots), then steps the index 1..11 past entries that cannot play; five a side,
  then one more each while level (sudden death). A kick goes through the watched engine `9564`; a goal is the same
  score write as in play (`685C`), so the score bytes count the kicks too; `record_goal` is not called for them
  (the original's goal count `DS:80F0` stays at the match's goals: measured, every shoot-out run).
- **After a non-friendly** run_match calls `E929` (kind != 1), which calls `1771:958D(country, DS:9976, 0)`: one pass
  of the competition's table screen, reading one key at `1771:9022` (8E9A), `91BE` (9028) or `9567` (9509, the
  finals' tree with "hit any key", reached from E031's World Cup state). The kit answers each with Enter, only once
  the match is played.
- **The budget** (F027 section 4): `A4A1` writes `DS:9B3A[side] := DS:066B[kind != 1]` = 5 or 2; `C5DC` counts it
  down and (C5F6-C612) sets element 3 (substituted off) on the slot's player.
- Not in run_match: "Do you want to watch this match?" (route_fixture, `000E:...`, F030: for fixtures goal2's manager
  does not play), the news pages and the sack check `4E0E` (F025).

## 2. What the kit does now (the interface additions)

`runtime/original_match/` (kit version 2: a saved match of version 1 is refused):
- `Fixture(kind=...)` accepts the kinds the builders write (`KINDS`: 1, 2, 3, 5, 6, 7, 8, 101-103, 200-203); others,
  4 included, are refused.
- `Match(..., substitutions=n | (n0, n1))`: the budget written over the set-up's when play_match starts (a declared
  input); `result()["substitution_budget"]` says what the match had.
- Events `extra_time` (at the `9B15` write, stamped with 89 and the score), `shootout` (A10A's entry; `score_120`),
  `shootout_kick` (team, player, name, scored, round, `shootout_score`; a goal at its score write, a miss at A006's
  return `A1EF`).
- Decisions `extra_time` with `half`, and `shootout_order` (`available`, `takers`); `answer(shootout_order=[...])`
  drives 9B93 closed-loop (the highlight `[bp-6]` read at each key read); no answer is the original's Enter result.
  `pause()` is refused in the shoot-out.
- `result()`: `kind`, `winner` (the fixture's +3 after play_match), `score_90`, `extra_time`, `shootout`
  ({score, kicks} or None), `score` = the 120 minutes' (the board's bytes hold the kicks too), result entries made in
  extra time carry `extra_time: True`, `players` (per player of both squads: confidence +0xC, energy +0xE, status
  +0x10 before and after, `suspended`, `carried_booking`, `injured`).
- The full-time board's event now comes at the board even when a pushed-back key passes its wait (after a
  shoot-out: 9B93's last Down). Before, `full_time` was missing after a shoot-out (probe c, seed 2).
- `example.py --competitive` (`play_knockout`), `check.py` step `knockout`, `fresh_state` (the kit's state of a new
  match, also used by `e031_shootout.py`).

## 3. The checks

- **Against an independently obtained run: E031's shoot-out** (`e031_shootout.py`). E031's DOSBox-X state at the
  start of its last-16 shoot-out (Holland v Belgium, 2-2; kind 8) has the CPU in the BIOS key wait under A10A's
  message; the script finds A10A's frame and run_match's on the stack (their return addresses), puts the CPU at A10A's
  entry with A10A's own return address (0C0B and 2929 run again: the speed byte A10A saves and restores, and the state
  bytes 2929 clears; neither is read by a kick), answers the order E031 picked (read from its order screen, step
  3932, through the kit's `shootout_order`) and lets the kit run the original's chain to route_fixture. E031's
  commentary panel over steps 3933 to the next fixture: 30 lines; all are, in order, in the kit's 31; the takers
  (8, from "X to shoot" and "shot from X") and the goals (4) are the kit's; the kit has Holland through 3-1 (E031's
  README: "last 16 won on penalties after 2-2").
  `out/e031-shootout-20261016a.json` (PASS); the final run `-20261016b`.
- **The engine on competitive fixtures, by the kit's own check** (`check.py` `knockout`): the knockout example
  straight, resumed at extra time's first decision and resumed at the order: one digest, recorded as
  `EXPECTED_KNOCKOUT`; `goal_problems` (now counting kicks in the score bytes and checking the shoot-out's score
  against its kicks and the board) holds; decided on penalties, winner the side ahead.
- **Stamps by independent hooks** (`stamps_competitive.py`, on E033's `Independent`): 8 scenarios (the knockout
  example; kind 200 at 42 watched, sudden death; at 30, decided in extra time; at 9 and 53 as quick results; at 42
  quick with goal2 managing 19; a qualifier; the friendly), every kind's stamps and the whole stream equal
  (`stamps-competitive-20261016a.jsonl`: the first 7, PASS; the final run `-20261016b`: 8).
- **Save boundaries** (`save_boundaries_competitive.py`): three scenarios, every first event of each kind
  (`extra_time`, `shootout`, `shootout_kick` included), every decision before and after its answer:
  resumed = straight (`save-boundaries-competitive-20261016a.jsonl`, PASS; final `-20261016b`).
- **Tests**: `CompetitiveTests`, 8 tests (kinds and budget arguments; penalties after extra time; goal2's order and
  the takers' rotation past a side's tenth taker after a sending off; the budget per side, 5 made and none for a
  side given 0; an extra-time goal marked; the stream against E034's hooks; a ban after a sending off; a
  qualifier). Against origin/main's kit every one errors (`base-tests-20261016b.txt`: "only friendlies" or no
  `substitutions` argument). 16 new mutation entries (`tests/mutations_original_match.py`), each killed by the test
  named with it (`mutations-20261016b.txt`). `out/tests-20261016a.txt` (30 OK) is from f116f62's parent's tests;
  `mutations-20261016a.txt` is empty: I stopped that run before its first line to add two tests.
- **Probes** (`probe_kinds.py`): a (kind 200, 6 seeds: the first two undeclared things, the competition table read
  1771:9022 and the extra-time minute write 9B15), b and c (after the first changes; c found the missing full-time
  board), d (31 indexes, every decision played on: all complete; 10 to extra time, 3 to penalties), e (80 indexes,
  quick from half time: all complete, 19 shoot-outs, up to 24 kicks), f (every competitive kind at index 9, quick:
  all complete), g and h (goal2 managing 19: 22 complete, 2 shoot-outs). In logs a-c the field `score_90` is the
  full-time board's score (named before the kit's field); from d it is the kit's.
- `find_knockout.py`: the index for the worked example (its answers fixed; a is empty: the first try stopped on
  the example's own bug, it read `minute` from the decision's data; b: 39, 44 and 51 go to penalties, 39 chosen).

## 4. The worked example

`python3 -m original_match.example --competitive` (about 18 s): Denmark v country 19, a World Cup knockout match
(kind 200, calendar number 39), goal2's budget 5 a side. Half time: play on. Before extra time (89'): Jensen,
Laudrup and Povlsen off for Nielsen, Nielsen and Frank, and "stand ground". Extra time's half time: play on. The
original takes back a goal of Frank's at 121'. 0-0 after 120 minutes; the shoot-out order is the available eleven
reversed (Frank first, the keeper last); the match is saved at the order (340 KB) and resumed; Denmark win 3-1
on penalties (Frank, Larsen in; Vilfort out; Sivebaek in; country 19 scored one of four). The result's `players`
show the post-match update (the first five of Denmark's: confidence down 2, energy up or unchanged).

## 5. Findings worth knowing for goal2

- **The kind changes the match, not only its end**: the same fixture index as a quick result gives 1-2 for kinds 2,
  5 and 6 and 1-1 for kinds 3, 7 and every decider (probe f): kinds in `DS:0F3E` = {3, 4, 7, 8..203} (F019) play
  differently from the rest before any extra time. goal2 must pass the fixture's real kind.
- **The budget is both sides'**: with 5 a side the computer side substituted up to 5 times (find-knockout b) and the
  90 minutes changed from the same index (index 60 went from a shoot-out to 2-1). Giving the computer 0 stops its
  substitutions. goal2's rule is its choice; the kit applies it per side.
- **Who manages changes the match**: index 9 quick is 1-1 with goal2 managing Denmark and 1-0 managing 19 (the
  computer picks for the other side).
- A sending off is a ban for the next fixture after B7FA (status 0x80), in a friendly too; energy after the update
  differs by kind (26 for kind 200, 15 for the friendly, the same player: B7FA's 3651/3558 split, F027 section 6).

## 6. What I could not do, and what it costs

- The sudden-death shoot-out E031 saw (third place v England, C49) has no savestate; only the last-16 one was kept,
  which ended within five kicks a side. The kit's sudden death is checked by its own runs (index 42 watched, 9 and 53
  quick) and the independent stamps, not against the original's screens.
- "Do you want to watch this match?", the news pages and the sack check are route_fixture's and not run (a fixture
  goal2's manager is not in is not supported at all: two computer sides would need the kit to drive no menus; about
  1 h). The set-piece taker prompts still keep the original's pick (about 1 h, unchanged).
- The 9B93 order screen's Esc (undo) is not used; an answer is a list.
- Time: the earlier estimate was about 2 h with E031's state; it took roughly 5 h (my estimate, not measured),
  mostly the checks (the independent stamps, the save boundaries, the E031 replay's stack walk); the kit's own code
  was about 1.5 h of it.
