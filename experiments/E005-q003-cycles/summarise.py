#!/usr/bin/env python3
"""E005 (T12, Q003): tabulate the records of runs/E005 and F001's probe re-run. Interprets nothing
beyond the recorded values.

    python3 experiments/E005-q003-cycles/summarise.py [runs/E005]

1. Calibration: DS:A9FF at the title screen per fresh launch, per `cycles` setting.
2. Runs: per match record the start route (restore of a state, or a fresh launch at its DOS time),
   `cycles`, arm, final score (the full-time scoreboard), events, DS:7B62 at full time and DS:A9FF,
   and its verdict against the same state's and arm's first completed restore at 30000 (`compare`):
   DIFFERS, IDENTITY UNDETERMINED (a reader flag marks a line it never read), or "no observed difference"
   (the same score, DS:7B62 and DS:80EE at full time, and every commentary occurrence both readers saw
   equal; completeness of the commentary is not claimed, issue #40);
   then the counts of each verdict.
3. Halves: for every watched run, the host seconds from the starting burst to the first read whose
   commentary rows hold HALF TIME, from there to the first read holding FULL TIME, and from the
   half-time team-screen Enter to FULL TIME; the guest seconds of the first and second half from the
   BIOS ticks; the ratio first half / second half (host, from the team-screen Enter); whether F001's
   unequal halves reproduce at `max` (ratio under UNEQUAL).
4. Cycles in effect after a restore: the guest seconds of the first half against the same state's and
   arm's 30000 restores (the restored DS:A9FF is fixed, so a busy-wait's guest time scales as 1/cycles).
5. F001's probe re-run (`measurements/match-speed*.json`): its halves, and per poll the BIOS ticks,
   DS:A9FF and the delay byte.
6. Checks: every record names its `cycles` setting (an observation, the fingerprint and the arm agree),
   and every record that sets the DOS clock declares I3. Exit 1 when a check fails."""
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNS = ROOT / "runs" / "E005"
TICKS_PER_S = 1193182 / 65536   # the PIT's 1.193182 MHz over 65536: 18.2065 BIOS ticks per second
# [designed] F001's halves (first / second, host s; second from the team-screen Enter, M:match-speed):
# 0.10 and 0.14 at 60000 and max, 0.93 ... 0.96 at auto, 5000, 10000 and 30000. Under 0.5 is unequal.
UNEQUAL = 0.5
REFERENCE_CYCLES = "30000"
CYCLES_FIELD = "cycles setting of the session"


def field(rec, start, step=None):
    for o in rec["observations"]:
        if o["field"].startswith(start) and (step is None or o["step"] == step):
            return o["value"]
    return None


def fields(rec, contains):
    """{label: value} of every observation whose field holds `contains` after `<label>: `."""
    out = {}
    for o in rec["observations"]:
        if contains in o["field"] and ": " in o["field"]:
            out[o["field"].split(": ", 1)[0]] = o["value"]
    return out


def scoreboard(text):
    """('DENMARK', 0, 'ENGLAND', 2) from rows 1 and 3 of the match screen (columns 13-27 the team, 29-30 the goals)."""
    rows = text.split("\n")

    def side(r):
        line = rows[r].ljust(40) if r < len(rows) else " " * 40
        return line[13:28].rstrip("-").strip(), int(line[29:31]) if line[29:31].strip().isdigit() else None
    a, b = side(1), side(3)
    return a[0], a[1], b[0], b[1]


def config_sets_clock(rec):
    """True when the session's autoexec set the DOS date or time (a `date MM/DD/YYYY` or `time HH:MM:SS`
    line in the config the record carries)."""
    conf = field(rec, "DOSBox-X config of the session") or ""
    return any(l.startswith(("date ", "time ")) and "/t" not in l for l in conf.splitlines())


def check(rec):
    """Problems with one record: its `cycles` setting not named, or named inconsistently; the clock set
    without I3 declared."""
    out = []
    rid = rec.get("run_id", "?")
    named = field(rec, CYCLES_FIELD)
    fp = rec.get("runtime", {}).get("fingerprint", {}).get("cycles")
    conf = field(rec, "DOSBox-X config of the session") or ""
    in_conf = [l.split("=", 1)[1] for l in conf.splitlines() if l.startswith("cycles=")]
    if not named:
        out.append(f"{rid}: no observation names the cycles setting")
    elif fp != named or in_conf != [named] or not rec.get("arm", "").endswith(f"cycles-{named}"):
        out.append(f"{rid}: cycles named {named!r}, fingerprint {fp!r}, config {in_conf}, arm {rec.get('arm')!r} disagree")
    if config_sets_clock(rec) and not any(i.get("level") == "I3" for i in rec.get("interventions", [])):
        out.append(f"{rid}: the config sets the DOS clock but no I3 intervention is declared")
    return out


def reads(rec):
    """The match reads in order: (host s since the burst, ticks, a9ff, commentary rows text). Three forms:
    every read in one observation, a JSON list of lists (README amendment 2, run.py READ_FIELDS); one
    observation per read, a JSON list (amendment 1); or, in the first records, E004's observations per
    read plus one holding `since ticks a9ff`."""
    out = []
    for v in fields(rec, "one list per read").values():   # amendment 2: all reads in one observation
        for x in json.loads(v):
            out.append((float(x[2]), int(x[3], 16), int(x[4], 16), x[10]))
    for label, v in fields(rec, "[host UTC time, host s since the starting burst").items():
        x = json.loads(v)
        out.append((float(x[1]), int(x[2], 16), int(x[3], 16), x[9]))
    rows = fields(rec, "commentary rows (rows 1-3")
    for label, v in fields(rec, "host seconds since the starting burst (monotonic").items():
        since, ticks, a9 = v.split()
        out.append((float(since), int(ticks, 16), int(a9, 16), rows.get(label, "")))
    return sorted(out, key=lambda r: r[0])


def last_counter(rec):
    """DS:80EE at the last match read (the full-time read), in any of the three forms, or None."""
    for v in fields(rec, "one list per read").values():
        return json.loads(v)[-1][6]
    reads_ = sorted((o["step"], o["value"]) for o in rec["observations"] if o["field"].startswith("match read")
                    and ("[host UTC time" in o["field"] or "words DS:80EE" in o["field"]))
    if not reads_:
        return None
    step, v = reads_[-1]
    return json.loads(v)[5] if v.startswith("[") else v.split()[0]


def first(rs, text):
    return next((r for r in rs if text in r[3]), None)


def ticks_of(rec, label):
    v = field(rec, f"{label}: 4 bytes at 0040:006C")
    return int(v.split()[0], 16) if v else None


def halves(r):
    """Host and guest seconds of each half of a match record, or None when a half was not seen."""
    rs, keys = r["reads"], r["keys"]
    ht, ft = first(rs, "HALF TIME"), first(rs, "FULL TIME")
    if not (ht and ft and r["ticks_ko"] is not None):
        return None
    team = [k[0] for k in keys if k[2] == "team screen"]
    t2 = team[-1] if team else None
    after = next((x for x in rs if t2 is not None and x[0] > t2), None)
    h = {"host_first": ht[0], "host_ht_to_ft": round(ft[0] - ht[0], 2),
         "host_second": round(ft[0] - t2, 2) if t2 is not None else None,
         "guest_first": round((ht[1] - r["ticks_ko"]) / TICKS_PER_S, 2),
         "guest_second": round((ft[1] - after[1]) / TICKS_PER_S, 2) if after else None}
    h["ratio"] = round(h["host_first"] / h["host_second"], 3) if h["host_second"] else None
    return h


def reproduced(ratios):
    """The verdict on F001's unequal halves from the first/second ratios of the watched runs at max."""
    if not ratios:
        return "F001's unequal halves at max: no completed watched run at max"
    n = sum(1 for x in ratios if x < UNEQUAL)
    verdict = "reproduced" if n == len(ratios) else ("not reproduced" if n == 0 else "reproduced in part")
    return (f"F001's unequal halves at max (ratio under {UNEQUAL}): {verdict}, in {n} of {len(ratios)} watched runs at max "
            f"(ratios {', '.join(str(x) for x in ratios)})")


def load(path):
    rec = json.loads(path.read_text())
    args = rec["actions"]["args"]
    r = {"id": rec["run_id"], "kind": args[0], "status": rec["status"], "cycles": field(rec, CYCLES_FIELD),
         "arm": args[args.index("--arm") + 1] if "--arm" in args else None,
         "state": args[args.index("--state") + 1] if "--state" in args else None, "problems": check(rec),
         "procs": field(rec, "other DOSBox-X and Xvfb processes on the host at launch"), "load": field(rec, "/proc/loadavg at launch")}
    if r["kind"] == "calibrate":
        v = field(rec, "title (fresh launch): dword DS:A9FF")
        r["a9ff"] = int(v.split()[0], 16) if v else None
        return r
    if r["status"] != "completed":
        return r
    text = field(rec, "full time: text screen rows 0-24")
    r["score"] = scoreboard(text)
    r["seed"] = field(rec, "full time: word at DS:7B62").split()[0]
    r["a9ff"] = int(field(rec, "full time: dword DS:A9FF").split()[0], 16)
    r["events"] = json.loads(field(rec, "events among them"))
    r["lines"] = json.loads(field(rec, "commentary lines of the match"))
    r["keys"] = json.loads(field(rec, "keys sent from the key"))
    r["seconds"] = field(rec, "match: savestate reads")
    r["reads"] = reads(rec)
    g = json.loads(field(rec, "commentary lines between successive reads"))
    r["gaps"], r["deltas"] = g["gaps"], g["deltas"]
    r["counter"] = last_counter(rec)
    r["ticks_ko"] = ticks_of(rec, "restored" if r["kind"] == "restores" else "captain screen")
    r["halves"] = halves(r)
    return r


RING = 200   # commentary records in the ring DS:7C38 (runtime/driver/commentary.py SIZE)
UNREAD = re.compile(r"^match read (\d+): record (\d+) is the end marker 0xFF$")
# Tracker.add's other flag: a read whose counter advanced GAP_LIMIT (100) or more records. It reads every one
# of them (fewer than RING), so no line of that read is unread; the flag warns that 200 or more lines may
# have passed, which the counter, modulo 200, would hide (E004 README amendment 2).
STRIDE = re.compile(r"^match read (\d+): counter \d+ -> \d+ \(\d+ lines\)$")
MEMORY = ("score", "seed", "counter")   # read whole from memory at full time, not from the ring


def unread_occurrences(r):
    """The commentary lines a run's reader never read, as absolute occurrences in the match (1-based):
    for each flag `match read k: record n is the end marker 0xFF` (runtime/driver/commentary.py
    Tracker.add), the lines before read k (the sum of the deltas of reads 1 .. k-1, DS:80EE starting at 0,
    0791:A4A1) plus n's place in read k's range. One occurrence per flag. Stride flags (STRIDE) name no
    unread line and are skipped here. None when the losses cannot be located: a flag of an unknown kind, an
    end-marker flag outside its read's range, or two flags for one occurrence."""
    out = []
    for g in r["gaps"]:
        if STRIDE.match(g):
            continue
        m = UNREAD.match(g)
        if not m:
            return None
        k, n = int(m[1]), int(m[2])
        if not 1 <= k <= len(r["deltas"]):
            return None
        before = sum(r["deltas"][:k - 1])
        j = (n - 1 - before % RING) % RING + 1
        if j > r["deltas"][k - 1]:
            return None
        out.append(before + j)
    if len(set(out)) != len(out):
        return None
    return sorted(out)


def strides(r):
    return [g for g in r["gaps"] if STRIDE.match(g)]


def located(r):
    """{absolute occurrence: line} for every line the run read, and the number of lines it counted (the sum
    of the deltas); None when its unread lines cannot be located or the lines read do not fit the
    occurrences left."""
    occ = unread_occurrences(r)
    if occ is None:
        return None
    total = sum(r["deltas"])
    places = [i for i in range(1, total + 1) if i not in set(occ)]
    if len(places) != len(r["lines"]):
        return None
    return {i: tuple(x) for i, x in zip(places, r["lines"])}, total


NO_DIFFERENCE = "no observed difference"


def compare(r, ref):
    """The verdict on a run against its reference, and why (review round 4: no claim of completeness).
    Completeness of the commentary cannot be shown from the reads: the counter and the ring are both modulo
    200, so a whole lap of the ring between two reads leaves no trace (issue #40). So:
    - DIFFERS when something observed differs: the score, DS:7B62 or DS:80EE at full time (memory, read
      whole), the number of lines counted, or a line at an occurrence both readers saw;
    - IDENTITY UNDETERMINED when a reader flag marks a line that side never read (an end marker), or a
      side's unread lines cannot be located, and nothing observed differs;
    - `no observed difference` otherwise: the same score, DS:7B62 and DS:80EE at full time, and every
      occurrence both readers saw equal. Stride flags are reported (`identity`), not decided on: they name
      no unread line, and their absence would not show completeness either."""
    if any(r[k] != ref[k] for k in MEMORY) or r["counter"] is None:
        return "DIFFERS", "score, DS:7B62 or DS:80EE at full time"
    a, b = located(r), located(ref)
    if a is not None and b is not None:
        if a[1] != b[1]:
            return "DIFFERS", f"lines counted {a[1]} against {b[1]}"
        both = sorted(set(a[0]) & set(b[0]))
        diff = [i for i in both if a[0][i] != b[0][i]]
        if diff:
            return "DIFFERS", f"occurrence {diff[0]} of the match ({len(diff)} occurrence(s) seen by both differ)"
    unread = [(name, x) for name, x in (("run", r), ("reference", ref)) if unread_occurrences(x) or located(x) is None]
    if unread:
        why = "; ".join(f"the {name}'s reader "
                        + (f"never read occurrence(s) {', '.join(map(str, unread_occurrences(x)))}" if unread_occurrences(x)
                           else "has lines it cannot locate")
                        + f" (gap flags: {'; '.join(x['gaps']) or 'none'})" for name, x in unread)
        return "IDENTITY UNDETERMINED", why
    return NO_DIFFERENCE, ""


def short(events):
    return "; ".join(f"{k} {t} {x}" for k, t, x in events) or "none"


def identity(r, ref):
    if ref is None:
        return "no reference"
    if ref is r:
        return "reference" if not unread_occurrences(r) and located(r) is not None else "reference, with unread lines: " + "; ".join(r["gaps"])
    verdict, why = compare(r, ref)
    if verdict == NO_DIFFERENCE:
        n = len(strides(r)) + len(strides(ref))
        return f"{NO_DIFFERENCE} from {ref['id']}" + (f" ({n} stride flag(s) reported)" if n else "")
    if verdict == "IDENTITY UNDETERMINED":
        return (f"IDENTITY UNDETERMINED against {ref['id']}: {why}; every occurrence both saw, the score, DS:7B62 and "
                f"DS:80EE at full time ({r['counter']}) are equal")
    return f"DIFFERS from {ref['id']}: {why}"


def verdict_counts(verdicts):
    """How many of each verdict `identity` gave, by the start each verdict string has."""
    starts = {NO_DIFFERENCE: NO_DIFFERENCE + " from ", "identity undetermined": "IDENTITY UNDETERMINED", "differ": "DIFFERS",
              "references": None, "references with unread lines": "reference, with unread lines", "no reference": None}
    out = {}
    for name, start in starts.items():
        if name == "references":
            out[name] = sum(v == "reference" for v in verdicts)
        elif name == "no reference":
            out[name] = sum(v == "no reference" for v in verdicts)
        else:
            out[name] = sum(v.startswith(start) for v in verdicts)
    return out


def reference(runs, r):
    """The same state's and arm's first completed restore at 30000."""
    return next((x for x in runs if x["kind"] == "restores" and x["status"] == "completed" and x["state"] == r["state"]
                 and x["arm"] == r["arm"] and x["cycles"] == REFERENCE_CYCLES), None)


def before_first_key(row):
    """What the read before the probe's key `c` (poll 0, `probe_f001.py --pre-read`) shows: whether the
    first half had already been played when the probe's clock started."""
    p0 = next((p for p in row.get("e005_polls", []) if p["poll"] == 0), None)
    if p0 is None:
        return "no read before the probe's key c"
    if "HALF TIME" in p0["rows"]:
        return (f"before the probe's key c: HALF TIME already on screen, DS:80EE {p0.get('counter')}: the first half was played "
                "before the probe's clock started")
    return f"before the probe's key c: no HALF TIME, DS:80EE {p0.get('counter')}"


def probe_rows(folder):
    out = []
    for p in sorted(folder.glob("match-speed*.json")):
        res = json.loads(p.read_text())
        for row in res.get("rows", []):
            out.append((p.name, row))
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    folder = Path(argv[0]) if argv else RUNS
    recs = [load(p) for p in sorted(folder.glob("E005-r*.json"))]
    problems = [x for r in recs for x in r["problems"]]

    print("## Calibration: DS:A9FF at the title screen of a fresh launch")
    for c in ("5000", "30000", "max"):
        vals = [r for r in recs if r["kind"] == "calibrate" and r["cycles"] == c and r.get("a9ff") is not None]
        print(f"cycles {c}: " + ", ".join(f"{r['id']} 0x{r['a9ff']:x} ({r['a9ff']})" for r in vals))

    runs = [r for r in recs if r["kind"] != "calibrate"]
    print("\n## Runs (verdict against the same state's and arm's first restore at 30000: DIFFERS, IDENTITY UNDETERMINED, or no observed difference: "
          "the same score, DS:7B62 and DS:80EE at full time and every commentary occurrence both readers saw)")
    for r in runs:
        if r["status"] != "completed":
            print(f"{r['id']} {r['kind']} {r['state']} cycles {r['cycles']} {r['arm']}: {r['status']}")
            continue
        ref = reference(runs, r)
        ident = identity(r, ref)
        a, ga, b, gb = r["score"]
        print(f"{r['id']} {'restore' if r['kind'] == 'restores' else 'fresh'} {r['state']} cycles {r['cycles']} {r['arm']}: "
              f"{a} {ga} {b} {gb}; DS:7B62 {r['seed']}; DS:A9FF 0x{r['a9ff']:x}; {ident}; events: {short(r['events'])}")

    verdicts = [identity(r, reference(runs, r)) for r in runs if r["status"] == "completed"]
    print("; ".join(f"{k}: {v}" for k, v in verdict_counts(verdicts).items()))

    print("\n## Halves of the watched runs (host s from the starting burst; guest s from the BIOS ticks)")
    print("run | route | state | cycles | DS:A9FF | host: burst→HALF TIME, HALF TIME→FULL TIME, team-screen Enter→FULL TIME | guest: 1st, 2nd | ratio 1st/2nd (host) | match s")
    for r in runs:
        if r["status"] != "completed" or r["arm"] != "watched":
            continue
        h = r["halves"]
        if not h:
            print(f"{r['id']} | halves not seen")
            continue
        print(f"{r['id']} | {r['kind']} | {r['state']} | {r['cycles']} | 0x{r['a9ff']:x} | {h['host_first']}, {h['host_ht_to_ft']}, {h['host_second']} | "
              f"{h['guest_first']}, {h['guest_second']} | {h['ratio']} | {r['seconds']}")
    at_max = [r["halves"]["ratio"] for r in runs if r["status"] == "completed" and r["arm"] == "watched" and r["cycles"] == "max"
              and r["halves"] and r["halves"]["ratio"] is not None]
    print(reproduced(at_max))

    print("\n## Cycles in effect after a restore (first-half guest seconds against the 30000 restores of the same state and arm)")
    for r in runs:
        if r["kind"] != "restores" or r["status"] != "completed" or not r["halves"]:
            continue
        refs = [x["halves"]["guest_first"] for x in runs if x["kind"] == "restores" and x["status"] == "completed" and x["halves"]
                and x["state"] == r["state"] and x["arm"] == r["arm"] and x["cycles"] == REFERENCE_CYCLES]
        g = r["halves"]["guest_first"]
        implied = round(int(REFERENCE_CYCLES) * statistics.fmean(refs) / g) if refs and g > 0 else None
        print(f"{r['id']} {r['state']} {r['arm']} cycles {r['cycles']}: first half {g} guest s; implied cycles {implied}")

    print("\n## F001's probe re-run (runtime/spike/probe.py match, its own keys)")
    for name, row in probe_rows(HERE / "measurements"):
        ht, s2, ft = row.get("half_time_after_s"), row.get("second_half_started_after_s"), row.get("full_time_after_s")
        ratio = round(ht / (ft - s2), 3) if None not in (ht, s2, ft) and ft > s2 else None
        print(f"{name} cycles {row.get('cycles')}: HALF TIME {ht} s, second half started {s2} s, FULL TIME {ft} s; "
              f"ratio 1st/2nd {ratio} ({'unequal' if ratio is not None and ratio < UNEQUAL else 'not unequal'}); polls {row.get('polls')}; "
              f"phase {row.get('phase_at_end')}")
        print("  " + before_first_key(row))
        for p in row.get("e005_polls", []):
            print(f"  poll {p['poll']}: {p['since']} s, ticks 0x{p['ticks']:08x}, DS:A9FF 0x{p['a9ff']:x}, delay byte {p['delay']}, DS:80EE {p.get('counter', 'not read')}, rows {p['rows']}")

    print("\n## Checks")
    print(f"{len(recs)} records; {sum(r['status'] == 'completed' for r in recs)} completed")
    for r in recs:
        if r["status"] != "completed":
            print(f"not completed: {r['id']} {r['status']}")
    others = sorted({(p[0], p[2]) for r in recs for p in json.loads(r["procs"] or "[]")})
    print("other DOSBox-X/Xvfb processes at any launch (pid name): " + ", ".join(f"{p} {n}" for p, n in others))
    print("\n".join(problems) if problems else "every record names its cycles setting; every record that sets the clock declares I3")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
