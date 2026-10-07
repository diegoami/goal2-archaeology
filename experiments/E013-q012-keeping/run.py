#!/usr/bin/env python3
"""E013 (T27, Q012): where keeping is read and where penalties are read — the I3 corroboration.

    python3 experiments/E013-q012-keeping/run.py edit --from-run E006-r0005 --who keeper --to 0x00 --batch b1

A watched match from an E012-class release start state under E004's conditions (E007's adopt,
E004's keys and watched arm), played to the half-time team-screen stall; there the driver's own
half-time savestate is taken, ONE byte of one player record is edited in a copy of it
(`runtime/driver/savestate.with_memory`, an I3 edit), and the edited copy is restored with
Host+L before the Enter that starts the second half — so the edit is in place for the whole
second half (the shoot-out hazard's rule: edits before the phase that must read them).

`--who keeper` edits squad word 1 of `--side` (the side's slot-1 goalkeeper, verified by its
record's +7 = 0 at run time); `--who outfield` edits squad word 2 of side 0 (verified +7 != 0).
`--to` is the new value of byte +4 (F008's scale of all twelve skills; there is no stored
keeping byte to edit).

Per run the record carries the ground truth `check_keeping.py` checks against the model
`runtime/model/keeping.py`: both sides' squad words; the edited player's 20 record bytes and the
class/profile tables DS:6D25/DS:6DCD read at the captain screen AND at the half-time stall
(before the edit); the same after the restore (the edit proven in memory); and the full
commentary line log in ring order. A record is written only when runtime/driver/ and this folder
have no uncommitted change, and never over an existing one (L207)."""
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

sys.path.insert(0, str(ROOT / "runtime" / "model"))
import keeping  # noqa: E402


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e004 = _load("e004_run", "experiments/E004-q002-quick-result/run.py")
e007 = _load("e007_run", "experiments/E007-q009-player-screen/run.py")

EXPERIMENT = "E013"
HERE = Path(__file__).resolve().parents[0]
OUT = ROOT / "runs" / EXPERIMENT
SCRIPT_SHA = driver.sha256(Path(__file__).read_bytes())  # as loaded (E004 amendment 2)
CYCLES = e004.CYCLES          # E004's and E006's value, so the start state's runtime is unchanged
STATE_CONFIG = {"cycles": CYCLES}
SIDES = 0x9B34                # DS offset of the two engine sides' country words (E012)
CLASS_TABLE_DS, PROFILE_TABLE_DS = 0x6D25, 0x6DCD   # F008; read from the savestate (hazard: data, not record)
CLASS_TABLE_LEN, PROFILE_TABLE_LEN = 14 * 12, 16 * 12


def tables(state):
    """The two derivation tables as the match will read them (F008's hazard: they live in the
    data segment, so a prediction must come from the same savestate as the record)."""
    return {"class": list(state.ds_bytes(CLASS_TABLE_DS, CLASS_TABLE_LEN)),
            "profile": list(state.ds_bytes(PROFILE_TABLE_DS, PROFILE_TABLE_LEN))}


def squad_read(state):
    """Both sides' country number and squad words, plus the full 20-byte record of each side's
    squad word 1 (its goalkeeper, verified) and of side 0's squad word 2 (the outfield arm)."""
    ca, pa = players.countries(state), players.players(state)
    sides = []
    for side in (0, 1):
        c = state.ds_word(SIDES + 2 * side)
        sq = players.squad(ca, c)
        sides.append({"side": side, "country": c, "squad": sq})
    for side in sides:
        for word, tag in ((1, "squadword1"), (2, "squadword2")):
            n = side["squad"][word - 1]
            side[tag] = {"word": word, "player": n,
                         "record": list(players.record(pa, players.PLAYER_SIZE, n))}
    return sides


def clock_read(state):
    b = state.ds_bytes
    return (state.ds_word(0x831F), state.ds_word(0x831D), b(0x8325, 1)[0], state.ds_word(0x831B),
            state.ds_word(0x7B62), (b(0x9B3C, 1)[0], b(0x9B3D, 1)[0]), state.ds_word(commentary.COUNTER))


def stall(sc, state, prev_stable):
    """The half-time team screen (E012's `stall`): stable, clock stopped, `location:` shown."""
    if state.ds_bytes(0x8325, 1)[0] != 0 or not prev_stable:
        return None
    return "location:" in sc.text() and state.ds_word(0x831F) in (45, 46)


class EditedState:
    """A savestate restored mid-run: the driver's `restore` needs a path, a name, the screen
    digest to wait for, and this driver's drive layout (driver.py's `check_start_state`)."""

    def __init__(self, name, path, screen_digest, drive_layout, sha):
        self.name, self.path = name, Path(path)
        self.screen_digest, self.drive_layout, self.sha256 = screen_digest, drive_layout, sha


class Run:
    def __init__(self, n, args, commit):
        self.run_id = f"{EXPERIMENT}-r{n:04d}"
        self.args, self.commit = args, commit
        self.st = driver.StartState(e007.adopt(args.from_run))
        self.d = driver.Driver(STATE_CONFIG, workdir=driver.SCRATCH / "e013" / self.run_id)
        self.obs, self.step, self.keys, self.pre_keys = [], 0, [], list(e004.TO_CAPTAIN)
        self.reads, self.seconds, self.final = 0, None, None
        self.tracker = commentary.Tracker()
        self.prev_digest = None
        self.halftime = None            # squad_read + tables of the stall state (before the edit)
        self.edited_done = False
        self.edit_desc = None

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
        if self.halftime is None and stall(sc, state, stable):
            self.halftime = True
            self.obs_mem("half-time team-screen stall (before the edit): both sides' country, squad words, the 20 record bytes of squad word 1 (the goalkeeper) and squad word 2 of each side, and the derivation tables DS:6D25/DS:6DCD",
                         json.dumps({"sides": squad_read(state), "tables": tables(state)}, separators=(",", ":")))
            self.obs_mem("half-time stall: commentary lines seen (the first half's extent)",
                         str(len(self.tracker.lines)))
            self.d.log(f"half-time stall at read {self.reads}: minute {m}")
            self.apply_edit(sc)
        elif self.halftime and not self.edited_done:
            raise RuntimeError("the stall was seen but the edit never completed")

    def apply_edit(self, sc):
        """The I3 edit: one byte of one player record in a copy of the driver's own half-time
        savestate, restored with Host+L before match.play sends the half-time Enter."""
        side = self.args.side
        _, state, blob = self.d.last[0], self.d.last[1], self.d.last_blob
        sq = squad_read(state)
        who = sq[side]["squadword1" if self.args.who == "keeper" else "squadword2"]
        rec = who["record"]
        want_pos = 0 if self.args.who == "keeper" else (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
        pos = rec[7]
        if self.args.who == "keeper" and pos != 0:
            raise RuntimeError(f"side {side} squad word 1 (player {who['player']}) has +7 = {pos}, not a goalkeeper")
        if self.args.who == "outfield" and pos == 0:
            raise RuntimeError(f"side {side} squad word 2 (player {who['player']}) has +7 = 0, a goalkeeper")
        seg, off, lin = players.far_pointer(state, players.PLAYERS_PTR)
        addr = lin + players.PLAYER_SIZE * who["player"] + 4
        new = int(self.args.to, 0)
        edited = savestate.with_memory(blob, addr, bytes([new]))
        name = f"{self.run_id}-halftime-edit"
        folder = driver.SCRATCH / "e013" / self.run_id
        folder.mkdir(parents=True, exist_ok=True)
        p = folder / f"{name}.sav"
        with open(p, "xb") as f:
            f.write(edited)
        self.d.log(f"I3 edit: player {who['player']} (side {side} squad word {who['word']}) +4 "
                   f"{rec[4]} -> {new} at guest 0x{addr:x}; edited savestate {p.name}")
        st = EditedState(name, p, sc.digest(), self.d.drive_layout(), driver.sha256(edited))
        self.d.restore(st)
        # prove the edit is in guest memory before the second half starts
        _, after = self.d.last[0], self.d.last[1]
        pa = players.players(after)
        got = players.record(pa, players.PLAYER_SIZE, who["player"])[4]
        if got != new:
            raise RuntimeError(f"the edit did not reach guest memory: +4 = {got}, wanted {new}")
        self.edited_done = True
        self.edit_desc = {"side": side, "who": self.args.who, "player": who["player"],
                          "squad_word": who["word"], "byte": "+4", "old": rec[4], "new": new,
                          "guest_addr": addr, "position_+7": pos,
                          "before": {"keeping": keeping.skill_value(rec[4], rec[5], rec[7], 1, *self.tab_of(after))},
                          "after": {"keeping": keeping.skill_value(new, rec[5], rec[7], 1, *self.tab_of(after))}}
        self.obs_mem("the I3 edit, restored at the half-time stall before the second half (player +4; the derived keeping values the model predicts from these bytes)",
                     json.dumps(self.edit_desc, separators=(",", ":")))

    @staticmethod
    def tab_of(state):
        t = tables(state)
        return t["class"], t["profile"]

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
            self.obs_mem("captain screen (the match's start): both sides' country, squad words, the 20 record bytes of squad word 1 (the goalkeeper) and squad word 2 of each side, and the derivation tables DS:6D25/DS:6DCD",
                         json.dumps({"sides": squad_read(state), "tables": tables(state)}, separators=(",", ":")))
            _, self.reads, self.seconds = match.play(d, "watched", self.on_read, keys=self.keys)
            if self.tracker.gaps:
                raise RuntimeError("commentary gap: " + "; ".join(self.tracker.gaps[:3]))
            if not self.edited_done:
                raise RuntimeError("the half-time stall was never seen: the edit never happened")
            self.step += 1
            _, fstate = self.final
            self.obs_mem("full time: both sides' country, squad words and the edited player's record (the edit's whole-match extent)",
                         json.dumps(squad_read(fstate), separators=(",", ":")))
            if not any("FULL TIME" in row for row in fstate.screen().lines()):
                raise RuntimeError("the full-time screen is not the summary")
            self.obs_mem("events of the match (runtime/driver/commentary.py): [kind, team, text]",
                         json.dumps(self.tracker.events(), ensure_ascii=False))
            self.obs_mem("commentary line log in ring order: [n, template, p1, p2, team] per line, as 1D4A wrote them (the predictor's input)",
                         json.dumps([[x["n"], x["template"], x["p1"], x["p2"], x["team"]] for x in self.tracker.lines],
                                    separators=(",", ":")))
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
            {"step": 0, "source": "log", "field": "keys sent after the restore to the captain screen, in order", "value": " ".join(self.pre_keys)},
            {"step": last, "source": "log", "field": "keys sent from the key that starts the match to full time: [seconds since the starting burst, key, why] (runtime/driver/match.py)",
             "value": json.dumps(self.keys)},
            {"step": last, "source": "log", "field": "match: savestate reads from the starting keys to full time, and seconds", "value": f"{self.reads} reads, {self.seconds} s"},
            {"step": last, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL after TERM_GRACE, see log)",
             "value": "both exited" if gone else "a process remained"},
            {"step": last, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
        ]
        obs = sorted(head + self.obs + tail, key=lambda o: o["step"])
        inter = [{"level": "I1", "what": "text screen, BIOS data area and GOAL.EXE memory (the match clock DS:831F/831D/8325/831B, the seed DS:7B62, the score DS:9B3C/9B3D, the commentary ring, the squad words, the edited player's 20 record bytes and the derivation tables DS:6D25/DS:6DCD) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
                 {"level": "I2", "what": "savestates written at every read; one loaded (Host+L): the start state; the match runs watched from the captain screen"},
                 {"level": "I3", "what": "one byte of one player record edited in a copy of the run's own half-time savestate (savestate.with_memory) and the copy restored with Host+L at the half-time stall, before the second half: the edit is the player's +4, the scale of all twelve derived skills (F008); there is no stored keeping byte"}]
        start = {"id": self.st.name, "sha256": self.st.sha256,
                 "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}), game folder recreated from the verified release copy, GOAL run to its title screen; "
                             f"key n to change the screen; then Host+L loads E006's published main-screen savestate whose sha256 is given ({self.st.name}.sav, release E006; "
                             f"the start state of E012's runs from the same E006 run); polled until the screen digest equals the one stored with it ({self.st.screen_digest}); "
                             f"DOS clock of this session not set")}
        record = {
            "schema": "run/1", "run_id": self.run_id, "experiment": EXPERIMENT, "arm": "watched-edit", "rep": int(self.run_id.split("-r")[1]),
            "code_commit": self.commit, "machine": cycle.machine_id(),
            "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
            "runtime": {"driver": f"runtime/driver/driver.py@{self.commit}",
                        "platform": f"python-{platform.python_version()}/{cycle.machine_id()}",
                        "fingerprint": cycle.fingerprint(d, conf_sha)},
            "interventions": inter, "start_state": start, "seed": None,
            "actions": {"script": "experiments/E013-q012-keeping/run.py", "sha256": SCRIPT_SHA, "args": list(self.args.argv) + ["arm edit"]},
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
        print(f"{self.run_id} {self.st.name} watched-edit: {status}")
        return status == "completed", OUT / f"{self.run_id}.json"


def next_id():
    used = [int(p.stem.split("-r")[1]) for p in OUT.glob(f"{EXPERIMENT}-r*.json")]
    return 1 + max(used, default=0)


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    w = sub.add_parser("edit", help="one watched match with one I3 edit at half time, one record")
    w.add_argument("--from-run", required=True, dest="from_run", help="the E006 run id whose manifest names the main-screen start state (E012's runs use the same)")
    w.add_argument("--who", choices=["keeper", "outfield"], required=True, help="keeper: squad word 1 of --side; outfield: squad word 2 of side 0")
    w.add_argument("--side", type=int, default=1, help="the side whose player is edited (default 1, the side whose keeper saved in E012-r0001)")
    w.add_argument("--to", required=True, help="the new value of byte +4, e.g. 0x00 or 0xFF")
    w.add_argument("--batch", default="", help="a label written into the record")
    return ap


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    a = parser().parse_args(argv)
    a.argv = argv
    dirty = git("status", "--porcelain", "--", "runtime/driver", str(HERE.relative_to(ROOT)))
    if dirty:
        raise SystemExit("uncommitted changes under runtime/driver/ or the experiment: commit them first\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    ok, _ = Run(next_id(), a, commit).go()
    return 0 if ok else 1


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


if __name__ == "__main__":
    sys.exit(main())
