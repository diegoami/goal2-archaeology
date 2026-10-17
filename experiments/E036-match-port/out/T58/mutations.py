"""Mutations of the port mode on a scratch copy of the tree: each must make tests.test_port_mode fail (T58).

    python3 -B experiments/E036-match-port/out/T58/mutations.py COPY   # COPY/runtime/original_match, COPY/tests

Each mutation is written into the copy, the test module run there, and the file's saved contents written back."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
MACHINE = ROOT / "runtime" / "original_match" / "machine.py"
PORT = ROOT / "runtime" / "original_match" / "port" / "__init__.py"
MUTATIONS = [
    ("write_as reaches no listener", MACHINE, "                if begin <= linear <= end:\n                    fn(linear, size, value)",
     "                if False:\n                    fn(linear, size, value)"),
    ("fire runs no hook", MACHINE, "            for h in list(self._handlers.get(lin, ())):\n                h(False)",
     "            for h in []:\n                h(False)"),
    ("a port runs after a stopping hook", MACHINE, "                    else:                       # a port runs",
     "                    if True:                       # a port runs"),
    ("a stop inside a port resumes as a replay", MACHINE, "self._resume_lin = None if fresh or start == self.no_replay_at else start",
     "self._resume_lin = None if fresh else start"),
    ("a stub's value is dropped", PORT, "        if value is not None:\n            value = int(value)",
     "        if False:\n            value = int(value)"),
    ("a decision inside a port is deferred", ROOT / "runtime" / "original_match" / "port" / "mem.py",
     'DEFERRABLE_STOPS = (None, "events")', 'DEFERRABLE_STOPS = (None, "events", "decision")'),
]
bad = 0
for name, path, old, new in MUTATIONS:
    saved = path.read_text()
    assert saved.count(old) == 1, name
    try:
        path.write_text(saved.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_mode"], cwd=ROOT,
                           capture_output=True, text=True)
        failed = [l for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        print(f"{'caught' if r.returncode else 'MISSED'}  {name}: {failed}")
        bad += not r.returncode
    finally:
        path.write_text(saved)
sys.exit(1 if bad else 0)
