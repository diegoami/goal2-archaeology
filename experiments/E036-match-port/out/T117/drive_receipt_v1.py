"""T117 receipt producer: E034-03's first straight drive (Fixture(7,19,index=9,kind=200), the
accepted checkpoint policy: quick answer at half time, the default elsewhere) on the plain port.

    python3 -B drive_receipt_v1.py --mode cpu  --out <new json>   # timing, no taps
    python3 -B drive_receipt_v1.py --mode taps --out <new json>   # equivalence hashes

Both record the ordered event records, the result, full memory and per-stretch CPU/wall times
(Match._advance). `taps` also hashes, in order, every io_tap call (memory reads, register reads
and sets, pc), write_tap call, site enter/leave and kit-listener enter/leave: the observable
behaviour T117 must keep. Unicorn imports are refused. The output is opened exclusively; the
source files are hashed before and after (a changed source fails the run). Diagnostic only."""
import argparse, builtins, hashlib, importlib.util, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ap = argparse.ArgumentParser()
ap.add_argument("--mode", choices=("cpu", "taps"), required=True)
ap.add_argument("--out", type=Path, required=True)
args = ap.parse_args()
out = args.out.open("x")
SOURCES = sorted((ROOT / "runtime/original_match").rglob("*.py")) + [
    ROOT / "experiments/E033-original-match-kit/save_boundaries.py", Path(__file__).resolve()]


def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES}


before = hashes()
real_import = builtins.__import__


def deny(name, *a, **k):
    if name == "unicorn" or name.startswith("unicorn."):
        raise ImportError("positive Unicorn denial")
    return real_import(name, *a, **k)


builtins.__import__ = deny
sys.path[:0] = [str(ROOT), str(ROOT / "runtime")]
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.assets import reference_image  # noqa: E402

spec = importlib.util.spec_from_file_location("boundaries", ROOT / "experiments/E033-original-match-kit/save_boundaries.py")
harness = importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)

stretches = []
advance = Match._advance


def timed(self):
    context = [self.st.get("phase"), self.st.get("stage"), self.st.get("minute")]
    wall, cpu = time.monotonic(), time.process_time()
    try:
        return advance(self)
    finally:
        stretches.append((context, time.process_time() - cpu, time.monotonic() - wall))


Match._advance = timed


class Recorder:
    """Every tap call, in order, into one hash."""
    def __init__(self):
        self.h, self.counts, self.token = hashlib.sha256(), {}, 0

    def add(self, kind, *values):
        self.counts[kind] = self.counts.get(kind, 0) + 1
        self.h.update(repr((kind,) + values).encode())

    def io(self, kind, a, b):
        self.add("io", kind, a, b if not isinstance(b, (bytes, bytearray)) else bytes(b))

    def write(self, linear, data):
        self.add("write", linear, bytes(data))

    def site_enter(self, linear, replay, fired=False):
        self.add("site_enter", linear, replay, fired)

    def site_leave(self, linear, stopped, fired=False):
        self.add("site_leave", linear, stopped, fired)

    def listen_enter(self, index, address, size, value):
        self.token += 1;self.add("listen_enter", index, address, size, value)
        return self.token

    def listen_leave(self, token):
        self.add("listen_leave", token)


m = Match(Image.from_savestate(reference_image(ROOT / ".cache/dl")), Fixture(7, 19, index=9, kind=200), managed=7,
          substitutions=None, engine="port", record_draws=True)
assert m.timeout_s == 60 and not hasattr(m.m, "_uc")
recorder = None
if args.mode == "taps":
    m.timeout_s = 10 ** 6  # the taps' own cost must not trip the guard; the cpu mode keeps 60 s
    recorder = Recorder()
    m.m.io_tap, m.m.write_tap, m.m.site_tap, m.m.listen_tap = recorder.io, recorder.write, recorder, recorder


def policy(match, data):
    match.answer(quick=True) if data["context"] == "half_time" else match.answer()


cpu0, wall0 = time.process_time(), time.monotonic()
events = harness.drive(m, policy, ())
cpu, wall = time.process_time() - cpu0, time.monotonic() - wall0
assert "unicorn" not in sys.modules
result = m.result()
digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()
longest = max(stretches, key=lambda s: s[1])
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
receipt = dict(mode=args.mode, head=head, python=sys.version, events=len(events), events_sha256=digest(events),
               score=result.get("score"), draws=result.get("draws"), result_sha256=digest(result),
               memory_sha256=hashlib.sha256(m.m.read(0, 0x110000)).hexdigest(),
               drive_cpu_s=cpu, drive_wall_s=wall, stretches=len(stretches),
               longest_stretch=dict(context=longest[0], cpu_s=longest[1], wall_s=longest[2]),
               stretches_over_1s=[dict(context=c, cpu_s=p, wall_s=w) for c, p, w in stretches if p > 1],
               taps=None if recorder is None else dict(sha256=recorder.h.hexdigest(), counts=recorder.counts),
               source_sha256=before, source_unchanged=before == hashes(), diagnostic_not_acceptance=True)
json.dump(receipt, out, indent=2);out.close()
print(json.dumps({k: receipt[k] for k in ("mode", "events", "score", "drive_cpu_s", "longest_stretch", "taps")}, default=str))
sys.exit(0 if receipt["source_unchanged"] else 2)
