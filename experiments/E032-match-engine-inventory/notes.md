# E032 match-engine inventory: notes and provenance

Made for the match-engine plan (`docs/match-engine-plan.md`, the owner's brief of 2026-10-15,
`docs/briefs/match-engine-plan.md`). It sizes the watched engine, measures what an oracle match costs,
finds which display code a port can leave out, and tries the porting method on one piece. No DOSBox-X run
was taken: every match is the original's own code in the E021 Unicorn harness
(`runtime/emul/watched_match.py`), from E011-r0001's watchstart savestate (Denmark, country 7, against
country 19; SHA-256 `d68e48c734a742a63e707a8c451b9011ef03b452ebd91f239d86f875464e07a9`, verified by
`check.asset` before every run). Packed GOAL.EXE is set `goal2-a949da2f`. Neither original bytes nor
savestates are committed. Python 3.12, Unicorn 2.1.4, capstone 5.0.7. Every writer refuses an existing
output; nothing in `out/` was deleted or overwritten. `out/sha256-20261015.tsv` (hashes.py) holds the hash
of every output written before it.

## Declared inputs

- The main seed `DS:7B62` per match (as E026's arms).
- The delay calibration dword `DS:A9FF/AA01` := 20, written at the first clock tick (`0791:970C` entry) by
  `timing.set_delay_at_kickoff`. Not at the start: the watchstart state resumes inside a delay
  (`214B:1E09`) whose pass counter is already above a small value, so that write never lets it end (two
  runs with the write at the start were stopped by me after about 10 minutes; they left no output). The
  value 1 hangs as well, for a different reason: the whistle `214B:1F87` divides by `A9FF div 10`.
- skip.py and pilot_movement.py substitute routines (Guest.hook), declared in each record.

## Runs and what they show

| what | script | outputs | result |
| --- | --- | --- | --- |
| cost of one plain match | timing.py | `timing-plain-20261015.jsonl`, `timing-plain-8seeds-20261015.jsonl` | 20-51 s CPU per match (the machine was shared) |
| the delay count at kick-off | timing.py `--delay-count 20`, compare.py | `timing-delay20-kickoff-20261015.jsonl`, `timing-delay20-8seeds-20261015.jsonl` | 10 of 10 matches identical in score, ticks, every main-seed draw (digest), the board's raw statistics and the commentary's template counts; 8-17 s per match |
| what a match executes | coverage.py | `cov-s1234-20261015.json` (no delay write), `cov-d20-*-20261015.json` (5 seeds) | 281 routines run between kick-off and full time; 84% of executed instructions are the delay loop `214B:1E09` |
| size by part | analyze.py | `parts-s1234-v3-20261015.md` (superseded, kept: `parts-s1234-20261015.md`, whose UI rule matched `draw_` inside `draw_table_byte` and `skill_draw_passes`; `parts-s1234-v2-20261015.md`, whose list of exactly substituted routines had `214B:0D1C` and `1771:3A06` instead of T48's `23E4:0279`) | engine parts: 190 routines, 13,902 static instructions, 3 substituted exactly before E032 |
| a seed family's reach | union.py | `union-5seeds-20261015.md` | engine parts reach 77-98% of their code bytes over five seeds; 9 routines on the frontier are never reached |
| display boundary | skip.py, skip_batch.sh | `skip-*-20261015.jsonl`, `skip-batch-20261015.txt`, `skip-display-set-20261015.jsonl`, `skip-0791-9372-20261015.jsonl` | removable, alone and together, on 2 seeds: `8F10` draw_ball, `9079`, `0481`, `1829`, `0425` delay, `0441` whistle, `94E8` speaker; `9372` key poll (no key pressed); NOT removable: `8537` (the match never ends) and `8E24` (the match changes) |
| the porting method | pilot_movement.py, pilot_batch.sh | `pilot-exact-try1-20261015.jsonl`, `pilot-exact-8seeds-20261015.jsonl`, `pilot-{coin-swapped,bound-36,no-picture}-20261015.jsonl`, `pilot-batch-20261015.txt` | `8889` + `86D0` and their helpers ported from the listing and substituted without proof: 10 of 10 matches identical (about 93,000 calls each); each of 3 falsifiers changes the match |

## Why 8537 and 8E24 stay

`8E24` moves a sprite on the pitch picture: it restores the cell at the old position from the background
copy `[DS:7C1E]` into the picture `[DS:7C16]` and writes the sprite's word at the new position
(`seg_0791_15.asm` 8E27-8EE5). `8537` does the same for a player, and moves the ball with its holder
(`seg_0791_14.asm` 8537-8F10 call). The move test `86D0` reads that picture: while the clock runs, an
outfield player who is neither `DS:830B` nor `DS:830C` cannot step onto a cell whose attribute is not 0x0D
and whose character is in the set `DS:0648` (`seg_0791_14.asm` 87E8-8855). So the picture is the
occupancy grid, the referee and the offside-line markers (`9119`, `8CF5` through `8E24`) are obstacles, and
a port keeps the picture's characters and attributes (not its look). Read from the listing; the skip runs
and the pilot's `no-picture` falsifier (the match changes) agree.

## Timing of the pilot

Reading the listing of `8889`, `86D0` and the six helpers, writing the port and running it took about 40
minutes; it was exact at the first run. The ported code is about 620 static instructions (`8889` 247,
`86D0` 135, `2BE5` 34, `2DCA` 25, `2CC5` 16, `045D` 15, `2974` 14, the set test and the two draw wrappers).
With the port hooked, a match takes 16-20 s instead of 8-17 s (93,000 Python calls).
