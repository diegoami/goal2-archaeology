#!/usr/bin/env python3
"""T02 probes behind findings/F001: determinism, speed, machines, writes, terminate, routes.

    python3 runtime/spike/probe.py <probe> [options]

Each probe launches DOSBox-X through dbx.Session (Xvfb + xdotool + savestate reads) unless it says
otherwise, and writes its raw measurements to runtime/spike/measurements/<probe>.json. Nothing here
interprets a screen; the finding does, citing these files. Savestates made here are the game's
memory: they go to .cache/states/ (git-ignored) and are never committed.

Every wait is a bounded poll for a screen (settle) or a delay that is written into the record."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbx  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "goal2"
STATES = ROOT / ".cache" / "states"
SCRATCH = ROOT / "scratch" / "probe"
OUT = Path(__file__).resolve().parent / "measurements"
TITLE = lambda sc: "Do you want to load a saved game" in sc.text()  # noqa: E731

# Key sequences. Each step is (key, wait): "settle" polls until the screen changed and two reads
# agree; a number is a recorded delay in seconds (used where the screen animates and never settles).
TO_MAIN = [("n", "settle"), ("Enter", "settle"), ("Enter", "settle"),
           ("b", "settle"), ("o", "settle"), ("b", "settle"),
           ("Enter", "settle"), ("Enter", "settle"), ("Enter", "settle"), ("Enter", "settle")]
SEQ_A = [("Esc", "settle"), ("Up", "settle"), ("Enter", "settle")]  # main menu -> play next game -> results of the other matches
SEQ_B = SEQ_A + [("Enter", "settle"), ("Enter", "settle"), ("c", 2.0), ("r", "settle"),
                 ("Enter", "settle"), ("Enter", "settle"), ("r", "settle")]  # ... -> match -> quick result -> bulletin
SEQ_MENU = [("Esc", "settle")]  # main menu with the next opponent shown


def sha(b):
    return hashlib.sha256(b).hexdigest()


_PATHS = {}  # name -> the file this process writes; a measurement file is never overwritten by a later run (L207)


def free_path(out, name):
    """<name>.json if no such file exists, else <name>-2.json, -3, ...: an earlier measurement is never replaced."""
    p, k = out / f"{name}.json", 2
    while p.exists():
        p, k = out / f"{name}-{k}.json", k + 1
    return p


def write_json(name, obj):
    OUT.mkdir(exist_ok=True)
    if name not in _PATHS:
        _PATHS[name] = free_path(OUT, name)
    p = _PATHS[name]  # the same run rewrites its own file as rows arrive
    text = json.dumps(obj, indent=1, ensure_ascii=False) + "\n"
    text = text.replace(str(ROOT), "<repo>").replace(os.path.expanduser("~"), "~")  # no host paths in committed files
    p.write_text(text, encoding="utf-8")
    print("wrote", p.relative_to(ROOT))


def versions():
    v = subprocess.run(["dosbox-x", "-version"], capture_output=True, text=True)
    git = lambda *x: subprocess.run(["git", "-C", str(ROOT), *x], capture_output=True, text=True).stdout.strip()  # noqa: E731
    return {"dosbox-x": (v.stdout + v.stderr).strip().splitlines()[0], "xdotool": subprocess.run(
        ["xdotool", "--version"], capture_output=True, text=True).stdout.strip(),
        "python": sys.version.split()[0], "code_commit": git("rev-parse", "--short", "HEAD"),
        "runtime_spike_uncommitted_changes": bool(git("status", "--porcelain", "--", "runtime/spike", ":!runtime/spike/measurements"))}


def fresh_game(name):
    # One fixed folder for every session: a DOSBox-X savestate keeps the host folder drive C: was mounted
    # from (F001), so restoring one in a session that mounted another folder would write to the old one.
    d = SCRATCH / "game"
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(CACHE, d)
    return d


def new_session(name, **cfg):
    game = fresh_game(name)
    return dbx.Session(SCRATCH / name / "dbx", game, **cfg), game


def settle(s, prev_digest, timeout=15):
    """Poll until the screen differs from prev_digest and two consecutive reads agree."""
    end = time.monotonic() + timeout
    last, polls = None, 0
    while time.monotonic() < end:
        polls += 1
        sc, _ = s.screen()
        d = sc.digest()
        if d != prev_digest and d == last:
            return sc, polls
        last = d if d != prev_digest else None
    raise RuntimeError(f"no settled change within {timeout}s")


def step(s, prev, key, wait):
    t = time.monotonic()
    s.key(key)
    if wait == "settle":
        sc, polls = settle(s, prev.digest())
        how = f"settle,{polls} polls"
    else:
        time.sleep(wait)
        sc, _ = s.screen()
        how = f"delay {wait}s"
    return sc, {"key": key, "wait": how, "seconds": round(time.monotonic() - t, 2),
                "mode": list(sc.mode), "digest": sc.digest(), "text": sc.text()}


def run_steps(s, start_screen, seq):
    out, prev = [], start_screen
    for key, wait in seq:
        try:
            prev, rec = step(s, prev, key, wait)
        except RuntimeError as e:
            raise RuntimeError(f"{e}; at step {len(out)}, key {key}; steps done: {[(r['key'], r['seconds']) for r in out]}; "
                               f"last screen head: {prev.text().splitlines()[:3]}") from None
        out.append(rec)
    return prev, out


def launch_to_title(s, timeout=30):
    s.start()
    sc, polls = s.wait_screen(TITLE, timeout, "title screen")
    return sc


def restore_verified(s, state_path, expect_digest, timeout=15):
    """Host+L loads the savestate; poll until the screen digest equals the one it was saved with."""
    shutil.copy(state_path, s.savefile)
    t = time.monotonic()
    s.restore(state_path)
    s.log("Host+L sent")
    end = time.monotonic() + timeout
    polls = 0
    while time.monotonic() < end:
        polls += 1
        sc, _ = s.screen()
        if sc.digest() == expect_digest:
            s.log(f"restored screen matched after {polls} polls")
            return sc, round(time.monotonic() - t, 2)
    raise RuntimeError("restored screen digest never matched")


def make_states():
    """title.sav (title screen) and main.sav (after TO_MAIN), under .cache/states/."""
    STATES.mkdir(parents=True, exist_ok=True)
    s, _ = new_session("states")
    try:
        sc = launch_to_title(s)
        shutil.copy(s.savefile, STATES / "title.sav")
        title = sc.digest()
        sc, _ = run_steps(s, sc, TO_MAIN)
        s.screen()
        shutil.copy(s.savefile, STATES / "main.sav")
        main = sc.digest()
    finally:
        s.stop()
    info = {"title": {"screen": title, "file_sha256": sha((STATES / "title.sav").read_bytes())},
            "main": {"screen": main, "file_sha256": sha((STATES / "main.sav").read_bytes())}}
    (STATES / "states.json").write_text(json.dumps(info, indent=1))
    return info


def load_states():
    p = STATES / "states.json"
    return json.loads(p.read_text()) if p.exists() else make_states()


def lines_differing(texts):
    """Row numbers whose text is not identical across all the given screen texts."""
    rows = [t.split("\n") for t in texts]
    n = max(len(r) for r in rows)
    return [i for i in range(n) if len({(r[i] if i < len(r) else "") for r in rows}) > 1]


# ---------------------------------------------------------------------------------------------
def probe_determinism(a):
    info = load_states()
    res = {"versions": versions(), "states": info, "reps": a.reps, "experiments": {}}

    # D0: fresh launch, the same keys, to the main menu: does the game's start differ per launch?
    runs = []
    for i in range(a.reps):
        s, _ = new_session(f"d0_{i}")
        try:
            sc = launch_to_title(s)
            sc, recs = run_steps(s, sc, TO_MAIN + SEQ_MENU)
            runs.append({"rep": i, "steps": recs, "events": s.events})
        finally:
            s.stop()
    res["experiments"]["D0_fresh_launch_same_keys_to_main_menu"] = summarise(runs)

    # D1..: restore main.sav in a fresh process, run a sequence, compare per step
    for name, seq in (("D1_restore_main_no_keys", []), ("D2_main_seqA_results_screen", SEQ_A),
                      ("D3_main_seqB_quick_result", SEQ_B)):
        runs = []
        for i in range(a.reps):
            s, _ = new_session(f"{name}_{i}")
            try:
                launch_to_title(s)
                sc, secs = restore_verified(s, STATES / "main.sav", info["main"]["screen"])
                sc, recs = run_steps(s, sc, seq)
                runs.append({"rep": i, "restore_seconds": secs, "start_digest": info["main"]["screen"],
                             "steps": recs, "events": s.events})
            finally:
                s.stop()
        res["experiments"][name] = summarise(runs)

    # D4: title.sav restored, typed keys to the main menu: does restoring the title state pin the start?
    runs = []
    for i in range(a.reps):
        s, _ = new_session(f"d4_{i}")
        try:
            launch_to_title(s)
            sc, secs = restore_verified(s, STATES / "title.sav", info["title"]["screen"])
            sc, recs = run_steps(s, sc, TO_MAIN + SEQ_MENU)
            runs.append({"rep": i, "restore_seconds": secs, "steps": recs, "events": s.events})
        finally:
            s.stop()
    res["experiments"]["D4_restore_title_same_keys_to_main_menu"] = summarise(runs)
    write_json("determinism" + a.tag, res)


def summarise(runs):
    n_steps = max((len(r["steps"]) for r in runs), default=0)
    per_step = []
    for k in range(n_steps):
        recs = [r["steps"][k] for r in runs if k < len(r["steps"])]
        digs = [x["digest"] for x in recs]
        per_step.append({"step": k, "key": recs[0]["key"], "digests": digs,
                         "identical": len(set(digs)) == 1,
                         "rows_differing": [] if len(set(digs)) == 1 else lines_differing([x["text"] for x in recs])})
    return {"runs": runs, "per_step": per_step,
            "final_identical": bool(per_step) and per_step[-1]["identical"]}


# ---------------------------------------------------------------------------------------------
def probe_speed(a):
    """cycles settings: seconds to the title screen, and seconds for the paced key sequence TO_MAIN + Esc,
    with the screen after it compared to the reference digest (the main menu seen at cycles=auto)."""
    info = load_states()
    ref = None
    res = {"versions": versions(), "settings": []}
    for cycles in a.cycles:
        row = {"cycles": cycles}
        s, _ = new_session(f"speed_{cycles.replace(' ', '_')}", cycles=cycles)
        try:
            t0 = time.monotonic()
            sc = launch_to_title(s)
            row["seconds_to_title_screen"] = round(time.monotonic() - t0, 2)
            row["title_digest_equals_reference"] = sc.digest() == info["title"]["screen"]
            t1 = time.monotonic()
            sc, recs = run_steps(s, sc, TO_MAIN)
            row["seconds_title_to_check_out_screen"] = round(time.monotonic() - t1, 2)
            row["check_out_digest_equals_reference"] = sc.digest() == info["main"]["screen"]
            row["step_seconds"] = [(r["key"], r["seconds"]) for r in recs]
        except Exception as e:  # noqa: BLE001
            row["error"] = f"{type(e).__name__}: {e}"[:700]
        finally:
            s.stop()
        res["settings"].append(row)
        print(row.get("cycles"), {k: v for k, v in row.items() if k != "step_seconds"})
    write_json("speed", res)


def play_to_full_time(s, row, timeout):
    """From the 'c' (computer select) screen: start the match, raise the game's speed (Right x5), and play both
    halves in real time until a screen holds FULL TIME. Fills `row` with the wall seconds of each phase."""
    s.key("c")
    t = time.monotonic()
    for _ in range(5):
        s.key("Right", hold=0.05)
    phase, polls = "first half", 0
    sc = None
    while time.monotonic() - t < timeout:
        polls += 1
        sc, _ = s.screen()
        tx = sc.text()
        now = round(time.monotonic() - t, 2)
        if phase == "first half" and "HALF TIME" in tx:
            row["half_time_after_s"] = now
            phase = "between halves"
        if phase == "between halves":
            if "location:" in tx:  # the team screen: move the bar to ' play ', then Enter
                if any(r[2].strip() == "play" for r in sc.highlighted()):
                    s.key("Enter")
                    row["second_half_started_after_s"] = now
                    phase = "second half"
                else:
                    s.key("Down")
            else:
                s.key("Enter")
        elif phase == "second half" and "FULL TIME" in tx:
            row["full_time_after_s"] = now
            phase = "done"
            break
    row["phase_at_end"] = phase
    row["polls"] = polls
    return sc


def probe_match(a):
    """A real-time (no R) match from main.sav at each cycles setting: wall seconds from the match start to a screen that
    holds HALF TIME and to one that holds FULL TIME, with the game's own speed raised (Right x5 after the start).
    Between the halves it presses Enter on the team screen, waits until ' play ' is the highlighted option, and Enter."""
    info = load_states()
    res = {"versions": versions(), "states": info, "rows": []}
    for cycles in a.cycles:
        for rep in range(a.reps):
            s, game = new_session(f"match_{cycles.replace(' ', '_')}_{rep}", cycles=cycles)
            tree_before = tree(game)
            row = {"cycles": cycles, "rep": rep}
            try:
                launch_to_title(s)
                sc, _ = restore_verified(s, STATES / "main.sav", info["main"]["screen"])
                sc, _ = run_steps(s, sc, SEQ_A + [("Enter", "settle"), ("Enter", "settle")])
                sc = play_to_full_time(s, row, a.timeout)
                phase = row["phase_at_end"]
                if phase != "done":
                    row["last_screen_head"] = sc.text().split("\n")[:5]
                if phase == "done":  # carry on, noting every prompt (does the game offer to save a goal or a summary?)
                    row["after_full_time"] = []
                    for _ in range(6):
                        s.key("Enter")
                        time.sleep(1.5)
                        sc, _ = s.screen()
                        row["after_full_time"].append({"first_row": sc.text().split("\n")[0][:60], "last_row": sc.text().split("\n")[-1][:80],
                                                       "prompt_words": [w for w in ("save", "Save", "goal", "summary", "replay") if w in sc.text()]})
                        if "SOCCER BULLETIN" in sc.text():
                            break
                if phase != "done":
                    row["last_screen_head"] = sc.text().split("\n")[:5]
                row["folder_changes"] = sorted(k for k, v in tree(game).items() if tree_before.get(k, {}).get("sha256") != v["sha256"])
            except Exception as e:  # noqa: BLE001
                row["error"] = f"{type(e).__name__}: {e}"[:700]
            finally:
                s.stop()
            res["rows"].append(row)
            print(row)
            write_json("match-speed" + a.tag, res)  # after every row, so an interrupted run keeps what it measured


# ---------------------------------------------------------------------------------------------
def tree(d):
    return {p.name: {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
            for p in sorted(Path(d).iterdir()) if p.is_file()}


def probe_writes(a):
    """File set of the game folder before and after sessions that save."""
    info = load_states()
    res = {"versions": versions(), "sessions": []}
    base = {p.name: sha(p.read_bytes()) for p in sorted(CACHE.iterdir())}

    def session(name, seq_keys, note, from_state=True):
        s, game = new_session(name)
        rec = {"session": name, "note": note, "before": tree(game)}
        try:
            launch_to_title(s)
            if from_state:
                sc, _ = restore_verified(s, STATES / "main.sav", info["main"]["screen"])
            else:
                sc = s.screen()[0]
            sc, _ = run_steps(s, sc, [("Esc", "settle")])
            for key, expect in seq_keys:
                if key.startswith("type:"):
                    for ch in key[5:]:
                        s.key(ch)
                        time.sleep(0.15)
                    time.sleep(0.3)
                    sc = s.screen()[0]
                    rec.setdefault("screens", []).append(sc.text().split("\n")[-1])
                    continue
                s.key(key)
                if expect == "EXIT":  # the game ends and DOSBox-X's `exit` follows: wait for the process, bounded
                    t = time.monotonic()
                    while s.dbx.poll() is None and time.monotonic() - t < 15:
                        time.sleep(0.1)
                    rec["exit_wait_seconds"] = round(time.monotonic() - t, 1)
                    rec.setdefault("screens", []).append("(process ended)" if s.dbx.poll() is not None else "(still running)")
                    continue
                end = time.monotonic() + 8
                while time.monotonic() < end:
                    sc, _ = s.screen()
                    if expect is None or expect in sc.text():
                        break
                else:
                    raise RuntimeError(f"{key}: did not see {expect!r}")
                rec.setdefault("screens", []).append(sc.text().split("\n")[-1])
            time.sleep(1.0)
            rec["after"] = tree(game)
            rec["dosbox_exited_by_itself"] = s.dbx.poll() is not None
            rec["exit_code"] = s.dbx.poll()
        except Exception as e:  # noqa: BLE001
            rec["error"] = f"{type(e).__name__}: {e}"[:700]
        finally:
            s.stop()
        rec["changed_or_new"] = sorted(k for k, v in rec.get("after", {}).items()
                                       if rec["before"].get(k, {}).get("sha256") != v["sha256"])
        rec["removed"] = sorted(set(rec["before"]) - set(rec.get("after", {})))
        res["sessions"].append(rec)
        print(name, rec["changed_or_new"], rec.get("error", ""))

    session("w0_no_save", [], "restore main.sav, Esc to the main menu, no save: folder after the session")
    session("w1_F7_default_name", [("F7", "name of saved game"), ("Enter", None)],
            "F7, accept the default name SAVED, continue playing")
    session("w2_F7_named", [("F7", "name of saved game"), ("type:zz", None), ("Enter", None)],
            "F7, type zz over the default name, Enter")
    session("w3_F10_save", [("F10", "Are you sure you want to quit"), ("y", "Do you want to save this game"),
                            ("y", "name of saved game"), ("Enter", "EXIT")],
            "F10, y (quit), y (save), default name; the game then ends and DOSBox-X's `exit` follows")
    session("w4_F10_nosave", [("F10", "Are you sure you want to quit"), ("y", "Do you want to save this game"),
                              ("n", "EXIT")],
            "F10, y (quit), n (do not save)")
    # w5: a watched match (no R) at cycles=10000, then y to the match-summary prompt and the default name
    s, game = new_session("w5_match_summary", cycles="10000")
    rec = {"session": "w5_match_summary", "note": "restore main.sav, play a match in real time at cycles=10000 (game speed x5), "
           "Enter after FULL TIME until the match-summary prompt, y, default name, Enter", "before": tree(game)}
    try:
        launch_to_title(s)
        sc, _ = restore_verified(s, STATES / "main.sav", info["main"]["screen"])
        sc, _ = run_steps(s, sc, SEQ_A + [("Enter", "settle"), ("Enter", "settle")])
        match = {}
        sc = play_to_full_time(s, match, 300)
        rec["match"] = match
        for i in range(8):
            s.key("Enter")
            time.sleep(1.5)
            sc, _ = s.screen()
            if "save the match summary" in sc.text():
                break
        else:
            raise RuntimeError("the match-summary prompt did not appear in 8 Enter presses")
        rec["prompt_rows"] = [r.strip() for r in sc.text().split("\n") if "Do you want" in r]
        s.key("y")
        time.sleep(1.5)
        sc, _ = s.screen()
        rec["name_prompt_row"] = sc.text().split("\n")[-1].strip()
        s.key("Enter")
        time.sleep(1.5)
        rec["after"] = tree(game)
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {e}"[:700]
    finally:
        s.stop()
    rec["changed_or_new"] = sorted(k for k, v in rec.get("after", {}).items() if rec["before"].get(k, {}).get("sha256") != v["sha256"])
    res["sessions"].append(rec)
    print("w5_match_summary", rec["changed_or_new"], rec.get("error", ""))
    res["release_files_unchanged_in_cache"] = (base == {p.name: sha(p.read_bytes()) for p in sorted(CACHE.iterdir())})
    write_json("writes", res)


# ---------------------------------------------------------------------------------------------
def probe_machines(a):
    """Machine types and memory: launch, the first screen by DOSBox-X's PNG capture (cell mask against
    the reference svga_s3 title screen), one keystroke, the PNG again."""
    res = {"versions": versions(), "rows": []}
    ref_mask = None
    for machine, mem in a.configs:
        row = {"machine": machine, "memsize": mem}
        s, _ = new_session(f"m_{machine}_{mem}", machine=machine, memsize=mem)
        try:
            s.start()
            time.sleep(a.delay)
            png = s.capture_png()
            size, lit = dbx.lit_cells(png)
            row["png_size"] = list(size)
            row["lit_cells_title"] = len(lit)
            if ref_mask is None and machine == "svga_s3":
                ref_mask = lit
            row["title_mask_equals_svga_s3"] = (lit == ref_mask) if ref_mask is not None else None
            s.key("n")
            time.sleep(a.delay)
            png2 = s.capture_png()
            size2, lit2 = dbx.lit_cells(png2)
            row["lit_cells_after_n"] = len(lit2)
            row["mask_changed_by_key"] = lit2 != lit
            row["alive"] = s.dbx.poll() is None
        except Exception as e:  # noqa: BLE001
            row["error"] = f"{type(e).__name__}: {e}"[:700]
        finally:
            s.stop()
        res["rows"].append(row)
        print(row)
    res["delay_seconds_before_capture"] = a.delay
    write_json("machines", res)


# ---------------------------------------------------------------------------------------------
def probe_layout(a):
    """Is the savestate layout (VGA_TEXT_BASE, MEM_HDR) the same on every machine type that gives a 720x400
    text screen, and for other memsize? Cells differing between the savestate read and DOSBox-X's PNG."""
    res = {"versions": versions(), "base": hex(dbx.VGA_TEXT_BASE), "mem_header": hex(dbx.MEM_HDR), "rows": []}
    for machine, mem in a.configs:
        row = {"machine": machine, "memsize": mem}
        s, _ = new_session(f"l_{machine}_{mem}", machine=machine, memsize=mem)
        try:
            launch_to_title(s)
            sc, _ = s.screen()
            png = s.capture_png()
            size, lit = dbx.lit_cells(png)
            cells = {(i // dbx.COLS, i % dbx.COLS) for i, c in enumerate(sc.chars) if c not in (0, 0x20)}
            row.update(png_size=list(size), mode=list(sc.mode), cells_differing=len(lit ^ cells),
                       screen_digest=sc.digest())
        except Exception as e:  # noqa: BLE001
            row["error"] = f"{type(e).__name__}: {e}"[:700]
        finally:
            s.stop()
        res["rows"].append(row)
        print(row)
    write_json("layout", res)


def probe_timing(a):
    """Does the delay between a restore and the first key change what follows? From main.sav, wait x seconds after
    the restore is verified, then the same keys (SEQ_A: Esc, Up, Enter = the results of the other matches)."""
    info = load_states()
    res = {"versions": versions(), "states": info, "rows": []}
    for x in a.delays:
        s, _ = new_session(f"tm_{x}")
        row = {"extra_wait_s": x}
        try:
            launch_to_title(s)
            sc, _ = restore_verified(s, STATES / "main.sav", info["main"]["screen"])
            s.log(f"extra wait {x}s")
            time.sleep(x)
            sc, recs = run_steps(s, sc, SEQ_A)
            row["digests"] = [r["digest"] for r in recs]
            row["results_screen_rows"] = [l for l in recs[-1]["text"].split("\n")[6:14]]
            row["events_tail"] = s.events[-6:]
        except Exception as e:  # noqa: BLE001
            row["error"] = f"{type(e).__name__}: {e}"[:700]
        finally:
            s.stop()
        res["rows"].append(row)
        print(x, row.get("digests"), row.get("error", ""))
        write_json("timing" + a.tag, res)


def probe_terminate(a):
    info = load_states()
    res = {"versions": versions(), "rows": []}
    # (1) the game's own quit; DOSBox-X's autoexec ends with `exit`
    s, _ = new_session("t_quit")
    row = {"route": "F10, y, n inside the game; autoexec `exit` follows"}
    try:
        launch_to_title(s)
        sc, _ = restore_verified(s, STATES / "main.sav", info["main"]["screen"])
        sc, _ = run_steps(s, sc, [("Esc", "settle")])
        for key in ("F10", "y", "n"):
            s.key(key)
            time.sleep(1.0)
        t = time.monotonic()
        while s.dbx.poll() is None and time.monotonic() - t < 15:
            time.sleep(0.1)
        row["exited_by_itself"] = s.dbx.poll() is not None
        row["exit_code"] = s.dbx.poll()
        row["seconds_after_last_key"] = round(time.monotonic() - t + 1.0, 1)
    except Exception as e:  # noqa: BLE001
        row["error"] = f"{type(e).__name__}: {e}"[:700]
    finally:
        s.stop()
    res["rows"].append(row)
    # (2) SIGTERM to the process group (what cycle.py does)
    s, _ = new_session("t_term")
    row = {"route": "SIGTERM to the dosbox-x and Xvfb process groups"}
    try:
        launch_to_title(s)
        t = time.monotonic()
        s.stop()
        row["seconds"] = round(time.monotonic() - t, 2)
        row["dosbox_return_code"] = s.dbx.returncode
        row["xvfb_return_code"] = s.xvfb.returncode
    finally:
        s.stop()
    res["rows"].append(row)
    write_json("terminate", res)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="probe", required=True)
    for name in ("determinism", "speed", "match", "writes", "machines", "terminate", "states", "layout", "timing"):
        p = sub.add_parser(name)
        p.add_argument("--reps", type=int, default=3)
        p.add_argument("--cycles", nargs="*", default=["auto", "max", "30000", "3000"])
        p.add_argument("--timeout", type=float, default=180)
        p.add_argument("--delays", type=float, nargs="*", default=[0, 0.3, 0.6, 0.9, 0, 0.3, 0.6, 0.9])
        p.add_argument("--delay", type=float, default=3.0)
        p.add_argument("--tag", default="", help="suffix for the measurement file name, e.g. -b for a second batch")
        p.add_argument("--configs", nargs="*", default=[])
    a = ap.parse_args()
    if a.probe == "layout" and not a.configs:
        a.configs = ["svga_s3:16", "svga_s3:8", "svga_s3:32", "vgaonly:16", "vgaonly:4", "svga_et4000:16"]
    if a.probe in ("machines", "layout"):
        a.configs = [tuple(c.split(":")[:1] + [int(c.split(":")[1])]) for c in
                     (a.configs or ["svga_s3:16", "vgaonly:16", "svga_et4000:16", "ega:16", "cga:16", "hercules:16",
                                    "tandy:16", "vgaonly:1", "vgaonly:2", "vgaonly:4"])]
    {"determinism": probe_determinism, "speed": probe_speed, "match": probe_match, "writes": probe_writes,
     "machines": probe_machines, "terminate": probe_terminate, "layout": probe_layout, "timing": probe_timing,
     "states": lambda a: print(json.dumps(make_states(), indent=1))}[a.probe](a)


if __name__ == "__main__":
    main()
