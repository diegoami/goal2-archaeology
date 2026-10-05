"""T18: the decompiled view of GOAL.EXE (tools/static/decompile.sh, static/goal-exe/decompiled/).

- GhidraMappingTests runs Ghidra's MZ loader and tools/static/ghidra/GoalSetup.java on the released
  GOAL.EXE and checks that known routines sit at their listing addresses with the listing's bytes,
  that a near call whose 16-bit displacement wraps (1771:9810) and far calls reach the right
  functions, and that DS-relative operands land in the data segment 2581. Skipped where Ghidra or
  the released file is missing (CI).
- RewriteTests and RenderTests check tools/static/decompiled.py on small made-up inputs.
- CommittedOutputTests check the committed static/goal-exe/decompiled/ against routines.tsv.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "static"))

import decompiled  # noqa: E402

OUT = ROOT / "static" / "goal-exe" / "decompiled"
ROUTINES = ROOT / "static" / "goal-exe" / "routines.tsv"
UNPACKED_HEADER = 8192  # static/goal-exe/README.md


def ghidra_home() -> Path | None:
    p = Path(os.environ.get("GHIDRA_HOME", str(Path.home() / "tools" / "ghidra_12.1.4_PUBLIC")))
    return p if (p / "support" / "analyzeHeadless").exists() else None


def java_home() -> Path | None:
    if os.environ.get("JAVA_HOME"):
        p = Path(os.environ["JAVA_HOME"])
        return p if (p / "bin" / "java").exists() else None
    found = sorted(glob.glob(str(Path.home() / "tools" / "jdk-21*")))
    return Path(found[-1]) if found else None


def released_exe() -> Path | None:
    for p in sorted(glob.glob(str(ROOT / ".cache" / "artifacts" / "*" / "GOAL.EXE"))) + [
            str(ROOT / ".cache" / "goal2" / "GOAL.EXE")]:
        if os.path.exists(p):
            return Path(p)
    return None


GHIDRA, JAVA, EXE = ghidra_home(), java_home(), released_exe()
SKIP_GHIDRA = (None if GHIDRA and JAVA and EXE else
               "needs Ghidra 12.1.4 (GHIDRA_HOME or ~/tools/ghidra_12.1.4_PUBLIC), a JDK 21 (JAVA_HOME "
               "or ~/tools/jdk-21*) and the released GOAL.EXE in .cache/ (python3 tools/fetch_artifact.py "
               "goal2-67cf27d6); CI has none of them")

PROBED = ["0791:97D0", "0791:A4A1", "1771:97CC", "1771:10E7", "214B:0688", "2138:0000", "23E4:0000"]


@unittest.skipIf(SKIP_GHIDRA, SKIP_GHIDRA or "")
class GhidraMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = Path(tempfile.mkdtemp())
        exe = cls.work / "goal.exe"
        subprocess.run([sys.executable, str(ROOT / "tools" / "static" / "unlzexe.py"), str(EXE), str(exe)],
                       check=True, capture_output=True)
        cls.image = exe.read_bytes()
        (cls.work / "project").mkdir()
        env = dict(os.environ, JAVA_HOME=str(JAVA))
        segmap, probe = cls.work / "segmap.tsv", cls.work / "probe.tsv"
        run = subprocess.run(
            [str(GHIDRA / "support" / "analyzeHeadless"), str(cls.work / "project"), "probe",
             "-import", str(exe), "-loader", "MzLoader", "-processor", "x86:LE:16:Real Mode",
             "-scriptPath", str(ROOT / "tools" / "static" / "ghidra"),
             "-preScript", "GoalSetup.java", str(ROUTINES), str(segmap),
             "-postScript", "GoalProbe.java", str(segmap), str(probe), *PROBED,
             "-deleteProject", "-max-cpu", "2"],
            env=env, capture_output=True, text=True, timeout=1200)
        if not probe.exists():
            raise RuntimeError("Ghidra probe failed:\n" + run.stdout[-3000:] + run.stderr[-3000:])
        cls.rows = {}
        for line in probe.read_text().splitlines():
            addr, ghidra, name, hexbytes, calls, data = line.split("\t")
            cls.rows[addr] = dict(ghidra=ghidra, name=name, bytes=hexbytes,
                                  calls=set(filter(None, calls.split(","))),
                                  data=set(filter(None, data.split(","))))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, ignore_errors=True)

    def listing_bytes(self, addr: str, n: int = 8) -> str:
        seg, off = (int(x, 16) for x in addr.split(":"))
        at = UNPACKED_HEADER + seg * 16 + off
        return self.image[at:at + n].hex().upper()

    def test_known_routines_sit_at_their_listing_addresses(self):
        for addr in PROBED:
            with self.subTest(addr=addr):
                row = self.rows[addr]
                self.assertEqual(row["name"], "f_" + addr.replace(":", "_"), row)
                if addr != "23E4:0000":  # its first word is relocated (next test)
                    self.assertEqual(row["bytes"], self.listing_bytes(addr))

    def test_relocated_segment_words_hold_the_mapped_segment(self):
        # 23E4:0000 BA 81 25: mov dx, 2581 (relocated); Ghidra holds the data segment at B000
        self.assertEqual(self.listing_bytes("23E4:0000"), "BA81258EDA8C065C")
        self.assertEqual(self.rows["23E4:0000"]["bytes"], "BA00B08EDA8C065C")

    def test_near_call_with_a_wrapping_displacement_reaches_its_routine(self):
        # 1771:9810 E8 D4 78: 0x9813 + 0x78D4 wraps to 1771:10E7 (seg_1771_14.asm:31)
        self.assertIn("f_1771_10E7", self.rows["1771:97CC"]["calls"])
        self.assertIn("f_1771_96D3", self.rows["1771:97CC"]["calls"])

    def test_near_calls_across_a_linear_64k_line_reach_their_routines(self):
        # 0791:97D0 (linear 0x110D0) calls 0791:0C65 (linear 0x08575) and 0791:15B9 (0x08EC9)
        calls = self.rows["0791:97D0"]["calls"]
        self.assertTrue({"f_0791_9564", "f_0791_D733", "f_0791_0C65", "f_0791_15B9"} <= calls, calls)

    def test_far_calls_follow_the_remapped_relocations(self):
        self.assertIn("f_214B_0018", self.rows["0791:A4A1"]["calls"])  # A4EA call far 214B:0018
        self.assertIn("f_214B_06FA", self.rows["0791:A4A1"]["calls"])

    def test_ds_operands_land_in_the_data_segment(self):
        self.assertIn("DS:9A3E", self.rows["0791:97D0"]["data"])  # cmp byte ptr [0x9a3e], 0
        self.assertIn("DS:A917", self.rows["1771:10E7"]["data"])  # les di, [0xa917]


def segmap() -> decompiled.SegMap:
    # listing segment, Ghidra segment, bytes held: as GoalSetup.java writes for GOAL.EXE
    return decompiled.SegMap([(0x0000, 0x0000, 0xE0), (0x0791, 0x2000, 0xF450), (0x214B, 0x7000, 0x2110),
                              (0x2581, 0xB000, 0xF760)])


class RewriteTests(unittest.TestCase):
    def test_data_segment_names_become_ds_offsets(self):
        self.assertEqual(decompiled.rewrite("if (DAT_b000_9a3e == 0) x = &_DAT_b000_82ee;", segmap()),
                         "if (DS:9A3E == 0) x = &DS:82EE;")

    def test_code_labels_get_listing_numbering(self):
        self.assertEqual(decompiled.rewrite("goto LAB_2000_4796; y = DAT_7000_0010;", segmap()),
                         "goto LAB_0791_4796; y = DAT_214B_0010;")

    def test_memory_outside_the_program_is_physical(self):
        # 0040:0049 (BIOS video mode) is linear 0x449, past segment 0000's 0xE0 bytes
        self.assertEqual(decompiled.rewrite("m = DAT_0000_0449;", segmap()), "m = ABS_00449;")
        # and so is a Ghidra segment that holds no listing segment
        self.assertEqual(decompiled.rewrite("m = DAT_c000_0001;", segmap()), "m = ABS_C0001;")

    def test_linear_addresses_get_listing_numbering(self):
        self.assertEqual(decompiled.rewrite("/* block (ram,0x00071dce) */ func_0x000287f7(); "
                                            "goto code_r0x00020711;", segmap()),
                         "/* block (214B:1DCE) */ func_0791_87F7(); goto code_r_0791_0711;")

    def test_other_text_is_left_alone(self):
        text = "x = CONCAT22(register0x00000010,in_CX) + 0xb000; f_0791_97D0(); PTR_c000_0001;"
        self.assertEqual(decompiled.rewrite(text, segmap()), text)


class RenderTests(unittest.TestCase):
    RAW = ("@@FUNC 2000:97d0 f_0791_97D0 __stdcall16near ok\n\nvoid f_0791_97D0(void)\n{\n"
           "  DAT_b000_9a3e = 0;\n}\n\n"
           "@@FUNC 7000:05f0 f_214B_05F0 __stdcall16far failed Exception: out of bounds\n"
           "@@FUNC 7000:1000 f_214B_1000 __cdecl16far ok\nvoid f_214B_1000(void)\n{\n}\n")

    def test_files_index_and_failures(self):
        functions = decompiled.parse_raw(self.RAW)
        files, rows = decompiled.render(functions, ["0791:97D0", "214B:05F0", "214B:0688"], segmap())
        self.assertEqual(sorted(files), ["seg_0791_01.c", "seg_214B_01.c"])
        by = {r[0]: r for r in rows}
        self.assertEqual(by["0791:97D0"][1:4], ["decompiled", "seg_0791_01.c", by["0791:97D0"][3]])
        line = int(by["0791:97D0"][3])
        self.assertTrue(files["seg_0791_01.c"].splitlines()[line - 1].startswith("// ---- 0791:97D0  "))
        self.assertIn("  DS:9A3E = 0;", files["seg_0791_01.c"])
        self.assertEqual(by["214B:05F0"][1], "failed")
        self.assertEqual(by["214B:05F0"][6], "Exception: out of bounds")
        self.assertEqual(by["214B:0688"][1], "missing")
        self.assertEqual(by["214B:1000"][5], "ghidra")

    def test_a_segment_splits_into_parts_under_the_size_limit(self):
        body = "  x = 1;\n" * 3000  # about 27 KB per function
        raw = "".join(f"@@FUNC 2000:{o:04x} f_0791_{o:04X} __cdecl16near ok\nvoid f(void)\n{{\n{body}}}\n"
                      for o in (0x10, 0x20, 0x30))
        files, rows = decompiled.render(decompiled.parse_raw(raw), [], segmap())
        self.assertEqual(sorted(files), ["seg_0791_01.c", "seg_0791_02.c", "seg_0791_03.c"])
        self.assertTrue(all(len(t.encode()) <= decompiled.MAX_FILE_BYTES for t in files.values()))


class CommittedOutputTests(unittest.TestCase):
    def setUp(self):
        if not (OUT / "index.tsv").exists():
            self.fail("static/goal-exe/decompiled/index.tsv is missing")
        self.rows = [l.split("\t") for l in (OUT / "index.tsv").read_text().splitlines()[1:]]

    def test_index_covers_every_routine(self):
        routines = decompiled.read_routines(ROUTINES)
        indexed = {r[0] for r in self.rows if r[5] == "routines.tsv"}
        self.assertEqual(indexed, set(routines))
        self.assertEqual(len(routines), 726)
        for r in self.rows:
            self.assertIn(r[1], ("decompiled", "failed", "missing"))
            if r[1] != "decompiled":
                self.assertTrue(r[6], f"{r[0]} has no reason")

    def test_each_heading_is_at_its_indexed_line(self):
        lines = {}
        for r in self.rows:
            if r[1] == "decompiled":
                text = lines.setdefault(r[2], (OUT / r[2]).read_text().splitlines())
                self.assertTrue(text[int(r[3]) - 1].startswith(f"// ---- {r[0]}  f_{r[0].replace(':', '_')}  "),
                                r)

    def test_files_stay_under_the_size_limit(self):
        for p in OUT.glob("seg_*.c"):
            self.assertLessEqual(p.stat().st_size, decompiled.MAX_FILE_BYTES, p.name)


if __name__ == "__main__":
    unittest.main()
