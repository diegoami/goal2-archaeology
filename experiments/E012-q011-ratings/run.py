#!/usr/bin/env python3
"""E012 (T26, Q011): the performance ratings of a watched match, read from the game itself.

    python3 experiments/E012-q011-ratings/run.py watched --from-run E006-r0001 --batch b1 --replays 1

A watched match from an E010 release start state (E010's runs start from E006's published
main-screen states; `--from-run` names the E006 run) under E004's conditions: E007's `adopt`
(Host+L of the published state), E004's keys to the captain screen, then E004's watched arm
(the starting burst `Enter Right Right Right Right Right`, one Enter only on a stopped-clock
screen that asks for one — half time and the team screen). Per run: a fresh launch, one record.
The record carries the ground truth the predictor (`runtime/model/ratings.py`) is checked
against (`check_ratings.py`):
- the two sides' country numbers (DS:9B34 word per side) and their 20 squad words in slot order,
  read at the captain screen (the match's start) — the squad words are the player numbers the
  commentary ring's records name, and their order is the scan order of CAB0's man of the match;
- every squad slot's +0x12 word both sides, read at the half-time team-screen stall and at full
  time (the summary screen; `MAN OF THE MATCH` is on it), with the MoM word DS:7C3A and the
  watched gate DS:9A3F;
- the full commentary line log in ring order — [n, template, p1, p2, team] per line — and the
  number of lines seen at the half-time read (the first half's extent).
A run whose commentary had a gap (Tracker) is aborted: its line log could not corroborate
anything. A record is written only when runtime/driver/ and this folder have no uncommitted
change, and never over an existing one (L207)."""
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


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e004 = _load("e004_run", "experiments/E004-q002-quick-result/run.py")
e007 = _load("e007_run", "experiments/E007-q009-player-screen/run.py")

EXPERIMENT = "E012"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2)
CYCLES = e004.CYCLES          # E004's and E006's value, so the start state's runtime is unchanged
STATE_CONFIG = {"cycles": CYCLES}
SIDES = 0x9B34                # DS offset of the two engine sides' country words (CAB0, seg_0791_20.asm:918)
MOM = 0x7C3A                  # DS offset of the man-of-the-match word CAB0 writes (CB4C)
WATCHED_GATE = 0x9A3F         # clear during a watched match: 0106 draws the MoM only then (E012 notes §5)


def squad_read(state):
    """Both sides' country number, 20 squad words in slot order, and every slot's +0x12 word —
    the ground-truth read the predictor is checked against (CAB0 scans the same order)."""
    ca, pa = players.countries(state), players.players(state)
    sides = []
    for side in (0, 1):
        c = state.ds_word(SIDES + 2 * side)
        sq = players.squad(ca, c)
        perf = [int.from_bytes(players.record(pa, players.PLAYER_SIZE, p)[0x12:0x14], "little")
                for p in sq]
        sides.append({"side": side, "country": c, "squad": sq, "perf12": perf})
    return sides


def clock_read(state):
    b = state.ds_bytes
    return (state.ds_word(0x831F), state.ds_word(0x831D), b(0x8325, 1)[0], state.ds_word(0x831B),
            state.ds_word(0x7B62), (b(0x9B3C, 1)[0], b(0x9B3D, 1)[0]), state.ds_word(commentary.COUNTER))


def stall(sc, state, prev_stable):
    """The half-time team screen: stable, clock stopped (8325 = 0), `location:` shown (0791:9A32's
    0791:ED8A wait, E011 notes.md §5); minute 45 or 46 (the second half's clock)."""
    if state.ds_bytes(0x8325, 1)[0] != 0 or not prev_stable:
        return None
    return "location:" in sc.text() and state.ds_word(0x831F) in (45, 46)


class Run:
    def __init__(self, n, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.args, self.commit = args, commit
        self.st = driver.StartState(e007.adopt(args.from_run))
        self.d = driver.Driver(STATE_CONFIG, workdir=driver.SCRATCH / "e012" / self.run_id)
        self.obs, self.step, self.keys, self.pre_keys = [], 0, [], list(e004.TO_CAPTAIN)
        self.reads, self.seconds, self.final = 0, None, None
        self.tracker = commentary.Tracker()
        self.prev_digest = None
        self.halftime_read = None       # the read number whose state is the half-time stall
        self.halftime = None            # squad_read of that state

    def obs_mem(self, field, value):
        self.obs.append({"step": self.step, "source": "memory", "field": field, "value": value})

    def on_read(self, label, times, state):
        self.step += 1
        self.reads += 1
        sc = state.screen()
        m, sub, running, left, seed, score, counter = clock_read(state)
        self.obs_mem(f"{label}: minute DS:831F, sub-tick DS:831D, clock running DS:8325, minutes left DS:831B, seed DS:7B62, score, commentary counter DS:80EE, screen sha256",
                     f"{m} {sub} {running} {left} 0x{seed:04x} {score[0]} {score[1]} {counter} {sc.digest()}")
        self.tracker.add(commentary.Snapshot(state), label)
        self.final = (times, state)
        stable = self.prev_digest == sc.digest()
        self.prev_digest = sc.digest()
        if self.halftime_read is None and stall(sc, state, stable):
            self.halftime_read = self.reads
            self.halftime = squad_read(state)
            self.obs_mem(f"{label}: half-time team-screen stall — both sides' country (DS:9B34 word per side), 20 squad words in slot order, and every slot's +0x12 word (the first half's ratings)",
                         json.dumps(self.halftime, separators=(",", ":")))
            self.obs_mem(f"{label}: commentary lines seen at the half-time stall (the first half's extent; the ring's counter DS:80EE = {counter})",
                         str(len(self.tracker.lines)))
            self.d.log(f"half-time team-screen stall at read {self.reads}: minute {m}, sub-tick {sub}, seed 0x{seed:04x}")

    def go(self):
        status, d = "completed", self.d
        try:
            sc = d.launch(self.st)
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
            _, state, _ = d.read()
            if state.ds_bytes(0x9A3E, 1)[0] != 0:
                raise RuntimeError("DS:9A3E set at the captain screen: the match would run quick")
            self.obs_mem("captain screen (the match's start): both sides' country (DS:9B34 word per side), 20 squad words in slot order, and every slot's +0x12 word (all 0x7FFF before F1F6)",
                         json.dumps(squad_read(state), separators=(",", ":")))
            _, self.reads, self.seconds = match.play(d, "watched", self.on_read, keys=self.keys)
            if self.halftime_read is None:
                raise RuntimeError("the half-time team-screen stall was never seen")
            if self.tracker.gaps:
                raise RuntimeError("commentary gap: " + "; ".join(self.tracker.gaps[:3]))
            self.step += 1
            _, fstate = self.final
            full = squad_read(fstate)
            mom = fstate.ds_word(MOM)
            self.obs_mem("full time (the summary screen): both sides' country, squad words in slot order, and every slot's +0x12 word (the full-time ratings)",
                         json.dumps(full, separators=(",", ":")))
            self.obs_mem("full time: man of the match DS:7C3A (CAB0's winner, the squad word) and the watched gate DS:9A3F",
                         f"0x{mom:04x} {fstate.ds_bytes(WATCHED_GATE, 1)[0]}")
            if not any("MAN OF THE MATCH" in row for row in fstate.screen().lines()):
                raise RuntimeError("the full-time screen is not the summary: no MAN OF THE MATCH row")
            self.obs_mem("events of the match (runtime/driver/commentary.py): [kind, team, text]",
                         json.dumps(self.tracker.events(), ensure_ascii=False))
            self.obs_mem("commentary line log in ring order: [n, template, p1, p2, team] per line, as 1D4A wrote them (the predictor's input)",
                         json.dumps([[x["n"], x["template"], x["p1"], x["p2"], x["team"]] for x in self.tracker.lines],
                                    separators=(",", ":")))
        except Exception as e:  # noqa: BLE001
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
            if d.last is not None:
                self.step += 1
                _, state = d.last
                self.obs_mem("last complete read before the abort: both sides' squad words and +0x12 words",
                             json.dumps(squad_read(state), separators=(",", ":")))
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
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [{"level": "I1", "what": "text screen, BIOS data area and GOAL.EXE memory (the match clock DS:831F/831D/8325/831B, the seed DS:7B62, the score DS:9B3C/9B3D, the commentary ring, the squad words and every squad player's +0x12 rating word, the man-of-the-match word DS:7C3A) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "savestates written at every read; one loaded (Host+L): the start state; the match runs watched from the captain screen"}]
        start = {"id": self.st.name, "sha256": self.st.sha256,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, GOAL run to its title screen; "
                             f"key n to change the screen; then Host+L loads E006's published main-screen savestate whose sha256 is given ({self.st.name}.sav, release E006; "
                             f"the start state of E010's runs from the same E006 run); polled until the screen digest equals the one stored with it ({self.st.screen_digest}); "
                             f"DOS clock of this session not set")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": "watched", "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E012-q011-ratings/run.py", "sha256": SCRIPT_SHA, "args": list(self.args.argv) + ["arm watched"]},
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
        print(f"{self.run_id} {self.st.name} watched: {status}")
        return status == "completed", OUT / f"{self.run_id}.json"


def ground_truth(record_path):
    """The deterministic identity of a watched match for the replay check: the half-time and
    full-time squad reads, the MoM word and the line log (the quantities E004's replays compared,
    plus this experiment's own reads). The mid-read clock samples are not part of it: their phase
    within a tick is host timing (E011 notes.md §6)."""
    d = json.loads(Path(record_path).read_text())

    def field(needle):
        return next((o["value"] for o in d["observations"] if needle in o.get("field", "")), None)

    return {"halftime": field("half-time team-screen stall"),
            "lines_at_halftime": field("commentary lines seen at the half-time stall"),
            "fulltime": field("full time (the summary screen)"),
            "mom": field("full time: man of the match"),
            "line_log": field("commentary line log in ring order")}


def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    w = sub.add_parser("watched", help="one watched match, one record")
    w.add_argument("--from-run", required=True, dest="from_run", help="the E006 run id whose manifest names the main-screen start state (an E010 start state; E007's run.py adopt)")
    w.add_argument("--batch", default="", help="a label written into the record")
    w.add_argument("--replays", type=int, default=1,
                   help="extra identical launches after the first; each writes its own record and must repeat the first's ground truth exactly (determinism, E004's replays)")
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
        ok, path = Run(next_id(), a, commit).go()
        if not ok:
            return 1
        truth = ground_truth(path)
        if base is None:
            base = truth
        elif truth != base:
            print("replay differs from the first run's ground truth (half-time and full-time reads, MoM, line log)")
            return 1
        else:
            print("replay: ground truth identical to the first run's (deterministic)")
    return 0


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


if __name__ == "__main__":
    sys.exit(main())
