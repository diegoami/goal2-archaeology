#!/usr/bin/env python3
"""E009 (T22, Q007): the managed country's pool screen, read from the E006 main-screen start state,
with the pool index array DS:A927 and the per-manager base table DS:6D18 read from the same savestate.

    python3 experiments/E009-q007-squad-pool/run.py adopt --from E006-r0001
    python3 experiments/E009-q007-squad-pool/run.py pool --state e006-1000-r0001 --batch b1

- adopt: fetch the main-screen savestate of an E006 record from release E006 (the asset the record's
  evidence manifest names), check its sha256 against the manifest, and store it under
  .cache/states/driver/ (the same start state E007 adopts; player values are the same in every new
  game, F007).
- pool: one fresh launch, the state restored (Host+L), then the keys that reach the two screens the
  question is about: Esc (the main menu, where "select squad" is an item), Space (the SELECT TEAM
  screen in its squad view), Left (toggle to the pool view). Each screen is read; the pool index
  array DS:A927, the per-manager base table DS:6D18, the name arrays and the 80 pool records are
  read from the same savestate the first screen is read from. One record per run.

A record is written only when runtime/driver/ and this folder have no uncommitted change, and never
over an existing one (L207)."""
import argparse
import json
import platform
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import cycle  # noqa: E402
import driver  # noqa: E402
import players  # noqa: E402
import savestate  # noqa: E402

EXPERIMENT = "E009"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())
CYCLES = "30000"  # E006's and E007's value; no match is played, it only keeps the runtime equal. [designed]

POOL_PTR = 0xA927     # DS offset of the far pointer to the pool index array (word[481], 0x3C2 bytes)
POOL_BASE = 0x6D18    # DS offset of the per-manager pool base table (word[7]: manager m at +2m)
POOL_FIRST = 0xA00    # the pool player record numbers are POOL_FIRST + index (make_pool_player, F007)
N_POOL = 80           # players make_managed_pool makes per manager (F007)

STATE_CONFIG = {"cycles": CYCLES}


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def manifest_of(run_id):
    path = ROOT / "evidence" / run_id.split("-")[0] / f"{run_id}.manifest.json"
    m = json.loads(path.read_text())
    entries = [e for e in m["files"] if e["name"].endswith(".sav")]
    if len(entries) != 1:
        raise SystemExit(f"{path}: expected one .sav, found {len(entries)}")
    return m, entries[0]


def adopt(run_id):
    """Store E006's published main-screen state as a start state of this driver; returns its name."""
    m, e = manifest_of(run_id)
    name = e["name"][:-4]
    states = driver.STATES
    sav = states / f"{name}.sav"
    if sav.exists():
        if driver.sha256(sav.read_bytes()) != e["sha256"]:
            raise SystemExit(f"{sav} does not match the manifest's sha256 {e['sha256']}")
        print(f"{name}: already stored, sha256 matches the manifest")
        return name
    dl = ROOT / ".cache" / "dl"
    dl.mkdir(parents=True, exist_ok=True)
    asset = dl / e["asset"]
    if not asset.exists():
        subprocess.run(["gh", "release", "download", m["store"].split(":")[1], "--repo", "diegoami/goal2-archaeology",
                        "--pattern", e["asset"], "--dir", str(dl)], check=True)
    data = asset.read_bytes()
    if driver.sha256(data) != e["sha256"]:
        raise SystemExit(f"{asset}: sha256 {driver.sha256(data)}, the manifest says {e['sha256']}")
    d = driver.Driver(STATE_CONFIG, workdir=driver.SCRATCH / f"adopt-{name}")
    sc = savestate.Savestate(data).screen()
    states.mkdir(parents=True, exist_ok=True)
    with open(sav, "xb") as f:
        f.write(data)
    meta = {"sha256": e["sha256"], "screen_digest": sc.digest(), "game_dir": str(d.game_dir), "drive_layout": d.drive_layout(),
            "config": STATE_CONFIG, "made": driver.host_times(), "adopted_from": f"{m['store']} {e['asset']}", "run_id": run_id,
            "screen": sc.text()}
    (states / f"{name}.json").write_text(json.dumps(meta, indent=1))
    print(f"{name}: stored from {m['store']}, sha256 {e['sha256']}")
    return name


def pool_words(state):
    """The 0x3C2 bytes of the pool index array, as the 481 16-bit words they hold."""
    seg, off, lin = players.far_pointer(state, POOL_PTR)
    raw = state.memory(lin, 0x3C2)
    return [int.from_bytes(raw[2 * i:2 * i + 2], "little") for i in range(0x3C2 // 2)]


def pool_observations(step, label, state, surnames, initials):
    """The pool index array, the base table, and the 80 pool records, from one savestate."""
    words = pool_words(state)
    obs = [
        {"step": step, "source": "memory", "addr": "0x" + f"{players.far_pointer(state, POOL_PTR)[2]:x}",
         "field": f"{label}: DS:A927 (the pool index array, word[481]) as decimal words 0..480, guest memory from the savestate",
         "value": json.dumps(words)},
        {"step": step, "source": "memory", "addr": f"0x{state.ds_bytes(POOL_BASE, 1) and state.program().ds_base + POOL_BASE:x}",
         "field": f"{label}: DS:6D18..6D27 (the per-manager pool base table, 8 words) hex, guest memory from the savestate",
         "value": state.ds_bytes(POOL_BASE, 16).hex()},
    ]
    arr = players.players(state)
    for n in range(POOL_FIRST + 1, POOL_FIRST + N_POOL + 1):
        obs.append({"step": step, "source": "memory", "addr": f"0x{players.far_pointer(state, players.PLAYERS_PTR)[2] + players.PLAYER_SIZE * n:x}",
                    "field": f"{label}: the 20 bytes of player record {n} at [DS:A91B] + 0x14 n, hex, guest memory from the same savestate",
                    "value": players.record(arr, players.PLAYER_SIZE, n).hex()})
    for n in (POOL_FIRST + N_POOL + 1, POOL_FIRST + N_POOL + 2):
        obs.append({"step": step, "source": "memory", "addr": f"0x{players.far_pointer(state, players.PLAYERS_PTR)[2] + players.PLAYER_SIZE * n:x}",
                    "field": f"{label}: the 20 bytes of player record {n} (just past the pool), hex, guest memory from the same savestate",
                    "value": players.record(arr, players.PLAYER_SIZE, n).hex()})
    # the name arrays, so the names on the screens can be matched to records without the original file
    obs.append({"step": step, "source": "memory", "addr": f"0x{players.far_pointer(state, players.NAMES_PTR)[2]:x}",
                "field": f"{label}: the 0x8387 bytes of surnames at [DS:9B6C], hex, guest memory from the same savestate",
                "value": surnames.hex()})
    obs.append({"step": step, "source": "memory", "addr": f"0x{players.far_pointer(state, players.INITIALS_PTR)[2]:x}",
                "field": f"{label}: the 0xBF5 bytes of initials at [DS:9B70], hex, guest memory from the same savestate",
                "value": initials.hex()})
    return obs


def screen_observations(step, label, state):
    sc = state.screen()
    return [{"step": step, "source": "ui-text", "field": f"{label}: text screen rows 0-24, CP437 decoded, trailing blanks trimmed",
             "value": sc.text()},
            {"step": step, "source": "screen", "field": f"{label}: text screen 80x25, chars+attributes (4000 bytes), sha256",
             "value": sc.digest()}]


class Session:
    def __init__(self, n, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.args, self.commit = args, commit
        self.st = driver.StartState(args.state)
        self.d = driver.Driver(STATE_CONFIG, workdir=driver.SCRATCH / "e009" / self.run_id)
        self.obs, self.step, self.keys = [], 0, []

    def press(self, key):
        self.step += 1
        prev = self.d.screen().digest()
        self.d.keys(key)
        sc = self.d.settle(prev, what=f"after key {key}")
        self.keys.append(key)
        return sc

    def read(self, label):
        times, state, _ = self.d.read()
        self.step += 1
        self.obs.extend(cycle.read_observations(self.step, label, times, state))
        return state

    def go(self):
        status, d = "completed", self.d
        try:
            sc = d.launch(self.st)
            times, state = d.last
            self.obs.extend(cycle.read_observations(self.step, "start state restored (the country-list screen)", times, state))
            self.surnames, self.initials = players.surnames(state), players.initials(state)
            self.obs.extend(pool_observations(self.step, "start state restored (the country-list screen)", state,
                                              self.surnames, self.initials))
            sc = self.press("Esc")          # the main menu (000E:7439), where "select squad" is an item
            self.obs.extend(screen_observations(self.step, "main menu after Esc", d.last[1]))
            sc = self.press("Space")        # the SELECT TEAM screen (0791:E44F) in its squad view
            self.obs.extend(screen_observations(self.step, "SELECT TEAM, squad view after Space", d.last[1]))
            sc = self.press("Left")         # toggle to the pool view (0791:E2E6)
            self.obs.extend(screen_observations(self.step, "SELECT TEAM, pool view after Left", d.last[1]))
        except Exception as e:  # noqa: BLE001
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
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
            {"step": 0, "source": "log", "field": "keys sent after the restore, in order", "value": " ".join(self.keys)},
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [{"level": "I1", "what": "text screen and GOAL.EXE data-segment memory (the pool index array at [DS:A927], the base table DS:6D18, the player array at [DS:A91B], the name arrays at [DS:9B6C] and [DS:9B70]) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "a savestate is written at each read, and one is loaded (Host+L) at the start (vocabulary/interventions.md lists save and load of state as I2)"}]
        start = {"id": self.st.name, "sha256": self.st.sha256,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, GOAL run to its title screen; "
                             f"key n to change the screen; then Host+L loads the savestate whose sha256 is given (E006's main-screen state of a new game made at DOS time 10:00 on "
                             f"10/04/2026, release E006, {self.st.name}.sav; screen digest {self.st.screen_digest}); polled until the screen digest equals the one stored with it; "
                             f"DOS clock of this session not set (the restore brings the state's own BIOS ticks, F004)")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT,
            "arm": "pool-screen", "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E009-q007-squad-pool/run.py", "sha256": SCRIPT_SHA, "args": list(self.args.argv)},
            "observations": obs, "outputs": [],
            "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
            "ended": driver.host_times()["utc"], "status": status,
        }
        text = json.dumps(record, indent=1, ensure_ascii=False) + "\n"
        if str(ROOT) in text:
            raise SystemExit(f"{self.run_id}: a host path leaked into the record")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / f"{self.run_id}.json", "x", encoding="utf-8") as f:  # never overwrite (L207)
            f.write(text)
        print(f"{self.run_id}: {status}")
        return status == "completed"


def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    a = sub.add_parser("adopt", help="store an E006 published main-screen savestate as a start state")
    a.add_argument("--from", dest="src", required=True, help="the E006 run id whose manifest names the state")
    c = sub.add_parser("pool", help="one record: the managed country's pool screen")
    c.add_argument("--state", required=True, help="the start state's name (from `adopt`)")
    c.add_argument("--batch", default="", help="a label written into each record")
    return ap


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    a = parser().parse_args(argv)
    a.argv = argv
    if a.kind == "adopt":
        adopt(a.src)
        return 0
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok = Session(next_id(), a, commit).go()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
