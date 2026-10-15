"""Count T48 falsifier reach before running a falsified watched match.

The original runs unhooked; a code hook reads each helper's inputs at entry.
Stack arguments follow seg_214B_02.asm:560-588 (entry SP + 8/10 is a,
SP + 4/6 is b, before push bp). Registers follow seg_23E4_01.asm:273-290.
No original result or register is changed.
"""
import json
from collections import Counter
from pathlib import Path

from check import asset, longs, max_variant
from watched_match import WatchedMatch
from unicorn import UC_HOOK_CODE

HERE = Path(__file__).resolve().parent


def main():
    for path in sorted((HERE.parents[1] / "runs/E011").glob("E011-r*.json")):
        record = json.loads(path.read_text())
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        match = WatchedMatch(asset(entry))
        counts = Counter()

        def maximum(uc, address, size, data):
            stack = match.reg("ss") * 16 + match.reg("sp")
            words = [int.from_bytes(uc.mem_read(stack + k, 2), "little") for k in (8, 10, 4, 6)]
            a, b = tuple(words[:2]), tuple(words[2:])
            honest = longs.max_0d56(*words)
            counts["214B:0D56 calls"] += 1
            counts["0d56-min changes the result"] += max_variant(honest, a, b, "min") != (honest.ax, honest.dx)
            counts["0d56-lowword-signed changes the result"] += max_variant(honest, a, b, "lowword-signed") != (honest.ax, honest.dx)
            counts["0d56 high words differ"] += a[1] != b[1]

        def multiply(uc, address, size, data):
            ax, dx, bx, cx = [match.reg(r) for r in ("ax", "dx", "bx", "cx")]
            counts["23E4:0279 calls"] += 1
            counts["0279-product+1 changes the result"] += 1
            counts["0279-no-cross-term changes DX"] += (ax * bx) & 0xffff != 0
            counts["0279-scratch SI differs at entry"] += match.reg("si") != ax

        for address, callback in (("214B:0D56", maximum), ("23E4:0279", multiply)):
            linear = match.lin(address)
            match.mu.hook_add(UC_HOOK_CODE, callback, begin=linear, end=linear)
        match.run(timeout_s=7200)
        print(f"{record['run_id']}: original unhooked; ticks {match.final['ticks']}, score {match.final['score']}; stopped at board {match.stopped_at_board}", flush=True)
        print(dict(counts), flush=True)
        if not match.stopped_at_board:
            raise RuntimeError("reach run did not finish at the full-time board")


if __name__ == "__main__":
    main()
