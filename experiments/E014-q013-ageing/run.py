#!/usr/bin/env python3
"""E014 (T28, Q013): the year-end ageing of the player records — the behavioural corroboration.

    python3 experiments/E014-q013-ageing/run.py adopt --from-run E006-r0001
    python3 experiments/E014-q013-ageing/run.py years --state e006-1000-r0001 --years 4 --batch b1
    python3 experiments/E014-q013-ageing/run.py years --state e014-b1-y2s3 --years 4 --batch b2

One session auto-plays the game from a start state (E006's published main-screen savestate of a
new game, or a year-end state an earlier E014 session staged) and captures the player records of
3 computer countries at every year end — the settling screen after the stage byte [A923]+0x3C
entered a stage in {2, 3, 5, 7}, the four transitions per 4-year cycle at which `1771:8208`
calls the ageing loop `1771:80DA` (experiments/E014-q013-ageing/notes.md, section 1). The auto-
play answers every stable screen: the main menu's `play next game` (Esc, Up, Enter — E003's
SEQ_A keys), the team screen (Enter), the captain screen (runtime/driver/match.py's quick arm:
Enter+r, then Enter per `hit any key` until FULL TIME), the watch-this-match prompt of
`0791:E80D` (n — the fixture is simulated by `000E:6970`), and any other stable screen (Enter:
the news, promise and championship lines, which end in `000E:05F6`'s key wait). No key is sent
while the screen is changing (E004's key discipline: one Enter per stopped-clock screen).

Each capture keeps, from one savestate (I1 reads, I2 the savestate itself): the state bytes
(+0x38 season, +0x3A base year, +0x3C stage, +0x3D rounds, +0x40 phase, +0x26/+0x28 the
fixture index and count), the 3 countries' records (+0x2E, the 20 squad words at +0..+0x27),
each squad player's 20 record bytes, surname (11 bytes at [DS:9B6C] + 11 n) and initial
([DS:9B70] + n), the derivation tables DS:6D25/DS:6DCD (F008's hazard: read from the same
savestate), and the savestate's sha256; the savestate is staged as a start state
(scratch, and published as an E014 evidence asset) so the next session resumes where this one
stopped. The countries are the first 3 unmanaged ones with 20 nonzero squad words at the first
capture, unless --countries says otherwise; a computer country's squad changes between year ends
only through the yearly loop and its deterministic retirement re-create (notes.md sections 2, 4)
— the managed country's offer path (000E:57E5) is RNG-selected and would poison the comparison.

`check_ageing.py` compares every consecutive capture pair against runtime/model/ageing.py.
A record is written only when runtime/driver/ and this folder have no uncommitted change, and
never over an existing one (L207)."""
import argparse
import importlib.util
import json
import platform
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
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
e010 = _load("e010_run", "experiments/E010-q010-quick-engine/run.py")

EXPERIMENT = "E014"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2)
CYCLES = "30000"          # E004's and E006's value, so the start state's runtime is unchanged
STATE_CONFIG = {"cycles": CYCLES}
STATES = driver.SCRATCH / "e014" / "states"     # staged year-end states (scratch, git-ignored)

# --- the state record [DS:A923] (notes.md section 1) -----------------------------------------
ST_SEASON, ST_BASEYEAR, ST_STAGE, ST_ROUNDS, ST_PHASE = 0x38, 0x3A, 0x3C, 0x3D, 0x40
ST_FIX_IDX, ST_FIX_CNT = 0x26, 0x28
AGEING_STAGES = (2, 3, 5, 7)     # the set CS:81E8 = 0xAC (seg_1771_12.asm:118, notes.md §1)
CLASS_TABLE_DS, PROFILE_TABLE_DS = 0x6D25, 0x6DCD       # F008/F015
CLASS_TABLE_LEN, PROFILE_TABLE_LEN = 14 * 12, 16 * 12
SQUAD = 20                        # the squad words, country +0..+0x27 (F011)


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def state_addr(state):
    """The absolute address of the state record: the far pointer at DS:A923."""
    return players.far_pointer(state, 0xA923)[2]


def state_tuple(state):
    a = state_addr(state)
    b = state.memory(a, 0x42)
    return {"season": int.from_bytes(b[ST_SEASON:ST_SEASON + 2], "little"),
            "base_year": int.from_bytes(b[ST_BASEYEAR:ST_BASEYEAR + 2], "little"),
            "stage": b[ST_STAGE], "rounds": b[ST_ROUNDS], "phase": b[ST_PHASE],
            "fix_idx": int.from_bytes(b[ST_FIX_IDX:ST_FIX_IDX + 2], "little"),
            "fix_cnt": int.from_bytes(b[ST_FIX_CNT:ST_FIX_CNT + 2], "little")}


def country_name(state, c):
    """The country's name: the Pascal string at [DS:9B68] + 16 c (F008's header reader 1771:0E24)."""
    base = players.far_pointer(state, 0x9B68)[2]
    raw = state.memory(base + 16 * c, 16)
    return raw[1:1 + min(raw[0], 15)].decode("cp437", "replace").strip()


def capture(state, blob, chosen, when):
    """One year-end (or start) capture: the state bytes, the 3 countries' squads and the record,
    surname and initial of every squad player, and the two derivation tables — all from this
    savestate (F008's hazard)."""
    carr = players.countries(state)
    parr = players.players(state)
    surn = players.surnames(state)
    init = players.initials(state)
    out = {"state": state_tuple(state), "when": when, "savestate_sha256": driver.sha256(blob),
           "tables": {"class": state.ds_bytes(CLASS_TABLE_DS, CLASS_TABLE_LEN).hex(),
                      "profile": state.ds_bytes(PROFILE_TABLE_DS, PROFILE_TABLE_LEN).hex()},
           "countries": []}
    for c in chosen:
        rec = players.record(carr, 0xBF, c)
        squad = [int.from_bytes(rec[2 * i:2 * i + 2], "little") for i in range(SQUAD)]
        ps = []
        for w in squad:
            pr = players.record(parr, 0x14, w)
            ps.append({"w": w, "rec": pr.hex(),
                       "surname": bytes(surn[11 * w:11 * w + 11]).hex(),
                       "initial": f"{init[w]:02x}"})
        out["countries"].append({"n": c, "name": country_name(state, c),
                                 "manager_byte": rec[0x2E], "squad": squad, "players": ps})
    return out


def pick_countries(state):
    """The first 3 unmanaged countries (their +0x2E below 0x80, 1771:0B77) with 20 nonzero
    squad words — a computer country's squad changes between year ends only through the yearly
    loop and its deterministic retirement re-create (notes.md sections 2, 4)."""
    carr = players.countries(state)
    chosen = []
    for c in range(1, 129):
        rec = players.record(carr, 0xBF, c)
        if rec[0x2E] >= 0x80:
            continue
        squad = [int.from_bytes(rec[2 * i:2 * i + 2], "little") for i in range(SQUAD)]
        if all(squad) and len(set(squad)) == SQUAD:
            chosen.append(c)
        if len(chosen) == 3:
            break
    if len(chosen) != 3:
        raise RuntimeError(f"only {len(chosen)} unmanaged countries with a full squad found")
    return chosen


def _headline(sc):
    """The screen's headline: its first non-empty row, the row the game titles a screen with."""
    for ln in sc.lines():
        if ln.strip():
            return ln.strip()
    return ""


def _headline(sc):
    """The screen's headline: its first non-empty row, the row the game titles a screen with."""
    for ln in sc.lines():
        if ln.strip():
            return ln.strip()
    return ""


class Session:
    def __init__(self, n, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.args, self.commit = args, commit
        self.st = driver.StartState(args.state, STATES if (STATES / f"{args.state}.sav").exists() else driver.STATES)
        self.d = driver.Driver(STATE_CONFIG, workdir=driver.SCRATCH / "e014" / self.run_id)
        self.obs, self.step, self.keys = [], 0, []
        self.captures = []
        self.chosen = [int(x) for x in args.countries.split(",")] if args.countries else None
        self.prev_tuple = None
        self.unknown = 0
        # live progress (owner direction 2026-10-07): what the heartbeat prints, and the
        # stuck-screen watchdog's state — the screen digest the loop last acted on and how
        # many keys in a row have left it unchanged.
        self.matches = 0
        self.last_text, self.last_tuple = "", {}
        self.last_digest, self.same_digest_keys = None, 0
        self.same_reason, self.same_reason_keys = None, 0
        self.cur_text = ""

    # --- observation helpers ---------------------------------------------------------------
    def add(self, source, field, value, addr=None):
        o = {"step": self.step, "source": source, "field": field, "value": value}
        if addr is not None:
            o["addr"] = addr
        self.obs.append(o)

    def log_key(self, key, why):
        self.keys.append((round(time.monotonic() - self.d.t0, 2), key, why))
        self.d.log(f"key {key!r}: {why}")
        # stuck-screen watchdog: 15 keys sent for the same reason with no other screen acted on
        # between them is a responder bug, not slow play (r0002: 1193 Enters on one `location:`
        # screen). The digest watchdog in go() misses screens with a blinking element, so this
        # counts reasons; at the threshold the loop's current screen is recorded in full.
        if why == self.same_reason:
            self.same_reason_keys += 1
        else:
            self.same_reason, self.same_reason_keys = why, 1
        if self.same_reason_keys >= 15:
            self.add("ui-text", f"stuck screen: {self.same_reason_keys} keys, one reason ({why}); its full text",
                     self.cur_text)
            raise RuntimeError(f"15 keys, one reason ({why}), no advance; screen recorded: "
                               + " / ".join(ln.strip() for ln in self.cur_text.splitlines()[:6] if ln.strip()))

    def stable(self, max_reads=40):
        """Poll reads until the screen digest repeats; returns (screen, times, state, blob)."""
        prev = None
        for _ in range(max_reads):
            times, state, blob = self.d.read()
            dg = state.screen().digest()
            if dg == prev:
                return state.screen(), times, state, blob
            prev = dg
        raise RuntimeError(f"no stable screen within {max_reads} reads")

    # --- the year-end capture ----------------------------------------------------------------
    def maybe_capture(self, state, blob, when):
        t = state_tuple(state)
        first = self.prev_tuple is None
        moved = (not first and (t["stage"], t["season"]) != (self.prev_tuple["stage"], self.prev_tuple["season"])
                 and t["stage"] in AGEING_STAGES)
        self.prev_tuple = t
        if not (first and when == "start" or moved):
            return False
        if self.chosen is None:
            self.chosen = pick_countries(state)
        k = len(self.captures)
        name = f"e014-{self.args.batch or 'x'}-y{k}"
        cap = capture(state, blob, self.chosen, when)
        cap["state_name"] = name
        e010.stage(name, blob, {"screen_digest": state.screen().digest(), "game_dir": str(self.d.game_dir),
                                "drive_layout": self.d.drive_layout(), "config": STATE_CONFIG}, STATES)
        self.captures.append(cap)
        self.step += 1
        self.add("memory", f"capture {k} ({when}): the state bytes, the 3 countries' squads, every squad "
                           "player's 20 record bytes, surname and initial, the tables DS:6D25/DS:6DCD, and the "
                           "savestate's sha256 (the savestate is staged as start state " + name + ")",
                 json.dumps(cap, separators=(",", ":")))
        self.add("ui-text", f"capture {k} ({when}): the settled screen at the capture", state.screen().text())
        print(f"{self.run_id}: capture {k} ({when}) {json.dumps(cap['state'])} countries {self.chosen}", flush=True)
        return True

    def heartbeat(self, stop):
        """Print live progress at most every 60 s (owner direction): elapsed wall clock, the
        current screen's headline, the state tuple and the matches played. stdout is unbuffered
        (main reconfigures it), so a detached run's log shows real progress."""
        while not stop.wait(60):
            print(f"{self.run_id}: {round(time.monotonic() - self.d.t0)} s: {self.last_text[:60]!r} "
                  f"{json.dumps(self.last_tuple)} matches {self.matches} captures {len(self.captures)}",
                  flush=True)

    # --- the auto-play loop --------------------------------------------------------------------
    def go(self):
        status = "completed"
        gone = False
        deadline = time.monotonic() + self.args.budget
        stop = threading.Event()
        threading.Thread(target=self.heartbeat, args=(stop,), daemon=True).start()
        try:
            sc = self.d.launch(self.st)
            times, state, blob = self.d.read()
            self.step += 1
            self.add("ui-text", "start state restored: the screen", state.screen().text())
            self.maybe_capture(state, blob, "start")
            while len(self.captures) < self.args.years + 1 and time.monotonic() < deadline:
                sc, times, state, blob = self.stable()
                if self.maybe_capture(state, blob, "year end"):
                    self.last_text, self.last_tuple = _headline(sc), state_tuple(state)
                    continue
                text = sc.text()
                self.cur_text = text
                self.last_text, self.last_tuple = _headline(sc), state_tuple(state)
                # stuck-screen watchdog: a key that leaves the screen unchanged 12 times in a
                # row is a responder bug, not slow play — abort naming the screen (r0002 looped
                # 1193 Enters on one `location:` screen without ever identifying it).
                dg = sc.digest()
                self.same_digest_keys = self.same_digest_keys + 1 if dg == self.last_digest else 0
                self.last_digest = dg
                if self.same_digest_keys >= 12:
                    raise RuntimeError(f"12 keys left the screen unchanged: " + sc.lines()[-1].strip()
                                       + " | screen: " + " / ".join(ln.strip() for ln in sc.lines()[:6] if ln.strip()))
                if "How many players" in text:
                    raise RuntimeError("the game is back at its title screen")
                if match.is_full_time(sc):
                    self.matches += 1
                    self.log_key("Enter", "the full-time board")
                    self.d.keys("Enter")
                elif "watch this match" in text:
                    self.log_key("n", "the watch-this-match prompt (0791:E80D): simulate (000E:6970)")
                    self.d.keys("n")
                elif e004.at_captain(sc):
                    self.log_key("Enter+r", "the captain screen: match.play quick (E004's d3b burst)")
                    ks, reads, secs = match.play(self.d, "quick", None)
                    self.keys.extend((round(time.monotonic() - self.d.t0, 2) + s, k, f"match.play: {w}")
                                       for s, k, w in ks)
                    self.d.log(f"match quick: {reads} reads, {secs} s")
                elif e004.team_screen(sc):
                    self.log_key("Enter", "the team screen (location:), its default option ' play '")
                    self.d.keys("Enter")
                elif "F2-new name" in text or "R,C-reposition" in text:
                    self.log_key("Esc", "the select-squad screen (menu item 5, reached in error): Esc-exit")
                    self.d.keys("Esc")
                elif "play next game" in text:
                    # the main menu: the selected item is the word DS:00B0, moved 1..6 with wrap by
                    # 214B:15B1 (u214b_menu_move_word_wrap(6, 0xB0, ...) in main_menu_loop 000E:7439);
                    # Enter runs item 6 (play_round, 000E:70B9). The cursor survives from the last
                    # Enter, so Up/Down are sent by the read item, never blind (E014-r0001: a blind
                    # Up from a remembered 6 selected item 5, the squad screen).
                    item = state.ds_word(0x00B0)
                    if item == 6:
                        self.log_key("Enter", "the main menu: item 6 (DS:00B0 = 6), play next game")
                        self.d.keys("Enter")
                    else:
                        self.log_key("Down", f"the main menu: item {item}, moving toward 6 (DS:00B0)")
                        self.d.keys("Down")
                elif "spacebar-players" in text:
                    self.log_key("Esc", "the team screen: open the main menu")
                    self.d.keys("Esc")
                elif match.wants_key(sc):
                    self.log_key("Enter", f"stable screen: {match.wants_key(sc)}")
                    self.d.keys("Enter")
                else:
                    self.unknown += 1
                    if self.unknown > 40:
                        raise RuntimeError("40 unknown stable screens in a row: " + sc.lines()[-1].strip())
                    self.log_key("Enter", "unknown stable screen (a news, promise or draw line): advance")
                    self.d.keys("Enter")
                    continue
                self.unknown = 0
            if len(self.captures) < 2:
                status = f"stopped: only {len(self.captures)} capture(s) within the budget"
        except Exception as e:  # noqa: BLE001
            status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
            traceback.print_exc()
        finally:
            stop.set()
            gone = self.d.terminate()
        return self.record(status, gone)

    # --- the record ------------------------------------------------------------------------------
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
            {"step": 0, "source": "log", "field": "the countries captured, and why (the first 3 unmanaged ones with a full squad unless --countries)", "value": json.dumps(self.chosen)},
            {"step": last, "source": "log", "field": "every key sent, in order: [seconds since launch, key, why]", "value": json.dumps(self.keys)},
            {"step": last, "source": "log", "field": "captures: the state tuple and the savestate sha256 of each", "value": json.dumps(
                [{"when": c["when"], "state": c["state"], "sha256": c["savestate_sha256"], "state_name": c["state_name"]} for c in self.captures])},
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [
            {"level": "I1", "what": "text screen and GOAL.EXE memory (the state record [DS:A923] bytes +0x26/+0x28/+0x38/+0x3A/+0x3C/+0x3D/+0x40, the 3 countries' records at [DS:A917] + 0xBF c, the squad players' 20 record bytes at [DS:A91B] + 0x14 n, the surnames at [DS:9B6C] + 11 n and initials at [DS:9B70] + n, the derivation tables DS:6D25/DS:6DCD) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
            {"level": "I2", "what": "savestates written at every read; one loaded (Host+L): the start state; every year-end capture's savestate staged as the next session's start state"},
        ]
        start = {"id": self.st.name, "sha256": self.st.sha256,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, "
                             f"GOAL run to its title screen; key n to change the screen; then Host+L loads the start state whose sha256 is given "
                             f"({self.st.name}.sav); polled until the screen digest equals the one stored with it ({self.st.screen_digest}); "
                             f"DOS clock of this session not set")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": "years",
            "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": e010.cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{e010.cycle.machine_id()}",
                        "fingerprint": e010.cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E014-q013-ageing/run.py", "sha256": SCRIPT_SHA,
                        "args": list(self.args.argv) + ["arm years"]},
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
        print(f"{self.run_id}: {status}; captures {len(self.captures)}", flush=True)
        return status == "completed", OUT / f"{self.run_id}.json"


def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    a = sub.add_parser("adopt", help="store an E006 published main-screen savestate as a start state (E007's adopt)")
    a.add_argument("--from-run", required=True, dest="from_run")
    y = sub.add_parser("years", help="auto-play and capture the year ends, one record")
    y.add_argument("--state", required=True, help="the start state's name (E006's adopted one, or an E014 staged one)")
    y.add_argument("--years", type=int, default=4, help="year-end captures to take after the start capture (default 4 = one cycle)")
    y.add_argument("--countries", default="", help="3 country numbers, comma-separated (default: auto-pick)")
    y.add_argument("--budget", type=int, default=1500, help="wall-clock seconds for the auto-play loop [designed]")
    y.add_argument("--batch", default="", help="a label written into the record and the staged state names")
    return ap


def main(argv=None):
    sys.stdout.reconfigure(line_buffering=True)   # live progress when redirected (owner direction)
    argv = sys.argv[1:] if argv is None else list(argv)
    a = parser().parse_args(argv)
    a.argv = argv
    if a.kind == "adopt":
        e007.STATE_CONFIG = STATE_CONFIG          # E007's adopt stores with this session's config
        e007.adopt(a.from_run)
        return 0
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok, _ = Session(next_id(), a, commit).go()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
