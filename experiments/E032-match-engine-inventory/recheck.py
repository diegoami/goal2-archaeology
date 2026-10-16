#!/usr/bin/env python3
"""E032: every comparison the plan quotes, re-made on the committed logs, from ONE explicit manifest, and
failing closed when anything is missing or extra (PR 243 review round 5: an acceptance script that skipped a
stamp's comparisons when a batch transcript was missing).

    python3 -B experiments/E032-match-engine-inventory/recheck.py [--out DIR]

The manifest below is the whole expected state: the stamps, the batch transcripts, every log, and every
comparison with its reference, candidate, seed family, expectation, the run the candidate must be
(--field) and the exit code compare.py must give: 0 for a comparison quoted as passing, 1 for a routine the
plan quotes as NOT removable (a measured difference). Nothing is skipped and nothing is optional:
- every transcript and every log of the manifest must exist in DIR (default: out/ beside this script), and
  DIR must hold no other match log (*.jsonl) nor batch transcript (*batch-*.txt) than the manifest's;
- every transcript of a stamp from review1 on must end with `batch exit 0`;
- every comparison runs (compare.py's main, in-process) and must give exactly its expected exit code;
- the number of comparisons run must equal the manifest's (EXPECTED_COMPARISONS: 80 for the five stamps at
  23fc03a, 95 once review5's batches were added).
Exit 0 when all of that holds, 2 otherwise; one line per comparison, then the counts. It generates nothing."""
import argparse
import contextlib
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare  # noqa: E402

STAMPS = ("20261015", "review1", "review2", "review3", "review4", "review5")   # a new batch stamp is added here
TRANSCRIPTS = [f"{kind}-batch-{s}.txt" for s in STAMPS for kind in ("pilot", "skip")] + ["coverage-batch-20261015.txt"]
TWO = "0x1234,0x2345"
EIGHT = "0x0101,0x2b7e,0x4c1d,0x6a33,0x8e05,0xa1f0,0xc3c3,0xe719"
REF_TWO = "timing-delay20-kickoff-20261015.jsonl"
REF_EIGHT = "timing-delay20-8seeds-20261015.jsonl"
PORTED = 'ported=["0791:8889", "0791:86D0"]'
DISPLAY = ["0791:8F10", "0791:9079", "0791:0481", "0791:1829", "0791:0425", "0791:0441", "0791:94E8", "0791:9372"]
FALSIFIERS = ("coin-swapped", "bound-36", "no-picture")


def skipped(routines):
    return "skipped=[" + ", ".join(f'"{r}"' for r in routines) + "]"


def manifest():
    """[(label, reference, candidate, [compare.py arguments after the two logs], expected exit)]"""
    out = []
    for s in STAMPS:
        for r in DISPLAY:
            out.append((f"skip {r} ({s})", REF_TWO, f"skip-{r.replace(':', '-')}-{s}.jsonl",
                        ["--seeds", TWO, "--field", skipped([r])], 0))
        dset = DISPLAY if s != "20261015" else DISPLAY[:7]
        out.append((f"skip the display set ({s})", REF_TWO, f"skip-display-set-{s}.jsonl",
                    ["--seeds", TWO, "--field", skipped(dset)], 0))
        for r in ("0791:8537", "0791:8E24"):
            out.append((f"skip {r} ({s}), not removable", REF_TWO, f"skip-{r.replace(':', '-')}-{s}.jsonl",
                        ["--seeds", TWO, "--field", skipped([r])], 1))
        out.append((f"pilot exact, 8 seeds ({s})", REF_EIGHT, f"pilot-exact-8seeds-{s}.jsonl",
                    ["--seeds", EIGHT, "--field", 'variant="exact"', "--field", PORTED], 0))
        for v in FALSIFIERS:
            out.append((f"falsifier {v} caught ({s})", REF_TWO, f"pilot-{v}-{s}.jsonl",
                        ["--seeds", "0x1234", "--expect", "differ", "--field", f'variant="{v}"', "--field", PORTED], 0))
    out += [
        ("delay count at kick-off, 2 seeds", "timing-plain-20261015.jsonl", REF_TWO,
         ["--seeds", TWO, "--field", "delay_count=20"], 0),
        ("delay count at kick-off, 8 seeds", "timing-plain-8seeds-20261015.jsonl", REF_EIGHT,
         ["--seeds", EIGHT, "--field", "delay_count=20"], 0),
        ("delay count written at the start, 1 seed", "timing-plain-20261015.jsonl", "timing-delay20-20261015.jsonl",
         ["--seeds", "0x1234", "--field", "delay_count=20"], 0),
        ("skip 8E24 with the display set (20261015), not removable", REF_TWO,
         "skip-0791-8E24_0791-9079_0791-0481_0791-1829_0791-0425_0791-0441_0791-94E8-20261015.jsonl",
         ["--seeds", TWO, "--field", skipped(["0791:8E24"] + DISPLAY[1:7])], 1),
        ("pilot exact, first try", REF_TWO, "pilot-exact-try1-20261015.jsonl",
         ["--seeds", TWO, "--field", 'variant="exact"', "--field", PORTED], 0),
    ]
    return out


COMPARISONS = manifest()
EXPECTED_COMPARISONS = 95          # 15 per stamp x 6 stamps + 5 single comparisons
LOGS = sorted({c[1] for c in COMPARISONS} | {c[2] for c in COMPARISONS})
assert len(COMPARISONS) == EXPECTED_COMPARISONS, len(COMPARISONS)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    problems = []
    if not out.is_dir():
        problems.append(f"{out}: not a directory")
    else:
        present_logs = {p.name for p in out.glob("*.jsonl")}
        present_transcripts = {p.name for p in out.glob("*batch-*.txt")}
        problems += [f"missing log {n}" for n in LOGS if n not in present_logs]
        problems += [f"unexpected log {n}" for n in sorted(present_logs - set(LOGS))]
        problems += [f"missing transcript {n}" for n in TRANSCRIPTS if n not in present_transcripts]
        problems += [f"unexpected transcript {n}" for n in sorted(present_transcripts - set(TRANSCRIPTS))]
        for n in TRANSCRIPTS:
            stamp = n.rsplit("-", 1)[1][:-4]
            if n in present_transcripts and stamp != "20261015":
                lines = (out / n).read_text(errors="replace").strip().splitlines()
                if not lines or lines[-1] != "batch exit 0":
                    problems.append(f"transcript {n} does not end with 'batch exit 0'")
    ran = 0
    for label, ref, cand, args, want in COMPARISONS:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = compare.main([str(out / ref), str(out / cand), *args])
            except Exception as e:                      # never a pass
                rc = f"raised {type(e).__name__}: {e}"
        ran += 1
        text = buf.getvalue().strip().splitlines()
        verdict = "ok" if rc == want else "FAIL"
        print(f"{verdict}: {label}: compare exit {rc}, expected {want}" + ("" if rc == want else f" ({text[-1] if text else ''})"))
        if rc != want:
            problems.append(f"{label}: compare exit {rc}, expected {want}")
    if ran != EXPECTED_COMPARISONS:
        problems.append(f"ran {ran} comparisons, expected {EXPECTED_COMPARISONS}")
    for p in problems:
        print(f"PROBLEM: {p}")
    print(f"{ran} comparisons run of {EXPECTED_COMPARISONS} expected; {len(LOGS)} logs and {len(TRANSCRIPTS)} "
          f"transcripts expected; {len(problems)} problems")
    print(f"recheck exit {2 if problems else 0}")
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
