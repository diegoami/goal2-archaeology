"""Load the initialised data segment (DS offsets) from static/goal-exe/data/ds_2581_0*.hex; print ranges.
usage: python3 -B ds.py START END   (hex DS offsets); rows of 16 bytes."""
import re, sys, glob, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static", "goal-exe", "data")

def load():
    mem = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "ds_2581_0*.hex"))):
        prev = None
        for line in open(f):
            if line.startswith(";"):
                continue
            m = re.match(r"([0-9A-F]{4})\s+((?:[0-9A-F]{2} ){32})", line)
            if m:
                off = int(m.group(1), 16)
                row = bytes.fromhex(m.group(2).replace(" ", ""))
                prev = (off, row)
            elif line.startswith("*") and prev:
                pass
            if m:
                for i, b in enumerate(row):
                    mem[off + i] = b
        # '*' rows: repeats of the row above up to the next printed offset
    return mem

def load_full():
    mem = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "ds_2581_0*.hex"))):
        rows = []
        for line in open(f):
            if line.startswith(";"):
                continue
            if line.startswith("*"):
                rows.append(("*", None)); continue
            m = re.match(r"([0-9A-F]{4})\s+((?:[0-9A-F]{2} ){32})", line)
            if m:
                rows.append((int(m.group(1), 16), bytes.fromhex(m.group(2).replace(" ", ""))))
        for i, (off, row) in enumerate(rows):
            if off == "*":
                continue
            for k, b in enumerate(row):
                mem[off + k] = b
            j = i + 1
            if j < len(rows) and rows[j][0] == "*":
                # fill until next printed row
                k2 = j
                while k2 < len(rows) and rows[k2][0] == "*":
                    k2 += 1
                end = rows[k2][0] if k2 < len(rows) else off + 32
                o = off + 32
                while o < end:
                    for k, b in enumerate(row):
                        mem[o + k] = b
                    o += 32
    return mem

if __name__ == "__main__":
    mem = load_full()
    a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
    for o in range(a, b, 16):
        print("%04X  %s" % (o, " ".join("%02X" % mem[o + k] if o + k in mem else "--" for k in range(16))))
