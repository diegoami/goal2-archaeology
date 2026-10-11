#!/usr/bin/env python3
"""Which engine reaches each match-time reader of player +0xC/+0xD/+0xE (E020 notes.md §2).

    python3 experiments/E020-q018-condition-performance/reach.py > experiments/E020-q018-condition-performance/reach-001.txt

Reads static/goal-exe/calls.tsv (direct near and far calls only: an indirect call or a jump table
would be invisible, a limit notes.md states). For each reader routine it prints, per engine root,
the callers of the reader that lie inside the root's call tree and the shortest chain from the root
to each. The roots are 0791:D733 (the quick engine, one call per minute) and 0791:9564 (the watched
engine's sweep). The pause/team screens - `0791:9372` (the key poll) and `0791:ED8A` (the half-time
and pause menu wait) - are cut from the trees and shown separately, because they draw the team
panels (1771:13D0, 1771:0BC4's callers 157D...) and are not match arithmetic."""
import sys
from collections import defaultdict, deque
from pathlib import Path

CALLS = Path(__file__).resolve().parents[2] / "static/goal-exe/calls.tsv"
READERS = ["1771:377E", "1771:0BC4", "0791:BD03", "0791:278A", "0791:287C", "0791:2B7B", "0791:4A28",
           "0791:5049", "0791:7CC5", "0791:7D56", "0791:8062", "0791:8AE9", "1771:3216", "0791:C88D",
           "1771:13D0", "0791:D47E", "0791:CB7D", "0791:D5C1"]
ROOTS = ["0791:D733", "0791:9564"]
CUT = {"0791:9372", "0791:ED8A"}

callers, callees = defaultdict(set), defaultdict(set)
for line in CALLS.read_text().splitlines():
    if line.startswith(";") or line.startswith("caller"):
        continue
    a, b, _ = line.split("\t")
    callers[b].add(a)
    callees[a].add(b)


def tree(root, cut):
    parent, queue = {root: None}, deque([root])
    while queue:
        x = queue.popleft()
        for y in sorted(callees[x]):
            if y not in cut and y not in parent:
                parent[y] = x
                queue.append(y)
    return parent


def chain(parent, node):
    out = []
    while node:
        out.append(node)
        node = parent[node]
    return " <- ".join(out)


for root in ROOTS:
    for cut, label in ((CUT, "pause screens cut"), (set(), "whole tree")):
        parent = tree(root, cut)
        print(f"ROOT {root} ({label}): {len(parent)} routines")
        for r in READERS:
            ins = [c for c in sorted(callers[r]) if c in parent]
            print(f"  {r}: callers inside the tree {ins if ins else 'none'}"
                  + (" (the routine itself is in the tree)" if r in parent else " (the routine is NOT in the tree)"))
            if cut:
                for c in ins:
                    print(f"      {chain(parent, c)}")
print("callers of the readers outside both trees (all of calls.tsv):")
for r in READERS:
    print(f"  {r}: {sorted(callers[r])}")
