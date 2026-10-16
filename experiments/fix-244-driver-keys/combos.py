#!/usr/bin/env python3
"""The combinations of E031's play.py key settings (--keys, --fkeys, --mapper), each launched once in the
emulator: after the title, `n` and F10, the BIOS keyboard flags and DS:A976 (what reached the game), and
whether the savestate reads worked at all. One JSON line per combination to --out.

    python3 experiments/fix-244-driver-keys/combos.py --out experiments/fix-244-driver-keys/out/combos.jsonl"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E031-play-the-game"))
import play  # noqa: E402

driver = play.driver
NOHOST = str(ROOT / "experiments" / "E031-play-the-game" / "mapper-nohost.map")
DOSBOX_DEFAULT = str(driver.xkeys.DEFAULT_MAP)  # the same binds as DOSBox-X's own, given as a file
COMBOS = [  # (name, PlayDriver arguments)
    ("default: --keys raw, mapper-nohost.map", dict(mapper=NOHOST)),
    ("--fkeys xdotool, mapper-nohost.map", dict(mapper=NOHOST, fkeys="xdotool")),
    ("--mapper '' --fkeys xdotool (the guide's reproduction)", dict(mapper="", fkeys="xdotool")),
    ("--keys xdotool --mapper '' (the old driver)", dict(mapper="", keys="xdotool")),
    ("--keys raw, a mapper file with the F12 chords", dict(mapper=DOSBOX_DEFAULT)),
    ("--keys xdotool, mapper-nohost.map", dict(mapper=NOHOST, keys="xdotool")),
]
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
a = ap.parse_args()
out = open(a.out, "w")
for name, kw in COMBOS:
    work = driver.SCRATCH / "combos"
    d = play.PlayDriver({"cycles": "fixed 8000"}, workdir=work, game_dir=work / "game", gl=[], **kw)
    row = {"combo": name, "hostkeys": d.hostkeys["s"]}
    try:
        d.launch(None)
        prev = d.screen().digest()
        d.keys("n")
        d.settle(prev, timeout=8)
        d.keys("F10")
        st = d.read()[1]
        f1, f2 = st.memory(0x417, 2)
        row.update({"0040:0017": f"{f1:08b}", "0040:0018": f"{f2:08b}", "alt_held": bool(f1 & 8 or f2 & 2),
                    "DS:A976": f"{st.ds_bytes(0xA976, 2)[0]:02x}", "reads_worked": True})
    except Exception as e:  # noqa: BLE001 - a combination whose reads fail is a finding, not a crash
        row.update({"reads_worked": False, "error": f"{type(e).__name__}: {e}"[:200]})
    finally:
        d.terminate()
    print(json.dumps(row))
    out.write(json.dumps(row) + "\n")
    out.flush()
