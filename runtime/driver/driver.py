#!/usr/bin/env python3
"""The G1 driver: GOAL2 under DOSBox-X 2024.03.01 in Xvfb, keys as raw XTEST events (xkeys.py), the
screen and guest memory read from savestates (F001, route A). Standard library only.

    d = Driver(config); d.launch(start_state); d.keys("n"); sc = d.screen(); d.memory(0x449, 1)
    d.save_state(); d.restore(state); d.terminate()

Every wait is a bounded poll or a delay written into `Driver.events` (seconds since launch, what);
the cycle writes `events` into each run record. Process groups are started by this driver and only
those are killed (by PID). Display `:99` is never used (another project runs there).

CLI:
    python3 runtime/driver/driver.py make-state title     # store the title-screen start state
    python3 runtime/driver/driver.py read <file.sav>      # print the screen, mode and ticks of a savestate
Keys (issue 244): every key is the one X keycode of its keysym, pressed and released with no modifier
added, and the savestate and load are single keys (Scroll Lock, Print Screen) through a mapper file the
driver writes, so the host key F12 is never pressed. On Ubuntu 26.04 (xdotool 3.20160805.1, Xvfb 21.1.22,
installed 2026-10-10) xdotool, asked for F10, sent Left Alt with it (the guest read Alt+F10), and its
F12+S chord left Left Alt held in the guest from the launch on. The 458 driver records made on Ubuntu 24.04
show no Alt held (34 published savestates checked: experiments/fix-244-driver-keys/out/published-states.tsv),
but their chord put a plain F12 (BIOS word 0x8600) into the guest at every read. `Driver(legacy_keys=True)`
is the old keys and chord, kept to reproduce the fault.
Read pace: the savestate key is held `save_hold` seconds (default SAVE_HOLD = 0.52), so a savestate read
takes about 0.53 s as it did with the F12 chord; scripts whose `settle` waits for two equal reads reproduce
their records only at that pace (SAVE_HOLD says how it was measured).
Do not press F1 in a driver run: the help viewer makes every later savestate crash DOSBox-X 2024.03.01
(buffer overflow detected, exit -6), even after Esc (E031).
Copied in part from runtime/spike/dbx.py (T02); the spike stays unchanged."""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import savestate  # noqa: E402
import xkeys  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "goal2"            # the verified release copy (setup/goal2-runtime.sh)
# The DOSBox-X this project is calibrated to is 2024.03.01 (F001; savestate.py's layout). Ubuntu
# 26.04's apt offers only 2026.01.02, whose savestates store Vga raw and the readers cannot parse
# (#117), so setup/dosbox-x-2024.03.01.sh unpacks Ubuntu 24.04's package into this bundle.
DOSBOX_BUNDLE = Path.home() / "tools" / "dosbox-x-2024.03.01" / "bin" / "dosbox-x"
WANT_DOSBOX = "2024.03.01"


def dosbox_x(env=None):
    """The dosbox-x to run: $DOSBOX_X, else the 2024.03.01 bundle when installed, else the one on
    PATH (#117). Every launch and version check of the driver and the recorder goes through it."""
    env = os.environ if env is None else env
    if env.get("DOSBOX_X"):
        return env["DOSBOX_X"]
    return str(DOSBOX_BUNDLE) if DOSBOX_BUNDLE.is_file() else "dosbox-x"


def dosbox_version_of(exe):
    """The exact version an executable's banner names (`DOSBox-X version 2024.03.01 ...`; it exits 1
    and writes to stderr), or None."""
    try:
        out = subprocess.run([exe, "-version"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return version_in(out.stdout + out.stderr)


def version_in(banner):
    """The whole version token of a `DOSBox-X version X ...` banner, or of a bare version string:
    2024.03.01.1 and 2024.03.010 are not 2024.03.01. None when there is none."""
    m = re.search(r"^DOSBox-X version (\S+)", banner or "", re.M)
    token = m.group(1) if m else ((banner or "").split() or [None])[0]
    return token.rstrip(",") if token else None


def require_dosbox(env=None):
    """The resolved dosbox-x if it is exactly WANT_DOSBOX, else RuntimeError: every launch of the
    driver and the recorder refuses another version, whichever way it was chosen (Luna's R1-R3 on
    PR 120; #117)."""
    exe = dosbox_x(env)
    v = dosbox_version_of(exe)
    if v != WANT_DOSBOX:
        raise RuntimeError(f"dosbox-x {WANT_DOSBOX} is required, found {v or 'none'} ({exe}); "
                           "run: bash setup/dosbox-x-2024.03.01.sh")
    return exe
# The registered set every launch verifies and every record names (artifacts/known.json): the
# successor goal2-67cf27d6, which declares the runtime writes F001 observed; runs recorded before
# it name its predecessor goal2-a949da2f, whose ten files are identical (U21, T11).
SET_ID = "goal2-67cf27d6"
STATES = ROOT / ".cache" / "states" / "driver"  # start states: <name>.sav and <name>.json, git-ignored
SCRATCH = ROOT / "scratch" / "driver"
# F001 Anomalies: a savestate keeps the host folder drive C: was mounted from, so every session
# mounts this one folder, recreated from the release copy at each launch.
GAME_DIR = SCRATCH / "game"
TITLE_TEXT = "Do you want to load a saved game"

# Delays (seconds) taken from runtime/spike/dbx.py, where F001 measured with them; each use is logged.
KEY_HOLD = 0.08       # a game key: press, hold, release
HOSTKEY_HOLD = 0.15   # each step of a DOSBox-X host-key (F12) combination
# How long the savestate (and load) key is held, so that a read takes the time it took before issue 244.
# The old chord _hostkey held 3 steps of HOSTKEY_HOLD (F12 down, S down, S up) = 0.45 s and made 4 xdotool
# calls; the gap between consecutive chords logged in E003-r0047 and r0049 ("host key F12+s") has median
# 0.536 s and 0.534 s (min 0.512, 29 and 30 gaps), and the single key with a hold h takes h + 0.013 s
# (median 0.163 s at h = 0.15, E003 re-run r0008), so h = 0.52 s gives the old 0.53 s per read.
# Earlier experiments' `settle` (two equal reads) depends on that pace: at 0.15 s E003 d3b stopped on a
# transient screen and its record did not reproduce (experiments/fix-244-driver-keys/README.md).
SAVE_HOLD = 0.52
POLL = 0.05           # savestate file poll interval
X_POLL = 0.1          # Xvfb and window poll interval
# Seconds to wait for exit after SIGTERM before SIGKILL to the group (issue #19): F001 M:terminate
# measured a clean exit 0.02 s after SIGTERM, F003 measured DOSBox-X ignore SIGTERM for the whole
# 10 s wait in 30 of 30 E002 records after a restore. 0.5 s is 25x the measured clean exit, a
# [designed] margin; the driver's own scratch sessions (2026-10-04) saw DOSBox-X flush its log and
# die on the SIGKILL 0.5 s later, and Xvfb still ends by SIGTERM alone.
TERM_GRACE = 0.5

# Session subfolder mounted as D: for the clock read-back, in every launch, clock option or not: a
# savestate keeps the mounted drives, and one made with D: crashed DOSBox-X (code -11 during a
# savestate) when restored in a session without D: (review round 2 R1; the reviewer's local runs).
CLOCK_DIR = "dosclock"
# Upper bound of the read-back time, seconds after the time set. Evidence: the read-back is written
# before `goal` starts, and the BIOS ticks read at GOAL's title screen, later still, are 0.7 ... 1.1 s
# past the time set in every fixed-time launch (E003-r0007 ... r0026, r0030, r0031, r0043, r0044,
# r0047, r0048: `summarise.py`, "clock at title"), so the read-back moment is under 1.1 s and the
# truncated second at most +1; the read-backs measured are all 1 s early (E003-r0045 ... r0048).
# [designed] one more second of margin for a loaded host, which E003 did not measure.
CLOCK_SLACK = 2
# DOSBox-X keeps DOS time as BIOS ticks (18.2/s) and `time /t` truncates: 10:00:00 set reads back as
# 9:59:59 (E003-r0045, r0046; the ticks 0x000A004A = 35999.98 s of E003-r0007 … agree), so a read-back
# up to 1 s before the time set is the same time.
CLOCK_EARLY = 1


# How to remake each known start state when its drive layout is refused (StateLayoutMismatch).
REMAKE = {"title": "python3 runtime/driver/driver.py make-state title",
          "main": "python3 experiments/E003-q001-inputs/run.py make-main --dos-time 10:00:00 --dos-date 10/04/2026"}


class StateLayoutMismatch(RuntimeError):
    """A start state was made with other DOS drives mounted than this driver mounts: refused before any
    restore. A state made without D: (T07, and T08 before rework round 3) stalled DOSBox-X's restore
    under a driver that mounts D: ("savestate not complete within 15s", PR #24 review round 3)."""


class ClockNotApplied(RuntimeError):
    """DOS reported another date or time than the one set: the I3 intervention did not take effect."""


def clock_values(dos_date, dos_time):
    """Parse and range-check a requested DOS date (MM/DD/YYYY, years 1980-2099: DOS's range) and time
    (HH:MM:SS); raise ValueError for anything DOSBox-X could not apply. Returns (date, time) or None each."""
    d = t = None
    if dos_date:
        if not re.fullmatch(r"\d\d/\d\d/\d{4}", dos_date):
            raise ValueError(f"dos_date={dos_date!r}: DOSBox-X needs MM/DD/YYYY")
        try:
            d = datetime.strptime(dos_date, "%m/%d/%Y").date()
        except ValueError as e:
            raise ValueError(f"dos_date={dos_date!r}: no such date ({e})") from None
        if not 1980 <= d.year <= 2099:
            raise ValueError(f"dos_date={dos_date!r}: DOS dates run from 1980 to 2099")
    if dos_time:
        if not re.fullmatch(r"\d\d:\d\d:\d\d", dos_time):
            raise ValueError(f"dos_time={dos_time!r}: DOSBox-X needs HH:MM:SS")
        try:
            t = datetime.strptime(dos_time, "%H:%M:%S").time()
        except ValueError as e:
            raise ValueError(f"dos_time={dos_time!r}: no such time ({e})") from None
    return d, t


def check_clock(dos_date, dos_time, readback):
    """Compare the requested clock with DOS's own read-back (`date /t` then `time /t` output, e.g.
    "10/04/1993\n9:59:59\n"): the date must be equal, the time from CLOCK_EARLY s before to
    CLOCK_SLACK s after the time set.
    Raises ClockNotApplied otherwise; returns the (date, time) DOS reported."""
    d, t = clock_values(dos_date, dos_time)
    m_d = re.search(r"(\d\d)/(\d\d)/(\d{4})", readback or "")
    m_t = re.search(r"(\d{1,2}):(\d\d):(\d\d)", readback or "")
    if not (m_d and m_t):
        raise ClockNotApplied(f"no DOS date and time in the read-back {readback!r}")
    got_d = datetime(int(m_d[3]), int(m_d[1]), int(m_d[2])).date()
    got_t = int(m_t[1]) * 3600 + int(m_t[2]) * 60 + int(m_t[3])
    if d and got_d != d:
        raise ClockNotApplied(f"DOS date set to {dos_date}, DOS reports {m_d[0]}")
    if t:
        want = t.hour * 3600 + t.minute * 60 + t.second
        if not -CLOCK_EARLY <= got_t - want <= CLOCK_SLACK:
            raise ClockNotApplied(f"DOS time set to {dos_time}, DOS reports {m_t[0]}")
    return m_d[0], m_t[0]


KEYMAP = xkeys.KEYMAP

DEFAULT_CONFIG = {"machine": "svga_s3", "memsize": 16, "cycles": "max", "core": "auto", "cputype": "auto"}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def host_times():
    """The host clock now: UTC, and local time with its UTC offset and zone name (DOS time follows local time)."""
    t = datetime.now(timezone.utc)
    local = t.astimezone()
    return {"utc": t.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "local": local.isoformat(timespec="milliseconds"), "tz": local.tzname() or ""}


class Driver:
    def __init__(self, config=None, workdir=None, game_dir=GAME_DIR, legacy_keys=False, save_hold=SAVE_HOLD):
        self.save_hold = save_hold  # seconds the savestate and load key is held: the read pace (SAVE_HOLD), read at each call
        self.legacy_keys = legacy_keys  # True: xdotool keys and the F12 host chord, the fault of issue 244
        self.config = dict(DEFAULT_CONFIG, **(config or {}))
        self.workdir = Path(workdir or SCRATCH / "session").resolve()
        self.game_dir = Path(game_dir).resolve()
        self.savefile = self.workdir / "state.sav"
        self.xvfb = self.dbx = None
        self.display = self.env = self.wid = None
        self.events = []
        self.last = self.pre_restore = None  # (host times, Savestate) of the latest read; the read before a restore
        self.last_blob = None  # the raw savestate bytes of the latest read (E010)
        self.t0 = time.monotonic()
        self.launched = None
        self.clock_applied = None  # CLOCK.TXT as DOS wrote it after setting the clock (clock option only)

    def log(self, what):
        self.events.append((round(time.monotonic() - self.t0, 3), what))

    # ---- configuration --------------------------------------------------------------------
    def conf_text(self):
        c = self.config
        return f"""[sdl]
fullscreen=false
output=surface
mapperfile={self.workdir}/mapper.map
[mixer]
nosound=true
[midi]
mididevice=none
[dosbox]
machine={c['machine']}
memsize={c['memsize']}
saveremark=false
captures={self.workdir}/cap
[cpu]
core={c['core']}
cputype={c['cputype']}
cycles={c['cycles']}
[autoexec]
mount c {self.game_dir}
c:
{self.clock_lines()}goal
exit
"""

    def clock_lines(self):
        """Autoexec lines that set the DOS date and time before GOAL runs (I3, T08), when the config
        has `dos_date` (MM/DD/YYYY) or `dos_time` (HH:MM:SS); else none, and the guest clock
        starts from the host's as before. DOSBox-X 2024.03.01's DATE takes MM/DD/YYYY only: given
        10-04-1993 it prints the current date and changes nothing (E003-r0030, r0031; F004), so any
        other form, and any date or time no calendar or DOS has (99/99/1993, a year outside DOS's
        1980-2099, 24:00:00), is refused here (clock_values). Then, in every launch (clock option or
        not, so a savestate's drives are the same either way: CLOCK_DIR), the lines write DOS's own date
        and time (`date /t`, `time /t`) to CLOCK.TXT on a drive D: mounted from the session folder, so
        launch() can read back the clock GOAL starts with (and check_clock it when one was set)."""
        c = self.config
        lines = ""
        if c.get("dos_date") or c.get("dos_time"):
            clock_values(c.get("dos_date"), c.get("dos_time"))
            lines = "".join(f"{cmd} {c[k]}\n" for cmd, k in (("date", "dos_date"), ("time", "dos_time")) if c.get(k))
        return (lines + f"mount d {self.workdir / CLOCK_DIR}\ndate /t > d:\\clock.txt\ntime /t >> d:\\clock.txt\nc:\n")

    def drive_layout(self):
        """The DOS drives this driver's autoexec mounts, host paths as <game> and <work>: what a savestate
        keeps and a restore needs again. Stored with each start state (make_state, run.py make-main)."""
        lines = [x for x in self.conf_text().splitlines() if x.startswith("mount ")]
        return [x.replace(str(self.game_dir), "<game>").replace(str(self.workdir), "<work>") for x in lines]

    def check_start_state(self, st):
        """Refuse, before DOSBox-X starts, a start state whose stored drive layout is not this driver's,
        or which stored none (made before T08 rework round 4)."""
        mine = self.drive_layout()
        if st.drive_layout != mine:
            made = st.drive_layout if st.drive_layout is not None else "none recorded (made before T08 rework round 4)"
            how = REMAKE.get(st.name, f"remake it as {st.name} was made")
            raise StateLayoutMismatch(
                f"start state {st.name} ({st.path}) was made with drive layout {made}; this driver mounts {mine}, and "
                f"restoring a state made with other drives stalls or crashes DOSBox-X. Recreate it: move {st.path.name} "
                f"and {st.path.stem}.json out of {st.path.parent}, then run `{how}`")

    def clock_readback(self):
        """The text DOS wrote to CLOCK.TXT before GOAL ran (after the date and time, when set), or None."""
        for f in (self.workdir / CLOCK_DIR).glob("*"):
            if f.name.lower() == "clock.txt":
                return f.read_text(errors="replace")
        return None

    def conf_public(self):
        """The config with host paths replaced by <work> and <game>, and its sha256 (what a record carries)."""
        text = self.conf.replace(str(self.workdir), "<work>").replace(str(self.game_dir), "<game>")
        return text, sha256(text.encode())

    # ---- launch ---------------------------------------------------------------------------
    # launch timeout 30 s (R2): F003 Timings -- the title screen after 1.80 ... 1.87 s in 29 of 30
    # E002 records, 13.07 s in the one outlier (E002-r0009, machine load); F001 M:speed saw
    # 0.77 ... 1.87 s across cycles settings. 30 s bounds the outlier with margin. [designed]
    def launch(self, start_state=None, timeout=30, displace_key="n"):
        """Start Xvfb and DOSBox-X, run GOAL and poll for the title screen. With a StartState, then
        press `displace_key` and poll until the screen settles on another digest (so the restore is
        seen to change the screen), keep that read as `self.pre_restore`, restore the state with
        Host+L and poll until the screen digest equals the one stored with it. Returns the screen.
        (Booting to the DOS prompt and restoring there failed once: DOSBox-X logged "Save state
        corrupted! ... Memory_Size" and wrote no savestate afterwards; not investigated.)"""
        self.t0 = time.monotonic()
        self.launched = host_times()
        if start_state is not None and Path(start_state.game_dir) != self.game_dir:
            raise RuntimeError(f"start state {start_state.name} was saved with C: mounted from another folder "
                               f"({start_state.game_dir}); restoring it here would write there (F001 Anomalies)")
        if start_state is not None:
            self.check_start_state(start_state)  # its drives must be this driver's (StateLayoutMismatch)
        dbx_exe = require_dosbox()          # before any folder, display or emulator (#117)
        self.workdir.mkdir(parents=True, exist_ok=True)
        (self.workdir / "cap").mkdir(exist_ok=True)
        shutil.rmtree(self.workdir / CLOCK_DIR, ignore_errors=True)
        (self.workdir / CLOCK_DIR).mkdir()
        verify_release(CACHE)
        shutil.rmtree(self.game_dir, ignore_errors=True)
        shutil.copytree(CACHE, self.game_dir)
        self.conf = self.conf_text()
        conf = self.workdir / "dosbox.conf"
        conf.write_text(self.conf)
        self._write_mapper()
        self._start_xvfb()
        self.env = dict(os.environ, DISPLAY=self.display, SDL_AUDIODRIVER="dummy")
        args = [dbx_exe, "-conf", str(conf), "-fastlaunch", "-nogui", "-nomenu",
                "-savedir", str(self.workdir), "-set", f"dosbox savefile={self.savefile}"]
        self.dbx = subprocess.Popen(args, env=self.env, stdout=open(self.workdir / "dosbox.out", "w"),
                                    stderr=subprocess.STDOUT, start_new_session=True)
        self.log("dosbox-x started")
        self.wid = self._wait_window(15)
        self._x("windowfocus", self.wid)
        self.log("window focused")
        sc = self.wait_screen(lambda sc: TITLE_TEXT in sc.text(), timeout, "title screen")
        # the clock GOAL starts with, as DOS reported it before GOAL ran; when one was set (I3), verified
        self.clock_applied = self.clock_readback()
        self.log(f"DOS clock read back: {(self.clock_applied or 'no CLOCK.TXT').strip()!r}")
        if self.config.get("dos_date") or self.config.get("dos_time"):
            check_clock(self.config.get("dos_date"), self.config.get("dos_time"), self.clock_applied)
        if start_state is None:
            return sc
        if sc.digest() == start_state.screen_digest:
            self.keys(displace_key)
            sc = self.settle(sc.digest(), what=f"displaced by {displace_key}")
        self.pre_restore = self.last
        return self.restore(start_state)

    def _write_mapper(self):
        """<work>/mapper.map, which the config names and DOSBox-X reads at start: the default binds with
        the savestate on Scroll Lock and the load on Print Screen (xkeys.mapper_text). With legacy_keys
        no file is written and a stale one is removed, so DOSBox-X's own default binds (Host+S, Host+L
        on F12) apply as they did before issue 244."""
        path = self.workdir / "mapper.map"
        if self.legacy_keys:
            path.unlink(missing_ok=True)
            return
        text = xkeys.mapper_text()
        path.write_text(text)
        self.log(f"mapper file written, sha256 {sha256(text.encode())}: savestate on Scroll Lock, load on Print Screen")

    def _start_xvfb(self):
        # Xvfb's -displayfd cannot choose here (WSLg owns X0): pick 200..899, never :99, and poll until it answers.
        for attempt in range(20):
            num = 200 + (os.getpid() + attempt * 7) % 700
            if os.path.exists(f"/tmp/.X{num}-lock"):
                continue
            self.xvfb = subprocess.Popen(["Xvfb", f":{num}", "-screen", "0", "1024x768x24", "-nolisten", "tcp"],
                                         stderr=subprocess.DEVNULL, start_new_session=True)
            self.display = f":{num}"
            if self._poll_x(10):
                self.log(f"Xvfb {self.display} answering")
                return
            self._kill(self.xvfb)
        raise RuntimeError("no Xvfb display could be started")

    def _poll_x(self, timeout):
        end = time.monotonic() + timeout
        env = dict(os.environ, DISPLAY=self.display)
        polls = 0
        while time.monotonic() < end and self.xvfb.poll() is None:
            polls += 1
            if subprocess.run(["xdotool", "getdisplaygeometry"], env=env, capture_output=True).returncode == 0:
                self.log(f"Xvfb poll: answered after {polls} polls of {X_POLL}s")
                return True
            time.sleep(X_POLL)  # poll loop, bounded by timeout; the count is logged
        self.log(f"Xvfb {self.display} poll: no answer after {polls} polls of {X_POLL}s")
        return False

    def _wait_window(self, timeout):
        end = time.monotonic() + timeout
        polls = 0
        while time.monotonic() < end:
            polls += 1
            p = subprocess.run(["xdotool", "search", "--class", "dosbox"], env=self.env, capture_output=True, text=True)
            if p.stdout.split():
                self.log(f"window found after {polls} polls of {X_POLL}s")
                return p.stdout.split()[0]
            time.sleep(X_POLL)  # poll loop, bounded by timeout; the count is logged
        raise RuntimeError(f"no DOSBox-X window within {timeout}s")

    def _x(self, *a):
        return subprocess.run(["xdotool", *a], env=self.env, capture_output=True, text=True, timeout=10)

    # ---- act ------------------------------------------------------------------------------
    def keys(self, *names, hold=KEY_HOLD):
        """One keystroke per name as raw XTEST events (xkeys.press_release): press, hold `hold` seconds
        (logged), release, with no modifier added. Function keys arrive as the function key (F10 as
        0x4400 in the BIOS buffer). With legacy_keys: xdotool, as before issue 244 (it added Left Alt)."""
        for name in names:
            k = KEYMAP.get(name, name)
            if self.legacy_keys:
                self._x("keydown", k)
                time.sleep(hold)  # key hold; its duration is logged just below
                self._x("keyup", k)
                self.log(f"key {name} held {hold}s")
            else:
                codes = xkeys.press_release(self.display, k, hold)  # the hold is inside the call
                self.log(f"key {name} held {hold}s (raw keycode {'+'.join(map(str, codes))})")

    def _hostkey(self, name, hold=None):
        """An emulator hotkey, not game input: `s` saves a state, `l` loads one. One key (xkeys.SINGLE_KEYS)
        through the mapper _write_mapper wrote, held `hold` s, by default `self.save_hold` (SAVE_HOLD, the
        pace of a read before issue 244; logged). With legacy_keys: DOSBox-X's host key F12 + the letter
        through xdotool (each of 3 steps held `hold`, default HOSTKEY_HOLD), which leaves Left Alt held in
        the guest (issue 244)."""
        if not self.legacy_keys:
            hold = self.save_hold if hold is None else hold
            k = xkeys.SINGLE_KEYS[name]
            codes = xkeys.press_release(self.display, k, hold)  # the hold is inside the call
            self.log(f"emulator key {k} (for host+{name}) held {hold}s (raw keycode {'+'.join(map(str, codes))})")
            return
        hold = HOSTKEY_HOLD if hold is None else hold
        self._x("keydown", "F12")
        time.sleep(hold)  # key hold (host key); logged below
        self._x("keydown", name)
        time.sleep(hold)  # key hold (host key); logged below
        self._x("keyup", name)
        time.sleep(hold)  # key hold (host key); logged below
        self._x("keyup", "F12")
        self.log(f"host key F12+{name}, each step held {hold}s")

    # ---- observe --------------------------------------------------------------------------
    def save_state(self, timeout=15, resend_after=3.0):
        """Host+S, then poll until a complete savestate zip is on disk; returns its bytes.
        Writing it is I2, reading it I1 (vocabulary/interventions.md). Host+S is sent again (logged)
        when no file appears within `resend_after` s; a dead process fails at once."""
        if self.savefile.exists():
            self.savefile.unlink()
        self._hostkey("s")
        t0 = sent = time.monotonic()
        polls = 0
        while time.monotonic() < t0 + timeout:
            polls += 1
            if self.dbx.poll() is not None:
                raise RuntimeError(f"dosbox-x exited with code {self.dbx.returncode} during a savestate")
            if self.savefile.exists():
                try:
                    with zipfile.ZipFile(self.savefile) as z:
                        names = z.namelist()
                        if z.testzip() is None and "Vga" in names and "Memory" in names and "Save_Remark" in names:
                            data = self.savefile.read_bytes()
                            self.log(f"savestate complete after {polls} polls of {POLL}s")
                            return data
                except (zipfile.BadZipFile, OSError):
                    pass
            if time.monotonic() - sent > resend_after:
                self.log(f"Host+S sent again: no savestate after {resend_after}s")
                self._hostkey("s")
                sent = time.monotonic()
            time.sleep(POLL)  # poll loop, bounded by timeout; the count is logged
        raise RuntimeError(f"savestate not complete within {timeout}s")

    def read(self):
        """One observation: host times, then a savestate. Returns (times, Savestate, savestate bytes)."""
        times = host_times()
        data = self.save_state()
        self.last = (times, savestate.Savestate(data))
        self.last_blob = data  # the raw savestate of the latest read (E010: the half-time state)
        return times, self.last[1], data

    def screen(self):
        """The 80x25 text screen (savestate.Screen; .digest() is its sha256, .text() CP437)."""
        return self.read()[1].screen()

    def memory(self, addr, n):
        """n bytes of guest physical memory at addr, from a fresh savestate."""
        return self.read()[1].memory(addr, n)

    def wait_screen(self, pred, timeout=20, what="screen"):
        """Poll savestates until pred(screen); bounded by timeout; the poll count is logged."""
        end = time.monotonic() + timeout
        polls, sc = 0, None
        while time.monotonic() < end:
            polls += 1
            sc = self.screen()
            if pred(sc):
                self.log(f"{what}: matched after {polls} savestate polls")
                return sc
        raise RuntimeError(f"{what}: not seen within {timeout}s ({polls} polls)")

    # settle timeout 15 s (R2): no per-settle duration is recorded, but the key's screen change
    # settled in every completed E002 record (F003 Observations), and the same poll loop matched a
    # Host+L restore 4.00 ... 4.11 s after launch (F003 Timings); 15 s is a margin of about 3.7x.
    # [designed]
    def settle(self, prev_digest, timeout=15, what="settle"):
        """Poll until the screen differs from prev_digest and two consecutive reads agree."""
        end = time.monotonic() + timeout
        last, polls = None, 0
        while time.monotonic() < end:
            polls += 1
            sc = self.screen()
            d = sc.digest()
            if d != prev_digest and d == last:
                self.log(f"{what}: changed and stable after {polls} savestate polls")
                return sc
            last = d if d != prev_digest else None
        raise RuntimeError(f"{what}: no settled change within {timeout}s")

    # ---- reset ----------------------------------------------------------------------------
    # restore timeout 15 s (R2): F003 Timings -- a Host+L restore matched at the first savestate
    # poll, 4.00 ... 4.11 s after launch, in 29 of 29 completed E002 records; the one slow session
    # (E002-r0009) failed in the savestate write after its Host+L, not at this bound. [designed]
    def restore(self, state, timeout=15):
        """Host+L loads state's savestate; poll until the screen digest equals the one stored with it.
        Every restore passes here, so the drive-layout check is here, before the copy and Host+L
        (T08 rework round 5); launch(), cycle.py and run.py check earlier only to refuse before a record."""
        self.check_start_state(state)
        shutil.copy(state.path, self.savefile)
        self._hostkey("l")
        self.log(f"Host+L sent ({state.name})")
        return self.wait_screen(lambda sc: sc.digest() == state.screen_digest, timeout, f"restore {state.name}")

    # ---- terminate ------------------------------------------------------------------------
    def _kill(self, p):
        """SIGTERM to one process group this driver started (start_new_session), then SIGKILL to the
        same group if it is still alive TERM_GRACE later (F003: DOSBox-X ignores SIGTERM after a
        restore). Logs the method (SIGTERM or SIGKILL) and the time to `events`; a record's log
        observation carries them (Done-when of #19)."""
        if not p:
            return
        what = "dosbox-x" if p is self.dbx else "Xvfb"
        t0 = time.monotonic()
        if p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGTERM)  # the process group this driver started (start_new_session)
            except ProcessLookupError:
                pass
        method = "SIGTERM"
        try:
            p.wait(timeout=TERM_GRACE)
        except subprocess.TimeoutExpired:
            self.log(f"{what} pid {p.pid} alive {round(time.monotonic() - t0, 3)}s after SIGTERM (grace "
                     f"{TERM_GRACE}s): SIGKILL to its group")
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            method = "SIGKILL"
        self.log(f"{what} pid {p.pid} ended by {method} {round(time.monotonic() - t0, 3)}s after the first signal")

    def terminate(self):
        """SIGTERM to the DOSBox-X and Xvfb process groups this driver started, SIGKILL to any group
        still alive TERM_GRACE after it (F003: DOSBox-X ignores SIGTERM after a restore); returns
        True when both are gone."""
        pids = [p.pid for p in (self.dbx, self.xvfb) if p]
        for p in (self.dbx, self.xvfb):
            self._kill(p)
        self.log("terminated")
        return all(not Path(f"/proc/{pid}").exists() for pid in pids)


class StartState:
    """A stored savestate: <name>.sav plus <name>.json (screen digest, the folder C: was mounted from, config)."""

    def __init__(self, name, states=STATES):
        self.name = name
        self.path = Path(states) / f"{name}.sav"
        meta = json.loads((Path(states) / f"{name}.json").read_text())
        self.screen_digest, self.game_dir, self.config = meta["screen_digest"], meta["game_dir"], meta["config"]
        self.drive_layout = meta.get("drive_layout")  # None: made before T08 rework round 4 (refused by launch)
        self.sha256 = sha256(self.path.read_bytes())
        if self.sha256 != meta["sha256"]:
            raise RuntimeError(f"{self.path} changed since it was stored")


def make_state(name, config=None, states=STATES):
    """Store a start state. `title`: a fresh launch polled to the title screen. Refuses to replace one."""
    if name != "title":
        raise SystemExit(f"unknown start state {name!r}: only 'title' is defined")
    states = Path(states)
    if (states / f"{name}.sav").exists():
        raise SystemExit(f"{states / name}.sav exists; start states are never replaced")
    states.mkdir(parents=True, exist_ok=True)
    d = Driver(config, workdir=SCRATCH / f"make-{name}")
    try:
        sc = d.launch(None)
        data = d.save_state()
        assert savestate.Savestate(data).screen().digest() == sc.digest()
    finally:
        d.terminate()
    (states / f"{name}.sav").write_bytes(data)
    meta = {"sha256": sha256(data), "screen_digest": sc.digest(), "game_dir": str(d.game_dir), "drive_layout": d.drive_layout(),
            "config": d.config, "made": host_times(), "events": d.events}
    (states / f"{name}.json").write_text(json.dumps(meta, indent=1))
    return StartState(name, states)


def verify_release(cache):
    known = json.loads((ROOT / "artifacts/known.json").read_text())["sets"]
    m = next(e["manifest"] for e in known if e["manifest"]["id"] == SET_ID)
    bad = [f["path"] for f in m["files"]
           if not (Path(cache) / f["path"]).is_file() or sha256((Path(cache) / f["path"]).read_bytes()) != f["sha256"]]
    if bad:
        raise SystemExit(f"{cache} does not match artifacts/known.json set {SET_ID} for: "
                         f"{', '.join(bad)} (run setup/goal2-runtime.sh)")
    return m["id"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("make-state").add_argument("name")
    sub.add_parser("read").add_argument("savestate")
    a = ap.parse_args(argv)
    if a.cmd == "make-state":
        st = make_state(a.name)
        print(f"{st.path}: sha256 {st.sha256}, screen {st.screen_digest}")
    else:
        s = savestate.Savestate(Path(a.savestate).read_bytes())
        ticks, raw = s.ticks()
        print(s.screen().text())
        print(f"screen sha256 {s.screen().digest()}; mode {s.video_mode():02x}; ticks 0x{ticks:08x} ({raw.hex(' ')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
