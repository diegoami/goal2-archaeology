"""T80b M1 probe: does a match need anything but T80a's tables and the read map's state bytes?

    PYTHONPATH=runtime pypy3.11 -B experiments/E036-match-port/out/T80/b/minimal_image_v1.py --out <new json>

Builds a memory image that is zero everywhere except T80a's tables (static/goal-exe/tables: the
initialised data segment and the code segments' data areas, at their image positions) and, from the
reference image (E006-r0001), exactly the bytes the family read map lists as read before written
(out/T80/a/read-map-family-v1.chunk-*.json) outside those tables, DS:7968 included. Then plays
E034-03's straight drive on the port from it and compares the events, the result and the post-match
records with the same drive from the full reference image. The build guard (GOAL.EXE's code digests,
Image.build_problems) is bypassed here only, because the probe zeroes the code on purpose: the sealed
engine never reads it. Diagnostic for T80b; counts and digests only, no byte of the original.
"""
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
ap = argparse.ArgumentParser();ap.add_argument("--out", required=True);a = ap.parse_args()
out = open(a.out, "x")
sys.path[:0] = [str(ROOT), str(ROOT / "runtime"), str(ROOT / "tools/static")]
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.assets import reference_image  # noqa: E402
import port_tables  # noqa: E402

spec = importlib.util.spec_from_file_location("b", ROOT / "experiments/E033-original-match-kit/save_boundaries.py")
harness = importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)


def policy(match, d): match.answer(quick=True) if d["context"] == "half_time" else match.answer()


def drive(image):
    m = Match(image, Fixture(7, 19, index=9, kind=200), managed=7, substitutions=None, engine="port", record_draws=True)
    events = harness.drive(m, policy, ())
    result = m.result()
    digest = lambda v: hashlib.sha256(json.dumps(v, sort_keys=True, default=repr).encode()).hexdigest()
    # The result names its input image by digest; the minimal image is another input by design, so that one
    # field is compared apart (minimal-image-v1.json: it was the only difference).
    return dict(events=len(events), events_sha256=digest(events), score=result["score"], draws=result["draws"],
                result_sha256_without_image=digest({k: v for k, v in result.items() if k != "image_sha256"}),
                image_sha256=result.get("image_sha256"))


reference = Image.from_savestate(reference_image(ROOT / ".cache/dl"))
full = drive(reference)

minimal = Image.from_savestate(reference_image(ROOT / ".cache/dl"))
source = bytes(minimal.memory)
memory = bytearray(len(source))
code0, ds0 = minimal.load * 16, minimal.DS * 16
manifest = json.loads(port_tables.MANIFEST.read_text())
ds_table, code_table = port_tables.read_tables(port_tables.TABLES)
memory[ds0:ds0 + len(ds_table)] = ds_table
at = 0
for off, n in manifest["code_data"]:
    memory[code0 + off:code0 + off + n] = code_table[at:at + n];at += n
state = set()
for chunk in sorted((ROOT / "experiments/E036-match-port/out/T80/a").glob("read-map-family-v1.chunk-*.json")):
    for s, n in json.loads(chunk.read_text())["ranges"]:
        state.update(range(s, s + n))
in_tables = {ds0 + i for i in range(len(ds_table))} | {code0 + o + i for o, n in manifest["code_data"] for i in range(n)}
state_bytes = sorted(x for x in state if x not in in_tables) + [ds0 + 0x7968]
for x in state_bytes:
    memory[x] = source[x]
minimal.memory = memory
Image.build_problems = lambda self: []           # the probe zeroes GOAL.EXE's code on purpose (see the docstring)
try:
    sealed = drive(minimal);error = None
except Exception as e:                            # the first missing input names itself here
    sealed, error = None, f"{type(e).__name__}: {str(e)[:300]}"
report = dict(full=full, minimal=sealed, error=error,
              equal=sealed is not None and all(full[k] == sealed[k] for k in full if k != "image_sha256"),
              nonzero_bytes=sum(1 for b in memory if b), state_bytes=len(state_bytes), table_bytes=len(ds_table) + len(code_table))
json.dump(report, out, indent=1);out.close()
print(json.dumps(report, indent=1))
