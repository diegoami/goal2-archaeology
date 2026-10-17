#!/usr/bin/env python3
"""T59 (L105): count, on the unhooked kit (no port), what the throw-in 0791:6E11 reaches in each selected match, before
relying on it: its calls (6E11's entry), the calls that pass its jne (6E1B: the branch the falsifier
`restarts.side-swapped` changes, 6E26-6E2E, follows it on every pass), and the substitution notices 0791:7FCF reached
inside its call of 8062 (between 6E20, the call, and 6E23, its return), with the decisions the kit stopped for there.

    python3 -B experiments/E036-match-port/out/T59/count_throw_ins.py --family ALL --out <new .jsonl> [--only ID,...]

Raw code hooks added after the kit's own (as family.py --count): each execution counted once, the kit's replays not.
One JSON line per match: id, completed, the counts. Writes only --out, a new file."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036.parents[1] / "runtime"))
sys.path.insert(0, str(E036))
import families  # noqa: E402
import family  # noqa: E402
import records  # noqa: E402

ENTRY, PAST_JNE, CALL_8062, RETURN_8062, NOTICE = "0791:6E11", "0791:6E1B", "0791:6E20", "0791:6E23", "0791:7FCF"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only")
    ap.add_argument("--cache", default=family.DEFAULT_CACHE)
    a = ap.parse_args(argv)
    if Path(a.out).exists():
        print(f"refused: {a.out} exists")
        return 2
    selected = [m for fam in families.select(a.family, families.discover()) for m in fam.matches]
    if a.only:
        selected = [m for m in selected if m.id in a.only.split(",")]
    from unicorn import UC_HOOK_CODE
    from original_match import Image
    from original_match.assets import reference_image
    image = Image.from_bytes(reference_image(a.cache))
    totals = {}
    for spec in selected:
        c = {"calls": 0, "past_jne": 0, "notices_in_throw_in": 0, "decisions_in_throw_in": 0}
        state = {"inside": False, "m": None}

        def watch(m):
            state["m"] = m

            def hook(address, fn):
                lin = m.m.lin(address)
                m.m.uc.hook_add(UC_HOOK_CODE, lambda uc, addr, size, data: fn(), begin=lin, end=lin)
            hook(ENTRY, lambda: c.__setitem__("calls", c["calls"] + 1))
            hook(PAST_JNE, lambda: c.__setitem__("past_jne", c["past_jne"] + 1))
            hook(CALL_8062, lambda: state.__setitem__("inside", True))
            hook(RETURN_8062, lambda: state.__setitem__("inside", False))

            def notice():
                if state["inside"]:
                    c["notices_in_throw_in"] += 1
            hook(NOTICE, notice)
            events = m.events

            def counted():             # a decision event while inside the throw-in's 8062
                for ev in events():
                    if ev.kind == "decision" and state["inside"]:
                        c["decisions_in_throw_in"] += 1
                    yield ev
            m.events = counted
        rec = family.run_match(image, spec, watch=watch)
        line = {"id": spec.id, "completed": records.is_completed(rec), "score": rec["score"], **c}
        with open(a.out, "a") as f:
            f.write(json.dumps(line) + "\n")
        print(json.dumps(line), flush=True)
        for k, v in c.items():
            totals[k] = totals.get(k, 0) + v
    with_notice = sum(1 for line in open(a.out) if json.loads(line)["notices_in_throw_in"])
    print(f"{len(selected)} matches; totals {totals}; matches with a notice at a throw-in: {with_notice}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
