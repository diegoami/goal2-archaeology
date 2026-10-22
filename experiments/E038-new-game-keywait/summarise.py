#!/usr/bin/env python3
"""E038: the trace's reads against the DOSBox-X record's kept states, screen by screen.

    python3 experiments/E038-new-game-keywait/summarise.py runs/E038/E038-r0001.json experiments/E038-new-game-keywait/out/trace-r0001.json

For each kept state of the record that waits in 08DD's read: its site and callers (the record's frame) and its screen
(the record's text) against the trace's read at the same position in the order of the record's screens; the seed
words where the record holds them. Prints a table and exits 1 when any row differs."""
import json
import sys

ORDER = ["title-load-prompt", "title-player-count", "country-select", "after-name-1", "after-name-2", "manager-menu"]


def kept(record):
    out = {}
    for o in record["observations"]:
        name, _, what = o["field"].partition(": ")
        if what.startswith("text screen rows 0-24"):
            out.setdefault(name, {})["screen"] = o["value"]
        elif what.startswith("214B:08DD's frame"):
            out.setdefault(name, {})["frame"] = json.loads(o["value"])
        elif what.startswith("word at DS:7B62"):
            out.setdefault(name, {})["seed"] = o["value"].upper()
        elif what.startswith("word at DS:7B64"):
            out.setdefault(name, {})["seed2"] = o["value"].upper()
    return out


def main(argv):
    record, trace = (json.load(open(p, encoding="utf-8")) for p in argv[:2])
    states = kept(record)
    # the trace's reads, one per screen of ORDER: the reads of the name entry (214B:112B) are not a kept state
    reads = [e for e in trace["events"] if e["kind"] == "read" and e["site"] != "214B:112B"]
    bad = 0
    print("| screen | site (DOSBox-X) | site (trace) | callers equal | screen equal | DS:7B62 D / T | DS:7B64 D / T |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for name, ev in zip(ORDER, reads):
        st = states[name]
        callers = st["frame"]["callers"]
        site_d = callers[0]
        screen_eq = (ev.get("screen") == st["screen"]) if name != "manager-menu" else (trace["final_screen"] == st["screen"])
        callers_eq = callers[1:] == ev["callers"]
        same = site_d == ev["site"] and callers_eq and screen_eq
        bad += not same
        print(f"| {name} | {site_d} | {ev['site']} | {'yes' if callers_eq else 'NO'} | {'yes' if screen_eq else 'NO'} | "
              f"{st['seed']} / {ev['seed']} | {st['seed2']} / {ev['seed2']} |")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
