#!/usr/bin/env python3
"""E007 (T16, Q009): the player screen of every player of one country's squad, read from a savestate
taken at each screen, with the player's own record read from the same savestate. One run/1 record per
country.

    python3 experiments/E007-q009-player-screen/run.py adopt --from E006-r0001
    python3 experiments/E007-q009-player-screen/run.py countries --state e006-1000-r0001 --list-positions 0,1,2 --batch b1

- adopt: fetch the main-screen savestate of an E006 record from release E006 (the asset the record's
  evidence manifest names), check its sha256 against the manifest, and store it under
  `.cache/states/driver/` with the metadata a start state needs (screen digest, drive layout). The
  state is E006's, not a new one: player values are the same in every new game (F007).
- countries: per position in the main screen's country list (0 = the managed country, Denmark; each
  step is one Down), a fresh launch, the state restored (Host+L), Down that many times, Space (the
  country's player list, and with it the first player's screen), then Down per player; a savestate
  (Host+S) at every player screen. Each read keeps the screen (text and the 4000 raw bytes with the
  attributes the bars are painted in), the host clock, and the 20-byte record of the player the screen
  names, found by the name `1771:2E93` builds (runtime/driver/players.py).
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
import playerscreen  # noqa: E402
import players  # noqa: E402
import savestate  # noqa: E402

EXPERIMENT = "E007"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2)
# E006's value (and E004's): no match is played here, the value only keeps the runtime equal. [designed]
CYCLES = "30000"
PLAYERS_PER_COUNTRY = 20     # a country's list shows its squad: 20 players (the boxes of the screens in E007's first exploratory reads, not a record)
# Data-segment ranges kept in every record, so the analysis needs no file of the original: the tables the
# routines of F008 index. Each range is named by the listing line that reads it.
TABLES = [
    (0x0E40, 0x0E90, "heights and feet (1771:2FAD at DS:0E46, DS:0E54; 1771:3088 at DS:0E60, DS:0E7C; DS:0E86)"),
    (0x0F20, 0x0F80, "the foot strings (1771:42BC: DS:0F2C + 6 * k)"),
    (0x6990, 0x6AC0, "position names (1771:42BC: DS:69B6 + 0x13 * position; DS:699A, DS:69A8)"),
    (0x6D20, 0x6E90, "the skill tables (1771:3947: DS:6D25 and DS:6DCD)"),
    (0x6EB4, 0x7940, "the words (1771:42BC: DS:6EB4 + 16 * i) and the word indexes (DS:78A3, DS:78C4, DS:78D5, DS:78F6, DS:7917)"),
]
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


def candidates(surnames, initials, name):
    """The players (1..3060) whose name, as 1771:2E93 builds it, is `name`."""
    return [n for n in range(1, players.N_PLAYERS) if players.full_name(surnames, initials, n) == name]


def player_observations(step, label, state, shown, surnames, initials):
    """The player the screen shows and its 20 bytes, from the savestate the screen was read from."""
    cand = candidates(surnames, initials, shown["name"])
    arr = players.players(state)
    cand_age = [n for n in cand if players.record(arr, players.PLAYER_SIZE, n)[1] == shown["age"]]
    n = cand_age[0] if len(cand_age) == 1 else None
    seg, off, lin = players.far_pointer(state, players.PLAYERS_PTR)
    obs = [{"step": step, "source": "memory",
            "field": f"{label}: the player the screen names: players whose name 1771:2E93 builds ([DS:9B70] + n, a space, 11 bytes at [DS:9B6C] + 11 n) is the shown name, "
                     f"narrowed by the shown age against byte +1 of their record",
            "value": f"n={n if n is not None else 'unresolved'} named={cand} named_and_aged={cand_age}"}]
    if n is not None:
        obs.append({"step": step, "source": "memory", "addr": f"0x{lin + players.PLAYER_SIZE * n:x}",
                    "field": f"{label}: the 20 bytes of player n's record at [DS:A91B] + 0x14 n, hex, guest memory from the same savestate",
                    "value": players.record(arr, players.PLAYER_SIZE, n).hex()})
    return obs


def table_observations(step, state):
    base = state.program().ds_base
    return [{"step": step, "source": "memory", "addr": f"0x{base + lo:x}",
             "field": f"DS:{lo:04X}..{hi - 1:04X}, {hi - lo} bytes, hex, guest memory from the savestate: {what}",
             "value": state.ds_bytes(lo, hi - lo).hex()} for lo, hi, what in TABLES]


class Session:
    def __init__(self, n, position, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.position, self.args, self.commit = position, args, commit
        self.st = driver.StartState(args.state)
        self.d = driver.Driver(self.st.config, workdir=driver.SCRATCH / "e007" / self.run_id)
        self.obs, self.step, self.keys = [], 0, []

    def press(self, key):
        self.step += 1
        prev = self.d.screen().digest()
        self.d.keys(key)
        sc = self.d.settle(prev, what=f"after key {key}")
        self.keys.append(key)
        return sc

    def go(self):
        status, d = "completed", self.d
        try:
            sc = d.launch(self.st)
            times, state = d.last
            self.obs.extend(cycle.read_observations(self.step, "start state restored (main screen)", times, state))
            for _ in range(self.position):
                sc = self.press("Down")
            self.step += 1
            self.obs.append({"step": self.step, "source": "ui-text", "field": f"main screen after {self.position} Down: the team panel of the selected country",
                             "value": sc.text()})
            sc = self.press("Space")
            for j in range(PLAYERS_PER_COUNTRY):
                if j:
                    sc = self.press("Down")
                self.read_player(j)
        except Exception as e:  # noqa: BLE001
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
        finally:
            gone = d.terminate()
        return self.record(status, gone)

    def read_player(self, j):
        d = self.d
        times, state, _ = d.read()
        self.step += 1
        label = f"player screen {j + 1} of the list"
        sc = state.screen()
        self.obs.extend(cycle.read_observations(self.step, label, times, state))
        self.obs.append({"step": self.step, "source": "memory", "field": f"{label}: text screen 80x25 as the 4000 bytes B800:0000 holds them (character, attribute, ...), hex",
                         "value": sc.raw().hex()})
        if j == 0:
            self.surnames, self.initials = players.surnames(state), players.initials(state)
            self.obs.extend(table_observations(self.step, state))
        try:
            shown = playerscreen.parse(sc)
        except ValueError as e:
            raise RuntimeError(f"{label} is not a readable player screen: {e}") from None
        self.obs.extend(player_observations(self.step, label, state, shown, self.surnames, self.initials))

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
        inter = [{"level": "I1", "what": "text screen (characters and attributes), BIOS data area and GOAL.EXE data-segment memory (the player array at [DS:A91B], the names at [DS:9B6C] and [DS:9B70], the tables of the player screen's routines) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "a savestate is written at every player screen and one is loaded (Host+L) at the start (vocabulary/interventions.md lists save and load of state as I2)"}]
        start = {"id": self.st.name, "sha256": self.st.sha256,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, GOAL run to its title screen; "
                             f"key n to change the screen; then Host+L loads the savestate whose sha256 is given (E006's main-screen state of a new game made at DOS time 10:00 on "
                             f"10/04/2026, release E006, {self.st.name}.sav; screen digest {self.st.screen_digest}); polled until the screen digest equals the one stored with it; "
                             f"DOS clock of this session not set (the restore brings the state's own BIOS ticks, F004)")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT,
            "arm": f"country-list-position-{self.position}", "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E007-q009-player-screen/run.py", "sha256": SCRIPT_SHA, "args": list(self.args.argv)},
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
        print(f"{self.run_id} list position {self.position}: {status}")
        return status == "completed"


def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    a = sub.add_parser("adopt", help="store an E006 published main-screen savestate as a start state")
    a.add_argument("--from", dest="src", required=True, help="the E006 run id whose manifest names the state")
    c = sub.add_parser("countries", help="one record per country-list position")
    c.add_argument("--state", required=True, help="the start state's name (from `adopt`)")
    c.add_argument("--list-positions", required=True, help="0,1,2: positions in the main screen's country list, one record each")
    c.add_argument("--batch", default="", help="a label written into each record")
    return ap


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    a = parser().parse_args(argv)
    a.argv = argv
    if a.kind == "adopt":
        adopt(a.src)
        return 0
    positions = [int(x) for x in a.list_positions.split(",")]
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok = 0
    for p in positions:
        ok += Session(next_id(), p, a, commit).go()
    print(f"{ok} of {len(positions)} runs completed")
    return 0 if ok == len(positions) else 1


if __name__ == "__main__":
    sys.exit(main())
