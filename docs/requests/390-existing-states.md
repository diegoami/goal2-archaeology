# Existing original states for goal2 G13/G16 (#390)

Delivery for [#390](https://github.com/diegoami/goal2-archaeology/issues/390), task
[T84](../tasks/T84.md). Importance high; inventory cost low. This mines existing evidence;
it makes no new game-rule finding and runs no new campaign. The findings below retain their
**proposed** status. No original bytes belong in either repository's Git history.

## Pull and verify

The 21 files in [the inventory](../../notes/390/inventory.json) are copied unchanged into the
owner's [private delivery folder](https://drive.google.com/drive/folders/19VahGbhN6YPiREXZ0uPAZbf7sCErSCLY)
at `goal2-archaeology/390-existing-states-20261023/`, relative to
[the owner artifact folder](https://drive.google.com/drive/folders/12fgdrQUQB4pHdq0ibY-NP-aU8jgNaRzc).
Each inventory row supplies the exact filename, SHA-256, size, original meaning, source path,
full immutable source commit, and rclone path. The sources are E031's `play-the-game-states`
and `play-the-game-saves` releases and E014's evidence release. Drive copies are the delivery
route; the existing release assets were neither replaced nor removed.

```sh
rclone copy goal2drive:goal2-archaeology/390-existing-states-20261023 .cache/390/assets
python3 notes/390/inventory.py --assets .cache/390/assets --check notes/390/inventory.json
```

Expected: `21 artifacts verified; shootout screen, key wait and caller frame match`.
This checks the actual file content, not a remote checksum label. `inventory.py` reads the
shootout screen, CPU and memory without executing the guest or changing it. It uses F001's
reader and E021's CPU layout. The reconstruction of the game's key-read frame follows
`214B:08DD`'s prologue/Intr arguments (`code/seg_214B_02.asm`) and goal2's existing
`goal2/core/runner.py` R1; BIOS register EBP is not a game frame pointer.

## What is available

| Requested case | Existing evidence and deliverable | Limit |
| --- | --- | --- |
| World Cup groups/bracket | E031 `G4A.GL`, `G4B.GL`, `G4C.GL`, `G4D.GL`; all 17 E031 campaign saves are delivered. F023 describes the builders. | These are game saves, not stops at `9567`. The desktop's original-key `.g2core` inputs already supplied the precise frames and were merged in goal2 #343, per #390. Do not extrapolate the continental frame. |
| Corner / goal-kick taker | E031 g1 steps 1552 / 2630, C43/C43b; F029/F030 identify `0791:CC7B`. | Screen observations, **no corresponding E031 kept savestate found**. |
| Extra time / its half time | E031 g1 3830 / 3851, C47/C47b; static `9B0C` / `9B5B`, shared `ED8A` menu. | Screen observations, **no checkpoint retained at either menu**. |
| Shootout announcement | E031 g1 checkpoint 3874, C48; delivered `3ea57029282b849f-g1-03874-shootout-start.sav`. | A real in-match savestate immediately before choosing the order, not an order already chosen. |
| Shootout order and sudden death | E031 g1 3876 / 3884 (C48b/c), 4611–4617 (C49–C49d); `9B93`, F015 and E034 notes. | The order itself and sixth kicks are logged screens, not separately kept states. The announcement checkpoint is the available resume input. |
| Pause | Desktop supplied `g13-78a03f2f42b4c68b-round-pause.g2core` with its full hash and frames on #390. | Already delivered there; not duplicated in this inventory. |
| Managed retirement / replacement | E031 g1 2390 / 2394 (Nicholls → Bolton, C56/C56b), 2560 (Kelso, C57), 3421 (C57b); `G2C.GL` / `G3A.GL` span the first retirement. | Original observations corroborate the visible event, not a captured instruction-by-instruction identity/RNG trace or isolated replacement before/after pair. |
| Ageing, squad plus 80 pool | E031 `G1E.GL` / `G2A.GL` span year 1→2; E014 states and records below; F016. | E014 captured three computer squads, **not the managed 100**. No new 100-player managed-boundary measurement is claimed. The desktop's T111 has that separate evidence. |
| E022 messages / EA09 vacancy | `0791:E022` and `EA09`, F029 and listing. | No retained instance located for E062 “There is no player here”, E19F “Nice try”, or EC60 vacancy. Here E022 means the routine, not either experiment named E022. |

E031's g1 log has only two explicit `checkpoint` requests: step 247 (first-match menu) and
3874 (shootout announcement). Only the latter appears in its published state table. The old
`.cache/kept/E031/` checkpoint directory is absent locally. The search also covered the current
archaeology/goal2 caches, `goal2-keep` filenames/content-addressed hashes for E014's missing
captures, E031's published tables/releases, and Drive's archaeology checkpoint folder listings.
This is an inventory of located evidence, not proof that no other owner backup exists.
F030's owner sittings r0013/r0017 record captain screens (280 / 202); F029's squad comparison
includes the owner's note about typing C at the captain/goal-kick prompts. Those observations
do not provide the missing E031 corner/goal-kick savestates.

## Shootout checkpoint: exact stop and frame

Source g1 log commit: `c601ecc7219b165de09d955e45a6eece5f4ab2c0`.
SHA-256: `3ea57029282b849fd3114a995178f35e48c420c768f0702b9d3b7d48600dc1fc`.
Screen digest: `b4406ce687da4b2cbff84104287686bcf25a2230fbeb10c74fd08a0f5f5ba0cd`.
The screen says `penalty shoot out  PRESS ANY KEY`, Belgium 2–Holland 2, LAST 16.

The saved CPU is inside BIOS at `F000:CFA6`, SS `3875`, SP `3CF2`; its EBP is `FEFE`.
The validated `08DD` frame is BP `3D1A`, returning to `214B:098A`. Its caller's BP `3D20`
returns to `214B:054E`; message-box BP `3E7A` returns near to `0791:A137`, immediately after
`A132 call far 214B:04F8`. The parent BP is `3EA6`, the shootout's `A10A` frame.
The inventory retains the raw register numbers for checking these normalized addresses.

The game record has season word 1, stage 8, fixture index 2392, count 2393; countries at
`DS:9B34/36` are 20/3 (Belgium/Holland); main RNG word `DS:7B62` is 5479. These are
observations of this artifact, not constants for other games. The saved caller identifies
the announcement independently of matching the screen text.

## Existing prompt contracts for the core

These are existing listing readings, not newly measured defaults. Read the named view first:
`named/seg_0791_10.c` (`CC7B`), `named/seg_0791_09.c` (`9B0C`, `9B93`, `A10A`),
`named/seg_0791_13.c` (`ED8A`), then the corresponding raw code below. Source pin for this
delivery's listings is archaeology `255de405b9c6a730960dcae23ed423ae433ad9f5`.

| Decision | Normal stop, fields, accepted inputs and default |
| --- | --- |
| Captain / set-piece taker (`CC7B`) | F030: `CC2E(1000)`, poll `CC4F → 214B:0723`; after the wait, `CED9 → 0723`, optional key read `CEE8 → 08DD` (return CEED). Role `[bp+4]`, side `[bp+6]`, highlighted squad slot word `[bp-5]`, selected player word `[bp-7]`; stored pick `DS:9976 + 10*side + 2*role`. Roles 1 captain, 2 corner, 3 penalty, 4 free kick, 5 goal kick. Up/Down move highlight; Enter picks if available; C computes/picks and exits; Esc preserves current pick. Space on a taker shows the board and performs a further `08DD` at CF35 (return CF3A). No key for 1000 polls retains current pick; other keys restart the wait. Nominal 10 s depends on calibration; never turn it into a fixed host-clock promise. |
| Extra-time menus (`9B0C`, `9B5B`) | Both call shared `ED8A(1)` when `DS:80FD` is set (returns 9B42 / 9B70). Shared menu key read `EE9A → 214B:1560` (return EE9F); that helper calls `08DD`. Menu selection word `[ED8A bp-7]`, side byte `[bp-2]`, country word `[bp-5]`. Existing F005/F016/F029 menu contract: cursor navigation and Enter select tactics, players, tournament, board or play; Space opens players; Insert toggles replay. Exit still requires `EA09`'s valid eleven. These are blocking reads, not the taker timeout. `9B0C` sets clock `831B=31`, `831F=89`, `8319=15`; use the callers to distinguish phase from a visually similar ordinary half-time menu. |
| Shootout announcement (`A10A`) | Message-box read `214B:098A`, any key; call A132, near return A137. The supplied checkpoint proves this stop. No timed automatic dismissal is shown by the message-box call. |
| Managed shootout order (`9B93`) | `9D62 → 214B:1560`, return 9D67. Highlight word `[9B93 bp-6]`; parent A10A BP passed at `[bp+4]`; side byte `[parent-1F]`; Pascal byte-string order at `[parent-1A + 12*side]`, length then pitch-slot bytes. Up/Down navigate available unchosen players, Enter appends, Esc removes the last pick when nonempty. Enter pushes back Down (`9E5B → 214B:0993`). Completion requires as many picks as available players among slots 1..11; this is **not just a five-player selection**. There is no timed/computer default in this managed-order loop. Do not drop the pushed-back key. |

Static references: `code/seg_0791_20.asm` CC2E–D010, `code/seg_0791_16.asm`
9B0C–A258, `code/seg_0791_23.asm` ED8A onward, `code/seg_214B_03.asm` 1560;
[F030](../../findings/F030-replay-save-goal-and-summary-prompts-wait-6-s-nominal-and-default-to-no-the-taker-prompt-10-s-and-keeps-its-pick-watch-this-match-never-times-out.md),
[F029](../../findings/F029-a-substitution-persists-the-squad-list-is-the-only-copy-and-nothing-restores-it-at-full-time-or-at-the-next-set-up.md),
[E034 notes](../../experiments/E034-kit-competitive/notes.md).

## Lifecycle evidence and its limits

[F016](../../findings/F016-ageing-peak-band-and-yearly-writes.md) and
[F017](../../findings/F017-retirement-creation-and-results-to-talent.md) already separate
continuing ageing, computer recreation and managed replacement. The delivered E014 states are:

| Filename | Meaning |
| --- | --- |
| `3789d8490d2b42d8-e006-2100-r0005.sav` | E014-r0001's published original E006 input. |
| `fd9469da4d0e2955-e014-s1-y0.sav` | E014's published initial campaign state, stage 2. |
| `291d0eb3b0dcec34-e014-cal3-y1.sav` | r0005's first annual after-state, stage 3; r0006's published input. |

The immutable complete r0005 record is at `e3016f41acc025d5c76cac7e469e8c42fe68d5bb`;
r0006 at `3a229bd77882401425509b786f2a572627838889`. Each record also records its
**producer** `code_commit`, which differs from the later commit storing the completed record.
The five consecutive yearly pairs compare 300 computer-player identities, with 262 continuing
and 38 recreated records (F016/F017). F017 recovers one RNG entry word per pair by exhaustive
search; these are inferred RNG words, not directly captured gate-entry registers.

The following captures are **named and hashed in records but their savestate files were not
located** in the release inventory or searched local retained stores. The records' extracted
computer-player bytes remain available; do not advertise the missing files as downloadable:

| Capture | SHA-256 |
| --- | --- |
| r0005 `e014-cal3-y0`, stage 2 | `e7c03379b69e565a18e677be9c56f161910abcd6eb0ed97b8f288b85bb52d03b` |
| r0006 `e014-c1-y0`, stage 3 | `e8ac6fab30987ffbe0821fba6f3f5c68cbcf62ba73e94083d9b4b1aaf0553535` |
| r0006 `e014-c1-y1`, stage 5 | `22d852905bf1364823d5d0c3cc33a8989185eda0405aa63ba7de44ff2a8f0fcf` |
| r0006 `e014-c1-y2`, stage 7 | `f44fa4f4dbf9f8784888c053387af2815ffaefdc50be42d4a85d545d26528681` |
| r0006 `e014-c1-y3`, stage 2 | `5ebe27b29bf8a3939dab2f53584f0c751994683e47104ae0066ecf6326dfc9fa` |
| r0006 `e014-c1-y4`, stage 3 | `6cf4ac60471dee887efa60b24ac9c658de65e1617ee9e6b67dc0a1e9da39ee78` |

E031 gives independently observed managed retirements, but its before/after `.GL` saves bracket
ordinary play and menu activity; they do not isolate the RNG or prove all record writes. F017's
managed path is statically `000E:57E5 → 56F3 → 54F0`: one replacement between fixtures, new
record identity and cleared old record, unlike computer recreation in place. The known result →
ranking → country rating → new-player +3 chain is static; this delivery adds **no measured
ranking change causing a quality change**. The existing desktop T111 annual/retirement proofs
remain separate corroboration, rather than being re-labelled E014 evidence.

No long campaign or new recording is required to use the supplied shootout checkpoint. Missing
taker/extra-time/vacancy states remain collection gaps; the static contracts give goal2 the
current assumption and its limitation without claiming those gaps closed.
