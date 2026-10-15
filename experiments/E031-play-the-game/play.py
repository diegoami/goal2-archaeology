#!/usr/bin/env python3
"""Play GOAL2 interactively under the G1 driver: one server holds the emulator, a client sends keys
and prints the screen (E031, the play-the-game brief).

    python3 experiments/E031-play-the-game/play.py serve S [--cycles "fixed 8000"] [--gl FILE.GL ...]
    python3 experiments/E031-play-the-game/play.py send S KEY [KEY ...] [--timeout 8] [--gap 0]
    python3 experiments/E031-play-the-game/play.py type S "text"          one key per character
    python3 experiments/E031-play-the-game/play.py show S                 read the screen again
    python3 experiments/E031-play-the-game/play.py wait S "text" [--timeout 60] [--gone]
    python3 experiments/E031-play-the-game/play.py checkpoint S LABEL     keep this savestate
    python3 experiments/E031-play-the-game/play.py note S "text"          a line in the log
    python3 experiments/E031-play-the-game/play.py stop S                 terminate and exit

The server is `runtime/driver/driver.Driver` (Xvfb on a private display the driver picks, never :99;
DOSBox-X 2024.03.01; keys by XTEST; every screen read is a savestate). It listens on the abstract
Unix socket `goal2-play-<S>`. `--gl` copies saved games into the game folder before DOSBox-X starts
(the driver recreates that folder from the release copy at each launch).

Every request is logged, append-only, to `experiments/E031-play-the-game/out/<S>/steps.jsonl`: the
host UTC time, the request, the screen digest after it, and the game's own progress bytes read from
the same savestate (the state block at the far pointer DS:A923: +0x38 the season word, +0x3C the
stage byte, +0x26 the fixture index word, +0x3F the match delay byte, +0x41 the replay toggle;
E014 notes, T28, F005, F030). Each distinct screen's text is written once to `screens.jsonl`, keyed by
its digest. `checkpoint` copies the savestate to `.cache/kept/E031/<S>/` (git-ignored) and logs its
sha256. A key is never sent by the server on its own: only what a client asks."""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import driver  # noqa: E402
import players  # noqa: E402
import playerscreen  # noqa: E402
sys.path.insert(0, str(HERE))
import xtest  # noqa: E402

OUT = HERE / "out"
KEPT = ROOT / ".cache" / "kept" / "E031"
GAME_RECORD = 0xA923
# Characters typed by `type` that are not their own X keysym.
CHAR_KEYS = {" ": "space", "-": "minus", ".": "period", "'": "apostrophe", ",": "comma", "/": "slash"}


def sock_name(session):
    return "\0goal2-play-" + session


def progress(state):
    """The game's progress bytes from a savestate, or {} before GOAL's data segment exists."""
    try:
        seg, off, lin = players.far_pointer(state, GAME_RECORD)
        if lin == 0:
            return {}
        b = state.memory(lin, 0x42)
        w = lambda o: int.from_bytes(b[o:o + 2], "little")  # noqa: E731
        return {"season": w(0x38), "stage": b[0x3C], "fixture": w(0x26), "fixtures": w(0x28),
                "delay": b[0x3F], "replay": b[0x41]}
    except Exception:  # noqa: BLE001 - at the DOS prompt there is no GOAL program yet
        return {}


def marks(sc):
    """Where the screen highlights: for each row, the cells whose background differs from the row's
    most common background, as {row: "  ^^^^ "}. The text alone does not show which option is
    selected; the background does."""
    out = {}
    lines = sc.lines()
    for r in range(25):
        bg = [a >> 4 for a in sc.attrs[r * 80:(r + 1) * 80]]
        common = max(set(bg), key=bg.count)
        row = "".join("^" if b != common else " " for b in bg).rstrip()
        if row and len(lines[r].strip()):
            out[r] = row
    return out


class PlayDriver(driver.Driver):
    """The driver, with saved games copied into the game folder before DOSBox-X starts."""

    def __init__(self, *a, gl=(), mapper=None, **k):
        super().__init__(*a, **k)
        self.gl = [Path(p) for p in gl]
        self.mapper = Path(mapper) if mapper else None

    # With mapper-nohost.map the savestate is Scroll Lock alone and the load Print Screen alone, so the
    # host key F12 is never pressed (make_mapper.py says why).
    SINGLE_KEYS = {"s": "Scroll_Lock", "l": "Print"}

    def keys(self, *names, hold=driver.KEY_HOLD):
        """Function keys go as raw XTEST keycodes (xtest.py: xdotool adds Left Alt to them); the rest
        through the driver (xdotool)."""
        for name in names:
            if re.fullmatch(r"F\d{1,2}", name):
                code = xtest.key_event(self.display, name, True)
                time.sleep(hold)  # key hold; logged below
                xtest.key_event(self.display, name, False)
                self.log(f"key {name} (raw keycode {code}) held {hold}s")
            else:
                super().keys(name, hold=hold)

    def _hostkey(self, name, hold=driver.HOSTKEY_HOLD):
        if not (self.mapper and self.mapper.name == "mapper-nohost.map"):
            return super()._hostkey(name, hold)
        k = self.SINGLE_KEYS[name]
        self._x("keydown", k)
        time.sleep(hold)  # key hold; logged below
        self._x("keyup", k)
        self.log(f"emulator key {k} (for host+{name}) held {hold}s")

    def _start_xvfb(self):
        if self.mapper:  # the config names <work>/mapper.map; DOSBox-X reads it at start
            shutil.copy(self.mapper, self.workdir / "mapper.map")
            self.log(f"mapper file {self.mapper.name} copied in, sha256 {driver.sha256(self.mapper.read_bytes())}")
        for p in self.gl:  # launch() has just recreated the game folder from the release copy
            shutil.copy(p, self.game_dir / p.name)
            self.log(f"saved game {p.name} copied in, sha256 {driver.sha256(p.read_bytes())}")
        super()._start_xvfb()


class Server:
    def __init__(self, session, cycles, gl, mapper=None):
        self.session = session
        self.out = OUT / session
        self.out.mkdir(parents=True, exist_ok=True)
        self.kept = KEPT / session
        self.kept.mkdir(parents=True, exist_ok=True)
        self.seen = set()
        sp = self.out / "screens.jsonl"
        if sp.exists():
            self.seen = {json.loads(l)["digest"] for l in sp.read_text().splitlines() if l.strip()}
        steps = self.out / "steps.jsonl"
        self.n = sum(1 for _ in steps.open()) if steps.exists() else 0
        work = driver.SCRATCH / "play" / session  # its own game folder: two sessions never share one
        self.d = PlayDriver({"cycles": cycles}, workdir=work, game_dir=work / "game", gl=gl, mapper=mapper)
        self.cur = None

    def log(self, entry):
        self.n += 1
        entry = {"n": self.n, "utc": driver.host_times()["utc"], **entry}
        with open(self.out / "steps.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def observe(self):
        _, state, blob = self.d.read()
        sc = state.screen()
        dg = sc.digest()
        if dg not in self.seen:
            self.seen.add(dg)
            with open(self.out / "screens.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"digest": dg, "text": sc.text()}, ensure_ascii=False) + "\n")
        return sc, dg, progress(state), blob

    def settle(self, prev, timeout):
        """Poll until the screen differs from prev and two reads agree, or timeout: the last read."""
        end = time.monotonic() + timeout
        last = None
        reads = 0
        while True:
            sc, dg, info, blob = self.observe()
            reads += 1
            if dg != prev and dg == last:
                return sc, dg, info, blob, True, reads
            if time.monotonic() > end:
                return sc, dg, info, blob, dg != prev, reads
            last = dg

    def reply(self, req, sc, dg, info, changed=None, reads=1, t0=None):
        entry = self.log({"req": req, "digest": dg, "info": info, "changed": changed, "reads": reads,
                          "secs": round(time.monotonic() - t0, 2) if t0 else None})
        self.cur = dg
        return {**entry, "screen": sc.text(), "marks": marks(sc)}

    def handle(self, req):
        cmd = req["cmd"]
        t0 = time.monotonic()
        if cmd in ("send", "type"):
            keys = req["keys"] if cmd == "send" else [CHAR_KEYS.get(c, c) for c in req["text"]]
            prev = self.cur
            for i, k in enumerate(keys):
                self.d.keys(k, hold=req.get("hold", driver.KEY_HOLD))
                if req.get("gap") and i < len(keys) - 1:
                    time.sleep(req["gap"])  # a pause between keys the client asked for; logged in the request
            if req.get("blind"):  # no savestate: the help viewer (F1) crashes DOSBox-X's savestate
                time.sleep(req.get("after", 0.5))  # the client's pause after the keys; logged in the request
                return {**self.log({"req": req, "blind": True}), "screen": "(not read: blind send)"}
            if req.get("timeout", 8) <= 0:
                sc, dg, info, _ = self.observe()
                return self.reply(req, sc, dg, info, dg != prev, 1, t0)
            sc, dg, info, _, changed, reads = self.settle(prev, req.get("timeout", 8))
            return self.reply(req, sc, dg, info, changed, reads, t0)
        if cmd == "show":
            sc, dg, info, _ = self.observe()
            return self.reply(req, sc, dg, info, dg != self.cur, 1, t0)
        if cmd == "wait":
            end = time.monotonic() + req.get("timeout", 60)
            reads = 0
            while True:
                sc, dg, info, _ = self.observe()
                reads += 1
                hit = req["text"] in sc.text()
                if hit != bool(req.get("gone")) or time.monotonic() > end:
                    return self.reply({**req, "met": hit != bool(req.get("gone"))}, sc, dg, info, None, reads, t0)
        if cmd == "checkpoint":
            sc, dg, info, blob = self.observe()
            name = f"{self.n + 1:05d}-{req['label']}.sav"
            (self.kept / name).write_bytes(blob)
            return self.reply({**req, "file": name, "sha256": driver.sha256(blob)}, sc, dg, info, None, 1, t0)
        if cmd == "scan":  # a player screen list: read the card, Down, n times (playerscreen.parse)
            cards = []
            prev = self.cur
            for i in range(req["n"]):
                sc, dg, info, _ = self.observe()
                try:
                    p = playerscreen.parse(sc)
                    cards.append({"name": p["name"], "age": p["age"], "caps": p["caps"], "pos": p["position"],
                                  "status": p["status"], "skills": p["skills"],
                                  "panel": {k: v["word"] for k, v in p["panel"].items()},
                                  "perf": p["performance"], "bias": p["bias"]})
                except ValueError as e:
                    cards.append({"error": str(e)})
                if i < req["n"] - 1:
                    self.d.keys("Down")
            sc, dg, info, _ = self.observe()
            entry = self.reply({"cmd": "scan", "n": req["n"]}, sc, dg, info, dg != prev, req["n"], t0)
            return {**entry, "cards": cards}
        if cmd == "snap":  # a DOSBox-X screenshot (Pause, mapper-nohost.map): no savestate is taken
            cap = self.d.workdir / "cap"
            before = set(cap.glob("*.png"))
            self.d._x("keydown", "Pause")
            time.sleep(driver.KEY_HOLD)  # key hold
            self.d._x("keyup", "Pause")
            end = time.monotonic() + 10
            new = []
            while time.monotonic() < end and not new:
                time.sleep(0.2)  # poll for the PNG, bounded by 10 s
                new = sorted(set(cap.glob("*.png")) - before)
            if not new:
                raise RuntimeError("no screenshot within 10 s")
            name = f"{self.n + 1:05d}-{req.get('label', 'snap')}.png"
            time.sleep(0.3)  # let DOSBox-X finish writing it
            shutil.copy(new[-1], self.kept / name)
            path = self.kept / name
            return {**self.log({"req": req, "png": name, "sha256": driver.sha256(path.read_bytes())}),
                    "screen": f"(screenshot {path})"}
        if cmd == "note":
            return {**self.log({"req": req}), "screen": ""}
        raise ValueError(f"unknown command {cmd}")

    def run(self):
        sc = self.d.launch(None)
        self.cur = sc.digest()
        self.log({"req": {"cmd": "launch", "config": self.d.config, "gl": [p.name for p in self.d.gl],
                          "display": self.d.display}, "digest": self.cur, "events": self.d.events})
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(sock_name(self.session))
        srv.listen(1)
        print(f"serving {self.session} on display {self.d.display}", flush=True)
        while True:
            conn, _ = srv.accept()
            with conn:
                data = b""
                while not data.endswith(b"\n"):
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                req = json.loads(data)
                if req["cmd"] == "stop":
                    self.log({"req": req})
                    conn.sendall(json.dumps({"stopped": True}).encode() + b"\n")
                    return
                try:
                    resp = self.handle(req)
                except Exception as e:  # noqa: BLE001 - reported to the client, the session goes on
                    resp = self.log({"req": req, "error": f"{type(e).__name__}: {e}"})
                    resp["screen"] = ""
                try:
                    conn.sendall(json.dumps(resp, ensure_ascii=False).encode() + b"\n")
                except OSError as e:  # the client went away (killed): the session goes on
                    self.log({"req": {"cmd": "client-gone"}, "error": f"{type(e).__name__}: {e}"})


def serve(a):
    s = Server(a.session, a.cycles, a.gl, a.mapper)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        s.run()
    finally:
        gone = s.d.terminate()
        s.log({"req": {"cmd": "terminated"}, "processes_gone": gone,
               "events_tail": s.d.events[-6:]})


def call(session, req, timeout=900):
    c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    c.settimeout(timeout)
    c.connect(sock_name(session))
    c.sendall(json.dumps(req).encode() + b"\n")
    data = b""
    while not data.endswith(b"\n"):
        chunk = c.recv(1 << 20)
        if not chunk:
            break
        data += chunk
    return json.loads(data)


def show(resp, quiet=False, marked=False):
    if "error" in resp:
        print("ERROR", resp["error"])
        return 1
    head = {k: resp.get(k) for k in ("n", "changed", "reads", "secs")}
    print(f"#{head['n']} changed={head['changed']} reads={head['reads']} secs={head['secs']} info={resp.get('info')}"
          + (f" met={resp['req'].get('met')}" if resp.get("req", {}).get("cmd") == "wait" else ""))
    if not quiet:
        mk = {int(k): v for k, v in (resp.get("marks") or {}).items()} if marked else {}
        r0, r1 = (int(x) for x in os.environ.get("G2P_ROWS", "0:25").split(":"))
        c0, c1 = (int(x) for x in os.environ.get("G2P_COLS", "0:80").split(":"))
        for r, line in enumerate(resp.get("screen", "").split("\n")):
            if not r0 <= r < r1:
                continue
            print(line[c0:c1])
            if r in mk:
                print(mk[r][c0:c1] + "   <highlight>")
    return 0


def watch(a):
    """Read the screen every `--every` seconds and answer the match prompts (F030's keys): the replay
    question `y` for the first `--replays` goals then `n`; "save this goal" `n`; a set-piece taker or
    captain prompt `c` (the computer's pick); the summary save `n`. Stops and prints the screen at the
    first screen that is not the live match or one of those prompts (half time, full time, an injury
    stop, the bench), or after `--timeout` seconds."""
    replays = a.replays
    end = time.monotonic() + a.timeout
    last_comment = None
    while time.monotonic() < end:
        resp = call(a.session, {"cmd": "show"})
        if "error" in resp:
            return show(resp)
        text = resp["screen"]
        rows = text.split("\n")
        comment = " / ".join(r[32:66].strip() for r in rows[1:4]) if len(rows) > 4 else ""
        if comment != last_comment and "spacebar-commentary" in text:
            score = [re.search(r"│\s*(\d+)│", rows[i]) for i in (1, 3)] if len(rows) > 3 else [None, None]
            score = [m.group(1) if m else "?" for m in score]
            if a.verbose or any(w in comment for w in ("GOAL", "INJUR", "BOOK", "SENT", "PENALTY", "TIME")):
                print(f"  [{score[0]}-{score[1]}] {comment}")
            last_comment = comment
        key = None
        if "Do you want an action replay" in text:
            key = "y" if replays > 0 else "n"
            replays -= key == "y"
        elif "Do you want to save this goal" in text:
            key = "y" if a.save_goals > 0 else "n"
            a.save_goals -= key == "y"
        elif "Please enter name of file" in text:
            key = "Return"  # the default name (G-<n>.HIL)
        elif "C-computer select" in text:
            key = "c"
        elif "Do you want to save the match summary" in text:
            key = "y" if a.save_summary else "n"
        elif "SUBSTITUTION" in rows[-1] and "press any key" in rows[-1]:
            key = "Return"  # the other side's substitution notice (it also leaves by itself)
        if key:
            if key == "Return":
                print(f"  notice: {rows[-1].strip()!r} -> Return")
                call(a.session, {"cmd": "send", "keys": [key], "timeout": 3})
                continue
            prompt = next((r.strip("■ ") for r in rows if "Do you want" in r or "C-computer" in r), "")
            print(f"  prompt: {prompt!r} -> {key}")
            call(a.session, {"cmd": "send", "keys": [key], "timeout": 3})
            continue
        if "spacebar-commentary" not in text and "REPLAY" not in text:
            return show(resp, marked=a.m)
        time.sleep(a.every)  # the read interval (each read is a savestate, which pauses the emulator)
    print("watch: timeout")
    return show(call(a.session, {"cmd": "show"}))


MENU = "play next game"


def kind(text):
    """A coarse name for the screen, from its fixed text (static/screens/kinds.tsv's phrases)."""
    last = text.rstrip("\n").split("\n")[-1]
    if "F10quit" in text and "find option" in text:
        return "manager-menu"
    if "Do you want to watch this match" in text:
        return "watch-prompt"
    if "C-computer select" in text:
        return "captain"
    if "Do you want to save the match summary" in text:
        return "summary-prompt"
    if "Do you want an action replay" in text or "Do you want to save this goal" in text:
        return "replay-prompt"
    if "Hit INS to turn automatic action replay" in text:
        if "FULL TIME" in text:
            return "match-menu-fulltime"
        return "match-menu"
    if "make substitutions now" in text or "substitution requested" in text or "request substitution" in text:
        return "bench"
    if "spacebar-commentary" in text:
        return "match-live"
    if "spacebar-pause" in text:
        return "round-playing"
    if "hit any key" in last or "press any key" in last.lower():
        if "MAN OF THE MATCH" in text or "half time" in text or "Scorers" in text:
            return "match-board"
        return "any-key"
    return "other"


def play_round(a):
    """One round from the manager menu to the manager menu: play next game, Return through the
    results, answer "watch this match" N for other fixtures, play our match as a quick result (Enter on
    play, Enter on the captain then R at once), space through the boards, exit, N to the summary,
    Return through the bulletins. Stops, printing the screen, at anything else (an injury, the bench,
    a screen it does not know) or at the end of the year's season pages it has not seen."""
    end = time.monotonic() + a.timeout
    started = False
    seen = []
    while time.monotonic() < end:
        resp = call(a.session, {"cmd": "show"})
        if "error" in resp:
            return show(resp)
        text = resp["screen"]
        k = kind(text)
        if not seen and k != "manager-menu":
            started = True  # called mid-round: finish this round only
        if not seen or seen[-1] != k:
            seen.append(k)
        if k == "manager-menu":
            if started:
                print(f"round done: {' > '.join(seen)}; info={resp['info']}")
                return show(resp, quiet=a.q)
            started = True
            r = call(a.session, {"cmd": "show"})
            # move to "play next game" and Enter
            for _ in range(8):
                rows = r["screen"].split("\n")
                hl = "".join("".join(ch for ch, mk in zip(rows[int(i)].ljust(80), m.ljust(80)) if mk == "^")
                             for i, m in (r.get("marks") or {}).items())
                if "play next" in hl:
                    break
                r = call(a.session, {"cmd": "send", "keys": ["Down"], "timeout": 3})
            call(a.session, {"cmd": "send", "keys": ["Return"], "timeout": 4})
            continue
        if k == "watch-prompt":
            ours = a.team.upper() in text.split("\n")[1].upper() or a.team.upper() in text.split("\n")[3].upper()
            print(f"  watch prompt (ours={ours}) -> n")
            call(a.session, {"cmd": "send", "keys": ["n"], "timeout": 4})
            continue
        if k == "match-menu":
            rows = text.split("\n")
            print(f"  match: {rows[1][12:28].strip('- ')} v {rows[3][12:28].strip('- ')} {rows[0][30:45].strip('─ ')}")
            if a.stop_at_match:
                return show(resp, quiet=a.q)
            r = resp
            for _ in range(8):
                hl = "".join("".join(ch for ch, mk in zip(r["screen"].split("\n")[int(i)].ljust(80), m.ljust(80)) if mk == "^")
                             for i, m in (r.get("marks") or {}).items())
                if "play" in hl:
                    break
                r = call(a.session, {"cmd": "send", "keys": ["Down"], "timeout": 3})
            call(a.session, {"cmd": "send", "keys": ["Return"], "timeout": 3})
            continue
        if k == "captain":
            call(a.session, {"cmd": "send", "keys": ["Return", "r"], "timeout": 3})
            continue
        if k == "match-board":
            rows = text.split("\n")
            print(f"  board: {rows[1][12:31].strip('- │')} {rows[3][12:31].strip('- │')} | {rows[3][32:66].strip()}")
            call(a.session, {"cmd": "send", "keys": ["space"], "timeout": 4})
            continue
        if k == "match-menu-fulltime":
            r = resp
            for _ in range(8):
                hl = "".join("".join(ch for ch, mk in zip(r["screen"].split("\n")[int(i)].ljust(80), m.ljust(80)) if mk == "^")
                             for i, m in (r.get("marks") or {}).items())
                if "exit" in hl:
                    break
                r = call(a.session, {"cmd": "send", "keys": ["Down"], "timeout": 3})
            call(a.session, {"cmd": "send", "keys": ["Return"], "timeout": 4})
            continue
        if k in ("summary-prompt", "replay-prompt"):
            call(a.session, {"cmd": "send", "keys": ["n"], "timeout": 4})
            continue
        if k == "any-key":
            rows = text.split("\n")
            head = " ".join(r.strip("─ │═║╔╗╚╝") for r in rows[8:12])[:90]
            print(f"  page: {head!r}")
            call(a.session, {"cmd": "send", "keys": ["Return"], "timeout": 4})
            continue
        if k in ("round-playing", "match-live"):
            time.sleep(1)  # results being played, or the quick result's HANG ON
            continue
        print(f"stopped at {k}: {' > '.join(seen)}")
        return show(resp, marked=a.m)
    print("round: timeout")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-m", action="store_true", help="mark the highlighted cells under each row")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("serve")
    p.add_argument("session")
    p.add_argument("--cycles", default="fixed 8000")
    p.add_argument("--gl", nargs="*", default=[])
    p.add_argument("--mapper", default=str(HERE / "mapper-nohost.map"),
                   help="the DOSBox-X mapper file (default mapper-nohost.map: savestate on Scroll Lock, "
                        "screenshot on Pause, no host key; '' for DOSBox-X's built-in binds and the F12 chords)")
    p = sub.add_parser("send")
    p.add_argument("session")
    p.add_argument("keys", nargs="+")
    p.add_argument("--timeout", type=float, default=8)
    p.add_argument("--gap", type=float, default=0)
    p.add_argument("--hold", type=float, default=0.08)
    p.add_argument("--blind", type=float, default=None, help="send without any savestate, then wait this many seconds")
    p.add_argument("-q", action="store_true")
    p = sub.add_parser("type")
    p.add_argument("session")
    p.add_argument("text")
    p.add_argument("--timeout", type=float, default=4)
    p.add_argument("-q", action="store_true")
    p = sub.add_parser("steps", help="several sends, each settled; prints the last screen")
    p.add_argument("session")
    p.add_argument("steps", nargs="+", help="each step: keys separated by spaces, e.g. 'Down Down' 'Return'")
    p.add_argument("--timeout", type=float, default=8)
    p.add_argument("-q", action="store_true")
    for name in ("show", "stop"):
        sub.add_parser(name).add_argument("session")
    p = sub.add_parser("wait")
    p.add_argument("session")
    p.add_argument("text")
    p.add_argument("--timeout", type=float, default=60)
    p.add_argument("--gone", action="store_true")
    p.add_argument("-q", action="store_true")
    p = sub.add_parser("checkpoint")
    p.add_argument("session")
    p.add_argument("label")
    p = sub.add_parser("note")
    p.add_argument("session")
    p.add_argument("text")
    p = sub.add_parser("watch", help="follow a watched match, answering its prompts")
    p.add_argument("session")
    p.add_argument("--replays", type=int, default=0, help="answer Y to this many replay questions")
    p.add_argument("--save-goals", type=int, default=0, help="answer Y to this many save-this-goal questions")
    p.add_argument("--save-summary", action="store_true", help="answer Y to the match summary question")
    p.add_argument("--every", type=float, default=1.0)
    p.add_argument("--timeout", type=float, default=560)
    p.add_argument("-v", dest="verbose", action="store_true", help="print every commentary change")
    p = sub.add_parser("round", help="one round as a quick result, from the manager menu back to it")
    p.add_argument("session")
    p.add_argument("--team", default="Holland")
    p.add_argument("--stop-at-match", action="store_true", help="stop at your match menu (to watch it)")
    p.add_argument("--timeout", type=float, default=500)
    p.add_argument("-q", action="store_true")
    p = sub.add_parser("advance", help="Return through 'hit any key' pages until a screen wants a choice")
    p.add_argument("session")
    p.add_argument("--timeout", type=float, default=300)
    p.add_argument("-q", action="store_true")
    p = sub.add_parser("select", help="press a key (Down) until WORD is highlighted, then Enter")
    p.add_argument("session")
    p.add_argument("word")
    p.add_argument("--key", default="Down")
    p.add_argument("--max", type=int, default=12)
    p.add_argument("--timeout", type=float, default=8)
    p.add_argument("--no-enter", action="store_true")
    p.add_argument("-q", action="store_true")
    p = sub.add_parser("find", help="press a key (Down) until the player card shows NAME")
    p.add_argument("session")
    p.add_argument("name")
    p.add_argument("--key", default="Down")
    p.add_argument("--max", type=int, default=100)
    p.add_argument("-q", action="store_true")
    p = sub.add_parser("scan", help="read n player cards of a list, pressing Down between them")
    p.add_argument("session")
    p.add_argument("n", type=int)
    p = sub.add_parser("snap", help="a DOSBox-X screenshot, no savestate (needs mapper-nohost.map)")
    p.add_argument("session")
    p.add_argument("label", nargs="?", default="snap")
    a = ap.parse_args(argv)
    if a.cmd == "serve":
        return serve(a)
    if a.cmd == "watch":  # follow a watched match, answering its prompts, until it needs a decision
        return watch(a)
    if a.cmd == "round":
        return play_round(a)
    if a.cmd == "advance":  # Return on every "hit any key" page, wait through the round being played
        end = time.monotonic() + a.timeout
        while time.monotonic() < end:
            resp = call(a.session, {"cmd": "show"})
            if "error" in resp:
                return show(resp)
            rows = resp["screen"].split("\n")
            last = rows[-1] if rows else ""
            if "hit any key" in last or "press any key" in last.lower():
                head = next((r.strip("─ │") for r in rows[6:12] if "BULLETIN" in r or "Group" in r), "")
                print(f"  #{resp['n']} hit any key {head[:40]!r} info={resp['info']}")
                call(a.session, {"cmd": "send", "keys": ["Return"], "timeout": 4})
                continue
            if "spacebar-pause" in resp["screen"]:
                time.sleep(1)  # the round's other matches are being played
                continue
            return show(resp, quiet=a.q, marked=a.m)
        print("advance: timeout")
        return 1
    if a.cmd == "select":  # move a menu's highlight onto a word, then (unless --no-enter) Enter
        for i in range(a.max + 1):
            resp = call(a.session, {"cmd": "show"} if i == 0 else {"cmd": "send", "keys": [a.key], "timeout": 4})
            if "error" in resp:
                return show(resp)
            rows = resp["screen"].split("\n")
            hit = False
            for r, m in (resp.get("marks") or {}).items():
                r = int(r)
                cells = "".join(ch for ch, mk in zip(rows[r].ljust(80), m.ljust(80)) if mk == "^")
                if a.word in cells:
                    hit = True
            if hit:
                print(f"{a.word!r} highlighted after {i} x {a.key}")
                if a.no_enter:
                    return show(resp, quiet=a.q)
                return show(call(a.session, {"cmd": "send", "keys": ["Return"], "timeout": a.timeout}), quiet=a.q)
        print(f"{a.word!r} not highlighted after {a.max} x {a.key}")
        return 1
    if a.cmd == "find":  # press a key until the player card (row 7) names the player
        key, turned = a.key, False
        for i in range(a.max + 1):
            resp = call(a.session, {"cmd": "show"} if i == 0 else {"cmd": "send", "keys": [key], "timeout": 2})
            if "error" in resp:
                return show(resp)
            rows = resp["screen"].split("\n")
            if len(rows) > 7 and rows[7][1:15].strip() == a.name:
                print(f"found {a.name} after {i} x {key}")
                return show(resp, quiet=a.q, marked=a.m)
            if i and resp.get("changed") is False:  # the list's end: lists do not wrap
                if turned:
                    break
                key, turned = {"Up": "Down", "Down": "Up"}[key], True
        print(f"{a.name} not found in {a.max} x {a.key}")
        return 1
    if a.cmd == "steps":
        for i, step in enumerate(a.steps):
            resp = call(a.session, {"cmd": "send", "keys": step.split(), "timeout": a.timeout})
            last = i == len(a.steps) - 1
            if "error" in resp or not last:
                show(resp, quiet=True)
            if "error" in resp:
                return 1
        return show(resp, quiet=a.q, marked=a.m)
    req = {"cmd": a.cmd}
    if a.cmd == "send":
        req.update(keys=a.keys, timeout=a.timeout, gap=a.gap, hold=a.hold)
        if a.blind is not None:
            req.update(blind=True, after=a.blind)
    elif a.cmd == "type":
        req.update(text=a.text, timeout=a.timeout)
    elif a.cmd == "wait":
        req.update(text=a.text, timeout=a.timeout, gone=a.gone)
    elif a.cmd == "checkpoint":
        req.update(label=a.label)
    elif a.cmd == "note":
        req.update(text=a.text)
    elif a.cmd == "snap":
        req.update(label=a.label)
    elif a.cmd == "scan":
        req.update(n=a.n)
    resp = call(a.session, req)
    if a.cmd == "scan":
        for i, c in enumerate(resp.get("cards", [])):
            if "error" in c:
                print(i, c["error"])
                continue
            sk = " ".join(f"{k[:3]}{v:2d}" for k, v in c["skills"].items())
            pn = " ".join(f"{k[:3]}:{v}" for k, v in c["panel"].items())
            print(f"{i:2d} {c['name']:14s} {c['age']:2d} {c['pos'][:18]:18s} {sk} | {pn} | {c['status']} {c['perf']}")
        return show(resp, quiet=True)
    if a.cmd == "stop":
        print(resp)
        return 0
    return show(resp, quiet=getattr(a, "q", False), marked=a.m)


if __name__ == "__main__":
    sys.exit(main())
