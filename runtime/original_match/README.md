# original_match: the original's watched match, played interactively on goal2's state

For a goal2 session. You need nothing of goal2-archaeology but this folder and one image goal2 already fetches.
The match is the original game's own code (`run_match` 0791:F1F6, then its post-match player update 0791:B7FA)
run under Unicorn; this kit answers the original's key reads, at the original's own decision points, with the
keys a manager would press. Nothing of the original is in this folder: its code and data come from the image.

## Get it (once)

1. **Vendor** this folder byte for byte into `goal2/engine/original_match/` and add a PROVENANCE row per file
   (source `diegoami/goal2-archaeology`, the commit you copied, findings F004 F010 F013 F014 F018 F026 F027 F028
   F029 F030, issue 250). Never edit it there; changes come upstream.
2. **unicorn** (approved, goal2 #97): `pip install unicorn` (2.1.x; Debian/Ubuntu: `python3-unicorn`). Only this
   kit imports it, so goal2's quick path keeps working without it.
3. **The image** is goal2's own E006-r0001 (release E006, SHA-256 `e0afff67…657d`, the file
   `tools/measure_p1.py` fetches): `assets.reference_image(".cache")` fetches it with `gh` and checks its hash.

## Know it works

    python3 -m goal2.engine.original_match.check --cache .cache            # about 25 s
    python3 -m goal2.engine.original_match.check --cache .cache --family   # + about 100 s

`engine PASS`: E011-r0001's friendly replayed from the image is the match E021 recorded from the original's own
DOSBox-X run (score, 4,149 ticks, all 182,188 RNG draws by digest, the board, the last 199 commentary lines).
`interactive PASS`: the worked example below, played straight and saved/resumed at minute 60, is the same match
and the one this kit recorded. `family PASS`: E032's ten seeds are E032's records.

## Play a match

```python
import zlib
from goal2.engine.original_match import Image, Match, Fixture
from goal2.game.state import to_savestate, from_savestate, _rewrite_zip

image = Image.from_savestate(to_savestate(state, original=template_bytes))   # goal2's state, as it saves it
m = Match(image, Fixture(first=7, second=19, index=40),   # Denmark v country 19, calendar number 40
          managed=state.managed_country)
for ev in m.events():                                     # events as they happen
    show(ev)                                              # ev.kind, ev.minute, ev.score, ev.data
    if ev.kind == "minute" and ev.minute == 20:
        m.pause()                                         # a manager pressing Enter in play
    if ev.kind == "decision":                             # the original stops and asks
        d = ev.data                                       # context, eleven, bench, positions, injured, ...
        if d["context"] == "pause":
            m.answer(tactics={6: True})                   # stand ground
        elif d["context"] == "half_time":
            m.answer(substitutions=[(d["eleven"][9], d["bench"][1])])
        else:
            m.answer()                                    # play on
    if want_to_stop:
        blob = m.save(); break                            # bytes; Match.load(blob) continues it exactly
result = m.result()          # score, goals, bookings, injuries, substitutions, board, commentary, decisions
after = m.memory_component() # the memory after the match and its post-match update: goal2's next state
next_state = from_savestate(_rewrite_zip(template_bytes, {"Memory": zlib.compress(after)}))
```

`Match(..., players=..., countries=...)` writes record lists over the image's instead (goal2's `GameState.players`
and `.countries` as they are, without the squad order and tactics `to_savestate` applies). E033's
`goal2_trial.py` is this flow on goal2's own code (5.9 s, the result read back by `from_savestate`).

`python3 -m goal2.engine.original_match.example --cache .cache` runs the same kind of match from the reference
image (a pause, a half-time substitution, a save and resume at minute 60; about 6 s).

**Events**: `minute`, `commentary` (the original's line, with its template and players), `goal`, `booking`,
`sending_off`, `injury`, `substitution` (both teams), `half_time`, `full_time` (the board's statistics),
`decision`, `tactics`, `position`, `player_tactics`, `substitution_requested`, `refused`, `end`; `tick` too with
`Match(..., ticks=True)`. `m.pitch()` gives the 22 players' and the ball's positions at any moment (for drawing).

**Decisions** (where the original itself stops for the manager) and what an answer does there:

| context | when | substitutions | other answers |
| --- | --- | --- | --- |
| `half_time` | after the half-time board | made now | tactics, positions, marking, own tactics, quick, speed |
| `substitution` | at a stoppage after an injury to your player, or after you asked for one | made now; the default is what you asked for | as above |
| `pause` | when you call `m.pause()` | asked for: the original offers them at its next stoppage | made now |
| `extra_time` | before each extra-time half (competitive fixtures, which the kit refuses until checked) | made now | as above |

`answer(substitutions=[(off, on)], tactics={element: bool}, positions={player: code}, marking={player: opponent
or 0}, own_tactics={player: {element 1..4: True/False/None}}, quick=True, speed=0..5)`; no argument plays on.
If the original refuses the result (its message, e.g. "Denmark has too many goalkeepers"), the same decision comes
back with `refused` set; answer again. A declined injury notice comes back at every stoppage, as in the original.

## What the original decides for you (rules to know)

- **The seed is the fixture's**: the set-up reseeds the RNG with `index * (year + 1)` (0791:2648), so a fixture
  number plays one match for given teams and answers. `seed=` overrides it at kick-off (a deviation, declared).
- **The match depends on the two teams' records, nothing else in the image** (E033: the stack, the screens zeroed,
  an image taken inside a match with the teams' records restored: the same match). The set-up writes into the
  computer side's records (it sorts its squad and sets its eleven's positions, 0791:BC5D), so **carry the records
  forward**: the next match starts from `memory_component()` of this one, as the original's next fixture does.
- The computer's side is the original's: its lineup, tactics and substitutions. Your country is made the human's
  (`managed=`); the image's former human country is released as the original releases a sacked manager's.
- `speed` changes no match (checked); it is the original's display speed, for goal2 to pace its own display.
- The post-match update runs (energy recovery, form and confidence from the result: F018, F019); the original's
  news pages after a fixture do not. Read the new player bytes from `memory_component()`.

## Limits and costs

Friendlies only (kind 1); competitive fixtures, extra time and the shoot-out are wired but unchecked (about 2 h with
E031's shoot-out state). The set-piece taker prompts keep the original's pick (exposing them: about 1 h). One
human side. A match costs 6-10 CPU s (a quick result after `R`, about 2 s); stepping by minute or tick adds nothing
measurable. `save()` is about 0.3 MB.
