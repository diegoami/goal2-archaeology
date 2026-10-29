"""T80b M1: E034-03's straight drive from goal2's state and GOAL.EXE's tables equals the drive from the image.

    PYTHONPATH=runtime pypy3.11 -B experiments/E036-match-port/out/T80/b/from_state_v1.py --out <new json>

The reference image (E006-r0001) gives goal2's state (Image.state_of: the memory without GOAL.EXE's load module,
and the 26 initialised bytes the game changed); the sealed image is Image.from_state(state, tables) with the
tables from static/goal-exe/tables (port/tables.py). Both play E034-03's straight drive on the port; the events,
the result (but its own input digest, image_sha256), the draws and records_after() (goal2's state after the
match and its post-match update) must be equal. The sealed image passes the build guard as built from tables
(Image.build_problems), unlike minimal_image_v1.py, which bypassed it. Digests and counts only.
"""
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
ap = argparse.ArgumentParser();ap.add_argument("--out", required=True);a = ap.parse_args()
out = open(a.out, "x")
sys.path[:0] = [str(ROOT), str(ROOT / "runtime")]
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.assets import reference_image  # noqa: E402
from original_match.port import tables as port_tables  # noqa: E402

spec = importlib.util.spec_from_file_location("b", ROOT / "experiments/E033-original-match-kit/save_boundaries.py")
harness = importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
digest = lambda v: hashlib.sha256(json.dumps(v, sort_keys=True, default=repr).encode()).hexdigest()


def policy(match, d): match.answer(quick=True) if d["context"] == "half_time" else match.answer()


def drive(image, tables):
    m = Match(image, Fixture(7, 19, index=9, kind=200), managed=7, substitutions=None, engine="port", record_draws=True)
    events = harness.drive(m, policy, ())
    result = m.result()
    after = m.records_after(tables)
    return dict(events=len(events), events_sha256=digest(events), score=result["score"], draws=result["draws"],
                result_sha256_without_image=digest({k: v for k, v in result.items() if k != "image_sha256"}),
                records_after_sha256=digest(after), initialised_after=len(after["initialised"]))


tables = port_tables.load(ROOT / "static/goal-exe/tables")
reference = Image.from_savestate(reference_image(ROOT / ".cache/dl"))
state = reference.state(tables)
sealed = Image.from_state(json.loads(json.dumps(state)), tables)     # as goal2 passes it: JSON
full = drive(reference, tables)
from_state = drive(sealed, tables)
report = dict(full=full, from_state=from_state, equal=full == from_state, build_problems=sealed.build_problems(),
              state_json_bytes=len(json.dumps(state)), state_initialised=len(state["initialised"]),
              tables_sha256=tables.sha256)
json.dump(report, out, indent=1);out.close()
print(json.dumps(report, indent=1))
