"""E024: the tables the lineup reads, in a running game (a savestate) against the data image of the unpacked file.

    python3 -B experiments/E024-computer-managers/check_tables.py

For each E010 half-time savestate compares DS:099A (14 x 8 bytes), DS:08D5 (14 x 14), DS:08CE (8 bytes) and the
three sets DS:693A / 695A / 697A (32 bytes each) with static/goal-exe/data/ds_2581_*.hex (what tables.py prints).
Prints one line per savestate and `tables equal: N/N`; exits non-zero on any difference.
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT / "experiments/E010-q010-quick-engine"))
import check_model  # noqa: E402
import savestate  # noqa: E402

img = {}
for fn in sorted(glob.glob(str(ROOT / "static/goal-exe/data/ds_2581_*.hex"))):
    for ln in open(fn):
        m = re.match(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)", ln)
        if m:
            a = int(m.group(1), 16)
            for i, b in enumerate(m.group(2).split()):
                img[a + i] = int(b, 16)
SPANS = {"DS:099A": (0x99A, 14 * 8), "DS:08D5": (0x8D5, 14 * 14), "DS:08CE": (0x8CE, 8),
         "DS:693A": (0x693A, 32), "DS:695A": (0x695A, 32), "DS:697A": (0x697A, 32)}
ok = n = 0
for p in sorted((ROOT / "runs/E010").glob("E010-r*.json")):
    record = json.loads(p.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
    st = savestate.Savestate(check_model.halftime_sav(entry))
    bad = [k for k, (a, ln) in SPANS.items() if bytes(st.ds_bytes(a, ln)) != bytes(img[a + i] for i in range(ln))]
    n += 1
    ok += not bad
    print(f"{record['run_id']}: {'equal' if not bad else 'DIFFERENT ' + ' '.join(bad)}")
print(f"tables equal: {ok}/{n}")
sys.exit(0 if ok == n else 1)
