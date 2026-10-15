#!/usr/bin/env python3
"""T35 reproductions and in-place mutation proofs; restores each source even when a test fails.

    python3 experiments/E015-human-playthrough/mutate_keys.py [--only-r2|--only-r3|--only-r4|…]
    python3 experiments/E015-human-playthrough/mutate_keys.py --r4-r1 --clock injected \
        --_submitted=2 --_finished=0 --keys 'a;b;c'
    python3 experiments/E015-human-playthrough/mutate_keys.py --r4-r2 --bracket --later-bytes \
        --keys 'a;b;c'

The two `--r4-r*` modes are the Sol delta r4 reproductions of issue #111, run against the
recorder and the acceptance guard exactly as the r4 review constructed them:

- `--r4-r1` (stability fallback): an injected clock and write source, `_submitted=2` /
  `_finished=0` (a later save request already queued, none answered). The recorder must never
  stage the live savestate's bytes under the earlier request's window — neither when the write
  lands while the capture polls (the review's reproduction: the live bytes carry a later
  request's save) nor through the stability fallback, where the write's `(events, sig)` pair is
  already in the pipeline's consumption ledger. Exit 1 = both refused (the report carries the
  stability-fallback message); exit 0 = the bypass staged them.
- `--r4-r2` (evidence-free guard): a bracketing snapshot and a key event whose staged bytes
  belong to a later request. All four acceptance checks (attribution, burst count,
  request-window timing, mapped coverage) must reject the sitting. Exit 1 = rejected (the
  report carries the evidence-free message); exit 0 = all four checks were green.

The remaining modes are the mutation proofs: each mutation replaces one exact string (it must
occur once) in one source, runs tests.test_human_keys and tests.test_human_record, and restores
the bytes in `finally`. A mutation the tests still pass is a survivor; the script exits 1 when
there is one."""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "human"))
sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))
import recorder as rec  # noqa: E402

REC = "runtime/human/recorder.py"
MAP = "experiments/E015-human-playthrough/keymap.py"
EXT = "experiments/E015-human-playthrough/extract.py"
SCRIPTED = "experiments/E015-human-playthrough/scripted_keys.py"
TEST = "tests/test_human_keys.py"
REPRO = ROOT / "scratch" / "t35-repro"
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
    # the burst snapshot (target refreshed for the r2 rework: the loop's due-time condition
    # replaced the old `send_burst = True`, which the pre-flight then found zero times)
    ("burst capture removed", REC,
     'send_burst = bool(burst.groups) and now >= last_event + EVENT_SETTLE_S',
     'send_burst = False'),
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
     '        self.xrun(key_cmd(self.wid))\n        self.last_sent = self.clock()\n        self.last_request = request',
     '        self.xrun(key_cmd(self.wid))\n        self.last_sent = request = self.clock()\n        self.last_request = request'),
    ("request_s is the staging time", REC,
     '"request_s": None if request is None else round(request - self.t0, 3),',
     '"request_s": round(self.clock() - self.t0, 3),'),
    ("sent_s is the request time", REC,
     '"sent_s": None if sent is None else round(sent - self.t0, 3)}',
     '"sent_s": None if request is None else round(request - self.t0, 3)}'),
    ("a resend does not move the window", REC,
     'sent = self.last_sent = self.clock()', 'sent = self.clock()'),
    ("a skipped request is not logged", REC,
     '            self.note_request(request, self.last_sent, origin, None, pre_sig=sig_hash(pre))\n'
     '            return None',
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
    ("ambiguous window rule removed", MAP, 'if any(lo <= t <= hi for lo, hi, _, _ in samples):', 'if False:'),
    ("ambiguous window opens after the request", MAP, 'if any(lo <= t <= hi for lo, hi, _, _ in samples):',
     'if any(lo < t <= hi for lo, hi, _, _ in samples):'),
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
    # The target is the two lines below `def check_bursts`: the one-line
    # `if len(bursts) != len(groups):` also guards the request-window check, so the
    # pre-flight's "exactly once" rule failed on it (found by T35's sweep pre-flight).
    ("R3: guard accepts fewer snapshots than groups", SCRIPTED,
     '    if len(bursts) != len(groups):\n'
     '        return False, (f"{len(bursts)} burst snapshots for {len(groups)} key group(s); each "',
     '    if len(bursts) > len(groups):\n'
     '        return False, (f"{len(bursts)} burst snapshots for {len(groups)} key group(s); each "'),
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
      'jobs.put((pre, request, sent, origin, pre_events,\n'
      '                      self.session / "requests" / f"rq-{self._request_seq:04d}.sav", epoch))',
      'jobs.put((pre, request, sent, origin, pre_events, None)); jobs.join()'),
    # Sol delta r3 R1: the deferred-capture check removed — a job that begins after a save
    # completed stages those (later request's) bytes under its own window again; the
    # deferred-capture regression must fail (no superseded line is ever written).
    ("r3-R1: deferred-capture check removed", REC,
     'if self._submitted - self._finished > 1:', 'if False:'),
    # Sol delta r3 R2: the deferred-capture regression's wrap-_stage_job sleeps no more, so
    # the sitting is clean and the regression (and the guard test) must fail: the wrap is
    # load-bearing, not vacuous.
    ("r3-R2: deferred-capture regression's wrap-_stage_job sleeps no more", TEST,
     'time.sleep(2.0)', 'pass'),
    # Sol delta r4 R1: the every-poll write-ownership check removed — a fast job stages a
    # later request's bytes whenever two saves land in one poll gap (the first-poll bypass)
    # and the stability fallback restages consumed bytes. Killed by AttributionBypassTests.
    ("r4-R1: every-poll write-ownership check removed", REC,
     'and events - pre_events > ONE_SAVE_MAX_EVENTS):', 'and False):'),
    # Sol delta r4 R2: the guard's attribution evidence requirement reverted — an ordinary
    # staged line (no superseded, no write accounting) is certified again. Killed by
    # GuardAttributionTests.
    ("r4-R2: guard accepts evidence-free staged lines", SCRIPTED,
     'if pre is None or acc is None:', 'if False:'),
    # T35 r5 R1 (issue #111 R1), two mutations of the unanchored-capture class: every shape
    # a capture uses to order the live file's write against the queued requests. (a) the
    # fresh-arrival gate removed — any write that arrives while a lagging job polls is its
    # own again; (b) every capture counted as the pipeline's head — the injected
    # `_submitted=2/_finished=0` state can no longer be told from an empty queue. Both must
    # fail AttributionBypassTests.test_a_one_save_of_later_write_events_is_not_staged_under_
    # the_earlier_request (the r4 R1 reproduction as a unit test).
    ("r5-R1: the unanchored-capture gate removed", REC,
     'and (entry_head or self._fast_consumed is not None)):',
     'and True):'),
    ("r5-R1: every capture counted as the pipeline's head", REC,
     'entry_head = self._submitted - self._finished <= 1',
     'entry_head = True'),
    # T35 r5 R2 (issue #111 R2), three mutations of the evidence-free-guard class: each
    # piece of the signature-pair requirement and the missing-staged rule, the absences the
    # guard must never treat as ownership. Killed by GuardAttributionTests: (a) the pre-send
    # state requirement, (b) the accept-time state requirement, (c) the staged-nothing rule.
    ("r5-R2: the pre-send state requirement removed", SCRIPTED,
     '        if pre_sig is None:', '        if False:'),
    ("r5-R2: the accept-time state requirement removed", SCRIPTED,
     '        if accept_sig is None:', '        if False:'),
    ("r5-R2: a staged-nothing request is skipped again", SCRIPTED,
     '        if r.get("seq") is None:\n'
     '            # T35 (issue #111 R2, Scope: missing-staged requests fail): a request line with\n'
     '            # no staged entry is a screen the recorder could not see — the boundary it was\n'
     '            # sent to catch is not in the chain. Certifying it would certify a boundary this\n'
     '            # request never owned; superseded lines are caught above with their own reason.\n'
     '            return False, (f"request attribution lost: request line {i} (request_s "\n'
     '                           f"{r[\'request_s\']}) staged nothing: no snapshot carries this "\n'
     '                           "request\'s window (evidence-free)")',
     '        if r.get("seq") is None:\n'
     '            continue'),
    # Sol's R2 on PR 112 (round 2): the shapes the r5 list lacked. (a) the unanchored-capture
    # gate's consumption test inverted; (b) the stability fallback reading the live file on
    # the fast path. Both must fail AttributionBypassTests.
    ("r5-R1: the consumed-ledger test inverted (is not None -> is None)", REC,
     'and (entry_head or self._fast_consumed is not None)):',
     'and (entry_head or self._fast_consumed is None)):'),
    ("r5-R1: the stability fallback reads the live file on the fast path", REC,
     '                if fast:\n                    self.log("stability fallback: stable',
     '                if False:\n                    self.log("stability fallback: stable'),
    # T35 round 3 (Sol's R1 on PR 112; the owner's option A, 2026-10-11): every piece of the
    # save-number binding. (a) dropped; (b) replaced by `length > 0`, the comparison a shallow
    # fix would write; (c) the unowned save after the last line accepted; (d) a save before the
    # first request accepted; (e) a session without its write total accepted. Killed by
    # GuardAttributionTests and the matching-window reproduction. (f) the recorder no longer
    # writes the total: only the end-to-end sitting can see it (heavy: run without
    # MUTATION_SWEEP, so the scripted sitting test runs).
    ("r6-R1: the save-number binding dropped", SCRIPTED,
     'if not (recorder.ONE_SAVE_MIN_EVENTS <= step <= recorder.ONE_SAVE_MAX_EVENTS):',
     'if False:'),
    ("r6-R1: the save-number binding replaced by length > 0", SCRIPTED,
     'if not (recorder.ONE_SAVE_MIN_EVENTS <= step <= recorder.ONE_SAVE_MAX_EVENTS):',
     'if not (step > 0):'),
    ("r6-R1: an unowned save after the last line accepted", SCRIPTED,
     'if rest >= recorder.ONE_SAVE_MIN_EVENTS:', 'if False:'),
    ("r6-R1: a save before the first request accepted", SCRIPTED,
     'if seen is None and pre >= recorder.ONE_SAVE_MIN_EVENTS:', 'if False:'),
    ("r6-R1: a session without its write total accepted", SCRIPTED,
     'if session is not None and write_events_total is None:', 'if False:'),
    ("r6-R1: the recorder writes no write total", REC,
     'meta["write_events_total"] = watcher.activity()[1]', 'pass', "heavy"),
    # Sol's round-3 R1 on PR 112: the write watch started with the Watcher again, after the
    # emulator is up, so an early save goes uncounted (killed by EarlySaveTests; heavy)
    ("r6-R1: the write watch starts after the emulator", REC,
     'xrun=lambda argv: send_save_event(wid, env), watch=watch,',
     'xrun=lambda argv: send_save_event(wid, env), watch=None,', "heavy"),
]


def tiny_zip(payload=b"vga", mem=b"mem"):
    """A complete savestate zip (the same three members the staging gate requires)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Save_Remark", b"")
        z.writestr("Vga", payload)
        z.writestr("Memory", mem)
    return buf.getvalue()


class _FakeDbx:
    returncode = 0

    def poll(self):
        return None


class _ScriptedClock:
    """The injected clock (Sol delta r4 R1): sleeps advance fake time and run the pending
    action, so a capture reaches its deadline instantly and the write source fires at a
    chosen poll. Bounded: a loop that never reaches its deadline fails instead of hanging."""
    LIMIT_S = 3600.0

    def __init__(self, actions):
        self.t = 0.0
        self.actions = list(actions)

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s
        if self.t > self.LIMIT_S:
            raise AssertionError(f"fake clock past {self.LIMIT_S}s")
        if self.actions:
            self.actions.pop(0)()


def _injected_watcher(actions, submitted=0, finished=0):
    """A Watcher on the injected clock and write source the r4 reproduction drives; the
    session lives under the worktree's scratch (never TMPDIR outside a checkout)."""
    REPRO.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(dir=REPRO))
    (session / "snapshots").mkdir()
    live = session / "state.sav"
    live.write_bytes(tiny_zip(b"vga-0"))
    state = {"busy": False, "events": 0}
    logs = []
    clock = _ScriptedClock(actions)
    w = rec.Watcher(session, live, "77", _FakeDbx(), {"DISPLAY": ":0"},
                    clock=clock, sleep=clock.sleep, xrun=lambda a: None,
                    alive=lambda: True, log=logs.append)
    w.activity = lambda: (state["busy"], state["events"])
    w._submitted, w._finished = submitted, finished
    return session, w, live, state, logs


def _staged(w, session):
    """(an entry was staged, the request lines, the index entries, the captured bytes)."""
    index = []
    if (session / "index.jsonl").is_file():
        index = [json.loads(x) for x in (session / "index.jsonl").read_text().splitlines()]
    lines = []
    if (session / "requests.jsonl").is_file():
        lines = [json.loads(x) for x in (session / "requests.jsonl").read_text().splitlines()
                 if x.strip()]
    return bool(index), lines, index


def _r1_scenarios(args):
    """The three shapes of the r4 R1 bypass. Each returns (name, staged, logs)."""
    out = []
    submitted, finished = args.submitted, args.finished
    req = "requests"     # per-request savestates live under the session's requests/

    # A — the stability fallback: the live savestate already holds a completed write whose
    # (events, sig) pair the pipeline has CONSUMED (`_fast_consumed` matches). Re-staging it
    # would put an already-staged save under this request's window again.
    session, w, live, state, logs = _injected_watcher([], submitted, finished)
    pre = rec.file_signature(live)
    live.write_bytes(tiny_zip(b"LATER REQUEST BYTES"))
    state["events"] = 54
    w._fast_consumed = (54, rec.file_signature(live))
    w._stage_job(pre, 0.0, 0.03, "burst", 0, session / req / "rq-0001.sav")
    staged, lines, _ = _staged(w, session)
    out.append(("A: stability fallback, consumed (events, sig) pair", staged, logs, lines))
    shutil.rmtree(session, ignore_errors=True)

    # B — the review's reproduction: the first sleep serves the queued requests' write, so
    # the live file carries a LATER request's save; the capture began with `_submitted=2,
    # _finished=0` (a later save request already queued, none answered) and polls into it.
    for name, advance in (("B: fresh arrival, the review's event advance", 2),
                          ("C: fresh arrival, one save's write events", 54)):
        session, w, live, state, logs = _injected_watcher([], submitted, finished)

        def write(live=live, state=state, advance=advance):
            live.write_bytes(tiny_zip(b"LATER REQUEST BYTES"))
            state["events"] = advance
        w.clock.actions.append(write)
        pre = rec.file_signature(live)
        state["events"] = 0
        w._stage_job(pre, 0.0, 0.03, "burst", 0, session / req / "rq-0001.sav")
        staged, lines, _ = _staged(w, session)
        out.append((name, staged, logs, lines))
        shutil.rmtree(session, ignore_errors=True)
    return out


def repro_r4_r1(args):
    """Sol delta r4 R1 (issue #111): no path of a capture may stage the live savestate's
    bytes under an earlier request's window. Exit 1 when every shape is refused."""
    print(f"T35 r4-R1 reproduction: injected clock, _submitted={args.submitted}, "
          f"_finished={args.finished}, keys {args.keys}")
    bypassed = []
    for name, staged, logs, lines in _r1_scenarios(args):
        state = "STAGED under the earlier request" if staged else "refused"
        print(f"  {name}: {state}")
        counts = {}
        for line in logs:
            counts[line] = counts.get(line, 0) + 1
        for line, n in counts.items():
            print(f"      log{' (x%d)' % n if n > 1 else ''}: {line}")
        for line in lines:
            print(f"      request line: {json.dumps(line, sort_keys=True)}")
        if staged:
            bypassed.append(name)
    if bypassed:
        print(f"R1 BYPASS: the live savestate's bytes were staged under the earlier request "
              f"({'; '.join(bypassed)})")
        return 0
    print("stability fallback: the live savestate's already-consumed or unowned bytes were "
          "not re-staged under the earlier request; every shape refused "
          f"(injected clock, _submitted={args.submitted}, _finished={args.finished}, "
          f"keys {args.keys})")
    return 1


def _sig_hash(*parts):
    """The request line's signature hash, the same digest recorder.sig_hash writes: a hex
    sha256 over the signature tuple. The reproduction writes its own (the signature pair is
    the recorder's evidence; the window of the staged snapshot is what this reproduction
    forges), so the command runs against a tree without that helper too."""
    return rec.sha256(json.dumps(list(parts)).encode("utf-8"))


def _r2_session(args):
    """The bracketing snapshot + key event whose staged bytes belong to a later request:
    the session files a sitting like that leaves behind."""
    REPRO.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(dir=REPRO))
    (session / "requests").mkdir()
    (session / "snapshots").mkdir()
    keys = [k for k in args.keys.split(";") if k]
    events = []
    for i, key in enumerate(keys):
        t = 1.0 + 0.5 * i
        events += [{"monotonic_s": t, "event": "press", "keysym": key},
                   {"monotonic_s": t + 0.012, "event": "release", "keysym": key}]
    (session / "keys.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    opening, later = tiny_zip(b"OPENING SCREEN BYTES"), tiny_zip(b"LATER REQUEST BYTES")
    burst_bytes = later if args.later_bytes else tiny_zip(b"THIS REQUEST'S OWN SAVE BYTES")
    entries = [
        {"seq": 1, "file": "snapshots/snap-0001.sav", "bytes": len(opening),
         "sha256": rec.sha256(opening), "elapsed_s": 0.5, "origin": "cadence",
         "request_s": 0.0, "sent_s": 0.03},
        # the burst snapshot: staged after the group's last key, so the bracketing checks
        # and the coverage check see exactly what the r4 review saw
        {"seq": 2, "file": "snapshots/snap-0002.sav", "bytes": len(burst_bytes),
         "sha256": rec.sha256(burst_bytes), "elapsed_s": 3.0, "origin": "burst",
         # --later-bytes: this window is the LATER request's own save request (sent at
         # 2.5 s); the request line below claims it under the burst request's window.
         # --matching-window (Sol's R1 on PR 112, round 2): the snapshot claims the burst
         # request's own window too, so the window check sees nothing wrong
         "request_s": 2.5 if args.later_bytes and not args.matching_window else 2.05,
         "sent_s": 2.53},
    ]
    (session / "snapshots" / "snap-0001.sav").write_bytes(opening)
    (session / "snapshots" / "snap-0002.sav").write_bytes(burst_bytes)
    (session / "index.jsonl").write_text("".join(json.dumps(e) + "\n" for e in entries))
    (session / "requests" / "rq-0001.sav").write_bytes(opening)
    (session / "requests" / "rq-0002.sav").write_bytes(burst_bytes)
    lines = [
        {"request_s": 0.0, "sent_s": 0.03, "origin": "cadence", "seq": 1,
         "pre_events": 0, "accept_events": 54, "request_file": "requests/rq-0001.sav",
         "request_sha256": rec.sha256(opening),
         "pre_sig": _sig_hash((1, 4096, 100, 100)), "accept_sig": _sig_hash((1, 4096, 200, 200))},
        # the burst request's line: full write accounting and a consistent per-request
        # savestate — yet the staged snapshot beside it is the LATER request's window
        {"request_s": 2.05, "sent_s": 2.08, "origin": "burst", "seq": 2,
         "pre_events": 54, "accept_events": 108, "request_file": "requests/rq-0002.sav",
         "request_sha256": rec.sha256(burst_bytes),
         "pre_sig": _sig_hash((1, 4096, 300, 300)), "accept_sig": _sig_hash((1, 4096, 400, 400))},
    ]
    (session / "requests.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    # the recorder's whole-sitting write count (T35 round 3): the later request's save happened
    # too — that is where the later bytes came from — but no line owns it, so a real sitting
    # like this one counts three saves for two staged lines
    total = 162 if args.later_bytes else 108
    return session, keys, events, lines, entries, total


def repro_r4_r2(args):
    """Sol delta r4 R2 (issue #111): the acceptance guard must not certify a sitting whose
    staged bytes belong to a later request, whatever the other three checks say. Exit 1 when
    any check rejects it."""
    import scripted_keys
    session, keys, events, lines, entries, total = _r2_session(args)
    try:
        index = [json.loads(x) for x in (session / "index.jsonl").read_text().splitlines()]
        bursts = [e for e in index if e["origin"] == "burst"]
        groups = scripted_keys.group_presses(events, rec.BURST_QUIET_S)
        checks = []
        ok, why = scripted_keys.check_attribution(lines, session=session, index=index,
                                                  write_events_total=total)
        checks.append(("attribution", ok, why))
        ok2, why2 = scripted_keys.check_bursts(groups, bursts, 0.0)
        checks.append(("burst count", ok2, why2))
        ok3, why3 = scripted_keys.check_request_windows(groups, bursts, 0.0, rec.CAPTURE_MARGIN_S)
        checks.append(("request-window timing", ok3, why3))
        sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))
        import keymap
        states = [{"entry": e, "screen_text": text, "error": None}
                  for e, text in zip(index, ("OPENING SCREEN", "TITLE SCREEN"))]
        mapped = keymap.build_map(states, events, 0.0, quiet=rec.BURST_QUIET_S,
                                  margin=rec.CAPTURE_MARGIN_S, requests=lines)
        ok4, why4 = scripted_keys.check_mapped(mapped)
        checks.append(("mapped coverage", ok4, why4))
        print(f"T35 r4-R2 reproduction: bracketing snapshot + key event, "
              f"{'later-request' if args.later_bytes else 'own-request'} bytes, "
              f"keys {args.keys}")
        for name, ok, why in checks:
            print(f"  {name}: {'PASS' if ok else 'FAIL'} — {why}")
        failed = [(name, why) for name, ok, why in checks if not ok]
        if failed:
            name, why = failed[0]
            print(f"evidence-free guard: {name} rejected the sitting — {why}")
            return 1
        print(f"R2 BYPASS: all four checks green on "
              f"{'later-request' if args.later_bytes else 'own-request'} bytes "
              f"(evidence-free guard)")
        return 0
    finally:
        shutil.rmtree(session, ignore_errors=True)


def run_sweep(argv):
    mutations = MUTATIONS
    if "--only-r2" in argv:
        mutations = [m for m in MUTATIONS if m[0].startswith("r2-")]
    if "--only-r3" in argv:
        mutations = [m for m in MUTATIONS if m[0].startswith("r3-")]
    if "--only-r4" in argv:
        mutations = [m for m in MUTATIONS if m[0].startswith("r4-")]
    if "--only-r5" in argv:
        mutations = [m for m in MUTATIONS if m[0].startswith("r5-")]
    if "--only-r6" in argv:
        mutations = [m for m in MUTATIONS if m[0].startswith("r6-")]
    survivors = []
    tmp = ROOT / "scratch" / "t34-tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(tmp), MUTATION_SWEEP="1")
    # pre-flight: every target string must occur exactly once in the pristine source, so a run
    # that starts on a source left mutated by an aborted earlier run fails before mutating
    for name, filename, old, *_ in mutations:
        count = (ROOT / filename).read_text().count(old)
        assert count == 1, (name, count, "source not pristine?")
    for name, filename, old, new, *heavy in mutations:
        path = ROOT / filename
        # a heavy mutation runs the suite with the end-to-end scripted sitting (no MUTATION_SWEEP)
        run_env = {k: v for k, v in env.items() if k != "MUTATION_SWEEP"} if heavy else env
        original = path.read_bytes()
        text = original.decode()
        assert text.count(old) == 1, (name, text.count(old))
        try:
            path.write_text(text.replace(old, new))
            result = subprocess.run([sys.executable, "-B", "-m", "unittest",
                                     "tests.test_human_keys", "tests.test_human_record"],
                                    cwd=ROOT, env=run_env, stdout=subprocess.PIPE,
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--r4-r1", action="store_true",
                    help="run the Sol delta r4 R1 stability-fallback reproduction")
    ap.add_argument("--r4-r2", action="store_true",
                    help="run the Sol delta r4 R2 evidence-free-guard reproduction")
    ap.add_argument("--clock", choices=["injected"], default=None,
                    help="the reproduction's clock (only 'injected' exists)")
    ap.add_argument("--_submitted", type=int, dest="submitted", default=2,
                    help="pipeline requests submitted at the reproduction's first poll")
    ap.add_argument("--_finished", type=int, dest="finished", default=0,
                    help="pipeline requests finished at the reproduction's first poll")
    ap.add_argument("--bracket", action="store_true",
                    help="r4-r2: build the bracketing snapshot and key event")
    ap.add_argument("--matching-window", action="store_true",
                    help="r4-R2: the staged snapshot claims the burst request's own window "
                         "(Sol's R1 on PR 112, round 2)")
    ap.add_argument("--later-bytes", action="store_true",
                    help="r4-r2: the staged bytes belong to a later request")
    ap.add_argument("--keys", default="a;b;c", help="the sitting's game keys (';'-separated)")
    ap.add_argument("--only-r2", action="store_true")
    ap.add_argument("--only-r3", action="store_true")
    ap.add_argument("--only-r4", action="store_true")
    ap.add_argument("--only-r5", action="store_true")
    ap.add_argument("--only-r6", action="store_true")
    a = ap.parse_args(argv)
    if a.r4_r1 and a.r4_r2:
        ap.error("--r4-r1 and --r4-r2 are separate reproductions")
    if a.r4_r1:
        if a.clock != "injected":
            ap.error("--r4-r1 needs --clock injected")
        return repro_r4_r1(a)
    if a.r4_r2:
        if not (a.bracket and a.later_bytes):
            ap.error("--r4-r2 needs --bracket --later-bytes")
        return repro_r4_r2(a)
    return run_sweep(list(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    sys.exit(main())
