#!/usr/bin/env python3
"""E011 (T25, Q010 milestone 1): the watched engine's ground truth — one watched match from an
E006 published start state, every savestate read recording the match clock (minute DS:831F,
sub-tick DS:831D, running DS:8325, minutes left DS:831B) and the seed DS:7B62, so (minute,
sub-tick, seed) pins each read to its tick (notes.md §4/§6). One run/1 record per launch.

    python3 experiments/E011-q010-watched-engine/run.py watched --from-run E006-r0005 --batch b1

Per run: a fresh launch; Host+L of an E006 published main-screen state (E007's `adopt`); E004's
keys to the captain screen; the savestate there is kept as this run's `watchstart` output. Then
E004's watched arm: `Enter Right Right Right Right Right` in one burst (the delay byte to 0, the
top speed), afterwards one Enter only on a stopped-clock screen that asks for one (half time
`hit any key`, the team screen `location:`), never during play (E004/F005's key discipline).
The savestate at the half-time team-screen stall — the wait inside 0791:9A32's 0791:ED8A, the
watched analogue of E010's quick half-time stall (notes.md §5) — is kept as the run's `halftime`
output and is the Unicorn harness's start state; both are published on release E011 and named in
the record's outputs. A record is written only when runtime/driver/ and this folder have no
uncommitted change, and never over an existing one (L207)."""
import argparse
import importlib.util
import json
import platform
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import commentary  # noqa: E402
import cycle  # noqa: E402
import driver  # noqa: E402
import match  # noqa: E402
import savestate  # noqa: E402


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e004 = _load("e004_run", "experiments/E004-q002-quick-result/run.py")
e007 = _load("e007_run", "experiments/E007-q009-player-screen/run.py")

EXPERIMENT = "E011"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
OUTPUTS = ROOT / "scratch" / "e011-outputs"       # git-ignored; published to release E011
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2)
CYCLES = e004.CYCLES          # E004's and E006's value, so the start state's runtime is unchanged
STATE_CONFIG = {"cycles": CYCLES}


def clock_read(state):
    """(minute 831F, sub-tick 831D, running 8325, minutes left 831B, seed 7B62, score)."""
    b = state.ds_bytes
    return (state.ds_word(0x831F), state.ds_word(0x831D), b(0x8325, 1)[0], state.ds_word(0x831B),
            state.ds_word(0x7B62), (b(0x9B3C, 1)[0], b(0x9B3D, 1)[0]))


def stall(sc, state, prev_stable):
    """The half-time team screen: stable, clock stopped (8325 = 0), `location:` shown (0791:9A32's
    0791:ED8A wait, notes.md §5). The minute there is 45 or 46 (the second half's clock, as E010's
    quick stall showed 46); the actual value is logged and checked by emu_check."""
    if state.ds_bytes(0x8325, 1)[0] != 0 or not prev_stable:
        return None
    return "location:" in sc.text() and state.ds_word(0x831F) in (45, 46)


class Run:
    def __init__(self, n, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.args, self.commit = args, commit
        self.st = driver.StartState(e007.adopt(args.from_run))
        self.d = driver.Driver(STATE_CONFIG, workdir=driver.SCRATCH / "e011" / self.run_id)
        self.obs, self.step, self.keys, self.pre_keys = [], 0, list(e004.TO_CAPTAIN)
        self.reads, self.seconds, self.final = 0, None, None
        self.tracker = commentary.Tracker()
        self.trajectory = []          # (831F, 831D, 7B62) per read: the ground truth emu_check uses
        self.prev_digest = None
        self.watchstart_blob, self.halftime_blob = None, None
        self.halftime_read = None

    def add_full(self, label, read):
        self.obs.extend(e004.full_observations(self.step, label, read[0], read[1]))
        self.obs.append({"step": self.step, "source": "memory",
                         "field": f"{label}: clock (831F, 831D, 8325, 831B), seed DS:7B62, score, GOAL.EXE data segment",
                         "value": " ".join(str(x) for x in clock_read(read[1]))})

    def on_read(self, label, times, state):
        self.step += 1
        self.reads += 1
        sc = state.screen()
        m, sub, running, left, seed, score = clock_read(state)
        self.obs.append({"step": self.step, "source": "memory",
                         "field": f"{label}: minute DS:831F, sub-tick DS:831D, clock running DS:8325, minutes left DS:831B, seed DS:7B62, score, screen sha256",
                         "value": f"{m} {sub} {running} {left} 0x{seed:04x} {score[0]} {score[1]} {sc.digest()}"})
        if running:
            self.trajectory.append((m, sub, seed))
        self.tracker.add(commentary.Snapshot(state), label)
        self.final = (times, state)
        stable = self.prev_digest == sc.digest()
        self.prev_digest = sc.digest()
        if self.halftime_blob is None and stall(sc, state, stable):
            self.halftime_blob = self.d.last_blob
            self.halftime_read = self.reads
            self.d.log(f"half-time team-screen stall at read {self.reads}: minute {m}, sub-tick {sub}, seed 0x{seed:04x}")

    def go(self):
        status, d = "completed", self.d
        try:
            sc = d.launch(self.st)
            self.add_full("start state restored (main screen)", d.last)
            for k in e004.TO_CAPTAIN:
                self.step += 1
                d.keys(k)
                sc = d.settle(sc.digest(), what=f"after key {k}")
            k = e004.extra_key(sc)
            if k:
                self.step += 1
                self.pre_keys.append(k)
                d.keys(k)
                sc = d.settle(sc.digest(), what=f"after key {k} (team screen: play)")
            if not e004.at_captain(sc):
                raise RuntimeError("not at the captain screen: " + sc.lines()[-1].strip())
            self.step += 1
            times, state, cap = d.read()
            self.add_full("captain screen (the watched match's start state)", (times, state))
            self.watchstart_blob = cap
            if state.ds_bytes(0x9A3E, 1)[0] != 0:
                raise RuntimeError("DS:9A3E set at the captain screen: the match would run quick")
            _, self.reads, self.seconds = match.play(d, "watched", self.on_read, keys=self.keys)
            if self.halftime_blob is None:
                raise RuntimeError("the half-time team-screen stall was never seen")
            self.step += 1
            self.add_full("full time", self.final)
            m, sub, running, left, seed, score = clock_read(self.final[1])
            self.obs.append({"step": self.step, "source": "memory",
                             "field": "half-time team-screen stall: the read whose savestate is this run's halftime output (8325=0, minute 45 or 46, stable team screen)",
                             "value": f"match read {self.halftime_read} of {self.reads}"})
            self.obs.append({"step": self.step, "source": "memory",
                             "field": "ground-truth trajectory: mid-play reads as [minute 831F, sub-tick 831D, seed 7B62], in read order",
                             "value": json.dumps(self.trajectory, separators=(",", ":"))})
        except Exception as e:  # noqa: BLE001
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
            if d.last is not None:
                self.step += 1
                self.add_full("last complete read before the abort", d.last)
        finally:
            gone = d.terminate()
        return self.record(status, gone)

    def record(self, status, gone):
        d = self.d
        head = []
        if d.launched:
            head = [{"step": 0, "source": "log", "field": "host UTC time at launch", "value": d.launched["utc"]},
                    {"step": 0, "source": "log", "field": "host local time at launch, with UTC offset, and zone name",
                     "value": f"{d.launched['local']} {d.launched['tz']}"}]
        conf_text, conf_sha = d.conf_public() if getattr(d, "conf", None) else ("not written", "0" * 64)
        last = self.step + 1
        tail = [
            {"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf_text},
            {"step": 0, "source": "file", "field": "sha256 of that config text (UTF-8)", "value": conf_sha},
            {"step": 0, "source": "log", "field": "batch label given on the command line", "value": self.args.batch},
            {"step": 0, "source": "log", "field": "keys sent after the restore to the captain screen, in order", "value": " ".join(self.pre_keys)},
            {"step": last, "source": "log", "field": "keys sent from the key that starts the match to full time: [seconds since the starting burst, key, why] (runtime/driver/match.py)",
             "value": json.dumps(self.keys)},
            {"step": last, "source": "log", "field": "match: savestate reads from the starting keys to full time, and seconds", "value": f"{self.reads} reads, {self.seconds} s"},
            {"step": last, "source": "memory", "field": "events of the match (runtime/driver/commentary.py): [kind, team, text]",
             "value": json.dumps(self.tracker.events(), ensure_ascii=False)},
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [{"level": "I1", "what": "text screen, BIOS data area and GOAL.EXE memory (the match clock DS:831F/831D/8325/831B, the seed DS:7B62, the score DS:9B3C/9B3D, the commentary ring) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "savestates written at every read; two loaded (Host+L): the start state, then none further (the match runs watched from the captain screen)"}]
        outputs = []
        if self.watchstart_blob is not None:
            name = f"{self.run_id}-watchstart.sav"
            OUTPUTS.mkdir(parents=True, exist_ok=True)
            (OUTPUTS / name).write_bytes(self.watchstart_blob)
            outputs.append({"name": name, "sha256": driver.sha256(self.watchstart_blob), "store": "release:E011"})
        if self.halftime_blob is not None:
            name = f"{self.run_id}-halftime.sav"
            OUTPUTS.mkdir(parents=True, exist_ok=True)
            (OUTPUTS / name).write_bytes(self.halftime_blob)
            outputs.append({"name": name, "sha256": driver.sha256(self.halftime_blob), "store": "release:E011"})
        start = {"id": self.st.name, "sha256": self.st.sha256,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, GOAL run to its title screen; "
                             f"key n to change the screen; then Host+L loads E006's published main-screen savestate whose sha256 is given ({self.st.name}.sav, release E006); "
                             f"polled until the screen digest equals the one stored with it ({self.st.screen_digest}); DOS clock of this session not set")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": "watched", "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E011-q010-watched-engine/run.py", "sha256": SCRIPT_SHA, "args": list(self.args.argv) + ["arm watched"]},
            "observations": obs, "outputs": outputs,
            "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
            "ended": driver.host_times()["utc"], "status": status,
        }
        text = json.dumps(record, indent=1, ensure_ascii=False) + "\n"
        if str(ROOT) in text:
            raise SystemExit(f"{self.run_id}: a host path leaked into the record")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / f"{self.run_id}.json", "x", encoding="utf-8") as f:  # never overwrite (L207)
            f.write(text)
        print(f"{self.run_id} {self.st.name} watched: {status}")
        return status == "completed", self.trajectory

def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    w = sub.add_parser("watched", help="one watched match, one record")
    w.add_argument("--from-run", required=True, dest="from_run", help="the E006 run id whose manifest names the main-screen start state (E007's run.py adopt)")
    w.add_argument("--batch", default="", help="a label written into the record")
    w.add_argument("--replays", type=int, default=1,
                   help="extra identical launches after the first; each writes its own record and must repeat the first's trajectory exactly (determinism, E004's replays)")
    return ap


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    a = parser().parse_args(argv)
    a.argv = argv
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    base = None
    for i in range(1 + a.replays):
        ok, traj = Run(next_id(), a, commit).go()
        if not ok:
            return 1
        if base is None:
            base = traj
        elif traj != base:
            print(f"replay differs from the first run's trajectory ({len(traj)} against {len(base)} reads)")
            return 1
        else:
            print("replay: trajectory identical to the first run's (deterministic)")
    return 0


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


if __name__ == "__main__":
    sys.exit(main())
