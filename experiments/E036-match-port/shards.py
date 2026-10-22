#!/usr/bin/env python3
"""E036: split a family run into shards for GitHub Actions (.github/workflows/family-run.yml) and join them again.

    python3 -B experiments/E036-match-port/shards.py plan --family ALL [--only ID,...] --shards N
        prints the matrix: {"include": [{"shard": i, "only": "ID,ID"}, ...]}, each shard a run of consecutive matches
        in the family run's order, sizes differing by at most one (fewer shards when there are fewer matches)
    python3 -B experiments/E036-match-port/shards.py collect --family ALL [--only ID,...] --out FILE SHARD.jsonl...
        writes FILE: every selected match's line, as its shard wrote it, in the family run's order; refuses (exit 2)
        a match missing, twice, or not selected, and a line the record grammar refuses; FILE must not exist

The owner, 2026-10-22: a cloud container restarts often and runs a match 3-4x slower than the owner's machine, so the
integrated runs of the port PRs run on Actions runners, one shard per job (#361). A shard is an ordinary family.py run
(`--only` its matches), so its records are the ones a single run writes; collect only joins and checks them."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import families  # noqa: E402
import records  # noqa: E402


class Refused(Exception):
    pass


def selected_ids(family, only=None):
    """The match ids a family.py run with --family and --only selects, in its order."""
    ids = [m.id for fam in families.select(family, families.discover()) for m in fam.matches]
    if only is None:
        return ids
    wanted = only.split(",")
    unknown = [i for i in wanted if i not in ids]
    if unknown or len(set(wanted)) != len(wanted):
        raise Refused(f"--only {only!r}: distinct ids among the selected matches (unknown: {unknown})")
    return [i for i in ids if i in wanted]


def plan(ids, shards):
    """Consecutive runs of `ids`, as even as can be: [{"shard": i, "only": "ID,..."}]."""
    if shards < 1:
        raise Refused("--shards is 1 or more")
    n = min(shards, len(ids))
    out, start = [], 0
    for i in range(n):
        size = len(ids) // n + (1 if i < len(ids) % n else 0)
        out.append({"shard": i, "only": ",".join(ids[start:start + size])})
        start += size
    return out


def collect(ids, shard_paths, out):
    """Join the shards' lines into `out` in the order of `ids`; returns the number of lines written."""
    if Path(out).exists():
        raise Refused(f"{out}: exists (an output is never overwritten)")
    lines = {}
    for path in shard_paths:
        try:
            recs = records.read_log(path)
        except records.SchemaError as e:
            raise Refused(f"{path} is not a valid log: {e}")
        raw = [l for l in Path(path).read_text().splitlines() if l.strip()]
        for rec, line in zip(recs, raw):
            if rec["id"] not in ids:
                raise Refused(f"{path} holds {rec['id']}, which is not selected")
            if rec["id"] in lines:
                raise Refused(f"{rec['id']} is in two shards ({lines[rec['id']][0]} and {path})")
            lines[rec["id"]] = (path, line)
    missing = [i for i in ids if i not in lines]
    if missing:
        raise Refused(f"{len(missing)} selected matches are in no shard: {missing}")
    Path(out).write_text("".join(lines[i][1] + "\n" for i in ids))
    return len(ids)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--family", required=True)
    p.add_argument("--only")
    p.add_argument("--shards", type=int, required=True)
    c = sub.add_parser("collect")
    c.add_argument("--family", required=True)
    c.add_argument("--only")
    c.add_argument("--out", required=True)
    c.add_argument("shard", nargs="+")
    a = ap.parse_args(argv)
    try:
        ids = selected_ids(a.family, a.only)
        if a.cmd == "plan":
            print(json.dumps({"include": plan(ids, a.shards)}))
        else:
            n = collect(ids, a.shard, a.out)
            print(f"{n} matches from {len(a.shard)} shards in {a.out}")
    except (Refused, families.FamilyError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
