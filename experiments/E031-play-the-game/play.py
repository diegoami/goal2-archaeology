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
                conn.sendall(json.dumps(resp, ensure_ascii=False).encode() + b"\n")


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
        for r, line in enumerate(resp.get("screen", "").split("\n")):
            print(line)
            if r in mk:
                print(mk[r] + "   <highlight>")
    return 0


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
    p = sub.add_parser("snap", help="a DOSBox-X screenshot, no savestate (needs mapper-nohost.map)")
    p.add_argument("session")
    p.add_argument("label", nargs="?", default="snap")
    a = ap.parse_args(argv)
    if a.cmd == "serve":
        return serve(a)
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
    resp = call(a.session, req)
    if a.cmd == "stop":
        print(resp)
        return 0
    return show(resp, quiet=getattr(a, "q", False), marked=a.m)


if __name__ == "__main__":
    sys.exit(main())
