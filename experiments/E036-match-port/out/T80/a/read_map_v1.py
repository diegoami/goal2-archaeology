"""T80a M1: what the plain port reads, and whether GOAL.EXE holds it.

    PYTHONPATH=runtime pypy3.11 -B experiments/E036-match-port/out/T80/a/read_map_v1.py \
        --exe .cache/artifacts/goal2-a949da2f/GOAL.EXE --out <new json> [--match e034-03|f40-0101]

Plays one match on the port from the reference image (E034-03's straight drive, or F40's first
seed), marking every guest byte the port reads before it writes it in that match (through
PortMachine._bounds, which every read and write passes, and write_as/write, which mark writes).
Those bytes are the engine's inputs. Each is placed in a region of the image: the code
(load:0000 .. +0x25810), the initialised data (DS:0000..7B6F), the rest of DS, and the rest of
memory. For the code and the initialised data, each input byte is compared with the unpacked
GOAL.EXE (tools/static/unlzexe.py; the code's relocated words are left out): equal means a
candidate for T80a's tables, different means set up before the match (records or state). Positions,
counts and digests only: no byte of the original is written. Diagnostic for T80a.
"""
import argparse, hashlib, importlib.util, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
ap = argparse.ArgumentParser()
ap.add_argument("--exe", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--match", choices=("e034-03", "f40-0101"), default="e034-03")
a = ap.parse_args()
out = open(a.out, "x")
sys.path[:0] = [str(ROOT), str(ROOT / "runtime"), str(ROOT / "tools/static")]
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.assets import reference_image  # noqa: E402
from original_match.machine import MEM_SIZE  # noqa: E402
from original_match.port.engine import PortMachine  # noqa: E402
from original_match import build  # noqa: E402
import unlzexe  # noqa: E402

spec = importlib.util.spec_from_file_location("boundaries", ROOT / "experiments/E033-original-match-kit/save_boundaries.py")
harness = importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)

written = bytearray(MEM_SIZE)          # 1: written in this match
inputs = bytearray(MEM_SIZE)           # 1: read before any write in this match
state = {"in_write": 0, "machine": None}
bulk = {}                              # reads over 4 KiB (snapshots, digests): counted apart, not inputs
outside = {"reads": 0, "bytes": 0}     # reads while the dispatcher is not running (the kit between events)
bounds, write_as, write = PortMachine._bounds, PortMachine.write_as, PortMachine.write


def traced_bounds(linear, n):
    bounds(linear, n)
    if not state["in_write"]:
        machine = state["machine"]
        if machine is not None and not machine.running:
            outside["reads"] += 1;outside["bytes"] += n
            return
        if n > 0x1000:
            bulk[(linear, n)] = bulk.get((linear, n), 0) + 1
            return
        for i in range(linear, linear + n):
            if not written[i]:
                inputs[i] = 1


def traced_write_as(self, linear, size, value, at):
    state["in_write"] += 1
    try:
        return write_as(self, linear, size, value, at)
    finally:
        state["in_write"] -= 1
        for i in range(linear, linear + size):
            written[i] = 1


def traced_write(self, linear, data):
    state["in_write"] += 1
    try:
        return write(self, linear, data)
    finally:
        state["in_write"] -= 1
        for i in range(linear, linear + len(bytes(data))):
            written[i] = 1


PortMachine._bounds = staticmethod(traced_bounds)
PortMachine.write_as, PortMachine.write = traced_write_as, traced_write

image = Image.from_savestate(reference_image(ROOT / ".cache/dl"))
if a.match == "e034-03":
    m = Match(image, Fixture(7, 19, index=9, kind=200), managed=7, substitutions=None, engine="port", record_draws=True)
else:
    m = Match(image, Fixture(7, 19, index=21, kind=1), managed=7, seed=257, record_draws=True, delay_byte=0, engine="port")
start_memory = bytes(m.m._memory)
state["machine"] = m.m
load, ds = image.load, image.DS
t = time.process_time()
def policy(match, d): match.answer(quick=True) if d["context"] == "half_time" else match.answer()
events = harness.drive(m, policy, ())
cpu = time.process_time() - t

raw = Path(a.exe).read_bytes()
unpacked = unlzexe.unpack(raw)
header = int.from_bytes(unpacked[8:10], "little") * 16
exe_image = unpacked[header:]
relocated = set()
count = int.from_bytes(unpacked[6:8], "little"); table = int.from_bytes(unpacked[0x18:0x1A], "little")
for k in range(count):
    off, seg = int.from_bytes(unpacked[table + 4 * k:table + 4 * k + 2], "little"), int.from_bytes(unpacked[table + 4 * k + 2:table + 4 * k + 4], "little")
    p = seg * 16 + off;relocated.update((p, p + 1))

code0, code1 = load * 16, load * 16 + build.CODE_SIZE
ds0 = ds * 16;init1, ds1 = ds0 + 0x7B70, ds0 + 0x10000
regions = {"code": (code0, min(code1, ds0)), "initialised data": (ds0, init1), "rest of DS": (init1, ds1)}


def ranges(addresses):
    out, start, prev = [], None, None
    for x in addresses:
        if start is None: start = prev = x
        elif x == prev + 1: prev = x
        else: out.append((start, prev - start + 1)); start = prev = x
    if start is not None: out.append((start, prev - start + 1))
    return out


report = {"match": a.match, "events": len(events), "result_score": m.result()["score"], "port_cpu_s": round(cpu, 1),
          "exe_sha256": hashlib.sha256(raw).hexdigest(), "unpacked_sha256": hashlib.sha256(unpacked).hexdigest(),
          "load": load, "ds": ds, "input_bytes": sum(inputs), "written_bytes": sum(written), "regions": {},
          "bulk_reads": [dict(linear=hex(k[0]), n=k[1], times=v) for k, v in bulk.items()],
          "reads_outside_dispatch": outside,
          "counted": "reads made while PortMachine.run dispatches, up to 4 KiB each, before the byte is written"}
claimed = set()
for name, (lo, hi) in regions.items():
    addrs = [x for x in range(lo, hi) if inputs[x]]
    claimed.update(addrs)
    entry = {"input_bytes": len(addrs)}
    if name in ("code", "initialised data"):
        same = [x for x in addrs if (x - code0) not in relocated and (x - code0) < len(exe_image) and start_memory[x] == exe_image[x - code0]]
        differ = [x for x in addrs if (x - code0) not in relocated and (x - code0) < len(exe_image) and start_memory[x] != exe_image[x - code0]]
        reloc = [x for x in addrs if (x - code0) in relocated]
        entry.update(equal_to_exe=len(same), differ_from_exe=len(differ), relocated_words=len(reloc),
                     differ_ranges=[(hex(x - lo), n) for x, n in ranges(differ)][:400],
                     equal_ranges_count=len(ranges(same)))
        if name == "initialised data":
            measured = {x for off, n in build.DATA_RANGES for x in range(ds0 + off, ds0 + off + n)}
            entry.update(in_build_ranges=len(set(addrs) & measured), outside_build_ranges=len(set(addrs) - measured),
                         build_ranges_not_read=len(measured - set(addrs)),
                         outside_ranges=[(hex(x - lo), n) for x, n in ranges(sorted(set(addrs) - measured))][:400])
    else:
        entry["ranges"] = [(hex(x - lo), n) for x, n in ranges(addrs)][:400]
    report["regions"][name] = entry
other = [x for x in range(MEM_SIZE) if inputs[x] and x not in claimed]
report["regions"]["elsewhere"] = {"input_bytes": len(other), "ranges": [(hex(x), n) for x, n in ranges(other)][:400]}
json.dump(report, out, indent=1);out.close()
print(json.dumps({k: (v if k != "regions" else {r: {kk: vv for kk, vv in e.items() if not kk.endswith("ranges")} for r, e in v.items()}) for k, v in report.items()}, indent=1))
