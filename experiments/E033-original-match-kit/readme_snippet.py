#!/usr/bin/env python3
"""E033: the README's "Play a match" loop, as written, on the reference image (goal2's to_savestate and
from_savestate, which this repository does not hold, stand for Image.from_savestate(reference) and the returned
memory component, checked by the build guard): the events, the decisions answered, the memory handed back.

    python3 -B experiments/E033-original-match-kit/readme_snippet.py"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image, Match, Fixture            # noqa: E402
from original_match.assets import reference_image          # noqa: E402

image = Image.from_savestate(reference_image(str(ROOT / ".cache")))
shown = []
want_to_stop = False
t = time.time()
m = Match(image, Fixture(first=7, second=19, index=40), managed=7)
for ev in m.events():
    shown.append(ev)
    if ev.kind == "minute" and ev.minute == 20:
        m.pause()
    if ev.kind == "decision":
        d = ev.data
        if d["context"] == "pause":
            m.answer(tactics={6: True})
        elif d["context"] == "half_time":
            m.answer(substitutions=[(d["eleven"][9], d["bench"][1])])
        else:
            m.answer()
    if want_to_stop:
        blob = m.save()
        break
result = m.result()
after = m.memory_component()
print("events", len(shown), "score", result["score"], "decisions", [(x["context"], x["minute"]) for x in result["decisions"]])
print("refused decisions:", [e.data.get("refused") for e in shown if e.kind == "decision" and e.data.get("refused")])
print("memory component", len(after), "== image", len(image.memory_component()))
print(Image.from_memory_component(after).build_problems(), "problems in the after image")
print("%.1f s" % (time.time() - t))
print(m.over, m.score, m.minute, m.waiting)
print(sorted({e.kind for e in shown}))
