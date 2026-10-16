"""E033 goal2 trial: goal2's own state -> the original's watched match, interactively -> back into goal2's state,
using only goal2's code and the kit vendored as goal2/engine/original_match.

Runs inside a goal2 checkout (here a throwaway clone of goal2 at 6f9da19 in /tmp, never pushed) with
runtime/original_match copied to goal2/engine/original_match and E006-r0001 in .cache:

    python3 -B trial_watch.py          (out/goal2-trial-20261016.txt)"""
import copy
import sys
import time
import zlib

from goal2.game.state import from_savestate, to_savestate, _rewrite_zip
from goal2.engine.original_match import Image, Match, Fixture

TEMPLATE = open(".cache/e0afff6751747233-e006-1000-r0001.sav", "rb").read()

# 1. goal2's state, as its screens leave it: Denmark, the 14th player starts instead of the 11th, tactics changed
state = from_savestate(TEMPLATE)
eleven = list(state.managed_squad[:11])
bench = list(state.managed_squad[11:])
eleven[10], bench[2] = bench[2], eleven[10]
state.managed_squad = eleven + bench
state.starting_eleven = eleven
state.country_tactics = state.country_tactics | 0x20          # element 6, stand ground
print("goal2 state: managed", state.managed_country, "eleven", state.starting_eleven, "tactics", hex(state.country_tactics))

# 2. the image goal2 already makes (to_savestate), the fixture goal2 chooses
image = Image.from_savestate(to_savestate(state, original=TEMPLATE))
m = Match(image, Fixture(first=state.managed_country, second=19, index=40), managed=state.managed_country)

# 3. play: a tactic change at a pause, a substitution at half time; show what happens
t0 = time.time()
paused = False
for ev in m.events():
    if ev.kind in ("goal", "booking", "sending_off", "injury", "substitution", "half_time", "full_time", "tactics", "refused"):
        print(" ", ev)
    if ev.kind == "minute" and ev.minute == 25 and not paused:
        paused = True
        m.pause()
    if ev.kind == "decision":
        d = ev.data
        print("  decision", d["context"], "at", ev.minute, "subs left", d["substitutions_left"])
        if d["context"] == "pause":
            m.answer(tactics={4: False})
        elif d["context"] == "half_time" and not d.get("refused"):
            pos = dict(d["positions"])
            off = d["eleven"][8]
            on = next((w for w in d["bench"] if pos.get(w) == pos[off]), next(w for w in d["bench"] if pos.get(w)))
            m.answer(substitutions=[(off, on)])
        else:
            m.answer()
r = m.result()
print(f"result {r['first']} {r['score'][0]}-{r['score'][1]} {r['second']} in {time.time() - t0:.1f} s; MOTM {r['man_of_the_match_name']}")

# 4. back into goal2's state: the kit's memory after the match and the post-match update
after = from_savestate(_rewrite_zip(TEMPLATE, {"Memory": zlib.compress(m.memory_component())}))
changed = [w for w in state.managed_squad if after.players[w] != state.players[w]]
print("players of the managed squad whose record changed:", len(changed), "of", len(state.managed_squad))
w = state.starting_eleven[0]
print("  e.g. player", w, "energy +0xE", state.players[w][0xE], "->", after.players[w][0xE],
      "form +0xC", state.players[w][0xC], "->", after.players[w][0xC])
print("squad after (the original's order):", after.managed_squad)
print("seeds after:", hex(after.rng_seed_7b62), hex(after.rng_seed_8336))
