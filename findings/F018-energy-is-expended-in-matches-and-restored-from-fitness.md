# F018 Energy is +0xE, fitness is +0xD: matches spend energy, and the recovery path changes fitness before restoring energy

- **Status**: proposed
- **Question**: Q015 (Q05.1–Q05.3), how energy falls in a match and recovers between matches (T31).
- **Tests claims**: F008's still-likely fitness/energy byte identities; F015's signed energy input; GOAL.HLP's man-marking/activity and substitute-start claims.
- **Experiment and runs**: E017, `experiments/E017-q015-energy/`. Original-code Unicorn probes, not DOSBox-X runs; no E015 record is used. All captures and failed attempts remain committed. No `runs/E017/` or `evidence/E017/` was produced.
- **Artifact**: `goal2-a949da2f`, packed GOAL.EXE SHA-256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`; unpacked SHA-256 `6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188` (listing headers). Watched input: E011 released half-time savestate SHA-256 `092f5f74bc5dc0c0f133709ca46be04122d3813a716c54fd23a686e9194ab9ff`.
- **Max intervention**: watched probe starts from the E011 state with F013's resume/BIOS conventions; recovery probe supplies eight literal player records to original 1771:3651. These are emulated guest-code probes, not a new unmodified game sitting.
- **Confidence**: unreviewed. The arithmetic claims below are static-derived; the watched tail and 3651 outputs additionally match original guest execution. This does not claim independent full-match, marking-counterfactual or substitution behavioural corroboration.

## Method

Static first: read `static/goal-exe/named/seg_0791_07.c` (8AE9, 9A32),
`seg_0791_10.c` (CB7D, D733 and manual substitutions), `seg_0791_09.c`
(B7FA, BA4E, C5DC, C88D), `seg_1771_03.c` (3558, 3651 and player screen),
then the raw decompiler and instruction listings. The exhaustive direct
C/D/E inventory in E017 `notes.md` removes the former player-load filter,
classifies every direct DI access by its base pointer, and includes pitch,
scorer, manager and runtime-object false positives. C arithmetic is inventoried
but morale-outcome rules remain Q016/Q017, not a new inference here.

The listing answers the field identities, arithmetic, call inputs, half-start
bonus, substitution and marking dependencies. Static analysis alone cannot
provide the exact activity/input sequence in a watched half; the Unicorn
probe therefore observes the inputs of the established write paths, replays
them in `runtime/model/energy.py`, audits unknown field stores and compares
every squad player's final C/D/E by word. It is not an independent movement
simulator. The standalone 3651 probe checks draw ordering and signed/clamp
edges against original instructions on literal records. No additional game
runs were needed to obtain these byte-write checks.

`records/watched-half-002.json` holds 40 comparisons, 184 counter tails,
182 decrement stores, no unknown C/D/E stores and no skipped wait-family calls.
It reaches clock 91 in 2077 ticks, but does not record terminal CS:IP;
no terminal-address assertion is inferred from the clock. `watched-half-001.log`
is the preserved failed hook attempt. `records/recovery-002.json` holds eight
comparisons. `recovery-001.json` lacks a healing draw because 06D0 calls
0688 directly, bypassing the original 06B1 hook
(`static/goal-exe/code/seg_214B_01.asm:913–935`); it remains unchanged and is
explicitly superseded by the same-case repeat in README and `supersessions.json`.
The checker prints the declaration/reason and fails if the successor is absent.

All assembly citations below are under `static/goal-exe/code/`; physical listing
line numbers, not decompiler line numbers. Each paragraph states its own limit.

## Answer

### 1. Byte identities — static-derived, guest-checked for their write paths

- **Fitness is player +0xD; energy is player +0xE.** The player-screen row y=20
  reads D, except that E=0 displays the injured word; row y=21 and its bar read E
  (`static:static/goal-exe/code/seg_1771_06.asm:1060, static:static/goal-exe/code/seg_1771_06.asm:1192`). Recovery changes D and then copies it
  to E (`static:static/goal-exe/code/seg_1771_05.asm:648`), while the watched and quick decrements write
  only E (`static:static/goal-exe/code/seg_0791_14.asm:1060`; `static:static/goal-exe/code/seg_0791_21.asm:1165`). The byte
  identities are thus settled by distinct consumers/writers, not by equality in
  new-game records. Zero E is the injury store (`static:static/goal-exe/code/seg_0791_13.asm:582`) and
  signed E<1 makes the player unavailable (`static:static/goal-exe/code/seg_1771_05.asm:193`). Negative
  energy encodings are not treated as playable positive energy by those gates.

- `DS:7624` is the Pascal text "very tired", **not** an energy table
  (`static:static/goal-exe/strings.tsv:1307`; the screen's string-table indexing is at
  `static:static/goal-exe/code/seg_1771_06.asm:1063`). The per-match activity word is pitch +0x14;
  pitch +0xD is a player **word index**, not fitness. Player pointers are rebased
  from it by multiplying by 20 and loading A91B
  (`static:static/goal-exe/code/seg_0791_14.asm:897`; `static:static/goal-exe/code/seg_0791_21.asm:1173`).

### 2. Watched energy loss — static-derived, replay matched on one guest half

- After the handler and 8889 movement, 8AE9 adds one to the unsigned pitch
  activity word if unsigned pitch +0xF is less than 5
  (`static:static/goal-exe/code/seg_0791_14.asm:1005`). If DS:8325 is nonzero and the counter is
  **strictly greater than 180**, it decrements E only if **signed E>1**, then
  resets the counter to zero even when the decrement is suppressed
  (`static:static/goal-exe/code/seg_0791_14.asm:1060`, 8C35–8C5D). It does not change fitness.
  The +F directions 1/2 or 3/4 arise from movement toward the target, 5 from
  already being there, with random axis selection and movement retries
  (`static:static/goal-exe/code/seg_0791_14.asm:775`). The activity count is active **updates**, not
  distance travelled, a per-minute weight, or a direct player-position multiplier.
  A2E6 resets it on slot initialization (`static:static/goal-exe/code/seg_0791_17.asm:113`).
  No fixed energy cost by role or man-marking appears at the write. State handlers,
  movement targets and the watched scheduler can alter how many active updates
  reach it; the exact sequence depends on the engine's draws (F013). E017's
  model consumes the actual counter at the tail, rather than predicting movement
  from the same final energy it checks.

### 3. Quick energy loss and half-start bonus — static-derived, unit-tested

- D733's slot loop decrements signed-positive E>1 by one for each pitch slot
  1..22 whenever unsigned DS:831B modulo **5** is zero
  (`static:static/goal-exe/code/seg_0791_21.asm:1165`, DA8D–DAC9). There is no role or marking gate
  at this write and no fitness write. This is a **slot-visit rule**; it is not a
  claim that every player plays 90 minutes or loses an invariant total amount:
  substitutions, half-start processing and engine scheduling are separate inputs.

- The shared pre-half 9A32 loops pitch slots 1..22 and adds **2 only for E=1..30**
  (CS:99F2's bytes FE FF FF 7F, `static:static/goal-exe/code/seg_0791_16.asm:339, static:static/goal-exe/code/seg_0791_16.asm:354`). Zero,31,32 and
  negative encodings are not set members. E011's half-time team-screen state is
  after this step (F013); E017 therefore does not apply it twice. The unit model
  exposes quick slot visits and watched tails, not a complete quick-game simulator.

### 4. Match-end restoration and between-match recovery — static-derived; 3651 guest-checked

- CB7D loops both sides' nonzero squad words in slots 1..20. It restores C from
  DS:9B07[20*side+slot], then copies D to E **only for signed E>0**
  (`static:static/goal-exe/code/seg_0791_20.asm:1010`, CBD2–CC27). This is restoration from the player's
  own fitness, not a literal 32 refill; zero/negative energy stays unchanged.
  The model's restore helper includes the C copy only for whole-byte accounting.
  1771:3651 starts with **signed D**, consumes draws in this order, and computes:

| Input branch | Ordered guest draws | Fitness word before bounds | Basis |
| --- | --- | --- | --- |
| E exactly 0 | rand(2), rand(8) | s8(D)+first-second | static:static/goal-exe/code/seg_1771_05.asm:647 |
| E nonzero, flag nonzero | rand(2), rand(8) | s8(D)+second-first | static:static/goal-exe/code/seg_1771_05.asm:666 |
| E nonzero, flag zero | rand(3), rand(2) | s8(D)+second-first; add 1 if intermediate <16 | static:static/goal-exe/code/seg_1771_05.asm:680 |

- It sets a result below 1 to 1 and **bypasses** the upper clamp in that branch;
  otherwise it caps at DS:0E84[unsigned age>unsigned peak_age+3]
  (`static:static/goal-exe/code/seg_1771_05.asm:694`). It stores D and restores E from D when signed E>0;
  otherwise it restores only when random-is-one(3) succeeds, which consumes the
  underlying 1..3 draw and succeeds on 1 (`static:static/goal-exe/code/seg_1771_05.asm:741`;
  `static:static/goal-exe/code/seg_214B_01.asm:913`). An E with a negative encoding takes the noninjured
  fitness branch, but still needs the healing-gate draw. These are draw-dependent
  steps, not average recovery constants.

- B7FA chooses 3651 when 5A8F is nonzero (3558 otherwise), passing flag 1 for
  the XI or participants carrying status bit 3 and flag 0 for unused bench
  players (`static:static/goal-exe/code/seg_0791_19.asm:103, static:static/goal-exe/code/seg_0791_19.asm:171`). BA4E makes the same selection,
  passing flag 0 for the manager's 80 pool words (`static:static/goal-exe/code/seg_0791_19.asm:245`).
  The selector is a caller result, not a fixed interval in days; no guessed daily
  recovery schedule is introduced.

- 3558 is a **redraw**, not 3651 recovery: B=DS:0E82[age>peak_age+4]; managed
  fitness byte is B+rand(3B)-rand(B+1), with rand(B+1) drawn first, unmanaged
  fitness byte is B+rand(2B). It clamps signed D above 32, copies D to E, then
  clamps signed D below 1 (`static:static/goal-exe/code/seg_1771_05.asm:542`). The ordering can leave
  pathological byte encodings unequal. This redraw is inventoried but is not
  implemented by E017's 3651 helper. A continuing player's yearly age loop does
  not directly write C/D/E; a computer retiree's recreation does, through
  7E80 -> 96D3 -> 3558 (`static:static/goal-exe/code/seg_1771_11.asm:870, static:static/goal-exe/code/seg_1771_11.asm:1000`;
  `static:static/goal-exe/code/seg_1771_13.asm:1186`; F016).

## Inferences

### 5. Help claims — static-derived, no counterfactual run claim

- **Man-marker loses more? No unconditional extra decrement; an indirect
  activity effect exists.** Country +2D element 8 supplies marking assignments
  (3EF8, `static:static/goal-exe/code/seg_1771_06.asm:715`, F010); player +F overrides only elements 1..4, not marking
  (`static:static/goal-exe/code/seg_0791_04.asm:787`). 47C5 uses the assigned opponent word or selects
  a zone-tested target when the word is zero (`static:static/goal-exe/code/seg_0791_08.asm:190`;
  `static:static/goal-exe/named/seg_0791_04.c:23`). 4A28 can copy that target's
  coordinates to pitch +7 after energy/tactic gates
  (`static:static/goal-exe/code/seg_0791_08.asm:553`). Movement toward that target can change the active
  updates counted by 8AE9, but the listing does **not** prove every man-marker
  necessarily loses more than his zonal counterpart. In quick mode the decrement
  write itself is identical for every pitch slot. No invented marking weight
  is placed in the model.

- **Substitute starts full? No automatic full-energy store.** C88D swaps squad
  words and shadows and calls C5DC; C5DC calls A2E6 to rebind the incoming word
  and reset the pitch activity/direction, not player fitness or energy
  (`static:static/goal-exe/code/seg_0791_20.asm:661, static:static/goal-exe/code/seg_0791_20.asm:490`;
  `static:static/goal-exe/code/seg_0791_17.asm:6`; F012's C88D trace). The manual E022 swap also calls
  C5DC (`static:static/goal-exe/named/seg_0791_11.c:506`). He brings his own E,
  normally unspent while on the bench, rather than receiving 32 or a D-to-E
  copy at the substitution. "Full" may describe that ordinary bench state;
  it is not an unconditional instruction-path refill.

## Checks and limits

`python3 experiments/E017-q015-energy/check_energy.py` compares **48/48**
player-word records (40 watched, eight recovery), all three C/D/E bytes for
each. No names, empty set, unknown stores or missing final words are accepted.
The superseded incomplete capture is printed by name and reason.

`python3 -m unittest -v tests.test_model_energy` passes 15 literal-record
tests. `mutations-001.log` preserves two surviving draw-bound mutations;
after adding literal rejection tests, `mutations-002.log` kills **16/16**
declared numeric constants edited in place, clean bytecode, a timeout per
mutant and restoration in `finally`. The added tests fail with REST_DRAW=4
and HEAL_DRAW=4 and pass with the listing's 3 restored.

There is no end-to-end complete quick-match prediction, independent watched
movement model, marking paired run, substituted-player behavioural comparison,
new morale-outcome rule, injury-cause rule or E015 comparison in this finding.
