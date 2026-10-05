#!/usr/bin/env python3
"""Count, per code segment, the functions of static/goal-exe/decompiled/ that read Ghidra's unassigned
inputs (T18 rework, F009 O5).

    python3 tools/static/ghidra/count_inputs.py static/goal-exe/decompiled

An unassigned input is a name Ghidra gives a flag or register the function reads without having set
it: `in_CF`, `in_ZF` (flags), `in_AX`, `in_CX`, ... (registers). Read after a call, it often stands
for a value the callee returned in that flag or register, which the callee's prototype does not
declare: the decompiled view then shows the caller's input, not the callee's result. Per segment the
script prints how many functions read a flag input or a register input, and how many first read it
after a call in their body; then the functions of each "after a call" class.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

FLAG = re.compile(r"\bin_[A-Z]F\b")
REG = re.compile(r"\bin_(?:[ABCD][XLH]|SI|DI|BP|ES|DS)\b")
CALL = re.compile(r"\b(?:f|func)_[0-9A-F]{4}_[0-9A-F]{4}\(|\(\*")
DECL = re.compile(r"^\s+\w[\w ]*\*?\s+(?:in|unaff|extraout)_\w+;$")


def count(out: Path) -> tuple[dict[str, dict[str, int]], dict[str, list[str]]]:
    stats: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    after: dict[str, list[str]] = {"flag": [], "reg": []}
    for p in sorted(out.glob("seg_*.c")):
        seg = p.name[4:8]
        lines = p.read_text(encoding="utf-8").splitlines()
        heads = [i for i, l in enumerate(lines) if l.startswith("// ---- ")]
        for k, h in enumerate(heads):
            end = heads[k + 1] if k + 1 < len(heads) else len(lines)
            addr = lines[h].split()[2]
            stats[seg]["functions"] += 1
            # the body: from the line after the opening brace, declarations left out
            start = next(i for i in range(h, end) if lines[i] == "{") + 1
            body = [(i, lines[i]) for i in range(start, end) if not DECL.match(lines[i])]
            for kind, rx in (("flag", FLAG), ("reg", REG)):
                first = next((i for i, l in body if rx.search(l)), None)
                if first is None:
                    continue
                stats[seg][kind] += 1
                if any(CALL.search(l) for i, l in body if i < first):
                    stats[seg][kind + "_after_call"] += 1
                    after[kind].append(f"{addr} ({p.name}:{first + 1})")
    return stats, after


def main() -> int:
    stats, after = count(Path(sys.argv[1]))
    total: dict[str, int] = defaultdict(int)
    print("segment\tfunctions\tflag_input\tflag_after_call\treg_input\treg_after_call")
    for seg in sorted(stats):
        s = stats[seg]
        print(f"{seg}\t{s['functions']}\t{s['flag']}\t{s['flag_after_call']}\t{s['reg']}\t{s['reg_after_call']}")
        for k, v in s.items():
            total[k] += v
    print(f"all\t{total['functions']}\t{total['flag']}\t{total['flag_after_call']}\t{total['reg']}\t"
          f"{total['reg_after_call']}")
    for kind in ("flag", "reg"):
        print(f"{kind} input after a call: " + ", ".join(after[kind]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
