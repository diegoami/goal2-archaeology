#!/usr/bin/env python3
"""E005 (T12): F001's match probe re-run once at `max` with its own keys, and its polls read further.

    python3 experiments/E005-q003-cycles/probe_f001.py [--cycles max] [--reps 1]

Runs `runtime/spike/probe.py`'s `probe_match` unchanged (its states `title.sav` and `main.sav` under
.cache/states/, made by its own `make_states` at its default `cycles=auto` when absent, as F001 made
them; its keys: `c`, Right ×5 held 0.05 s, an Enter at every poll between HALF TIME and the team
screen, Down until ` play ` is highlighted, Enter). Two things differ from F001's run, neither a key:
- its output goes to this folder's `measurements/` (never over an earlier file: probe.free_path);
- each savestate its match loop reads is also decoded here for the BIOS ticks, the dword DS:A9FF, the
  delay byte [DS:A923]+0x3F and the commentary rows, kept in the row as `e005_polls` with the host
  seconds since this wrapper entered `play_to_full_time` (just before the probe's key `c`; the probe's
  own times start after that key's hold, 0.08 s later). The extra decoding runs after each read, so it
  adds host time between polls, not between a poll and its screen.
The states made here hold the game's memory and stay in .cache/ (git-ignored)."""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import commentary  # noqa: E402
import match  # noqa: E402
import savestate  # noqa: E402

_spec = importlib.util.spec_from_file_location("probe", ROOT / "runtime" / "spike" / "probe.py")
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)

A9FF = 0xA9FF  # seg_214B_04.asm:64-65 (the dword 214B:1DA7 stores)


def decode(data, since, n):
    """One poll's savestate: ticks, DS:A9FF, delay byte and commentary rows."""
    st = savestate.Savestate(data)
    out = {"poll": n, "since": since, "ticks": st.ticks()[0]}
    try:
        out["a9ff"] = int.from_bytes(st.ds_bytes(A9FF, 4), "little")
        out["delay"] = commentary.Snapshot(st).speed
    except ValueError as e:  # GOAL.EXE not located in this savestate
        out["a9ff"], out["delay"] = None, f"not read: {e}"
    out["rows"] = " / ".join(match.commentary_rows(savestate.Savestate(data).screen()))
    return out


def instrument():
    """Wrap probe.play_to_full_time so that every Session.screen() inside it is decoded too."""
    original_play, original_screen = probe.play_to_full_time, probe.dbx.Session.screen
    polls = None

    def screen(self):
        sc, data = original_screen(self)
        if polls is not None:
            polls.append(decode(data, round(time.monotonic() - polls_t0[0], 3), len(polls) + 1))
        return sc, data

    polls_t0 = [0.0]

    def play(s, row, timeout):
        nonlocal polls
        polls, polls_t0[0] = [], time.monotonic()
        try:
            return original_play(s, row, timeout)
        finally:
            row["e005_polls"], polls = polls, None

    probe.play_to_full_time = play
    probe.dbx.Session.screen = screen


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cycles", nargs="*", default=["max"])
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--timeout", type=float, default=180)  # probe.py's own default for `match`
    a = ap.parse_args(argv)
    probe.OUT = HERE / "measurements"
    instrument()
    probe.probe_match(argparse.Namespace(cycles=a.cycles, reps=a.reps, timeout=a.timeout, tag=""))
    print(json.dumps(probe.load_states()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
