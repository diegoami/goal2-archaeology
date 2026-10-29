"""T78d: run `family.py --family ALL --engine port --no-unicorn` as parallel chunks, then join them.

    python3 -B experiments/E036-match-port/out/T78/family_chunks_v1.py start --chunks 12 --tag port-v1
    python3 -B experiments/E036-match-port/out/T78/family_chunks_v1.py join --tag port-v1

`start` splits the 75 admitted matches round-robin (the declared order) into --chunks disjoint `--only`
lists and starts one family.py per chunk through tools/heavy.sh (each holds one slot of
HARNESS_HEAVY_SLOTS, default 16 here), with the unchanged limits (300 s a match, 60 s a stretch).
Each chunk writes its own new `family-<tag>.part-<k>.jsonl` and log; the chunk lists are written
first to `family-<tag>.chunks.json`. `join` checks that the parts hold every match once, completed,
and writes `family-<tag>.jsonl` (new, never overwritten) with the records in the declared order;
the Done-when command run on it then finds every match present and validates each record itself
(family.py's resume check). A match that failed in its chunk is not joined: rerun it in a new part.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "experiments/E036-match-port"), str(ROOT)]


def ids():
    import families
    return [m.id for fam in families.select("ALL", families.discover()) for m in fam.matches]


def start(args):
    order = ids()
    chunks = [order[k::args.chunks] for k in range(args.chunks)]
    plan = OUT / f"family-{args.tag}.chunks.json"
    with plan.open("x") as f:
        json.dump(dict(tag=args.tag, matches=len(order), chunks=chunks), f, indent=2)
    env = dict(os.environ, PYTHONPATH="runtime", HARNESS_HEAVY_SLOTS=str(args.slots))
    for k, chunk in enumerate(chunks):
        part = OUT / f"family-{args.tag}.part-{k}.jsonl"
        log = (OUT / f"family-{args.tag}.part-{k}.log").open("x")
        cmd = ["tools/heavy.sh", f"t78d-{args.tag}-{k}", "--", sys.executable, "-B",
               "experiments/E036-match-port/family.py", "--family", "ALL", "--engine", "port", "--no-unicorn",
               "--only", ",".join(chunk), "--out", str(part.relative_to(ROOT))]
        p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True)
        print(f"chunk {k}: {len(chunk)} matches, pid {p.pid}, {part.name}")


def join(args):
    import records  # family.py's own record rules
    order = ids()
    found = {}
    for part in sorted(OUT.glob(f"family-{args.tag}.part-*.jsonl")):
        for line in part.read_text().splitlines():
            record = json.loads(line)
            key = record.get("id")
            if key in found:
                raise SystemExit(f"{key} twice ({part.name})")
            found[key] = (record, line)
    missing = [i for i in order if i not in found]
    failed = [i for i in order if i in found and not records.is_completed(found[i][0])]
    if missing or failed:
        raise SystemExit(f"not joined: missing {missing}, not completed {failed}")
    with (OUT / f"family-{args.tag}.jsonl").open("x") as f:
        for i in order:
            f.write(found[i][1] + "\n")
    print(f"joined {len(order)} records into family-{args.tag}.jsonl")


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="action", required=True)
s = sub.add_parser("start");s.add_argument("--chunks", type=int, default=12);s.add_argument("--tag", required=True)
s.add_argument("--slots", type=int, default=16)
j = sub.add_parser("join");j.add_argument("--tag", required=True)
a = ap.parse_args()
start(a) if a.action == "start" else join(a)
