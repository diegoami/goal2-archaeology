#!/usr/bin/env python3
"""E032: what the committed match records actually hold, and whether every one conforms to record_schema.py
(PR 243 review round 3, issue 246: the schema is derived from the real records, not guessed).

    python3 -B experiments/E032-match-engine-inventory/derive_schema.py <out.txt>

Reads every JSON line of every out/*.jsonl (the match logs of timing.py, skip.py, pilot_movement.py), and
reports per field the types and ranges seen, split into completed and incomplete records: the statistics rows
by index (labels, value keys, addresses, value ranges) and the templates (ids, counts). Then validates every
record with record_schema.validate. Exits 1 when a committed record does not conform (the schema would be
too strict, or the record malformed), 0 otherwise. Refused if <out.txt> exists."""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import record_schema  # noqa: E402


def kind(v):
    return "bool" if isinstance(v, bool) else type(v).__name__


def main():
    dest = Path(sys.argv[1])
    if dest.exists():
        sys.exit(f"refused: {dest} exists")
    files = sorted(p for p in (HERE / "out").glob("*.jsonl"))
    seen = collections.defaultdict(set)
    rng = {}
    rows = collections.defaultdict(lambda: {"labels": set(), "keys": set(), "address": set(), "lo": None, "hi": None})
    tid, tcount = [], []
    n = collections.Counter()
    bad = []

    def span(key, v):
        lo, hi = rng.get(key, (v, v))
        rng[key] = (min(lo, v), max(hi, v))

    for p in files:
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if not line.strip():
                continue
            r = record_schema.loads(line)
            try:
                record_schema.validate(r)
            except record_schema.SchemaError as e:
                bad.append(f"{p.name}:{i}: {e}")
                continue
            done = record_schema.is_completed(r)
            n["completed" if done else "incomplete"] += 1
            tag = "completed" if done else "incomplete"
            for k, v in r.items():
                seen[(tag, k)].add(kind(v))
            span("seed", r["seed"])
            span(f"cpu_s ({tag})", r["cpu_s"])
            if not done:
                seen[("incomplete", "why")].add("error" if r["error"] else "not at board" if not r["stopped_at_board"]
                                                else "strays")
                continue
            for k in ("ticks", "draws"):
                span(k, r[k])
            for j, s in enumerate(r["score"]):
                span(f"score[{j}]", s)
            for j, row in enumerate(r["statistics_raw"]):
                d = rows[j]
                d["labels"].add(row["row_label"])
                d["keys"].add(tuple(sorted(row)))
                d["address"].add(row["address"])
                vals = row.get("raw_bytes") or row.get("raw_words")
                d["lo"] = min(vals) if d["lo"] is None else min(d["lo"], min(vals))
                d["hi"] = max(vals) if d["hi"] is None else max(d["hi"], max(vals))
            for k, v in r["templates"].items():
                tid.append(int(k))
                tcount.append(v)
    L = [f"# E032 committed match records: {len(files)} logs, {n['completed']} completed and "
         f"{n['incomplete']} incomplete records conform to record_schema.py; {len(bad)} do not", ""]
    L.append("## Fields and the JSON types seen")
    for (tag, k), types in sorted(seen.items()):
        L.append(f"- {tag} {k}: {', '.join(sorted(types))}")
    L.append("")
    L.append("## Ranges seen")
    for k, (lo, hi) in sorted(rng.items()):
        L.append(f"- {k}: {lo}..{hi}")
    L.append("")
    L.append("## statistics_raw by row")
    for j in sorted(rows):
        d = rows[j]
        L.append(f"- row {j}: labels {sorted(d['labels'])}; keys {sorted(d['keys'])}; addresses {sorted(d['address'])}; "
                 f"values {d['lo']}..{d['hi']}")
    L.append("")
    if tid:
        L.append(f"## templates: ids {min(tid)}..{max(tid)} ({len(set(tid))} distinct); counts {min(tcount)}..{max(tcount)}")
    L.append("")
    L.append("## Records that do not conform")
    L += [f"- {b}" for b in bad] or ["- none"]
    dest.write_text("\n".join(L) + "\n")
    print("\n".join(L[:1] + L[-max(1, len(bad)):]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
