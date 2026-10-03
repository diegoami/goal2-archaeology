"""Checks that static/goal-exe-map.md agrees with the generated listing it indexes.
It reads only tracked files (static/goal-exe/*.tsv), so it needs neither the originals nor capstone."""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAP = os.path.join(ROOT, "static", "goal-exe-map.md")
LST = os.path.join(ROOT, "static", "goal-exe")


def tsv(name):
    rows = []
    with open(os.path.join(LST, name), encoding="utf-8") as f:
        for ln in f:
            if ln.startswith(";") or not ln.strip():
                continue
            rows.append(ln.rstrip("\n").split("\t"))
    return rows[1:]  # without the column header


def addr(a):
    s, o = a.split(":")
    return int(s, 16), int(o, 16)


def table_rows():
    rows, in_table = [], False
    with open(MAP, encoding="utf-8") as f:
        for n, ln in enumerate(f, 1):
            if ln.startswith("|"):
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                if all(set(c) <= set("- ") for c in cells):
                    in_table = True
                    continue
                if in_table:
                    rows.append((n, cells))
                else:
                    pass  # the header row
            else:
                in_table = False
    return rows


class MapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routines = {r[0]: r for r in tsv("routines.tsv")}
        cls.strings = tsv("strings.tsv")
        cls.texts = [r[3] for r in cls.strings]
        cls.string_addrs = {r[0] for r in cls.strings}
        cls.rows = table_rows()

    def test_there_are_rows(self):
        self.assertGreater(len(self.rows), 80)

    def test_every_row_is_marked(self):
        for n, cells in self.rows:
            self.assertRegex(cells[-1], r"^(observed|inferred|not placed)", "line %d: %s" % (n, cells[0]))

    def test_every_routine_cited_exists(self):
        """Any SSSS:OOOO in backticks is a routine start, or the address of a listed string."""
        for n, cells in self.rows:
            for a in re.findall(r"`([0-9A-F]{4}:[0-9A-F]{4})`", " ".join(cells)):
                if a.startswith("2581:"):
                    continue
                self.assertTrue(a in self.routines or a in self.string_addrs, "line %d cites %s" % (n, a))

    def test_first_cell_data_addresses_are_listed_strings(self):
        for n, cells in self.rows:
            for off in re.findall(r"`DS:([0-9A-F]{4})`", cells[0]):
                self.assertIn("2581:" + off, self.string_addrs, "line %d: DS:%s" % (n, off))

    def test_every_quoted_string_is_in_the_listing(self):
        for n, cells in self.rows:
            for q in re.findall(r'"([^"]+)"', " ".join(cells[1:])):
                self.assertTrue(any(q in t for t in self.texts), "line %d: %r is in no listed string" % (n, q))

    def test_beside_it_strings_are_next_to_the_routine(self):
        """'beside it' rows: the quoted strings are in the code segment just before the routine
        (or in the routine's own string references)."""
        for n, cells in self.rows:
            if "beside it" not in " ".join(cells):
                continue
            a = re.match(r"`([0-9A-F]{4}:[0-9A-F]{4})`", cells[0])
            self.assertTrue(a, "line %d" % n)
            seg, off = addr(a.group(1))
            r = self.routines[a.group(1)]
            size = int(r[1])
            near = [t for (sa, _, _, t) in self.strings
                    if int(sa[:4], 16) == seg and sa[:4] != "2581" and off - 0x100 <= int(sa[5:], 16) < off + size]
            near.append(r[8])
            before = cells[2].split("beside it")[0]  # the quotes the row says are beside the routine
            for q in re.findall(r'"([^"]+)"', before):
                self.assertTrue(any(q in t for t in near), "line %d: %r is not beside %s" % (n, q, a.group(1)))

    def test_unit_table_matches_routines_tsv(self):
        counts = {}
        for r in self.routines.values():
            seg = r[0][:4]
            c = counts.setdefault(seg, [0, 0])
            c[0] += 1
            c[1] += int(r[1])
        seen = 0
        for n, cells in self.rows:
            m = re.match(r"^`([0-9A-F]{4})`$", cells[0])
            if m and m.group(1) in counts and len(cells) == 6 and cells[2].isdigit():
                seen += 1
                self.assertEqual([int(cells[2]), int(cells[3])], counts[m.group(1)], "segment %s" % m.group(1))
        self.assertEqual(seen, len(counts))

    def test_loader_sizes_add_up_to_the_file(self):
        for n, cells in self.rows:
            if cells[0] == "`1771:018A`":
                sizes = re.search(r"sizes `([^`]+)`", cells[2]).group(1).split()
                self.assertEqual(sum(int(s, 16) for s in sizes), 44040)
                return
        self.fail("no row for 1771:018A")


if __name__ == "__main__":
    unittest.main()
