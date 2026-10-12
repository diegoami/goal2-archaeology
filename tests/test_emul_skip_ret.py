"""Fix #142: the 000E wait-family hook returns NEAR (`ret n`: pops IP only, CS unchanged).

seg_000E_01.asm:530, 576, 640, 668 are `ret 4`, `ret 4`, `ret 2`, `ret 6`. The test builds a
tiny Unicorn machine (no savestate), calls each routine's entry, and checks the hook's return.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/emul"))

try:
    import watched  # noqa: E402
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16  # noqa: E402
    from unicorn.x86_const import *  # noqa: E402
except ModuleNotFoundError:
    raise unittest.SkipTest("unicorn not installed")


class SkipRetNearTests(unittest.TestCase):
    def test_near_return(self):
        for off, nb in watched.WAIT_FAMILY:
            with self.subTest(entry=hex(off)):
                half = watched.WatchedHalf.__new__(watched.WatchedHalf)
                half.SEG000E, half.SEG214B, half.CODE, half.DS = 0x1000, 0x2000, 0x3000, 0x4000
                half.seed_lin = half.DS * 16 + 0x7B62
                half.draws, half.speaker, half.strays = [], [], []
                half.ticks, half.tick_marks = 0, []
                half.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
                mu.mem_map(0, 0x110000)
                half._hook()
                ss, sp, ret_ip, other = 0x7000, 0x6000, 0x0123, 0x5555
                mu.mem_write(ss * 16 + sp, ret_ip.to_bytes(2, "little") + other.to_bytes(2, "little"))
                mu.mem_write(half.SEG000E * 16 + ret_ip, b"\x90\x90\x90\x90")
                mu.reg_write(UC_X86_REG_SS, ss)
                mu.reg_write(UC_X86_REG_SP, sp)
                mu.reg_write(UC_X86_REG_CS, half.SEG000E)
                mu.reg_write(UC_X86_REG_EIP, off)
                mu.emu_start(half.SEG000E * 16 + off, half.SEG000E * 16 + ret_ip, count=4)
                self.assertEqual(mu.reg_read(UC_X86_REG_CS), half.SEG000E)
                self.assertEqual(mu.reg_read(UC_X86_REG_EIP), ret_ip)
                self.assertEqual(mu.reg_read(UC_X86_REG_SP), sp + 2 + nb)
                self.assertEqual(half.strays, ["000E:%04X" % off])


if __name__ == "__main__":
    unittest.main()
