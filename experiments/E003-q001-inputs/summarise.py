#!/usr/bin/env python3
"""Tabulate E003's records for F004 (T08's Done-when 2 and 3).

    python3 experiments/E003-q001-inputs/summarise.py [runs/E003/E003-r0001.json ...]

Per d0 launch: the DOS clock requested and the date and time applied (DOS's read-back where the record
has one, else the best evidence it has: applied_clock), the guest clock at the title (BIOS ticks as HH:MM:SS.s),
the main-screen digest, and the words DS:7B62 and DS:7B64 at the main screen. Per d3 or d3b run: the batch,
the DOS time set, the clock after the restore, the result screen digests (after the first `r` and at
the end), and the three seed words before and after `r`. Then the distinct values per group.
Reads the records only. The one computation beyond the recorded values: how many steps of the LCG
of 214B:0688 (seed = seed * 0x7ABD + 0x1B0F mod 2^16) lead from the hour:minute word of DS:7B64's
INT 21h call (CX = hour * 256 + minute, inferred from the DOS time the record names) to DS:7B62."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TICKS_PER_SECOND = 1193182 / 65536  # PIT input clock / 65536: the BIOS tick rate


def clock(ticks_value):
    tenths = round(int(ticks_value.split()[0], 16) / TICKS_PER_SECOND * 10)
    h, rem = divmod(tenths, 36000)
    m, s = divmod(rem, 600)
    return f"{h:02d}:{m:02d}:{s // 10:02d}.{s % 10}"


def lcg_steps(start, target, limit=5000):
    x = start
    for n in range(limit + 1):
        if x == target:
            return n
        x = (x * 0x7ABD + 0x1B0F) & 0xFFFF
    return None


def reads(rec):
    """label -> {what: value} for each read, in step order."""
    out = {}
    for o in rec["observations"]:
        f = o.get("field", "")
        if ": " not in f:
            continue
        label, what = f.split(": ", 1)
        out.setdefault(label, {})[what] = o["value"]
    return out


def get(r, label, key):
    for what, v in r.get(label, {}).items():
        if key in what:
            return v
    return None


def word(r, label, off):
    v = get(r, label, f"word at DS:{off}")
    return v.split()[0] if v else "-"


def field(rec, name):
    return next((o["value"] for o in rec["observations"] if o.get("field") == name), "")


DEFAULT_DATES = ("10-04-2026", "10/04/2026")


def dos_time(rec):
    """The DOS clock the record requested: its time (with the date when not the default), or "free".
    What was applied is applied_clock's: a request is not evidence that it took effect."""
    a = rec["actions"]["args"]
    if "--dos-time" not in a:
        return "free"
    t, d = a[a.index("--dos-time") + 1], a[a.index("--dos-date") + 1]
    return t if d in DEFAULT_DATES else f"{t} on {d}"


READBACK = "DOS clock read back"


def applied_clock(rec, r, last):
    """The DOS date actually in effect, from the best evidence the record has:
    - records from the rework round: DOS's own `date /t`/`time /t` read-back (CLOCK.TXT);
    - earlier records: the year GOAL.EXE stored at DS:A9FD (r0034 …), or, for a date given as
      MM-DD-YYYY (r0001 … r0033), the host's date: DOSBox-X ignored that form (README, amendment 2);
    - free launches: the host clock (not set)."""
    back = next((o["value"] for o in rec["observations"] if o.get("field", "").startswith(READBACK)), None)
    if back is not None:
        return "read back " + " ".join(back.split()) if back != "not read" else "NOT read back"
    a = rec["actions"]["args"]
    if "--dos-time" not in a:
        return "host clock"
    y = word(r, last, "A9FD")
    if y.startswith("0x"):
        return f"not read back; year {int(y, 16)} at DS:A9FD"
    d = a[a.index("--dos-date") + 1]
    return "not read back; date not applied (host's)" if "-" in d else "not read back"


def labels_of(r, prefix):
    return [lb for lb in r if lb.startswith(prefix)]


def main(argv):
    paths = [Path(p) for p in argv] or sorted((ROOT / "runs/E003").glob("E003-r*.json"))
    recs = [json.loads(p.read_text()) for p in paths]
    d0 = [x for x in recs if x["arm"].startswith("d0")]
    d3 = [x for x in recs if x["arm"].startswith("d3")]
    s8 = lambda x: (x or "-")[:8]  # noqa: E731

    print("== d0: fresh launch, F001's D0 keys (11) to the main menu")
    print("run | status | batch | launch local | DOS clock requested | DOS date/time applied | clock at title | main-screen digest | DS:7B62 | DS:7B64 | LCG steps from hh:mm | DS:A9FD")
    groups = defaultdict(set)
    for rec in d0:
        r = reads(rec)
        steps = labels_of(r, "after key ")
        last = steps[-1] if steps else None
        t = dos_time(rec)
        w62, w64 = word(r, last, "7B62"), word(r, last, "7B64")
        n = "-"
        if t != "free" and w62 != "-" and w62.startswith("0x"):
            hh, mm = int(t[:2]), int(t[3:5])
            n = lcg_steps(hh * 256 + mm, int(w62, 16))
        complete = rec["status"] == "completed" and last and last.startswith("after key 11")
        ap = applied_clock(rec, r, last)
        if complete:
            groups[f"{t} [{ap}]"].add(get(r, last, "sha256"))
        print(" | ".join([rec["run_id"], rec["status"][:30], field(rec, "batch label given on the command line"),
                          field(rec, "host local time at launch, with UTC offset, and zone name")[:23], t, ap,
                          clock(get(r, "title (fresh launch)", "0040:006C") or "0x0"), get(r, last, "sha256") or "-",
                          w62, w64, str(n), word(r, last, "A9FD")]))
    print("distinct main-screen digests per DOS clock requested [applied] (completed launches):")
    for t, ds in sorted(groups.items()):
        print(f"  {t}: {len(ds)} distinct: {', '.join(s8(d) for d in sorted(ds))}")

    print("\n== d3 / d3b: restore `main`, F001's D3 keys (d3) or with Enter+r sent together (d3b); seeds before and after the first `r`")
    print("run | arm | status | batch | launch local | DOS time set | clock after restore | after r | end | "
          "before r: 7B62 7B64 8336 | after r: 7B62 7B64 8336")
    g3 = defaultdict(list)
    for rec in d3:
        r = reads(rec)
        steps = labels_of(r, "after key ")
        ir = next((i for i, lb in enumerate(steps) if lb.endswith("(r)") or lb.endswith("+r)")), None)
        after = steps[ir] if ir is not None else None
        before = (steps[ir - 1] if ir else "restored") if ir is not None else None
        end = steps[-1] if steps else None
        kind = rec["arm"].split("-")[0]
        b = " ".join(word(r, before, o) for o in ("7B62", "7B64", "8336"))
        a = " ".join(word(r, after, o) for o in ("7B62", "7B64", "8336"))
        batch = field(rec, "batch label given on the command line")
        if rec["status"] == "completed":
            g3[(kind, dos_time(rec), batch)].append((get(r, after, "sha256"), get(r, end, "sha256"), b, a))
        print(" | ".join([rec["run_id"], kind, rec["status"][:30], batch,
                          field(rec, "host local time at launch, with UTC offset, and zone name")[:23], dos_time(rec),
                          clock(get(r, "restored", "0040:006C") or "0x0"), get(r, after, "sha256") or "-",
                          get(r, end, "sha256") or "-", b, a]))
    print("per (arm, DOS time, batch), completed runs: distinct after-r digests / end digests / seeds before r / seeds after r")
    for k, rows in sorted(g3.items()):
        print(f"  {' '.join(k)}: {len(rows)} runs; " + " / ".join(
            f"{len(set(c))}: {', '.join(sorted(set(s8(x) if len(x) == 64 else x for x in c)))}" for c in zip(*rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
