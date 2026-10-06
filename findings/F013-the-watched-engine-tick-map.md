# F013 The watched engine `9564`: one player sweep per tick over the pitch records, the display drawing from the seed every tick, and the match clock as the tick id

- **Status**: proposed
- **Question**: What is the tick skeleton of the watched match engine (`0791:9564` and the loop
  around it) — the internal order of one engine call, each callee's role, which draws happen per
  tick and which per event, and how a watched half is paced — so later milestones can model it
  seed-exactly as F012 modelled the quick engine? (Q010, `docs/backlog.md`; T25, milestone 1)
- **Tests claims**: the backlog's Q010 (the watched half); feeds the rebuild's watched-match path
  and the bot (whose own matches are watched); bears on F005 (which engine a watched match runs),
  F006 (host speed does not change a match), F012 (the quick engine, whose tick loop, clock and
  pre-half sequence this engine shares), F010 (the tactic updates reached from both engines).
- **Experiment and runs**: E011 (T25; two watched launches from E006's published start state
  `e006-2100-r0005`, the ground truth), and the Unicorn harness `runtime/emul/watched.py` emulating
  the original binary's second half from the runs' published half-time savestates
  (`experiments/E011-q010-watched-engine/emu_check.py`).
- **Artifact**: set `goal2-67cf27d6`, variant none (the E011 records' watchstart and half-time
  savestates, release E011).
- **Max intervention**: I2 (savestates written at every read and the start state loaded, Host+L;
  memory read from them, I1 — the clock words `DS:831F/831D/8325/831B` and the seed `DS:7B62`).
- **Tier reached**: V2 (the emulated half puts every mid-play second-half read of both records on
  the emulated trajectory, `match: 38/38`; a mutated resume constant drops it to 0/10).
- **Confidence**: unreviewed (status `proposed`). Static: every claim read from the listing
  (`static/goal-exe/code/`, the named view first). Behavioural: the two E011 records and the
  Unicorn emulation of the original's own code. Claims on one route say so.

## Answer

- **One watched tick is: the engine sweep `9564`, then `8CF5`, then `9119`, then the clock
  `970C`** (both). `0791:97D0` (seg_0791_16.asm:97D3-983C): with `DS:9A3E` clear, in order —
  the replay handling (`0C65` when `DS:7C37`, else `15B9` when `DS:9B55`, `97DF`-`97F2`),
  `9B55/0C20/7C37` cleared (`97F5`-`9806`), `call 9564` (`980B`), then while still watched
  `call 8CF5` and `call 9119` with `DS:82EE` and argument 0 (`9815`-`9821`), then `970C`
  (`9824`); `983F` pushes 0 as the loop's guard (`9879`-`987C`), so the loop runs to the
  clock's end-of-half. High confidence (listing; the emulation runs exactly this and matches).
- **`9564` is one sweep of a slot loop 1..0x16 over the pitch records, not a physics step of
  the whole pitch at once** (static; the emulation runs it as guest code). Per slot
  (seg_0791_15.asm:946-1140): the ball phase, gated by `DS:8302` nonzero (`9574`) and the
  threshold byte at `0x899 + 0x16*flag + slot <= DS:8300` (`95AA`-`95B4`; flag 0, or the
  membership of `DS:8327` in the set `CS:9544` when `DS:8303` is set, `958D`-`959D`; `0x899`
  is a two-row threshold table, `0x883` a different table mapping the loop index to a record
  number) — the shot counter pair `DS:80F6+2*eq` (`95B9`-`95EE`), `83A2 move_ball`, `2FB1`,
  `2996`, the keeper special `2CEC`/`2E36`/`8AE9` (`9636`-`9666`), `59B3 check_woodwork` and
  the 22-record `6188 handle_player_at_ball` loop (`9669`-`9699`); then always the per-slot
  tail: `8AE9 update_player` on the record `DS:883[slot]` maps to (`969B`-`96C8`), `2FB1`
  again when that slot is `DS:830B` (`96CB`-`96D6`), `94E8 speaker_noise`, `8F10 draw_ball`,
  `9372` the key poll (`96DB`-`96E7`); the sweep returns at once when R sets `DS:9A3E`
  (`96F1`), and at slot 0x16 takes 2 off `DS:832A` (`96FC`-`9703`). High confidence.
- **The seed advances every tick of a watched match, through the display** (both). `9119`,
  called by the loop with argument 0 every tick, draws exactly one `rand(2)` — the referee's
  target column (seg_0791_15.asm:91CC or 91F1; `214B:0D1C`/`0D56` are RNG-free min/max
  clamps, seg_214B_02.asm:0D1C-0D53) — and `8889`, reached from `update_player` per updated
  record, draws one coin (`214B:06FA` at 8A2E, seg_0791_14.asm) on its 2CC5 = 0 path: 0..22
  more draws per tick. The emulated second half drew 91985 times in 2077 ticks (~44 per tick);
  the quick engine's whole second half is 3617 draws (F012). This is F005's "the display path
  draws from the seed every tick", now quantified: a watched match cannot be modelled without
  emulating the display-side draws. High confidence.
- **A watched minute is the `0x24` sub-tick countdown, and `(DS:831F, DS:831D)` identifies a
  tick** (both). `9564` never writes `DS:831D` (no `0x831d` operand in seg_0791_15.asm:946-1140;
  `D733` zeroes it at D811, F012), so `970C` paces a watched half at ~0x25 loop iterations per
  minute: `831F` the minute, `831D` the sub-tick (reloaded 0x24 at each minute boundary,
  seg_0791_16.asm:972E-9762). The E011 records read both words at every savestate, which pins
  each read to its tick. High confidence.
- **The watched half-time stall is the `ED8A` wait inside `9A32`, and the second half resumes
  through `983F`** (both). `9A32` (seg_0791_16.asm:268-346): per slot the player's `+0xE` +2
  (set-gated, `9A71`-`9A85`), `9B41=1`, screen copies, `0106`, the wait `ED8A` (`9AE0`,
  skipped only when `DS:80FD=0` AND the key `DS:A977` is in the set `CS:9A12`; with no key
  sent it always waits, and the wait consumes no RNG — E010/F012's lesson, the watched analogue
  confirmed by both records' equal half-time state: seed `0xf457`, `831F=46`, `831B=45`, score
  1-1); the tail then sets `DS:830B = 0668[(831A==0?1:0)]+10` and `DS:832A = 0x50`
  (`9AEE`-`9AFF`) and calls `983F`. `983F` (:349-403) runs the half: `8062`, `2A15`, the
  watched-only `2929` and `8CCA`, the flags, the tick loop, the `9079` cleanups, `8325=0`,
  speaker off. The Unicorn harness enters at `983F` from the stall savestate with the tail's
  two writes applied and reproduces the records' trajectory. High confidence.
- **A watched match from one start state is deterministic in its outcome, and its mid-read
  samples are host-timed** (behavioural). E011-r0001 and r0002 (one replay): identical
  half-time state, events, full-time score 1-1 and seed `0xb601`, full-time screen; the
  mid-play reads land at minutes 51..91 (r0001) and 55..91 (r0002) — the same minutes differ
  in phase, as the tick reading predicts: a savestate catches the guest at an arbitrary
  instruction, so its `(831F, 831D, 7B62)` is a point on the trajectory, not a fixed tick.
  That is why the ground truth is checked by membership: `emu_check.py` matches a read when
  its seed value is one of the values the word takes at that minute (`match: 38/38` over both
  records' second-half reads; a mutated `830B` resume constant drops r0001's own checkpoints
  to 0/10, so the check is not vacuous). High confidence.
- **The `000E` wait family (the crowd animation, an RNG consumer) is unreachable from the
  match** (static, re-verified). Its callers are `000E` menu code only (`calls.tsv`); the
  harness's skip log stayed empty through both emulated halves (E010's closure miss, closed
  again for the watched tree). High confidence.
- **`8CF5` tracks and draws each side's offside line, and can raise the offside path**
  (static): per side, over the side's outfield slots `0668[side]+2..+11`, it keeps in the
  six-byte per-side sprite at `DS:82E2+6*side` the DEEPEST defender — the smallest y × the
  side's attack direction (`2BE5`, `jge` keeps the earlier, seg_0791_15.asm:28-110), stored
  back as that y (min × direction, `8DB5`-`8DC3`) — draws the sprite through `8E24` (`8DCD`),
  and when that y's sign equals the ball y's sign, `DS:8328` is set and the y is nonzero,
  calls `90C5` on the record at `DS:8304` (`8DD3`-`8E14`). No RNG anywhere in its tree
  (`8E24`, `90C5` make no RNG calls); called every tick by the loop. Likely (listing only;
  what `90C5` does with `DS:8304` is milestone 2+).

## Method

- Machine and tools: as F004/F010 (Ubuntu 24.04 in WSL2, DOSBox-X 2024.03.01, Xvfb, xdotool,
  python 3.12.3), `cycles=30000` fixed, driver `runtime/driver/driver.py`, the watched arm of
  `runtime/driver/match.py` (E004's key discipline: `Enter Right×5` in one burst — the delay
  byte 0 — then one Enter per stopped-clock screen: the half-time `hit any key`, the team
  screen; never a key during play). Runner `experiments/E011-q010-watched-engine/run.py`
  (`code_commit` in each record); two launches only (the run cap's first two).
- Start state: E006's published `e006-2100-r0005` (release E006, manifest-verified), adopted
  by E007's `adopt`; a fresh launch, Host+L, E004's keys to the captain screen; that savestate
  is each run's `watchstart` output. Outputs published on release E011
  (`evidence/E011/*.manifest.json`, `tools/verify_evidence.py E011`).
- Static first (U32): the named view `static/goal-exe/named/` was read before the raw
  listings; the tick map's order, guards and callee roles were established from
  `static/goal-exe/code/seg_0791_15.asm`, `seg_0791_16.asm`, `seg_0791_14.asm` and
  `seg_214B_02.asm`, with `calls.tsv` for the RNG-consumer closure. What static analysis
  answered: everything above — the loop order, the sweep's structure, the per-tick draws, the
  clock, the stall and resume, the unreachable waits.
- Why runs were needed: to corroborate (rule 19) — that the tick map is the real watched
  engine's order (a mis-ordered map would desynchronise the emulation), that the per-tick draw
  claim holds on a real match (the records' minutes advance while the seed churns ~44 draws
  per tick), that the stall state is exact and the resume constants sufficient, and that the
  read phase is host timing while the outcome is deterministic. The ground truth is also the
  deliverable later milestones check models against (E011's per-read `(minute, sub-tick,
  seed)` trajectory, in each record's observations).
- The Unicorn harness (`runtime/emul/watched.py`, generalised from T24's
  `emu_full_loop.py`): the savestate Memory component's 0x78-byte header, 16-bit linear
  addresses, the BIOS key thunk `214B:0723 → 235C:000B` stubbed AL=0, interrupts swallowed.
  No display or engine routine is skipped: `983F` whole (head, loop, cleanups) runs as guest
  code; only the `000E` wait family is skipped, behind a stray log that must stay empty (it
  did). One emulated second half: 2077 clock ticks, 91985 main-seed draws, final minute 91,
  score 1-1, in ~2 minutes of host time.

## Scope and limits

Milestone 1 (the tick map) only: a seed-exact Python model of `9564` is milestone 2+; the
event routines' internal rules (`5B36`, `5F8A`, `690C`, the foul path, `8206`), ratings
(Q011), keeping and penalties (Q012), energy (Q015) and formations (Q023) are out of scope —
they appear here only as event-drawing callees. `8CF5`'s tracked value's consumers, the
threshold table `0x899`'s semantics and `8889`'s movement rule are listing-read but not
corroborated in isolation (the emulation covers them only as part of the whole). The two
records' four differing bytes outside the data segment (the BIOS tick and four heap bytes,
checked byte-for-byte) are timing artefacts, not game state.
