"""T23 rework round 3 (review round 2 findings R1 and R2), on a synthetic savestate built here.

R1 (blocking): 0791:254D sets the a260 loop bound to base+11 (`add ax, 0xb`), 255F starts the
slot counter at base+1, and 2581 calls a260 BEFORE 2587/258A compare the counter against the
bound — so a260 runs on ALL eleven slots base+1..base+11. The probe is the reviewer's: an
aligned, deliberately unsorted pitch/squad whose first player has the largest sort key, so
apply_230c() moves it to the last slot; a260 must then reset that slot's pitch+6 to its own
address (22 for team 0, 11 for team 1), not leave the traveled value (12 / 1).

R2 (not blocking): seg_0791_20.asm has ONE C6FA/C718/C724 sequence in c5dc, so the incoming
player's initialisation and set_player_tactics() run once per substitution, not twice.

No DOSBox-X, no original file, no /dev: the state is a flat synthetic memory (seeded Python
randomness only, and none is needed)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))

import quick_engine  # noqa: E402  (inserts runtime/driver into sys.path itself)

PLAYER_SIZE = quick_engine.PLAYER_SIZE    # 0x14
COUNTRY_SIZE = quick_engine.COUNTRY_SIZE  # 0xBF
PLAYERS_SEG, PLAYERS_OFF = 0x1000, 0       # linear 0x10000: the player array's far pointer
PLAYERS_AT = PLAYERS_SEG * 16 + PLAYERS_OFF
COUNTRIES_AT = 0x2000                      # segment 0, offset 0x2000
MANAGERS_SEG, MANAGERS_OFF = 0x1F00, 0     # linear 0x1F000: the manager table
MANAGERS_AT = MANAGERS_SEG * 16 + MANAGERS_OFF
MEM_SIZE = 0x1F400


class FakeState:
    """Only what QuickMatch reads: DS offsets address the flat array directly (DS base 0)."""

    def __init__(self):
        self.mem = bytearray(MEM_SIZE)

    def memory(self, addr, n):
        return bytes(self.mem[addr:addr + n])

    def ds_bytes(self, off, n):
        return self.memory(off, n)

    def ds_word(self, off):
        return int.from_bytes(self.ds_bytes(off, 2), "little")

    def put(self, off, data):
        self.mem[off:off + len(data)] = data

    def put_word(self, off, w):
        self.put(off, w.to_bytes(2, "little"))


def build_match():
    """A QuickMatch at a half-time stall: country 1 (team 0, slots 12..22) against country 2
    (team 1, slots 1..11), both with deliberately unsorted pitches: the FIRST slot of each side
    holds the player with the LARGEST sort key, so the 230C sort moves it to the LAST slot."""
    st = FakeState()
    # the far pointers players.py reads (offset:segment, offset first)
    st.put_word(0xA917, COUNTRIES_AT)   # DS:A917 -> the country array (segment 0)
    st.put_word(0xA919, 0)
    st.put_word(0xA91B, PLAYERS_OFF)    # DS:A91B -> the player array
    st.put_word(0xA91D, PLAYERS_SEG)
    st.put_word(0xA91F, MANAGERS_OFF)   # DS:A91F -> the manager table
    st.put_word(0xA921, MANAGERS_SEG)
    # the scalars __init__ reads (a normal half-time stall: no extra time, five subs each)
    st.put_word(0x7B62, 1)
    st.put_word(0x8336, 1)
    st.put(0x9B3C, b"\x00\x00")         # score
    st.put_word(0x9B34, 1)              # team 0 = country 1
    st.put_word(0x9B36, 2)              # team 1 = country 2
    st.put(0x80FC, b"\x00")
    st.put(0x831A, b"\x00")
    st.put(0x9A3D, b"\x00")
    st.put(0x8319, b"\x2D")             # the half length marker of a normal match
    st.put(0x7C36, b"\x00")             # no extra time
    st.put(0x8324, b"\x00")
    st.put(0x7C39, b"\x00")
    st.put(0x9B3A, b"\x05\x05")         # the substitution budget
    st.put(0x8332, b"\x00\x00")
    st.put(0x8334, b"\x00\x00")
    st.put(0x668, b"\x0b\x00")          # side_base = [11, 0]: team 0 owns slots 12..22
    # the pitch records (0x80E8 + 0x16*slot): +6 the slot number, +0xD the player word
    for slot in range(1, 23):
        base = 0x80E8 + 0x16 * slot
        st.put(base + 6, bytes([slot]))
        st.put_word(base + 0xD, 20 + slot)      # slot s -> player 20+s (21..31 / 32..42)
    # the player records: +6 the position (the sort key), +0xE the stamina (available)
    # team 1 (country 2, players 21..31, slots 1..11): the first player's key is the largest,
    # so the sort moves it from slot 1 to slot 11
    for w in range(21, 32):
        p = PLAYERS_AT + PLAYER_SIZE * w
        st.mem[p] = 2
        st.mem[p + 6] = 11 if w == 21 else w - 21
        st.mem[p + 0xE] = 100
    # team 0 (country 1, players 32..42, slots 12..22): same shape, first -> last (slot 22)
    for w in range(32, 43):
        p = PLAYERS_AT + PLAYER_SIZE * w
        st.mem[p] = 1
        st.mem[p + 6] = 11 if w == 32 else w - 32
        st.mem[p + 0xE] = 100
    # the country records: 20 squad words each, aligned with the pitch (squad slot s of team t
    # names the player pitch slot side_base[t]+s names, as 2218's swaps keep them)
    for i in range(11):
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 2 + 2 * i, 21 + i)   # country 2 (team 1)
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 1 + 2 * i, 32 + i)   # country 1 (team 0)
    for i in range(11, 20):                                            # the bench words
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 2 + 2 * i, 63 + i)
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 1 + 2 * i, 52 + i)
    return quick_engine.QuickMatch(st)


class A260Extent(unittest.TestCase):
    """R1: a260 runs on base+1..base+11 (254D/255F/2581-258A), so the LAST slot's pitch+6 is
    its own address after the 230C sort, not the traveled value of the slot it started at."""

    def test_last_slot_gets_its_own_address(self):
        m = build_match()
        first0, first1 = m.pitch[12]["player"], m.pitch[1]["player"]
        m.apply_230c()
        # the probe's premise: the sort moved each side's first player to the last slot
        self.assertEqual(m.pitch[22]["player"], first0)
        self.assertEqual(m.pitch[11]["player"], first1)
        # a260 (A269) reset pitch+6 := the address slot on every slot base+1..base+11
        for slot in range(1, 23):
            self.assertEqual(m.pitch[slot]["slot_no"], slot,
                             f"slot {slot}: pitch+6 is {m.pitch[slot]['slot_no']}, not the address")
        # the reviewer's exact probe: the last team-0 slot must be 22, not the stale 12
        self.assertEqual(m.pitch[22]["slot_no"], 22)
        self.assertEqual(m.pitch[11]["slot_no"], 11)


class C5dcSingleTacticsCall(unittest.TestCase):
    """R2: one C6FA/C718/C724 sequence in the listing, so one set_player_tactics call."""

    def test_set_player_tactics_called_once(self):
        m = build_match()
        incoming = m.pitch[12]["player"]      # the word a2e6 hands to the C6FA block
        calls = []
        real = m.set_player_tactics

        def counting(w):
            calls.append(w)
            return real(w)

        m.set_player_tactics = counting
        m.c5dc(chosen=12, slot=12, t=0, incoming=incoming)
        self.assertEqual(calls, [incoming])


if __name__ == "__main__":
    unittest.main()
