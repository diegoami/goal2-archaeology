#!/usr/bin/env python3
"""E004 (T10, Q002): the same fixture played as a quick result and as a watched match, from one
seeded start state, with the score, the commentary events and DS:7B62 read at full time. One run/1
record per match.

    python3 experiments/E004-q002-quick-result/run.py make-state --dos-time 10:00:00 [--dos-date 10/04/2026]
    python3 experiments/E004-q002-quick-result/run.py pairs --state e004-1000 --pairs 5 --batch b1
    python3 experiments/E004-q002-quick-result/run.py sample --arm quick --minutes 10:00-11:39 --batch s1 [--slot 1]

- make-state: a fresh launch at the DOS time given (I3), F001's keys to the main screen (TO_MAIN), then
  `Esc Up Enter Enter` to the captain screen of the next match (`CAPTAIN` on its last row), Host+S;
  stored as `e004-HHMM` in .cache/states/driver/ (git-ignored) with its drive layout;
- pairs: restore a state (Host+L), then a quick result; restore it again, then a watched match; n times;
- sample: per DOS minute, a fresh launch at that minute (I3), the same keys to the captain screen, and
  one match of the arm (no savestate restored; `--slot` gives the session its own game folder, so two
  slots can run at once).
The match itself is runtime/driver/match.py (`play`); the commentary, score and speed are read from
every savestate by runtime/driver/commentary.py (I1). A record is written only when runtime/driver/
and this folder have no uncommitted change, and never over an existing one (L207)."""
import argparse
import importlib.util
import json
import platform
import re
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

_spec = importlib.util.spec_from_file_location("e003", ROOT / "experiments" / "E003-q001-inputs" / "run.py")
e003 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e003)

EXPERIMENT = "E004"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
IDS = driver.SCRATCH / "e004" / "ids"   # run-id reservations (mkdir is atomic), so two slots never share an id
# Fixed cycles: DOSBox-X then runs a set number of instructions per emulated millisecond, so the
# guest's own timing does not follow the host's speed (`max` adapts to the host); 30000 is F001
# M:match-speed's fastest fixed setting measured (a watched match, speed raised, kick-off to FULL TIME
# 20.27 and 20.35 s). Whether cycles change a match is Q003, not tested here. [designed]
CYCLES = "30000"
TO_MAIN = e003.TO_MAIN                       # F001's keys to the main screen (E003's `main`)
TO_CAPTAIN = ["Esc", "Up", "Enter", "Enter"]  # E003's d3b keys 1-4: main menu, next game, other results, captain screen
DEFAULT_DATE = e003.DEFAULT_DATE
DS_WORDS = e003.DS_WORDS                      # DS:7B62, 7B64, 8336, A9FD (F004)


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def state_name(dos_time):
    return "e004-" + dos_time.replace(":", "")[:4]


def remake_command(name):
    hhmm = name.split("-")[1]
    return f"python3 experiments/E004-q002-quick-result/run.py make-state --dos-time {hhmm[:2]}:{hhmm[2:]}:00 --dos-date {DEFAULT_DATE}"


def at_captain(sc):
    """The captain screen of the next match: `CAPTAIN` on its last row (E003-r0049, key 4)."""
    return "CAPTAIN" in sc.lines()[-1]


def team_screen(sc):
    """The team screen before a match (`location:`), reached instead of the captain screen at some
    DOS minutes; its default option is ` play `."""
    return "location:" in sc.text()


def extra_key(sc):
    """The one further key the pre-match path may need: Enter on the team screen (play), after which
    the captain screen must follow; None at the captain screen."""
    return "Enter" if team_screen(sc) and not at_captain(sc) else None


def match_observations(step, label, times, state):
    """A compact read during the match: host time, screen digest, the commentary rows, the counter,
    the score bytes and DS:7B62."""
    sc = state.screen()
    snap = commentary.Snapshot(state)
    return [{"step": step, "source": "log", "field": f"{label}: host UTC time just before the savestate was requested", "value": times["utc"]},
            {"step": step, "source": "screen", "field": f"{label}: text screen 80x25, chars+attributes, sha256", "value": sc.digest()},
            {"step": step, "source": "ui-text", "field": f"{label}: commentary rows (rows 1-3, columns 31-66)", "value": " / ".join(match.commentary_rows(sc))},
            {"step": step, "source": "memory", "field": f"{label}: words DS:80EE (commentary counter) and DS:7B62 (seed), bytes DS:9B3C, DS:9B3D (score), GOAL.EXE data segment",
             "value": f"0x{snap.counter:04x} 0x{state.ds_word(0x7B62):04x} {snap.score[0]} {snap.score[1]}"}]


def full_observations(step, label, times, state):
    obs = cycle.read_observations(step, label, times, state) + e003.seed_observations(step, label, state)
    snap = commentary.Snapshot(state)
    obs.append({"step": step, "source": "memory", "field": f"{label}: score bytes DS:9B3C, DS:9B3D (engine teams 0 and 1)", "value": f"{snap.score[0]} {snap.score[1]}"})
    obs.append({"step": step, "source": "memory", "field": f"{label}: match delay byte at the far pointer DS:A923 + 0x3F (0 fastest)", "value": str(snap.speed)})
    return obs


class Run:
    def __init__(self, kind, arm, n, args, commit, st=None, dos_time=None, slot=None):
        self.kind, self.arm, self.n, self.args, self.commit, self.st = kind, arm, n, args, commit, st
        self.dos_time, self.dos_date = dos_time, args.dos_date
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        cfg = {"cycles": CYCLES}
        if dos_time:
            cfg.update(dos_time=dos_time, dos_date=self.dos_date)
        game = driver.GAME_DIR if slot is None else driver.SCRATCH / f"e004-game-{slot}"
        self.d = driver.Driver(cfg, workdir=driver.SCRATCH / "e004" / self.run_id, game_dir=game)
        self.obs, self.step, self.located = [], 0, False
        self.tracker = commentary.Tracker()
        self.keys, self.reads, self.seconds = [], 0, None
        self.clock_error = None
        self.final = None
        self.pre_keys = list(TO_MAIN + TO_CAPTAIN)  # with the team screen's Enter where one is needed

    def add_full(self, label, read):
        times, state = read[0], read[1]
        self.obs.extend(full_observations(self.step, label, times, state))
        if not self.located:
            p = e003.program_observations(self.step, state)
            self.obs.extend(p)
            self.located = "not found" not in p[0]["value"]

    def on_read(self, label, times, state):
        self.step += 1
        self.obs.extend(match_observations(self.step, label, times, state))
        self.tracker.add(commentary.Snapshot(state), label)
        self.final = (times, state)

    def go(self):
        status = "completed"
        try:
            if self.kind == "pairs":
                self.d.launch(self.st, displace_key="n")
                self.add_full("before restore (title screen displaced by n)", self.d.pre_restore)
                sc = self.d.last[1].screen()
                self.add_full("restored", self.d.last)
            else:
                sc = self.d.launch(None)
                self.add_full("title (fresh launch)", self.d.last)
                keys = TO_MAIN + TO_CAPTAIN
                for i, k in enumerate(keys):
                    self.step += 1
                    self.d.keys(k)
                    sc = self.d.settle(sc.digest(), what=f"after key {k}")
                    if i == len(TO_MAIN) - 1:  # the main screen
                        self.add_full(f"after key {i + 1} ({k})", self.d.last)
                k = extra_key(sc)
                if k:
                    self.step += 1
                    self.pre_keys.append(k)
                    self.d.keys(k)
                    sc = self.d.settle(sc.digest(), what=f"after key {k} (team screen: play)")
                self.add_full("captain screen", self.d.last)
            if not at_captain(sc):
                raise RuntimeError("not at the captain screen before the match: " + sc.lines()[-1].strip())
            self.keys, self.reads, self.seconds = match.play(self.d, self.arm, self.on_read)
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
        events = self.tracker.events()
        last = self.step + 1
        tail = [
            {"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf_text},
            {"step": 0, "source": "file", "field": "sha256 of that config text (UTF-8)", "value": conf_sha},
            {"step": 0, "source": "log", "field": "batch label given on the command line", "value": self.args.batch},
            {"step": last, "source": "log", "field": "keys sent from the key that starts the match to full time: [seconds since the starting burst, key, why] (runtime/driver/match.py)",
             "value": json.dumps(self.keys)},
            {"step": last, "source": "log", "field": "match: savestate reads from the starting keys to full time, and seconds", "value": f"{self.reads} reads, {self.seconds} s"},
            {"step": last, "source": "memory", "field": "commentary lines of the match in order, accumulated over the reads from the ring DS:7C38 (runtime/driver/commentary.py): [n, template, team, text]",
             "value": json.dumps([[x["n"], x["template"], x["team"], x["text"]] for x in self.tracker.lines], ensure_ascii=False)},
            {"step": last, "source": "memory", "field": "events among them (templates " + ", ".join(f"{k} {v}" for k, v in commentary.EVENTS.items()) + "): [kind, team, text]",
             "value": json.dumps(events, ensure_ascii=False)},
            {"step": last, "source": "memory", "field": "commentary lines between successive reads (deltas of DS:80EE modulo 200), and reads where lines may have been lost",
             "value": json.dumps({"deltas": self.tracker.deltas, "gaps": self.tracker.gaps})},
            {"step": last, "source": "log", "field": "lines of DOSBox-X's own output (dosbox.out) that mention save, load, corrupt, date or time (Save_Remark and Time_Stamp lines left out), in order",
             "value": "\n".join(l for l in cycle.dosbox_out(d).splitlines()
                                if any(w in l.lower() for w in ("save", "load", "corrupt", "date", "time"))
                                and "Save_Remark" not in l and "Time_Stamp" not in l)},
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [{"level": "I1", "what": "text screen, BIOS data area (0040:0049, 0040:006C) and GOAL.EXE data-segment memory (DS:7B62, DS:7B64, DS:8336, DS:A9FD, the commentary ring DS:7C38 and counter DS:80EE, the score DS:9B3C, the names at [DS:9B6C], the delay byte at [DS:A923]+0x3F, two known strings) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "a savestate is written at each read, including every read during the match" + (", and one is loaded (Host+L) at the start" if self.st else "")
                  + " (vocabulary/interventions.md lists save and load of state as I2; neutrality tested by the replays of E004, not assumed)"}]
        if self.dos_time:
            back = (d.clock_applied or "").split()
            if self.clock_error is None and d.clock_applied is not None and len(back) >= 2:
                applied = f"applied: DOS reported date {back[0]} and time {back[1]} right after (`date /t`, `time /t`), checked by Driver.launch"
            else:
                applied = f"NOT verified as applied: {self.clock_error or 'no read-back'}"
            inter.append({"level": "I3", "what": f"DOS date {self.dos_date} and DOS time {self.dos_time} requested with the DOSBox-X commands "
                          f"`date {self.dos_date}` and `time {self.dos_time}` in the autoexec, before GOAL runs; {applied}"})
        if self.st:
            made = self.st.config
            start = {"id": self.st.name, "sha256": self.st.sha256,
                     "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}) with C: mounted from the folder the savestate was made with, "
                                 f"recreated from the verified release copy; GOAL run to its title screen; key n to change the screen; then Host+L "
                                 f"loads the savestate whose sha256 is given (made by `run.py make-state` at DOS time {made.get('dos_time')} on "
                                 f"{made.get('dos_date')}, DOS read-back {self.st.meta.get('clock_applied', 'not stored')!r}: the captain screen of the next match); "
                                 f"polled until the screen digest equals the one stored with it ({self.st.screen_digest}); DOS clock of this session not set "
                                 f"(the restore brings the state's own BIOS ticks, F004)")}
        else:
            start = {"id": "fresh-launch", "sha256": conf_sha,
                     "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, nothing "
                                 f"restored; DOS time set to {self.dos_time} on {self.dos_date} before GOAL ran; then the keys "
                                 f"{' '.join(self.pre_keys)}, each followed by a settle poll, to the captain screen (an Enter after the last only when the team screen came first)")}
        arm = f"{self.arm}-{'state-' + self.st.name if self.st else 'fresh-time-' + self.dos_time.replace(':', '')}"
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": arm, "rep": self.n,
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E004-q002-quick-result/run.py", "sha256": driver.sha256(Path(__file__).read_bytes()),
                        "args": [self.kind, "--arm", self.arm] + (["--state", self.st.name] if self.st else ["--dos-time", self.dos_time, "--dos-date", self.dos_date])
                        + ["--batch", self.args.batch, "starting keys: " + " ".join(match.START_KEYS[self.arm])]},
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
        print(f"{self.run_id} {arm}: {status}")
        return status == "completed"


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


def minutes(spec):
    """'10:00-10:03' -> ['10:00:00', '10:01:00', '10:02:00', '10:03:00']."""
    m = re.fullmatch(r"(\d\d):(\d\d)-(\d\d):(\d\d)", spec)
    if not m:
        raise ValueError(f"--minutes {spec!r}: HH:MM-HH:MM")
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    if b < a:
        raise ValueError(f"--minutes {spec!r}: the end is before the start")
    return [f"{t // 60:02d}:{t % 60:02d}:00" for t in range(a, b + 1)]


def load_state(name):
    st = driver.StartState(name)
    st.meta = json.loads((driver.STATES / f"{name}.json").read_text())
    try:
        driver.Driver({"cycles": CYCLES}).check_start_state(st)
    except driver.StateLayoutMismatch as e:
        raise SystemExit(f"refused: {e}; for an E004 state: `{remake_command(name)}`") from None
    return st


def make_state(args):
    name = state_name(args.dos_time)
    states = driver.STATES
    if (states / f"{name}.sav").exists():
        raise SystemExit(f"{states}/{name}.sav exists; start states are never replaced")
    states.mkdir(parents=True, exist_ok=True)
    d = driver.Driver({"cycles": CYCLES, "dos_time": args.dos_time, "dos_date": args.dos_date}, workdir=driver.SCRATCH / f"make-{name}")
    try:
        sc = d.launch(None)
        for k in TO_MAIN + TO_CAPTAIN:
            prev = sc.digest()
            d.keys(k)
            sc = d.settle(prev, what=f"after key {k}")
        keys = TO_MAIN + TO_CAPTAIN
        if extra_key(sc):
            d.keys(extra_key(sc))
            keys = keys + ["Enter"]
            sc = d.settle(sc.digest(), what="after key Enter (team screen: play)")
        if not at_captain(sc):
            raise SystemExit("not at the captain screen: " + sc.lines()[-1].strip())
        data = d.save_state()
        st = savestate.Savestate(data)
        assert st.screen().digest() == sc.digest()
    finally:
        d.terminate()
    (states / f"{name}.sav").write_bytes(data)
    words = {f"DS:{o:04X}": f"0x{st.ds_word(o):04x}" for o in DS_WORDS}
    meta = {"sha256": driver.sha256(data), "screen_digest": sc.digest(), "game_dir": str(d.game_dir),
            "drive_layout": d.drive_layout(), "config": d.config, "clock_applied": d.clock_applied,
            "made": driver.host_times(), "keys": keys, "ticks": st.ticks()[0], "ds_words": words,
            "screen": sc.text(), "events": d.events}
    (states / f"{name}.json").write_text(json.dumps(meta, indent=1))
    print(f"{name}.sav sha256 {meta['sha256']}, screen {sc.digest()}, {words}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=["make-state", "pairs", "sample"])
    ap.add_argument("--dos-time", help="make-state: HH:MM:SS, set by `time` in the autoexec (I3)")
    ap.add_argument("--dos-date", default=DEFAULT_DATE, help="MM/DD/YYYY, set with the DOS time")
    ap.add_argument("--state", help="pairs: the start state, e.g. e004-1000")
    ap.add_argument("--pairs", type=int, default=1)
    ap.add_argument("--arm", choices=sorted(match.START_KEYS), help="sample: the arm")
    ap.add_argument("--minutes", help="sample: HH:MM-HH:MM, one fresh launch per DOS minute")
    ap.add_argument("--slot", type=int, help="sample: a game folder of the session's own")
    ap.add_argument("--batch", default="", help="a label written into each record")
    a = ap.parse_args(argv)
    if a.kind == "make-state":
        if not a.dos_time:
            raise SystemExit("make-state needs --dos-time")
        driver.clock_values(a.dos_date, a.dos_time)
        return make_state(a) or 0
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok = total = 0
    if a.kind == "pairs":
        if not a.state:
            raise SystemExit("pairs needs --state")
        st = load_state(a.state)
        for _ in range(a.pairs):
            for arm in ("quick", "watched"):
                total += 1
                ok += Run("pairs", arm, reserve_id(), a, commit, st=st).go()
    else:
        if not (a.arm and a.minutes):
            raise SystemExit("sample needs --arm and --minutes")
        times = minutes(a.minutes)
        for t in times:
            driver.clock_values(a.dos_date, t)
        for t in times:
            total += 1
            ok += Run("sample", a.arm, reserve_id(), a, commit, dos_time=t, slot=a.slot).go()
    print(f"{ok} of {total} runs completed")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
