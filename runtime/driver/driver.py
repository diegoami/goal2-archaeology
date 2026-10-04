#!/usr/bin/env python3
"""The G1 driver: GOAL2 under DOSBox-X 2024.03.01 in Xvfb, keys through xdotool (XTEST), the screen
and guest memory read from savestates (F001, route A). Standard library only.

    d = Driver(config); d.launch(start_state); d.keys("n"); sc = d.screen(); d.memory(0x449, 1)
    d.save_state(); d.restore(state); d.terminate()

Every wait is a bounded poll or a delay written into `Driver.events` (seconds since launch, what);
the cycle writes `events` into each run record. Process groups are started by this driver and only
those are killed (by PID). Display `:99` is never used (another project runs there).

CLI:
    python3 runtime/driver/driver.py make-state title     # store the title-screen start state
    python3 runtime/driver/driver.py read <file.sav>      # print the screen, mode and ticks of a savestate
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

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "goal2"            # the verified release copy (setup/goal2-runtime.sh)
STATES = ROOT / ".cache" / "states" / "driver"  # start states: <name>.sav and <name>.json, git-ignored
SCRATCH = ROOT / "scratch" / "driver"
# F001 Anomalies: a savestate keeps the host folder drive C: was mounted from, so every session
# mounts this one folder, recreated from the release copy at each launch.
GAME_DIR = SCRATCH / "game"
TITLE_TEXT = "Do you want to load a saved game"

# Delays (seconds) taken from runtime/spike/dbx.py, where F001 measured with them; each use is logged.
KEY_HOLD = 0.08       # a game key: press, hold, release
HOSTKEY_HOLD = 0.15   # each step of a DOSBox-X host-key (F12) combination
POLL = 0.05           # savestate file poll interval
X_POLL = 0.1          # Xvfb and window poll interval

CLOCK_DIR = "dosclock"  # session subfolder mounted as D: for the clock read-back (clock option only)
CLOCK_SLACK = 5        # seconds a read-back time may run past the time set (written right after `time`)


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
    "10/04/1993\n10:00:00\n"): the date must be equal, the time within CLOCK_SLACK seconds after.
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
        if not 0 <= got_t - want <= CLOCK_SLACK:
            raise ClockNotApplied(f"DOS time set to {dos_time}, DOS reports {m_t[0]}")
    return m_d[0], m_t[0]


KEYMAP = {"Enter": "Return", "Esc": "Escape", "Space": "space", "Up": "Up", "Down": "Down",
          "Left": "Left", "Right": "Right", "Backspace": "BackSpace", "Tab": "Tab"}

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
    def __init__(self, config=None, workdir=None, game_dir=GAME_DIR):
        self.config = dict(DEFAULT_CONFIG, **(config or {}))
        self.workdir = Path(workdir or SCRATCH / "session").resolve()
        self.game_dir = Path(game_dir).resolve()
        self.savefile = self.workdir / "state.sav"
        self.xvfb = self.dbx = None
        self.display = self.env = self.wid = None
        self.events = []
        self.last = self.pre_restore = None  # (host times, Savestate) of the latest read; the read before a restore
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
        has `dos_date` (MM/DD/YYYY) or `dos_time` (HH:MM:SS); else nothing, and the guest clock
        starts from the host's as before. DOSBox-X 2024.03.01's DATE takes MM/DD/YYYY only: given
        10-04-1993 it prints the current date and changes nothing (E003-r0030, r0031; F004), so any
        other form, and any date or time no calendar or DOS has (99/99/1993, a year outside DOS's
        1980-2099, 24:00:00), is refused here (clock_values). After setting, the lines write DOS's own
        date and time (`date /t`, `time /t`) to CLOCK.TXT on a drive D: mounted from the session folder,
        so launch() can read back what DOSBox-X applied (check_clock) before GOAL runs."""
        c = self.config
        if not (c.get("dos_date") or c.get("dos_time")):
            return ""
        clock_values(c.get("dos_date"), c.get("dos_time"))
        lines = "".join(f"{cmd} {c[k]}\n" for cmd, k in (("date", "dos_date"), ("time", "dos_time")) if c.get(k))
        return (lines + f"mount d {self.workdir / CLOCK_DIR}\ndate /t > d:\\clock.txt\ntime /t >> d:\\clock.txt\nc:\n")

    def clock_readback(self):
        """The text DOS wrote to CLOCK.TXT after the date and time were set, or None (no clock option)."""
        for f in (self.workdir / CLOCK_DIR).glob("*"):
            if f.name.lower() == "clock.txt":
                return f.read_text(errors="replace")
        return None

    def conf_public(self):
        """The config with host paths replaced by <work> and <game>, and its sha256 (what a record carries)."""
        text = self.conf.replace(str(self.workdir), "<work>").replace(str(self.game_dir), "<game>")
        return text, sha256(text.encode())

    # ---- launch ---------------------------------------------------------------------------
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
        self._start_xvfb()
        self.env = dict(os.environ, DISPLAY=self.display, SDL_AUDIODRIVER="dummy")
        args = [os.environ.get("DOSBOX_X", "dosbox-x"), "-conf", str(conf), "-fastlaunch", "-nogui", "-nomenu",
                "-savedir", str(self.workdir), "-set", f"dosbox savefile={self.savefile}"]
        self.dbx = subprocess.Popen(args, env=self.env, stdout=open(self.workdir / "dosbox.out", "w"),
                                    stderr=subprocess.STDOUT, start_new_session=True)
        self.log("dosbox-x started")
        self.wid = self._wait_window(15)
        self._x("windowfocus", self.wid)
        self.log("window focused")
        sc = self.wait_screen(lambda sc: TITLE_TEXT in sc.text(), timeout, "title screen")
        if self.clock_lines():
            # I3 verified, not assumed: what DOS reported right after `date`/`time`, before GOAL ran
            self.clock_applied = self.clock_readback()
            self.log(f"DOS clock read back: {(self.clock_applied or 'no CLOCK.TXT').strip()!r}")
            check_clock(self.config.get("dos_date"), self.config.get("dos_time"), self.clock_applied)
        if start_state is None:
            return sc
        if sc.digest() == start_state.screen_digest:
            self.keys(displace_key)
            sc = self.settle(sc.digest(), what=f"displaced by {displace_key}")
        self.pre_restore = self.last
        return self.restore(start_state)

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
        """One keystroke per name through XTEST: press, hold `hold` seconds (logged), release."""
        for name in names:
            k = KEYMAP.get(name, name)
            self._x("keydown", k)
            time.sleep(hold)  # key hold; its duration is logged just below
            self._x("keyup", k)
            self.log(f"key {name} held {hold}s")

    def _hostkey(self, name, hold=HOSTKEY_HOLD):
        """DOSBox-X host key (F12) + a key: an emulator hotkey, not game input. Holds are logged."""
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
    def restore(self, state, timeout=15):
        """Host+L loads state's savestate; poll until the screen digest equals the one stored with it."""
        shutil.copy(state.path, self.savefile)
        self._hostkey("l")
        self.log(f"Host+L sent ({state.name})")
        return self.wait_screen(lambda sc: sc.digest() == state.screen_digest, timeout, f"restore {state.name}")

    # ---- terminate ------------------------------------------------------------------------
    def _kill(self, p):
        if p and p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGTERM)  # the process group this driver started (start_new_session)
            except ProcessLookupError:
                pass
        if p:
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.log(f"{'dosbox-x' if p is self.dbx else 'Xvfb'} pid {p.pid} still running 10s after SIGTERM: SIGKILL to its group")
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()

    def terminate(self):
        """SIGTERM to the DOSBox-X and Xvfb process groups this driver started; returns True when both are gone."""
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
    meta = {"sha256": sha256(data), "screen_digest": sc.digest(), "game_dir": str(d.game_dir),
            "config": d.config, "made": host_times(), "events": d.events}
    (states / f"{name}.json").write_text(json.dumps(meta, indent=1))
    return StartState(name, states)


def verify_release(cache):
    m = json.loads((ROOT / "artifacts/known.json").read_text())["sets"][0]["manifest"]
    bad = [f["path"] for f in m["files"]
           if not (Path(cache) / f["path"]).is_file() or sha256((Path(cache) / f["path"]).read_bytes()) != f["sha256"]]
    if bad:
        raise SystemExit(f"{cache} does not match artifacts/known.json for: {', '.join(bad)} (run setup/goal2-runtime.sh)")
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
