#!/usr/bin/env python3
"""T39b in-place mutation proofs for the pause rules: each mutation replaces one exact string (it
must occur exactly once) in one source, runs the T39b tests (tests.test_human_pause and
tests.test_human_coach), and writes the source's saved bytes back in `finally`, failing or not. A
mutation the tests still pass is a survivor; the script exits 1 when there is one.

    python3 experiments/E015-human-playthrough/mutate_pause.py [--before]

`--before` is the fail-before proof instead: recorder.py, keymap.py and extract.py are written
back to their origin/main bytes (the tree before T39b) in place and note.py and live.py (new in
T39b) are taken away, the T39b tests run, and every test must fail or error; every file is
written back in `finally`."""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = "runtime/human/recorder.py"
MAP = "experiments/E015-human-playthrough/keymap.py"
EXT = "experiments/E015-human-playthrough/extract.py"
TESTS = ["tests.test_human_pause", "tests.test_human_coach", "tests.test_human_resume"]
MUTATIONS = [
    ("loop: the pause is not read after key events or periodically", REC,
     "if self.pause_probe is not None and (drained or now >= next_pause_poll):", "if False:"),
    ("loop: the pause is not read again before a send", REC,
     "if self.pause_probe is not None and self.poll_pause():", "if False:"),
    ("loop: no paused branch (cadence not skipped, no sleep while paused)", REC,
     "                if self.paused:\n                    # no save request while paused",
     "                if False:\n                    # no save request while paused"),
    ("loop: no resume snapshot", REC,
     "send_resume = self.resume_due and now >= last_event + EVENT_SETTLE_S", "send_resume = False"),
    ("loop: the resume request leaves the pause's key groups pending", REC,
     "burst.groups.clear()", "pass"),
    ("capture: resends whatever the pause", REC,
     "and (self.paused or (epoch is not None and epoch != self.pause_epoch))):", "and False):"),
    ("capture: resends after a pause began (epoch ignored)", REC,
     "and (self.paused or (epoch is not None and epoch != self.pause_epoch))):",
     "and (self.paused)):"),
    ("capture: resends while paused", REC,
     "and (self.paused or (epoch is not None and epoch != self.pause_epoch))):",
     "and ((epoch is not None and epoch != self.pause_epoch))):"),
    ("poll_pause: the epoch is not bumped", REC, "self.pause_epoch += 1", "pass"),
    ("capture: a write after a later pause is taken as the request's own", REC,
     "if (after_pause is not None and events is not None and events > after_pause):",
     "if False:"),
    ("tick: a lost attribution off the pipeline is not caught", REC,
     "        except _AttributionLost as e:\n            # T39b: a write after a pause",
     "        except ZeroDivisionError as e:\n            # T39b: a write after a pause"),
    ("poll_pause: the write count at the pause is not kept", REC,
     'self._write_state()[1] if hasattr(self, "activity") else None)', "None)"),
    ("poll_pause: pauses.jsonl not written", REC,
     'with open(self.pauses_path, "a", encoding="utf-8") as f:',
     'with open(os.devnull, "a", encoding="utf-8") as f:'),
    ("poll_pause: a resume does not make the snapshot due", REC,
     "self.resume_due = True", "pass"),
    ("mapper: F12+P not bound to pause", REC,
     """'hand_pause "key 72 host" "key 19 host" '""", """'hand_pause "key 72 host" '"""),
    ("mapper: F12+P left on the screenshot", REC,
     """'hand_scrshot "key 19 host" ': 'hand_scrshot '""",
     """'hand_scrshot "key 19 host" ': 'hand_scrshot "key 19 host" '"""),
    ("mapper: the default file's hash not checked", REC,
     "if sha256(data) != MAPPER_DEFAULT_SHA256:", "if False:"),
    ("new_session: no mapper file written", REC,
     '(session / "mapper.map").write_text(mapper)', "pass"),
    ("window_paused: the title is not read", REC,
     "return PAUSED_TITLE in p.stdout", "return False"),
    ("map: a paused span counted as time", MAP,
     'monotonic_s=e["monotonic_s"] - paused_before(e["monotonic_s"], pauses))',
     'monotonic_s=e["monotonic_s"] - 0)'),
    ("map: a pause removes its whole span from keys inside it", MAP,
     "max(0.0, min(t, hi) - lo)", "max(0.0, hi - lo)"),
    ("map: a pause the sitting ended in is dropped", MAP,
     "    if start is not None:\n        spans.append((start, end))",
     "    if False:\n        spans.append((start, end))"),
    ("map: the session's pauses.jsonl is not read", MAP,
     "requests=requests, pauses=pauses)", "requests=requests)"),
    ("extract: notes and pauses not placed (all at the end)", EXT,
     "while marks and (i == len(states) or mark_before(marks[0], times[i])):",
     "while marks and i == len(states):"),
    ("extract: placement ignores the monotonic clock", EXT,
     'if mark["clock"] == "monotonic" and when["monotonic"] is not None:', "if False:"),
    ("extract: placement ignores UTC", EXT,
     'return at is not None and when["utc"] is not None and at < when["utc"]', "return False"),
    # Scope 5-8 (the amendment of 2026-10-11; Done-when 4)
    ("loop: F12+P while paused is not watched", REC, "self.resume_chord(drained)", "pass"),
    ("chord: a P before the pause was seen counts", REC,
     '                  and e["monotonic_s"] > self._pause_since\n', ""),
    ("chord: F12 not required", REC, "and self._f12_down and self.paused", "and self.paused"),
    ("chord: no debounce", REC,
     'e["monotonic_s"] > self._inject_time + RESUME_DEBOUNCE_S', "True"),
    ("chord: F12 never released", REC,
     'self._f12_down = e.get("event") == "press"', "self._f12_down = True"),
    ("poll_pause: the recorder's resume not marked", REC,
     'line["by"] = "recorder (F12+P)"', "pass"),
    ("key log: injected keys not marked", REC, 'event["by"] = "recorder"', "pass"),
    ("key log: no count on the injected keys", REC,
     "if want and want[0] > 0 and now <= want[1]:", "if want and now <= want[1]:"),
    ("key log: no deadline on the injected keys", REC,
     "if want and want[0] > 0 and now <= want[1]:", "if want and want[0] > 0:"),
    ("inject: the window is not focused", REC,
     'ok = xdotool(["windowfocus", str(wid)], env=env).returncode == 0', "ok = True"),
    ("inject: the key log is not told", REC,
     '    if keys is not None:\n        keys.expect_injected("Pause")\n', ""),
    ("loop: the recorder's keys make bursts", REC,
     'drained = [e for e in drained if e.get("by") != "recorder"]', "drained = drained"),
    ("map: the recorder's keys counted as the owner's", MAP,
     'events = [e for e in events if e.get("by") != "recorder"]', "events = list(events)"),
    ("title read: a timeout crashes the loop", REC,
     "    except subprocess.TimeoutExpired:\n        return None          # an unanswered",
     "    except ZeroDivisionError:\n        return None          # an unanswered"),
    ("loop: a dead key logger raises (the 215411 end)", REC,
     "                    self.log(self.stop_cause)\n                    break",
     "                    raise RuntimeError(self.stop_cause)"),
    ("play: a closed window is not named so", REC,
     '        else:\n            reason = "window-closed"',
     '        else:\n            reason = "quit-after"'),
    ("play: an error writes no end", REC,
     'meta.update({"ended": host_times(), "stop_reason": f"error: {e!r}"})', "pass"),
    ("load: the default copies none", REC,
     "src = Path(load) if load else newest_saved_game(Path(session).parent, exclude=session)",
     "src = Path(load) if load else None"),
    ("load: the oldest, not the newest", REC,
     "max(found, key=lambda p: p.stat().st_mtime_ns)", "min(found, key=lambda p: p.stat().st_mtime_ns)"),
    ("load: --fresh ignored", REC,
     '    if fresh:\n        return {"fresh": True, "file": None}',
     '    if False:\n        return {"fresh": True, "file": None}'),
    ("load: no sha256 recorded", REC,
     '"bytes": len(data), "sha256": sha256(data),', '"bytes": len(data), "sha256": None,'),
    ("load: --load ignored", REC, "src = Path(load) if load else", "src = None if load else"),
    ("main: no subcommand does not play", REC, "if not argv or (", "if argv and ("),
    ("extract: the placed saved game is not declared", EXT,
     '    if load.get("file"):\n        rec["interventions"].append(',
     '    if False:\n        rec["interventions"].append('),
    ("extract: --declare dropped", EXT,
     '        rec["interventions"].append({"level": level.strip(), "what": what.strip()})', "        pass"),
    ("extract: the recorder's presses counted as the owner's", EXT,
     'if e.get("event") == "press" and e.get("by") != "recorder")))',
     'if e.get("event") == "press")))'),
]


def run_tests():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-m", "unittest", "-v", *TESTS], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=600)
    tail = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""
    ran = re.search(r"Ran (\d+) test", p.stderr)
    return p.returncode, tail, p.stderr, int(ran.group(1)) if ran else 0


def sweep():
    survivors = []
    for name, rel, old, new in MUTATIONS:
        path = ROOT / rel
        saved = path.read_bytes()
        text = saved.decode("utf-8")
        if text.count(old) != 1:
            print(f"PREFLIGHT {name}: target found {text.count(old)} times in {rel}", flush=True)
            survivors.append(name)
            continue
        try:
            path.write_text(text.replace(old, new))
            rc, tail, _, _ = run_tests()
        finally:
            path.write_bytes(saved)
        verdict = "killed" if rc != 0 else "SURVIVED"
        if rc == 0:
            survivors.append(name)
        print(f"{verdict}: {name} ({rel}) -> {tail}", flush=True)
    rc, tail, _, _ = run_tests()
    print(f"restored sources: {tail}", flush=True)
    print(f"survivors: {survivors}", flush=True)
    return 1 if survivors or rc != 0 else 0


def before():
    sources = [REC, MAP, EXT]
    new = ["runtime/human/note.py", "runtime/human/live.py"]     # absent before T39b
    saved = {rel: (ROOT / rel).read_bytes() for rel in sources + new}
    try:
        for rel in new:
            (ROOT / rel).unlink()
        for rel in sources:
            old = subprocess.run(["git", "show", f"origin/main:{rel}"], cwd=ROOT, check=True,
                                 capture_output=True).stdout
            (ROOT / rel).write_bytes(old)
        rc, tail, err, ran = run_tests()
    finally:
        for rel, data in saved.items():
            (ROOT / rel).write_bytes(data)
    passed = [line for line in err.splitlines() if line.endswith(" ... ok")]
    print(f"T39b tests on origin/main's {', '.join(sources)}: exit {rc}, {tail}", flush=True)
    print(f"passing: {passed}", flush=True)
    rc2, tail2, _, _ = run_tests()
    print(f"restored sources: {tail2}", flush=True)
    return 0 if rc != 0 and not passed and rc2 == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--before", action="store_true", help="the fail-before proof (see above)")
    a = ap.parse_args(argv)
    return before() if a.before else sweep()


if __name__ == "__main__":
    sys.exit(main())
