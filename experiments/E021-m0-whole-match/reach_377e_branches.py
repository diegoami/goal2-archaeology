"""Which branches of 1771:377E (seg_1771_05.asm:763-824) E011's recorded watched matches take, run unhooked.

    python3 experiments/E021-m0-whole-match/reach_377e_branches.py

Code hooks inside the original routine, each at a listing line:
  379F `or al, al` after `call 3216`: AL != 0 is the unavailable exit (strength 0);
  37C8 `cmp byte ptr es:[di + 0xc], 0x20` (ES:DI the player record, from 37C5's les): the form branch,
       and the form values next to the threshold (0x1F, 0x20, 0x21);
  37E8 `cmp word ptr [bp - 4], 0`: the value before the clamp (below 0, above 0x100, exactly 0 or 0x100);
  3808 `or al, al` after `call 3179`: AL != 0 is the wrong-foot halving.
A falsifier of a branch can stop only if these matches take it (docs/lessons.md L105).
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check import asset  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402
from unicorn import UC_HOOK_CODE  # noqa: E402


def s8(b):
    return b - 0x100 if b & 0x80 else b


def s16(w):
    return w - 0x10000 if w & 0x8000 else w


def main():
    for p in sorted((HERE.parents[1] / "runs/E011").glob("E011-r*.json")):
        record = json.loads(p.read_text())
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        m = WatchedMatch(asset(entry))
        c = Counter()
        forms = Counter()

        def unavailable(uc, addr, size, data):           # 379F
            c["calls"] += 1
            c["unavailable" if m.reg("eax") & 0xFF else "available"] += 1

        def form(uc, addr, size, data):                  # 37C8
            f = s8(uc.mem_read(m.reg("es") * 16 + m.reg("edi") + 0xC, 1)[0])
            forms[f] += 1
            c["form >= 0x20 (v -= v idiv 16)" if f >= 0x20 else "form < 0x20 (v += form)"] += 1
            if f in (0x1F, 0x20, 0x21):
                c[f"form exactly 0x{f:02X}"] += 1

        def clamp(uc, addr, size, data):                 # 37E8
            v = s16(int.from_bytes(uc.mem_read(m.reg("ss") * 16 + m.reg("ebp") - 4, 2), "little"))
            c["below 0 (clamped to 0)" if v < 0 else "above 0x100 (clamped to 0x100)" if v > 0x100
              else "exactly 0 or 0x100" if v in (0, 0x100) else "inside 1..0xFF"] += 1

        def foot(uc, addr, size, data):                  # 3808
            c["wrong foot (halved)" if m.reg("eax") & 0xFF else "right foot"] += 1

        for off, fn in ((0x379F, unavailable), (0x37C8, form), (0x37E8, clamp), (0x3808, foot)):
            lin = m.lin(f"1771:{off:04X}")
            m.mu.hook_add(UC_HOOK_CODE, fn, begin=lin, end=lin)
        m.run(timeout_s=1800)
        print(f"{record['run_id']}: ticks {m.final['ticks']}, score {m.final['score']}")
        for k in sorted(c):
            print(f"  {k}: {c[k]}")
        print(f"  form values seen (signed): {dict(sorted(forms.items()))}")


if __name__ == "__main__":
    main()
