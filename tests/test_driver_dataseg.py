"""GOAL.EXE's data segment located in a savestate (T08), and the DOS clock option of the driver.

A synthetic savestate holds a DOS memory control block (MCB) and a PSP where DOSBox-X put them in
E003 (MCB 0812, PSP 0813), written with literal offsets taken from the DOS MCB layout and
static/goal-exe/README.md (data segment 2581), not from the parser. Every planted word has
neighbours that differ from it, so a parser whose offset moves by one byte (or one paragraph)
reads other bytes and these tests fail."""
import io
import sys
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "experiments" / "E003-q001-inputs"))

import driver  # noqa: E402
import savestate  # noqa: E402
import summarise  # noqa: E402

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

    def test_no_or_two_programs_raise(self):
        with self.assertRaises(ValueError):
            savestate_of(memory_image(mcbs=())).program()
        with self.assertRaises(ValueError):
            savestate_of(memory_image(mcbs=((0x0600, 0x0601, b"GOAL\0\0\0\0"), (MCB_SEG, PSP_SEG, b"GOAL\0\0\0\0")))).program()


class ClockOption(unittest.TestCase):
    def test_date_and_time_lines_before_goal(self):
        d = driver.Driver({"dos_time": "10:00:00", "dos_date": "10-04-2026"})
        tail = d.conf_text().split("[autoexec]\n", 1)[1]
        self.assertEqual(tail.splitlines()[2:5], ["date 10-04-2026", "time 10:00:00", "goal"])

    def test_no_lines_by_default(self):
        tail = driver.Driver().conf_text().split("[autoexec]\n", 1)[1]
        self.assertEqual(tail.splitlines()[2:4], ["goal", "exit"])


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
