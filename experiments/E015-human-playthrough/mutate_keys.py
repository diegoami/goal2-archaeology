#!/usr/bin/env python3
"""T34 in-place mutation proofs; restores each source even when a test fails.

Each mutation replaces one exact string (it must occur once) in one source, runs
tests.test_human_keys and tests.test_human_record, and restores the bytes in `finally`. A mutation
the tests still pass is a survivor; the script exits 1 when there is one."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REC = "runtime/human/recorder.py"
MAP = "experiments/E015-human-playthrough/keymap.py"
EXT = "experiments/E015-human-playthrough/extract.py"
MUTATIONS = [
    # the display restriction (privacy)
    ("display restriction removed", REC,
     'if not env.get("DISPLAY") or env["DISPLAY"] == outer_display:', 'if False:'),
    ("R3: logger also reads the outer display", REC,
     '["stdbuf", "-oL", "xinput", "test-xi2", "--root"],',
     '["sh", "-c", f"stdbuf -oL xinput test-xi2 --root & DISPLAY={self.outer_display} '
     'stdbuf -oL xinput test-xi2 --root; wait"],'),
    ("R3: logger reads the outer display instead", REC,
     '                                     env=self.env, stdout=subprocess.PIPE,',
     '                                     env=dict(self.env, DISPLAY=self.outer_display), '
     'stdout=subprocess.PIPE,'),
    ("R8: save keys through XTEST", REC,
     '    import ctypes as c\n    class KeyEvent(c.Structure):',
     '    subprocess.run(["xdotool", "key", "F12+s"], env=env)\n    return\n'
     '    import ctypes as c\n    class KeyEvent(c.Structure):'),
    # the burst snapshot
    ("burst capture removed", REC, 'is_burst = burst.due(now)', 'is_burst = False'),
    # constants, +1 and -1
    ("BURST_QUIET_S +1", REC, 'BURST_QUIET_S = 0.5\n', 'BURST_QUIET_S = 1.5\n'),
    ("BURST_QUIET_S -1", REC, 'BURST_QUIET_S = 0.5\n', 'BURST_QUIET_S = -0.5\n'),
    ("CAPTURE_MARGIN_S +1", REC, 'CAPTURE_MARGIN_S = 0.05\n', 'CAPTURE_MARGIN_S = 1.05\n'),
    ("CAPTURE_MARGIN_S -1", REC, 'CAPTURE_MARGIN_S = 0.05\n', 'CAPTURE_MARGIN_S = -0.95\n'),
    ("NESTED_START_S +1", REC, 'NESTED_START_S = 10.0\n', 'NESTED_START_S = 11.0\n'),
    ("NESTED_START_S -1", REC, 'NESTED_START_S = 10.0\n', 'NESTED_START_S = 9.0\n'),
    ("first display +1", REC, 'for number in range(600, 700):', 'for number in range(601, 700):'),
    ("first display -1", REC, 'for number in range(600, 700):', 'for number in range(599, 700):'),
    # the request window (R1)
    ("request time taken after the send", REC,
     '        request = self.clock()\n        self.xrun(key_cmd(self.wid))\n        self.last_sent = self.clock()',
     '        self.xrun(key_cmd(self.wid))\n        self.last_sent = request = self.clock()'),
    ("request_s is the staging time", REC,
     '"request_s": None if request is None else round(request - self.t0, 3),',
     '"request_s": round(self.clock() - self.t0, 3),'),
    ("sent_s is the request time", REC,
     '"sent_s": None if sent is None else round(sent - self.t0, 3)}',
     '"sent_s": None if request is None else round(request - self.t0, 3)}'),
    ("a resend does not move the window", REC,
     'sent = self.last_sent = self.clock()', 'sent = self.clock()'),
    ("a skipped request is not logged", REC,
     '            self.note_request(request, origin, None)\n            return None',
     '            return None'),
    ("the shutdown window opens at shutdown", REC,
     'lo = self.t0 if self.last_staged_request is None else self.last_staged_request',
     'lo = self.clock()'),
    ("quiet and margin not in meta", REC,
     '"resolution": res, "burst_quiet_s": BURST_QUIET_S,', '"resolution": res,'),
    # the Xephyr window (R4)
    ("R4: accept a live Xephyr without its window", REC,
     '            wid = find(outer_env, title)\n', '            wid = "guess"\n'),
    ("R4: no per-session title", REC, '                                 "-title", title],',
     '                                 ],'),
    ("R4: title match not exact", REC,
     '.stdout.rstrip("\\n") == title]', '.stdout.startswith(title)]'),
    ("R4: several title matches accepted", REC,
     'return named[0] if len(named) == 1 else None', 'return named[0] if named else None'),
    ("R4: video window found by pid", REC,
     '            geom0 = window_geometry(xephyr_wid, outer_env)',
     '            geom0 = window_geometry(find_window(outer_env, xephyr.pid, timeout=2, '
     'search_class="Xephyr"), outer_env)'),
    # the map rules
    ("headline keeps host paths", MAP, 'if row and "/" not in row:', 'if row:'),
    ("text identity removed", MAP, 'digest = hashlib.sha256(text.encode("utf-8")).hexdigest()',
     'digest = state["screen_digest"]'),
    ("headline removed", MAP, 'screens[digest] = headline(text)', 'screens[digest] = "(no headline)"'),
    ("invalid snapshot filter removed", MAP,
     'if not state.get("error") and state.get("screen_text") is not None:',
     'if state.get("screen_text") is not None:'),
    ("skipped requests ignored", MAP, 'if req.get("seq") is None:', 'if False:'),
    ("legacy entry bracketed at staging", MAP, 'return -math.inf, staged', 'return staged, staged'),
    ("resend window ignored", MAP, 'sent = entry["request_s"] if sent is None else sent',
     'sent = entry["request_s"]'),
    ("snapshot ordering removed", MAP, 'samples.sort(key=lambda s: s[0])', 'pass'),
    ("event ordering removed", MAP, 'sorted(events, key=lambda e: e["monotonic_s"])', 'events'),
    ("split: a key at a request joins the earlier gap", MAP, 'gap = sum(1 for lo in starts if lo < t)',
     'gap = sum(1 for lo in starts if lo <= t)'),
    ("ambiguous window rule removed", MAP, 'if any(lo <= t <= hi for lo, hi, _ in samples):', 'if False:'),
    ("ambiguous window opens after the request", MAP, 'if any(lo <= t <= hi for lo, hi, _ in samples):',
     'if any(lo < t <= hi for lo, hi, _ in samples):'),
    ("burst grouping removed", MAP, 'event["monotonic_s"] > bursts[-1][-1]["monotonic_s"] + quiet', 'True'),
    ("adjacency: two bursts in a gap mapped", MAP, 'if len(pressed) > 1 or gap in ambiguous', 'if gap in ambiguous'),
    ("release filter removed", MAP, 'if e["event"] == "press"', 'if True'),
    ("before is the snapshot after", MAP, 'before = samples[gap - 1][2] if gap > 0 else None',
     'before = samples[gap][2] if gap < len(samples) else None'),
    ("after is the snapshot before", MAP, 'after = samples[gap][2] if gap < len(samples) else None',
     'after = samples[gap - 1][2] if gap > 0 else None'),
    ("missing-bracket rule removed", MAP, ' or before is None or after is None:', ':'),
    ("session constants ignored", MAP,
     'quiet=meta.get("burst_quiet_s"), margin=meta.get("capture_margin_s"),', ''),
    ("missing-bracket count removed", MAP, 'unmapped += n', 'unmapped += 0'),
    ("transition count removed", MAP, 'transitions.get(key, 0) + 1', '1'),
    ("press count removed", MAP, 'total += n', 'total += 0'),
    # the record (R9)
    ("record keeps the home directory", EXT, 'return value.replace(home, "~")', 'return value'),
]


def main():
    survivors = []
    tmp = ROOT / "scratch" / "t34-tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(tmp))
    for name, filename, old, new in MUTATIONS:
        path = ROOT / filename
        original = path.read_bytes()
        text = original.decode()
        assert text.count(old) == 1, (name, text.count(old))
        try:
            path.write_text(text.replace(old, new))
            result = subprocess.run([sys.executable, "-B", "-m", "unittest",
                                     "tests.test_human_keys", "tests.test_human_record"],
                                    cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, timeout=900)
            failing = [line for line in result.stdout.splitlines()
                       if line.startswith(("FAIL:", "ERROR:"))]
            print(f"MUTATION: {name} ({filename}); exit={result.returncode}; "
                  f"failing tests: {len(failing)}", flush=True)
            for line in failing:
                print(f"    {line}", flush=True)
            print("    " + (result.stdout.strip().splitlines() or ["(no output)"])[-1], flush=True)
            if result.returncode == 0:
                survivors.append(name)
        finally:
            path.write_bytes(original)
    print(f"Mutations: {len(MUTATIONS)}; survivors: {survivors}", flush=True)
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
