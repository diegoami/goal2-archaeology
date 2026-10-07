# E015 protocol: one maximally informative sitting

The owner plays once; the project extracts everything (the owner's direction, 2026-10-07). A
savestate is the whole machine state, so a timestamped chain of them — plus the screens they
carry and (between snapshots) the video — is a complete behavioural record any later question is
mined from without new play. The sitting is **not scripted**: everything below is what makes one
sitting maximally informative, not a procedure to follow key by key. A partial chain is a valid
record: start, stop, and restart whenever you like; the recorder and the extraction tolerate it.

## Before

```
bash setup/goal2-runtime.sh        # once: the verified release copy in .cache/goal2
bash runtime/human/play.sh --self-test
```

## The sitting

One command starts everything (from a graphical session, so the game window opens on your
display):

```
bash runtime/human/play.sh --countries …   # see below; --video adds the screen video
```

A windowed DOSBox-X appears, booted from a per-session copy of the verified release. From then
on you simply play. The watcher (invisible) sends the savestate host key **directly to the game
window** (`xdotool key --window`, never a global keystroke — your terminal can keep the focus the
whole time) and stages a timestamped snapshot every 20 s, hashed into the session's index. The
session folder is `scratch/human/sessions/<date-time>/` (git-ignored: the savestates and the
video never enter the repository; only the extracted record does). The sitting is silent: the
config family is the G1 driver's, with `nosound=true`.

What makes the sitting maximally informative (each row of the map below is fed by one of these):

- **Start a new game** (or load one — both are fine; the chain records which).
- **Watch a few matches fully**, and let the match run at a *moderate speed* (the in-match speed
  controls): at top speed a half can pass between two snapshots and the commentary ring can lap
  itself (issue #40's wrap problem). At a moderate speed consecutive snapshots share commentary
  rows, and the screen history shows the lines moving.
- **Quick-result (R) the rest** — seasons move fast and the year-end diffs are the point.
- **Cross year-ends slowly**: play until the season turnover, then pause a moment (a snapshot
  lands within 20 s) and check the news screens. Year-end player-record and squad diffs (Q013,
  Q014) come from the states either side of the turnover.
- **Do transfers / pre-season squad edits** while the recorder runs: squad diffs are read from
  the same states (Q014).
- **Play a knockout cup run to a penalty shoot-out** if the fixture list offers one (F015's
  shoot-out arm has never been watched: `0791:A10A`).
- **Visit the board / news screens** between rounds (Q016, Q017): the screens are captured.
- **Play a World Cup cycle** if you reach one: the stage and fixture bytes of the chain are the
  bot's map of the competition path.
- If you save in-game, the `.GL` save lands in the session's own game-folder copy — it stays with
  the session, never in the release cache.

Stopping: close the game window (or Ctrl+C in the terminal). The watcher stops with it, stages
your last F12+S if one is pending, and writes the session's meta.

## After

```
python3 experiments/E015-human-playthrough/extract.py scratch/human/sessions/<date-time> --countries 1,4
python3 tools/validate_runs.py runs/E015
python3 tools/publish_evidence.py E015 --run E015-r0001 --file <snapshot> …   # the savestates
python3 tools/verify_evidence.py E015
```

`--countries` picks whose records the chain carries: pass the countries you manage (their
numbers as GOAL shows them). The record lands in `runs/E015/`, never overwriting an earlier one.

## The map: open question → what in the chain answers it

| Question | What in the chain answers it |
| --- | --- |
| Q013 ageing / peak age (T28 corroboration) | the player-record diffs across the states either side of a year-end, against the year word `[A923]+0x3A` in the same states |
| Q014 retirements and new players | the same year-end states: squad changes (slot moves) and `players.check` flipping from the start layout |
| Q015 energy through a match | player-record diffs across consecutive states of a *watched* match, before/after side |
| #40 exact commentary identity | consecutive `ui-text` screens of a watched match at moderate speed: commentary rows move between snapshots without lapping the 200-record ring |
| F015 shoot-out arm | states during a knockout match that reaches penalties (`0791:A10A` runs it watched); screens show the shoot-out, records carry the takers |
| #65 R008 tactic bytes across seasons | the country record (`+0x2D` among the 0xBF bytes) of the managed country, season over season |
| Q016/Q017 confidence, morale, board | the `ui-text` of the states where the board/news screens were up |
| the bot's World Cup path | the stage byte `[A923]+0x3C`, fixture index/count `[A923]+0x26/+0x28` across a cycle's chain |

The analysis of any one row is **not** this experiment's: it belongs to the question's own task,
which corroborates its finding against the chain.
