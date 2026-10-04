"""The driver's savestate parser and record observations, on a synthetic savestate built here.

No DOSBox-X and no original file: the zip below has the two components the parser reads, with the
text page and guest memory placed at the offsets F001 measured, written as literals (not taken from
the parser), so a parser whose offset moves by one byte reads other bytes and these tests fail."""
import io
import json
import re
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import cycle  # noqa: E402
import driver  # noqa: E402
import savestate  # noqa: E402

TEXT_BASE = 0x86024   # F001: text page offset in the inflated Vga component
MEM_BASE = 0x78       # F001: guest physical address 0 in the inflated Memory component
CELL = 8


def chars_attrs():
    """2000 characters and attributes with no two neighbouring cells equal, so a shift shows."""
    chars = bytes((i * 7 + 33) % 223 + 32 for i in range(2000))
    attrs = bytes((i * 13 + 5) % 256 for i in range(2000))
    return chars, attrs


def synthetic_savestate(mode=0x03, ticks=b"\x6c\x3a\x0f\x00"):
    chars, attrs = chars_attrs()
    vga = bytearray((i * 31 + 17) % 256 for i in range(TEXT_BASE + CELL * 2000 + 64))  # filler differs from the page
    for i in range(2000):
        vga[TEXT_BASE + CELL * i] = chars[i]
        vga[TEXT_BASE + CELL * i + 1] = attrs[i]
    mem = bytearray((i * 11 + 3) % 256 for i in range(MEM_BASE + 0x1000))
    mem[MEM_BASE + 0x448] = 0x07      # neighbours of the mode byte, distinct from it
    mem[MEM_BASE + 0x449] = mode
    mem[MEM_BASE + 0x44A] = 0x50
    mem[MEM_BASE + 0x46B] = 0xEE      # neighbours of the tick dword
    mem[MEM_BASE + 0x46C:MEM_BASE + 0x470] = ticks
    mem[MEM_BASE + 0x470] = 0xDD
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Save_Remark", b"")
        z.writestr("Vga", zlib.compress(bytes(vga)))
        z.writestr("Memory", zlib.compress(bytes(mem)))
    return buf.getvalue()


class SavestateParser(unittest.TestCase):
    def setUp(self):
        self.s = savestate.Savestate(synthetic_savestate())

    def test_text_page_at_the_measured_offset(self):
        chars, attrs = chars_attrs()
        sc = self.s.screen()
        self.assertEqual(sc.chars, chars)
        self.assertEqual(sc.attrs, attrs)
        raw = bytes(b for c, a in zip(chars, attrs) for b in (c, a))
        self.assertEqual(sc.digest(), savestate.sha256(raw))
        self.assertEqual(len(sc.text().split("\n")), 25)

    def test_memory_at_the_measured_offset(self):
        self.assertEqual(self.s.memory(0x449, 1), b"\x03")
        self.assertEqual(self.s.video_mode(), 0x03)
        self.assertEqual(self.s.memory(0x448, 3), b"\x07\x03\x50")
        self.assertEqual(self.s.ticks(), (0x000F3A6C, b"\x6c\x3a\x0f\x00"))

    def test_reads_a_file_too(self):
        with tempfile.NamedTemporaryFile(suffix=".sav") as f:
            f.write(synthetic_savestate(mode=0x13))
            f.flush()
            self.assertEqual(savestate.Savestate(f.name).video_mode(), 0x13)

    def test_out_of_range_memory_is_refused(self):
        with self.assertRaises(ValueError):
            self.s.memory(0x1000, 1)
        with self.assertRaises(ValueError):
            self.s.memory(-1, 1)

    def test_short_vga_component_is_refused(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("Vga", zlib.compress(b"\0" * TEXT_BASE))
            z.writestr("Memory", zlib.compress(b"\0" * 0x1000))
        with self.assertRaises(ValueError):
            savestate.Savestate(buf.getvalue()).screen()


class RecordObservations(unittest.TestCase):
    def test_one_read_gives_clock_screen_mode_and_ticks(self):
        s = savestate.Savestate(synthetic_savestate())
        times = {"utc": "2026-10-04T07:00:00.000Z", "local": "2026-10-04T09:00:00.000+02:00", "tz": "CEST"}
        obs = cycle.read_observations(1, "after", times, s)
        by_addr = {o["addr"]: o["value"] for o in obs if "addr" in o}
        self.assertEqual(by_addr, {"0x449": "03", "0x46c": "0x000f3a6c (6c 3a 0f 00)"})
        values = [o["value"] for o in obs]
        self.assertIn("2026-10-04T07:00:00.000Z", values)
        self.assertIn("2026-10-04T09:00:00.000+02:00 CEST", values)
        self.assertIn(s.screen().digest(), values)
        self.assertTrue(all(o["step"] == 1 and o["field"].startswith("after: ") for o in obs))

    def test_host_times_carry_utc_and_local_with_offset(self):
        t = driver.host_times()
        self.assertRegex(t["utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
        self.assertRegex(t["local"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}[+-]\d\d:\d\d$")


class FakeDriver:
    """Stands in for driver.Driver: launches, makes one read before the restore, then the restore fails."""

    def __init__(self, config=None, workdir=None):
        self.config, self.workdir, self.game_dir = dict(driver.DEFAULT_CONFIG), Path(workdir), Path("/g")
        self.events, self.launched, self.last, self.pre_restore = [], None, None, None
        self.conf = "[cpu]\ncycles=max\n"

    def launch(self, st, displace_key="n"):
        self.launched = {"utc": "2026-10-04T07:00:00.000Z", "local": "2026-10-04T09:00:00.000+02:00", "tz": "CEST"}
        self.last = self.pre_restore = (dict(self.launched), savestate.Savestate(synthetic_savestate()))
        raise RuntimeError("savestate not complete within 15s")

    def conf_public(self):
        return self.conf, driver.sha256(self.conf.encode())

    def terminate(self):
        return True


class AbortedCycle(unittest.TestCase):
    def test_an_aborted_record_keeps_launch_time_and_the_reads_made(self):
        class St:
            name, sha256, screen_digest, config = "title", "0" * 64, "x", {}
        out = io.StringIO()
        with mock.patch.object(cycle.driver, "Driver", FakeDriver), \
                mock.patch.object(cycle.driver, "verify_release", lambda c: "goal2-a949da2f"), \
                mock.patch("sys.stdout", out), mock.patch("sys.stderr", io.StringIO()):
            ok = cycle.one_cycle(1, St(), "n", None, "abcdef0", dry=True)
        self.assertFalse(ok)
        rec = json.loads(out.getvalue())
        self.assertTrue(rec["status"].startswith("aborted: RuntimeError"))
        values = {o.get("addr", o.get("field")): o["value"] for o in rec["observations"]}
        self.assertEqual(values["host UTC time at launch"], "2026-10-04T07:00:00.000Z")
        self.assertEqual(values["0x449"], "03")
        self.assertEqual(values["0x46c"], "0x000f3a6c (6c 3a 0f 00)")


class StartStates(unittest.TestCase):
    def test_a_changed_savestate_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            data = synthetic_savestate()
            (Path(d) / "t.sav").write_bytes(data)
            meta = {"sha256": driver.sha256(data), "screen_digest": "x", "game_dir": "/g", "config": {}}
            (Path(d) / "t.json").write_text(json.dumps(meta))
            self.assertEqual(driver.StartState("t", d).sha256, meta["sha256"])
            (Path(d) / "t.sav").write_bytes(data + b"\0")
            with self.assertRaises(RuntimeError):
                driver.StartState("t", d)

    def test_a_state_from_another_mounted_folder_is_refused_before_launch(self):
        class St:
            name, game_dir = "t", "/elsewhere"
        with self.assertRaisesRegex(RuntimeError, "another folder"):
            driver.Driver(game_dir="/here").launch(St())


if __name__ == "__main__":
    unittest.main()
