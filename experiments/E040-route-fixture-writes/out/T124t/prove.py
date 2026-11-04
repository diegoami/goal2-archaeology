"""T124t: state 213 reaches the ends of stages 3 and 4, through the original team menu.

Run with --out NAME; writes NAME.jsonl after each returned round or failure, never overwrites receipts.
--resume verifies the latest completed round checkpoint under .cache/t124t/ and runs only missing rounds.
--stop-after-round N pauses after that round for a bounded batch; the next --resume continues it.
--no-selection is the falsifier: the old play-only policy, refused by the original before stage 3 finishes.
Each round receipt holds its newly played matches, policy choices and every key those matches took.
"""
import argparse
import datetime
import hashlib
import json
import os
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
from original_match.machine import MEM_SIZE, REGS
from original_match.port.prove import Prover
from runner import expected

STATE = "53b69d3dfb964e77-snap-0213-20261011T142027Z.sav"


def source_hashes():
    paths = ["runtime/original_match/route.py", "runtime/original_match/route_team.py",
             "runtime/original_match/port/stages.py", str(HERE.relative_to(ROOT) / "prove.py")]
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}


def load_checkpoint(path, sha):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        raise ValueError(f"checkpoint hash mismatch: {path}")
    return Image(data)


def checkpoint_context(route, prover=None):
    if route.m.running or route.m.frames or route.m.muted or (prover is not None and
            (prover.state is not None or prover._visit is not None)):
        raise ValueError("checkpoint requires a returned round with no live port or proof frame")
    return {"regs": {r: route.m.reg(r) for r in REGS}, "waiting_key": route.keys.waiting}


def restore_context(route, context):
    if set(context["regs"]) != set(REGS):
        raise ValueError("checkpoint does not hold every machine register")
    for name, value in context["regs"].items():
        route.m.set_reg(name, value)
    route.keys.waiting = context["waiting_key"]


def play(out, no_selection=False, resume=False, stop_after_round=4):
    data = (ROOT / ".cache" / "dl" / STATE).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    assert sha == expected(STATE)
    # The falsifier changes only the harness's decision. EA09 still runs and must reject it.
    if no_selection:
        route_team.choose_eleven = lambda squad, player: []
    image = Image.from_savestate(data)
    previous = []
    if resume:
        records = [json.loads(line) for line in out.read_text().splitlines()]
        header = records[0]
        if header["sha256"] != sha or header["no_selection"] != no_selection:
            raise ValueError("resume input differs from the original receipt")
        if header.get("source_hashes") != source_hashes():
            raise ValueError("resume source differs from the original receipt")
        previous = [v for v in records if v.get("status") == "round"]
        if previous:
            checkpoint = previous[-1]["checkpoint"]
            image = load_checkpoint(ROOT / checkpoint["path"], checkpoint["sha256"])
    r = R.Route(image, entry="play_round", record_writes=False)
    if previous:
        restore_context(r, previous[-1]["checkpoint"]["context"])
    inst = port.install(r.m, ["stages"])
    prover = Prover(r.m, inst)
    start = time.monotonic()
    with out.open("a" if resume else "x") as f:
        def record(value):
            f.write(json.dumps(value, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
            print(json.dumps({k: v for k, v in value.items() if k not in ("teams", "matches", "proof")}), flush=True)
        if not resume:
            record({"schema": "t124t/3", "state": STATE, "sha256": sha, "no_selection": no_selection,
                "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "source_hashes": source_hashes(),
                "started": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        reached = [v["end"]["stage"] for v in previous]
        for number in range(len(previous) + 1, 5):
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
            component = r.header + r.m.read(0, MEM_SIZE) + r.tail
            checkpoint_sha = hashlib.sha256(component).hexdigest()
            checkpoint = ROOT / ".cache/t124t" / out.stem / f"round-{number}-{checkpoint_sha[:16]}.mem"
            checkpoint.parent.mkdir(parents=True, exist_ok=True)
            if not checkpoint.exists():
                partial = checkpoint.with_suffix(".partial")
                with partial.open("wb") as state_file:
                    state_file.write(component)
                    state_file.flush()
                    os.fsync(state_file.fileno())
                partial.replace(checkpoint)
            # Read back before writing the durable public receipt. Guest bytes stay local, never in git.
            load_checkpoint(checkpoint, checkpoint_sha)
            record({"status": "round", "round": number, "end": end,
                    "elapsed_s": round(time.monotonic() - start, 1),
                    "checkpoint": {"path": str(checkpoint.relative_to(ROOT)), "sha256": checkpoint_sha,
                                   "context": checkpoint_context(r, prover)},
                    "matches": [e[1] for e in entries if e[0] == "match"],
                    "teams": [e[1] for e in entries if e[0] == "team"], "proof": prover.summary()})
            if number == stop_after_round and number < 4:
                record({"status": "paused", "after_round": number})
                return r
        assert reached == [2, 3, 4, 4], reached
        assert all(v["before"] == 0 for v in prover.summary().values())
        record({"status": "completed", "reached": reached, "elapsed_s": round(time.monotonic() - start, 1)})
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-selection", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--stop-after-round", type=int, choices=range(1, 5), default=4)
    a = ap.parse_args()
    play(HERE / (a.out + ".jsonl"), a.no_selection, a.resume, a.stop_after_round)


if __name__ == "__main__":
    main()
