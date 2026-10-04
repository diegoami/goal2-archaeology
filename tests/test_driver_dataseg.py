"""GOAL.EXE's data segment located in a savestate (T08), and the DOS clock option of the driver.

A synthetic savestate holds a DOS memory control block (MCB) and a PSP where DOSBox-X put them in
E003 (MCB 0812, PSP 0813), written with literal offsets taken from the DOS MCB layout and
static/goal-exe/README.md (data segment 2581), not from the parser. Every planted word has
neighbours that differ from it, so a parser whose offset moves by one byte (or one paragraph)
reads other bytes and these tests fail."""
import argparse
import io
import json
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "experiments" / "E003-q001-inputs"))

import driver  # noqa: E402
import run  # noqa: E402
import savestate  # noqa: E402
import summarise  # noqa: E402
from unittest import mock  # noqa: E402

MEM_BASE = 0x78           # F001: guest address 0 in the inflated Memory component
MCB_SEG, PSP_SEG = 0x0812, 0x0813
LOAD_SEG = PSP_SEG + 0x10      # an EXE's load module starts 256 bytes after its PSP
DS_SEG = LOAD_SEG + 0x2581     # static/goal-exe/README.md: "Data segment 2581"
DS_BASE = DS_SEG * 16          # 0x2DA40, the base E003 found


def memory_image(mcbs=((MCB_SEG, PSP_SEG, b"GOAL\0\0\0\0"),), words=None):
    mem = bytearray((i * 11 + 3) % 251 for i in range(0xA0000 + 0x100))
    for seg in range(0x50, 0xA000):          # no stray MCB signature in the filler
        if mem[seg * 16] in (0x4D, 0x5A):
            mem[seg * 16] = 0x00
    for mcb, owner, name in mcbs:
        a = mcb * 16
        mem[a] = 0x4D
        mem[a + 1:a + 3] = owner.to_bytes(2, "little")
        mem[a + 3:a + 5] = (0x1000).to_bytes(2, "little")
        mem[a + 8:a + 16] = name
        mem[owner * 16:owner * 16 + 2] = b"\xcd\x20"
    for off, value in (words or {}).items():
        mem[DS_BASE + off:DS_BASE + off + 2] = value.to_bytes(2, "little")
    return bytes(mem)


def savestate_of(mem):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Save_Remark", b"")
        z.writestr("Vga", zlib.compress(b"\0" * 16))
        z.writestr("Memory", zlib.compress(b"\0" * MEM_BASE + mem))
    return savestate.Savestate(buf.getvalue())


# Distinct words at the three seed offsets and at every byte and paragraph neighbour of DS:7B62.
WORDS = {0x7B62: 0x0A00, 0x7B64: 0x0935, 0x8336: 0x0057, 0x7B60: 0x1111, 0x7B66: 0x2222,
         0x7B52: 0x3333, 0x7B72: 0x4444, 0x0024: 0x5407}


class DataSegment(unittest.TestCase):
    def setUp(self):
        self.s = savestate_of(memory_image(words=WORDS))

    def test_program_found_where_planted(self):
        p = self.s.program()
        self.assertEqual((p.mcb, p.psp, p.load, p.ds, p.ds_base), (MCB_SEG, PSP_SEG, LOAD_SEG, DS_SEG, 0x2DA40))

    def test_seed_words(self):
        self.assertEqual(self.s.ds_word(0x7B62), 0x0A00)
        self.assertEqual(self.s.ds_word(0x7B64), 0x0935)
        self.assertEqual(self.s.ds_word(0x8336), 0x0057)

    def test_describe_names_the_segments(self):
        self.assertIn("PSP 0813, load segment 0823", self.s.program().describe())
        self.assertIn("DS 2DA4", self.s.program().describe())

    def test_mcb_owned_by_another_block_is_ignored(self):
        # an environment block's MCB: name GOAL, but owned by a PSP that is not the next segment
        mem = memory_image(mcbs=((0x0700, PSP_SEG, b"GOAL\0\0\0\0"), (MCB_SEG, PSP_SEG, b"GOAL\0\0\0\0")), words=WORDS)
        self.assertEqual(savestate_of(mem).program().psp, PSP_SEG)

    def test_other_program_is_ignored(self):
        mem = memory_image(mcbs=((0x0600, 0x0601, b"COMMAND\0"), (MCB_SEG, PSP_SEG, b"GOAL\0\0\0\0")), words=WORDS)
        self.assertEqual(savestate_of(mem).program().mcb, MCB_SEG)

    def test_goal_mcb_without_psp_signature_is_rejected(self):
        # an MCB that matches in every other way (M, owner = next segment, name GOAL) but whose next
        # paragraph does not start with INT 20h (CD 20) is not a program's block (review R2)
        mem = bytearray(memory_image(words=WORDS))
        for not_psp in (b"\xcd\x21", b"\x00\x00"):
            mem[PSP_SEG * 16:PSP_SEG * 16 + 2] = not_psp
            with self.assertRaises(ValueError, msg=not_psp.hex()):
                savestate_of(bytes(mem)).program()

    def test_no_or_two_programs_raise(self):
        with self.assertRaises(ValueError):
            savestate_of(memory_image(mcbs=())).program()
        with self.assertRaises(ValueError):
            savestate_of(memory_image(mcbs=((0x0600, 0x0601, b"GOAL\0\0\0\0"), (MCB_SEG, PSP_SEG, b"GOAL\0\0\0\0")))).program()


class ClockOption(unittest.TestCase):
    def test_date_and_time_lines_before_goal(self):
        d = driver.Driver({"dos_time": "10:00:00", "dos_date": "10/04/1993"})
        tail = d.conf_text().split("[autoexec]\n", 1)[1]
        lines = tail.splitlines()
        # the clock is set (and read back, the next four lines) on C: before GOAL runs
        self.assertEqual(lines[2:4], ["date 10/04/1993", "time 10:00:00"])
        self.assertEqual(lines[7:10], ["c:", "goal", "exit"])

    def test_forms_dosbox_ignores_are_refused(self):
        # DOSBox-X 2024.03.01's DATE ignores 10-04-1993 (E003-r0030, r0031): refused, not written
        for cfg in ({"dos_date": "10-04-1993"}, {"dos_date": "1993/10/04"}, {"dos_time": "10:00"}):
            with self.assertRaises(ValueError):
                driver.Driver(cfg).conf_text()

    def test_no_lines_by_default(self):
        tail = driver.Driver().conf_text().split("[autoexec]\n", 1)[1]
        self.assertEqual(tail.splitlines()[2:4], ["goal", "exit"])


class ClockApplied(unittest.TestCase):
    """Review R1: a requested clock is declared applied only when DOS reports it back."""

    def test_impossible_dates_and_times_refused(self):
        # review R1: a local run of the reviewer (numbered 51, not in the repository): 99/99/1993 validated and was declared set
        for cfg in ({"dos_time": "10:00:00", "dos_date": "99/99/1993"}, {"dos_date": "02/30/1993"},
                    {"dos_date": "01/01/1979"}, {"dos_date": "01/01/2100"}, {"dos_time": "24:00:00"},
                    {"dos_time": "10:60:00"}):
            with self.assertRaises(ValueError, msg=cfg):
                driver.Driver(cfg).conf_text()

    def test_runner_refuses_before_any_run(self):
        with self.assertRaises(ValueError):
            run.main(["d0", "--dos-time", "10:00:00", "--dos-date", "99/99/1993"])

    def test_readback_lines_follow_the_setting(self):
        lines = driver.Driver({"dos_time": "10:00:00", "dos_date": "10/04/1993"}).clock_lines().splitlines()
        self.assertEqual(lines[:2], ["date 10/04/1993", "time 10:00:00"])
        self.assertTrue(lines[2].startswith("mount d ") and lines[2].endswith(driver.CLOCK_DIR))
        self.assertEqual(lines[3:], ["date /t > d:\\clock.txt", "time /t >> d:\\clock.txt", "c:"])

    def test_check_clock(self):
        self.assertEqual(driver.check_clock("10/04/1993", "10:00:00", "10/04/1993\r\n10:00:01\r\n"),
                         ("10/04/1993", "10:00:01"))
        # DOSBox-X's tick-truncated read-back of 10:00:00 (E003-r0045, r0046)
        self.assertEqual(driver.check_clock("10/04/1993", "10:00:00", "10/04/1993\r\n 9:59:59\r\n"),
                         ("10/04/1993", "9:59:59"))
        # DOS kept the host's date: the reviewer's case, where the year stayed 2026
        with self.assertRaises(driver.ClockNotApplied):
            driver.check_clock("10/04/1993", "10:00:00", "10/04/2026\n10:00:00\n")
        with self.assertRaises(driver.ClockNotApplied):
            driver.check_clock("10/04/1993", "10:00:00", "10/04/1993\n10:00:30\n")   # beyond CLOCK_SLACK
        with self.assertRaises(driver.ClockNotApplied):
            driver.check_clock("10/04/1993", "10:00:00", "10/04/1993\n9:59:58\n")   # 2 s before the time set
        with self.assertRaises(driver.ClockNotApplied):
            driver.check_clock("10/04/1993", "10:00:00", None)

    def _launch(self, readback):
        """Driver.launch with DOSBox-X, Xvfb and xdotool replaced: the fake process writes CLOCK.TXT
        as DOS would (or nothing, readback None), and the title screen appears at once."""
        with tempfile.TemporaryDirectory() as tmp:
            d = driver.Driver({"dos_time": "10:00:00", "dos_date": "10/04/1993"},
                              workdir=Path(tmp) / "work", game_dir=Path(tmp) / "game")

            def popen(*a, **k):
                if readback is not None:
                    (d.workdir / driver.CLOCK_DIR / "CLOCK.TXT").write_text(readback)
                return mock.Mock()
            screen = mock.Mock()
            screen.text.return_value = driver.TITLE_TEXT
            with mock.patch.object(driver, "verify_release"), mock.patch.object(driver.shutil, "copytree"), \
                    mock.patch.object(driver.subprocess, "Popen", popen), \
                    mock.patch.object(driver.Driver, "_start_xvfb"), \
                    mock.patch.object(driver.Driver, "_wait_window", return_value="1"), \
                    mock.patch.object(driver.Driver, "_x"), \
                    mock.patch.object(driver.Driver, "wait_screen", return_value=screen):
                d.display = ":0"
                d.launch(None)
            return d

    def test_launch_checks_the_read_back(self):
        self.assertEqual(self._launch("10/04/1993\r\n 9:59:59\r\n").clock_applied.split(), ["10/04/1993", "9:59:59"])
        with self.assertRaises(driver.ClockNotApplied):
            self._launch("10/04/2026\r\n 9:59:59\r\n")   # DOS kept the host's year (review R1's case)
        with self.assertRaises(driver.ClockNotApplied):
            self._launch(None)                            # no read-back at all

    def _record(self, readback, error):
        args = argparse.Namespace(dos_time="10:00:00", dos_date="10/04/1993", batch="t")
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(run, "OUT", Path(tmp)), \
                mock.patch.object(driver, "verify_release", return_value="goal2-a949da2f"):
            r = run.Run("d0", 9999, args, "abc1234")

            def launch(*a, **k):
                r.d.launched = driver.host_times()
                r.d.clock_applied = readback
                if error:
                    raise driver.ClockNotApplied(error)
                raise RuntimeError("stop after launch (test)")
            r.d.launch = launch
            r.d.terminate = lambda: True
            with mock.patch("traceback.print_exc"):
                r.go()
            return json.loads((Path(tmp) / "E003-r9999.json").read_text())

    def test_record_declares_what_dos_reported(self):
        rec = self._record("10/04/1993\n10:00:01\n", None)
        i3 = [i["what"] for i in rec["interventions"] if i["level"] == "I3"][0]
        self.assertIn("applied: DOS reported date 10/04/1993 and time 10:00:01", i3)
        self.assertEqual(summarise.applied_clock(rec, summarise.reads(rec), None), "read back 10/04/1993 10:00:01")

    def test_record_never_declares_an_unapplied_clock_applied(self):
        rec = self._record("10/04/2026\n10:00:00\n", "DOS date set to 10/04/1993, DOS reports 10/04/2026")
        i3 = [i["what"] for i in rec["interventions"] if i["level"] == "I3"][0]
        self.assertIn("NOT verified as applied: DOS date set to 10/04/1993, DOS reports 10/04/2026", i3)
        self.assertNotIn("applied: DOS reported", i3)
        self.assertTrue(rec["status"].startswith("aborted: ClockNotApplied"))
        self.assertEqual(summarise.applied_clock(rec, summarise.reads(rec), None), "read back 10/04/2026 10:00:00")


class Summarise(unittest.TestCase):
    def test_lcg_of_214B_0688(self):
        # 214B:0694..069F: seed = seed * 0x7ABD + 0x1B0F, 16 bits
        x1 = (0x0A00 * 0x7ABD + 0x1B0F) & 0xFFFF
        self.assertEqual(summarise.lcg_steps(0x0A00, x1), 1)
        self.assertEqual(summarise.lcg_steps(0x0A00, 0x0A00), 0)

    def test_clock_of_ticks(self):
        # 0x000A004A = 655434 ticks at 1193182/65536 per second = 35999.98 s
        self.assertEqual(summarise.clock("0x000a004a (4a 00 0a 00)"), "10:00:00.0")
        self.assertEqual(summarise.clock("0x000a00e1 (e1 00 0a 00)"), "10:00:08.3")


if __name__ == "__main__":
    unittest.main()
