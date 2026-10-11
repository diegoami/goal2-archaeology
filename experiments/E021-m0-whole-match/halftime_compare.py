#!/usr/bin/env python3
"""Corroboration (not a Done-when): the first half, run as guest code from the captain screen,
reaches the state E011 saved at the half-time team-screen stall.

    python3 experiments/E021-m0-whole-match/halftime_compare.py

For each E011 record: emulate from its watchstart state until the harness delivers the team
screen's Enter (the `ED8A` read, notes.md §2), snapshot the 64 KiB data segment there, and compare
it byte by byte with the data segment of the record's half-time savestate (E011's stall, taken
inside the same wait). Prints and writes (under out/, never overwritten) the differing byte ranges."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402
from check import asset, write_out  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402


def ranges(diff):
    out = []
    for i in diff:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return ["%04X-%04X" % (a, b) if a != b else "%04X" % a for a, b in out]


def main():
    for p in sorted((ROOT / "runs/E011").glob("E011-r*.json")):
        record = json.loads(p.read_text())
        ws = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        ht = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
        m = WatchedMatch(asset(ws))
        snap = {}

        class Log(list):
            def append(self, e):
                super().append(e)
                if e[0].startswith("team screen"):
                    snap["ds"] = m.mem(m.DS * 16, 0x10000)
                    snap["clock_seed"] = (m.rd(0x831F), m.rd(0x831D), m.rd(0x7B62))
                    m.mu.emu_stop()

        m.key_log = Log()
        m.run()
        ref = savestate.Savestate(asset(ht))
        theirs = ref.ds_bytes(0, 0x10000)
        diff = [i for i in range(0x10000) if snap["ds"][i] != theirs[i]]
        ss_base = m.reg("ss") * 16 - m.DS * 16
        result = {"run_id": record["run_id"], "watchstart": ws, "halftime": ht,
                  "emulated_clock_and_seed_at_the_team_screen_read": snap["clock_seed"],
                  "savestate_clock_and_seed": (ref.ds_word(0x831F), ref.ds_word(0x831D), ref.ds_word(0x7B62)),
                  "differing_bytes": len(diff), "differing_ranges": ranges(diff),
                  "stack_segment_offset_in_DS": ss_base}
        print(f"{record['run_id']}: emulated (831F, 831D, 7B62) at the team screen's read {snap['clock_seed']},"
              f" E011 half-time state {result['savestate_clock_and_seed']}; data segment: {len(diff)} of 65536"
              f" bytes differ: {' '.join(result['differing_ranges'])} (SS starts at DS+0x{ss_base:X})")
        print(f"  {write_out('halftime-compare', record['run_id'], result).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
