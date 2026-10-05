"""GOAL.EXE's commentary ring, score and delay byte read from guest memory (T10, runtime/driver/commentary.py).

A synthetic memory image plants the data segment at a known base and writes the ring, the counter,
the templates, the names and the far pointers at literal offsets taken from the listing
(seg_0791_03.asm, seg_0791_17.asm, seg_0791_15.asm), not from the module, so a module whose offset
moves reads other bytes and these tests fail."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import commentary  # noqa: E402

DS_BASE = 0x2DA40          # E003: DS 2DA4
NAMES_SEG, NAMES_OFF = 0x3000, 0x0010
GAME_SEG, GAME_OFF = 0x3100, 0x0020


class FakeState:
    """ds_word, ds_bytes and memory over one bytearray, as savestate.Savestate offers them."""

    def __init__(self):
        self.mem = bytearray(0x40000)

    def memory(self, addr, n):
        return bytes(self.mem[addr:addr + n])

    def ds_bytes(self, off, n):
        return self.memory(DS_BASE + off, n)

    def ds_word(self, off):
        return int.from_bytes(self.ds_bytes(off, 2), "little")

    def put(self, addr, b):
        self.mem[addr:addr + len(b)] = b

    def put_ds(self, off, b):
        self.put(DS_BASE + off, b)


def pascal(s, size):
    b = bytes([len(s)]) + s.encode("cp437")
    return b + bytes(size - len(b))


def make_state(counter, records, score=(2, 1), delay=0):
    st = FakeState()
    # the ring at DS:7C38 + 6*n, 0xFF everywhere first (A4A1, seg_0791_17.asm:272-280)
    st.put_ds(0x7C3E, b"\xff" * (6 * 200))
    for n, (tpl, p1, p2, team) in records.items():
        st.put_ds(0x7C38 + 6 * n, bytes([tpl]) + p1.to_bytes(2, "little") + p2.to_bytes(2, "little") + bytes([team]))
    st.put_ds(0x80EE, counter.to_bytes(2, "little"))
    # templates at DS:00BE + 0x15*t (seg_0791_03.asm:292-306); a few real ones from ds_2581_01.hex
    for t, text in {0: "\x01on for\x02", 2: "\x01makes a pass", 38: "**** GOAL **** by\x01", 50: "\x01BOOKED",
                    51: "\x01SENT OFF", 52: "\x01INJURED", 63: "---- FULL TIME ----"}.items():
        st.put_ds(0x00BE + 0x15 * t, pascal(text, 0x15))
    # names: far pointer at DS:9B6C, 11 bytes each (seg_0791_03.asm:318-321)
    st.put_ds(0x9B6C, NAMES_OFF.to_bytes(2, "little") + NAMES_SEG.to_bytes(2, "little"))
    for i, nm in {5: "Nilsson", 6: "Brolin", 7: "Ekstrom"}.items():
        st.put(NAMES_SEG * 16 + NAMES_OFF + 11 * i, pascal(nm, 11))
    st.put_ds(0x9B3C, bytes(score))
    st.put_ds(0xA923, GAME_OFF.to_bytes(2, "little") + GAME_SEG.to_bytes(2, "little"))
    st.put(GAME_SEG * 16 + GAME_OFF + 0x3F, bytes([delay]))
    return st


class SnapshotTest(unittest.TestCase):
    def test_reads_counter_score_delay_and_lines(self):
        st = make_state(3, {1: (2, 5, 0, 0), 2: (0, 6, 7, 1), 3: (38, 7, 0, 1)}, score=(2, 1), delay=4)
        s = commentary.Snapshot(st)
        self.assertEqual(s.counter, 3)
        self.assertEqual(s.score, (2, 1))
        self.assertEqual(s.speed, 4)
        self.assertEqual(s.record(2), {"template": 0, "p1": 6, "p2": 7, "team": 1})
        self.assertEqual(s.text(s.record(1)), "Nilsson makes a pass")
        self.assertEqual(s.text(s.record(2)), "Brolin on for Ekstrom")
        self.assertEqual(s.text(s.record(3)), "**** GOAL **** by Ekstrom")


class TrackerTest(unittest.TestCase):
    def test_accumulates_across_reads_and_wraps(self):
        t = commentary.Tracker()
        t.add(commentary.Snapshot(make_state(2, {1: (2, 5, 0, 0), 2: (50, 6, 0, 1)})), "r1")
        self.assertEqual([x["text"] for x in t.lines], ["Nilsson makes a pass", "Brolin BOOKED"])
        # 199 more lines later the counter has wrapped to 1: records 3 .. 200 and 1 are new
        recs = {n: (2, 5, 0, 0) for n in range(3, 201)}
        recs[1] = (52, 7, 0, 0)
        t.add(commentary.Snapshot(make_state(1, recs)), "r2")
        self.assertEqual(len(t.lines), 2 + 199)
        self.assertEqual(t.lines[-1]["text"], "Ekstrom INJURED")
        self.assertEqual(t.deltas, [2, 199])

    def test_a_large_step_is_noted_as_a_gap(self):
        t = commentary.Tracker()
        recs = {n: (2, 5, 0, 0) for n in range(1, 101)}
        t.add(commentary.Snapshot(make_state(commentary.GAP_LIMIT, recs)), "r1")
        self.assertEqual(len(t.gaps), 1)
        t2 = commentary.Tracker()
        t2.add(commentary.Snapshot(make_state(commentary.GAP_LIMIT - 1, recs)), "r1")
        self.assertEqual(t2.gaps, [])

    def test_an_end_marker_stops_the_read_until_the_record_is_written(self):
        # read 1 lands after the game raised the counter to 3 and before it wrote record 2 (still 0xFF):
        # the read stops at record 2 and does not advance past it, and the next read takes the record
        t = commentary.Tracker()
        t.add(commentary.Snapshot(make_state(3, {1: (2, 5, 0, 0), 3: (2, 5, 0, 0)})), "r1")  # record 2 is 0xFF
        self.assertEqual([x["n"] for x in t.lines], [1])
        self.assertEqual(t.gaps, ["r1: record 2 is the end marker 0xFF (pending)"])
        t.add(commentary.Snapshot(make_state(3, {1: (2, 5, 0, 0), 2: (50, 6, 0, 1), 3: (2, 5, 0, 0)})), "r2")
        self.assertEqual([x["n"] for x in t.lines], [1, 2, 3])
        self.assertEqual(t.deltas, [3, 2])

    def test_a_read_between_the_counters_increment_and_the_write_keeps_the_line(self):
        # E005-r0035's case: the read lands after `214B:1C86` raised DS:80EE to 3 and before `0791:1D4A`
        # wrote record 3, so record 3 is still 0xFF; the next read has the record and the line is kept,
        # in order, with no duplicate
        t = commentary.Tracker()
        t.add(commentary.Snapshot(make_state(3, {1: (2, 5, 0, 0), 2: (50, 6, 0, 1)})), "r1")
        self.assertEqual([x["n"] for x in t.lines], [1, 2])
        self.assertEqual(t.gaps, ["r1: record 3 is the end marker 0xFF (pending)"])
        t.add(commentary.Snapshot(make_state(5, {1: (2, 5, 0, 0), 2: (50, 6, 0, 1), 3: (38, 7, 0, 1),
                                                 4: (2, 6, 0, 0), 5: (63, 0, 0, 1)})), "r2")
        self.assertEqual([x["n"] for x in t.lines], [1, 2, 3, 4, 5])
        self.assertEqual(t.lines[2]["text"], "**** GOAL **** by Ekstrom")
        self.assertEqual(t.deltas, [3, 3])

    def test_a_record_still_unwritten_at_the_last_read_is_reported_unread(self):
        # the match ends with record 3 still unwritten: every read to the end notes it, and the note
        # stands as the record's unread report
        t = commentary.Tracker()
        t.add(commentary.Snapshot(make_state(3, {1: (2, 5, 0, 0), 2: (50, 6, 0, 1)})), "r1")
        t.add(commentary.Snapshot(make_state(3, {1: (2, 5, 0, 0), 2: (50, 6, 0, 1)})), "r2")
        self.assertEqual([x["n"] for x in t.lines], [1, 2])
        self.assertEqual(len(t.gaps), 2)
        self.assertTrue(all("record 3 is the end marker 0xFF" in g for g in t.gaps), t.gaps)
        self.assertEqual(t.deltas, [3, 1])

    def test_no_new_line(self):
        t = commentary.Tracker()
        snap = commentary.Snapshot(make_state(2, {1: (2, 5, 0, 0), 2: (2, 5, 0, 0)}))
        t.add(snap, "r1")
        t.add(snap, "r2")
        self.assertEqual(len(t.lines), 2)
        self.assertEqual(t.deltas, [2, 0])

    def test_events(self):
        t = commentary.Tracker()
        t.add(commentary.Snapshot(make_state(5, {1: (2, 5, 0, 0), 2: (38, 7, 0, 1), 3: (50, 6, 0, 0), 4: (51, 6, 0, 0), 5: (63, 0, 0, 1)})), "r1")
        self.assertEqual(t.events(), [("goal", 1, "**** GOAL **** by Ekstrom"), ("booking", 0, "Brolin BOOKED"), ("sending off", 0, "Brolin SENT OFF")])


if __name__ == "__main__":
    unittest.main()
