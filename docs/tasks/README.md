# Tasks

One file per task, `T<nn>.md`, from [`TEMPLATE.md`](TEMPLATE.md). This index carries no status:
the issue's `status:*` label is the status (`gh issue list --label task --label status:ready`).
Each title ends with the task's plan label (G0, G1, …) from `docs/plan.md` once it
exists.

| Task | Title | Issue | Merge after |
| --- | --- | --- | --- |
| [T96a](T96a.md) | Persistent player-record dictionary (ES-R1) | [#464](https://github.com/diegoami/goal2-archaeology/issues/464) | T95 |
| [T96b](T96b.md) | Derived player traits and field-use boundaries (ES-R1) | [#465](https://github.com/diegoami/goal2-archaeology/issues/465) | T96a |
| [T97a](T97a.md) | Persistent team and fixture state (ES-R1) | [#466](https://github.com/diegoami/goal2-archaeology/issues/466) | T95 |
| [T97b](T97b.md) | Transient pitch, ball and match globals (ES-R1) | [#467](https://github.com/diegoami/goal2-archaeology/issues/467) | T97a |
| [T98a](T98a.md) | Effective skill arithmetic and worked examples (ES-R1) | [#468](https://github.com/diegoami/goal2-archaeology/issues/468) | T96b, T97b |
| [T98b](T98b.md) | Strength, availability and foot arithmetic (ES-R1) | [#469](https://github.com/diegoami/goal2-archaeology/issues/469) | T98a |
| [T99a](T99a.md) | RNG and single-player skill gates (ES-R1) | [#470](https://github.com/diegoami/goal2-archaeology/issues/470) | T98b |
| [T99b](T99b.md) | Opposing contests and quick scoring probabilities (ES-R1) | [#471](https://github.com/diegoami/goal2-archaeology/issues/471) | T99a |
| [T95](T95.md) | Engine inventory and evidence map (engine study) | [#434](https://github.com/diegoami/goal2-archaeology/issues/434) | planning merge |
| [T96](T96.md) | Player attribute dictionary (engine study) | [#435](https://github.com/diegoami/goal2-archaeology/issues/435) | T95 |
| [T97](T97.md) | Team, fixture and transient match-state dictionary (engine study) | [#436](https://github.com/diegoami/goal2-archaeology/issues/436) | T95 |
| [T98](T98.md) | Attribute formulas and worked player examples (engine study) | [#437](https://github.com/diegoami/goal2-archaeology/issues/437) | T96, T97 |
| [T99](T99.md) | Contest probabilities and decision thresholds (engine study) | [#438](https://github.com/diegoami/goal2-archaeology/issues/438) | T98 |
| [T100](T100.md) | Match tick, state transitions and random-number flow (engine study) | [#439](https://github.com/diegoami/goal2-archaeology/issues/439) | T95, T97 |
| [T101](T101.md) | Pitch positioning, marking and movement anatomy (engine study) | [#440](https://github.com/diegoami/goal2-archaeology/issues/440) | T97, T100; [ES-R1](../engine-study-reviews.md#es-r1) accepted |
| [T102](T102.md) | Possession, ball actions and scoring anatomy (engine study) | [#441](https://github.com/diegoami/goal2-archaeology/issues/441) | T99, T100, T101 |
| [T103](T103.md) | Tactics, formation choices and computer-manager behaviour (engine study) | [#442](https://github.com/diegoami/goal2-archaeology/issues/442) | T96, T97, T101, T102 |
| [T104](T104.md) | Restarts, discipline, substitutions and post-match effects (engine study) | [#443](https://github.com/diegoami/goal2-archaeology/issues/443) | T96, T97, T100, T102 |
| [T105](T105.md) | Preregister bounded experiments and synthetic scenarios (engine study) | [#444](https://github.com/diegoami/goal2-archaeology/issues/444) | T98, T99, T101, T102, T103, T104 |
| [T106](T106.md) | Validate isolated mechanisms with synthetic probes (engine study) | [#445](https://github.com/diegoami/goal2-archaeology/issues/445) | T105; [ES-R2](../engine-study-reviews.md#es-r2) accepted |
| [T107](T107.md) | Run the first bounded match sensitivity batch (engine study) | [#446](https://github.com/diegoami/goal2-archaeology/issues/446) | T105, T106; [ES-R2](../engine-study-reviews.md#es-r2) accepted |
| [T108](T108.md) | Audit arithmetic, boundaries and record indexing (engine study) | [#447](https://github.com/diegoami/goal2-archaeology/issues/447) | T96, T97, T98, T99; [ES-R1](../engine-study-reviews.md#es-r1) accepted |
| [T109](T109.md) | Audit cross-module consistency and execution paths (engine study) | [#448](https://github.com/diegoami/goal2-archaeology/issues/448) | T100, T101, T102, T103, T104, T106 |
| [T110](T110.md) | Readable-engine architecture and rewrite decision (engine study) | [#449](https://github.com/diegoami/goal2-archaeology/issues/449) | T95, T98, T99, T100, T101, T102, T103, T104, T108, T109; [ES-R3](../engine-study-reviews.md#es-r3) accepted |
| [T111](T111.md) | Conditional readable-rule prototype (engine study) | [#450](https://github.com/diegoami/goal2-archaeology/issues/450) | T110; [ES-R4](../engine-study-reviews.md#es-r4) accepted |
| [T112](T112.md) | Assemble the engine guide and exploration atlas (engine study) | [#451](https://github.com/diegoami/goal2-archaeology/issues/451) | T95, T96, T97, T98, T99, T100, T101, T102, T103, T104, T106, T107, T108, T109, T110; [ES-R3](../engine-study-reviews.md#es-r3) accepted, [ES-R4](../engine-study-reviews.md#es-r4) accepted |
| [T113](T113.md) | Independent milestone review of the engine study (engine study) | [#452](https://github.com/diegoami/goal2-archaeology/issues/452) | T112 |
| [T114](T114.md) | Country TEAM team-skills bars | [#432](https://github.com/diegoami/goal2-archaeology/issues/432) | T94 |
| [T115](T115.md) | Country TEAM performance bars | [#432](https://github.com/diegoami/goal2-archaeology/issues/432) | T114 |
| [T116](T116.md) | Country TEAM characteristics | [#432](https://github.com/diegoami/goal2-archaeology/issues/432) | T114 |
| T93 | Manager-name boundaries and the B Vogts glyph | #429 | — |
| T94 | Country TEAM Status and Skill | #428 | T93 |
| T01 | The GOAL2 research repository: layout, the artifact by hash, the plan (G0) | #1 | — |
| T02 | Runtime feasibility: launch, act, observe, reset GOAL2 under DOSBox-X (G1) | #3 | T01 |
| T03 | The record tools, adapted from toy-archaeology (G2) | #4 | T01 |
| T04 | Static inventory: unpack GOAL.EXE, map its code, propose GOAL.DAT's structure (G3) | #5 | T01 |
| T05 | The documentation map: GOAL.HLP passages as sources (G4) | #6 | T01 |
| T06 | The research backlog: falsifiable questions per area (G5) | #15 | T02, T04, T05 |
| T07 | The G1 driver: launch, act, observe, reset, with run records (G1) | #16 | T02 |
| T08 | Q001: what inputs beyond the start state and the keys does GOAL2 use (G5 Q001) | #21 | T06, T07 |
| T09 | Use game-archaeologist's pinned validator and register_artifact.py (ADR-009) | #22 | T08 |
| T10 | Q002: does the quick result run the same engine as a watched match (G5 Q002) | #26 | T08 |
| T11 | Register the successor of goal2-a949da2f that declares the runtime writes (U21) | #14 | T09 |
| T12 | Q003: do `cycles`, the host speed or wall-clock time change a match (G5 Q003) | #33 | T10 |
| T13 | Savestates as evidence bundles: publish start states to a release (ADR-008) | #37 | T12 |
| T14 | Use game-archaeologist's shared verify_evidence.py and check_citations.py (ADR-009) | #36 | T13 |
| T15 | Q004: where and how are player skills and attributes made (G5 Q004) | #43 | T12, T13 |
| T16 | Q009: which skills the player screen shows, on what scale, from which fields (G5 Q009) | #48 | T15 |
| T17 | Findings pass the pinned citation checker, with no claim changed | #50 | T14 |
| T18 | Decompile GOAL.EXE with Ghidra: pseudo-C per routine, checked against the listing (G3) | #52 | T04 |
| T19 | Q005: what R008 sets, and the continental order of country strength (G5 Q005) | #59 | T18 |
| T20 | The named view: annotations applied to the decompiled GOAL.EXE, improved by each task (G3) | #60 | T18 |
| T21 | F010's fields and routines into the named view's annotations | #66 | T19, T20 |
| T22 | Q007: the squad pool, 100 players and which (G5 Q007) | #67 | T20 |
| T23 | Q010 (quick engine): how strengths and tactics meet in the quick result's contests (G5 Q010) | #68 | T20, T21 |
| T24 | Q010 (quick engine) milestone 2: r0010's divergence, model tests, F012 and the annotations | #75 | T23 |
| T25 | Q010 (watched engine `9564`) milestone 1: the tick map, the Unicorn ground truth and F013 | #81 | T24 |
| T26 | Q011: how performance ratings and the man of the match are computed | 83 | T24 |
| T27 | Q012: where keeping is read (only the keeper), and where penalties are read (only in `A10A`) | 88 | T26 |
| T28 | Q013: how skills change with age, and what is a player's peak age (G5 Q004) | opened at dispatch | T27 |
| T29 | recorder: the owner's playthrough as a complete behavioural record | opened at dispatch | T28 |
| T30 | Q014: how retirements happen, how new players are made, and whether results feed new talent | opened at dispatch | T28 |
| T31 | Q015: how energy falls in a match and recovers between matches | #99 | T28 |
| T32 | Q016: how confidence changes after a match, and against what expected margin | #103 | T31 |
| T33 | Q017: do injuries, cards and friendlies change confidence, and how does team morale follow | #107 | T32 |
| T34 | recorder 2: the keys typed into the game, and the screen/key map they draw | #105 | T29 |
| T36 | Q018: do fitness and confidence change match performance at equal skill | #121 | T35 |
| T37 | Findings F010–F020 meet the pinned citation checker (#95) | #124 | — |
| T38 | M0: the emulator runs whole watched matches, with inputs and a substitution hook | #135 | — |
| T39a | the screen catalogue and the screenshot renderer | #137 | — |
| T39b | the coaching kit: a pause key, live view and notes in the recorder | #138 | — |
| T39c | screens read back from a sitting's video (a test) | #139 | T39a |
| T40 | keeping.py: the keeper gate tests DS:8327 in {3, 4}, not == 0x18 | #126 | — |
| T41 | F020 restates F019's result-term set wrongly; F010 cites a blank line | #127 | — |
| T42 | M1a: the skill reader 0791:278A substituted in whole watched matches | #163 | — |
| T43 | M1b: the strength reader 1771:377E substituted in whole watched matches | #166 | T42 |
| T44 | the recorder keeps one save in flight and merges the key groups that settle while it writes | #128 | — |
| T45 | M2a: the contests a watched match reaches, read from the listing (Q010) | #170 | T43 |
| T46 | M2b: the contest gate 0791:287C substituted in whole watched matches | #172 | T45 |
| T47 | M2c: the draw wrappers 214B:06B1 and 214B:06D0 substituted in whole watched matches | #178 | T46 |
| T48 | M2d: the long helpers 214B:0D56 and 23E4:0279 substituted in whole watched matches | #188 | T47 |
| T49 | Pass one: the competition calendar: the stage builders, the group table, seeding and hosts | #191 | — |
| T50 | Pass one: how a computer team picks its eleven, formation and tactics; computer-vs-computer results | #192 | — |
| T51 | Pass one: when the manager is sacked, the shareware limit, and whether play ever ends | #193 | — |
| T52 | Pass one: what each team tactic changes in a watched match | #194 | — |
| T53 | Pass one: bookings, sendings off, injuries, bans, substitutions: the drafters' readings reviewed as one finding | #195 | — |
| T54 | Pass one: formations and start positions, the 14 position codes, and the foot test | #196 | — |
| T55 | Does a watched match keep a copy of the lineup and restore it? (Q037) | #146 | — |
| T56 | Prompts around a match: how long each waits, the goal-kick taker prompt, the watch-again re-ask, which goals get a replay | #226 | — |
| T57 | The seed families and the fail-closed comparison on the original-match kit (P0a) | #268 | — |
| T58 | The port mode in the kit, with the E032 pilot moved in (P0b) | #269 | — |
| T59 | Guest calls, a decision under a port, and the divergence locator (P0c) | #270 | T57, T58 |
| T60 | The runtime primitives and the geometry queries, ported (P1a) | #271 | T59 |
| T61 | The player attributes (segment 1771), ported (P1b) | #272 | T59 |
| T62 | Ball and player motion, the offside line and the referee, ported (P2a) | #273 | T59 |
| T63 | Positioning, marking and the leaders, ported (P2b) | #274 | T59 |
| T64 | The ball: passing, launching and shooting, ported (P3a) | #275 | T59 |
| T65 | The holder's decisions and the contests, ported (P3b) | #276 | T59 |
| T66 | Duels, play at the ball, the goal and the after-goal swing, ported (P4a) | #277 | T59 |
| T67 | Kick-offs, restarts and set pieces, the walk-off and the booking, ported (P4b) | #278 | T59 |
| T68 | Fouls, cards, injuries and form; substitutions and the computer manager in play, ported (P5a) | #279 | T59 |
| T69 | The commentary and the match frame (9564 to play_match), ported (P5b) | #280 | T59 |
| T70 | The per-match set-up (A4A1 and what it reaches), ported (P5c) | #281 | T59 |
| T71 | run_match and its tail: the man of the match, the group tables, D050, the tactics reset, ported (P5d) | #282 | T59 |
| T72 | The post-match update B7FA and the pool update BA4E, ported (P5e) | #283 | T59 |
| T73 | The display boundary: what is drawn, sounded or waited for, removed or stubbed (UI-a) | #284 | T59 |
| T74 | The manager's decisions in play and a fixture with no managed side, ported (UI-b) | #285 | T59 |
| T75 | The manager's substitutions: SELECT TEAM, the swap and the eleven's check, ported (UI-c) | #286 | T74 |
| T76 | The takers and the shoot-out: the captain and set-piece prompts, extra time, the order and the kicks, ported (P7a) | #287 | T75 |
| T77 | The paths a plain match does not reach (the quick result from a pause, penalties, sendings off, the frontier), ported (P7b) | #288 | T59 |
| T78 | The engine on its own: run_match and the post-match update in Python, no Unicorn (P6) | #289 | T60-T77 |
| T79 | The fidelity sheet: the original's distributions, and the port's against them (sheet A) | #290 | T78 |
| T80 | The end state sealed: the engine in pure Python with no GOAL.EXE bytes at run time (end) | #291 | T78, T79 |
| T81 | Q008 (goal2 T45): when the squad and the reserve pool may exchange records: finals, tours, selection-mode gates | #254 | — |
| T82 | goal2 request (stage 3, G10): a savestate at the new-game screens in the key read, and the interrupts to the first manager menu | #367 | — |
| T83 | goal2 request (stage 3): the start year as an input to the core: a state before the DOS date read, and the path to the title's read | #369 | — |
| T84 | goal2 G13/G16: deliver existing E031/E014 states and identify evidence gaps | #390 | — |
| T85 | goal2 G13: correct mutable DS:066A in the original-match build guard | #396 | — |
| T86 | goal2 G13: collect a nearby original-loaded input for missing decisions | #400 | T85 |
| T88 | goal2 G13: bounded original-key taker/warning inputs and explicit remaining limits | #400 | T86 |
| T89 | goal2 G13: closer retained saves for remaining taker/vacancy inputs | #400 | T88 |
| T90 | goal2 G13: bounded original-key penalty/free-kick search | #400 | T89 |
| T91 | goal2 G13: static and retained-source reassessment of four remaining inputs | #400 | T90 |

| [T92](T92.md) | Controlled synthetic fixtures for #400 |

- [T103a](T103a.md): Tactics and manager-control matrix.
- [T103b](T103b.md): Computer lineup selection and sorting.
- [T103c](T103c.md): Computer tactics and emergency role policy.

- [T105a](T105a.md): Preregister isolated probes and match intervention boundaries.
- [T105b](T105b.md): Preregister seed blocks, precision, stopping and compute caps.
| [T78a](T78a.md) | Plain-memory port dispatcher | #289 | T77 |
| [T78b](T78b.md) | Wire Match to the plain-memory engine | #289 | T78a |
| [T78c](T78c.md) | Checkpoint the plain-memory engine at event boundaries | #289 | T78b |
| [T78d](T78d.md) | Close T78 with strict family and measured runtime | #289 | T78b and T78c |
| [T78b1](T78b1.md) | Residual helper ABI entrypoints | #289 | T78a |
