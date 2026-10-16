#!/usr/bin/env python3
"""Issue 244: what reaches the guest from the driver's keys. One launch, a few keys, then F10, reading
the guest's BIOS keyboard flags (0040:0017, 0040:0018, 0040:0096) and the last key the game read
(DS:A976, scan + 0x64 for an extended key; lastkey.py of E031 reads the same) from the savestates the
driver takes anyway. Writes one JSON line per read to --out and prints a verdict line.

    python3 experiments/fix-244-driver-keys/probe.py --out experiments/fix-244-driver-keys/out/new.jsonl
    python3 experiments/fix-244-driver-keys/probe.py --driver-dir <old runtime/driver> --out ...
    python3 experiments/fix-244-driver-keys/probe.py --legacy --out ...     # the fixed driver's old keys

--driver-dir imports the driver from another folder (a copy of origin/main made before the fix, for the
fault's reproduction on the driver as it was). Exit 0 when no Alt was held at any read and F10 arrived as
F10 (DS:A976 = 0xA8, the word 0x4400 in the BIOS buffer, no 0x7100); exit 1 otherwise."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--driver-dir", default=str(ROOT / "runtime" / "driver"))
ap.add_argument("--out", required=True)
ap.add_argument("--legacy", action="store_true", help="Driver(legacy_keys=True, mapper=\"dosbox\"): the old keys and F12 chord on the fixed driver")
ap.add_argument("--workdir", default=None)
a = ap.parse_args()
sys.path.insert(0, a.driver_dir)
import driver  # noqa: E402
import savestate  # noqa: E402

# E031's start of a new game: the title's N, then Enter on the players, country and name screens.
KEYS = ["n", "Enter", "Enter", "Enter", "Enter", "Enter"]


def flags(state):
    """The BIOS keyboard state of a savestate. alt: Left or Right Alt held (0417 bit 3, 0418 bit 1, 0496 bit 3)."""
    f1, f2 = state.memory(0x417, 2)
    f3 = state.memory(0x496, 1)[0]
    a976 = state.ds_bytes(0xA976, 2)[0]
    bda = state.memory(0x41A, 0x24)
    words = [int.from_bytes(bda[4 + i:6 + i], "little") for i in range(0, 32, 2)]
    return {"0040:0017": f"{f1:08b}", "0040:0018": f"{f2:08b}", "0040:0096": f"{f3:08b}",
            "alt_held": bool(f1 & 8 or f2 & 2 or f3 & 8), "DS:A976": f"{a976:02x}",
            "buffer_words": [f"{w:04x}" for w in words]}


def main():
    work = Path(a.workdir) if a.workdir else driver.SCRATCH / "probe-244"
    kw = {"legacy_keys": True, "mapper": "dosbox"} if a.legacy else {}  # the old driver: xdotool and the F12 chord
    d = driver.Driver({"cycles": "fixed 8000"}, workdir=work, **kw)
    out = open(a.out, "w")
    rows = []

    def record(label, state):
        row = {"read": label, "driver": str(Path(a.driver_dir)), "legacy_keys": a.legacy, **flags(state)}
        rows.append(row)
        out.write(json.dumps(row) + "\n")
        out.flush()
        print(label, row["0040:0017"], row["0040:0018"], "alt" if row["alt_held"] else "no alt", "A976", row["DS:A976"])

    try:
        d.launch(None)
        record("launch: the savestate that showed the title", d.last[1])
        for k in KEYS:
            prev = d.screen().digest()
            d.keys(k)
            d.settle(prev, timeout=8, what=f"key {k}")
        record(f"after {' '.join(KEYS)}", d.last[1])
        d.keys("F10", hold=0.08)
        d.read()  # the savestate taken after F10 (the save key itself is the next read's)
        record("after F10 (first read)", d.last[1])
        d.read()
        record("after F10 (second read, after another save key)", d.last[1])
        out.write(json.dumps({"events_tail": d.events[-12:]}) + "\n")
    finally:
        d.terminate()
        out.close()
    last = rows[-1]
    ok = (not any(r["alt_held"] for r in rows) and last["DS:A976"] == "a8"
          and "4400" in last["buffer_words"] and "7100" not in last["buffer_words"])
    print("VERDICT", "no Alt held, F10 arrived as F10" if ok else
          "FAULT: Alt held at " + str([r["read"] for r in rows if r["alt_held"]]) + f", F10 read as DS:A976={last['DS:A976']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
