"""T80b M1 probe over a family: every match from its image reduced to T80a's tables plus the state bytes.

    chunk:   PYTHONPATH=runtime pypy3.11 -B .../probe_family_v1.py chunk --only ID,... --records <new jsonl>
    compare: PYTHONPATH=runtime python3 -B .../probe_family_v1.py compare <records.jsonl>...

`chunk` runs family.py in process (one worker, --engine port) with image_sources.load replaced: each
image it hands out is zero except T80a's tables and the family read map's state bytes, taken from that
image (minimal_image_v1.py's construction); an image whose load segment is not the reference's is
refused, since the read map's positions are the reference's. The build guard is bypassed (the probe
zeroes the code on purpose), and so is the registered source's memory digest\n(image_sources.validate_image), which the reduced image cannot match. `compare` runs compare.py's own check on the records under the strict
display profile against its bound reference, with the image binding left out: every record names its
input image by digest, and these inputs are the reduced images by design.
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT), str(ROOT / "runtime"), str(ROOT / "experiments/E036-match-port"), str(ROOT / "tools/static")]


def reducer():
    import port_tables
    from original_match import Image
    from original_match.assets import reference_image
    manifest = json.loads(port_tables.MANIFEST.read_text())
    ds_table, code_table = port_tables.read_tables(port_tables.TABLES)
    reference = Image.from_savestate(reference_image(ROOT / ".cache/dl"))
    state = set()
    for chunk in sorted((ROOT / "experiments/E036-match-port/out/T80/a").glob("read-map-family-v1.chunk-*.json")):
        for s, n in json.loads(chunk.read_text())["ranges"]:
            state.update(range(s, s + n))
    code0, ds0 = reference.load * 16, reference.DS * 16
    tables = {ds0 + i for i in range(len(ds_table))} | {code0 + o + i for o, n in manifest["code_data"] for i in range(n)}
    keep = sorted(x for x in state if x not in tables) + [ds0 + 0x7968]

    def reduce(image):
        if image.load != reference.load:
            raise SystemExit(f"refused: an image loaded at {image.load:#x}, not the reference's {reference.load:#x}")
        source, memory = bytes(image.memory), bytearray(len(image.memory))
        memory[ds0:ds0 + len(ds_table)] = ds_table
        at = 0
        for off, n in manifest["code_data"]:
            memory[code0 + off:code0 + off + n] = code_table[at:at + n];at += n
        for x in keep:
            memory[x] = source[x]
        image.memory = memory
        return image
    return reduce


def chunk(a):
    import image_sources, family
    from original_match import Image
    reduce, load = reducer(), image_sources.load
    image_sources.load = lambda key, cache: reduce(load(key, cache))
    # The reduced image differs on purpose from what both guards check: the build guard (GOAL.EXE's code) and
    # the registered source's memory digest. Both are bypassed in this probe only.
    Image.build_problems = lambda self: []
    image_sources.validate_image = lambda image, key: None
    return family.main(["--family", "ALL", "--engine", "port", "--workers", "1", "--only", a.only, "--out", a.records])


def compare_records(a):
    import compare, families
    cand = {}
    for path in a.records:
        cand.update(compare.load(Path(path)))
    declared = families.discover()
    chosen = [f for f in families.select("ALL", declared) if f.name != "A700"]
    expected = {mid: d for f in chosen for mid, d in f.expected().items()}
    profile = compare.candidate_display_profile(cand, True)
    ref_path = ROOT / profile["reference"] if profile else None
    ref = compare.load(ref_path) if ref_path else {}
    ref = {mid: r for mid, r in ref.items() if mid in expected}
    lines, ok = compare.check(ref, cand, expected, "identical", True, None, strict_display=profile is not None)
    print(f"strict display profile: {profile is not None}; reference {profile['reference'] if profile else None}")
    print("\n".join(lines[-3:]))
    return 0 if ok else 1


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
c = sub.add_parser("chunk");c.add_argument("--only", required=True);c.add_argument("--records", required=True)
p = sub.add_parser("compare");p.add_argument("records", nargs="+")
a = ap.parse_args()
sys.exit(chunk(a) if a.cmd == "chunk" else compare_records(a))
