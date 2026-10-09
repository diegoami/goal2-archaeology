# E015 protocol: one maximally informative sitting

The owner plays once; the project extracts everything (the owner's direction, 2026-10-07). A
savestate is the whole machine state, so a timestamped chain of them — plus the screens they
carry and (between snapshots) the video — is a complete behavioural record any later question is
mined from without new play. The sitting is **not scripted**: everything below is what makes one
sitting maximally informative, not a procedure to follow key by key. A partial chain is a valid
record: start, stop, and restart whenever you like; the recorder and the extraction tolerate it.

## Before

```
bash setup/goal2-runtime.sh            # once: the verified release copy in .cache/goal2
bash runtime/human/play.sh --self-test
```

## The sitting

One command starts everything (from a graphical session, so the game window opens on your
display):

```
bash runtime/human/play.sh [--video] [--quit-after SECS] [--res WIDTHxHEIGHT]
```

The recorder's `--countries` argument does not exist; country selection is an extraction
parameter (rework round 2 R15: `--countries 1,4` is passed to `extract.py`, not to `play.sh`).
A Xephyr window contains DOSBox-X on a private nested display, booted from a per-session copy of the verified release. From then
on you simply play. The watcher (invisible) sends the savestate host key **directly to the game
window** (explicit XSendEvent, never a global keystroke — your terminal can keep the focus the
whole time) and stages a timestamped snapshot every 20 s and after a key burst's 0.5 s quiet interval, hashed into the session's index. The
session folder is `scratch/human/sessions/<date-time>/` (git-ignored: the savestates and the
video never enter the repository; only the extracted record does). The sitting is silent: the
config family is the G1 driver's, with `nosound=true`.

The logger listens only on that nested display. It writes press/release events,
UTC and monotonic timestamps, keycodes and base keysyms to `keys.jsonl`, flushed
per line; it never attaches to the outer desktop. The key log stays out of git.
The burst interval is [designed], not a measured game timing: T29's timings and
the T34 brief were searched, and neither specified a human typing interval.

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
  the same states (Q014). Pick a player from the pool into your country, drop one out, change
  tactic bytes (R008, open finding #65) and the captain/penalty/corner presets (F015's reading
  paths), watch the squad slots move.
- **Play a knockout cup run to a penalty shoot-out** if the fixture list offers one (F015's
  shoot-out arm has never been watched: `0791:A10A`).
- **Reposition a player on the pitch** (national repositioning: F008's +6/+7 written live),
  with the watched match's states either side of the move.
- **Take a corner / a penalty / make a substitution** during a watched match (F015's reading
  paths; Q09.5 replays).
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
python3 tools/publish_evidence.py E015 --run E015-r<nnnn> --file <snapshot> …   # the savestates
python3 tools/verify_evidence.py E015
```

`extract.py <session-dir>` is positional; it accepts `--countries` (the countries whose records
the chain carries — pass the ones you manage, their numbers as GOAL shows them), `--runs-dir`,
and `--machine`. The record lands in `runs/E015/`, never overwriting an earlier one
(`O_CREAT|O_EXCL`, rework round 2 R2).

The key map identifies screens by SHA256 of their UTF-8 decoded text, not their
attributes, and associates each ordered key burst with the nearest preceding
snapshot and first snapshot after the quiet interval. It does not assert that
each individual key caused the eventual screen. Missing bracketing snapshots
are counted as unmapped presses. `extract.py` carries the map as a JSON
observation in the sitting's one run/1 record (T34 review R5: there is no
separate map-writing step; `keymap.py <session>` merely prints the summary and
table again from the session). A readable `<run-id>-keymap.md` table sits beside
this protocol, written from `keymap.py`'s output. Raw events
may be included with `--scripted-keys` only for scripted acceptance sittings.

## The living coverage map

The owner plays unscripted, and the map below is how the project's main session reports what one
sitting filled and what remains. Each row is a knowledge item the project will eventually need:
the byte (or set of bytes) in guest memory, the open question or finding it belongs to, the
coverage status, and the named session that fills it. The map is updated after every sitting.

Coverage statuses (the project-recognised vocabulary):

- **static-known** — the byte location and reading rules are confirmed by static analysis (one of
  `static/goal-exe/named/`, the decompiled listings, or an annotation row); no behavioural run
  needed for the location; a run may still be wanted to corroborate a value.
- **corroborated** — a behavioural run confirmed the static answer; named session cited.
- **needs-play** — no static answer; the row will be filled the first time the owner happens to
  act on the item during a sitting.
- **covered-by-a-named-session** — a sitting already captured it; the record's id is cited.

| Knowledge item | Byte / observation | Question / finding | Status | Named session |
| --- | --- | --- | --- | --- |
| Selection picks and drops (the pool into the squad, out of it) | country record `c` at `[A917]+c*0xBF`: the squad, 20 words at `+0x00..+0x27` (fields.tsv `country 0x00 squad`; F007, F008); a pool player's record `+0` (country) | F011's pool, Q014 | static-known | E015-r0001 (initial layout) |
| Repositioning on the pitch (national, between matches) | player record `+6` (position) and `+7` (club position) at `[A91B]+n*0x14` (F008); the squad words' order, sorted by `+6` in `1771:52CC` (F010) | F008, open finding | needs-play | — |
| Team-tactic changes | country record byte `+0x2D`, R008, the default team tactic set (F010; fields.tsv `country 0x2D`); a player's own overrides of elements 1..4 in player record `+0xF` (F010) | #65 R008 | static-known | E015-r0001 |
| Captain / penalty / corner presets | not established: no finding names a stored byte for them (F015 ranks the shoot-out takers by the derived penalty skill, element 12, rather than reading a stored choice); found by diffing the states either side of the owner setting one | F015 | needs-play | — |
| Transfer promise line | `000E:544D` (the screen line "the transfer promise") | Q014, open question | needs-play | — |
| Training / fitness recovery | player record `+0xC` morale, `+0xD` fitness, `+0xE` energy (F008's record layout) across consecutive states between matches | Q015 | needs-play | — |
| Watched-match substitutions | player record changes between states either side of a substitution key | Q09.5 | needs-play | — |
| Watched-match replays | screen-history of a watched match with replays on (commentary ring position) | Q09.5, #40 | needs-play | — |
| Knockout shoot-out arm | the screen + takers' records during `0791:A10A` | F015 (follow-up) | needs-play | — |
| Year-end player-record diffs | states either side of a year end: the stage byte `[A923]+0x3C` entering 2, 3, 5 or 7, the season word `[A923]+0x38` (E014 notes, T28, PR #91; `+0x3A` is the new game's base year and does not move) | Q013 (T28 corroboration) | static-known | E015-r0001 (state words present) |
| Year-end squad diffs (retirements, new players) | squad words `+0x00..+0x27` either side of the same year ends, `players.check` flipping from the start layout | Q014 | static-known | E015-r0001 (initial layout) |
| Energy through a watched match | player record `+0xE` energy and `+0xD` fitness (F008's layout) across consecutive states of a watched match | Q015 | needs-play | — |
| Exact commentary identity | consecutive `ui-text` screens of a watched match at moderate speed | #40 | needs-play | — |
| Board / confidence / morale | `ui-text` of the states where the board/news screens were up | Q016, Q017 | needs-play | — |
| Bot's World Cup path | stage `[A923]+0x3C`, fixture index/count `[A923]+0x26/+0x28` across a cycle's chain (E014 notes, T28, PR #91) | bot input | needs-play | — |
| Scripted opening-screen key burst | shell/mount text → title text after `a`; nearest snapshots bracket the burst, not proof that `a` caused the boot transition | T34 recorder/map acceptance | covered-by-a-named-session | E015-r0004, E015-r0005, E015-r0006; their `<run-id>-keymap.md` tables |
| Scripted title-screen key burst | title text → same title text after `b`/`c`; burst captures per key group (0.5–1.5 s human-paced gaps), all press/release events recorded, outer-app `x/y/z` absent while xev and an outer raw reader prove they were really typed | T34 recorder privacy and timing | covered-by-a-named-session | E015-r0004, E015-r0005, E015-r0006 |
| Screen-flow controls during normal play | `C`, `N`, `Insert`, and recovery keys on the relevant screens; the scripted acceptance keys do not visit those screens | T34 screen/key map; T28 EA09 stall | needs-play | — |

After a sitting, the main session appends a row per knowledge item the chain covered, with the
session's run id (e.g. `covered-by-a-named-session — E015-r0001` for the items the first sitting
already captured), and moves the relevant `needs-play` rows to `covered-by-a-named-session` once
the next sitting captures them. The map is the project's way of saying which facts still depend on
the owner's normal play, not on scripted scenarios.

The analysis of any one row is **not** this experiment's: it belongs to the question's own task,
which corroborates its finding against the chain.
