#!/usr/bin/env python3
"""T02: the other routes tried, behind the rows of findings/F001.

    python3 runtime/spike/routes.py [b-headless] [c-procmem] [f-png] [debugger]

b-headless: SDL dummy video driver, no X server; AUTOTYPE types the key from inside the guest;
            DOSBox-X's `autosave` writes savestates on a timer; the screens are read from them.
c-procmem:  the text screen found in DOSBox-X's own memory through /proc/<pid>/mem.
f-png:      DOSBox-X's PNG capture only (pixels, no text), hashed across launches.
debugger:   whether this build has the DOSBox-X debugger.
Writes runtime/spike/measurements/routes.json. Savestates stay in scratch/ (git-ignored)."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbx  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "goal2"
SCRATCH = ROOT / "scratch" / "routes"
OUT = Path(__file__).resolve().parent / "measurements"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def game_copy(name):
    d = SCRATCH / name / "game"
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(CACHE, d)
    return d


def b_headless(reps=3, wait=2, pace=0.5, seconds=14, every=2):
    """No Xvfb, no xdotool: SDL_VIDEODRIVER=dummy, `autotype -w <wait> -p <pace> n` before `goal`, and
    autosave every <every> s into slots 1-12. The run ends by DOSBox-X's own -time-limit."""
    rows = []
    for rep in range(reps):
        work = SCRATCH / f"b{rep}"
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        game = game_copy(f"b{rep}_game")
        conf = f"""[sdl]
output=surface
mapperfile={work}/mapper.map
[mixer]
nosound=true
[midi]
mididevice=none
[dosbox]
machine=svga_s3
memsize=16
saveremark=false
autosave={every} 1-12
[cpu]
cycles=auto
[autoexec]
mount c {game}
c:
autotype -w {wait} -p {pace} n
goal
exit
"""
        (work / "dosbox.conf").write_text(conf)
        env = {k: v for k, v in os.environ.items() if k != "DISPLAY"}
        env.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        t0 = time.monotonic()
        p = subprocess.run(["dosbox-x", "-conf", str(work / "dosbox.conf"), "-fastlaunch", "-nogui", "-nomenu",
                            "-savedir", str(work), "-time-limit", str(seconds)], env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=seconds + 30)
        elapsed = round(time.monotonic() - t0, 2)
        saves = sorted(work.glob("*.sav"), key=lambda f: f.stat().st_mtime)
        screens = []
        for f in saves:
            sc = dbx.read_screen_from_savestate(str(f))
            screens.append({"slot_file": f.name, "mtime_offset_s": round(f.stat().st_mtime - saves[0].stat().st_mtime, 1),
                            "digest": sc.digest(), "mode": list(sc.mode), "last_row": sc.text().split("\n")[-1].strip()[:70]})
        rows.append({"rep": rep, "return_code": p.returncode, "seconds": elapsed, "autosaves": screens})
        print("b-headless", rep, [(s["mtime_offset_s"], s["digest"][:6]) for s in screens])
    return {"setup": f"SDL_VIDEODRIVER=dummy, no DISPLAY; autotype -w {wait} -p {pace} n; autosave={every} 1-12; -time-limit {seconds}",
            "runs": rows}


def c_procmem(reps=2):
    """Read the text screen from DOSBox-X's heap. /usr/bin/dosbox-x carries file capability cap_net_raw, which makes
    the process non-dumpable (/proc/<pid>/maps: Permission denied); a copy without the capability is
    readable. The copy is made in scratch/ and is byte-identical to /usr/bin/dosbox-x."""
    res = {"capability": subprocess.run(["getcap", "/usr/bin/dosbox-x"], capture_output=True, text=True).stdout.strip(),
           "runs": []}
    exe = SCRATCH / "dosbox-x-nocap"
    SCRATCH.mkdir(parents=True, exist_ok=True)
    shutil.copy("/usr/bin/dosbox-x", exe)
    res["copy_sha256_equals_original"] = sha(exe.read_bytes()) == sha(Path("/usr/bin/dosbox-x").read_bytes())
    for label, binary in (("installed binary", "/usr/bin/dosbox-x"), ("copy without capability", str(exe))):
        for rep in range(reps):
            os.environ["DOSBOX_X"] = binary
            s = dbx.Session(SCRATCH / f"c_{label[:4]}{rep}", game_copy(f"c{label[:4]}{rep}_game"))
            row = {"binary": label, "rep": rep}
            try:
                s.start()
                s.wait_screen(lambda sc: "Do you want to load a saved game" in sc.text(), 30, "title")
                ref, _ = s.screen()
                pat = b"Do you want to load a saved game"
                found = None
                try:
                    with open(f"/proc/{s.dbx.pid}/maps") as m, open(f"/proc/{s.dbx.pid}/mem", "rb", 0) as mem:
                        t = time.monotonic()
                        for line in m:
                            rng, perms = line.split()[:2]
                            if not perms.startswith("rw"):
                                continue
                            lo, hi = (int(x, 16) for x in rng.split("-"))
                            if hi - lo > 512 << 20:
                                continue
                            try:
                                mem.seek(lo)
                                data = mem.read(hi - lo)
                            except (OSError, ValueError):
                                continue
                            for off in range(8):
                                j = data[off::8].find(pat)
                                if j >= 0:
                                    # the string is on text row 24 at column 20 (known from the savestate read)
                                    base = j * 8 + off - (24 * 80 + 20) * 8
                                    if 0 <= base <= len(data) - 2000 * 8:
                                        chars = bytes(data[base + 8 * i] for i in range(2000))
                                        attrs = bytes(data[base + 8 * i + 1] for i in range(2000))
                                        found = {"heap_region": line.split()[-1] if len(line.split()) > 5 else "anon",
                                                 "equals_savestate_read": chars == ref.chars and attrs == ref.attrs}
                                        if found["equals_savestate_read"]:
                                            break
                            if found and found["equals_savestate_read"]:
                                break
                        row["scan_seconds"] = round(time.monotonic() - t, 2)
                    row["read"] = found
                except PermissionError as e:
                    row["read"] = f"fails: {e}"
            except Exception as e:  # noqa: BLE001
                row["error"] = f"{type(e).__name__}: {e}"[:300]
            finally:
                s.stop()
                os.environ.pop("DOSBOX_X", None)
            res["runs"].append(row)
            print("c-procmem", row)
    return res


def f_png(reps=3, delay=3.0):
    """Pixels only: DOSBox-X's PNG capture at the title screen, three launches; and the file hash."""
    rows = []
    for rep in range(reps):
        s = dbx.Session(SCRATCH / f"f{rep}", game_copy(f"f{rep}_game"))
        try:
            s.start()
            time.sleep(delay)
            png = Path(s.capture_png())
            size, lit = dbx.lit_cells(str(png))
            _, _, px = dbx.png_pixels(str(png))
            pixhash = sha(b"".join(bytes(p) for row in px for p in row))
            rows.append({"rep": rep, "delay_s": delay, "png_sha256": sha(png.read_bytes()), "pixels_sha256": pixhash,
                         "size": list(size), "lit_cells": len(lit)})
        finally:
            s.stop()
        print("f-png", rows[-1])
    return {"runs": rows}


def debugger():
    out = subprocess.run(["strings", "/usr/bin/dosbox-x"], capture_output=True, text=True).stdout
    words = ["DEBUGBOX", "debugger", "Breakpoint", "breakpoint", "MEMDUMP", "Enter Debugger Command"]
    counts = {w: len(re.findall(re.escape(w), out)) for w in words}
    helps = subprocess.run(["dosbox-x", "-h"], capture_output=True, text=True)
    line = [l.strip() for l in (helps.stdout + helps.stderr).splitlines() if "break-start" in l]
    import pty
    import select
    work = SCRATCH / "dbg"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    game = game_copy("dbg_game")
    (work / "dosbox.conf").write_text(f"[sdl]\noutput=surface\nmapperfile={work}/mapper.map\n[mixer]\nnosound=true\n[midi]\nmididevice=none\n[autoexec]\nmount c {game}\nc:\ngoal\n")
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    pid, fd = pty.fork()
    if pid == 0:
        os.execvpe("dosbox-x", ["dosbox-x", "-conf", str(work / "dosbox.conf"), "-fastlaunch", "-nogui", "-nomenu",
                                "-break-start", "-time-limit", "12"], env)
    buf, t0 = b"", time.monotonic()
    while time.monotonic() - t0 < 9:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                buf += os.read(fd, 65536)
            except OSError:
                break
    os.kill(pid, 9)
    os.waitpid(pid, 0)
    text = buf.decode("latin1")
    return {"strings_counts_in_binary": counts, "help_line": line,
            "break_start_run": {"seconds": 9, "output_bytes": len(buf), "escape_sequences": text.count("\x1b["),
                                "lines_not_starting_with_LOG": [l[:80] for l in text.splitlines() if l.strip() and not l.startswith("LOG:")][:8]}}


def main():
    which = sys.argv[1:] or ["b-headless", "c-procmem", "f-png", "debugger"]
    git = lambda *x: subprocess.run(["git", "-C", str(ROOT), *x], capture_output=True, text=True).stdout.strip()  # noqa: E731
    res = {"dosbox-x": (subprocess.run(["dosbox-x", "-version"], capture_output=True, text=True).stderr or "").strip().splitlines()[:1],
           "code_commit": git("rev-parse", "--short", "HEAD"),
           "runtime_spike_uncommitted_changes": bool(git("status", "--porcelain", "--", "runtime/spike", ":!runtime/spike/measurements"))}
    for w in which:
        res[w] = {"b-headless": b_headless, "c-procmem": c_procmem, "f-png": f_png, "debugger": debugger}[w]()
    OUT.mkdir(exist_ok=True)
    p = OUT / "routes.json"
    text = json.dumps(res, indent=1, ensure_ascii=False) + "\n"
    p.write_text(text.replace(str(ROOT), "<repo>").replace(os.path.expanduser("~"), "~"), encoding="utf-8")
    print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
