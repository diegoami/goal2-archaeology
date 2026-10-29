"""T78d: run `family.py --family ALL --engine port --no-unicorn` as parallel chunks, then join them.

    python3 -B experiments/E036-match-port/out/T78/family_chunks_v1.py start --chunks 12 --tag port-v1
    python3 -B experiments/E036-match-port/out/T78/family_chunks_v1.py resume --tag port-v1
    python3 -B experiments/E036-match-port/out/T78/family_chunks_v1.py sync --tag port-v1 [--every 900]
    python3 -B experiments/E036-match-port/out/T78/family_chunks_v1.py join --tag port-v1

`start` splits the 75 admitted matches round-robin (the declared order) into --chunks disjoint `--only`
lists and starts one family.py per chunk through tools/heavy.sh (each holds one slot of
HARNESS_HEAVY_SLOTS, default 16 here), with the unchanged limits (300 s a match, 60 s a stretch).
Each chunk writes its own new `family-<tag>.part-<k>.jsonl` and log; the chunk lists are written
first to `family-<tag>.chunks.json`. `join` checks that the parts hold every match once, completed,
and writes `family-<tag>.jsonl` (new, never overwritten) with the records in the declared order;
the Done-when command run on it then finds every match present and validates each record itself
(family.py's resume check). A match that failed in its chunk is rerun alone into a new
`family-<tag>.rerun-<n>.jsonl`; `join` takes a rerun's completed record in place of the failed one,
keeps the failed one where it is, and lists every replacement in `family-<tag>.joined.json`.

`sync` commits and pushes the tag's chunk plan, parts and logs whenever they changed, every --every
seconds, until every chunk is complete and none runs (then once more): the records survive a lost
machine. Only those paths are staged; the commit says how many matches are recorded.

`resume` (after a crash, a reboot or a stop): every chunk whose part does not yet hold all its
matches and whose family.py is not running is started again with the same command, which skips
the matches already recorded (family.py's resumable --out): a match killed midway starts again
from its kick-off (family.py refuses --checkpoint with engine=port). Its log is a new
`part-<k>.r<n>.log`. A chunk counts as running when a family.py process writes its part (read from
/proc), whatever started it. Records are public digests (no original bytes): commit and push the
parts to keep them.
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


def launch(tag, k, chunk, slots, log_name):
    env = dict(os.environ, PYTHONPATH="runtime", HARNESS_HEAVY_SLOTS=str(slots))
    part = OUT / f"family-{tag}.part-{k}.jsonl"
    log = (OUT / log_name).open("x")
    cmd = ["tools/heavy.sh", f"t78d-{tag}-{k}", "--", sys.executable, "-B",
           "experiments/E036-match-port/family.py", "--family", "ALL", "--engine", "port", "--no-unicorn",
           "--only", ",".join(chunk), "--out", str(part.relative_to(ROOT))]
    p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True)
    (OUT / f".family-{tag}.part-{k}.pid").write_text(str(p.pid))
    print(f"chunk {k}: {len(chunk)} matches, pid {p.pid}, {part.name}, log {log_name}")


def start(args):
    order = ids()
    chunks = [order[k::args.chunks] for k in range(args.chunks)]
    plan = OUT / f"family-{args.tag}.chunks.json"
    with plan.open("x") as f:
        json.dump(dict(tag=args.tag, matches=len(order), chunks=chunks), f, indent=2)
    for k, chunk in enumerate(chunks):
        launch(args.tag, k, chunk, args.slots, f"family-{args.tag}.part-{k}.log")


def running(tag, k):
    """Whether any family.py process writes this chunk's part (its command line names it)."""
    part = f"family-{tag}.part-{k}.jsonl"
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            args = (proc / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        if any(a.endswith(b"family.py") for a in args) and any(a.decode(errors="replace").endswith(part) for a in args):
            return True
    return False


def recorded(tag, k):
    part = OUT / f"family-{tag}.part-{k}.jsonl"
    return {json.loads(l)["id"] for l in part.read_text().splitlines()} if part.exists() else set()


def sync(args):
    import time
    plan = json.loads((OUT / f"family-{args.tag}.chunks.json").read_text())
    while True:
        paths = [str(p.relative_to(ROOT)) for p in sorted(OUT.glob(f"family-{args.tag}.*"))
                 if not p.name.startswith(".")]
        subprocess.run(["git", "add", "--", *paths], cwd=ROOT, check=True)
        staged = subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT).returncode
        done = sum(len(recorded(args.tag, k) & set(c)) for k, c in enumerate(plan["chunks"]))
        if staged:
            subprocess.run(["git", "commit", "-q", "-m", f"T78d: {args.tag} family run, {done} of {plan['matches']} "
                            "matches recorded (sync)", "--", *paths], cwd=ROOT, check=True)
            subprocess.run(["git", "push", "-q"], cwd=ROOT, check=True)
            print(f"synced: {done} of {plan['matches']}", flush=True)
        finished = all(set(c) <= recorded(args.tag, k) or not running(args.tag, k) for k, c in enumerate(plan["chunks"]))
        if finished and not any(running(args.tag, k) for k in range(len(plan["chunks"]))):
            print("all chunks stopped", flush=True);return
        time.sleep(args.every)


def resume(args):
    plan = json.loads((OUT / f"family-{args.tag}.chunks.json").read_text())
    for k, chunk in enumerate(plan["chunks"]):
        done = recorded(args.tag, k)
        if set(chunk) <= done:
            print(f"chunk {k}: all {len(chunk)} recorded");continue
        if running(args.tag, k):
            print(f"chunk {k}: running, {len(done)} of {len(chunk)} recorded");continue
        n = 1
        while (OUT / f"family-{args.tag}.part-{k}.r{n}.log").exists():
            n += 1
        launch(args.tag, k, chunk, args.slots, f"family-{args.tag}.part-{k}.r{n}.log")


def join(args):
    import records  # family.py's own record rules
    order = ids()
    found, replaced = {}, []
    files = sorted(OUT.glob(f"family-{args.tag}.part-*.jsonl")) + sorted(OUT.glob(f"family-{args.tag}.rerun-*.jsonl"))
    for part in files:
        for line in part.read_text().splitlines():
            record = json.loads(line)
            key = record.get("id")
            if key in found:
                earlier = found[key][0]
                if records.is_completed(earlier) or ".rerun-" not in part.name or not records.is_completed(record):
                    raise SystemExit(f"{key} twice ({part.name}), not a completed rerun of a failed record")
                replaced.append(dict(id=key, failed_cpu_s=earlier.get("cpu_s"), failed_error=earlier.get("error"),
                                     rerun=part.name, rerun_cpu_s=record.get("cpu_s")))
            found[key] = (record, line)
    missing = [i for i in order if i not in found]
    failed = [i for i in order if i in found and not records.is_completed(found[i][0])]
    if missing or failed:
        raise SystemExit(f"not joined: missing {missing}, not completed {failed}")
    with (OUT / f"family-{args.tag}.jsonl").open("x") as f:
        for i in order:
            f.write(found[i][1] + "\n")
    with (OUT / f"family-{args.tag}.joined.json").open("x") as f:
        json.dump(dict(tag=args.tag, matches=len(order), files=[p.name for p in files], replaced=replaced), f, indent=2)
    print(f"joined {len(order)} records into family-{args.tag}.jsonl; replaced {[r['id'] for r in replaced]}")


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="action", required=True)
s = sub.add_parser("start");s.add_argument("--chunks", type=int, default=12);s.add_argument("--tag", required=True)
s.add_argument("--slots", type=int, default=16)
j = sub.add_parser("join");j.add_argument("--tag", required=True)
r = sub.add_parser("resume");r.add_argument("--tag", required=True);r.add_argument("--slots", type=int, default=16)
y = sub.add_parser("sync");y.add_argument("--tag", required=True);y.add_argument("--every", type=int, default=900)
a = ap.parse_args()
dict(start=start, join=join, resume=resume, sync=sync)[a.action](a)
