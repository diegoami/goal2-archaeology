"""E008 (T19, Q005): the one-byte savestate edit (runtime/driver/savestate.py with_memory), the ranks
and rating of experiments/E008-*/summarise.py, and the listing filter of experiments/E008-*/readers.py.

The synthetic savestate is written here with literal offsets (F001: guest address 0 at offset 0x78 of
the inflated Memory component), not from the module; the GOAL.DAT blocks are planted at the offsets
static/goal-dat/blocks.tsv gives (blocks 8 and 9: 0xA0F2 and 0xA173, 129 one-byte records)."""
import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402

HERE = ROOT / "experiments" / "E008-q005-r008-tactics"
sys.path.insert(0, str(HERE))


def load_by_path(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


summarise = load_by_path("e008_summarise", "experiments/E008-q005-r008-tactics/summarise.py")
readers = load_by_path("e008_readers", "experiments/E008-q005-r008-tactics/readers.py")

TRAILER = b"\x01\x02\x03\x04\x05\x06\x07\x08"   # DOSBox-X writes 8 bytes after the Memory stream


def synthetic(mem):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("CPU", b"cpu bytes", compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("Memory", zlib.compress(b"\0" * 0x78 + mem, 1) + TRAILER, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("Vga", zlib.compress(b"\0" * 16), compress_type=zipfile.ZIP_STORED)
    return buf.getvalue()


class WithMemory(unittest.TestCase):
    def setUp(self):
        self.mem = bytes(range(256)) * 16
        self.data = synthetic(self.mem)

    def test_edits_only_the_named_bytes(self):
        out = savestate.with_memory(self.data, 0x123, b"\xee")
        got = savestate.Savestate(out).memory(0, len(self.mem))
        want = bytearray(self.mem)
        want[0x123] = 0xEE
        self.assertEqual(got, bytes(want))

    def test_other_components_order_compression_and_trailer_kept(self):
        out = savestate.with_memory(self.data, 0, b"\x99\x98")
        a, b = zipfile.ZipFile(io.BytesIO(self.data)), zipfile.ZipFile(io.BytesIO(out))
        self.assertEqual([(i.filename, i.compress_type) for i in a.infolist()], [(i.filename, i.compress_type) for i in b.infolist()])
        for n in ("CPU", "Vga"):
            self.assertEqual(a.read(n), b.read(n))
        d = zlib.decompressobj()
        d.decompress(b.read("Memory"))
        self.assertEqual(d.unused_data, TRAILER)

    def test_outside_memory_refused(self):
        with self.assertRaises(ValueError):
            savestate.with_memory(self.data, len(self.mem), b"\x00")
        with self.assertRaises(ValueError):            # the run's end reaches past memory
            savestate.with_memory(self.data, len(self.mem) - 1, b"\x00\x00")
        with self.assertRaises(ValueError):
            savestate.with_memory(self.data, -1, b"\x00")
        out = savestate.with_memory(self.data, len(self.mem) - 1, b"\x77")   # the last byte is inside
        self.assertEqual(savestate.Savestate(out).memory(len(self.mem) - 1, 1), b"\x77")


class Ranks(unittest.TestCase):
    def dat(self, order8, order9):
        b = bytearray(0xA1F4)
        b[0xA0F2 + 1:0xA0F2 + 129] = bytes(order8)
        b[0xA173 + 1:0xA173 + 129] = bytes(order9)
        return bytes(b)

    def test_positions_become_ranks(self):
        order8 = list(range(128, 0, -1))           # world rank k is country 129 - k
        order9 = list(range(1, 129))               # continent position i is country i
        rk = summarise.ranks(self.dat(order8, order9))
        self.assertEqual(rk[1], (1, 128, 1))
        self.assertEqual(rk[33], (1, 96, 2))       # position 33: first of continent 2
        self.assertEqual(rk[128], (32, 1, 4))

    def test_not_a_permutation_refused(self):
        with self.assertRaises(ValueError):
            summarise.ranks(self.dat([1] * 128, list(range(1, 129))))

    def test_rating_formula(self):
        # 1771:10E7 at world 1, continent 1, rank 1: ((5-1)*(33-1) + (129-1)) // 2 = 128
        self.assertEqual(summarise.rating(1, 1, 1), 128)
        self.assertEqual(summarise.rating(32, 128, 4), (1 * 1 + 1) // 2)

    def test_order(self):
        rows = [{"continent": k, "mean": m} for k, m in ((1, 4.0), (2, 3.0), (3, 2.0), (4, 1.0))]
        self.assertTrue(summarise.order_holds(rows))
        rows[1]["mean"] = 1.5
        self.assertFalse(summarise.order_holds(rows))
        rows[1]["mean"] = 2.0                      # a tie is not the order
        self.assertFalse(summarise.order_holds(rows))

    def test_e006_means_skip_records_not_completed(self):
        def record(run_id, status, plus3):
            arr = bytearray(20 * 3061)
            for p in range(1, 2561):
                arr[20 * p] = (p - 1) // 20 + 1
                arr[20 * p + 3] = plus3
            return {"run_id": run_id, "status": status,
                    "observations": [{"field": "player array: hex", "value": arr.hex()}]}
        with tempfile.TemporaryDirectory() as t:
            Path(t, "E006-r0001.json").write_text(json.dumps(record("E006-r0001", "aborted: x", 0x10)))
            Path(t, "E006-r0002.json").write_text(json.dumps(record("E006-r0002", "completed", 0x90)))
            run_id, means = summarise.e006_plus3(t)
        self.assertEqual(run_id, "E006-r0002")
        self.assertEqual(means[1], 0x90)
        self.assertEqual(len(means), 128)


LISTING = """; header lines before the first routine are not code of any routine
0000  C4 3E 17 A9     les di, ptr [0xa917]
0000  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
; ---- routine 1771:0001  (found by: call)
0001  C4 3E 17 A9     les di, ptr [0xa917]
0005  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
; ---- routine 1771:0010  (found by: call)
0010  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
; ---- routine 1771:0020  (found by: call)
0020  C4 3E 1B A9     les di, ptr [0xa91b]
0024  81 C7 0F 00     add di, 0xf
0028  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
"""


class Readers(unittest.TestCase):
    def test_access_counted_only_with_its_array_pointer(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "seg_1771_01.asm").write_text(LISTING)
            got = readers.scan(t)
        self.assertEqual(sorted(got), ["1771:0001", "1771:0020"])
        self.assertEqual(got["1771:0001"], {"+0x2D": [("seg_1771_01.asm", 6)]})
        self.assertEqual(got["1771:0020"], {"+0xF": [("seg_1771_01.asm", 11)]})

    def test_reach_follows_edges(self):
        g = {"a": {"b"}, "b": {"c"}, "c": set(), "d": {"a"}}
        import collections
        g = collections.defaultdict(set, g)
        self.assertEqual(readers.reach(g, "a"), {"a", "b", "c"})


# ---- the runner (experiments/E008-*/run.py), with a fake driver ----------------------------------
import contextlib  # noqa: E402
import json  # noqa: E402
import types  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, str(ROOT / "tests"))
from test_driver_dataseg import DS_BASE, memory_image  # noqa: E402

run = load_by_path("e008_run", "experiments/E008-q005-r008-tactics/run.py")

COUNTRIES_AT = (0x7400, 0x0030)                       # segment, offset of the planted country array
FIELD_AT = COUNTRIES_AT[0] * 16 + COUNTRIES_AT[1] + 0xBF * 7 + 0x2D   # country 7, byte +0x2D
R008_DENMARK = 0x8B


def captain_bytes():
    mem = bytearray(memory_image())
    mem[DS_BASE + 0xA917:DS_BASE + 0xA91B] = COUNTRIES_AT[1].to_bytes(2, "little") + COUNTRIES_AT[0].to_bytes(2, "little")
    mem[FIELD_AT] = R008_DENMARK
    buf = io.BytesIO()      # deflated at level 9: any rewrite of the Memory component changes the zip's bytes
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Memory", zlib.compress(b"\0" * 0x78 + bytes(mem), 9) + TRAILER, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("Vga", zlib.compress(b"\0" * 16), compress_type=zipfile.ZIP_STORED)
    return buf.getvalue()


class FakeScreen:
    def __init__(self, last_row):
        self.last_row = last_row

    def lines(self):
        return [""] * 24 + [self.last_row]

    def text(self):
        return self.last_row

    def digest(self):
        return "digest-" + self.last_row


class FakeDriver:
    """Driver's surface as Run.go uses it. `stale_restore`: Host+L leaves the captain-screen state in
    place instead of loading the arm's savestate (the failure the read-back check exists for)."""

    def __init__(self, cap, last_row="CAPTAIN", stale_restore=False):
        self.cap, self.last_row, self.stale = cap, last_row, stale_restore
        self.current, self.last, self.launched, self.events = cap, None, None, []
        self.game_dir, self.restored = Path("/nonexistent/game"), None

    def launch(self, st):
        self.last = ({"utc": "t"}, savestate.Savestate(self.cap))
        return FakeScreen("main")

    def keys(self, *k):
        pass

    def settle(self, prev, what=""):
        return FakeScreen(self.last_row)

    def read(self):
        st = savestate.Savestate(self.current)
        self.last = ({"utc": "t"}, st)
        return {"utc": "t"}, st, self.current

    def drive_layout(self):
        return ["mount c <game>"]

    def restore(self, st):
        self.restored = st.path.read_bytes()
        if not self.stale:
            self.current = self.restored

    def terminate(self):
        return True


def _outside_checkout():
    t = Path(tempfile.gettempdir()).resolve()
    return None if run.ROOT.resolve() not in (t, *t.parents) else "/tmp"


class Runner(unittest.TestCase):
    def setUp(self):
        # outside the checkout whatever TMPDIR is: a scratch inside it would contain ROOT, and the
        # record's own leak check (cycle.py) would refuse every record (#80, #100)
        self.tmp = tempfile.TemporaryDirectory(dir=_outside_checkout())
        self.addCleanup(self.tmp.cleanup)

    def go(self, arm, batch="t", **fake):
        tmp = Path(self.tmp.name)
        d = FakeDriver(captain_bytes(), **fake)
        start = types.SimpleNamespace(name="e006-test", sha256="0" * 64, screen_digest="digest-main")
        real_start_state = run.driver.StartState
        args = types.SimpleNamespace(state="e006-test", batch=batch, argv=["quick"])
        with contextlib.ExitStack() as s:
            s.enter_context(mock.patch.object(run.driver, "StartState",
                                              lambda name, states=None: real_start_state(name, states) if states else start))
            s.enter_context(mock.patch.object(run.driver, "Driver", lambda *a, **k: d))
            s.enter_context(mock.patch.object(run.driver, "SCRATCH", tmp / "scratch"))
            s.enter_context(mock.patch.object(run.driver, "verify_release", lambda cache: "set"))
            s.enter_context(mock.patch.object(run, "OUT", tmp / "runs"))
            s.enter_context(mock.patch.object(run.cycle, "machine_id", lambda: "m"))
            s.enter_context(mock.patch.object(run.cycle, "fingerprint", lambda *a: {}))
            s.enter_context(mock.patch.object(run.match, "play", lambda *a, **k: (None, 1, 0.5)))
            s.enter_context(mock.patch.object(run.Run, "add_full", lambda self, label, read: None))
            s.enter_context(contextlib.redirect_stderr(io.StringIO()))
            s.enter_context(contextlib.redirect_stdout(io.StringIO()))
            ok = run.Run(1, arm, args, "c0ffee").go()
        rec = json.loads((tmp / "runs" / "E008-r0001.json").read_text())
        return ok, rec, d

    def value(self, rec, prefix):
        return next(o["value"] for o in rec["observations"] if o.get("field", "").startswith(prefix))

    def test_edited_arm_loads_the_xor_and_completes(self):
        ok, rec, d = self.go("edited")
        self.assertTrue(ok, rec["status"])
        self.assertEqual(savestate.Savestate(d.restored).memory(FIELD_AT, 1)[0], R008_DENMARK ^ 0x31)
        self.assertEqual(self.value(rec, "country 7 byte +0x2D read back"), f"0x{R008_DENMARK ^ 0x31:02x}")
        self.assertEqual(rec["interventions"][-1]["level"], "I3")

    def test_unchanged_arm_loads_the_captain_state_as_saved(self):
        ok, rec, d = self.go("unchanged")
        self.assertTrue(ok, rec["status"])
        self.assertEqual(d.restored, d.cap)
        self.assertNotIn("I3", [i["level"] for i in rec["interventions"]])

    def test_a_byte_that_did_not_load_aborts_the_run(self):
        ok, rec, _ = self.go("edited", stale_restore=True)
        self.assertFalse(ok)
        self.assertIn("reads 0x8b after the load, 0xba was written", rec["status"])

    def test_not_at_the_captain_screen_aborts_the_run(self):
        ok, rec, d = self.go("edited", last_row="something else")
        self.assertFalse(ok)
        self.assertIn("not at the captain screen", rec["status"])
        self.assertIsNone(d.restored)

    def test_a_record_is_never_overwritten(self):
        self.go("unchanged")
        with self.assertRaises(FileExistsError):
            self.go("unchanged")

    def test_a_host_path_in_the_record_is_refused(self):
        host = str(Path(self.tmp.name) / "host")
        self.go("unchanged", batch=host)      # ROOT not in the record: written
        with mock.patch.object(run, "ROOT", Path(host)):
            with self.assertRaises(SystemExit):
                self.go("unchanged", batch=host)

    def test_unknown_arm_refused(self):
        started = []
        with mock.patch.object(run, "git", lambda *a: ""), mock.patch.object(run, "Run", lambda *a: started.append(a)):
            with self.assertRaises(SystemExit):
                run.main(["quick", "--state", "x", "--arms", "unchanged,other"])
        self.assertEqual(started, [])

    def test_uncommitted_changes_refused(self):
        started = []
        with mock.patch.object(run, "git", lambda *a: " M runtime/driver/driver.py"), \
                mock.patch.object(run, "Run", lambda *a: started.append(a)):
            with self.assertRaises(SystemExit):
                run.main(["quick", "--state", "x", "--arms", "unchanged"])
        self.assertEqual(started, [])


if __name__ == "__main__":
    unittest.main()
