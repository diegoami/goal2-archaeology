#!/usr/bin/env python3
"""Decode the 32-byte set DS:0F3E with 23E4:08DF's rule (element n at bit n mod 8 of byte n div 8)
and print its members (T41, #127). Expected: {3, 4, 7, 8..203}."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEX = os.path.join(ROOT, "static", "goal-exe", "data", "ds_2581_01.hex")


def ds_bytes(path):
    mem = {}
    for line in open(path):
        m = re.match(r"^([0-9A-F]{4})\s+((?:[0-9A-F]{2} ?)+)", line)
        if m:
            base = int(m.group(1), 16)
            for i, b in enumerate(m.group(2).split()):
                mem[base + i] = int(b, 16)
    return mem


def members(path=HEX, off=0x0F3E):
    mem = ds_bytes(path)
    raw = [mem[off + i] for i in range(32)]
    return [n for n in range(256) if raw[n // 8] >> (n % 8) & 1]


def fmt(ms):
    """Elements below 8 (byte 0) listed singly, the rest as one run per contiguous stretch from 8."""
    low = [str(n) for n in ms if n < 8]
    hi, runs, i = [n for n in ms if n >= 8], [], 0
    while i < len(hi):
        j = i
        while j + 1 < len(hi) and hi[j + 1] == hi[j] + 1:
            j += 1
        runs.append(str(hi[i]) if i == j else "%d..%d" % (hi[i], hi[j]))
        i = j + 1
    return "{" + ", ".join(low + runs) + "}"


if __name__ == "__main__":
    out = fmt(members())
    print(out)
    sys.exit(0 if out == "{3, 4, 7, 8..203}" else 1)
