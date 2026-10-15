# E031 play-the-game

Playing the original for years under the driver, like a half-decent manager, to write the guide
[`docs/play-guide.md`](../../docs/play-guide.md) and to show that a run does not get stuck. Brief:
[`docs/briefs/play-the-game.md`](../../docs/briefs/play-the-game.md) (the owner, 2026-10-15). Not a
research experiment with hypotheses: its outputs are the guide, the session logs and the saved games.

- **Artifact**: set `goal2-67cf27d6` (`bash setup/goal2-runtime.sh`), variant none.
- **Runtime**: `runtime/driver/driver.py` (DOSBox-X 2024.03.01, Xvfb on a private display the driver
  picks, never `:99`), `cycles=fixed 8000` (the owner's pace), through `play.py`'s `PlayDriver`:
  function keys as raw XTEST events (`xtest.py`), the mapper `mapper-nohost.map` (written by
  `make_mapper.py` from DOSBox-X's own default binds: savestate on Scroll Lock, screenshot on Pause,
  load on Print Screen; no F12 host chord), saved games copied into the game folder before the launch
  (`--gl`). Maximum intervention: I2 (savestates for every screen read; no memory is written).
- **Method**: one server per session (`start.sh S`, a systemd user unit `goal2-play-S`) holds the
  emulator; the client sends keys and reads the screen (`play.py`). Decisions are taken from the
  screens: squad condition by `scan`, picks by `find`, rounds as quick results by `round` (or
  `rounds.sh`), watched matches by `watch`. The game is saved with its own F7 at each milestone.

## Outputs

- `out/<S>/steps.jsonl`: every request, append-only: host UTC, the request, the screen digest after
  it, whether it changed, the reads it took, and the game's progress bytes from the same savestate
  (`season` = `[A923]+0x38`, `stage` = `+0x3C`, `fixture`/`fixtures` = `+0x26`/`+0x28`, `delay` =
  `+0x3F`, `replay` = `+0x41`; E014 notes, F005, F030).
- `out/<S>/screens.jsonl`: the text of every distinct screen, once, keyed by digest
  (`screen.py S STEP|digest` prints one; `replay_log.py S --row R` lists one row after each step).
- `out/<S>/progress.md`: `progress.py S --md out/S/progress.md`: the launches, every stage and season
  change and every full-time board of the managed team, each with the step that shows it.
- `out/saves.tsv`: every saved game kept (`keepsave.py`): name, size, sha256, what it is. The files
  are in `.cache/kept/E031/saves/` (git-ignored: a `.GL` holds the game's data) and go to the
  release `goal2-saves` with `tools/fetch_saves.py --add`.
- Savestates of `checkpoint` and screenshots of `snap` are in `.cache/kept/E031/<S>/`, named by step;
  their sha256 is in `steps.jsonl`.

Sessions: `t1`..`t8` are the trials that found the key and help-viewer faults (section 2 of the
guide); `run1` is the first Holland game, abandoned when the function keys turned out dead; `g1` is
the game the guide is written from; `mp` a two-player trial (Denmark and Scotland: "next player",
one round, F5); `chk` a fresh launch that loads `G5A.GL` from a list of two saves and shows its
history.

## The plan, as carried out

1. A tool to play by hand from the shell (one emulator per session, keys in, screen and progress
   bytes out, every step logged), then fix whatever stops a human's keys from working under it.
2. A new game (Holland, one player), every menu option and F-key, a save, a quit and a load.
3. The first match watched, with squad work before it (pool picks, a rename, repositioning, player
   and team tactics) and a substitution; the rest of year 1 as quick results with the squad checked
   between rounds; the last match watched with in-match changes.
4. Years 2 and 3 with a different formation each (3-5-2, 4-3-3, back to 4-4-2), the assistant's 20,
   a saved goal and a saved summary loaded back, the replay toggle, injuries; a save at every
   milestone, kept and hashed.
5. Then on through year 4 (the World Cup) into year 5, because the brief's "years" turned out to be
   the stages of a four-year cycle and the knockout stage held the screens no other year has (extra
   time, the shoot-out order).

## What g1 did (2026-10-15, 19:42 to 21:20 UTC)

`out/g1/progress.md` has every match and stage change with its step. In short: year 1 (2028 Euro
qualifying, stage 2) 12 matches, second in group F behind Eire, out; year 2 (stages 3-4) nine
friendlies; year 3 (2030 World Cup qualifying, stages 5-6) second in group H, qualified; year 4
(stages 7-8) five friendlies, the World Cup group (2nd), last 16 won on penalties after 2-2 (watched),
quarter-final won, semi-final lost, third place won on penalties after extra time; year 5 (2032,
stage 2) begun. The game's own history in `G5A.GL`: 2027/28 EC 9 won 7 drawn 5 lost, 2029/30 WC 12
won 4 drawn 6 lost, third. Saves: `out/saves.tsv` (17 files, release `play-the-game-saves`).

## Checking a claim

`python3 experiments/E031-play-the-game/progress.py g1` lists the matches and the year changes;
`screen.py g1 <step>` shows the screen behind any line. A saved game can be loaded in the original
(title `Y`, its name) to see the year and the results it holds (team info, history, tournament).
