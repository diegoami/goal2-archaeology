"""Per routine of row T62: its port's calls per match (min-max and total, per family and in all), and whether they
equal the counted entries (--count) in every match. Counts of other addresses (the blocks, on an unhooked run) are
listed per address: the matches that reach it and its executions in all.

    python3 -B experiments/E036-match-port/out/T62/summary.py LOG [--blocks]"""
import sys

sys.path.insert(0, "experiments/E036-match-port")
import records  # noqa: E402

ROUTINES = ("835F", "83A2", "8537", "869F", "8AE9", "8C67", "8CCA", "8CF5", "8E24", "90C5", "9119")


def main(path, blocks=False):
    recs = records.read_log(path)
    print(f"{path}: {len(recs)} records")
    if blocks:
        addrs = sorted({a for r in recs for a in r["counts"]})
        for a in addrs:
            per = {r["id"]: r["counts"].get(a, 0) for r in recs}
            reached = [m for m, n in per.items() if n]
            fams = {}
            for m in reached:
                fams[m.split("/")[0]] = fams.get(m.split("/")[0], 0) + 1
            print(f"{a}: {sum(per.values())} executions in {len(reached)} of {len(recs)} matches "
                  f"({', '.join(f'{f} {n}' for f, n in sorted(fams.items())) or 'none'})")
        return 0
    ok = True
    for r in ROUTINES:
        a = f"0791:{r}"
        fams = {}
        for rec in recs:
            calls = rec["port_calls"].get(a)
            counted = rec["counts"].get(a)
            if calls != counted:
                ok = False
                print(f"{rec['id']}: port {a} called {calls}, entry counted {counted}: DIFFER")
            fams.setdefault(rec["id"].split("/")[0], []).append(calls)
        parts = [f"{f} {min(v)}-{max(v)} ({sum(v)})" for f, v in sorted(fams.items())]
        total = [c for v in fams.values() for c in v]
        print(f"{a}: per match {', '.join(parts)}; all {min(total)}-{max(total)}, {sum(total)} calls, "
              f"{sum(1 for c in total if c)} of {len(total)} matches call it")
    print("port calls equal the counted entries in every match" if ok else "port calls DIFFER from the counts")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], "--blocks" in sys.argv))
