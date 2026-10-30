"""T80: the sealed engine, the kit's check from goal2's state and GOAL.EXE's tables, with no image of the original.

The parent reads the reference image (E006-r0001) and makes goal2's state from it (Image.state_of), as goal2
passes its own; a child process, in which `import unicorn` fails and opening any .sav, .EXE or .DAT file raises,
runs the kit's check (engine, interactive, goals, knockout, family) on the port from that state and the tables
(static/goal-exe/tables) and must PASS every step against the recorded digests. Several CPU-hours on CPython:
its own CI group (tools/ci_gate.py, `seal`)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "static/goal-exe/tables"
STEPS = ("engine", "interactive", "goals", "knockout", "family")

# The child: Unicorn imports and opening the original's files both raise, proved before the check runs.
BOOTSTRAP = r"""
import builtins, io, os, sys, runpy
FORBIDDEN = ('.sav', '.exe', '.dat')
def forbidden(path):
    try:
        return os.fspath(path).lower().endswith(FORBIDDEN)
    except TypeError:
        return False
original_import, original_open, original_os_open = builtins.__import__, builtins.open, os.open
def guarded_import(name, *a, **kw):
    if name == 'unicorn' or name.startswith('unicorn.'):
        raise ImportError('positive Unicorn denial')
    return original_import(name, *a, **kw)
def guarded_open(file, *a, **kw):
    if forbidden(file):
        raise PermissionError(f'the sealed engine opened {file}')
    return original_open(file, *a, **kw)
def guarded_os_open(path, *a, **kw):
    if forbidden(path):
        raise PermissionError(f'the sealed engine opened {path}')
    return original_os_open(path, *a, **kw)
builtins.__import__, builtins.open, io.open, os.open = guarded_import, guarded_open, guarded_open, guarded_os_open
sys._goal2_unicorn_denied = True
for probe in (lambda: __import__('unicorn'), lambda: open('probe.sav', 'rb'), lambda: open('GOAL.EXE', 'rb'),
              lambda: os.open('x.DAT', os.O_RDONLY)):
    try:
        probe()
    except (ImportError, PermissionError):
        pass
    else:
        raise AssertionError('the denial did not take effect')
print('denied: unicorn, .sav, .EXE, .DAT', flush=True)
sys.argv = ['original_match.check'] + sys.argv[1:]
runpy.run_module('original_match.check', run_name='__main__')
"""


def failure_summary(report):
    """What a failed sealed check says first (#633): the report's path and each failed step's reasons, without
    the ports' call counters, which ran to more than the 3,000 characters of output the assertion kept."""
    lines = [f"report: {report}"]
    try:
        got = json.loads(Path(report).read_text())
    except (OSError, ValueError) as e:
        return "\n".join(lines + [f"no readable report: {e}"])
    for step, check in sorted(got.get("checks", {}).items()):
        if check.get("pass"):
            continue
        detail = check.get("detail")
        if isinstance(detail, dict):
            detail = {k: ({kk: vv for kk, vv in v.items() if kk != "port_calls"} if isinstance(v, dict) else v)
                      for k, v in detail.items()}
        lines.append(f"{step} failed: {json.dumps(detail)[:2000]}")
    return "\n".join(lines)


def reference_state():
    sys.path.insert(0, str(ROOT / "runtime"))
    from original_match import Image
    from original_match.assets import reference_image
    from original_match.port import tables
    return Image.from_savestate(reference_image(ROOT / ".cache/dl")).state(tables.load(TABLES))


class Sealed(unittest.TestCase):
    def test_the_check_passes_from_state_and_tables_alone(self):
        tmp = Path(tempfile.mkdtemp())
        state, report = tmp / "state.json", tmp / "report.json"
        state.write_text(json.dumps(reference_state()))
        env = dict(os.environ, PYTHONPATH=str(ROOT / "runtime"))
        run = subprocess.run([sys.executable, "-B", "-c", BOOTSTRAP, "--engine", "port", "--no-unicorn",
                              "--state", str(state), "--tables", str(TABLES), "--family", "--json", str(report)],
                             cwd=tmp, env=env, capture_output=True, text=True)
        self.assertIn("denied: unicorn, .sav, .EXE, .DAT", run.stdout, run.stderr[-3000:])
        self.assertEqual(run.returncode, 0, failure_summary(report) + "\n" + run.stdout[-3000:] + run.stderr[-3000:])
        got = json.loads(report.read_text())
        self.assertTrue(got.get("state"))
        self.assertEqual(sorted(got["checks"]), sorted(STEPS))
        for step in STEPS:
            self.assertTrue(got["checks"][step]["pass"], (step, got["checks"][step]))


class StateContract(unittest.TestCase):
    """Pure: no image. A state holds no byte of GOAL.EXE's load module, and other tables are refused."""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "runtime"))
        from original_match import image
        from original_match.port import tables
        self.image, self.tables = image, tables
        self.t = tables.load(TABLES)

    def fake(self, load=0x823):
        img = self.image.Image.__new__(self.image.Image)
        img.header, img.memory, img.load, img.DS, img.tables = bytes(0x78), bytearray(0x110000), load, load + 0x2581, None
        module = load * 16
        img.memory[module:module + self.tables.MODULE_SIZE] = b"\x5a" * self.tables.MODULE_SIZE   # "GOAL.EXE"
        self.t.place(img.memory, load)
        ds = module + 0x25810
        img.memory[ds + 0x7B62] ^= 0xFF                 # a byte the game changed after start-up
        img.memory[module + self.tables.MODULE_SIZE] = 7   # DS:7B70, a variable: state
        return img

    def test_the_state_leaves_the_module_out_and_from_state_restores_it(self):
        img = self.fake()
        state = img.state(self.t)
        self.assertEqual(state["initialised"], [[0x7B62, img.memory[img.load * 16 + 0x25810 + 0x7B62]]])
        import base64, zlib
        memory = zlib.decompress(base64.b64decode(state["memory"]))
        module = img.load * 16
        self.assertFalse(any(memory[module:module + self.tables.MODULE_SIZE]))
        self.assertEqual(memory[module + self.tables.MODULE_SIZE], 7)
        sealed = self.image.Image.from_state(state, self.t)
        expect = bytearray(img.memory)
        expect[module:module + self.tables.MODULE_SIZE] = bytes(self.tables.MODULE_SIZE)
        self.t.place(expect, img.load)
        expect[module + 0x25810 + 0x7B62] = img.memory[module + 0x25810 + 0x7B62]
        self.assertEqual(sealed.memory, expect)
        self.assertEqual(sealed.build_problems(), [])

    def test_a_state_with_module_bytes_or_other_tables_is_refused(self):
        state = self.fake().state(self.t)
        import base64, zlib
        memory = bytearray(zlib.decompress(base64.b64decode(state["memory"])))
        memory[0x823 * 16 + 5] = 1
        bad = dict(state, memory=base64.b64encode(zlib.compress(bytes(memory))).decode())
        with self.assertRaises(ValueError):
            self.image.Image.from_state(bad, self.t)
        other = dict(state, tables_sha256={"ds": "0" * 64, "code_data": "0" * 64})
        with self.assertRaises(self.tables.TablesError):
            self.image.Image.from_state(other, self.t)

    def test_tables_that_differ_from_their_manifest_are_refused(self):
        import shutil
        folder = Path(tempfile.mkdtemp()) / "t"
        shutil.copytree(TABLES, folder)
        text = (folder / "code_data.hex").read_text().splitlines()
        row = next(i for i, l in enumerate(text) if l and not l.startswith(";") and len(l.split("|")[0].split()) > 1)
        head, _, tail = text[row].partition("|")
        cells = head.split()
        cells[1] = f"{int(cells[1], 16) ^ 1:02X}"
        text[row] = f"{cells[0]}  {' '.join(cells[1:]):<95}  |{tail}"
        (folder / "code_data.hex").write_text("\n".join(text) + "\n")
        with self.assertRaises(self.tables.TablesError):
            self.tables.load(folder)


class FailureSummary(unittest.TestCase):
    """#633: a seed's exception comes first in a failed sealed check's message, whatever the ports' counters."""

    def test_the_exception_survives_long_port_counters(self):
        tmp = Path(tempfile.mkdtemp());report = tmp / "report.json"
        calls = {f"port_{i}": i for i in range(400)}
        self.assertGreater(len(json.dumps(calls)), 3000)
        report.write_text(json.dumps({"checks": {
            "engine": {"pass": True, "detail": {}},
            "family": {"pass": False, "detail": {"0xA1F0": {"stopped": "MemoryError: ", "port_calls": calls}}}}}))
        summary = failure_summary(report)
        self.assertIn(f"report: {report}", summary)
        self.assertIn('family failed: {"0xA1F0": {"stopped": "MemoryError: "}}', summary)
        self.assertNotIn("port_399", summary)
        self.assertNotIn("engine failed", summary)

    def test_a_missing_report_is_said(self):
        self.assertIn("no readable report", failure_summary(Path(tempfile.mkdtemp()) / "none.json"))


if __name__ == "__main__":
    unittest.main()
