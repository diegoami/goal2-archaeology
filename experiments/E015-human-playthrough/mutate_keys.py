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
SCRIPTED = "experiments/E015-human-playthrough/scripted_keys.py"
TEST = "tests/test_human_keys.py"
MUTATIONS = [
    # the display restriction (privacy)
    ("display restriction removed", REC,
     'if not env.get("DISPLAY") or env["DISPLAY"] == outer_display:', 'if False:'),
    ("R3 focused-XTEST: logger also reads the outer display", REC,
     # only the focused real XTEST keys (y/z to a foreign focused window) generate raw events
     # on the outer display, so only that test path can kill this mutation
     '["stdbuf", "-oL", "xinput", "test-xi2", "--root"],',
     '["sh", "-c", f"stdbuf -oL xinput test-xi2 --root & DISPLAY={self.outer_display} '
     'stdbuf -oL xinput test-xi2 --root; wait"],'),
    ("R3: logger reads the outer display instead", REC,
      '                                     env=self.env, stdout=subprocess.PIPE,',
      '                                     env=dict(self.env, DISPLAY=self.outer_display), '
      'stdout=subprocess.PIPE,'),
    ("R3: play() attaches the logger to the outer display", REC,
     '        keys = KeyLogger(env, outer_env["DISPLAY"], session / "keys.jsonl")',
     '        keys = KeyLogger(outer_env, outer_env["DISPLAY"], session / "keys.jsonl")'),
    ("R8: save keys through XTEST", REC,
     '    import ctypes as c\n    class KeyEvent(c.Structure):',
     '    subprocess.run(["xdotool", "key", "F12+s"], env=env)\n    return\n'
     '    import ctypes as c\n    class KeyEvent(c.Structure):'),
    # the burst snapshot
    ("burst capture removed", REC, 'send_burst = True', 'send_burst = False'),
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
     '            self.note_request(request, self.last_sent, origin, None)\n            return None',
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
    # R1 (Sol delta): the privacy test's positive control — the focused real-XTEST sends to the
    # foreign application. Removing them must fail the privacy test (xev never receives y/z).
    ("R1: focused-XTEST foreign sends removed", TEST,
     '                subprocess.run(["xdotool", "windowfocus", "--sync", wid], env=env, check=True)\n'
     '                subprocess.run(["xdotool", "key", "y", "z"], env=env, check=True)\n',
     ''),
    # R2 (Sol delta): the drain-events-overwrite — every drained key joins the first group, so N
    # groups become one burst (the pre-fix behaviour). The human-pace test must fail.
    ("drain-events-overwrite: every key joins one group", REC,
     'if not self.groups or t >= self.groups[-1]["last"] + self.quiet:',
     'if not self.groups:'),
    # R3 (Sol delta): the acceptance guard accepts fewer snapshots than groups. With `>` the
    # 4-for-10 case slips past the count check and zip() pairs only the first four groups.
    ("R3: guard accepts fewer snapshots than groups", SCRIPTED,
     'if len(bursts) != len(groups):',
     'if len(bursts) > len(groups):'),
    # Sol delta r2: the settle wait removed, the request window opens at the key event itself
    # and swallows the key's own release (and any key spaced just over the quiet): the burst
    # is ambiguous. Killed by the 10-key mapping test (releases land in the windows).
    ("r2-R1: burst request sent without the settle wait", REC,
     'send_burst = bool(burst.groups) and now >= last_event + EVENT_SETTLE_S',
     'send_burst = bool(burst.groups)'),
    # Sol delta r2: the acceptance guard must verify mapped coverage, not only counts.
    ("r2-R2: guard counts snapshots only", SCRIPTED,
     'if result["unmapped_keys"]:', 'if False:'),
    # Sol delta r2: the scheduler must not wait for the previous capture before sending the
    # next group's request; with the modelled 0.6 s write latency the requests fall behind
    # the 0.527 s key spacing and key pairs share a gap (unmapped).
    ("r2-R3: scheduler waits for the previous capture", REC,
     'jobs.put((pre, request, sent, origin, pre_events, pre_closes))',
     'jobs.put((pre, request, sent, origin, pre_events, pre_closes)); jobs.join()'),
]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mutations = [m for m in MUTATIONS if m[0].startswith("r2-")] if "--only-r2" in argv else MUTATIONS
    survivors = []
    tmp = ROOT / "scratch" / "t34-tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(tmp), MUTATION_SWEEP="1")
    # pre-flight: every target string must occur exactly once in the pristine source, so a run
    # that starts on a source left mutated by an aborted earlier run fails before mutating
    for name, filename, old, _ in mutations:
        count = (ROOT / filename).read_text().count(old)
        assert count == 1, (name, count, "source not pristine?")
    for name, filename, old, new in mutations:
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
    print(f"Mutations: {len(mutations)}; survivors: {survivors}", flush=True)
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
