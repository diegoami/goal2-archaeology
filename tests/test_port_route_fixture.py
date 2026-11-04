"""T121: the fixture router and its news/watch helpers, pinned to the listing."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port

class Registry(unittest.TestCase):
    def test_the_ten_routines_and_their_returns(self):
        reg = port._module_registry("route")
        self.assertEqual({a: e.ret for a, e in reg.entries.items()}, {
            "000E:6CA7": "ret", "000E:6C21": "ret 4", "0791:E80D": "retf 4",
            "000E:6685": "ret 4", "000E:038E": "ret", "000E:05F6": "ret 6",
            "000E:062F": "ret 0xc", "000E:070B": "ret 6", "000E:075F": "ret 0xc",
            "000E:5978": "ret 4"})
