"""T124a (#427): the round's end proved in the route harness.

    python3 -B experiments/E040-route-fixture-writes/out/T124a/prove.py --state ASSET --config frame|helpers \
        [--rounds N] [--variant NAME] --out NAME

One run: Route(image, entry="play_round", record_writes=False) on the published state `.cache/dl/ASSET` (verified
against its evidence manifest's sha256, as runner.py --fetch does), the ports of the config installed and a Prover
(port/prove.py) on the route's machine from the start, then Route.round() N times (default 1): play_round calls until
each round's end, the managed matches by Match(tail=False) on their own machines, everything else on the proved one.
It writes out/T124a/NAME.json: the state and its hash, the config, the ports installed, the round ends reached
(Route's ("round_end", ...) entries, the stage and rounds bytes after each), the Prover's summary per routine (proved,
nested, before, dead, scratch), the ported calls (Installed.calls), the managed matches, the counts of the record's
entries, the elapsed time, the code commit, and how the run ended ("completed", or the exception that ended it: a
ProofError is a difference; a MatchError or GuestError a harness limit the run met, with the round ends before it
proved).

Configs [designed: T124a]:
- frame: port/stages.py's seven ports and display's 5C94 and 5CCB (stages.display_helpers()). stage_end 8208 and
  run_stage 76B1 are proved; the helpers' calls inside 76B1's builders are nested in its proof (their writes and
  returned registers compared inside it), and 5C94/5CCB are proved where route_fixture's news 6685 calls them.
- helpers: the same without 8208 and 76B1, which then run as the original's: every helper call the builders make is
  proved on its own (5D02's, inside 5D94's, nested).
--variant NAME: one falsifier, `stages.NAME` or `display.NAME` (display's omit-1771-5c94, omit-1771-5ccb): the run must
end in a ProofError."""
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(HERE.parent.parent))

from original_match import port, route as R          # noqa: E402
from original_match.image import Image                # noqa: E402
from original_match.port import stages, Registry      # noqa: E402
from original_match.port.prove import Prover          # noqa: E402
from runner import expected                           # noqa: E402  (E040's: the state's manifest sha256)

FRAME = ("1771:8208", "1771:76B1")


def subset(reg, drop):
    out = Registry(reg.name, reg.doc)
    for address, entry in reg.entries.items():
        if address not in drop:
            out._add(entry)
    out.variants = dict(reg.variants)
    return out


def specs(config, variant):
    reg = stages.PORTS if config == "frame" else subset(stages.PORTS, FRAME)
    disp = stages.display_helpers()
    sv = dv = None
    if variant:
        module, _, name = variant.partition(".")
        if module == "stages" and name in reg.variants:
            sv = name
        elif module == "display" and name in disp.variants:
            dv = name
        else:
            raise SystemExit(f"no variant {variant} in config {config}")
    return [(reg, sv), (disp, dv)]


def game_bytes(m):
    g = m.far(R.GAME_PTR)
    return {"cursor": m.word_at(g + 0x26), "count": m.word_at(g + 0x28), "stage": m.read(g + 0x3C, 1)[0],
            "rounds": m.read(g + 0x3D, 1)[0], "flag_40": m.read(g + 0x40, 1)[0], "season_38": m.word_at(g + 0x38)}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--config", choices=("frame", "helpers"), required=True)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--variant")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = HERE / f"{a.out}.json"
    if out.exists():
        raise SystemExit(f"{out} exists: outputs are never overwritten")
    path = ROOT / ".cache" / "dl" / a.state
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != expected(a.state):
        raise SystemExit(f"{a.state}: sha256 {sha} is not its evidence manifest's")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                                capture_output=True, text=True).stdout.strip())
    r = R.Route(Image.from_savestate(data), entry="play_round", record_writes=False)
    inst = port.install(r.m, specs(a.config, a.variant))
    prover = Prover(r.m, inst)
    result = {"schema": "t124a-prove/1", "state": a.state, "sha256": sha, "config": a.config, "variant": a.variant,
              "rounds_asked": a.rounds, "ports": inst.names, "installed": sorted(prover.names), "code_commit": commit,
              "dirty_tree": dirty, "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "start": game_bytes(r.m), "round_ends": []}
    t = time.time()
    status = "completed"
    try:
        for _ in range(a.rounds):
            r.round()
            ends = [e[1] for e in r.record if e[0] == "round_end"]
            result["round_ends"].append({"at": ends[-1], "after": game_bytes(r.m)})
    except Exception as e:                                # the run's end, kept: a difference or a harness limit
        status = f"{type(e).__name__}: {e}"
    result["elapsed_s"] = round(time.time() - t, 1)
    result["status"] = status
    result["summary"] = prover.summary()
    result["calls"] = dict(inst.calls)
    result["matches"] = [e[1] for e in r.record if e[0] == "match"]
    result["record_counts"] = dict(Counter(e[0] for e in r.record))
    result["keys"] = sorted([list(k) + [n] for k, n in Counter((e[1], e[2], e[4]) for e in r.record
                                                                if e[0] == "key").items()])
    result["end"] = game_bytes(r.m)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "round_ends", "elapsed_s")}, indent=1))
    for address, v in result["summary"].items():
        print(address, inst.calls.get(address), v)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
