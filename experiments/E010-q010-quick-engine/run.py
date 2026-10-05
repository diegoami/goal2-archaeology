#!/usr/bin/env python3
"""E010 (T23, Q010): a quick result captured at its half-time stall and at full time, to check the
quick-engine model (`runtime/model/quick_engine.py`) seed for seed. One run/1 record per run.

    python3 experiments/E010-q010-quick-engine/run.py quick --state e006-1000-r0001 --arms unchanged,edited --batch b0

Per run: a fresh launch; Host+L of an E006 published main-screen state; E004's keys to the captain
screen; a savestate there (Host+S). Then the arm's state is loaded with Host+L: `unchanged` the
captain-screen savestate as saved, `edited` the same savestate with the one byte at [DS:A917] +
0xBF * 7 + 0x2D (Denmark's +0x2D, R008) XOR 0x31 (E008's edit, F010's both tactic arms). The match
then runs as a quick result (Enter r). At the half-time stall — the stable screen with `hit any key`
while DS:9A3E = 1 and 831F = 46 (the game blocks in 0791:ED8A inside 0791:9A32; E010's notes batch 2:
the half-time screen is drawn BEFORE the wait and the wait consumes no RNG, so the state at the
stall is the model's exact input; the key that leaves it only sets DS:830B, which the model derives
itself) — the savestate just read is kept: it is this run's half-time state, published on release
E010 and named in the record's outputs. The match continues to full time; the record observes the
result screen, the score, the goal words and minutes the engine stored (DS:7BD1 + side*0x21 + n*3,
written by 0791:6443), the commentary events and the two seed words there. A record is written only
when runtime/driver/ and this folder have no uncommitted change, and never over an existing one."""
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
import players  # noqa: E402
import savestate  # noqa: E402


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e004 = _load("e004_run", "experiments/E004-q002-quick-result/run.py")
e008 = _load("e008_run", "experiments/E008-q005-r008-tactics/run.py")

EXPERIMENT = "E010"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
HALFTIME = ROOT / "scratch" / "e010-halftime"       # git-ignored; published to release E010
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2)
CYCLES = e004.CYCLES          # E004's and E006's value, so the start state's runtime is unchanged
STATE_CONFIG = {"cycles": CYCLES}
COUNTRY = e008.COUNTRY        # 7: Denmark, the managed country with F001's keys (F007)
FIELD = e008.FIELD            # 0x2D: R008's copy in the country record
EDIT_MASK = e008.EDIT_MASK    # 0x31: elements 1, 5, 6 of the tactics set
GOALS = 0x7BD1                # 6443's goal store: side*0x21 + n*3, player word + minute byte


def field_addr(state):
    return players.far_pointer(state, players.COUNTRIES_PTR)[2] + players.COUNTRY_SIZE * COUNTRY + FIELD


def seed_words(state):
    seg, off, lin = players.far_pointer(state, e008.SEED_PTR)
    w = int.from_bytes(state.memory(lin, 2), "little")
    return f"DS:7B62=0x{state.ds_word(0x7B62):04x} [DS:A978]={seg:04x}:{off:04x}=0x{w:04x}"


def goal_store(state):
    """The goals 0791:6443 stored: per engine team, [(player word, minute byte)]."""
    out = []
    for side in (0, 1):
        team = []
        for n in range(0x21 // 3):
            b = state.ds_bytes(GOALS + side * 0x21 + n * 3, 3)
            w = int.from_bytes(b[0:2], "little")
            if w == 0 and b[2] == 0:
                continue
            team.append([w, b[2]])
        out.append(team)
    return out


def stage(name, data, meta_from, states):
    """Store savestate bytes as a scratch start state (not a published one) and return it."""
    states.mkdir(parents=True, exist_ok=True)
    (states / f"{name}.sav").write_bytes(data)
    meta = dict(meta_from, sha256=driver.sha256(data))
    (states / f"{name}.json").write_text(json.dumps(meta, indent=1))
    return driver.StartState(name, states)


class Run:
    def __init__(self, n, arm, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.arm, self.args, self.commit = arm, args, commit
        self.st = driver.StartState(args.state)
        self.d = driver.Driver(STATE_CONFIG, workdir=driver.SCRATCH / "e010" / self.run_id)
        self.obs, self.step, self.keys, self.pre_keys = [], 0, [], list(e004.TO_CAPTAIN)
        self.reads, self.seconds, self.final = 0, None, None
        self.tracker = commentary.Tracker()
        self.halftime_blob, self.halftime_step, self.prev_digest = None, None, None

    def add_full(self, label, read):
        self.obs.extend(e004.full_observations(self.step, label, read[0], read[1]))
        self.obs.append({"step": self.step, "source": "memory", "field": f"{label}: seed words, GOAL.EXE data segment", "value": seed_words(read[1])})

    def on_read(self, label, times, state):
        self.step += 1
        self.reads += 1
        self.obs.extend(e004.match_observations(self.step, label, times, state))
        self.tracker.add(commentary.Snapshot(state), label)
        self.final = (times, state)
        sc = state.screen()
        stable = self.prev_digest == sc.digest()
        self.prev_digest = sc.digest()
        if (self.halftime_blob is None and stable
                and state.ds_bytes(0x9A3E, 1)[0] == 1
                and state.ds_word(0x831F) == 46
                and "hit any key" in sc.lines()[-1]):
            self.halftime_blob = self.d.last_blob
            self.halftime_step = self.step

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
            self.add_full("captain screen (the savestate both arms load)", (times, state))
            addr = field_addr(state)
            before = state.memory(addr, 1)[0]
            after = before ^ EDIT_MASK if self.arm == "edited" else before
            data = savestate.with_memory(cap, addr, bytes([after])) if self.arm == "edited" else cap
            self.obs.append({"step": self.step, "source": "memory", "addr": f"0x{addr:x}",
                             "field": f"edit: country {COUNTRY} byte +0x{FIELD:X} at [DS:A917] + 0xBF*{COUNTRY} + 0x{FIELD:X}, in the captain-screen savestate, then in the state this arm loads; sha256 of both savestates",
                             "value": f"0x{before:02x} -> 0x{after:02x}; captain {driver.sha256(cap)}; loaded {driver.sha256(data)}"})
            meta = {"screen_digest": sc.digest(), "game_dir": str(d.game_dir), "drive_layout": d.drive_layout(), "config": STATE_CONFIG}
            loaded = stage(f"{self.run_id}-{self.arm}", data, meta, driver.SCRATCH / "e010" / "states")
            self.step += 1
            d.restore(loaded)
            times, state, _ = d.read()
            self.add_full("after Host+L of the arm's state", (times, state))
            got = state.memory(field_addr(state), 1)[0]
            self.obs.append({"step": self.step, "source": "memory", "field": f"country {COUNTRY} byte +0x{FIELD:X} read back after the load",
                             "value": f"0x{got:02x}"})
            if got != after:
                raise RuntimeError(f"+0x{FIELD:X} reads 0x{got:02x} after the load, 0x{after:02x} was written")
            _, self.reads, self.seconds = match.play(d, "quick", self.on_read, keys=self.keys)
            if self.halftime_blob is None:
                raise RuntimeError("the half-time stall was never seen")
            self.step += 1
            self.add_full("full time", self.final)
            self.obs.append({"step": self.step, "source": "memory",
                             "field": "half-time stall: the read whose savestate is this run's half-time state (9A3E=1, 831F=46, stable screen, hit any key)",
                             "value": f"match read {self.halftime_step} of {self.reads}; DS:7B62=0x{self.final_halftime_seed:04x}"})
            self.obs.append({"step": self.step, "source": "memory",
                             "field": "goals the engine stored (0791:6443, DS:7BD1 + side*0x21 + n*3): [[player word, minute byte] per engine team]",
                             "value": json.dumps(goal_store(self.final[1]))})
        except Exception as e:  # noqa: BLE001
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
            if d.last is not None:
                self.step += 1
                self.add_full("last complete read before the abort", d.last)
        finally:
            gone = d.terminate()
        return self.record(status, gone)

    @property
    def final_halftime_seed(self):
        return int.from_bytes(savestate.Savestate(self.halftime_blob).ds_bytes(0x7B62, 2), "little") if self.halftime_blob else 0

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
        inter = [{"level": "I1", "what": "text screen, BIOS data area and GOAL.EXE memory (DS:7B62, the word at [DS:A978], the score DS:9B3C/9B3D, the commentary ring, the goal store DS:7BD1, the country array at [DS:A917]) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "savestates written at every read; two loaded (Host+L): the start state, then the captain-screen savestate of this run (vocabulary/interventions.md lists save and load of state as I2)"}]
        if self.arm == "edited":
            inter.append({"level": "I3", "what": f"one byte of guest memory edited: country {COUNTRY}'s +0x{FIELD:X} at [DS:A917] + 0xBF*{COUNTRY} + 0x{FIELD:X}, XOR 0x{EDIT_MASK:02X}, "
                                                 "written into the Memory component of the captain-screen savestate (runtime/driver/savestate.py with_memory) before it is loaded; no other byte changed"})
        outputs = []
        if self.halftime_blob is not None:
            name = f"{self.run_id}-halftime.sav"
            HALFTIME.mkdir(parents=True, exist_ok=True)
            (HALFTIME / name).write_bytes(self.halftime_blob)
            outputs.append({"name": name, "sha256": driver.sha256(self.halftime_blob), "store": "release:E010"})
        start = {"id": self.st.name, "sha256": self.st.sha256,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, GOAL run to its title screen; "
                             f"key n to change the screen; then Host+L loads E006's published main-screen savestate whose sha256 is given ({self.st.name}.sav, release E006); "
                             f"polled until the screen digest equals the one stored with it ({self.st.screen_digest}); DOS clock of this session not set")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": self.arm, "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E010-q010-quick-engine/run.py", "sha256": SCRIPT_SHA, "args": list(self.args.argv) + [f"arm {self.arm}"]},
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
        print(f"{self.run_id} {self.st.name} {self.arm}: {status}")
        return status == "completed"


def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


ARMS = ("unchanged", "edited")


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    q = sub.add_parser("quick", help="one record per arm, in the order given")
    q.add_argument("--state", required=True, help="an adopted E006 state (E007's run.py adopt)")
    q.add_argument("--arms", required=True, help="comma-separated, each unchanged or edited")
    q.add_argument("--batch", default="", help="a label written into each record")
    return ap


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    a = parser().parse_args(argv)
    a.argv = argv
    arms = a.arms.split(",")
    if any(x not in ARMS for x in arms):
        raise SystemExit(f"arms must be among {ARMS}")
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok = sum(Run(next_id(), arm, a, commit).go() for arm in arms)
    print(f"{ok} of {len(arms)} runs completed")
    return 0 if ok == len(arms) else 1


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


if __name__ == "__main__":
    sys.exit(main())
