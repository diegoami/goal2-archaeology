# F021 Energy (+0xE) and form (+0xC) set a player's strength in both match engines, fitness (+0xD) is read by no match arithmetic, and at equal skill the fit and confident side wins about three times as often as the tired and unconfident one

- **Status**: proposed
- **Question**: Q018 (Q05.10, T36): do fitness and confidence change match performance at equal skill, which routines read them in a match in each engine, with what arithmetic, and how large is the effect?
- **Tests claims**: Q018's hypothesis (at equal skills a fit, confident side wins more often); F012 (the quick engine's `377E`), F013 (the watched tick map), F015 (`278A`), F018 (fitness/energy), F019/F020 (confidence, team morale `DS:9B5A` is display only).
- **Experiment and runs**: E020, `experiments/E020-q018-condition-performance/`. No DOSBox-X run was taken and `runs/E020/` is empty: every behavioural comparison is the original binary executed in Unicorn on E010's half-time savestate (the release asset named in the records), as F018 did; the six E015 records hold only start-menu screens and zero squads, so no E015 comparison exists.
- **Artifact**: set `goal2-a949da2f`; packed GOAL.EXE SHA-256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`; the Unicorn image is E010-r0010's half-time savestate, SHA-256 `3c7983fa4869d3278fe9f1f6140e5ca1b84f602e97b5862f547c6332d086e1e6`.
- **Max intervention**: edits of guest memory (literal player records, pitch records, +0xC/+0xE of squads, `DS:80FC`, the main seed) before an emulated call or half; no change of guest code.
- **Tier reached**: V2 for the quick engine (model equal to the original on 585 literal-record comparisons and 32 whole halves); static plus 209 contest comparisons for the watched engine's `278A`; V0 for the watched engine's match-level effect.
- **Confidence**: unreviewed. The effect sizes are the model's, exact over its own draws (all 65,536 seeds of the second half from 0-0), not a measurement of the DOSBox-X game; the first half is not modelled.

## Answer

### Which routines read the three bytes in a match

- Fitness `+0xD` is read by no match arithmetic in either engine: the original `1771:377E` and `0791:278A` return one value while `+0xD` runs over 0, 1, 0x10, 0x20, 0x7F, 0x80 and 0xFF, and the other in-match reader is the team panel total. static:experiments/E020-q018-condition-performance/records/strength-002-fitness.json static:experiments/E020-q018-condition-performance/records/contest-003-fitness.json static:static/goal-exe/code/seg_1771_02.asm:1061
- Fitness reaches a match only as the energy it was copied to at the end of the previous one, `0791:CB7D` copying `+0xD` to `+0xE` when signed `+0xE` is positive. static:static/goal-exe/code/seg_0791_20.asm:1031
- The quick engine reads energy and form only through `1771:377E`, which `1771:0BC4` calls for each squad word at every `D733` minute, for both sides. static:static/goal-exe/code/seg_1771_02.asm:187 static:static/goal-exe/code/seg_0791_21.asm:831 static:static/goal-exe/code/seg_0791_21.asm:837
- `377E` is: strength 0 when the player is unavailable; otherwise `v = (+4) + s8(+0xE) - 0x3E`, then `v += s8(+0xC)` while the signed form is below 0x20 and `v -= v idiv 16` from 0x20 up, clamped to 0..0x100, halved when `3179` says the wrong foot. static:static/goal-exe/code/seg_1771_05.asm:785 static:static/goal-exe/code/seg_1771_05.asm:795 static:static/goal-exe/code/seg_1771_05.asm:805 static:static/goal-exe/code/seg_1771_05.asm:815
- The original `377E` equals the model on 193 literal records and a further 183 that vary position, foot byte, two-footedness, word mod 3, each `+0x10` bit and the clamp edges (strength 255, 256, 257 and 13-13, 13-14, 13-12 before the clamp). static:experiments/E020-q018-condition-performance/records/strength-001.json static:experiments/E020-q018-condition-performance/records/strength-003-structure.json
- The quick engine also reads energy in the five-minute energy loop (decrement when signed `+0xE > 1`), in the substitution gate (`+0xE > 0`) and the forced-removal guard (`+0xE < 1`), in the half-time `+2` step for `+0xE` in 1..30, and through `377E` in the computer's tactic comparison after a goal. static:static/goal-exe/code/seg_0791_21.asm:1181 static:static/goal-exe/code/seg_0791_13.asm:1019 static:static/goal-exe/code/seg_0791_20.asm:687 static:static/goal-exe/code/seg_0791_16.asm:370 static:static/goal-exe/code/seg_0791_19.asm:554
- In a non-friendly quick match the foul roll `D5C1` compares `278A(.,10)` of one side's player with `278A(.,3)` of the other's, the watched blend below; this path is not modelled. static:static/goal-exe/code/seg_0791_21.asm:712 static:static/goal-exe/code/seg_0791_21.asm:720
- The result of a fixture the owner does not play (`0791:D47E`) runs `0BC4` for both sides and `B19D(12)`, so `377E` decides those results as well; read from the listing only. static:static/goal-exe/code/seg_0791_21.asm:507 static:static/goal-exe/code/seg_0791_21.asm:514 static:static/goal-exe/code/seg_0791_21.asm:517
- The watched engine reads form and energy in every skill read, `0791:278A`: `base = (s8(+0xC) < 0x20 ? s8(+0xC) + 1 : 0) + (element >= 0xC ? 0x20 : s8(+0xE))`, `value = ((base * skill) mod 65536) div 256 + skill div 4`. static:static/goal-exe/code/seg_0791_04.asm:860 static:static/goal-exe/code/seg_0791_04.asm:874 static:static/goal-exe/code/seg_0791_04.asm:878 static:static/goal-exe/code/seg_0791_04.asm:902
- The original `278A` equals the model on 209 literal comparisons over elements 3, 10 and 12, energy 0..0xFE, form 0..0xFF, the halving flag, the keeper extra and the home share. static:experiments/E020-q018-condition-performance/records/contest-001.json static:experiments/E020-q018-condition-performance/records/contest-002-events.json static:experiments/E020-q018-condition-performance/records/contest-003-fitness.json
- The watched engine reads energy alone in three chance gates: `2B7B` (true with probability 1/(33 - E), used by `4A28`), `4A28` (a marking target is followed only if signed E exceeds a 1..6 draw) and `5049` (random-is-one of E idiv 2). static:static/goal-exe/code/seg_0791_05.asm:220 static:static/goal-exe/code/seg_0791_08.asm:561 static:static/goal-exe/code/seg_0791_09.asm:353
- The watched engine reaches `377E` only through `BD03`, the post-goal tactics comparison, and not through `0BC4`. static:experiments/E020-q018-condition-performance/reach-001.txt:98
- Team morale `DS:9B5A` reaches no match code: its only readers are the team panel `157D` (label index and bar) and its writer `13D0`, reached from the team screens. static:static/goal-exe/code/seg_1771_03.asm:246 static:static/goal-exe/code/seg_1771_03.asm:303 static:static/goal-exe/code/seg_1771_02.asm:1056

### The rule

- Both bytes are read signed: energy 0x80..0xFF and 0 make a player unavailable, form 0x80..0xFF subtracts. static:experiments/E020-q018-condition-performance/records/strength-001.json static:static/goal-exe/code/seg_1771_05.asm:777
- In the quick engine one energy point is one strength point (`+1` per point of `+0xE`) and one form point is one strength point up to 0x1F; at form 0x20 and above the term turns into a loss of a sixteenth, so form 0x1F is the best value and the clamp's top value 0x20 is worse, for example 226 at (energy 32, form 31) against 183 at (32, 32) at skill +4 = 225. static:experiments/E020-q018-condition-performance/tables-001.txt:7 static:static/goal-exe/code/seg_1771_05.asm:796
- In the watched engine the same cutoff holds (form adds `s8(+0xC) + 1` below 0x20 and nothing from 0x20 up), and a skill read at (energy 1, form 1) is 0.514 of the value at (32, 31), at element 3 of the sample record. static:experiments/E020-q018-condition-performance/tables-001.txt:17 static:static/goal-exe/code/seg_0791_04.asm:860

### The size of the effect at equal skill (quick engine, second half from 0-0)

- A side at (energy 32, form 31) has line sums (keeper, defence, midfield, attack) 242, 1022, 1045, 433 against 181, 778, 770, 341 for a side at (1, 1) with identical skill bytes, tactics and manager, and one B19D attempt scores with probability 0.0692 against 0.0197, exact under uniform independent draws. static:experiments/E020-q018-condition-performance/effect-001.json static:experiments/E020-q018-condition-performance/attempt-check-001.json
- Played from all 65,536 start seeds of the generator, the fit and confident side wins 32.9% and 33.8% of second halves (as team 0 and as team 1), the tired and unconfident side 11.3% and 11.2%, draws 55.8% and 55.1%; the same two sides with equal condition split 19.6/59.9/20.5 (both fit) and 20.3/57.3/22.4 (both tired). static:experiments/E020-q018-condition-performance/effect-001.json
- Energy alone (32 against 1, form 1 both) gives wins of 26.5% and 25.7% for the fitter side, losses of 16.7% and 15.4%; form alone (31 against 1, energy 1 both) gives 26.9% and 25.2% wins, 15.9% and 15.0% losses. static:experiments/E020-q018-condition-performance/effect-002.json
- The clamp's top form value costs: (32, 31) against (32, 32) gives 27.4% and 26.5% wins for form 31, 13.5% and 13.8% for form 32. static:experiments/E020-q018-condition-performance/effect-001.json
- The task's boundary example (energy 0x7F, form 0x3F against 0x3E, 0x00) gives 25.5% and 24.3% wins for the first side, 15.7% and 15.6% for the second. static:experiments/E020-q018-condition-performance/effect-001.json
- The model equals the original binary's whole second half (score, final seed, number of draws) on 32 edited halves in four scenarios. static:experiments/E020-q018-condition-performance/records/half-fit-tired-001.json static:experiments/E020-q018-condition-performance/records/half-tired-fit-001.json static:experiments/E020-q018-condition-performance/records/half-fit-fit_form32-001.json static:experiments/E020-q018-condition-performance/records/half-example_high-example_low-001.json

### The hypothesis, per engine

- Quick engine: yes, with one exception for form, since energy always helps and form helps up to 0x1F and hurts at 0x20 and above. static:experiments/E020-q018-condition-performance/effect-001.json static:experiments/E020-q018-condition-performance/tables-001.txt:7
- Watched engine: yes at the level of every skill read, which scales with energy and form, but the size of the effect on a match is not established, because no model of `9564` exists to play it. static:experiments/E020-q018-condition-performance/tables-001.txt:17 static:static/goal-exe/code/seg_0791_04.asm:902

## Method

Static first (U32): the named view `static/goal-exe/named/` was consulted for names, then the instruction listings for every claim; E017's exhaustive `+0xC/+0xD/+0xE` inventory was re-run (`experiments/E017-q015-energy/inventory.py`) and a second grep over the other addressing forms found only runtime-library objects. Engine membership comes from the call trees of `reach.py` over `calls.tsv` (direct calls only). `notes.md` holds the claim map with listing lines.

Static analysis answered the readers and the arithmetic. It could not give the match-level size of the effect, so the quick-engine model (`runtime/model/condition.py`, reusing `quick_engine.QuickMatch.player_strength` and `keeping.contest_value` unchanged) computes it, after the original code was run to check the model: `probe_original.py` calls the original `377E` and `278A` on literal records, `probe_halves.py` runs the original second half (`emu_quick.py`, T24's interventions) on a half-time state edited by player word (`common.equal_skill_edits`: team 1's records overwritten by team 0's except the country byte, country 19's tactics and manager equal to country 7's, `DS:80FC` cleared, then the (energy, form) pair on each side). `effect.py` plays the model from every seed in both orientations; `attempt_check.py` compares the exact attempt probability with the generator.

A defect found on the way: `keeping.py` names the keeper-extra event as the value 0x18, but 0x18 is the byte of a set whose members are `DS:8327` = 3 and 4; `condition.contest` passes the membership, and `event-gate-001.log` is the original's answer. `keeping.py` is outside this task and is unchanged.

## Observations

| Item | Value | Source |
| --- | --- | --- |
| original 377E vs model | 617 of 617 comparisons by player word (strength 172 + 21 + 183, contest 155 + 12 + 42, halves 32) | check_condition.py, `check-001.log` |
| keeper-extra event gate | extra added for `DS:8327` = 3, 4 only (0..0x20 tried) | `event-gate-001.log` |
| model, fit/tired, all seeds | 21569 / 36579 / 7388 and 7315 / 36101 / 22120 (team 0 wins / draws / team 1 wins) | `effect-001.json` |
| attempt probability vs generator | exact 0.06920 / 0.01970, observed 0.06868 / 0.01959 over 786,432 attempts per team | `attempt-check-001.json` |
| mutations | 148 literals of `condition.py` and the `377E`, `3216`, `3179` bodies, +1 and -1: 146 killed; 2 survivors are equivalent mutants (`quick_engine.py:257` `< 0` to `< 1` and `:259` `> 0x100` to `> 0xff` give the same clamp result) | `mutations-002.log` |

## Inferences

- The quick result favours a fit and confident side because it enters every one of its eleven strengths and therefore the midfield and attack sums that the three B19D contests compare. static:static/goal-exe/code/seg_1771_02.asm:187 static:experiments/E020-q018-condition-performance/effect-001.json
- Confidence beyond 0x1F cannot help in either engine because both arithmetic forms stop adding the form byte at 0x20. static:static/goal-exe/code/seg_1771_05.asm:796 static:static/goal-exe/code/seg_0791_04.asm:860
- Resting a player cannot raise a match strength through fitness alone, only through the energy that fitness is copied to before the next match. static:static/goal-exe/code/seg_0791_20.asm:1031

## Alternatives considered

- That a hidden reader of `+0xD` exists beyond the scan: not excluded for a record reached through a register-computed offset; the two grep passes and the original code's invariance to `+0xD` in `377E` and `278A` exclude the direct readers.
- That team morale `DS:9B5A` reaches a match: excluded by the complete list of its references in `datarefs.tsv` and the listing grep.
- That the effect on the watched engine equals the quick one: not excluded and not claimed.

## What this does not establish

- The first half (the model starts at the half-time stall), extra time, penalties and the foul path `D5C1` (not modelled).
- The effect on a watched match, and what `4E28` does when `5049` calls it.
- Other skill levels than the E010 state's, and the fraction of play at the ends of the energy range.
- A DOSBox-X run of an edited state: none was taken.

## Where the evidence is

Records, logs and outputs are tracked under `experiments/E020-q018-condition-performance/`; the savestate is E010's release asset `3c7983fa4869d327-E010-r0010-halftime.sav`. No evidence bundle was published for E020.

## Reproduction

`python3 experiments/E020-q018-condition-performance/check_condition.py`; `python3 -m unittest -v tests.test_model_condition`; `python3 experiments/E020-q018-condition-performance/effect.py <new-name>.json` (about 4 minutes per scenario pair).
