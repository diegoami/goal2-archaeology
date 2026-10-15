#!/usr/bin/env python3
"""E032: the watched engine's size by part, from one coverage run (coverage.py's JSON).

    python3 -B experiments/E032-match-engine-inventory/analyze.py <coverage.json> <out.md>

Takes every routine that executed between kick-off and the end of the match (`exec_match` > 0) and puts it
in a PART by its address range in segment 0791 (the Pascal source keeps related routines together; the
ranges below are this script's judgment, made from the annotation names of static/goal-exe/annotations/
routines.tsv, and an unnamed routine takes its neighbours' part), with these overrides:
- UI: a routine that writes the text page, or whose name says it draws, shows, asks or waits; these are
  checked one by one by skip.py, not assumed;
- LIB: segments 214B and 23E4 (the runtime: RNG, sets, long arithmetic, screen primitives, the delay);
- 1771: by name (draw_*/performance_text = UI, the rest = player attributes).
Writes a markdown table (refused if it exists): per part, routines, static instructions, the share of
executed instructions, code bytes reached, how many routines carry a name, and how many are already
substituted exactly (MODELLED, from spec/match-engine.md's routine table and T42-T48)."""
import json
import sys
from pathlib import Path

PARTS = [  # (first, last, part) in segment 0791, inclusive offsets
    (0x0000, 0x0424, "UI: boards, scores"), (0x0425, 0x0444, "UI: delay, whistle"),
    (0x045D, 0x045D, "geometry and queries"), (0x0481, 0x15B8, "UI: boards, scores"),
    (0x15B9, 0x15B9, "UI: replay"), (0x1829, 0x1F3B, "commentary and ratings"),
    (0x1F3C, 0x2260, "marking and leaders"), (0x230C, 0x230C, "match frame"),
    (0x261A, 0x2F28, "geometry and queries"), (0x2F29, 0x418F, "ball, passing, shooting"),
    (0x419C, 0x4D3F, "positioning and marking movement"), (0x4D40, 0x5A8E, "decisions and contests"),
    (0x5A8F, 0x6336, "duels and play at the ball"), (0x6337, 0x7CC4, "goals, restarts, set pieces"),
    (0x7CC5, 0x82FF, "form, fouls, cards, substitutions"), (0x8300, 0x90FF, "ball and player motion, offside line"),
    (0x9100, 0x9371, "referee"), (0x9372, 0x94C8, "UI: key poll, in-match menu"),
    (0x94C9, 0x9563, "sound"), (0x9564, 0x9A80, "match frame"), (0x9A81, 0xC172, "set-up and computer manager"),
    (0xC173, 0xCC2D, "set-up and computer manager"), (0xCC2E, 0xFFFF, "UI: menus, captain screen"),
]
UI_PREFIXES = ("draw_", "show_", "ask_", "wait_")   # a prefix: draw_table_byte (261A) is a draw from a table, not drawing
UI_WORDS = ("menu", "performance_text", "snapshot", "replay")
# substituted exactly in whole matches (spec/match-engine.md routine table; T42-T48)
MODELLED = {"0791:278A", "1771:377E", "0791:287C", "214B:0688", "214B:06B1", "214B:06D0", "214B:06FA",
            "214B:0D1C", "214B:0D56", "1771:3A06"}


def part(r):
    seg, off = r["address"].split(":")
    off = int(off, 16)
    name = r["name"] or ""
    if seg in ("214B", "23E4"):
        return "LIB: runtime (RNG, sets, longs, screen, delay)"
    if r["video_bytes"] or name.startswith(UI_PREFIXES) or any(w in name for w in UI_WORDS):
        return "UI: draws or waits (skip.py checks)"
    if seg == "1771":
        return "player attributes (1771)"
    for lo, hi, p in PARTS:
        if lo <= off <= hi:
            return p
    return "unplaced"


def main():
    d = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    if out.exists():
        sys.exit(f"refused: {out} exists")
    rows = [r for r in d["routines"] if r["exec_match"] > 0]
    total = sum(r["instr_match"] for r in rows)
    agg = {}
    for r in rows:
        a = agg.setdefault(part(r), {"routines": 0, "instr": 0, "exec": 0, "reached": 0, "size": 0, "named": 0,
                                     "modelled": 0, "list": []})
        a["routines"] += 1
        a["instr"] += r["instructions_static"]
        a["exec"] += r["instr_match"]
        a["reached"] += min(r["bytes_reached"], r["size"])
        a["size"] += r["size"]
        a["named"] += bool(r["name"])
        a["modelled"] += r["address"] in MODELLED
        a["list"].append(r["address"][5:] if r["address"].startswith("0791") else r["address"])
    lines = [f"# E032 coverage by part: seed 0x{d['seed']:04x}, score {d['score']}, {d['ticks']} ticks, "
             f"{d['draws']} main-seed draws", "",
             f"Routines executed between kick-off and full time: {len(rows)}; executed instructions {total:,}.", "",
             "| part | routines | static instructions | executed share | code bytes reached | named | substituted exactly | routines |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    engine = {"routines": 0, "instr": 0, "named": 0, "modelled": 0}
    for p, a in sorted(agg.items(), key=lambda kv: (kv[0].startswith(("UI", "LIB", "sound")), kv[0])):
        lines.append(f"| {p} | {a['routines']} | {a['instr']:,} | {100 * a['exec'] / total:.1f}% | "
                     f"{100 * a['reached'] / a['size']:.0f}% | {a['named']} | {a['modelled']} | {' '.join(sorted(a['list']))} |")
        if not p.startswith(("UI", "LIB", "sound")):
            for k in engine:
                engine[k] += a[k]
    lines += ["", f"Engine parts (not UI, LIB or sound): {engine['routines']} routines, {engine['instr']:,} static "
              f"instructions, {engine['named']} named, {engine['modelled']} substituted exactly."]
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[-1:]))


if __name__ == "__main__":
    main()
