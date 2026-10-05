#!/usr/bin/env python3
"""E006 (T15, Q004): new games at fixed DOS times, read at the main screen: the whole player array at
the far pointer DS:A91B and the country array at DS:A917. One run/1 record per new game.

    python3 experiments/E006-q004-skills/run.py games --times 10:00,10:01 --batch b1

Per DOS time: a fresh launch with the DOS date and time set (I3), F001's keys to the main screen
(`n Enter Enter b o b Enter Enter Enter Enter`, each followed by a settle poll), Host+S. The savestate
is kept as `.cache/states/driver/e006-HHMM-r<nnnn>.sav` (git-ignored; with its .json, as a start state
of E004's form) and named by sha256 in the record's `outputs`; `tools/publish_evidence.py E006`
publishes it. The arrays go into the record as hex (runtime/driver/players.py), after `players.check`
has placed them. A record is written only when runtime/driver/ and this folder have no uncommitted
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
import cycle  # noqa: E402
import driver  # noqa: E402
import players  # noqa: E402
import savestate  # noqa: E402

_spec = importlib.util.spec_from_file_location("e003", ROOT / "experiments" / "E003-q001-inputs" / "run.py")
e003 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e003)

EXPERIMENT = "E006"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2)
# E004's fixed cycles (F001 M:match-speed's fastest fixed setting); no match is played here, the value
# only keeps the runtime equal to E004's. [designed]
CYCLES = "30000"
TO_MAIN = e003.TO_MAIN
DEFAULT_DATE = e003.DEFAULT_DATE
STORE = f"release:{EXPERIMENT}"


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def state_name(dos_time, run_id):
    return f"e006-{dos_time.replace(':', '')[:4]}-{run_id.split('-')[1]}"


def array_observations(step, state):
    obs = []
    for label, ptr, size, read in (("player array", players.PLAYERS_PTR, players.PLAYERS_BYTES, players.players),
                                   ("country array", players.COUNTRIES_PTR, players.COUNTRIES_BYTES, players.countries)):
        seg, off, lin = players.far_pointer(state, ptr)
        obs.append({"step": step, "source": "memory", "addr": f"0x{state.program().ds_base + ptr:x}",
                    "field": f"far pointer at DS:{ptr:04X} (offset word, segment word): segment:offset and linear address",
                    "value": f"{seg:04X}:{off:04X} 0x{lin:05x}"})
        obs.append({"step": step, "source": "memory", "addr": f"0x{lin:x}",
                    "field": f"{label}: 0x{size:X} bytes at [DS:{ptr:04X}], hex, guest memory from the savestate",
                    "value": read(state).hex()})
    problems = players.check(players.players(state), players.countries(state))
    obs.append({"step": step, "source": "memory", "field": "players.check: lengths, squad words of countries 1..128, byte 0 of their players",
                "value": "ok" if not problems else "; ".join(problems)})
    return obs


class Game:
    def __init__(self, n, dos_time, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.dos_time, self.dos_date, self.args, self.commit = dos_time, args.dos_date, args, commit
        self.d = driver.Driver({"cycles": CYCLES, "dos_time": dos_time, "dos_date": self.dos_date},
                               workdir=driver.SCRATCH / "e006" / self.run_id)
        self.obs, self.step, self.outputs, self.clock_error = [], 0, [], None

    def add_read(self, label, read):
        times, state = read
        self.obs.extend(cycle.read_observations(self.step, label, times, state) + e003.seed_observations(self.step, label, state))

    def go(self):
        status = "completed"
        try:
            sc = self.d.launch(None)
            self.add_read("title (fresh launch)", self.d.last)
            self.obs.extend(e003.program_observations(self.step, self.d.last[1]))
            for k in TO_MAIN:
                self.step += 1
                prev = sc.digest()
                self.d.keys(k)
                sc = self.d.settle(prev, what=f"after key {k}")
            self.step += 1
            data = self.d.save_state()
            st = savestate.Savestate(data)
            if st.screen().digest() != sc.digest():
                raise RuntimeError("the main-screen savestate's screen differs from the settled screen")
            self.add_read("main screen (after key 10)", (driver.host_times(), st))
            self.obs.extend(array_observations(self.step, st))
            self.keep(data, st, sc)
        except Exception as e:  # noqa: BLE001
            if isinstance(e, driver.ClockNotApplied):
                self.clock_error = str(e)
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
        finally:
            gone = self.d.terminate()
        return self.record(status, gone)

    def keep(self, data, st, sc):
        name = state_name(self.dos_time, self.run_id)
        states = driver.STATES
        states.mkdir(parents=True, exist_ok=True)
        with open(states / f"{name}.sav", "xb") as f:  # never replaced
            f.write(data)
        d = self.d
        meta = {"sha256": driver.sha256(data), "screen_digest": sc.digest(), "game_dir": str(d.game_dir),
                "drive_layout": d.drive_layout(), "config": d.config, "clock_applied": d.clock_applied,
                "made": driver.host_times(), "keys": TO_MAIN, "ticks": st.ticks()[0], "run_id": self.run_id,
                "screen": sc.text(), "events": d.events}
        (states / f"{name}.json").write_text(json.dumps(meta, indent=1))
        self.outputs.append({"name": f"{name}.sav", "sha256": meta["sha256"], "store": STORE})
        print(f"{name}.sav sha256 {meta['sha256']}")

    def record(self, status, gone):
        d = self.d
        head = []
        if d.launched:
            head = [{"step": 0, "source": "log", "field": "host UTC time at launch", "value": d.launched["utc"]},
                    {"step": 0, "source": "log", "field": "host local time at launch, with UTC offset, and zone name",
                     "value": f"{d.launched['local']} {d.launched['tz']}"}]
        conf_text, conf_sha = d.conf_public() if getattr(d, "conf", None) else ("not written", "0" * 64)
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
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        back = (d.clock_applied or "").split()
        if self.clock_error is None and d.clock_applied is not None and len(back) >= 2:
            applied = f"applied: DOS reported date {back[0]} and time {back[1]} right after (`date /t`, `time /t`), checked by Driver.launch"
        else:
            applied = f"NOT verified as applied: {self.clock_error or 'no read-back'}"
        inter = [{"level": "I1", "what": "text screen, BIOS data area (0040:0049, 0040:006C) and GOAL.EXE memory (DS:7B62, DS:7B64, DS:8336, DS:A9FD, two known strings, the far pointers DS:A917 and DS:A91B and the arrays they point to) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "a savestate is written at the title and at the main screen (vocabulary/interventions.md lists save of state as I2)"},
                 {"level": "I3", "what": f"DOS date {self.dos_date} and DOS time {self.dos_time} requested with the DOSBox-X commands "
                  f"`date {self.dos_date}` and `time {self.dos_time}` in the autoexec, before GOAL runs; {applied}"}]
        start = {"id": "fresh-launch", "sha256": conf_sha,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, nothing "
                             f"restored; DOS time set to {self.dos_time} on {self.dos_date} before GOAL ran; then the keys {' '.join(TO_MAIN)}, "
                             f"each followed by a settle poll, to the main screen of a new game")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT,
            "arm": "new-game-" + self.dos_time.replace(":", ""), "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E006-q004-skills/run.py", "sha256": SCRIPT_SHA,
                        "args": record_args(self.args.argv)},
            "observations": obs, "outputs": self.outputs,
            "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
            "ended": driver.host_times()["utc"], "status": status,
        }
        text = json.dumps(record, indent=1, ensure_ascii=False) + "\n"
        if str(ROOT) in text:
            raise SystemExit(f"{self.run_id}: a host path leaked into the record")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / f"{self.run_id}.json", "x", encoding="utf-8") as f:  # never overwrite (L207)
            f.write(text)
        print(f"{self.run_id} {self.dos_time}: {status}")
        return status == "completed"


def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=["games"])
    ap.add_argument("--times", required=True, help="HH:MM[,HH:MM...]: one new game per entry, in order (an entry may repeat)")
    ap.add_argument("--dos-date", default=DEFAULT_DATE, help="MM/DD/YYYY, set with the DOS time")
    ap.add_argument("--batch", default="", help="a label written into each record")
    return ap


def record_args(argv):
    """The record's actions.args: the argv this process ran, as given (E006 README amendment 1), so
    that parser() accepts it and replays the invocation."""
    return list(argv)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    a = parser().parse_args(argv)
    a.argv = argv
    times = [t + ":00" for t in a.times.split(",")]
    for t in times:
        driver.clock_values(a.dos_date, t)
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok = 0
    for t in times:
        ok += Game(next_id(), t, a, commit).go()
    print(f"{ok} of {len(times)} runs completed")
    return 0 if ok == len(times) else 1


if __name__ == "__main__":
    sys.exit(main())
