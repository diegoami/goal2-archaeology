"""T80a M1 over a family: the port's inputs (read before written while it dispatches) over matches.

    chunk:  PYTHONPATH=runtime pypy3.11 -B .../read_map_family_v1.py chunk --only ID,... --ranges <new json> --records <new jsonl>
    union:  PYTHONPATH=runtime python3 -B .../read_map_family_v1.py union --exe GOAL.EXE --out <new json> <ranges.json>...

`chunk` installs read_map_v1.py's tracing (PortMachine._bounds, write_as, write; reads counted only
while PortMachine.run dispatches, up to 4 KiB, before the byte is written in that match) and runs
family.py itself (one worker, in process, --engine port) on the given matches, then writes the
positions read as ranges (positions only). Its records go to --records (a scratch log, ordinary
family.py output). `union` merges chunks and classifies the union like read_map_v1.py, against the
unpacked GOAL.EXE and the reference image (E006-r0001) for the code and the initialised data.
"""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT), str(ROOT / "runtime"), str(ROOT / "experiments/E036-match-port"), str(ROOT / "tools/static")]


def ranges(addresses):
    out, start, prev = [], None, None
    for x in addresses:
        if start is None: start = prev = x
        elif x == prev + 1: prev = x
        else: out.append([start, prev - start + 1]); start = prev = x
    if start is not None: out.append([start, prev - start + 1])
    return out


def chunk(a):
    from original_match.machine import MEM_SIZE
    from original_match.port.engine import PortMachine
    out = open(a.ranges, "x")
    inputs = bytearray(MEM_SIZE)
    state = {"in_write": 0, "written": None, "running_machine": None}
    bounds, write_as, write, run = PortMachine._bounds, PortMachine.write_as, PortMachine.write, PortMachine.run

    def traced_run(self, *args, **kw):
        if state["running_machine"] is not self:            # a new match: its own "written" map
            state["running_machine"], state["written"] = self, bytearray(MEM_SIZE)
        return run(self, *args, **kw)

    def traced_bounds(linear, n):
        bounds(linear, n)
        m = state["running_machine"]
        if state["in_write"] or m is None or not m.running or n > 0x1000:
            return
        written = state["written"]
        for i in range(linear, linear + n):
            if not written[i]:
                inputs[i] = 1

    def mark(linear, n):
        if state["written"] is not None:
            for i in range(linear, linear + n):
                state["written"][i] = 1

    def traced_write_as(self, linear, size, value, at):
        state["in_write"] += 1
        try: return write_as(self, linear, size, value, at)
        finally: state["in_write"] -= 1; mark(linear, size)

    def traced_write(self, linear, data):
        state["in_write"] += 1
        try: return write(self, linear, data)
        finally: state["in_write"] -= 1; mark(linear, len(bytes(data)))

    PortMachine._bounds = staticmethod(traced_bounds)
    PortMachine.write_as, PortMachine.write, PortMachine.run = traced_write_as, traced_write, traced_run
    import family
    code = family.main(["--family", "ALL", "--engine", "port", "--workers", "1", "--only", a.only, "--out", a.records])
    json.dump(dict(only=a.only.split(","), family_exit=code, ranges=ranges([x for x in range(MEM_SIZE) if inputs[x]])), out)
    out.close()
    return 0


def union(a):
    from original_match import Image, build
    from original_match.assets import reference_image
    import unlzexe
    out = open(a.out, "x")
    addrs, ids = set(), []
    for path in a.chunks:
        c = json.loads(Path(path).read_text());ids += c["only"]
        for start, n in c["ranges"]:
            addrs.update(range(start, start + n))
    image = Image.from_savestate(reference_image(ROOT / ".cache/dl"))
    memory = image.memory if hasattr(image, "memory") else image.memory_component()
    raw = Path(a.exe).read_bytes();unpacked = unlzexe.unpack(raw)
    header = int.from_bytes(unpacked[8:10], "little") * 16;exe = unpacked[header:]
    count, table = int.from_bytes(unpacked[6:8], "little"), int.from_bytes(unpacked[0x18:0x1A], "little")
    relocated = set()
    for k in range(count):
        off = int.from_bytes(unpacked[table + 4 * k:table + 4 * k + 2], "little")
        seg = int.from_bytes(unpacked[table + 4 * k + 2:table + 4 * k + 4], "little")
        relocated.update((seg * 16 + off, seg * 16 + off + 1))
    code0, ds0 = image.load * 16, image.DS * 16
    regions = {"code": (code0, ds0), "initialised data": (ds0, ds0 + 0x7B70), "rest of DS": (ds0 + 0x7B70, ds0 + 0x10000)}
    report = dict(matches=len(ids), exe_sha256=hashlib.sha256(raw).hexdigest(), input_bytes=len(addrs), regions={})
    claimed = set()
    for name, (lo, hi) in regions.items():
        inside = sorted(x for x in addrs if lo <= x < hi);claimed.update(inside)
        entry = dict(input_bytes=len(inside))
        if name != "rest of DS":
            same = [x for x in inside if (x - code0) not in relocated and memory[x] == exe[x - code0]]
            differ = [x for x in inside if (x - code0) not in relocated and memory[x] != exe[x - code0]]
            entry.update(equal_to_exe=len(same), differ_from_exe=len(differ),
                         relocated=len([x for x in inside if (x - code0) in relocated]),
                         table_ranges=[[x - code0, n] for x, n in ranges(same)],
                         differ_ranges=[[hex(x - lo), n] for x, n in ranges(differ)])
            if name == "initialised data":
                measured = {ds0 + o + i for o, n in build.DATA_RANGES for i in range(n)}
                entry.update(outside_build_ranges=len(set(inside) - measured), build_not_read=len(measured - set(inside)))
        else:
            entry["ranges"] = [[hex(x - lo), n] for x, n in ranges(inside)]
        report["regions"][name] = entry
    rest = sorted(x for x in addrs if x not in claimed)
    report["regions"]["elsewhere"] = dict(input_bytes=len(rest), ranges_count=len(ranges(rest)))
    json.dump(report, out, indent=1);out.close()
    print(json.dumps({k: v for k, v in report.items() if k != "regions"}))
    for name, e in report["regions"].items():
        print(name, {k: v for k, v in e.items() if not k.endswith("ranges")})
    return 0


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
c = sub.add_parser("chunk");c.add_argument("--only", required=True);c.add_argument("--ranges", required=True)
c.add_argument("--records", required=True)
u = sub.add_parser("union");u.add_argument("--exe", required=True);u.add_argument("--out", required=True)
u.add_argument("chunks", nargs="+")
a = ap.parse_args()
sys.exit(chunk(a) if a.cmd == "chunk" else union(a))
