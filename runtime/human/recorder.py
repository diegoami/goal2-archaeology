#!/usr/bin/env python3
"""The human-playthrough recorder: one command that runs GOAL2 on a private nested display
and turns the sitting into a complete behavioural record — a timestamped chain of whole-machine
savestates, an index of them, and (optionally) a screen video of the game window.

    python3 runtime/human/recorder.py self-test [--video]
    python3 runtime/human/recorder.py play [--video] [--quit-after SECS]

Xephyr is shown on $DISPLAY; the game and raw key logger use only its nested display.
The emulator, config family and session layout follow the G1 driver (runtime/driver/driver.py):
windowed `surface` output, `savefile` in the session folder, drive C: mounted from a per-session
copy of the verified release (never the release cache itself — F001: a savestate remembers the
mounted folder, and the owner's in-game saves must land in the copy, not in the cache), drive D:
mounted for the clock read-back, exactly as every driver launch lays them out.

Correctness rules (each pinned by a test in tests/test_human_record.py):
- The window-bind gate (rework round 2 R1). The hazard is sending the emulator host key (F12+S)
  to a window the recorder did not launch — the owner's terminal, a stale window from a prior
  sitting, anything else. The new `find_window` searches for dosbox-class windows and accepts
  only the one whose `xdotool getwindowpid` equals the launched dosbox-x's pid; with no match,
  the search fails closed (no window id, no sends ever). The watcher's first action after the
  pid is known is to read the bind; a vanished bind (window closed) is end-of-session.
- The staging gate (rework rounds 2 and 3). The live savestate (`state.sav`) is never renamed
  or written, and only `Watcher.capture` reads it. A snapshot is staged — copied to snapshots/,
  hashed, indexed — only when:
    1. the file's signature (inode, size, mtime_ns, ctime_ns — metadata, no content read) has
       been identical for STABLE_POLLS consecutive polls; AND
    2. that signature differs from the one taken before the key was sent — evidence of a fresh
       write, not the previous tick's savestate re-indexed; nothing reads the live file's bytes
       before the key is sent (round 3: a pre-send content read could catch an in-progress
       write); AND
    3. no write session on the file is open before the read (inotify: a modify not yet
       followed by a close-write), the bytes read validate as a complete zip (the same checks
       driver.save_state applies: opens, tests clean, holds Vga, Memory, Save_Remark), AND the
       kernel reports no write event on the file between the check and the end of the read —
       so bytes read while a write was in progress are never staged (the task's hazard).
  The shutdown pass runs AFTER `terminate(dbx)` through the same `capture` (no pre-send
  signature); one deadline bounds every capture, retries included.
- The capture pipeline (T34 Sol-r2 R1). With keys attached, each settled key episode's save
  request is sent EVENT_SETTLE_S after its newest event (the scheduling quiet; the grouping
  quiet BURST_QUIET_S is what the map reads), and its staging capture runs in a worker thread,
  so a savestate that takes ~0.8 s never delays the next request: keys ~0.53 s apart still get
  one request window each — a due-time window (last key + BURST_QUIET_S) can never fit between
  two such keys — and the map can place every press. The worker's fast path takes the kernel's
  write-event count (inotify CLOSE_WRITE/MOVED_TO past the pre-send count) as the
  write-completed evidence — the stability polls cannot fit between writes 0.5 s apart. Every
  other gate check is unchanged.
- The clean termination (rework round 2 R5). The watcher's loop detects a dead dosbox-x between
  ticks and between polls of `capture` and treats it as end-of-session: the loop returns, the
  shutdown pass runs (R4), `play()` writes meta, the file/socket is closed. A dead emulator
  during a snapshot no longer raises out of the loop.
- The pause (T39b). F12+P is DOSBox-X's own pause (the session's mapper file); the Pause key
  resumes. The loop reads it from the game window's title (after every key event, every
  PAUSE_POLL_S, and right before every send), logs pauses.jsonl, sends no save request while
  paused, requests the pause's snapshot right after the resume, and no capture re-sends, or
  accepts a write landed after, a pause that began after its request (tests/test_human_pause.py).
- A sitting ends by closing the game window, by Ctrl+C in the terminal, or (scripted sittings)
  when --quit-after elapses; a partial chain is a valid record.
- Video. The recorder writes Matroska with `-flush_packets 1`, so bytes reach the disk as frames
  arrive (a dead recorder leaves them behind), and stops the grab with SIGTERM (never SIGKILL
  while it can be helped), which finalizes a valid file (duration reads back exactly). An
  unclean death can still truncate the last element, so the video is a convenience channel
  between snapshots — the savestates carry every screen — and the session meta records bytes,
  sha256 and a stalled flag, warned about loudly: the prototype's silent failure is made
  visible. `poll_growth()` is wired into the loop between ticks (R16) and `Video.stop()` checks
  for stalled state.

Standard library only, plus the G1 driver's modules."""
import argparse
import errno
import hashlib
import json
import os
import struct
import shutil
import signal
import subprocess
import sys
import time
import threading
import queue
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import driver  # noqa: E402  (verify_release, host_times, SET_ID, CACHE; config family via Driver)

# ---- constants ----------------------------------------------------------------------------------
# Each one is a rule of the recorder; tests/test_human_record.py fails when any is mutated.
# Cadence. 20 s is what the brief asks for (one savestate per ~20 s); the design choice below
# STABLE_POLLS grounds how the live file is read; the cadence itself is in the task.
CADENCE_S = 20.0      # seconds between snapshot ticks (the brief: every ~20 s) [brief]
# Stability. STABLE_POLLS = 3 means three consecutive equal-size polls before bytes are captured
# (R3). DOSBox-X 2024.03.01 writes the savestate in one shot to `state.sav` — measured on this
# host, the file goes from 0 to its final size in under one poll (POLL_S = 0.25 s). Three polls =
# 0.75 s of stability is comfortably longer than any internal chunk-to-disk flush and shorter
# than a player-triggered re-save. The constant grounds a [designed] margin — searched: a savestate
# write takes <0.5 s end-to-end, and one 0.25 s poll is the worst case for a brief equal size
# during a write. Tests pin the boundary (a growing file is never staged).
STABLE_POLLS = 3
POLL_S = 0.25         # savestate poll interval, as the driver's POLL but human-paced
SAVE_TIMEOUT_S = 15.0  # bound on one savestate write, driver.save_state's timeout
RESEND_AFTER_S = 3.0   # F12+S sent again when no savestate appeared, driver.save_state's resend
TERM_GRACE_S = 0.5     # SIGTERM -> SIGKILL grace for dosbox-x, driver's measured TERM_GRACE
# Video finalize grace. VIDEO_TERM_GRACE_S = 10 s: ffmpeg's matroska muxer with `-flush_packets
# 1` finalizes within 0.5 s on this machine in three sessions — the worst observed across the
# prototype runs was 1.2 s (release 2024.03.01, libx264 `-preset veryfast`, x11grab at 10 fps). 10 s
# is 8x the worst observed: SIGKILL after 10 s leaves a mkv file that mplayer will not finalize
# cleanly, so the grace matters. Boundary test asserts the EXACT 10 s: a proc alive at the 10.001
# s mark is SIGKILLed, not SIGTERMed.
VIDEO_TERM_GRACE_S = 10.0
# Stall detection. VIDEO_STALL_S = 60 s: with a 10 fps frame rate and -flush_packets 1, the
# file grows roughly every 0.1 s; the worst measured gap between file growth and an -vf
# `fps=10` grab on a busy host was 0.4 s. 60 s of no growth while ffmpeg is running is
# 150x the worst observed, well below the recorder's tick (20 s) × 3 = 60 s coincidence
# limit, so a stalled file is reliably flagged. Boundary test asserts the EXACT 60 s.
VIDEO_STALL_S = 60.0
SEND_TO_WINDOW = True  # the focus gate: keys only DIRECTLY to the game window, never global
SAVE_KEYS = "F12+s"    # the G1 driver's host key + save (F001)
SESSIONS = ROOT / "scratch" / "human" / "sessions"   # session folders (git-ignored: savestates
SELFTEST = ROOT / "scratch" / "human" / "selftest"   # and videos stay out of git, like run states)
WANT_DOSBOX = driver.WANT_DOSBOX
WINDOW_CLASS = "dosbox"  # the driver's window search

# [designed] A 0.5 s quiet interval groups human typing without waiting for
# the 20 s cadence. Searched T29 timing constants and T34 brief: neither
# specifies a human burst interval. This is recorder policy, not game timing.
BURST_QUIET_S = 0.5
# [designed] The SCHEDULING quiet: how long the key stream must be still before the settled
# episode's save request goes out (one snapshot per episode — the grouping quiet above stays
# what keymap.py reads from meta). Two measured facts fix its value (session 20261009-142948,
# the Sol-r2 reproduction): a key's release follows its press by ~12 ms (xdotool's key
# duration), and keys slept 0.51 s apart arrive 0.525-0.529 s apart on the wire. A window
# opened at the due time (last key + BURST_QUIET_S) can never fit between two such keys —
# it needs spacing >= quiet + window width (~0.58 s at width = send ~26 ms + margin 50 ms)
# — so it either swallows the next key or, sent later, leaves the pair unseparated; either
# way the pair is unmapped. Sent instead EVENT_SETTLE_S after the newest event, the window
# opens after that key's release and still ~0.39 s before the next key. 0.05 s is ~4x the
# measured release lag; the honest cost is a dead zone — an event arriving inside the open
# window ([settle, settle + width] after the last event) makes its gap ambiguous, the
# ambiguity keymap.py already documents. Searched: T34-probe-20261009-05.log (send ~26 ms,
# logger delivery max 5.7 ms) and the session's press/release intervals. Recorder policy,
# not game timing.
EVENT_SETTLE_S = 0.05
# [designed] The write-event bound of ONE save request. Measured on this host
# (evidence/E015/T34-probe-closes-20261009-01.log, three real saves): a single
# DOSBox-X save produces 53-54 write events on state.sav (27 CLOSE_WRITE plus as
# many MODIFY — the old docstring's '27 close events' counted only half). 80 is
# ~1.5x the measured worst save, far above one save's jitter and far below two
# saves' ~108: a fast pipeline job whose live savestate has advanced by more than
# this since its request was sent is reading a LATER request's save (the single
# serialized writer answers requests in order). Searched: the probe above; no
# prior measurement of per-save event counts existed. Recorder policy.
ONE_SAVE_MAX_EVENTS = 80
# [designed] The write-event floor of ONE save (T35 round 3, the owner's option A of 2026-10-11:
# each staged request owns exactly one save past the previous one). Measured: 53-54 events per
# save in the probe above (three saves) and 53 for each of the 12 saves of T35's ten-key
# reproduction on DOSBox-X 2024.03.01 (evidence/E015/T35-r3/dw3-write-events-20261011-01.log).
# 40 sits well under one save's jitter and far above zero, so a request step of [40, 80] events
# is one save and nothing else: none (0) or two (~106) fall outside it. DOSBox-X 2026.01.02
# writes a save in 3 events (#117): this project runs 2024.03.01 only. Recorder policy.
ONE_SAVE_MIN_EVENTS = 40
# [designed] A snapshot's screen is taken when DOSBox-X handles the save key, which the X server
# delivers after the recorder's request (the clock read before the send) and before the send's last
# event is flushed (`sent_s`). A key the logger stamps later than `sent_s` may still have reached
# the nested server first: the logger's delivery latency. Measured on this host
# (T34-probe-20261009-05.log, 200 XTEST presses with the main thread busy): median 0.08 ms, max
# 5.7 ms. 50 ms is ~9x the worst observed; a key stamped inside [request_s, sent_s + margin] is
# ambiguous and its burst unmapped (keymap.py). It is no game timing.
CAPTURE_MARGIN_S = 0.05
# [designed] Bound on Xephyr showing its window on the outer display. Xephyr binds its display
# socket before it creates the host window, so a titled window proves the display number is the
# launched Xephyr's own; on a busy number it exits in ~25 ms without one (T34-probe-20261009-05.log).
NESTED_START_S = 10.0
# The pause key (T39b). The session's mapper file (the G1 config's `[sdl] mapperfile`) is DOSBox-X
# 2024.03.01's own default bind set — saved by its mapper editor's Save button on a private Xvfb
# (MAPPER_DEFAULT, sha256 MAPPER_DEFAULT_SHA256) — with one change: `hand_pause` (the event the
# binary names mapper_pause, "Pause emulation") also answers F12+P. The file is complete because
# a mapper file DOSBox-X finds replaces its default binds (probe_pause log). In that default set
# F12+P (`key 19 host`, SDL scancode 19 = P) is the screenshot key `hand_scrshot`; the session file
# takes it from the screenshot (the recorder takes no screenshots) and keeps DOSBox-X's own Host+
# Pause (`key 72 host`) as a second pause bind. DOSBox-X appends " PAUSED" to the game window's
# title while paused (a string in its binary; probe_pause log): the recorder reads the pause from
# the title, the emulator's own state, never from guessing at the keys.
MAPPER_DEFAULT = Path(__file__).resolve().parent / "dosbox-x-2024.03.01-default.map"
MAPPER_DEFAULT_SHA256 = "1849ec80ad0b32949869ed8b2d38e7b2e1e89f5959965328b5f8c561196b589a"
PAUSE_BINDS = {'hand_pause "key 72 host" ': 'hand_pause "key 72 host" "key 19 host" ',
               'hand_scrshot "key 19 host" ': 'hand_scrshot '}
PAUSED_TITLE = " PAUSED"
# [designed] How often the loop reads the game window's title for the pause (one xdotool call,
# ~5 ms). A key event always triggers a read at once (a pause chord is keys), so this period only
# bounds how late a pause or resume with no logged key is seen. Recorder policy.
PAUSE_POLL_S = 0.25


def mapper_text(default=None):
    """The session's mapper file: DOSBox-X 2024.03.01's default binds with F12+P bound to pause
    (PAUSE_BINDS). Refuses a default file that is not the recorded one, or one missing a line it
    changes: a wrong mapper file would leave keys unbound for the whole sitting."""
    data = Path(default or MAPPER_DEFAULT).read_bytes()
    if sha256(data) != MAPPER_DEFAULT_SHA256:
        raise RuntimeError(f"{default or MAPPER_DEFAULT}: not DOSBox-X 2024.03.01's default mapper "
                           f"(sha256 {sha256(data)})")
    lines = data.decode("ascii").split("\n")
    for old, new in PAUSE_BINDS.items():
        if lines.count(old) != 1:
            raise RuntimeError(f"default mapper: the line {old!r} is not there exactly once")
        lines[lines.index(old)] = new
    return "\n".join(lines)


class Burst:
    """The pending key groups, one burst each. A group is a run of key events no two consecutive
    of which are BURST_QUIET_S apart; a new key at least a quiet interval after the group's last
    starts the next group. The oldest group is `due` once quiet has elapsed since its last key,
    and `consume()` drops it after its snapshot is taken.

    The groups are a queue, not one `last` (R2): keys that arrive while a burst snapshot is being
    captured are appended as their own groups, never merged into the one just snapshotted, so N
    groups produce N burst snapshots, one per loop pass. Each group keeps `first` (the pre-send
    start of the burst), `last` (the key that schedules its snapshot) and, once its save request
    has been sent, `request_time`/`sent` — the pre-send clock and the send's end, the window the
    map reads (T34 Sol-r2 R1a), recorded on the group at the moment of the send, never at
    staging."""

    def __init__(self, quiet=BURST_QUIET_S):
        self.quiet = quiet
        self.groups = []

    def add(self, event):
        t = event["monotonic_s"]
        if not self.groups or t >= self.groups[-1]["last"] + self.quiet:
            self.groups.append({"first": t, "last": t})
        else:
            self.groups[-1]["last"] = t

    def due(self, now):
        return bool(self.groups) and now >= self.groups[0]["last"] + self.quiet

    def consume(self):
        if self.groups:
            self.groups.pop(0)


class KeyParser:
    """Parse raw XI2 events only (ordinary events would duplicate each key)."""
    def __init__(self, symbols):
        self.symbols, self.event = symbols, None

    def line(self, line):
        if line.startswith("EVENT"):
            self.event = ("press" if "(RawKeyPress)" in line else
                          "release" if "(RawKeyRelease)" in line else None)
        elif self.event and line.strip().startswith("detail:"):
            code = int(line.split(":", 1)[1].strip())
            event, self.event = self.event, None
            return {"event": event, "keycode": code,
                    "keysym": self.symbols.get(code, f"keycode-{code}")}
        return None


class KeyLogger:
    """The only event source is the child display, never the outer desktop."""
    def __init__(self, env, outer_display, path):
        if not env.get("DISPLAY") or env["DISPLAY"] == outer_display:
            raise ValueError("key logger requires a distinct nested display")
        self.env, self.path = dict(env), Path(path)
        self.outer_display = outer_display   # never read from: kept for the error message only
        self.events = queue.Queue()
        self.proc, self.thread = None, None
        self.error = None

    def start(self):
        import ctypes
        xlib = ctypes.CDLL("libX11.so.6")
        xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
        xlib.XOpenDisplay.restype = ctypes.c_void_p
        xlib.XKeycodeToKeysym.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_int]
        xlib.XKeycodeToKeysym.restype = ctypes.c_ulong
        xlib.XKeysymToString.argtypes = [ctypes.c_ulong]
        xlib.XKeysymToString.restype = ctypes.c_char_p
        xlib.XCloseDisplay.argtypes = [ctypes.c_void_p]
        display = xlib.XOpenDisplay(self.env["DISPLAY"].encode())
        if not display:
            raise RuntimeError("cannot open nested display for key symbols")
        try:
            symbols = {}
            # X11 keycodes are one byte, with protocol range 8 through 255.
            for code in range(8, 256):
                name = xlib.XKeysymToString(xlib.XKeycodeToKeysym(display, code, 0))
                if name:
                    symbols[code] = name.decode()
        finally:
            xlib.XCloseDisplay(display)
        self.proc = subprocess.Popen(["stdbuf", "-oL", "xinput", "test-xi2", "--root"],
                                     env=self.env, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True,
                                     start_new_session=True)
        parser = KeyParser(symbols)

        def read():
            try:
                with open(self.path, "x", encoding="utf-8") as out:
                    for line in self.proc.stdout:
                        event = parser.line(line)
                        if event is not None:
                            event.update({"utc": datetime.now(timezone.utc).isoformat(),
                                          "monotonic_s": time.monotonic()})
                            out.write(json.dumps(event) + "\n")
                            out.flush()
                            self.events.put(event)
            except Exception as e:
                self.error = str(e)
        self.thread = threading.Thread(target=read, daemon=True)
        self.thread.start()

    def drain(self):
        events = []
        while True:
            try:
                events.append(self.events.get_nowait())
            except queue.Empty:
                return events

    def stop(self):
        terminate(self.proc)
        if self.thread:
            self.thread.join(timeout=2)
        if self.proc and self.proc.stdout:
            self.proc.stdout.close()


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def host_times():
    """The host clock now, as the driver writes it into records (UTC + local + zone)."""
    return driver.host_times()


def dosbox_version():
    """The version banner of the dosbox-x the recorder runs (driver.dosbox_x(), #117; it exits 1 and
    writes to stderr), or None."""
    try:
        out = subprocess.run([driver.dosbox_x(), "-version"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = [ln.strip() for ln in (out.stdout + out.stderr).splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("DOSBox-X version"):
            return ln
    return lines[0] if lines else None


def xdotool(args, env=None, timeout=10):
    """One xdotool call on the recorder's display; returns the CompletedProcess (never raises for
    a non-zero exit: callers check)."""
    return subprocess.run(["xdotool", *args], env=env, capture_output=True, text=True, timeout=timeout)


def xev_presses(path):
    """The KeyPress events an `xev` window received, parsed from its captured stdout (one JSON
    dict per press, in order). xev's KeyPress and KeyRelease lines both read
    `... keycode NN (keysym 0xNN, name), ...`; this records only the press line's keycode, so
    a press is listed once, not press-and-release.

    Used only by the privacy proof's positive control (R1): the foreign application's own log
    proves the keys were really typed on the outer display — a raw logger on that display would
    have seen them, so their absence from keys.jsonl is the privacy claim, not a silent no-op."""
    import re
    out = []
    event = None
    for line in Path(path).read_text(errors="replace").splitlines():
        if line.startswith("KeyPress event"):
            event = "press"
        elif line.startswith("KeyRelease event"):
            event = "release"
        elif event == "press":
            m = re.search(r"keycode (\d+) \(keysym 0x[0-9a-fA-F]+, ([^)]*)\)", line)
            if m:
                out.append({"event": "press", "keycode": int(m.group(1)), "keysym": m.group(2)})
                event = None
    return out


def key_cmd(wid):
    """The argv that sends the host save key. The focus gate lives here: with SEND_TO_WINDOW the
    keys go to the game window only (--window wid, an XSendEvent to that one window); turning the
    gate off would broadcast F12+S to whatever has the owner's focus, which is the hazard the
    brief forbids. The watcher never calls this with wid=None."""
    if not SEND_TO_WINDOW:
        return ["xdotool", "key", SAVE_KEYS]
    return ["xdotool", "key", "--window", str(wid), SAVE_KEYS]


def send_save_event(wid, env):
    """Explicit XSendEvent: xdotool uses XTEST for the focused window, which
    would feed our own snapshot keys back into the raw-input burst scheduler.
    X11 KeyPress/KeyRelease masks and event layouts are protocol constants.
    """
    import ctypes as c
    class KeyEvent(c.Structure):
        _fields_ = [("type", c.c_int), ("serial", c.c_ulong), ("send_event", c.c_int),
                    ("display", c.c_void_p), ("window", c.c_ulong), ("root", c.c_ulong),
                    ("subwindow", c.c_ulong), ("time", c.c_ulong), ("x", c.c_int),
                    ("y", c.c_int), ("x_root", c.c_int), ("y_root", c.c_int),
                    ("state", c.c_uint), ("keycode", c.c_uint), ("same_screen", c.c_int)]
    class Event(c.Union):
        _fields_ = [("key", KeyEvent), ("pad", c.c_long * 24)]
    lib = c.CDLL("libX11.so.6")
    lib.XOpenDisplay.argtypes, lib.XOpenDisplay.restype = [c.c_char_p], c.c_void_p
    lib.XDefaultRootWindow.argtypes, lib.XDefaultRootWindow.restype = [c.c_void_p], c.c_ulong
    lib.XKeysymToKeycode.argtypes, lib.XKeysymToKeycode.restype = [c.c_void_p, c.c_ulong], c.c_ubyte
    lib.XSendEvent.argtypes = [c.c_void_p, c.c_ulong, c.c_int, c.c_long, c.POINTER(Event)]
    lib.XFlush.argtypes = lib.XCloseDisplay.argtypes = [c.c_void_p]
    display = lib.XOpenDisplay(env["DISPLAY"].encode())
    if not display:
        raise RuntimeError("cannot open nested display to send save event")
    try:
        codes = [lib.XKeysymToKeycode(display, symbol) for symbol in (0xFFC9, ord("s"))]
        for kind, mask in ((2, 1), (3, 2)):
            for code in codes:
                event = Event()
                event.key.type, event.key.display = kind, display
                event.key.window, event.key.root = int(wid), lib.XDefaultRootWindow(display)
                event.key.keycode, event.key.same_screen = code, 1
                if not lib.XSendEvent(display, int(wid), 0, mask, c.byref(event)):
                    raise RuntimeError("save event send failed")
                lib.XFlush(display)
                # [designed] Match xdotool's roughly 6 ms inter-event spacing,
                # observed in T34-scripted-20261009-01.log's host-save events.
                time.sleep(0.006)
    finally:
        lib.XCloseDisplay(display)


def window_alive(wid, env):
    """Whether the game window still exists (a cheap named lookup; also the send's precondition —
    a vanished window means the sitting is over, never a blind send)."""
    return xdotool(["getwindowname", str(wid)], env=env).returncode == 0


def window_paused(wid, env):
    """Whether DOSBox-X is paused, from the game window's own title (DOSBox-X appends PAUSED_TITLE
    while its pause loop runs; T39b probe log); None when the title cannot be read. A read of the
    nested display's game window, never a key logger and never the outer display."""
    p = xdotool(["getwindowname", str(wid)], env=env)
    if p.returncode != 0:
        return None
    return PAUSED_TITLE in p.stdout


def window_pid(wid, env):
    """The X server's pid for the window (xdotool getwindowpid). Returns None on failure."""
    p = xdotool(["getwindowpid", str(wid)], env=env)
    if p.returncode != 0 or not p.stdout.strip():
        return None
    try:
        return int(p.stdout.strip())
    except ValueError:
        return None


def find_window(env, dbx_pid, timeout=15.0, sleep=time.sleep, clock=time.monotonic,
                search_class=WINDOW_CLASS):
    """The game window's id: polled like the driver's _wait_window, but the accept test is the
    window's pid matching `dbx_pid` (rework round 2 R1). The old search took the first class
    match — proved to bind to a *different* dosbox-x when more than one was on the display —
    sending F12+S to it produced no snapshot in the recorder's session. The new bind fails
    closed when no class window reports pid `dbx_pid` within `timeout`."""
    end = clock() + timeout
    while clock() < end:
        p = xdotool(["search", "--class", search_class], env=env)
        ids = [w for w in p.stdout.split() if w]
        for wid in ids:
            if window_pid(wid, env) == dbx_pid:
                return wid
        sleep(0.25)
    raise RuntimeError(f"no {search_class} window with pid {dbx_pid} within {timeout}s on "
                       f"DISPLAY={env.get('DISPLAY')!r}")


def window_geometry(wid, env):
    """(x, y, w, h) of the game window, for the video grab region; None when xdotool fails."""
    p = xdotool(["getwindowgeometry", "--shell", str(wid)], env=env)
    vals = {}
    for line in p.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    try:
        return int(vals["X"]), int(vals["Y"]), int(vals["WIDTH"]), int(vals["HEIGHT"])
    except (KeyError, ValueError):
        return None


def zip_is_complete(data):
    """A complete savestate zip: opens, tests clean, holds Vga, Memory, Save_Remark. Reads only
    the bytes given — never the live file. Used both at capture time (R3: the bytes you stage
    are validated, not a fresh read of the live file) and at the staging gate (the shutdown
    pass: R4 — the live file is read after the emulator is gone, then the captured bytes are
    validated before any I/O on the shared state)."""
    if not isinstance(data, (bytes, bytearray)):
        return False
    try:
        with zipfile.ZipFile(__import__("io").BytesIO(bytes(data))) as z:
            names = z.namelist()
            return (z.testzip() is None and "Vga" in names and "Memory" in names
                    and "Save_Remark" in names)
    except (zipfile.BadZipFile, OSError):
        return False


def zip_complete(path):
    """The savestate zip's bytes when `path` holds a complete one, else None. Read-only: the
    live file is never touched (the staging gate); used by callers that need to peek the file
    before the watcher's capture step."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    return bytes(data) if zip_is_complete(data) else None


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def file_signature(path):
    """The live file's identity without reading its content: (inode, size, mtime_ns, ctime_ns),
    or None when it is missing. The staging gate compares signatures, never bytes, so nothing
    reads the live savestate before it has held still (round-2 R1: the pre-send digest read an
    in-progress write). A rewrite of the same length still moves mtime_ns/ctime_ns (round-2 R2)."""
    try:
        st = os.stat(path)
    except OSError:
        return None
    return (st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def sig_hash(sig):
    """A signature's digest as it goes into a request line: sha256 over the canonical JSON of
    (inode, size, mtime_ns, ctime_ns), or over `null` when the file was absent (the opening
    tick, before the first save created it). note_request records the request's PRE-SEND
    signature and its accept-time signature this way (T35, issue #111 R2), so the acceptance
    guard can require a pre-send state and an accept-time state that DIFFER — a fresh write
    inside this request's own window — while still never reading the live savestate's bytes
    before the key is sent (T35 R1 forbids that read; this is metadata only)."""
    return sha256(json.dumps(list(sig) if sig is not None else None).encode("utf-8"))


class WriteWatch:
    """Whether a write session on the live savestate is still open, from the kernel's inotify
    events on its directory (round-4 R1). A writer that pauses mid-write leaves the file's bytes
    and metadata still, so stillness cannot show the write is over. The kernel can: IN_MODIFY
    (a write, or an O_TRUNC open) opens a session, and IN_CLOSE_WRITE (the writer closed it) or
    IN_MOVED_TO (a finished file renamed into place) ends it. Our own reads raise neither.
    /proc/<pid>/fd cannot serve: /usr/bin/dosbox-x carries cap_net_raw, so the kernel makes it
    non-dumpable and hides its descriptors even from its parent (found 2026-10-08).
    An event queue overflow (IN_Q_OVERFLOW) counts as an open session until the next close:
    the check fails closed."""
    IN_MODIFY, IN_CLOSE_WRITE, IN_MOVED_TO, IN_Q_OVERFLOW = 0x2, 0x8, 0x80, 0x4000
    IN_NONBLOCK, IN_CLOEXEC = 0o4000, 0o2000000

    def __init__(self, path):
        import ctypes
        import ctypes.util
        self.name = Path(path).name.encode()
        libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
        self.fd = libc.inotify_init1(self.IN_NONBLOCK | self.IN_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), "inotify_init1 failed")
        wd = libc.inotify_add_watch(self.fd, str(Path(path).parent).encode(),
                                    self.IN_MODIFY | self.IN_CLOSE_WRITE | self.IN_MOVED_TO)
        if wd < 0:
            err = ctypes.get_errno()
            os.close(self.fd)
            raise OSError(err, f"inotify_add_watch on {Path(path).parent} failed")
        self.open_session = False
        self.events = 0                   # write events on the file seen so far (round-6 R1)

    def writing(self):
        """Drain the pending events; True while a write session on the file is open."""
        while True:
            try:
                buf = os.read(self.fd, 65536)
            except BlockingIOError:
                return self.open_session
            i = 0
            while i < len(buf):
                _wd, mask, _cookie, size = struct.unpack_from("iIII", buf, i)
                name = buf[i + 16:i + 16 + size].rstrip(b"\0")
                i += 16 + size
                if mask & self.IN_Q_OVERFLOW:
                    self.open_session = True
                    self.events += 1
                elif name == self.name:
                    self.events += 1
                    if mask & (self.IN_CLOSE_WRITE | self.IN_MOVED_TO):
                        self.open_session = False
                    elif mask & self.IN_MODIFY:
                        self.open_session = True

    def activity(self):
        """(a write session is open, the number of write events so far), after draining."""
        busy = self.writing()
        return busy, self.events

    def close(self):
        os.close(self.fd)


class Watcher:
    """The snapshot loop: one tick every CADENCE_S — send the host save key straight to the game
    window, wait for a complete and size-stable live savestate, stage a copy, append the index.

    clock/sleep/xrun and dbx.poll() are injectable so tests run the whole loop on a fake clock
    with no emulator. `stop` is polled between ticks (the SIGINT/SIGTERM flag).

    Every staging decision passes through the staging gate (R3, R4, R6): the bytes are captured
    once (single read after size-stable for STABLE_POLLS polls), the captured bytes are validated
    as a complete zip (NOT a fresh read of the live file), a concurrent change between capture
    and validation is rejected, and the captured bytes differ from the pre-send snapshot of
    the live file (evidence of a fresh write, not the previous tick's savestate re-indexed)."""

    # The pause (T39b). Class defaults, so a Watcher made without __init__ (the loop tests) is a
    # sitting that never pauses.
    pause_probe = None        # () -> True while DOSBox-X is paused (window_paused), else no pause
    paused = False            # the latest read of the pause
    pause_epoch = 0           # pauses seen so far: a capture compares it with its request's
    pauses_path = None        # pauses.jsonl: one flushed line per pause and per resume
    resume_due = False        # a resume was seen and its snapshot request is not yet sent
    _pause_since = None
    _hold_logged = False
    _events_at_pause = None   # {pause epoch: the write-event count when that pause was seen}

    def __init__(self, session, live, wid, dbx, env, t0=None, index="index.jsonl",
                 clock=time.monotonic, sleep=time.sleep, xrun=None, alive=None, log=None,
                 writing=None, watch=None, paused=None):
        self.session = Path(session)
        self.live = Path(live)
        self.wid = wid
        self.dbx = dbx
        self.env = env
        self.clock = clock
        self.sleep = sleep
        self.xrun = xrun or (lambda argv: xdotool(argv[1:], env=env))
        self.alive = alive or (lambda: window_alive(wid, env))
        self.log = log or (lambda msg: None)
        # the live savestate's write activity (round-4/6 R1): `activity()` gives (a write session
        # is open, the number of write events so far); an injected `writing` has no event count
        if writing is None:
            # `watch`: the sitting's own WriteWatch, started before the emulator was launched, so
            # its count covers every save of the sitting (Sol's round-3 R1 on PR 112)
            ww = watch if watch is not None else WriteWatch(self.live)
            self.activity = ww.activity
        else:
            self.activity = lambda: (writing(), 0)
        self.index_path = self.session / index
        # every save request, staged or skipped (T34 R2): the map must know a missing snapshot
        self.requests_path = self.session / "requests.jsonl"
        self.last_sent = None
        self.last_staged_request = None
        self.snapshots = self.session / "snapshots"
        self.t0 = self.clock() if t0 is None else t0
        self.seq = 0
        self.problems = []
        # the last fast capture's (event count, signature): what the pipeline already consumed,
        # and its pending-job watermark (submitted - finished > 1 at a job's first poll means
        # later requests were already queued before that job began — Sol delta r3 R1's
        # deferred-capture signal; one writer thread, no lock needed)
        self._fast_consumed = None
        self._submitted = 0
        self._finished = 0
        self._request_seq = 0            # pipeline requests, for the per-request savestate path
        self.pause_probe = paused
        self.pauses_path = self.session / "pauses.jsonl"

    # -- staging (the staging gate) -----------------------------------------------------
    def capture(self, pre_sig, live_emulator=True, pre_events=None, fast=False, sent_box=None,
                req_path=None, epoch=None):
        """The staging gate, the one path that reads the live savestate (round 2: R1, R2, R4,
        and the R9 follow-up). Iterative, one deadline:

        1. poll the file's signature (file_signature: metadata only, no content read) until it
           has been identical for STABLE_POLLS consecutive polls;
        2. require that signature to differ from `pre_sig`, the one taken before the key was
           sent (evidence of a fresh write; R6), when `pre_sig` is given;
        3. check that no write session on the file is open (WriteWatch: an IN_MODIFY not yet
           followed by IN_CLOSE_WRITE), and note the kernel's write-event count; read the bytes
           once (read-only) and validate THOSE bytes as a complete zip; then take the event
           count again: any write event on the file in between — a write that began, ended or
           rewrote identical bytes during the read, which neither the content nor coarse
           timestamps can show — rejects the bytes and counting restarts (rounds 4-6 R1). An
           event-queue overflow counts as a write event; a check that cannot be made rejects:
           fail closed. The writer model is single-writer (the task's hazards): the session
           folder is private and the launched DOSBox-X its only writer.

        With `live_emulator`, a dead emulator ends the sitting (_EmulatorGone, R5) and the key
        is re-sent after RESEND_AFTER_S (`sent_box[0]`, when given, receives the last send's
        clock, so a pipeline job's window widens to it). Returns the 4-tuple documented at the
        end of this docstring; raises TimeoutError.

        With `fast` and `pre_events` (the write-event count taken before the request was sent,
        T34 Sol-r2 R1), the kernel replaces the 0.75 s stability wait as the write-completed
        evidence: an event count past `pre_events` means inotify saw this request's write close
        (IN_CLOSE_WRITE/IN_MOVED_TO) — the same completed-write fact STABLE_POLLS polls infer
        from 0.75 s of quiet, available at the speed overlapping burst requests need: keys
        ~0.53 s apart rewrite the live file faster than the stability window could ever elapse
        between two writes. Every other check is unchanged (fresh signature vs `pre_sig`, no
        open write session, the event-count bracket around the read, zip validation). A count
        of None (the check failed) never takes the fast path: fail closed.

        Per-request attribution (Sol delta r3 R1). A real DOSBox-X save is fast — the whole
        write (many close events; 27 were measured on this host for one save) can complete
        before the worker's first poll — so "the job began before its save completed" cannot be
        the test. What makes an already-completed, UNCONSUMED write (its event count and
        signature differ from the last accepted capture's) unattributable is the pipeline
        having moved past this job: when later requests were already submitted before this
        job began (lag > 1), such a write is some LATER request's save, and staging its bytes
        under this request's window misattributes the screen — the deferred capture of the r3
        reproduction (a stage job that waited while later requests overwrote the live file).
        That raises _AttributionLost; the caller marks the request superseded and the
        acceptance guard rejects the sitting (r3 R2). With lag == 1 (this job is the pipeline's
        head) the only save past the pre-send count is this request's own: accepted at once. A
        job that begins before its save completes accepts on FRESH ARRIVAL — at least one
        write event arriving during its polling, the count past its first poll's. Bytes
        already consumed by the previous acceptance are never re-staged, and identical bytes
        from an unchanged screen are NOT rejected: the rules compare event counts and
        signatures against the pipeline's own consumption, never hashes.

        Request ownership on every poll (Sol delta r4 R1): a pipeline job whose live savestate
        has advanced by more than ONE_SAVE_MAX_EVENTS write events since its request was sent
        is reading a LATER request's save — _AttributionLost on the first-poll path, the
        fresh-arrival path and the stability fallback alike. With `req_path`, the accepted
        bytes are also written to that per-request path (the single source of truth the
        staging reads back), and a fast job never stages from a merely stable live file.

        The unanchored capture (T35, issue #111 R1): FRESH ARRIVAL accepts a write that landed
        while this job polled, which is its own save only while no OTHER save request could
        have produced it. A capture that began with later save requests already queued
        (`_submitted - _finished > 1` at its first poll) and with an EMPTY consumption ledger
        (`_fast_consumed` is None: the pipeline has staged nothing yet) has nothing to order
        those saves by — the Sol delta r4 R1 reproduction injects exactly that state
        (`--_submitted=2 --_finished=0`, the write landing one poll in and within one save's
        bound, so the magnitude check does not fire) and the live file then carries a later
        request's save. Such a capture raises _AttributionLost instead of accepting: the
        request is marked superseded, the acceptance guard rejects the sitting, and the
        stability fallback — which NEVER reads the live savestate (stability says nothing
        about whose save is on it; the per-request path, the only source it may read, holds
        this request's bytes only when this job accepted, which it did not) — is what the
        shapes that reach it fall through to. A capture that was the head at its first poll,
        or that follows an already-consumed write, keeps the fresh-arrival path: the ledger or
        the head position orders the saves.

        Returns (bytes, sha256, accept_events, accept_sig): the write-event count and the live
        savestate's signature at the accepted capture — the ownership evidence note_request
        records and the guard checks. accept_events is None on the non-fast paths (no event
        accounting there); accept_sig is then the signature the stable bytes were read under."""
        deadline = self.clock() + SAVE_TIMEOUT_S
        sent = self.clock()
        last_sig, count = None, 0
        entry_events = None               # the event count at this job's first poll
        entry_head = False                # the pipeline had no later request queued then (T35)
        while self.clock() < deadline:
            if live_emulator and self.dbx.poll() is not None:
                self.log(f"dosbox-x exited with code {self.dbx.returncode} during a savestate")
                raise _EmulatorGone(self.dbx.returncode)
            busy, events = self._write_state()
            # r4 R1: request ownership on BOTH capture paths. More than one save's
            # write events since this request was sent mean the live savestate holds
            # a LATER request's save (the single serialized writer answers requests
            # in order; one save is ~53-54 events on this host, ONE_SAVE_MAX_EVENTS
            # bounds it). The check runs at EVERY poll of a pipeline job, so it
            # covers the first-poll fast path, the fresh-arrival path AND the
            # stability fallback — the r3 lag check saw only the first poll.
            if (fast and pre_events is not None and events is not None
                    and events - pre_events > ONE_SAVE_MAX_EVENTS):
                raise _AttributionLost(
                    f"{events - pre_events} write events on the live savestate since this "
                    f"request was sent (more than one save's bound of {ONE_SAVE_MAX_EVENTS}): "
                    "a later request's savestate has already overwritten it "
                    "(request attribution lost)")
            # T39b: a pause that began after this request was sent. DOSBox-X writes no
            # savestate while paused (probe_pause log), so a write past the event count at
            # that pause's start landed after the resume: post-resume play, never this
            # request's screen (the hazard of a save that "lands after resume as if it were
            # later play"). Refused like any write this request does not own.
            after_pause = (self._events_at_pause or {}).get(None if epoch is None else epoch + 1)
            if (after_pause is not None and events is not None and events > after_pause):
                raise _AttributionLost(
                    f"a savestate write landed after a pause that began after this request "
                    f"({events} write events, {after_pause} at the pause): post-resume play, "
                    "not this request's screen (request attribution lost)")
            sig = file_signature(self.live)
            first_poll = entry_events is None
            if first_poll:
                entry_events = events
                # T35 (issue #111 R1): was this capture the pipeline's head when it began?
                # With later save requests already queued, a write landing while it polls
                # could be theirs — the ledger below is what orders the saves, and an empty
                # one (nothing consumed yet) orders nothing.
                entry_head = self._submitted - self._finished <= 1
            fast_ready = (fast and pre_events is not None and events is not None
                          and events > pre_events and not busy and sig is not None
                          and (pre_sig is None or sig != pre_sig))
            accept = False
            if fast_ready:
                if self._fast_consumed == (events, sig):
                    # r4 R1: bytes an earlier job already staged are never re-staged
                    # on any path; this request's own write has not arrived (the
                    # deadline bounds the wait)
                    pass
                elif first_poll:
                    if self._submitted - self._finished > 1:
                        raise _AttributionLost(
                            "a savestate write completed before this capture began while later "
                            "requests were already pending (deferred capture: request "
                            "attribution lost: lost boundary)")
                    accept = True   # the pipeline's head: the completed write is its own save
                elif (events is not None and entry_events is not None
                      and events > entry_events
                      and (entry_head or self._fast_consumed is not None)):
                    accept = True   # a write event arrived while this job polled: a fresh save
                elif (events is not None and entry_events is not None
                      and events > entry_events):
                    # T35 (issue #111 R1): the write arrived, but this capture began with
                    # later save requests queued and the pipeline has consumed nothing, so
                    # nothing orders those saves — the live file's write cannot be tied to
                    # this request. The Sol delta r4 R1 reproduction injects exactly this
                    # (an injected clock, `_submitted=2/_finished=0`, a later request's save
                    # landing one poll in, within one save's bound of write events so the
                    # every-poll magnitude check does not fire). Not accepted: _AttributionLost
                    # marks the request superseded, and the stability fallback never runs for
                    # a job that no longer owns its window (its log line is what the
                    # reproduction's report quotes for the shapes that reach it).
                    raise _AttributionLost(
                        "a write arrived while later save requests were queued and the "
                        "pipeline has consumed nothing: the live savestate's write cannot be "
                        "tied to this request (unanchored capture: request attribution lost)")
            if accept:
                # the write is finished (the fact the stability polls wait 0.75 s to infer),
                # the signature is fresh, and no session is open — read once, bracketed by the
                # event count exactly as the stability path does
                data = self._read_live()
                if data is not None and zip_is_complete(data):
                    _, after = self._write_state()
                    if after == events:
                        if req_path is not None and not self._write_request_bytes(req_path, data):
                            self.log("per-request savestate could not be written: retrying")
                            last_sig, count = None, 0
                        else:
                            self._fast_consumed = (events, sig)
                            return data, sha256(data), events, sig
                self.log("live savestate changed or incomplete during capture: retrying")
                last_sig, count = None, 0
            if sig is None or sig[1] == 0:
                last_sig, count = None, 0
            elif sig == last_sig:
                count += 1
            else:
                last_sig, count = sig, 1
            if count >= STABLE_POLLS and (pre_sig is None or last_sig != pre_sig):
                # r4 R1(c): a pipeline job NEVER stages a stable live file — stability
                # says nothing about WHOSE save is on it (the stability-fallback
                # bypass restaged bytes the pipeline had already consumed this way);
                # only the write accounting above can own bytes, so the job keeps
                # polling for its own write and the deadline bounds the wait.
                # T35 (issue #111 R1): the fallback's only source is the PER-REQUEST
                # path, and a job reaches this point without one (its per-request copy
                # is written at acceptance, which returns), so it stages nothing and
                # never reads the live savestate here.
                if fast:
                    self.log("stability fallback: stable live savestate not staged on the "
                             "fast path (no owned write; only the per-request path may be "
                             "read, and it holds no bytes for this request)")
                else:
                    # bytes read while a write was in progress are never staged (the task's
                    # hazard, b7777fd): no read starts while a session is open, and any write
                    # event between the check before the reads and the one after them rejects
                    # the bytes — the kernel's event count sees a write the content and the
                    # timestamps cannot (round-6 R1). Reads are read-only and cannot disturb
                    # the writer.
                    busy, before = self._write_state()
                    if busy:
                        self.log("a write session on the savestate is still open: waiting")
                        self.sleep(POLL_S)
                        continue
                    data = self._read_live()
                    if data is not None and zip_is_complete(data):
                        _, after = self._write_state()
                        if after == before:            # None (check failed) never equals a count
                            return data, sha256(data), None, last_sig
                    self.log("live savestate changed or incomplete during capture: retrying")
                    last_sig, count = None, 0
            if (live_emulator and self.clock() - sent > RESEND_AFTER_S
                    and (self.paused or (epoch is not None and epoch != self.pause_epoch))):
                # T39b: no save request while paused, and none for a request a pause began
                # after: DOSBox-X drops a save key while paused (probe_pause log), so a resend
                # after the resume would stage post-resume play under this pre-pause window.
                # The request waits for its own write until the deadline, then stages nothing.
                if not self._hold_logged:
                    self.log("F12+S not sent again: a pause began after this request")
                    self._hold_logged = True
            elif live_emulator and self.clock() - sent > RESEND_AFTER_S:
                self.log(f"F12+S sent again: no complete savestate after {RESEND_AFTER_S}s")
                self.xrun(key_cmd(self.wid))
                sent = self.last_sent = self.clock()
                if sent_box is not None:
                    sent_box[0] = sent
            self.sleep(POLL_S)
        raise TimeoutError(f"savestate not complete and stable within {SAVE_TIMEOUT_S}s")

    def _write_state(self):
        """(a write session is open, the write-event count); when it cannot be told, (True, None):
        fail closed."""
        try:
            busy, events = self.activity()
            return bool(busy), events
        except OSError as e:
            self.log(f"writer check failed ({e}): treating as a write in progress")
            return True, None

    def _read_live(self):
        """The live savestate's bytes, or None when it cannot be read. Called only by `capture`,
        after the signature has held still (the staging gate's only content read)."""
        try:
            with open(self.live, "rb") as f:
                return f.read()
        except OSError:
            return None

    def _write_request_bytes(self, req_path, data):
        """Atomically write a request's owned savestate bytes to its per-request path (r4 R1a):
        tmp file + rename in the same folder, so a reader never sees a half-written file. The
        per-request path is the SINGLE source of truth for the bytes staged under a request's
        window; the live savestate is only an intermediate."""
        try:
            req_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = req_path.with_name(req_path.name + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(req_path)
            return True
        except OSError as e:
            self.log(f"per-request savestate write failed ({e})")
            return False

    def stage(self, data, digest, origin="watcher", request=None, sent=None):
        """Copy the bytes to snapshots/ (the live file is not moved or renamed), append one index
        line (flushed at once, so an abrupt end leaves a valid prefix). `digest` is the sha256 of
        `data` as captured, so the line matches the bytes on disk exactly (R3)."""
        self.seq += 1
        name = f"snap-{self.seq:04d}-{utc_stamp()}.sav"
        out = self.snapshots / name
        out.write_bytes(data)
        entry = {"seq": self.seq, "file": f"snapshots/{name}", "bytes": len(data), "sha256": digest,
                 "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                 "elapsed_s": round(self.clock() - self.t0, 3), "origin": origin,
                 # the save request's window (T34 R1): the screen was taken between the clock read
                 # before the first send and the end of the last send, not at staging (elapsed_s)
                 "request_s": None if request is None else round(request - self.t0, 3),
                 "sent_s": None if sent is None else round(sent - self.t0, 3)}
        if request is not None and origin != "shutdown":
            self.last_staged_request = request
        with open(self.index_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.log(f"staged {entry['file']} ({len(data)} bytes, sha256 {entry['sha256'][:16]}...)")
        return entry

    def tick(self, video=None, origin="watcher", submit=None):
        """One snapshot: send the host key to the game window, then stage when stable. The pre-send
        signature (metadata only) is taken before the key is sent so `capture` can require a
        fresh write (R6). If `video` is not None, its `poll_growth()` is called between key and stage (R16).

        With `submit` (the capture pipeline, T34 Sol-r2 R1), the request is sent here and the
        staging is handed to the pipeline: the loop never waits for a savestate while later keys
        arrive, and each group's window is its own send's. Returns the staged entry, or None
        (skipped or pipelined)."""
        if not self.alive():
            raise StopIteration("game window is gone")
        pre = file_signature(self.live)
        _, pre_events = self._write_state()   # the write-event count before this request
        epoch = self.pause_epoch              # the pauses seen before this request (T39b)
        request = self.clock()
        self.xrun(key_cmd(self.wid))
        self.last_sent = self.clock()
        self.last_request = request
        self.log(f"F12+S sent to window {self.wid}")
        if video is not None:
            video.poll_growth()
        if submit is not None:
            submit(pre, request, self.last_sent, origin, pre_events, epoch)
            return None
        try:
            data, digest, _, accept_sig = self.capture(pre, epoch=epoch)
        except TimeoutError as e:
            self.problems.append(str(e))
            self.log(f"snapshot skipped: {e}")
            self.note_request(request, self.last_sent, origin, None, pre_sig=sig_hash(pre))
            return None
        except _AttributionLost as e:
            # T39b: a write after a pause that began after this request is not its own
            self.problems.append(str(e))
            self.log(f"request superseded: {e}")
            self.note_request(request, self.last_sent, origin, None, superseded=True,
                              pre_sig=sig_hash(pre))
            return None
        except _EmulatorGone:
            self.note_request(request, self.last_sent, origin, None, pre_sig=sig_hash(pre))
            raise
        entry = self.stage(data, digest, origin=origin, request=request, sent=self.last_sent)
        self.note_request(request, self.last_sent, origin, entry["seq"],
                          pre_sig=sig_hash(pre), accept_sig=accept_sig)
        return entry

    def note_request(self, request, sent, origin, seq, superseded=False, pre_events=None,
                     accept_events=None, request_file=None, request_sha256=None,
                     pre_sig=None, accept_sig=None):
        """One flushed line per save request in requests.jsonl; `seq` is the staged entry's, None
        for a request that staged nothing (a skipped snapshot), which keymap.py counts as a screen
        it could not see (T34 R2). `sent` is this request's own last send (a resend widens the
        window to it), never whatever send happened to be the watcher's latest. `superseded`
        (Sol delta r3 R1) marks a request whose capture found a LATER request's write already on
        the live savestate: it staged nothing by design, and the acceptance guard rejects the
        sitting (R2) rather than certify a boundary it does not own.

        The ownership evidence fields (Sol delta r4 R2) — `pre_events` (the write-event count
        before this request was sent), `accept_events` (the count when its own write was
        accepted), `request_file`/`request_sha256` (the per-request savestate the bytes were
        staged from) — are what the guard's attribution check REQUIRES on a staged line:
        absence of `superseded` alone proved nothing (the r4 bypasses produced ordinary
        successful lines).

        T35 (issue #111 R2) adds the signature pair: `pre_sig`, the live savestate's signature
        hash taken before this request was sent, and `accept_sig`, its hash at the accepted
        capture. Both on the line, the guard can require a pre-send state that DIFFERS from the
        accept-time state — a fresh write inside this request's own window — which is the
        closest thing to a byte-level proof of ownership that never reads the live savestate
        before the send (round-2 R1). A staged line without the pair is evidence-free and the
        guard rejects the sitting."""
        line = {"request_s": round(request - self.t0, 3),
                "sent_s": round(sent - self.t0, 3), "origin": origin, "seq": seq}
        if superseded:
            line["superseded"] = True
        if pre_events is not None:
            line["pre_events"] = pre_events
        if accept_events is not None:
            line["accept_events"] = accept_events
        if request_file is not None:
            line["request_file"] = request_file
        if request_sha256 is not None:
            line["request_sha256"] = request_sha256
        if pre_sig is not None:
            # the line always carries the digest: a caller may hand over the signature tuple
            line["pre_sig"] = pre_sig if isinstance(pre_sig, str) else sig_hash(pre_sig)
        if accept_sig is not None:
            line["accept_sig"] = accept_sig if isinstance(accept_sig, str) else sig_hash(accept_sig)
        with open(self.requests_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
            f.flush()

    def _stage_job(self, pre, request, sent, origin, pre_events, req_path=None, epoch=None):
        """One pipeline job: the staging gate for a request already sent (fast: the kernel's
        write-event count is the write-completed evidence), then stage + note_request. A
        timeout marks THIS request as staged-nothing — the group is skipped and its bursts
        unmapped, never silently covered by a later group's snapshot (T34 Sol-r2 R1c) — and a
        lost attribution (Sol delta r3 R1, r4 R1) marks it superseded the same way: no snapshot
        is staged under a window whose bytes belong to another request. A dead emulator re-raises
        _EmulatorGone for the pipeline to flag the loop (R5).

        r4 R1(a)/(b): the staged bytes come from the request's per-request path, re-read and
        verified (present, hash equal to the accepted digest, a complete zip) — the live
        savestate is only the intermediate; a verification failure is a lost attribution."""
        box = [sent]
        pre_digest = sig_hash(pre)      # the pre-send state, recorded on every line (T35)
        try:
            data, digest, accept_events, accept_sig = self.capture(
                pre, pre_events=pre_events, fast=True, sent_box=box, req_path=req_path,
                epoch=epoch)
        except TimeoutError as e:
            self.problems.append(str(e))
            self.log(f"snapshot skipped: {e}")
            self.note_request(request, box[0], origin, None, pre_events=pre_events,
                              pre_sig=pre_digest)
            return None
        except _AttributionLost as e:
            self.problems.append(str(e))
            self.log(f"request superseded: {e}")
            self.note_request(request, box[0], origin, None, superseded=True,
                              pre_events=pre_events, pre_sig=pre_digest)
            return None
        except _EmulatorGone:
            self.note_request(request, box[0], origin, None, pre_events=pre_events,
                              pre_sig=pre_digest)
            raise
        if req_path is not None:
            try:
                owned = req_path.read_bytes()
            except OSError:
                owned = None
            if owned is None or sha256(owned) != digest or not zip_is_complete(owned):
                e = "the per-request savestate is missing or not the accepted bytes"
                self.problems.append(e)
                self.log(f"request superseded: {e}")
                self.note_request(request, box[0], origin, None, superseded=True,
                                  pre_events=pre_events, pre_sig=pre_digest)
                return None
            data = owned
        entry = self.stage(data, digest, origin=origin, request=request, sent=box[0])
        self.note_request(request, box[0], origin, entry["seq"], pre_events=pre_events,
                          accept_events=accept_events,
                          request_file=str(req_path.relative_to(self.session))
                          if req_path is not None else None,
                          request_sha256=digest,
                          pre_sig=pre_digest, accept_sig=accept_sig)
        return entry

    # -- the pause (T39b) ----------------------------------------------------------------
    def poll_pause(self):
        """Read the pause (pause_probe: the game window's title) and log a change to pauses.jsonl,
        one flushed line per pause and per resume, with UTC, the monotonic clock and the sitting's
        elapsed seconds. A pause bumps pause_epoch (the captures of earlier requests never resend
        after it); a resume makes the resume snapshot due. An unreadable title (None) changes
        nothing. Returns whether the sitting is paused."""
        now_paused = self.pause_probe()
        if now_paused is None or bool(now_paused) == self.paused:
            return self.paused
        now = self.clock()
        line = {"event": "pause" if now_paused else "resume",
                "utc": datetime.now(timezone.utc).isoformat(),
                "monotonic_s": now, "elapsed_s": round(now - self.t0, 3)}
        if now_paused:
            self.pause_epoch += 1
            self._pause_since = now
            # the writes before this pause: a capture of an earlier request refuses any past it
            if self._events_at_pause is None:
                self._events_at_pause = {}
            self._events_at_pause[self.pause_epoch] = (
                self._write_state()[1] if hasattr(self, "activity") else None)
            # DOSBox-X 2024.03.01 writes no savestate while paused and drops the request
            # (probe_pause log), so the pause's snapshot is requested right after it ends
            line["snapshot"] = "after-resume"
        else:
            line["paused_s"] = (None if self._pause_since is None
                                else round(now - self._pause_since, 3))
            self.resume_due = True
        self.paused = bool(now_paused)
        with open(self.pauses_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
            f.flush()
        self.log(f"{line['event']} at +{line['elapsed_s']:.3f}s")
        return self.paused

    # -- the loop -----------------------------------------------------------------------
    def run(self, quit_after=None, stop=lambda: False, video=None, keys=None):
        """Tick at t0 + n*CADENCE_S (the first tick immediately: the session's opening state is
        part of the chain) until the window closes, dosbox-x exits, `stop()` fires or (scripted
        sittings) quit_after seconds have passed. Returns the staged entries.

        With `keys`, staging runs on a capture pipeline off the loop (T34 Sol-r2 R1): each
        settled key episode's save request is sent EVENT_SETTLE_S after its newest event —
        after that key's release, and between it and the next key where a due-time window
        (last key + BURST_QUIET_S) could never fit for keys spaced just over the quiet. The
        capture/staging of every request happens in the worker, so a slow savestate never
        delays the next request; each episode is bracketed by (Burst.request_time, its
        staging time)."""
        entries, n = [], 0
        burst = Burst()
        self.last_request = self.last_sent = None
        last_event = float("-inf")   # the newest key event seen (presses AND releases)
        jobs = queue.Queue()
        staged = []          # the pipeline's entries, in staging order
        dead = []            # _EmulatorGone raised inside the pipeline (R5)

        def submit(pre, request, sent, origin, pre_events, epoch=None):
            self._submitted += 1
            self._request_seq += 1
            (self.session / "requests").mkdir(exist_ok=True)
            jobs.put((pre, request, sent, origin, pre_events,
                      self.session / "requests" / f"rq-{self._request_seq:04d}.sav", epoch))

        def pipeline():
            while True:
                job = jobs.get()
                if job is None:
                    return
                try:
                    entry = self._stage_job(*job)
                except _EmulatorGone as e:
                    dead.append(e)
                    jobs.task_done()
                    return
                finally:
                    self._finished += 1
                if entry is not None:
                    staged.append(entry)
                jobs.task_done()

        worker = threading.Thread(target=pipeline, daemon=True, name="capture-pipeline")
        worker.start()
        next_pause_poll = float("-inf")
        try:
            while True:
                drained = keys.drain() if keys else []
                for event in drained:
                    burst.add(event)
                if drained:
                    last_event = drained[-1]["monotonic_s"]
                if keys and (keys.error or keys.proc.poll() is not None):
                    raise RuntimeError(f"key logger stopped: {keys.error}")
                if dead:
                    self.log(f"emulator gone ({dead[0].returncode}): ending the loop cleanly")
                    break
                if stop():
                    self.log("stop requested")
                    break
                if quit_after is not None and self.clock() - self.t0 >= quit_after:
                    self.log(f"quit-after {quit_after}s reached")
                    break
                if self.dbx.poll() is not None:
                    self.log(f"dosbox-x exited with code {self.dbx.returncode}: the sitting is over")
                    break
                now = self.clock()
                # T39b: the pause is read from the game window's title after every key event
                # (a pause is typed) and every PAUSE_POLL_S
                if self.pause_probe is not None and (drained or now >= next_pause_poll):
                    self.poll_pause()
                    next_pause_poll = now + PAUSE_POLL_S
                if self.paused:
                    # no save request while paused (DOSBox-X would drop it: probe_pause log):
                    # the cadence ticks that fall in the pause are skipped, and the key groups
                    # typed before and during it wait for the resume's request (no key lost)
                    while self.t0 + n * CADENCE_S <= now:
                        n += 1
                    self.sleep(0.01 if keys else PAUSE_POLL_S)
                    continue
                next_tick = self.t0 + n * CADENCE_S
                # the settled episode's request goes out EVENT_SETTLE_S after the newest key
                # event: after that key's release, and — for keys spaced just over the
                # grouping quiet (the 0.527 s reproduction) — still between it and the next
                # key, where a due-time window could never fit; see EVENT_SETTLE_S
                send_burst = bool(burst.groups) and now >= last_event + EVENT_SETTLE_S
                # the snapshot of a pause, right after it ends (DOSBox-X writes none while
                # paused), once the resume's own keys have settled
                send_resume = self.resume_due and now >= last_event + EVENT_SETTLE_S
                if now < next_tick and not send_burst and not send_resume:
                    self.sleep(min(next_tick - now, 0.01 if keys else 0.5))
                    continue
                if self.pause_probe is not None and self.poll_pause():
                    # a fresh read before every send: a pause typed within its own keys'
                    # settle is seen here, not after a request DOSBox-X would drop
                    next_pause_poll = self.clock() + PAUSE_POLL_S
                    continue
                if now >= next_tick:
                    n += 1
                if send_resume:
                    try:
                        e = self.tick(video=video, origin="resume",
                                      submit=submit if keys else None)
                    except StopIteration as e:
                        self.log(str(e))
                        break
                    except _EmulatorGone as e:
                        self.log(f"emulator gone ({e.returncode}): ending the loop cleanly")
                        break
                    self.resume_due = False
                    # every key group typed before this request (the pause chord, keys typed
                    # while paused, the resume key) lies before its window: one request
                    # brackets them all, not one per group of a span DOSBox-X did not run
                    burst.groups.clear()
                    if e:
                        entries.append(e)
                elif send_burst:
                    head = burst.groups[0]
                    try:
                        e = self.tick(video=video, origin="burst",
                                      submit=submit if keys else None)
                    except StopIteration as e:
                        self.log(str(e))
                        break
                    except _EmulatorGone as e:
                        # R5: clean termination, not an exception that aborts the sitting
                        self.log(f"emulator gone ({e.returncode}): ending the loop cleanly")
                        break
                    # Burst.request_time (R1a): the pre-send clock of this group's save request,
                    # recorded at the send, never at staging
                    if self.last_request is not None:
                        head["request_time"], head["sent"] = self.last_request, self.last_sent
                        self.log(f"burst group (last key +{head['last'] - self.t0:.3f}s) "
                                 f"requested at +{head['request_time'] - self.t0:.3f}s")
                    burst.consume()
                    if e:
                        entries.append(e)
                else:
                    try:
                        e = self.tick(video=video, submit=submit if keys else None)
                    except StopIteration as e:
                        self.log(str(e))
                        break
                    except _EmulatorGone as e:
                        # R5: clean termination, not an exception that aborts the sitting
                        self.log(f"emulator gone ({e.returncode}): ending the loop cleanly")
                        break
                    if e:
                        entries.append(e)
        finally:
            jobs.put(None)
            worker.join(timeout=SAVE_TIMEOUT_S + 5.0)
            if worker.is_alive():
                self.log("capture pipeline did not finish before the join timeout")
        return entries + staged

    def shutdown_stage(self, indexed_sha):
        """Best-effort last snapshot: the owner's manual F12+S, captured after the emulator is
        gone (R4) through the same staging gate as every tick (capture, with no pre-send
        signature and no emulator to poll); skipped when its bytes are already indexed.
        Returns the entry, or None."""
        # the owner's save was written after the last staged write, whose window opened at that
        # entry's request: [that request, now] is all the map may assume about its screen (R1)
        lo = self.t0 if self.last_staged_request is None else self.last_staged_request
        try:
            data, d, _, _ = self.capture(None, live_emulator=False)
        except TimeoutError as e:
            self.problems.append(f"shutdown snapshot not captured: {e}")
            return None
        if d in indexed_sha:
            self.log(f"shutdown snapshot already indexed ({d[:16]}...): skipping")
            return None
        try:
            return self.stage(data, d, origin="shutdown", request=lo, sent=self.clock())
        except OSError as e:
            self.problems.append(f"shutdown snapshot failed: {e}")
            return None


class _EmulatorGone(Exception):
    """The emulator died mid-snapshot. Watcher.run catches this and ends the loop cleanly
    (R5), so it never propagates as an unhandled exception."""

    def __init__(self, returncode):
        self.returncode = returncode
        super().__init__(f"emulator gone (returncode {returncode})")


class _AttributionLost(Exception):
    """The bytes on the live savestate cannot be tied to THIS save request (Sol delta r3 R1):
    two or more writes completed since the request was sent, so the file holds a later
    request's savestate. Watcher._stage_job marks the request superseded (nothing staged under
    a window it does not own) and the acceptance guard rejects the sitting (R2)."""


# ---- video ---------------------------------------------------------------------------------------
def video_cmd(geometry, display, out):
    """The ffmpeg argv for the game window's screen video: x11grab on the window's region,
    Matroska with `-flush_packets 1` (bytes reach the disk as frames arrive; the mp4
    replacement, see the module docstring). `-flush_packets 1` is the documented fix to the
    2026-10-07 prototype's silent-failure bug (R12: a load-bearing test pins the constant)."""
    x, y, w, h = geometry
    # libx264 needs even dimensions; the game window is 640x400 at 2x, but never trust it
    w, h = w - (w % 2), h - (h % 2)
    return ["ffmpeg", "-nostdin", "-loglevel", "level", "-y",
            "-f", "x11grab", "-framerate", "10", "-video_size", f"{w}x{h}", "-i", f"{display}+{x},{y}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-pix_fmt", "yuv420p",
            "-flush_packets", "1",
            str(out)]


class Video:
    """The optional screen video: a subprocess whose file growth is polled; stopped with SIGTERM
    (clean finalize), SIGKILL only after VIDEO_TERM_GRACE_S."""

    def __init__(self, argv, out, clock=time.monotonic):
        self.argv, self.out, self.clock = argv, Path(out), clock
        self.proc = None
        self.started = None
        self.stalled = False
        self.last_size, self.last_growth = 0, self.clock()

    def start(self):
        self.out.parent.mkdir(parents=True, exist_ok=True)
        self.proc = subprocess.Popen(self.argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     start_new_session=True)
        self.started = self.clock()
        return self.proc

    def poll_growth(self):
        """Called between snapshot ticks: a file that stopped growing while ffmpeg runs is the
        prototype's silent failure — flag it loudly instead. R16: the old recorder never called
        this and a stalled recording received no warning."""
        if self.proc is None or self.proc.poll() is not None:
            return
        try:
            size = self.out.stat().st_size
        except OSError:
            return
        if size != self.last_size:
            self.last_size, self.last_growth = size, self.clock()
        elif self.clock() - self.last_growth > VIDEO_STALL_S:
            if not self.stalled:
                self.stalled = True

    def stop(self):
        """SIGTERM to the process group (ffmpeg writes its trailer), SIGKILL to a survivor after
        VIDEO_TERM_GRACE_S (boundary: the EXACT 10.000 s mark is SIGKILLed, not SIGTERMed)."""
        if self.proc is None:
            return {"file": self.out.name, "bytes": 0, "sha256": None, "seconds": 0, "stalled": self.stalled,
                    "ended": "never started"}
        t0 = self.clock()
        try:
            os.killpg(self.proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            self.proc.wait(timeout=VIDEO_TERM_GRACE_S)
            how = "SIGTERM"
        except subprocess.TimeoutExpired:
            os.killpg(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
            how = "SIGKILL"
        data = self.out.read_bytes() if self.out.is_file() else b""
        return {"file": self.out.name, "bytes": len(data), "sha256": sha256(data) if data else None,
                "seconds": round(self.clock() - (self.started or self.clock()), 3),
                "stop_seconds": round(self.clock() - t0, 3),
                "stalled": self.stalled, "ended": how}


# ---- session -------------------------------------------------------------------------------------
def conf_for(session):
    """The session's dosbox.conf text: the G1 driver's own config family (windowed surface output,
    savefile, captures, mapper in the session folder, C: from the session's game copy, D: for the
    clock read-back), via driver.Driver.conf_text — nothing is launched."""
    return driver.Driver(workdir=session, game_dir=Path(session) / "game").conf_text()


def new_session(when=None):
    """Create the session folder and everything the launch needs: a per-session copy of the
    verified release (F001: the mount is remembered; the owner's in-game saves land here, never in
    the release cache), the config, and empty cap/dosclock/snapshots folders."""
    verify_release_or_die()
    ts = (when or datetime.now()).strftime("%Y%m%d-%H%M%S")
    session = SESSIONS / ts
    session.mkdir(parents=True)
    (session / "snapshots").mkdir()
    (session / "cap").mkdir()
    (session / "dosclock").mkdir()
    shutil.copytree(driver.CACHE, session / "game")
    conf = conf_for(session)
    (session / "dosbox.conf").write_text(conf)
    # the config's `[sdl] mapperfile` names this file: DOSBox-X's default binds + F12+P = pause (T39b)
    mapper = mapper_text()
    (session / "mapper.map").write_text(mapper)
    meta = {"created": host_times(), "ended": None, "stop_reason": None,
            "artifact_set": driver.SET_ID, "config": conf, "config_sha256": sha256(conf.encode()),
            "mapper_sha256": sha256(mapper.encode()),
            "dosbox_x_version": dosbox_version(), "display": os.environ.get("DISPLAY"),
            "video": None, "problems": []}
    (session / "meta.json").write_text(json.dumps(meta, indent=1))
    return session, meta


def verify_release_or_die():
    """The release copy verified against artifacts/known.json, downloaded with gh when the cache
    is empty (as setup/goal2-runtime.sh does); a mismatch stops everything before any launch."""
    try:
        return driver.verify_release(driver.CACHE)
    except (SystemExit, OSError, json.JSONDecodeError):
        if shutil.which("gh") is None:
            raise
        driver.CACHE.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["gh", "release", "download", "goal2-original", "--repo",
                            "diegoami/goal2-archaeology", "-D", str(driver.CACHE), "--clobber"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"the release copy could not be fetched: {r.stderr.strip()}\n"
                             f"run: bash setup/goal2-runtime.sh")
        return driver.verify_release(driver.CACHE)


def terminate(p, grace=TERM_GRACE_S):
    """SIGTERM to the process group, SIGKILL to a survivor after `grace` (the driver's measured
    pattern: DOSBox-X can ignore SIGTERM)."""
    if p is None or p.poll() is not None:
        return
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=grace)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.wait()


def find_xephyr_window(outer_env, title):
    """The launched Xephyr's own window on the outer display, or None. Xephyr sets no _NET_WM_PID
    (T34 review R4), so the pid bind of `find_window` cannot serve; the window is the one Xephyr
    class window whose WM_NAME is exactly this sitting's `title`, a random per-session token. Zero
    or several matches give None: a foreign window is never picked (fail closed)."""
    p = xdotool(["search", "--class", "Xephyr"], env=outer_env)
    ids = [w for w in p.stdout.split() if w]
    named = [w for w in ids
             if xdotool(["getwindowname", w], env=outer_env).stdout.rstrip("\n") == title]
    return named[0] if len(named) == 1 else None


def start_nested(outer_env, res, logf, title=None, find=find_xephyr_window,
                 clock=time.monotonic, sleep=time.sleep):
    """Start Xephyr on the first free display from 600 (never :99, never the outer display);
    returns (process, nested env, Xephyr's window id on the outer display).

    No system socket or lock file is inspected (WSLg's /tmp/.X11-unix is shared): each candidate
    is tried. A candidate is accepted only once the launched Xephyr's titled window appears on the
    outer display (`find`), which it creates after binding its display socket; a process that
    exits first had a busy number, and the next one is tried. [designed] The 600..699 candidates
    follow the T34 dispatch probe; NESTED_START_S bounds the wait for the window."""
    title = title or f"goal2-recorder-{os.getpid()}-{os.urandom(8).hex()}"
    for number in range(600, 700):
        display = f":{number}"
        if display in (outer_env.get("DISPLAY"), ":99"):
            continue
        proc = subprocess.Popen(["Xephyr", display, "-screen", res, "-nolisten", "tcp",
                                 "-title", title],
                                env=outer_env, stdout=logf, stderr=logf,
                                start_new_session=True)
        end = clock() + NESTED_START_S
        while proc.poll() is None and clock() < end:
            wid = find(outer_env, title)
            if wid is not None:
                return proc, dict(outer_env, DISPLAY=display), wid
            sleep(0.05)
        if proc.poll() is None:
            terminate(proc)
            raise RuntimeError(f"Xephyr on {display} showed no window titled {title!r} "
                               f"within {NESTED_START_S}s")
    raise RuntimeError("no free nested display in candidates 600 through 699")


def play(video=False, quit_after=None, res="1280x800"):
    """One sitting: launch windowed dosbox-x, watch it, stop cleanly, write meta. Returns 0."""
    if not os.environ.get("DISPLAY"):
        print("play: DISPLAY is not set; run from a graphical session", file=sys.stderr)
        return 1
    try:
        # the calibrated emulator or nothing, before any session, display or logger (#117)
        dbx_exe = driver.require_dosbox()
    except RuntimeError as e:
        print(f"play: refused: {e}", file=sys.stderr)
        return 2
    session, meta = new_session()
    logf = open(session / "session.log", "a", encoding="utf-8")

    def log(msg):
        line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
        logf.write(line + "\n")
        logf.flush()
        print(line, flush=True)

    log(f"session {session}")
    outer_env = dict(os.environ)
    title = f"goal2-recorder-{session.name}-{os.urandom(8).hex()}"
    xephyr, env, xephyr_wid = start_nested(outer_env, res, logf, title=title)
    meta.update({"outer_display": outer_env["DISPLAY"], "display": env["DISPLAY"],
                 "xephyr_pid": xephyr.pid, "xephyr_title": title, "xephyr_window_id": xephyr_wid,
                 "resolution": res, "burst_quiet_s": BURST_QUIET_S,
                 "capture_margin_s": CAPTURE_MARGIN_S})
    stop_flag = {"now": False}

    def on_signal(signum, frame):
        stop_flag["now"] = True
        log(f"signal {signum}: stopping after the current step")

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    vid = None
    keys = None
    geom0 = None
    dbx = None
    try:
        # the logger starts before the emulator is launched (T34 review R6)
        keys = KeyLogger(env, outer_env["DISPLAY"], session / "keys.jsonl")
        keys.start()
        # the write watch starts before the emulator too (Sol's round-3 R1 on PR 112): a save the
        # running emulator writes before the Watcher exists must be in write_events_total, or a
        # save before the first request goes unowned and uncounted
        watch = WriteWatch(session / "state.sav")
        argv = [dbx_exe, "-conf", str(session / "dosbox.conf"),
                "-fastlaunch", "-nogui", "-nomenu", "-savedir", str(session),
                "-set", f"dosbox savefile={session / 'state.sav'}"]
        dbx = subprocess.Popen(argv, env=env, stdout=logf, stderr=subprocess.STDOUT,
                               start_new_session=True)
        log(f"dosbox-x started (pid {dbx.pid})")
        try:
            wid = find_window(env, dbx.pid)
        except RuntimeError as e:
            # R1: failed to bind the dosbox-x pid → fail closed
            log(f"window bind failed: {e}")
            terminate(dbx)
            meta.update({"ended": host_times(), "stop_reason": "window-bind-failed",
                         "snapshots": 0,
                         "video": {"requested": bool(video), "used": False},
                         "problems": [str(e)]})
            (session / "meta.json").write_text(json.dumps(meta, indent=1))
            return 2
        log(f"game window {wid} (pid {dbx.pid})")
        meta.update({"window_id": wid, "dosbox_x_pid": dbx.pid})
        meta["monotonic_start_s"] = time.monotonic()
        (session / "meta.json").write_text(json.dumps(meta, indent=1))
        if video:
            # the video is a convenience channel: no failure here ends the sitting (T34 R4)
            geom0 = window_geometry(xephyr_wid, outer_env)
            if shutil.which("ffmpeg") is None:
                log("--video requested but ffmpeg is not installed: continuing without video")
            elif geom0 is None:
                log("--video requested but the window geometry is unknown: continuing without video")
            else:
                v = video_cmd(geom0, outer_env["DISPLAY"], session / "video.mkv")
                vid = Video(v, session / "video.mkv")
                vid.start()
                log(f"video started: {' '.join(v)}")
        if os.environ.get("GOAL2_RECORDER_TEST_EARLY_SAVE") == "1":
            # test only (tests.test_human_keys, the early-save regression): one save of the live
            # emulator before the Watcher exists — the window Sol's round-3 R1 used
            send_save_event(wid, env)
            time.sleep(0.5)
        watcher = Watcher(session, session / "state.sav", wid, dbx, env, log=log,
                          xrun=lambda argv: send_save_event(wid, env), watch=watch,
                          paused=lambda: window_paused(wid, env))
        meta["pause"] = {"pause_key": "F12+P", "resume_key": "Pause",
                         "file": "pauses.jsonl", "snapshot": "after-resume"}
        log("pause: F12+P; resume: the Pause key (DOSBox-X's own pause ends on Pause only)")
        meta["monotonic_start_s"] = watcher.t0
        (session / "meta.json").write_text(json.dumps(meta, indent=1))
        entries = watcher.run(quit_after=quit_after, stop=lambda: stop_flag["now"], video=vid, keys=keys)
        # the window may have closed between the last poll and here; terminate the emulator
        # BEFORE the shutdown staging pass so the live file is no longer being written (R4)
        if dbx.poll() is None:
            reason = "signal" if stop_flag["now"] else "quit-after"
            terminate(dbx)
        else:
            reason = "window-closed"
        # R4 — the live file is stable now: apply the same staging gate to the owner's last F12+S
        last = watcher.shutdown_stage({e["sha256"] for e in entries})
        if last:
            entries.append(last)
        vinfo = vid.stop() if vid else None
        if vinfo and vinfo["bytes"] == 0:
            log(f"WARNING: the video file is empty ({vinfo['ended']})")
        if vinfo and vinfo.get("stalled"):
            log(f"WARNING: the video was flagged stalled (no growth for >{VIDEO_STALL_S}s)")
        meta.update({"ended": host_times(), "stop_reason": reason,
                     "snapshots": len(entries),
                     "video": dict(vinfo, requested=bool(video), geometry=geom0) if vid else
                              {"requested": bool(video), "used": False},
                      "problems": watcher.problems})
        # T35 round 3: the sitting's whole write count on the live savestate, after the emulator
        # is gone, so the acceptance guard can prove every save is owned by exactly one staged
        # request (scripted_keys.check_attribution); 0 with an injected `writing`
        meta["write_events_total"] = watcher.activity()[1]
        keys.stop()
        keydata = (session / "keys.jsonl").read_bytes()
        meta["keys"] = {"file": "keys.jsonl", "sha256": sha256(keydata), "bytes": len(keydata)}
        (session / "meta.json").write_text(json.dumps(meta, indent=1))
        log(f"done: {len(entries)} snapshots, stop {reason}"
            + (f", video {vinfo['bytes']} bytes" if vinfo else ""))
    finally:
        if keys:
            keys.stop()
        terminate(dbx)
        terminate(xephyr)
        if vid and vid.proc and vid.proc.poll() is None:
            vid.stop()
        logf.close()
    return 0


def ensure_cache():
    """Fetch the release copy when missing (gh, as setup/goal2-runtime.sh); a failure is a named
    error. Self-test only: play() calls verify_release_or_die()."""
    try:
        return driver.verify_release(driver.CACHE)
    except (SystemExit, OSError):
        r = subprocess.run(["gh", "release", "download", "goal2-original", "--repo",
                            "diegoami/goal2-archaeology", "-D", str(driver.CACHE), "--clobber"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"release goal2-original could not be downloaded: {r.stderr.strip()}\n"
                             f"run: bash setup/goal2-runtime.sh")
        return driver.verify_release(driver.CACHE)


def self_test(with_video=False):
    """`play.sh --self-test`: verify the release copy, check the tools, write the session config,
    exit without launching anything."""
    problems = []
    try:
        set_id = ensure_cache()
        print(f"release    {driver.CACHE} matches artifacts/known.json set {set_id}")
    except (SystemExit, OSError) as e:
        problems.append(f"release copy: {e}")
    v = dosbox_version()
    if driver.version_in(v) != WANT_DOSBOX:
        problems.append(f"dosbox-x {WANT_DOSBOX} (found {v or 'none'})")
    else:
        print(f"dosbox-x   {v}")
    if shutil.which("xdotool") is None:
        problems.append("xdotool")
    else:
        print("xdotool    present")
    if with_video:
        if shutil.which("ffmpeg") is None:
            problems.append("ffmpeg (needed for --video)")
        else:
            print("ffmpeg     present")
    try:
        print(f"mapper     F12+P pauses (sha256 {sha256(mapper_text().encode())[:16]}...)")
    except (OSError, RuntimeError) as e:
        problems.append(f"session mapper: {e}")
    for tool in ("Xephyr", "xinput", "stdbuf"):
        if shutil.which(tool) is None:
            problems.append(tool)
        else:
            print(f"{tool:10} present")
    if not problems:
        SELFTEST.mkdir(parents=True, exist_ok=True)
        conf = conf_for(SELFTEST)
        (SELFTEST / "dosbox.conf").write_text(conf)
        print(f"config     {SELFTEST / 'dosbox.conf'} (sha256 {sha256(conf.encode())})")
    if problems:
        print("missing: " + "; ".join(problems), file=sys.stderr)
        return 1
    print("self-test ok (nothing was launched)")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "--self-test":   # play.sh --self-test: the brief's spelling
        argv[0] = "self-test"
    if argv and argv[0] not in ("self-test", "play") and not argv[0].startswith("-"):
        argv.insert(0, "play")
    if argv and argv[0].startswith("-"):    # flags without a subcommand mean play
        argv.insert(0, "play")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    st = sub.add_parser("self-test", help="verify the release copy and tools, write a config, exit")
    st.add_argument("--video", action="store_true", help="also require ffmpeg")
    pl = sub.add_parser("play", help="record one sitting")
    pl.add_argument("--video", action="store_true", help="also record the game window (mkv)")
    pl.add_argument("--res", default="1280x800", help="nested window size WIDTHxHEIGHT")
    pl.add_argument("--quit-after", type=float, default=None, metavar="SECS",
                    help="stop the sitting after SECS seconds (scripted sittings)")
    a = ap.parse_args(argv)
    if a.cmd == "self-test":
        return self_test(with_video=a.video)
    if not __import__("re").fullmatch(r"[1-9][0-9]*x[1-9][0-9]*", a.res):
        ap.error("--res must be WIDTHxHEIGHT")
    return play(video=a.video, quit_after=a.quit_after, res=a.res)


if __name__ == "__main__":
    sys.exit(main())
