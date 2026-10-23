#!/usr/bin/env python3
"""E039: a date's trace (trace.py) against the DOSBox-X record of the same DOS date, screen by screen.

    python3 experiments/E039-start-year/summarise.py runs/E039/E039-r0001.json experiments/E039-start-year/out/trace-1990.json

For each kept read state of the record, in E038's order: the site and callers, the screen, DS:A9FD (the DOS year),
DS:7B62 and DS:7B64 (F004), and from the manager menu's state the game record's +0x38..+0x41 (start year +0x3A,
stage +0x3C, +0x40); these must be equal (exit 1 otherwise), and the trace must hold exactly one read per screen of
ORDER, the last at the manager menu: a read missing or one more fails (#378). DS:A9FF (the start-up's delay calibration) and DS:8336
(the BIOS tick read at 0791:F3F2) are printed, not required equal: the trace's come from derive.py's modelled tick."""
import json
import sys

ORDER = ["title-load-prompt", "title-player-count", "country-select", "after-name-1", "after-name-2", "manager-menu"]


def kept(record):
    out = {}
    for o in record["observations"]:
        name, _, what = o["field"].partition(": ")
        st = out.setdefault(name, {})
        if what.startswith("text screen rows 0-24"):
            st["screen"] = o["value"]
        elif what.startswith("214B:08DD's frame"):
            st["frame"] = json.loads(o["value"])
        elif what.startswith("word at DS:"):
            st[what[len("word at DS:"):len("word at DS:") + 4]] = o["value"].upper()
        elif what.startswith("the game record"):
            st["game_38_41"] = o["value"]
    return out


def main(argv):
    record, trace = (json.load(open(p, encoding="utf-8")) for p in argv[:2])
    states = kept(record)
    reads = [e for e in trace["events"] if e["kind"] == "read" and e["site"] != "214B:112B"]
    bad = 0
    if len(reads) != len(ORDER):           # zip() below would stop at the shorter list and pass a truncated replay
        print(f"the trace holds {len(reads)} reads outside the name entry, not {len(ORDER)} (one per screen of ORDER)")
        bad += 1
    print("| screen | site D / T | callers | screen | DS:A9FD D / T | DS:7B62 D / T | DS:7B64 D / T | game +38..+41 D / T | DS:A9FF D / T | DS:8336 D / T |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, ev in zip(ORDER, reads):
        st = states[name]
        callers = st["frame"]["callers"]
        screen_t = ev.get("screen") if name != "manager-menu" else trace["final_screen"]
        eq = {"site": callers[0] == ev["site"], "callers": callers[1:] == ev["callers"], "screen": screen_t == st["screen"],
              "A9FD": st["A9FD"] == ev["A9FD"], "7B62": st["7B62"] == ev["seed"], "7B64": st["7B64"] == ev["seed2"],
              "game": st.get("game_38_41") == ev.get("game_38_41")}
        bad += not all(eq.values())
        yn = lambda k: "yes" if eq[k] else "NO"  # noqa: E731
        print(f"| {name} | {callers[0]} / {ev['site']} | {yn('callers')} | {yn('screen')} | {st['A9FD']} / {ev['A9FD']} | "
              f"{st['7B62']} / {ev['seed']} | {st['7B64']} / {ev['seed2']} | {st.get('game_38_41', '—')} / {ev.get('game_38_41', '—')} | "
              f"{int(st['A9FF'], 16)} / {ev['A9FF']} | {st['8336']} / {ev['8336']} |")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
