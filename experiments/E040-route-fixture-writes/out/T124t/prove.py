"""T124t: state 213 reaches the ends of stages 3 and 4, through the original team menu.

Run with --out NAME; writes NAME.jsonl after each returned round or failure, never overwrites an existing output.
--no-selection is the falsifier: the old play-only policy, refused by the original before stage 3 finishes.
Each round receipt holds its newly played matches, policy choices and every key those matches took.
"""
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(HERE.parent.parent))
from original_match import route as R, port, route_team
from original_match.image import Image
from original_match.port.prove import Prover
from runner import expected

STATE = "53b69d3dfb964e77-snap-0213-20261011T142027Z.sav"


def play(out, no_selection=False):
    data = (ROOT / ".cache" / "dl" / STATE).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    assert sha == expected(STATE)
    # The falsifier changes only the harness's decision. EA09 still runs and must reject it.
    if no_selection:
        route_team.choose_eleven = lambda squad, player: []
    r = R.Route(Image.from_savestate(data), entry="play_round", record_writes=False)
    inst = port.install(r.m, ["stages"])
    prover = Prover(r.m, inst)
    start = time.monotonic()
    with out.open("x") as f:
        def record(value):
            f.write(json.dumps(value, sort_keys=True) + "\n")
            f.flush()
            print(json.dumps({k: v for k, v in value.items() if k not in ("teams", "matches", "proof")}), flush=True)
        record({"schema": "t124t/1", "state": STATE, "sha256": sha, "no_selection": no_selection,
                "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "started": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        reached = []
        for number in range(1, 5):
            before = len(r.record)
            try:
                r.round()
            except Exception as e:
                record({"status": "failed", "round": number, "error": f"{type(e).__name__}: {e}",
                        "elapsed_s": round(time.monotonic() - start, 1),
                        "teams": [e[1] for e in r.record[before:] if e[0] == "team"]})
                raise
            entries = r.record[before:]
            end = next(e[1] for e in reversed(entries) if e[0] == "round_end")
            reached.append(end["stage"])
            record({"status": "round", "round": number, "end": end,
                    "elapsed_s": round(time.monotonic() - start, 1),
                    "matches": [e[1] for e in entries if e[0] == "match"],
                    "teams": [e[1] for e in entries if e[0] == "team"], "proof": prover.summary()})
        assert reached == [2, 3, 4, 4], reached
        assert all(v["before"] == 0 for v in prover.summary().values())
        record({"status": "completed", "reached": reached, "elapsed_s": round(time.monotonic() - start, 1)})
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-selection", action="store_true")
    a = ap.parse_args()
    play(HERE / (a.out + ".jsonl"), a.no_selection)


if __name__ == "__main__":
    main()
