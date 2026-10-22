#!/usr/bin/env python3
"""E039 (T83, #369): E038's new game at a chosen DOS date, plus a savestate caught during GOAL's start-up before
it reads the DOS date (214B:1C63 -> 235C:006C, `int 21h` AH=2Ah at 235C:0071; T83 static reading). One record per run.

    python3 experiments/E039-start-year/run.py --dos-date 10/04/1990 --batch b1

As E038 (its docstring below), with these differences: `cycles=30000` (fixed, so the start-up's delay calibration
214B:1DA7 is not host-dependent; savestates during DOSBox-X's boot crash this build at fixed cycles, T83 probe, so
the first savestate is requested `FIRST_SAVE` s after the window appears); the DOS date is given; and every
savestate polled before the title is checked: the first whose CPU is in GOAL.EXE's code (load + 0000..2580) while
DS:A9FD (the year 214B:1C63 stores) is still 0 is kept as `e039-pre-date-r<nnnn>.sav`. A run that catches none
records that and goes on (the state is date-independent; one run's catch serves both dates).

E038's docstring:

A fresh launch at DOS time 10:00:00 on 10/04/2026 (I3, as E006-r0001), then F001's keys of a new game
(`n Enter Enter b o b Enter Enter Enter`: E006's keys without the last Enter, which leaves the first manager menu for
the country browser). Before each key and at the end, savestates are polled (Host+S, I2) until the screen is the one
expected AND, at a screen that reads its key through 214B:08DD (1771:080C, static reading in T82), the CPU is inside
08DD's INT 16h call: CS F000 and one frame of 08DD's call of `Intr` 235C:000B on the stack (its far return
214B:0904, its three argument words; goal2 core/runner.py read_entry). The name entry (214B:0D90, a "key pressed?"
poll loop that reads the BIOS tick count for the cursor's blink, F004) never waits in the read: its state is kept
at the first read whose screen shows the prompt. Each kept state is written to `.cache/states/driver/e038-<screen>-
r<nnnn>.sav` (git-ignored; never replaced), named in the record's `outputs` by sha256 and stored on the owner's Drive
(`goal2drive:goal2-archaeology/E038/`). Per kept state the record holds the screen, the CPU's registers (the `CPU`
component, E021 notes section 1), 08DD's frame and its callers' return addresses, the seed words DS:7B62, DS:7B64
(F004) and the BIOS mode byte and tick count. A record is written only when this folder and runtime/driver/ have
no uncommitted change, and never over an existing one (L207)."""
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
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
import cycle  # noqa: E402
import driver  # noqa: E402
import savestate  # noqa: E402
from watched_match import cpu_state  # noqa: E402

EXPERIMENT = "E039"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())
DOS_TIME = "10:00:00"      # E006-r0001's (I3)
CYCLES = "30000"           # E004's fixed value
FIRST_SAVE = 0.2           # [designed] s: T83 probe, the first savestate at 0.2 s landed in 214B:1DE4 (calibration)
STORE = "drive:goal2drive:goal2-archaeology/E039/"
# (screen, key pressed to reach it, how it waits, text that must be on the screen). The texts are the screens'
# own (F001's keys; tools/screens/build.py names the kinds); "read": the CPU is in 08DD's INT 16h call.
SCREENS = [
    ("title-load-prompt", None, "read", "Do you want to load a saved game? (Y/N)"),
    ("title-player-count", "n", "read", "How many players"),
    ("country-select", "Enter", "read", "PLEASE SELECT YOUR COUNTRY"),
    ("country-select-name-entry", "Enter", "poll", "Type in characters (maximum 14)"),
    (None, "b", None, None),
    (None, "o", None, None),
    (None, "b", None, None),
    ("after-name-1", "Enter", "read", None),
    ("after-name-2", "Enter", "read", None),
    ("manager-menu", "Enter", "read", None),
]
WAIT = 300                # [designed] s per screen: E039-r0001 (aborted) did not reach the title's read in 60 s at cycles=30000 with continuous savestate polling
INTR_RETURN, READ_LOCALS, INTR_ARGS = 0x0904, 0x14, 6     # 214B:08DD 08E0, 08F7-08FF


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def read_frame(st, regs):
    """08DD's frame above SS:SP when the CPU is in its INT 16h call, else None: {'bp', 'callers', ...}."""
    if regs["CS"] != 0xF000:
        return None
    load = st.program().load
    ss, sp = regs["SS"], regs["ESP"] & 0xFFFF
    w = lambda off: int.from_bytes(st.memory(ss * 16 + (off & 0xFFFF), 2), "little")  # noqa: E731
    hits = []
    for off in range(sp, sp + 0x200, 2):
        if w(off) == INTR_RETURN and w(off + 2) == (load + 0x214B) & 0xFFFF:
            bp = (off + 4 + INTR_ARGS + READ_LOCALS) & 0xFFFF
            if w(off + 4) == (bp - READ_LOCALS) & 0xFFFF and w(off + 6) == ss and w(off + 8) & 0xFF == 0x16:
                hits.append((off, bp))
    if len(hits) != 1:
        return None
    off, bp = hits[0]
    return {"intr_return_at": f"{ss:04X}:{off:04X}", "bp": f"{bp:04X}", "callers": callers(st, load, ss, bp)}


def callers(st, load, ss, bp, depth=6):
    """Return addresses up the BP chain from a frame of 214B (as the listing writes them). A frame is near when the
    call before its return address is `E8` not preceded by `push cs` (0E), and its caller is then in the same
    segment; otherwise far, its segment the word above."""
    w = lambda off: int.from_bytes(st.memory(ss * 16 + (off & 0xFFFF), 2), "little")  # noqa: E731
    out, cs = [], (load + 0x214B) & 0xFFFF
    for _ in range(depth):
        ip = w(bp + 2)
        code = st.memory(cs * 16 + ip - 5, 5)
        near = code[2] == 0xE8 and code[1] != 0x0E
        if not near:
            cs = w(bp + 4)
        rel = (cs - load) & 0xFFFF
        if rel >= 0x2581:
            out.append(f"{cs:04X}:{ip:04X} (outside the program)")
            break
        out.append(f"{rel:04X}:{ip:04X}" + (" (near)" if near else ""))
        nb = w(bp)
        if nb <= bp:
            break
        bp = nb
    return out


class EarlyDriver(driver.Driver):
    """The driver, with the first savestate delayed and every read before the title checked for the pre-date state."""
    def read(self):
        if not getattr(self, "_first_done", False):
            time.sleep(self.first_save)  # one bounded wait before the first savestate (docstring)
            self._first_done = True
        times, st, data = super().read()
        if getattr(self, "pre_date", None) is None and not getattr(self, "titled", False):
            regs = cpu_state(data)
            try:
                prog = st.program()
                rel = (regs["CS"] - prog.load) & 0xFFFF
                pre = rel < 0x2581 and st.ds_word(0xA9FD) == 0
            except ValueError:
                rel, pre = None, False
            self.log(f"pre-title read: CPU {regs['CS']:04X}:{regs['EIP'] & 0xFFFF:04X}"
                     + (f" (load + {rel:04X})" if rel is not None else " (no GOAL program yet)")
                     + (f", DS:A9FD {st.ds_word(0xA9FD)}" if rel is not None else ""))
            if pre:
                self.pre_date = (times, st, data, regs)
        return times, st, data


class Run:
    def __init__(self, n, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.args, self.commit = args, commit
        self.dos_date = args.dos_date
        self.year = args.dos_date.split("/")[2]
        self.d = EarlyDriver({"dos_time": DOS_TIME, "dos_date": self.dos_date, "cycles": CYCLES},
                             workdir=driver.SCRATCH / "e039" / self.run_id)
        self.d.pre_date = None
        self.d.first_save = args.first_save
        self.obs, self.outputs, self.step, self.kept = [], [], 0, []

    def wait(self, name, how, text):
        t0 = time.monotonic()
        polls = 0
        while time.monotonic() - t0 < WAIT:
            polls += 1
            times, st, data = self.d.read()
            sc = st.screen()
            if text and text not in sc.text():
                continue
            regs = cpu_state(data)
            frame = read_frame(st, regs)
            if how == "read" and frame is None:
                continue
            if how == "read" and not text and self.kept and frame["callers"] == self.kept[-1][1]["callers"] \
                    and sc.digest() == self.kept[-1][2]:
                continue      # still the screen before the key
            self.d.log(f"{name}: kept after {polls} savestate polls ({time.monotonic() - t0:.1f} s)")
            return times, st, data, regs, frame
        raise RuntimeError(f"{name}: not reached within {WAIT}s ({polls} polls)")

    def keep(self, name, how, read):
        times, st, data, regs, frame = read
        label = name
        obs = cycle.read_observations(self.step, label, times, st)
        for o in obs:  # a screen before GOAL shows DOSBox-X's mount messages: host paths as conf_public writes them
            if isinstance(o.get("value"), str):
                o["value"] = (o["value"].replace(str(self.d.game_dir), "<game>").replace(str(self.d.workdir), "<work>")
                              .replace(str(ROOT), "<root>"))  # a path the screen wraps at column 80 keeps its root whole
        self.obs.extend(obs)
        self.obs.append({"step": self.step, "source": "memory", "field": f"{label}: CPU registers from the savestate's CPU component (E021 notes section 1), hex",
                         "value": json.dumps({k: f"{v:04X}" if k in ("ES", "CS", "SS", "DS", "FS", "GS") else f"{v:08X}" for k, v in regs.items()})})
        self.obs.append({"step": self.step, "source": "memory", "field": f"{label}: 214B:08DD's frame (Intr's return 214B:0904 on the stack) and the callers' return addresses up the BP chain, listing addresses; null when the CPU is not in 08DD's INT 16h call",
                         "value": json.dumps(frame)})
        for off in (0x7B62, 0x7B64, 0xA9FD, 0xA9FF, 0x8336):
            self.obs.append({"step": self.step, "source": "memory", "addr": f"0x{st.program().ds_base + off:x}",
                             "field": f"{label}: word at DS:{off:04X} (F004; A9FD the year 214B:1C63 stores, A9FF the delay calibration), hex", "value": f"{st.ds_word(off):04x}"})
        gseg, goff = st.ds_word(0xA925), st.ds_word(0xA923)
        if gseg:
            g = st.memory(gseg * 16 + goff, 0x42)
            self.obs.append({"step": self.step, "source": "memory", "field": f"{label}: the game record [DS:A923] +0x38..+0x41 (1771:9B85: +0x3A year, +0x3C stage, +0x40 year mod 4 = 2), hex",
                             "value": g[0x38:0x42].hex()})
        fname = f"e039-{self.year}-{name}-{self.run_id.split('-')[1]}.sav"
        states = driver.STATES
        states.mkdir(parents=True, exist_ok=True)
        with open(states / fname, "xb") as f:
            f.write(data)
        meta = {"sha256": driver.sha256(data), "screen_digest": st.screen().digest(), "game_dir": str(self.d.game_dir),
                "drive_layout": self.d.drive_layout(), "config": self.d.config, "clock_applied": self.d.clock_applied,
                "run_id": self.run_id, "screen": name, "wait": how, "cpu": {k: v for k, v in regs.items()}, "frame": frame}
        (states / fname.replace(".sav", ".json")).write_text(json.dumps(meta, indent=1))
        self.outputs.append({"name": fname, "sha256": meta["sha256"], "store": STORE})
        self.kept.append((name, frame or {"callers": None}, st.screen().digest()))
        print(f"{name}: {fname} sha256 {meta['sha256']} CPU {regs['CS']:04X}:{regs['EIP'] & 0xFFFF:04X} "
              f"callers {frame['callers'] if frame else None}", flush=True)

    def go(self):
        status = "completed"
        try:
            self.d.launch(None)
            self.d.titled = True
            if self.d.pre_date is not None:
                times, st, data, regs = self.d.pre_date
                self.keep("pre-date", "start-up", (times, st, data, regs, None))
            else:
                self.obs.append({"step": 0, "source": "log", "field": "pre-date: no savestate before the title had the CPU in GOAL.EXE's code with DS:A9FD 0", "value": "none caught"})
            for name, key, how, text in ([] if self.args.catch_only else SCREENS):
                if key is not None:
                    self.step += 1
                    if name is None:
                        prev = self.d.last[1].screen().digest()
                        self.d.keys(key)
                        self.d.settle(prev, what=f"after key {key}")
                        continue
                    self.d.keys(key)
                self.keep(name, how, self.wait(name, how, text))
        except Exception as e:  # noqa: BLE001
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
        finally:
            gone = self.d.terminate()
        return self.record(status, gone)

    def record(self, status, gone):
        d = self.d
        conf_text, conf_sha = d.conf_public() if getattr(d, "conf", None) else ("not written", "0" * 64)
        head = []
        if d.launched:
            head = [{"step": 0, "source": "log", "field": "host UTC time at launch", "value": d.launched["utc"]}]
        head.append({"step": 0, "source": "file", "field": "DOS clock read back: CLOCK.TXT as DOS wrote it (`date /t`, then `time /t`) before GOAL, right after setting the date and time",
                     "value": d.clock_applied if d.clock_applied is not None else "not read"})
        last = self.step + 1
        tail = [
            {"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf_text},
            {"step": 0, "source": "file", "field": "sha256 of that config text (UTF-8)", "value": conf_sha},
            {"step": 0, "source": "log", "field": "batch label given on the command line", "value": self.args.batch},
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        back = (d.clock_applied or "").split()
        applied = (f"applied: DOS reported date {back[0]} and time {back[1]} right after (`date /t`, `time /t`), checked by Driver.launch"
                   if len(back) >= 2 else "NOT verified as applied: no read-back")
        keys = [k for _, k, _, _ in SCREENS if k]
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": f"start-year-{self.year}" + ("-catch" if self.args.catch_only else ""),
            "rep": int(self.run_id.split("-r")[1]), "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": [
                {"level": "I1", "what": "text screen, BIOS data area (0040:0049, 0040:006C), GOAL.EXE memory (DS:7B62, DS:7B64, the stack above SS:SP) and the CPU's registers read from DOSBox-X savestates (Host+S; components Vga, Memory, CPU)"},
                {"level": "I2", "what": "savestates written at every poll (vocabulary/interventions.md lists save of state as I2); one per screen kept"},
                {"level": "I3", "what": f"DOS date {self.dos_date} and DOS time {DOS_TIME} requested with the DOSBox-X commands `date {self.dos_date}` and `time {DOS_TIME}` in the autoexec, before GOAL runs; {applied}"}],
            "start_state": {"id": "fresh-launch", "sha256": conf_sha,
                            "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, nothing "
                                        f"restored; DOS time set to {DOS_TIME} on {self.dos_date} before GOAL ran; then the keys {' '.join(keys)}, "
                                        "each sent once the screen before it waits in 214B:08DD's read (the name's letters after a settle poll)")},
            "seed": None,
            "actions": {"script": "experiments/E039-start-year/run.py", "sha256": SCRIPT_SHA, "args": list(self.args.argv)},
            "observations": sorted(head + self.obs + tail, key=lambda o: o["step"]), "outputs": self.outputs,
            "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
            "ended": driver.host_times()["utc"], "status": status,
        }
        text = json.dumps(record, indent=1, ensure_ascii=False) + "\n"
        if str(ROOT) in text:
            where = [o["field"] for o in record["observations"] if str(ROOT) in json.dumps(o, ensure_ascii=False)]
            raise SystemExit(f"{self.run_id}: a host path leaked into the record: {where}")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / f"{self.run_id}.json", "x", encoding="utf-8") as f:
            f.write(text)
        print(f"{self.run_id}: {status}")
        return status == "completed"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", default="")
    ap.add_argument("--dos-date", required=True, help="MM/DD/YYYY, set before GOAL runs")
    ap.add_argument("--first-save", type=float, default=FIRST_SAVE, help="s before the first savestate (default %(default)s)")
    ap.add_argument("--catch-only", action="store_true", help="stop at the title: only the pre-date catch (amendment 1)")
    a = ap.parse_args(argv)
    a.argv = argv
    driver.clock_values(a.dos_date, DOS_TIME)
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    ok = Run(1 + max(used, default=0), a, git("rev-parse", "--short", "HEAD")).go()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
