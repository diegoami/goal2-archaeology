#!/usr/bin/env python3
"""E005 (T12, Q003): the same seeded matches at `cycles` 5000, 30000 and `max`, from a restored state
(its delay calibration DS:A9FF made at 30000) and from a fresh launch at the state's DOS time
(calibrated anew). One run/1 record per match, and one per calibration read.

    python3 experiments/E005-q003-cycles/run.py calibrate --cycles 5000 --reps 3 --batch c1
    python3 experiments/E005-q003-cycles/run.py restores --state e004-1001 --cycles 30000 --reps 3 --batch b1
    python3 experiments/E005-q003-cycles/run.py fresh --state e004-1001 --cycles 30000 [--slot 1] --batch b1

- calibrate: a fresh launch at the setting, polled to the title screen; DS:A9FF read there (`214B:1DA7`
  has run by then: start-up code, F004, F005);
- restores: per rep, restore the state (Host+L) then a quick result; restore it again, then a watched
  match;
- fresh: a fresh launch at the setting with the DOS clock set to the state's own DOS date and time
  (I3, from the state's stored config), E004's keys to the captain screen, then a quick result; the
  same again for a watched match (`--slot` gives the session its own game folder).
The start states are E004's (`experiments/E004-q002-quick-result/run.py make-state`, at cycles=30000).
The match is runtime/driver/match.py (`play`, unchanged); the clock passed to it is also the clock of
every read's "seconds since the starting burst". A record is written only when runtime/driver/ and
this folder have no uncommitted change, and never over an existing one (L207)."""
import argparse
import importlib.util
import json
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import commentary  # noqa: E402
import cycle  # noqa: E402
import driver  # noqa: E402
import match  # noqa: E402

_spec = importlib.util.spec_from_file_location("e004", ROOT / "experiments" / "E004-q002-quick-result" / "run.py")
e004 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e004)

EXPERIMENT = "E005"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2, r0231)
IDS = driver.SCRATCH / "e005" / "ids"
CYCLES = ("5000", "30000", "max")   # the task's three settings (T12 Scope)
# Bound of one match, seconds from the starting keys to full time, in place of match.py's 900 s (E004's
# watched matches at 30000). Evidence: the smoke run of this script before E005-r0001 (records kept in
# scratch, not runs/) played e004-1001 watched at 30000 in 209.8 host s, its halves 75.0 and 73.7 guest
# s by the BIOS ticks; every guest instruction takes 6 times the guest time at 5000, so about 900 guest s
# there, longer than 900 host s with the reads. [designed] three times that.
MATCH_TIMEOUT = 2700
A9FF = 0xA9FF   # the calibrated delay count, a dword (DS:A9FF low word, DS:AA01 high word): seg_214B_04.asm:44-69


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def a9ff(state):
    """The dword DS:A9FF of GOAL.EXE (low word at A9FF, high at AA01, as 214B:1DA7 stores and 214B:1E09
    compares them): passes of the calibration loop per millisecond, measured at start-up."""
    return int.from_bytes(state.ds_bytes(A9FF, 4), "little")


def emulators(own=()):
    """The DOSBox-X and Xvfb processes on the host not started by this run: [pid, seconds running, name].
    Only the name is kept (another session's command line holds its host paths)."""
    p = subprocess.run(["ps", "-eo", "pid=,etimes=,comm="], capture_output=True, text=True).stdout
    out = []
    for line in p.splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3 and parts[2].strip() in ("dosbox-x", "Xvfb") and int(parts[0]) not in own:
            out.append([int(parts[0]), int(parts[1]), parts[2].strip()])
    return out


def loadavg():
    try:
        return Path("/proc/loadavg").read_text().strip()
    except OSError:
        return "not read"


class Clock:
    """time.monotonic, remembering its first call: match.play calls it first just before the starting
    burst (`t0 = clock()`), so `since()` is seconds since that burst on the clock play measures with."""

    def __init__(self, clock=time.monotonic):
        self.clock, self.t0 = clock, None

    def __call__(self):
        now = self.clock()
        if self.t0 is None:
            self.t0 = now
        return now

    def since(self):
        return None if self.t0 is None else round(self.clock() - self.t0, 3)


class Run:
    def __init__(self, kind, arm, n, args, commit, cycles, st, slot=None):
        if cycles not in CYCLES:
            raise ValueError(f"cycles {cycles!r}: one of {', '.join(CYCLES)}")
        self.kind, self.arm, self.n, self.args, self.commit, self.st = kind, arm, n, args, commit, st
        self.cycles = cycles
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        cfg = {"cycles": cycles}
        self.dos_time = self.dos_date = None
        if kind == "fresh":  # the state's own DOS date and time (I3), so the seed is the state's
            self.dos_time, self.dos_date = st.config["dos_time"], st.config["dos_date"]
            cfg.update(dos_time=self.dos_time, dos_date=self.dos_date)
        game = driver.GAME_DIR if slot is None else driver.SCRATCH / f"e005-game-{slot}"
        self.d = driver.Driver(cfg, workdir=driver.SCRATCH / "e005" / self.run_id, game_dir=game)
        self.obs, self.step, self.located = [], 0, False
        self.tracker = commentary.Tracker()
        self.keys, self.reads, self.seconds = [], 0, None
        self.clock = Clock()
        self.clock_error = None
        self.final = None
        self.pre_keys = list(e004.TO_MAIN + e004.TO_CAPTAIN)
        self.host = {}
        self.read_rows = []   # every match read, kept in one observation (README amendment 2)

    def add_full(self, label, read):
        times, state = read[0], read[1]
        self.obs.extend(e004.full_observations(self.step, label, times, state))
        self.obs.append(a9ff_observation(self.step, label, state))
        if not self.located:
            p = e004.e003.program_observations(self.step, state)
            self.obs.extend(p)
            self.located = "not found" not in p[0]["value"]

    def on_read(self, label, times, state):
        self.step += 1
        self.reads += 1
        self.read_rows.append(read_row(self.step, times, self.clock.since(), state))
        self.tracker.add(commentary.Snapshot(state), label)
        self.final = (times, state)

    def own(self):
        return {p.pid for p in (self.d.dbx, self.d.xvfb) if p}

    def go(self):
        status = "completed"
        try:
            if self.kind == "restores":
                self.d.launch(self.st, displace_key="n")
                self.host["launch"] = (emulators(self.own()), loadavg())
                self.add_full("before restore (title screen displaced by n)", self.d.pre_restore)
                sc = self.d.last[1].screen()
                self.add_full("restored", self.d.last)
            else:
                sc = self.d.launch(None)
                self.host["launch"] = (emulators(self.own()), loadavg())
                self.add_full("title (fresh launch)", self.d.last)
                keys = e004.TO_MAIN + e004.TO_CAPTAIN
                for i, k in enumerate(keys):
                    self.step += 1
                    self.d.keys(k)
                    sc = self.d.settle(sc.digest(), what=f"after key {k}")
                    if i == len(e004.TO_MAIN) - 1:
                        self.add_full(f"after key {i + 1} ({k})", self.d.last)
                k = e004.extra_key(sc)
                if k:
                    self.step += 1
                    self.pre_keys.append(k)
                    self.d.keys(k)
                    sc = self.d.settle(sc.digest(), what=f"after key {k} (team screen: play)")
                self.add_full("captain screen", self.d.last)
            if not e004.at_captain(sc):
                raise RuntimeError("not at the captain screen before the match: " + sc.lines()[-1].strip())
            _, self.reads, self.seconds = match.play(self.d, self.arm, self.on_read, timeout=MATCH_TIMEOUT, clock=self.clock, keys=self.keys)
            self.step += 1
            self.add_full("full time", self.final)
        except Exception as e:  # noqa: BLE001
            if isinstance(e, driver.ClockNotApplied):
                self.clock_error = str(e)
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
            if self.d.last is not None:
                self.step += 1
                self.add_full("last complete read before the abort", self.d.last)
        finally:
            self.host["end"] = (emulators(self.own()), loadavg())
            gone = self.d.terminate()
        return self.record(status, gone)

    def record(self, status, gone):
        d = self.d
        head = []
        if d.launched:
            head = [{"step": 0, "source": "log", "field": "host UTC time at launch", "value": d.launched["utc"]},
                    {"step": 0, "source": "log", "field": "host local time at launch, with UTC offset, and zone name",
                     "value": f"{d.launched['local']} {d.launched['tz']}"}]
        conf_text, conf_sha = d.conf_public() if getattr(d, "conf", None) else ("not written", "0" * 64)
        head.append({"step": 0, "source": "file", "field": "DOS clock read back: CLOCK.TXT as DOS wrote it (`date /t`, then `time /t`) before GOAL, right after setting the date and time when they were set",
                     "value": d.clock_applied if d.clock_applied is not None else "not read"})
        head.append(cycles_observation(self.cycles))
        last = self.step + 1
        tail = host_observations(self.host, last) + [reads_observation(self.read_rows, last)] + [
            {"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf_text},
            {"step": 0, "source": "file", "field": "sha256 of that config text (UTF-8)", "value": conf_sha},
            {"step": 0, "source": "log", "field": "batch label given on the command line", "value": self.args.batch},
            {"step": last, "source": "log", "field": "keys sent from the key that starts the match to full time: [seconds since the starting burst, key, why] (runtime/driver/match.py)",
             "value": json.dumps(self.keys)},
            {"step": last, "source": "log", "field": "match: savestate reads from the starting keys to full time, and seconds", "value": f"{self.reads} reads, {self.seconds} s"},
            {"step": last, "source": "memory", "field": "commentary lines of the match in order, accumulated over the reads from the ring DS:7C38 (runtime/driver/commentary.py): [n, template, team, text]",
             "value": json.dumps([[x["n"], x["template"], x["team"], x["text"]] for x in self.tracker.lines], ensure_ascii=False)},
            {"step": last, "source": "memory", "field": "events among them (templates " + ", ".join(f"{k} {v}" for k, v in commentary.EVENTS.items()) + "): [kind, team, text]",
             "value": json.dumps(self.tracker.events(), ensure_ascii=False)},
            {"step": last, "source": "memory", "field": "commentary lines between successive reads (deltas of DS:80EE modulo 200), and reads where lines may have been lost",
             "value": json.dumps({"deltas": self.tracker.deltas, "gaps": self.tracker.gaps})},
            {"step": last, "source": "log", "field": "lines of DOSBox-X's own output (dosbox.out) that mention save, load, corrupt, date, time or cycle, in order, "
             "except the two lines every savestate writes (counted in the next observation)",
             "value": "\n".join(dosbox_lines(cycle.dosbox_out(d))[0])},
            {"step": last, "source": "log", "field": "count of the lines left out of the previous observation: [`LOG: File : <work>/... is N bytes`, `Saved. (Slot`]",
             "value": json.dumps(dosbox_lines(cycle.dosbox_out(d))[1])},
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [{"level": "I1", "what": "text screen, BIOS data area (0040:0049, 0040:006C) and GOAL.EXE data-segment memory (DS:7B62, DS:7B64, DS:8336, DS:A9FD, the dword DS:A9FF, the commentary ring DS:7C38 and counter DS:80EE, the score DS:9B3C, the names at [DS:9B6C], the delay byte at [DS:A923]+0x3F, two known strings) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "a savestate is written at each read, including every read during the match"
                  + (", and one is loaded (Host+L) at the start" if self.kind == "restores" else "")
                  + " (vocabulary/interventions.md lists save and load of state as I2; neutrality tested by E004's replays, not assumed)"}]
        if self.dos_time:
            inter.append(i3(self.dos_date, self.dos_time, d.clock_applied, self.clock_error))
        made = self.st.config
        if self.kind == "restores":
            start = {"id": self.st.name, "sha256": self.st.sha256,
                     "restore": (f"fresh DOSBox-X process at cycles={self.cycles} (config sha256 {conf_sha}) with C: mounted from the folder the savestate was made with, "
                                 f"recreated from the verified release copy; GOAL run to its title screen; key n to change the screen; then Host+L "
                                 f"loads the savestate whose sha256 is given (made by E004's `run.py make-state` at cycles={made.get('cycles')}, DOS time {made.get('dos_time')} on "
                                 f"{made.get('dos_date')}: the captain screen of the next match; it carries the DS:A9FF calibrated in that session); "
                                 f"polled until the screen digest equals the one stored with it ({self.st.screen_digest}); DOS clock of this session not set "
                                 f"(the restore brings the state's own BIOS ticks, F004)")}
        else:
            start = {"id": "fresh-launch", "sha256": conf_sha,
                     "restore": (f"fresh DOSBox-X process at cycles={self.cycles} (config sha256 {conf_sha}), game folder recreated from the verified release copy, nothing "
                                 f"restored (GOAL calibrates DS:A9FF anew); DOS time set to {self.dos_time} on {self.dos_date} (the DOS time of start state {self.st.name}) before GOAL ran; then the keys "
                                 f"{' '.join(self.pre_keys)}, each followed by a settle poll, to the captain screen (an Enter after the last only when the team screen came first)")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT,
            "arm": arm_name(self.arm, self.kind, self.st.name, self.cycles), "rep": self.n,
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E005-q003-cycles/run.py", "sha256": SCRIPT_SHA,
                        "args": [self.kind, "--arm", self.arm, "--state", self.st.name, "--cycles", self.cycles]
                        + (["--dos-time", self.dos_time, "--dos-date", self.dos_date] if self.dos_time else [])
                        + ["--batch", self.args.batch, "starting keys: " + " ".join(match.START_KEYS[self.arm])]},
            "observations": obs, "outputs": [],
            "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
            "ended": driver.host_times()["utc"], "status": status,
        }
        return write_record(record)


def arm_name(arm, kind, state, cycles):
    return f"{arm}-{'restore' if kind == 'restores' else 'fresh'}-{state}-cycles-{cycles}"


def cycles_observation(cycles):
    return {"step": 0, "source": "file", "field": "cycles setting of the session: DOSBox-X [cpu] cycles in the config it was launched with", "value": cycles}


def a9ff_observation(step, label, state):
    raw = state.ds_bytes(A9FF, 4)
    return {"step": step, "source": "memory", "addr": f"0x{state.program().ds_base + A9FF:x}",
            "field": f"{label}: dword DS:A9FF of GOAL.EXE (the delay count 214B:1DA7 calibrates), little-endian (bytes in memory order)",
            "value": f"0x{int.from_bytes(raw, 'little'):08x} ({raw.hex(' ')})"}


def read_row(step, times, since, state):
    """One match read as a list: its step, host UTC time just before the savestate was requested, host
    seconds since the starting burst (monotonic, the clock match.play measures with, taken after the
    read), the BIOS tick count 0040:006C, the dword DS:A9FF, the screen's sha256 (chars+attributes),
    DS:80EE, DS:7B62, the score bytes DS:9B3C and DS:9B3D, and the commentary rows (rows 1-3, columns 31-66)."""
    sc = state.screen()
    snap = commentary.Snapshot(state)
    return [step, times["utc"], since, f"0x{state.ticks()[0]:08x}", f"0x{a9ff(state):08x}", sc.digest(), f"0x{snap.counter:04x}",
            f"0x{state.ds_word(0x7B62):04x}", snap.score[0], snap.score[1], " / ".join(match.commentary_rows(sc))]


def reads_observation(rows, step):
    """Every match read in one observation (a record of a match at 5000 stays under T07's 1 MB: E005-r0031,
    one observation per read, is 1.48 MB)."""
    return {"step": step, "source": "memory", "field": f"match reads, one list per read: {READ_FIELDS}",
            "value": json.dumps(rows, ensure_ascii=False, separators=(",", ":"))}


READ_FIELDS = ("[step, host UTC time, host s since the starting burst, BIOS ticks 0040:006C, dword DS:A9FF, screen sha256, "
               "DS:80EE, DS:7B62, score DS:9B3C, score DS:9B3D, commentary rows 1-3]")


def dosbox_lines(text):
    """The DOSBox-X output lines a record keeps (save, load, corrupt, date, time, cycle; not Save_Remark or
    Time_Stamp), less the two each savestate writes, and the counts of those two: ([lines], [n, n])."""
    keep, files, saved = [], 0, 0
    for line in text.splitlines():
        low = line.lower()
        if not any(w in low for w in ("save", "load", "corrupt", "date", "time", "cycle")) or "Save_Remark" in line or "Time_Stamp" in line:
            continue
        if line.startswith("LOG: File : <work>/"):
            files += 1
        elif "Saved. (Slot" in line:
            saved += 1
        else:
            keep.append(line)
    return keep, [files, saved]


def host_observations(host, last):
    out = []
    for when, step in (("launch", 0), ("end", last)):
        if when in host:
            procs, load = host[when]
            out.append({"step": step, "source": "process", "field": f"other DOSBox-X and Xvfb processes on the host at {when} (not started by this run): [pid, seconds running, name]",
                        "value": json.dumps(procs)})
            out.append({"step": step, "source": "process", "field": f"/proc/loadavg at {when}", "value": load})
    return out


def i3(dos_date, dos_time, applied_text, clock_error):
    back = (applied_text or "").split()
    if clock_error is None and applied_text is not None and len(back) >= 2:
        applied = f"applied: DOS reported date {back[0]} and time {back[1]} right after (`date /t`, `time /t`), checked by Driver.launch"
    else:
        applied = f"NOT verified as applied: {clock_error or 'no read-back'}"
    return {"level": "I3", "what": f"DOS date {dos_date} and DOS time {dos_time} requested with the DOSBox-X commands "
            f"`date {dos_date}` and `time {dos_time}` in the autoexec, before GOAL runs; {applied}"}


def write_record(record):
    text = json.dumps(record, indent=1, ensure_ascii=False) + "\n"
    if str(ROOT) in text:
        raise SystemExit(f"{record['run_id']}: a host path leaked into the record")
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{record['run_id']}.json", "x", encoding="utf-8") as f:  # never overwrite (L207)
        f.write(text)
    print(f"{record['run_id']} {record['arm']}: {record['status']}")
    return record["status"] == "completed"


def calibrate(n, args, commit, cycles):
    """A fresh launch at `cycles` to the title screen; DS:A9FF read there."""
    run_id = f"{EXPERIMENT}-r{n:04d}"
    d = driver.Driver({"cycles": cycles}, workdir=driver.SCRATCH / "e005" / run_id, game_dir=driver.SCRATCH / "e005-game-cal")
    obs, status, host = [], "completed", {}
    try:
        d.launch(None)
        host["launch"] = (emulators({p.pid for p in (d.dbx, d.xvfb) if p}), loadavg())
        times, state = d.last
        obs = cycle.read_observations(1, "title (fresh launch)", times, state) + [a9ff_observation(1, "title (fresh launch)", state)]
    except Exception as e:  # noqa: BLE001
        status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
        traceback.print_exc()
    finally:
        host["end"] = (emulators({p.pid for p in (d.dbx, d.xvfb) if p}), loadavg())
        gone = d.terminate()
    conf_text, conf_sha = d.conf_public() if getattr(d, "conf", None) else ("not written", "0" * 64)
    obs = [cycles_observation(cycles),
           {"step": 0, "source": "log", "field": "host UTC time at launch", "value": d.launched["utc"] if d.launched else "not launched"},
           {"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf_text},
           {"step": 0, "source": "log", "field": "batch label given on the command line", "value": args.batch}] + obs + host_observations(host, 2) + [
           {"step": 2, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)", "value": "both exited" if gone else "a process remained"},
           {"step": 2, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))}]
    record = {
        "schema": "run/1", "run_id": run_id, "experiment": EXPERIMENT, "arm": f"calibrate-cycles-{cycles}", "rep": n,
        "code_commit": commit, "machine": cycle.machine_id(),
        "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
        "runtime": {"driver": f"runtime/driver/driver.py@{commit}", "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                    "fingerprint": cycle.fingerprint(d, conf_sha)},
        "interventions": [{"level": "I1", "what": "text screen, BIOS data area and the dword DS:A9FF of GOAL.EXE read from a DOSBox-X savestate (Host+S)"},
                          {"level": "I2", "what": "one savestate written at the title screen"}],
        "start_state": {"id": "fresh-launch", "sha256": conf_sha,
                        "restore": f"fresh DOSBox-X process at cycles={cycles} (config sha256 {conf_sha}), game folder recreated from the verified release copy, nothing restored, DOS clock not set; polled to GOAL's title screen"},
        "seed": None,
        "actions": {"script": "experiments/E005-q003-cycles/run.py", "sha256": SCRIPT_SHA,
                    "args": ["calibrate", "--cycles", cycles, "--batch", args.batch]},
        "observations": sorted(obs, key=lambda o: o["step"]), "outputs": [],
        "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
        "ended": driver.host_times()["utc"], "status": status,
    }
    return write_record(record)


def reserve_id():
    """The next run number not used by a record or a reservation; mkdir makes the claim atomic."""
    IDS.mkdir(parents=True, exist_ok=True)
    while True:
        used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")] + [int(p.name) for p in IDS.iterdir() if p.name.isdigit()]
        n = 1 + max(used, default=0)
        try:
            (IDS / str(n)).mkdir()
            return n
        except FileExistsError:
            continue


def load_state(name):
    st = e004.load_state(name)   # refuses a state with another drive layout, with E004's remake command
    if st.config.get("cycles") != "30000":
        raise SystemExit(f"refused: {name} was made at cycles={st.config.get('cycles')}; E005's states are made at 30000")
    return st


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=["calibrate", "restores", "fresh"])
    ap.add_argument("--cycles", required=True, choices=CYCLES)
    ap.add_argument("--state", help="restores, fresh: an E004 start state, e.g. e004-1001")
    ap.add_argument("--reps", type=int, default=1, help="calibrate, restores: repetitions")
    ap.add_argument("--slot", type=int, help="fresh: a game folder of the session's own")
    ap.add_argument("--batch", default="", help="a label written into each record")
    a = ap.parse_args(argv)
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)), "experiments/E004-q002-quick-result")
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiments: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok = total = 0
    if a.kind == "calibrate":
        for _ in range(a.reps):
            total += 1
            ok += calibrate(reserve_id(), a, commit, a.cycles)
    else:
        if not a.state:
            raise SystemExit(f"{a.kind} needs --state")
        st = load_state(a.state)
        reps = a.reps if a.kind == "restores" else 1
        for _ in range(reps):
            for arm in ("quick", "watched"):
                total += 1
                ok += Run(a.kind, arm, reserve_id(), a, commit, a.cycles, st, slot=a.slot if a.kind == "fresh" else None).go()
    print(f"{ok} of {total} runs completed")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
