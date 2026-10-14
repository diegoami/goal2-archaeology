"""A collision is refused and renamed, never overwritten or mixed (rule 20). Run: python3 -m unittest experiments/E027-discipline-rules/test_exclusive_logs.py
(from the repository root, or python3 test_exclusive_logs.py here). It fails if logs.open_new used mode 'w' or 'a'."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logs import open_new, stamped  # noqa: E402


class ExclusiveLogs(unittest.TestCase):
    def test_same_name_twice_keeps_both(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.log"
            p1, f1 = open_new(p)
            f1.write("first\n")
            f1.close()
            p2, f2 = open_new(p)
            f2.write("second\n")
            f2.close()
            p3, f3 = open_new(p, "a")      # an append request is also exclusive
            f3.close()
            self.assertEqual((p1.name, p2.name, p3.name), ("x.log", "x-1.log", "x-2.log"))
            self.assertEqual(p1.read_text(), "first\n")
            self.assertEqual(p2.read_text(), "second\n")

    def test_two_launches_in_one_second_do_not_share_a_name(self):
        with tempfile.TemporaryDirectory() as d:
            a = stamped(d, "probe")
            b = stamped(d, "probe")
            self.assertEqual(a, b)         # same second, same pid: the name collides ...
            _, fa = open_new(a)
            pb, fb = open_new(b)           # ... and the second launch gets its own file
            fa.close()
            fb.close()
            self.assertNotEqual(pb, a)


if __name__ == "__main__":
    unittest.main()
