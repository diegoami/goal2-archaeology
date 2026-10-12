"""Count, in E011's recorded watched matches run unhooked, the entries of routines and their callers.

    python3 experiments/E021-m0-whole-match/reach.py 1771:377E [0791:BD03 ...]

For each record: how often each address is entered, and for the first address its calls broken
down by the far return address on the stack at entry (CS:IP of the call's next instruction). A
milestone's falsifier can stop only on a branch these matches reach (docs/lessons.md L105).
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


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    target, rest = argv[0], argv[1:]
    for p in sorted((HERE.parents[1] / "runs/E011").glob("E011-r*.json")):
        record = json.loads(p.read_text())
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        m = WatchedMatch(asset(entry))
        counts = Counter()
        callers = Counter()

        def at(address):
            def fn(uc, addr, size, data):
                counts[address] += 1
                if address == target:   # a far call: [SS:SP] = IP, [SS:SP+2] = CS
                    sp = m.reg("ss") * 16 + m.reg("sp")
                    ip, cs = (int.from_bytes(uc.mem_read(sp + k, 2), "little") for k in (0, 2))
                    callers[f"{cs:04X}:{ip:04X}"] += 1
            return fn

        for address in [target, *rest]:
            lin = m.lin(address)
            m.mu.hook_add(UC_HOOK_CODE, at(address), begin=lin, end=lin)
        m.run(timeout_s=1800)
        print(f"{record['run_id']}: ticks {m.final['ticks']}, score {m.final['score']}")
        for address in [target, *rest]:
            print(f"  {address} entered {counts[address]}")
        for ret, c in sorted(callers.items()):
            print(f"  {target} returns to {ret} (run-time CS:IP): {c}")


if __name__ == "__main__":
    main(sys.argv[1:])
