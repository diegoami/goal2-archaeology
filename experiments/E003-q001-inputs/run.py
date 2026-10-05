#!/usr/bin/env python3
"""E003 (T08, Q001): fresh launches and restored quick results with the DOS time fixed (I3) or free,
reading the seed words of GOAL.EXE's data segment from every savestate. One run/1 record per run.

    python3 experiments/E003-q001-inputs/run.py make-main [--dos-time 10:00:00 --dos-date 10/04/2026]
    python3 experiments/E003-q001-inputs/run.py d0 --runs 2 [--dos-time HH:MM:SS --dos-date MM/DD/YYYY] --batch b1
    python3 experiments/E003-q001-inputs/run.py d3 --runs 3 [--dos-time ... --dos-date ...] --batch b1

Arms (F001's D0 and D3, keys copied from runtime/spike/probe.py TO_MAIN, SEQ_MENU, SEQ_B):
- d0: a fresh launch (nothing restored), GOAL to its title, then the 11 D0 keys to the main menu;
- d3: a fresh launch, the `main` start state restored with Host+L (polled until its screen digest
  returns), then the 10 D3 keys: into a match, `c`, a logged 2.0 s delay, the quick result `r`, ...;
- d3b (added after r0026): as d3, but the Enter that starts the match and `r` are sent together.
Each key is followed by a settle poll (the screen changed and two reads agree), except `c`, followed by
a 2.0 s delay as in F001. Every read (a savestate) records the host clock, the screen, the BIOS tick
count and, from GOAL.EXE's data segment located through its MCB (runtime/driver/savestate.py), the
words at DS:7B62, DS:7B64 and DS:8336 (I1). With --dos-time the autoexec sets the DOS date and time
before GOAL runs (I3). A record is written only when runtime/driver/ and this folder have no
uncommitted change, and never over an existing one (L207)."""
import argparse
import json
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import cycle  # noqa: E402
import driver  # noqa: E402
import savestate  # noqa: E402

EXPERIMENT = "E003"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
# The script's sha256 as loaded, for every record of this process: a record written after the file
# changed on disk would otherwise name code it did not run (E004-r0231, as E004's run.py does).
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())
CYCLES = "auto"   # F001's determinism probes ran at cycles=auto (runtime/spike/dbx.py default)

# F001 (runtime/spike/probe.py): TO_MAIN reaches the screen main.sav was taken at; SEQ_MENU is D0's last key.
TO_MAIN = ["n", "Enter", "Enter", "b", "o", "b", "Enter", "Enter", "Enter", "Enter"]
SEQ_MENU = ["Esc"]
SEQ_A = ["Esc", "Up", "Enter"]
SEQ_B = SEQ_A + ["Enter", "Enter", "c", "r", "Enter", "Enter", "r"]
DELAY_AFTER = {"c": 2.0}  # F001 SEQ_B: ("c", 2.0); the match screen animates and never settles
# Arm d3b (added after r0026): D3 without the live-match wait. "Enter+r" sends Enter (the captain
# screen's select, which starts the match) and then r with no poll between, so r is in the keyboard
# buffer before the match loop polls it; then the settle poll.
SEQ_B_BUFFERED = SEQ_A + ["Enter", "Enter+r", "Enter", "Enter", "r"]
DEFAULT_DATE = "10/04/2026"  # MM/DD/YYYY; r0001 … r0033 passed MM-DD-YYYY, which DOSBox-X ignored (README, amendment 2)

# Data-segment words read at every read (static leads of T06): TP RandSeed low and high words
# (23E4:11D7 stores CX and DX of INT 21h AH=2Ch there), and the second stream's seed (0791:F3F2).
# DS:A9FD (added in amendment 2): the year GetDate returned at startup (214B:1C63).
DS_WORDS = (0x7B62, 0x7B64, 0x8336, 0xA9FD)
# Known bytes of the initialised data segment (static/goal-exe/data/ds_2581_01.hex), read once per
# record to show that the located base is GOAL.EXE's DS: a Pascal string "TRY OUT" and "on for".
DS_CHECKS = ((0x0024, b"\x07TRY OUT"), (0x00C0, b"on for"))


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def seed_observations(step, label, state):
    obs = []
    for off in DS_WORDS:
        try:
            base = state.program().ds_base
            raw = state.ds_bytes(off, 2)
            obs.append({"step": step, "source": "memory", "addr": f"0x{base + off:x}",
                        "field": f"{label}: word at DS:{off:04X} of GOAL.EXE, guest memory from the savestate, little-endian (bytes in memory order)",
                        "value": f"0x{int.from_bytes(raw, 'little'):04x} ({raw.hex(' ')})"})
        except ValueError as e:
            obs.append({"step": step, "source": "memory", "field": f"{label}: word at DS:{off:04X} of GOAL.EXE", "value": f"not read: {e}"})
    return obs


def program_observations(step, state):
    try:
        p = state.program()
    except ValueError as e:
        return [{"step": step, "source": "memory", "field": "GOAL.EXE data segment located through its MCB", "value": f"not found: {e}"}]
    obs = [{"step": step, "source": "memory", "addr": f"0x{p.mcb * 16:x}",
            "field": "GOAL.EXE located: its MCB (owner = the next segment, name GOAL), PSP, load segment and data segment",
            "value": p.describe()}]
    for off, want in DS_CHECKS:
        got = state.ds_bytes(off, len(want))
        obs.append({"step": step, "source": "memory", "addr": f"0x{p.ds_base + off:x}",
                    "field": f"{len(want)} bytes at DS:{off:04X}, hex (static/goal-exe/data/ds_2581_01.hex has {want.hex(' ')})",
                    "value": got.hex(" ")})
    return obs


class Run:
    def __init__(self, arm, n, args, commit, start_state=None):
        self.arm, self.n, self.args, self.commit, self.st = arm, n, args, commit, start_state
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        cfg = {"cycles": CYCLES}
        if args.dos_time:
            cfg.update(dos_time=args.dos_time, dos_date=args.dos_date)
        self.d = driver.Driver(cfg, workdir=driver.SCRATCH / "e003" / self.run_id)
        self.obs, self.recorded, self.step = [], set(), 0
        self.located = False
        self.clock_error = None  # driver.ClockNotApplied's message when the read-back disagreed

    def add(self, label, read=None):
        read = read or self.d.last
        if read is None or id(read) in self.recorded:
            return
        self.recorded.add(id(read))
        times, state = read
        self.obs.extend(cycle.read_observations(self.step, label, times, state))
        if not self.located:
            p = program_observations(self.step, state)
            self.obs.extend(p)
            self.located = "not found" not in p[0]["value"]
        self.obs.extend(seed_observations(self.step, label, state))

    def press(self, key):
        self.step += 1
        prev = self.d.last[1].screen().digest()
        self.d.keys(*key.split("+"))
        if key in DELAY_AFTER:
            time.sleep(DELAY_AFTER[key])  # recorded delay (F001 SEQ_B), logged below
            self.d.log(f"delay {DELAY_AFTER[key]}s after key {key} (the screen animates)")
            self.d.read()
        else:
            self.d.settle(prev, what=f"after key {key}")
        self.add(f"after key {self.step} ({key})")

    def go(self):
        status = "completed"
        try:
            if self.arm == "d0":
                self.d.launch(None)
                self.add("title (fresh launch)")
                keys = TO_MAIN + SEQ_MENU
            else:
                self.d.launch(self.st, displace_key="n")
                self.add("before restore (title screen displaced by n)", self.d.pre_restore)
                self.add("restored")
                keys = SEQ_B if self.arm == "d3" else SEQ_B_BUFFERED
            for k in keys:
                self.press(k)
        except Exception as e:  # noqa: BLE001
            if isinstance(e, driver.ClockNotApplied):
                self.clock_error = str(e)
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
            self.step += 1
            self.add("last complete read before the abort")
        finally:
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
        if d.clock_applied is not None or self.args.dos_time:  # every launch from rework round 3
            head.append({"step": 0, "source": "file", "field": "DOS clock read back: CLOCK.TXT as DOS wrote it (`date /t`, then `time /t`) before GOAL, right after setting the date and time when they were set",
                         "value": d.clock_applied if d.clock_applied is not None else "not read"})
        tail = [
            {"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf_text},
            {"step": 0, "source": "file", "field": "sha256 of that config text (UTF-8)", "value": conf_sha},
            {"step": 0, "source": "log", "field": "batch label given on the command line", "value": self.args.batch},
            {"step": self.step, "source": "log", "field": "lines of DOSBox-X's own output (dosbox.out) that mention save, load, corrupt, date or time (Save_Remark and Time_Stamp lines left out), in order",
             "value": "\n".join(l for l in cycle.dosbox_out(d).splitlines()
                                if any(w in l.lower() for w in ("save", "load", "corrupt", "date", "time"))
                                and "Save_Remark" not in l and "Time_Stamp" not in l)},
            {"step": self.step, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after 10 s, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": self.step, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [{"level": "I1", "what": "text screen, BIOS data area (0040:0049, 0040:006C) and GOAL.EXE data-segment words (DS:7B62, DS:7B64, DS:8336, and two known strings) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "a savestate is written at each read" + (", and one is loaded (Host+L) at the start" if self.st else "")
                  + " (vocabulary/interventions.md lists save and load of state as I2; neutrality not tested)"}]
        if self.args.dos_time:
            # From the rework round: what DOS reported after setting the clock decides what is declared.
            back = (d.clock_applied or "").split()
            if self.clock_error is None and d.clock_applied is not None:
                applied = f"applied: DOS reported date {back[0]} and time {back[1]} right after (`date /t`, `time /t`)"
            else:
                applied = f"NOT verified as applied: {self.clock_error or 'no read-back'}"
            inter.append({"level": "I3", "what": f"DOS date {self.args.dos_date} and DOS time {self.args.dos_time} requested with the DOSBox-X "
                          f"commands `date {self.args.dos_date}` and `time {self.args.dos_time}` in the autoexec, before GOAL runs; {applied}"})
        keys = TO_MAIN + SEQ_MENU if self.arm == "d0" else SEQ_B if self.arm == "d3" else SEQ_B_BUFFERED
        if self.st:
            start = {"id": self.st.name, "sha256": self.st.sha256,
                     "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}) with C: mounted from the folder the savestate was made with, "
                                 f"recreated from the verified release copy; GOAL run to its title screen; key n to change the screen; then Host+L "
                                 f"loads the savestate whose sha256 is given; polled until the screen digest equals the one stored with it "
                                 f"({self.st.screen_digest}); DOS time {'set to ' + self.args.dos_time + ' before GOAL ran' if self.args.dos_time else 'not controlled'}")}
        else:
            start = {"id": "fresh-launch", "sha256": conf_sha,
                     "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}, the hash of the config text with host paths replaced), "
                                 f"game folder recreated from the verified release copy, nothing restored; DOS time "
                                 f"{'set to ' + self.args.dos_time + ' on ' + self.args.dos_date + ' before GOAL ran' if self.args.dos_time else 'not controlled (the guest clock starts from the host clock)'}")}
        arm = f"{self.arm}-{'time-' + self.args.dos_time.replace(':', '') if self.args.dos_time else 'time-free'}"
        if self.args.dos_time and self.args.dos_date != DEFAULT_DATE:
            arm += "-date-" + self.args.dos_date.replace("/", "").replace("-", "")
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": arm, "rep": self.n,
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E003-q001-inputs/run.py", "sha256": SCRIPT_SHA,
                        "args": [self.arm] + (["--dos-time", self.args.dos_time, "--dos-date", self.args.dos_date] if self.args.dos_time else [])
                        + ["--batch", self.args.batch, "keys: " + " ".join(keys)]},
            "observations": obs, "outputs": [],
            "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
            "ended": driver.host_times()["utc"], "status": status,
        }
        text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
        if str(ROOT) in text:
            raise SystemExit(f"{self.run_id}: a host path leaked into the record")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / f"{self.run_id}.json", "x", encoding="utf-8") as f:  # never overwrite (L207)
            f.write(text)
        print(f"{self.run_id} {arm}: {status}")
        return status == "completed"


def make_main(args):
    """The `main` start state: a fresh launch, TO_MAIN (F001's main.sav), stored like driver.make_state."""
    states = driver.STATES
    if (states / "main.sav").exists():
        raise SystemExit(f"{states}/main.sav exists; start states are never replaced")
    states.mkdir(parents=True, exist_ok=True)
    cfg = {"cycles": CYCLES}
    if args.dos_time:
        cfg.update(dos_time=args.dos_time, dos_date=args.dos_date)
    d = driver.Driver(cfg, workdir=driver.SCRATCH / "make-main")
    try:
        sc = d.launch(None)
        for k in TO_MAIN:
            prev = sc.digest()
            d.keys(k)
            sc = d.settle(prev, what=f"after key {k}")
        data = d.save_state()
        st = savestate.Savestate(data)
        assert st.screen().digest() == sc.digest()
    finally:
        d.terminate()
    (states / "main.sav").write_bytes(data)
    words = {f"DS:{o:04X}": f"0x{st.ds_word(o):04x}" for o in DS_WORDS}
    meta = {"sha256": driver.sha256(data), "screen_digest": sc.digest(), "game_dir": str(d.game_dir),
            "drive_layout": d.drive_layout(), "config": d.config,
            "made": driver.host_times(), "keys": TO_MAIN, "ticks": st.ticks()[0], "ds_words": words, "events": d.events}
    (states / "main.json").write_text(json.dumps(meta, indent=1))
    print(f"main.sav sha256 {meta['sha256']}, screen {sc.digest()}, ticks {meta['ticks']}, {words}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("arm", choices=["d0", "d3", "d3b", "make-main"])
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--dos-time", help="HH:MM:SS, set by `time` in the autoexec (I3)")
    ap.add_argument("--dos-date", default=DEFAULT_DATE, help="MM/DD/YYYY, set with --dos-time")
    ap.add_argument("--batch", default="", help="a label written into each record")
    a = ap.parse_args(argv)
    if a.arm == "make-main":
        return make_main(a) or 0
    if a.dos_time:
        driver.clock_values(a.dos_date, a.dos_time)  # refuse, before any run, a clock DOSBox-X cannot apply
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    st = driver.StartState("main") if a.arm in ("d3", "d3b") else None
    if st is not None:
        try:
            driver.Driver({"cycles": CYCLES}).check_start_state(st)  # refuse an incompatible state before any record
        except driver.StateLayoutMismatch as e:
            raise SystemExit(f"refused: {e}") from None
    first = 1 + max((int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")), default=0)
    ok = sum(Run(a.arm, first + i, a, commit, st).go() for i in range(a.runs))
    print(f"{ok} of {a.runs} runs completed")
    return 0 if ok == a.runs else 1


if __name__ == "__main__":
    sys.exit(main())
