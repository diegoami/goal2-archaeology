#!/usr/bin/env python3
"""The T29 human-playthrough recorder: one command that runs GOAL2 windowed on the owner's display
and turns the sitting into a complete behavioural record — a timestamped chain of whole-machine
savestates, an index of them, and (optionally) a screen video of the game window.

    python3 runtime/human/recorder.py self-test [--video]
    python3 runtime/human/recorder.py play [--video] [--quit-after SECS]

Windows on the display $DISPLAY points at (the owner's session); there is no headless mode here.
The emulator, config family and session layout follow the G1 driver (runtime/driver/driver.py):
windowed `surface` output, `savefile` in the session folder, drive C: mounted from a per-session
copy of the verified release (never the release cache itself — F001: a savestate remembers the
mounted folder, and the owner's in-game saves must land in the copy, not in the cache), drive D:
mounted for the clock read-back, exactly as every driver launch lays them out.

Correctness rules (each pinned by a test in tests/test_human_record.py):
- The focus gate. The hazard is sending the emulator host key (F12+S) while another window is
  focused — the owner's terminal would receive it. WSLg's XWayland exposes no focus API (the two
  real prototype sittings of 2026-10-07: `xdotool getactivewindow` and `getwindowfocus` both
  fail), so a focus *check* is impossible; the gate is enforced by construction instead: every
  host key is sent with `xdotool key --window <wid>` DIRECTLY to the game window (verified live in
  the same sittings), never as a global keystroke. SEND_TO_WINDOW is the gate's constant; the
  watcher refuses to send at all when it has no window id.
- The staging gate. The watcher never renames, moves, deletes or writes the savestate file
  DOSBox-X is writing (`state.sav` in the session folder). A snapshot is staged — copied to
  snapshots/, hashed, indexed — only after the live file is a complete savestate zip (the same
  test driver.save_state applies) AND its size has been stable for STABLE_POLLS consecutive polls.
- A sitting ends by closing the game window, by Ctrl+C in the terminal, or (scripted sittings)
  when --quit-after elapses; a partial chain is a valid record. On the way out the watcher stages
  one last complete live savestate if there is one (the owner's own F12+S presses are captured
  too), stops the video with SIGTERM (a clean finalize), and writes the session's meta.json.
- Video. The 2026-10-07 prototype bug — a detached `ffmpeg -f x11grab` writing a 48-byte
  header-only mp4 while running — is the mp4 (mov) muxer's finalize-only index: an unclean death
  leaves `ftyp` alone. The recorder replaces mp4 with Matroska, whose clusters are written as
  frames arrive, finalizes it with SIGTERM (never SIGKILL while it can be helped), polls the file's
  growth while recording, and records bytes, sha256 and a stalled flag in the session meta — so a
  grab that stopped producing frames is visible in the record instead of silent.

Standard library only, plus the G1 driver's modules."""
import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import driver  # noqa: E402  (verify_release, host_times, SET_ID, CACHE; config family via Driver)

# ---- constants ----------------------------------------------------------------------------------
# Each one is a rule of the recorder; tests/test_human_record.py fails when any is mutated.
CADENCE_S = 20.0      # seconds between snapshot ticks (the brief: every ~20 s) [designed]
STABLE_POLLS = 3      # consecutive equal-size polls before a snapshot is staged (the brief: poll
                      # size stability; never touch the live file) [designed]
POLL_S = 0.25         # savestate poll interval, as the driver's POLL but human-paced [designed]
SAVE_TIMEOUT_S = 15.0  # bound on one savestate write, driver.save_state's timeout
RESEND_AFTER_S = 3.0   # F12+S sent again when no savestate appeared, driver.save_state's resend
TERM_GRACE_S = 0.5     # SIGTERM -> SIGKILL grace for dosbox-x, driver's measured TERM_GRACE
VIDEO_TERM_GRACE_S = 10.0  # grace for ffmpeg's clean finalize on SIGTERM [designed]
VIDEO_STALL_S = 60.0   # no growth for this long while recording => meta `video_stalled` [designed]
SEND_TO_WINDOW = True  # the focus gate: keys only DIRECTLY to the game window, never global
SAVE_KEYS = "F12+s"    # the G1 driver's host key + save (F001)
SESSIONS = ROOT / "scratch" / "human" / "sessions"   # session folders (git-ignored: savestates
SELFTEST = ROOT / "scratch" / "human" / "selftest"   # and videos stay out of git, like run states)
WANT_DOSBOX = "2024.03.01"
WINDOW_CLASS = "dosbox"  # the driver's window search


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def host_times():
    """The host clock now, as the driver writes it into records (UTC + local + zone)."""
    return driver.host_times()


def dosbox_version():
    """The version banner of the dosbox-x on PATH (it exits 1 and writes to stderr), or None."""
    try:
        out = subprocess.run(["dosbox-x", "-version"], capture_output=True, text=True, timeout=30)
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


def key_cmd(wid):
    """The argv that sends the host save key. The focus gate lives here: with SEND_TO_WINDOW the
    keys go to the game window only (--window wid, an XSendEvent to that one window); turning the
    gate off would broadcast F12+S to whatever has the owner's focus, which is the hazard the
    brief forbids. The watcher never calls this with wid=None."""
    if not SEND_TO_WINDOW:
        return ["xdotool", "key", SAVE_KEYS]
    return ["xdotool", "key", "--window", str(wid), SAVE_KEYS]


def window_alive(wid, env):
    """Whether the game window still exists (a cheap named lookup; also the send's precondition —
    a vanished window means the sitting is over, never a blind send)."""
    return xdotool(["getwindowname", str(wid)], env=env).returncode == 0


def find_window(env, timeout=15.0, sleep=time.sleep, clock=time.monotonic):
    """The game window's id, polled like the driver's _wait_window."""
    end = clock() + timeout
    while clock() < end:
        p = xdotool(["search", "--class", WINDOW_CLASS], env=env)
        ids = p.stdout.split()
        if ids:
            return ids[0]
        sleep(0.25)
    raise RuntimeError(f"no {WINDOW_CLASS} window within {timeout}s on DISPLAY={env.get('DISPLAY')!r}")


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


def zip_complete(path):
    """The savestate zip's bytes when `path` holds a complete one (every driver.save_state check:
    a zip that opens, tests clean, and holds the three components), else None. Read-only: the
    live file is never touched."""
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if z.testzip() is None and "Vga" in names and "Memory" in names and "Save_Remark" in names:
                return path.read_bytes()
    except (zipfile.BadZipFile, OSError):
        pass
    return None


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


class Watcher:
    """The snapshot loop: one tick every CADENCE_S — send the host save key straight to the game
    window, wait for a complete and size-stable live savestate, stage a copy, append the index.

    clock/sleep/xrun and dbx.poll() are injectable so tests run the whole loop on a fake clock
    with no emulator. `stop` is polled between ticks (the SIGINT/SIGTERM flag)."""

    def __init__(self, session, live, wid, dbx, env, t0=None, index="index.jsonl",
                 clock=time.monotonic, sleep=time.sleep, xrun=None, alive=None, log=None):
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
        self.index_path = self.session / index
        self.snapshots = self.session / "snapshots"
        self.t0 = self.clock() if t0 is None else t0
        self.seq = 0
        self.problems = []

    # -- staging (the staging gate) -----------------------------------------------------
    def wait_stable(self):
        """Wait until the live savestate is complete AND its size has been stable for
        STABLE_POLLS consecutive polls; returns its bytes. The live file is only ever read."""
        sent = self.clock()
        stable_size, stable_count = None, 0
        deadline = self.clock() + SAVE_TIMEOUT_S
        while self.clock() < deadline:
            if self.dbx.poll() is not None:
                raise RuntimeError(f"dosbox-x exited with code {self.dbx.returncode} during a savestate")
            data = zip_complete(self.live)
            if data is not None:
                if len(data) == stable_size:
                    stable_count += 1
                else:
                    stable_size, stable_count = len(data), 1
                if stable_count >= STABLE_POLLS:
                    return data
            else:
                stable_size, stable_count = None, 0
            if self.clock() - sent > RESEND_AFTER_S:
                self.log(f"F12+S sent again: no complete savestate after {RESEND_AFTER_S}s")
                self.xrun(key_cmd(self.wid))
                sent = self.clock()
            self.sleep(POLL_S)
        raise TimeoutError(f"savestate not complete and stable within {SAVE_TIMEOUT_S}s")

    def stage(self, data, origin="watcher"):
        """Copy the bytes to snapshots/ (the live file is not moved or renamed), append one index
        line (flushed at once, so an abrupt end leaves a valid prefix)."""
        self.seq += 1
        name = f"snap-{self.seq:04d}-{utc_stamp()}.sav"
        out = self.snapshots / name
        out.write_bytes(data)
        entry = {"seq": self.seq, "file": f"snapshots/{name}", "bytes": len(data), "sha256": sha256(data),
                 "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                 "elapsed_s": round(self.clock() - self.t0, 3), "origin": origin}
        with open(self.index_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.log(f"staged {entry['file']} ({len(data)} bytes, sha256 {entry['sha256'][:16]}...)")
        return entry

    def tick(self):
        """One snapshot: send the host key to the game window, then stage when stable."""
        if not self.alive():
            raise StopIteration("game window is gone")
        self.xrun(key_cmd(self.wid))
        self.log(f"F12+S sent to window {self.wid}")
        try:
            data = self.wait_stable()
        except TimeoutError as e:
            self.problems.append(str(e))
            self.log(f"snapshot skipped: {e}")
            return None
        return self.stage(data)

    # -- the loop -----------------------------------------------------------------------
    def run(self, quit_after=None, stop=lambda: False):
        """Tick at t0 + n*CADENCE_S (the first tick immediately: the session's opening state is
        part of the chain) until the window closes, dosbox-x exits, `stop()` fires or (scripted
        sittings) quit_after seconds have passed. Returns the staged entries."""
        entries, n = [], 0
        while True:
            if stop():
                self.log("stop requested")
                break
            if quit_after is not None and self.clock() - self.t0 >= quit_after:
                self.log(f"quit-after {quit_after}s reached")
                break
            if self.dbx.poll() is not None:
                self.log(f"dosbox-x exited with code {self.dbx.returncode}: the sitting is over")
                break
            next_tick = self.t0 + n * CADENCE_S
            now = self.clock()
            if now < next_tick:
                self.sleep(min(next_tick - now, 0.5))
                continue
            n += 1
            try:
                e = self.tick()
            except StopIteration as e:
                self.log(str(e))
                break
            if e:
                entries.append(e)
        return entries

    def shutdown_stage(self, indexed_sha):
        """Best-effort last snapshot: a complete live savestate the loop has not staged yet (the
        owner may have pressed F12+S themselves just before ending the sitting)."""
        data = zip_complete(self.live)
        if data is None or sha256(data) in indexed_sha:
            return None
        try:
            return self.stage(data, origin="shutdown")
        except OSError as e:
            self.problems.append(f"shutdown snapshot failed: {e}")
            return None


# ---- video ---------------------------------------------------------------------------------------
def video_cmd(geometry, display, out):
    """The ffmpeg argv for the game window's screen video: x11grab on the window's region,
    Matroska output (clusters written as frames arrive; a killed recorder leaves a playable
    prefix — the mp4 replacement, see the module docstring)."""
    x, y, w, h = geometry
    # libx264 needs even dimensions; the game window is 640x400 at 2x, but never trust it
    w, h = w - (w % 2), h - (h % 2)
    return ["ffmpeg", "-nostdin", "-loglevel", "level", "-y",
            "-f", "x11grab", "-framerate", "10", "-video_size", f"{w}x{h}", "-i", f"{display}+{x},{y}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-pix_fmt", "yuv420p",
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
        prototype's silent failure — flag it loudly instead."""
        if self.proc is None or self.proc.poll() is not None:
            return
        try:
            size = self.out.stat().st_size
        except OSError:
            return
        if size != self.last_size:
            self.last_size, self.last_growth = size, self.clock()
        elif self.clock() - self.last_growth > VIDEO_STALL_S:
            self.stalled = True

    def stop(self):
        """SIGTERM to the process group (ffmpeg writes its trailer), SIGKILL to a survivor."""
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
                "seconds": round(self.clock() - t0, 3), "stalled": self.stalled, "ended": how}


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
    meta = {"created": host_times(), "ended": None, "stop_reason": None,
            "artifact_set": driver.SET_ID, "config": conf, "config_sha256": sha256(conf.encode()),
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


def play(video=False, quit_after=None):
    """One sitting: launch windowed dosbox-x, watch it, stop cleanly, write meta. Returns 0."""
    if not os.environ.get("DISPLAY"):
        print("play: DISPLAY is not set; run from a graphical session", file=sys.stderr)
        return 1
    session, meta = new_session()
    logf = open(session / "session.log", "a", encoding="utf-8")

    def log(msg):
        line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
        logf.write(line + "\n")
        logf.flush()
        print(line, flush=True)

    log(f"session {session}")
    env = dict(os.environ)
    argv = [os.environ.get("DOSBOX_X", "dosbox-x"), "-conf", str(session / "dosbox.conf"),
            "-fastlaunch", "-nogui", "-nomenu", "-savedir", str(session),
            "-set", f"dosbox savefile={session / 'state.sav'}"]
    dbx = subprocess.Popen(argv, stdout=logf, stderr=subprocess.STDOUT, start_new_session=True)
    log(f"dosbox-x started (pid {dbx.pid})")
    stop_flag = {"now": False}

    def on_signal(signum, frame):
        stop_flag["now"] = True
        log(f"signal {signum}: stopping after the current step")

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    vid = None
    geom0 = None
    try:
        wid = find_window(env)
        log(f"game window {wid}")
        meta.update({"window_id": wid, "dosbox_x_pid": dbx.pid})
        if video:
            if shutil.which("ffmpeg") is None:
                log("--video requested but ffmpeg is not installed: continuing without video")
            else:
                geom0 = window_geometry(wid, env)
                if geom0 is None:
                    log("--video requested but the window geometry is unknown: continuing without video")
                else:
                    v = video_cmd(geom0, env["DISPLAY"], session / "video.mkv")
                    vid = Video(v, session / "video.mkv")
                    vid.start()
                    log(f"video started: {' '.join(v)}")
        watcher = Watcher(session, session / "state.sav", wid, dbx, env, log=log)
        entries = watcher.run(quit_after=quit_after, stop=lambda: stop_flag["now"])
        # the window may have closed between the last poll and here; stage the owner's last
        # F12+S if there is one, then stop the emulator
        last = watcher.shutdown_stage({e["sha256"] for e in entries})
        if last:
            entries.append(last)
        if dbx.poll() is None:
            reason = "signal" if stop_flag["now"] else "quit-after"
            terminate(dbx)
        else:
            reason = "window-closed"
        vinfo = vid.stop() if vid else None
        if vinfo and vinfo["bytes"] == 0:
            log(f"WARNING: the video file is empty ({vinfo['ended']})")
        meta.update({"ended": host_times(), "stop_reason": reason,
                     "snapshots": len(entries),
                     "video": dict(vinfo, requested=bool(video), geometry=geom0) if vid else
                              {"requested": bool(video), "used": False},
                     "problems": watcher.problems})
        (session / "meta.json").write_text(json.dumps(meta, indent=1))
        log(f"done: {len(entries)} snapshots, stop {reason}"
            + (f", video {vinfo['bytes']} bytes" if vinfo else ""))
    finally:
        terminate(dbx)
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
    if v is None or WANT_DOSBOX not in v:
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
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    st = sub.add_parser("self-test", help="verify the release copy and tools, write a config, exit")
    st.add_argument("--video", action="store_true", help="also require ffmpeg")
    pl = sub.add_parser("play", help="record one sitting")
    pl.add_argument("--video", action="store_true", help="also record the game window (mkv)")
    pl.add_argument("--quit-after", type=float, default=None, metavar="SECS",
                    help="stop the sitting after SECS seconds (scripted sittings)")
    a = ap.parse_args(argv)
    if a.cmd == "self-test":
        return self_test(with_video=a.video)
    return play(video=a.video, quit_after=a.quit_after)


if __name__ == "__main__":
    sys.exit(main())
