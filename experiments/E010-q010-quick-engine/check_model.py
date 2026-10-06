#!/usr/bin/env python3
"""Check the quick-engine model against every E010 record (Done-when 2).

    python3 experiments/E010-q010-quick-engine/check_model.py [--runs runs/E010]

For each run record: take its half-time savestate (the output asset named by sha256, from
scratch/e010-halftime/ or downloaded from release E010), run runtime/model/quick_engine.py's
`simulate` on it, and print the model's and the original's final score, second-half goal minutes
(the goals 0791:6443 stored at DS:7BD1, minute byte with the 0x80 mark masked, minutes >= 46) and
the two seed words after the match. Ends with `match: N/N`; every record must match exactly."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT / "runtime/model"))
import driver  # noqa: E402
import quick_engine  # noqa: E402
import savestate  # noqa: E402

HALFTIME = ROOT / "scratch/e010-halftime"
DL = ROOT / ".cache/dl"


def halftime_sav(entry):
    """The half-time savestate an E010 record names, sha256-checked (downloaded when missing)."""
    local = HALFTIME / entry["name"]
    if not local.is_file() or driver.sha256(local.read_bytes()) != entry["sha256"]:
        asset = f"{entry['sha256'][:16]}-{entry['name']}"
        DL.mkdir(parents=True, exist_ok=True)
        path = DL / asset
        if not path.is_file():
            subprocess.run(["gh", "release", "download", "E010", "--repo", "diegoami/goal2-archaeology",
                            "--pattern", asset, "--dir", str(DL)], check=True)
        data = path.read_bytes()
        if driver.sha256(data) != entry["sha256"]:
            raise SystemExit(f"{path}: sha256 does not match the record's {entry['sha256']}")
        return data
    return local.read_bytes()


def originals(record):
    """The original's full-time score, second-half goals and seed words, from the record."""
    score = seeds = goals = None
    for o in record["observations"]:
        f = o.get("field", "")
        if f.startswith("full time: score bytes"):
            score = tuple(int(x) for x in o["value"].split()[-2:])
        elif f.startswith("full time: word at DS:7B62"):
            seeds = {"7B62": int(o["value"].split()[0], 16)}
        elif f.startswith("full time: word at DS:8336"):
            seeds["8336"] = int(o["value"].split()[0], 16)
        elif f.startswith("goals the engine stored"):
            goals = [[(w, m & 0x7F) for w, m in team] for team in json.loads(o["value"])]
    missing = [n for n, v in (("score", score), ("seeds", seeds), ("goals", goals)) if v is None]
    if missing:
        raise SystemExit(f"{record['run_id']}: the record lacks {missing}")
    second_half = [[(w, m) for w, m in team if m >= 46] for team in goals]
    return score, second_half, seeds


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs/E010"))
    a = ap.parse_args(argv)
    records = sorted(Path(a.runs).glob("E010-r*.json"))
    if not records:
        raise SystemExit(f"no records under {a.runs}")
    n = ok = 0
    for p in records:
        record = json.loads(p.read_text())
        entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
        state = savestate.Savestate(halftime_sav(entry))
        result = quick_engine.simulate(state)
        o_score, o_goals, o_seeds = originals(record)
        m_goals = [[(g["player"], g["minute"]) for g in result["goals"] if g["team"] == t] for t in (0, 1)]
        checks = {
            "score": (tuple(result["score"]), o_score),
            "goals": (m_goals, o_goals),
            "seed DS:7B62": (result["seed_DS7B62"], o_seeds["7B62"]),
            "seed DS:8336": (result["seed_DS8336"], o_seeds["8336"]),
        }
        good = all(m == o for m, o in checks.values())
        n += 1
        ok += good
        print(f"{record['run_id']} ({record['start_state']['id']}, {record['arm']}): "
              f"{'MATCH' if good else 'MISMATCH'}")
        for name, (m, o) in checks.items():
            mark = "=" if m == o else "!"
            print(f"    {name:13} {mark} model {m}  original {o}")
    print(f"match: {ok}/{n}")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
