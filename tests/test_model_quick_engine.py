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


# ---------------------------------------------------------------------------
# T24 (round 3): one test class per modelled routine, on a richer fixture.
# Constants and branch expectations are hand-derived from the listing
# (static/goal-exe/code); the mutation run (PR body) flips each model constant
# or branch direction and watches these tests fail.
# ---------------------------------------------------------------------------

def build_fixture():
    """build_match()'s shape plus every table QuickMatch's routines read, and player
    fields chosen to exercise the predicates' branches (form 1 everywhere, energy 100,
    positions 11 then 1..10 for both pitch sides, a bench of five per team)."""
    st = FakeState()
    st.put_word(0xA917, COUNTRIES_AT)
    st.put_word(0xA919, 0)
    st.put_word(0xA91B, PLAYERS_OFF)
    st.put_word(0xA91D, PLAYERS_SEG)
    st.put_word(0xA91F, MANAGERS_OFF)
    st.put_word(0xA921, MANAGERS_SEG)
    st.put_word(0x7B62, 1)
    st.put_word(0x8336, 7)
    st.put(0x9B3C, b"\x00\x00")
    st.put_word(0x9B34, 1)              # team 0 = country 1 (pitch slots 12..22)
    st.put_word(0x9B36, 2)              # team 1 = country 2 (pitch slots 1..11)
    st.put(0x80FC, b"\x00")
    st.put(0x831A, b"\x00")
    st.put(0x9A3D, b"\x00")
    st.put(0x8319, b"\x2D")
    st.put(0x7C36, b"\x00")
    st.put(0x8324, b"\x00")
    st.put(0x7C39, b"\x00")
    st.put(0x9B3A, b"\x05\x05")
    st.put(0x8332, b"\x00\x00")
    st.put(0x8334, b"\x00\x00")
    st.put(0x668, b"\x0b\x00")          # side_base [11, 0]
    st.put(0x66B, b"\x05\x02")
    # --- tables ---------------------------------------------------------
    st.put(0x7920, b"\xff\x01")          # 65FE's form deltas: [-1, +1]
    fit = bytearray(0x28)
    fit[0x26] = 40                       # the quick goal id 0x26 -> +0x28 fitness
    st.put(0x720, bytes(fit))
    scorer = bytearray(31)               # byte at 0xA6B + rand(30), r in 1..30
    for r in range(1, 31):
        scorer[r] = 2 + (r % 10)
    st.put(0xA6B, bytes(scorer))
    st.put(0xA8A, b"\x0c\x10")           # attempts [12, 16]
    st.put(0xA8C, b"\x5a\x78")           # minute range [90, 120]
    st.put(0xA8E, b"\x21\x0a")           # stats element 1 [33, 10]
    st.put(0xA90, b"\x3c\x1e\x0b\x0a\x09\x08\x07\x06\x05\x04\x03\x02")
    st.put(0xD4E, bytes([0, 1, 1, 4, 4, 2, 2, 2, 2, 5, 5, 5, 3, 3, 0, 1]))
    form = bytearray(8 * 16)             # formation: count then +7 roles
    for pos in range(16):
        form[8 * pos] = 1
        form[8 * pos + 1] = 1
        form[8 * pos + 2] = 2
    form[8 * 5] = 2                      # position 5 expects two roles: 7 and 9
    form[8 * 5 + 1], form[8 * 5 + 2] = 7, 9
    st.put(0x99A, bytes(form))
    st.put(0x8CE, bytes([12]) + b"0123456789AB")       # Pos(pos char) = pos + 1
    bench = bytearray(0xE0)                            # BENCH_VALUE[14*pos + role]
    for i in range(0xE0):
        bench[i] = i & 0xFF
    st.put(0x8D5, bytes(bench))
    r008 = bytearray(129)
    r008[1], r008[2] = 0x14, 0x28
    st.put(0x9B7C, bytes(r008))
    st.put(0xA28, b"\x03\x09")            # BEC7's replacement positions [3, 9]
    foot = bytearray(0xE0)                # E60[14*E7C[w%3] + role]: 1 only at index 7
    foot[7] = 1
    st.put(0xE60, bytes(foot))
    st.put(0xE7C, b"\x00\x01\x02")
    st.put(0xE54, bytes([5] * 12))        # 2FAD = E54[w%12] + E46[+7]
    e46 = bytearray(16)
    e46[5] = 0x43                         # +7 == 5 -> 2FAD = 0x48 (the threshold)
    st.put(0xE46, bytes(e46))
    # --- pitch, players, squads ------------------------------------------
    for w in range(21, 32):               # team 1 (country 2): positions 11, 1..10
        set_player(st, w, country=2, pos=(11 if w == 21 else w - 21))
    for w in range(32, 43):               # team 0 (country 1): positions 11, 1..10
        set_player(st, w, country=1, pos=(11 if w == 32 else w - 32))
    set_player(st, 72, country=2, pos=6, role=7, skill=60)   # country 2's bench
    set_player(st, 73, country=2, pos=5, role=9, skill=60)
    for w in (74, 75, 76):
        set_player(st, w, country=2, pos=5, role=5, skill=60)
    for w in (52, 53, 54, 55, 56):        # country 1's bench
        set_player(st, w, country=1, pos=5, role=5, skill=60)
    for slot in range(1, 23):
        base = 0x80E8 + 0x16 * slot
        st.put(base + 6, bytes([slot]))
        st.put_word(base + 0xD, 20 + slot)
    for i in range(11):
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 2 + 2 * i, 21 + i)
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 1 + 2 * i, 32 + i)
    for i, w in enumerate([72, 73, 74, 75, 76]):
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 2 + 2 * (11 + i), w)
    for i, w in enumerate([52, 53, 54, 55, 56]):
        st.put_word(COUNTRIES_AT + COUNTRY_SIZE * 1 + 2 * (11 + i), w)
    return st


def set_player(st, w, country=0, pos=0, role=1, skill=100, form=1, energy=100,
               plus2=0, plus3=0, plus5=0, bitsF=0, bits10=0, fit12=0, goals=0):
    p = PLAYERS_AT + PLAYER_SIZE * w
    st.mem[p] = country
    st.mem[p + 2], st.mem[p + 3], st.mem[p + 5] = plus2, plus3, plus5
    st.mem[p + 4] = skill
    st.mem[p + 6] = pos
    st.mem[p + 7] = role
    st.mem[p + 0xA:p + 0xC] = goals.to_bytes(2, "little")
    st.mem[p + 0xC] = form
    st.mem[p + 0xE] = energy
    st.mem[p + 0xF] = bitsF
    st.mem[p + 0x10:p + 0x12] = bits10.to_bytes(2, "little")
    st.mem[p + 0x12:p + 0x14] = fit12.to_bytes(2, "little")


class ScriptedRNG:
    """Pops a scripted sequence (cycling when it runs out); every call's n is recorded,
    so an unexpected draw or a scripted value out of range fails."""

    def __init__(self, seq=()):
        self.seq = list(seq)
        self.calls = []

    def rand(self, n):
        self.calls.append(n)
        if not self.seq:
            raise AssertionError(f"unexpected draw rand({n})")
        v = self.seq.pop(0)
        self.seq.append(v)                       # cycle
        assert 1 <= v <= max(n, 1), f"scripted {v} out of range 1..{n}"
        return v

    def chance(self, n):
        return self.rand(n) == 1


class TestRNG(unittest.TestCase):
    """214B:0688: seed = seed*0x7ABD + 0x1B0F; value = ((seed*n)>>16) + 1; 06D0 = rand==1."""

    def test_step_and_value(self):
        rng = quick_engine.LCG(1)
        self.assertEqual([rng.rand(100) for _ in range(3)], [59, 92, 85])
        self.assertEqual(rng.seed, 0xD94E)       # 1 -> 0x95CC -> 0x4293 -> 0xD94E

    def test_value_uses_the_new_seed_and_n(self):
        rng = quick_engine.LCG(0)
        first = (0 * 0x7ABD + 0x1B0F) & 0xFFFF
        self.assertEqual(rng.rand(7), ((first * 7) >> 16) + 1)

    def test_chance_is_equality_with_one(self):
        rng = quick_engine.LCG(1)
        v = quick_engine.LCG(1).rand(59)         # the first value from seed 1 is 59
        self.assertEqual(rng.chance(59), v == 59)


class TestPlayerPredicates(unittest.TestCase):
    """3216, 3041, 3088, 3179, 2FFB."""

    def test_unavailable_energy_and_elements(self):
        st = build_fixture()
        set_player(st, 21, energy=0)              # +0xE < 1
        set_player(st, 22, bits10=1 << 7)         # element 8
        set_player(st, 23, bits10=1 << 5)         # element 6
        set_player(st, 24, bits10=1 << 2)         # element 3
        m = quick_engine.QuickMatch(st)
        for w in (21, 22, 23, 24):
            self.assertTrue(m.unavailable(w), f"player {w} should be unavailable")
        self.assertFalse(m.unavailable(25))

    def test_two_footed_is_sum_30(self):
        st = build_fixture()
        set_player(st, 21, plus5=12, plus2=18)
        m = quick_engine.QuickMatch(st)
        self.assertTrue(m.two_footed(21))
        self.assertFalse(m.two_footed(22))

    def test_foot_index_table(self):
        # foot = E60[14*E7C[w%3] + (+7)]; E7C = [0,1,2], E60 is 1 only at index 7
        st = build_fixture()
        set_player(st, 21, pos=6, role=7)         # 21%3=0 -> 14*0 + 7 = 7 -> 1
        set_player(st, 22, pos=6, role=7)         # 22%3=1 -> 14 + 7 = 21 -> 0
        m = quick_engine.QuickMatch(st)
        self.assertEqual(m.foot_index(21), 1)
        self.assertEqual(m.foot_index(22), 0)

    def test_wrong_foot_positions(self):
        st = build_fixture()
        set_player(st, 21, pos=3, role=7)     # foot 1, pos 3 in {3,7,10}
        set_player(st, 22, pos=4)             # foot 0, pos 4 in {4,8,11}
        set_player(st, 23, pos=3, role=7, plus5=12, plus2=18)  # two-footed: exempt
        m = quick_engine.QuickMatch(st)
        self.assertTrue(m.wrong_foot(21))
        self.assertTrue(m.wrong_foot(22))
        self.assertFalse(m.wrong_foot(23))
        st = build_fixture()                  # pos 0: wrong foot iff +7 != 0
        set_player(st, 24, pos=0, role=0)
        set_player(st, 25, pos=0, role=1)
        m = quick_engine.QuickMatch(st)
        self.assertFalse(m.wrong_foot(24))
        self.assertTrue(m.wrong_foot(25))

    def test_hardness(self):
        st = build_fixture()
        set_player(st, 21, pos=6, plus5=7, plus3=1)
        set_player(st, 22, pos=6, plus5=7)
        m = quick_engine.QuickMatch(st)
        self.assertEqual(m.hardness(21), 6)
        self.assertEqual(m.hardness(22), 7)


class TestPlayerStrength(unittest.TestCase):
    """377E: v = (+4) + s8(+0xE) - 0x3E; form < 0x20 adds, else v -= v idiv 16; clamp
    0..0x100; wrong foot halves (idiv); unavailable is 0."""

    def _with(self, w, **kw):
        kw.setdefault("pos", 6)               # neutral position: no wrong foot
        st = build_fixture()
        set_player(st, w, **kw)
        return quick_engine.QuickMatch(st)

    def test_low_form_adds(self):
        m = self._with(21, skill=100, energy=10, form=5)
        self.assertEqual(m.player_strength(21), 100 + 10 - 0x3E + 5)

    def test_high_form_shrinks(self):
        v = 100 + 10 - 0x3E
        m = self._with(21, skill=100, energy=10, form=0x25)
        self.assertEqual(m.player_strength(21), v - (v // 16))
        m = self._with(21, skill=100, energy=10, form=0x20)   # 0x20 itself shrinks
        self.assertEqual(m.player_strength(21), v - (v // 16))

    def test_clamp_both_ends(self):
        self.assertEqual(self._with(21, skill=220, energy=100, form=0).player_strength(21), 0x100)
        self.assertEqual(self._with(21, skill=0, energy=0, form=0).player_strength(21), 0)

    def test_unavailable_is_zero(self):
        m = self._with(21, bits10=1 << 7)
        self.assertEqual(m.player_strength(21), 0)

    def test_wrong_foot_halves(self):
        m = self._with(21, skill=100, energy=10, form=0, pos=3, role=7)  # foot 1
        self.assertEqual(m.player_strength(21), (100 + 10 - 0x3E) // 2)


class TestSetPlayerTactics(unittest.TestCase):
    """3431: hardness < 4 sets element 8 and clears 4; positions {0,1,3,4} set elements
    5 and 1; position 2 sets elements 6 and 2 (and 5 when +5 < 14); else nothing."""

    def test_all_branches(self):
        st = build_fixture()
        set_player(st, 21, pos=1, plus5=2, plus3=1)   # hardness 1 < 4, pos 1
        set_player(st, 22, pos=2, plus5=5, plus3=1)   # hardness 4, pos 2, +5 = 5 < 14
        set_player(st, 23, pos=2, plus5=20, plus3=1)  # hardness 4, pos 2, +5 = 20
        set_player(st, 24, pos=6, plus5=9, plus3=1)   # no branch at all
        set_player(st, 25, pos=1, plus5=9, plus3=0)   # hardness 9, pos 1
        set_player(st, 26, pos=4, plus5=9, plus3=1)   # hardness 9, pos 4: elements 5, 1
        set_player(st, 27, pos=2, plus5=14, plus3=1)  # +5 == 14: NO element 5
        m = quick_engine.QuickMatch(st)
        m.set_player_tactics(21)
        self.assertEqual(m._player(21)[0xF], (1 << 7) | (1 << 4) | (1 << 0))
        m.set_player_tactics(22)
        self.assertEqual(m._player(22)[0xF], (1 << 4) | (1 << 5) | (1 << 1))
        m.set_player_tactics(23)
        self.assertEqual(m._player(23)[0xF], (1 << 5) | (1 << 1))
        m.set_player_tactics(24)
        self.assertEqual(m._player(24)[0xF], 0)
        m.set_player_tactics(25)
        self.assertEqual(m._player(25)[0xF], (1 << 4) | (1 << 0))
        m.set_player_tactics(26)
        self.assertEqual(m._player(26)[0xF], (1 << 4) | (1 << 0))
        m.set_player_tactics(27)
        self.assertEqual(m._player(27)[0xF], (1 << 5) | (1 << 1))


class TestLineSums(unittest.TestCase):
    """0AA7 (manager byte zero-extended, /8 + 0x10) and 0BC4: v+M per player, m8 shares
    to attack or defence by +0xF/tactics, the pos->line table, and the flag's idiv-8
    boost. On the base fixture both tactics bytes are 0 (every non-keeper share lands
    on defence) and the sums are team 0 = [0, 460, 865, 231], team 1 = [0, 495, 935,
    196] (both sides' players: strength 139 except the wrong-foot positions 3, 4, 8 at
    69; no pos-0 player, so the keeper line is 0)."""

    def test_base_sums(self):
        m = quick_engine.QuickMatch(build_fixture())
        self.assertEqual(m.line_sums(0, 0, 1), [0, 460, 865, 231])
        self.assertEqual(m.line_sums(0, 0, 2), [0, 495, 935, 196])

    def test_manager_bonus_zero_extended(self):
        st = build_fixture()
        st.put(COUNTRIES_AT + COUNTRY_SIZE * 2 + 0x2E, b"\x02")  # country 2 managed 2
        st.put(MANAGERS_AT + 3 * 2 + 1, b"\x40")                 # quality 0x40
        m = quick_engine.QuickMatch(st)
        self.assertEqual(m.manager_bonus(2), 0x40 // 8 + 0x10)
        st.put(MANAGERS_AT + 3 * 2 + 1, b"\x88")                 # 0x88 unsigned = 136
        m = quick_engine.QuickMatch(st)
        self.assertEqual(m.manager_bonus(2), 136 // 8 + 0x10)

    def test_player_f_share_moves_to_attack(self):
        st = build_fixture()
        m = quick_engine.QuickMatch(st)
        base = m.line_sums(0, 0, 1)
        set_player(st, 37, pos=5, bitsF=(1 << 4) | 1)  # elements 5 and 1 -> attack
        m = quick_engine.QuickMatch(st)
        moved = m.line_sums(0, 0, 1)
        m8 = m.manager_bonus(1) // 8
        self.assertEqual(moved[3] - base[3], m8)
        self.assertEqual(base[1] - moved[1], m8)

    def test_tactics_bit_moves_share(self):
        st = build_fixture()
        m = quick_engine.QuickMatch(st)
        base = m.line_sums(0, 0, 1)
        m._country(1)["tactics"] = 0x3F           # elements 1..6 all set
        after = m.line_sums(0, 0, 1)
        m8 = m.manager_bonus(1) // 8
        self.assertEqual(after[3] - base[3], 3 * 11 * m8)   # e in {1,5,6} x 11 players
        self.assertEqual(base[1] - after[1], 3 * 11 * m8)

    def test_flag_boosts_eighths(self):
        m = quick_engine.QuickMatch(build_fixture())
        s0 = m.line_sums(0, 0, 1)
        s1 = m.line_sums(1, 0, 1)
        for k in range(4):
            self.assertEqual(s1[k] - s0[k], quick_engine.idiv(s0[k], 8))


class TestRollQuickGoals(unittest.TestCase):
    """B19D: per attempt the OPPONENT's draw comes first (side 1-t), the own side's
    second; a lost contest (jle) stops the attempt; all three won -> a goal; team t
    draws against side 1-t's sums. Team sums on the fixture: t0 = [0, 460, 865, 231],
    t1 = [0, 495, 935, 196]."""

    def setUp(self):
        self.m = quick_engine.QuickMatch(build_fixture())
        self.s0 = [0, 460, 865, 231]
        self.s1 = [0, 495, 935, 196]

    def test_order_and_stop(self):
        rng = ScriptedRNG([2, 1])               # own 1 <= opponent 2: stop after c1
        self.m.rng = rng
        fresh = self.m.roll_quick_goals(1)
        self.assertEqual(rng.calls[:2], [self.s1[2], self.s0[2]])   # mid[1-t], mid[t]
        self.assertEqual(fresh, [0, 0])

    def test_equal_values_lose(self):
        # jle: the own draw equal to the opponent's also stops the attempt
        rng = ScriptedRNG([3, 3])
        self.m.rng = rng
        fresh = self.m.roll_quick_goals(1)
        self.assertEqual(len(rng.calls), 4)    # one attempt per team, two draws each
        self.assertEqual(fresh, [0, 0])

    def test_second_contest_uses_double_defence(self):
        rng = ScriptedRNG([1, 5, 5, 1])         # c1 passes, c2 fails (1 <= 5)
        self.m.rng = rng
        self.m.roll_quick_goals(1)
        self.assertEqual(rng.calls[:4],
                         [self.s1[2], self.s0[2], 2 * self.s1[1], self.s0[3]])

    def test_goal_needs_all_three(self):
        rng = ScriptedRNG([1, 5, 1, 5, 1, 5])   # every own draw above the opponent's
        self.m.rng = rng
        fresh = self.m.roll_quick_goals(12)     # the fixture's 12 attempts per team
        self.assertEqual(rng.calls[:6], [self.s1[2], self.s0[2], 2 * self.s1[1],
                                         self.s0[3], self.s1[0], self.s0[3]])
        self.assertEqual(fresh, [12, 12])       # all 12 attempts of both teams win


class TestComputerTactics(unittest.TestCase):
    """C173's tree: BD83 resets +0x2D to R008, adds 2 rand(6) includes when stronger,
    and clears the once flags; BF6B includes or excludes 3 rand(6) elements; C01A
    includes 5 rand(5) plus element 6, once only; C0DF excludes 5 rand(5) plus 6."""

    def test_bd83_resets_to_r008(self):
        m = quick_engine.QuickMatch(build_fixture())
        m._country(2)["tactics"] = 0xFF
        m.bd83(1)
        self.assertEqual(m._country(2)["tactics"], 0x28)
        self.assertEqual((m.once_8332[1], m.once_8334[1]), (0, 0))

    def test_bd83_strength_draws_two_includes(self):
        m = quick_engine.QuickMatch(build_fixture())
        m.team_stronger = lambda t: True
        m.rng = ScriptedRNG([1, 2])
        m.bd83(1)
        self.assertEqual(m._country(2)["tactics"], 0x28 | 1 | 2)

    def test_bf6b_three_includes_or_excludes(self):
        m = quick_engine.QuickMatch(build_fixture())
        m.team_stronger = lambda t: False
        m.rng = ScriptedRNG([1, 2, 3])
        m.bf6b(1, 1)
        self.assertEqual(m._country(2)["tactics"], 0x28 | 1 | 2 | 4)
        self.assertEqual(len(m.rng.calls), 3)   # exactly three rand(6) draws
        m = quick_engine.QuickMatch(build_fixture())
        m.team_stronger = lambda t: False
        m._country(2)["tactics"] = 0x3F
        m.rng = ScriptedRNG([1, 2, 3])
        m.bf6b(0, 1)
        self.assertEqual(m._country(2)["tactics"], 0x28)

    def test_c01a_once_flag_and_elements(self):
        m = quick_engine.QuickMatch(build_fixture())
        m.rng = ScriptedRNG([1, 1, 1, 1, 1])    # rand(5) results are ELEMENT numbers
        m.c01a(1)
        self.assertEqual(m._country(2)["tactics"], (1 << 0) | (1 << 5))  # elements 1, 6
        self.assertEqual(len(m.rng.calls), 5)   # exactly five rand(5) draws
        self.assertEqual(m.once_8332[1], 1)
        m.rng = ScriptedRNG()
        m.c01a(1)                                # the once flag: no more draws
        self.assertEqual(m.rng.calls, [])

    def test_c0df_excludes_five_plus_six(self):
        m = quick_engine.QuickMatch(build_fixture())
        m._country(2)["tactics"] = 0xFF
        m.rng = ScriptedRNG([1, 1, 1, 1, 1])    # exclude element 1 five times
        m.c0df(1)
        self.assertEqual(m._country(2)["tactics"], 0xFF & ~((1 << 0) | (1 << 5)))
        self.assertEqual(m.once_8334[1], 1)

    def test_c173_routes_by_score(self):
        m = quick_engine.QuickMatch(build_fixture())
        m._country(1)["managed"] = 0x90         # team 0's country: managed, skipped
        calls = []
        m.bd83 = lambda t: (calls.append(t), self.assertEqual(t, 1))
        m.score = [0, 0]                         # d = 0, |d| < 2 -> BD83 for team 1
        m.c173()
        m.score = [1, 0]                         # |d| = 1: still BD83 (ad < 2)
        m.c173()
        self.assertEqual(calls, [1, 1])
        m.bd83 = lambda t: None
        m.score = [3, 1]                         # |d| = 2, team 1 behind -> BF6B(1, 1)
        m.bf6b = lambda flag, t: self.assertEqual((flag, t), (1, 1))
        m.c173()
        m.bf6b = lambda flag, t: None
        m.score = [0, 4]                         # |d| = 4, team 1 ahead -> C0DF(1)
        m.c0df = lambda t: self.assertEqual(t, 1)
        m.c173()
        m.c0df = lambda t: None
        m.score = [5, 0]                         # |d| = 5, team 1 behind -> C01A(1)
        m.c01a = lambda t: self.assertEqual(t, 1)
        m.c173()


class TestBec7(unittest.TestCase):
    """BEC7 re-places only the FIRST available back-four player (positions 9..11), at
    A28[1] when 2FAD >= 0x48, else A28[0]."""

    def test_first_only_and_threshold(self):
        st = build_fixture()
        set_player(st, 21, pos=11, role=5)       # squad word 1: FIRST, 2FAD = 0x48
        set_player(st, 23, pos=10, role=5)       # squad word 3: qualifies, not first
        set_player(st, 24, pos=9, role=0)        # squad word 4: in the set, not first
        m = quick_engine.QuickMatch(st)
        m.bec7(2)
        self.assertEqual(m._player(21)[6], 9)    # A28[1]: 2FAD = 0x48 >= 0x48
        self.assertEqual(m._player(23)[6], 10)   # untouched: not the first
        self.assertEqual(m._player(24)[6], 9)    # untouched: not the first


class TestAfterGoal(unittest.TestCase):
    """6337's keeper redraw (rand(10), +1, on the side of the old 830B) and 65FE's
    per-slot form swing: every available player moves +1 on the side of DS:830B and
    -1 on the other, with 7CC5's 1..0xFF clamp (T24 round 3's fix)."""

    def test_6337_keeper_redraw(self):
        m = quick_engine.QuickMatch(build_fixture())
        m.c173 = lambda: None
        m.after_goal_form_swing = lambda: None
        m.eight30b = 1                          # a team-1 keeper slot
        m.rng = ScriptedRNG([4])
        m.after_goal()
        self.assertEqual(m.eight30b, 4 + 1)     # 0668[2996=1] = 0, r + 1
        m.eight30b = 12                         # a team-0 keeper slot
        m.rng = ScriptedRNG([4])
        m.after_goal()
        self.assertEqual(m.eight30b, 11 + 4 + 1)
        m.eight30b = 5                          # not a keeper slot: no draw at all
        m.rng = ScriptedRNG()
        m.after_goal()
        self.assertEqual(m.rng.calls, [])

    def test_form_swing_sides_clamp_and_skip(self):
        st = build_fixture()
        set_player(st, 21, pos=6, form=1)       # team 1: +1
        set_player(st, 22, pos=6, form=1, bits10=1 << 7)   # unavailable: skipped
        set_player(st, 32, pos=6, form=1)       # team 0: 1 - 1 = 0 -> clamps at 1
        set_player(st, 33, pos=6, form=0x1F)    # team 0: 31 - 1
        m = quick_engine.QuickMatch(st)
        m.eight30b = 5                          # side 1 holds 830B
        m.after_goal_form_swing()
        self.assertEqual(m._player(21)[0xC], 2)
        self.assertEqual(m._player(22)[0xC], 1)  # unavailable: unchanged
        self.assertEqual(m._player(32)[0xC], 1)  # clamp lower bound
        self.assertEqual(m._player(33)[0xC], 0x1E)

    def test_form_swing_follows_830b_side(self):
        st = build_fixture()
        set_player(st, 21, pos=6, form=0x10)
        set_player(st, 32, pos=6, form=0x10)
        m = quick_engine.QuickMatch(st)
        m.eight30b = 15                         # side 0 holds 830B now
        m.after_goal_form_swing()
        self.assertEqual(m._player(21)[0xC], 0x0F)
        self.assertEqual(m._player(32)[0xC], 0x11)
        m = quick_engine.QuickMatch(build_fixture())
        set_player(st, 21, pos=6, form=0x10)
        m = quick_engine.QuickMatch(st)
        m.eight30b = 11                         # 11 < 12: still side 1
        m.after_goal_form_swing()
        self.assertEqual(m._player(21)[0xC], 0x11)
        self.assertEqual(m._player(32)[0xC], 0x0F)

    def test_swing_runs_after_c173(self):
        """65FE's order: 6337 -> C173 -> the form loop (6666 comes after 665C)."""
        m = quick_engine.QuickMatch(build_fixture())
        order = []
        m.c173 = lambda: order.append("c173")
        real = m.after_goal_form_swing
        m.after_goal_form_swing = lambda: (order.append("swing"), real())
        m.eight30b = 5
        m.after_goal()
        self.assertEqual(order, ["c173", "swing"])

    def test_scorer_effects(self):
        """6443's scorer writes: +0A++, +0xC clamp(+1), +0x12 += fitness[0x26] = 40."""
        st = build_fixture()
        set_player(st, 21, pos=6, form=0x1F, fit12=0x100, goals=2)
        m = quick_engine.QuickMatch(st)
        m.record_goal_scorer_effects(21)
        p = m._player(21)
        self.assertEqual(int.from_bytes(p[0xA:0xC], "little"), 3)
        self.assertEqual(p[0xC], 0x20)
        self.assertEqual(int.from_bytes(p[0x12:0x14], "little"), 0x128)


class TestCheckSubstitutions(unittest.TestCase):
    """8062's unmanaged branch: the scan needs element 6 clear, +0xE > 0, the clock gate
    1 < 831B < 0x23, and the player's signed +0x12 < 0x5A - 831B."""

    def test_clock_gates(self):
        m = quick_engine.QuickMatch(build_fixture())
        fired = []
        m.c88d = lambda t, slot: fired.append((t, slot))
        m.check_substitutions(0x23)             # 831B == 0x23: jae skips
        m.check_substitutions(1)                # 831B == 1: jbe skips
        self.assertEqual(fired, [])
        self.assertEqual(m.sub_budget, [5, 5])

    def test_energy_gate_boundary(self):
        st = build_fixture()
        for w in range(21, 43):
            set_player(st, w, pos=(11 if w in (21, 32) else (w - 21 if w < 32 else w - 32)),
                      fit12=0x46)
        set_player(st, 33, pos=1, fit12=10, energy=1)   # +0xE == 1: still eligible
        m = quick_engine.QuickMatch(st)
        fired = []
        m.c88d = lambda t, slot: fired.append((t, slot))
        m.check_substitutions(20)
        self.assertEqual(fired, [(0, 13)])

    def test_player_gates(self):
        st = build_fixture()
        for w in range(21, 43):                 # both teams' eleven: +0x12 = 70 fails
            set_player(st, w, pos=(11 if w in (21, 32) else (w - 21 if w < 32 else w - 32)),
                      fit12=0x46)
        set_player(st, 33, pos=1, fit12=10)     # 10 < 70: the only eligible one
        m = quick_engine.QuickMatch(st)
        fired = []
        m.c88d = lambda t, slot: fired.append((t, slot))
        m.check_substitutions(20)               # 0x5A - 20 = 70
        self.assertEqual(fired, [(0, 13)])
        st = build_fixture()
        for w in range(21, 43):
            set_player(st, w, pos=(11 if w in (21, 32) else (w - 21 if w < 32 else w - 32)),
                      fit12=0x46)
        set_player(st, 33, pos=1, fit12=0x46)   # 70 >= 70: nobody eligible
        m = quick_engine.QuickMatch(st)
        fired = []
        m.c88d = lambda t, slot: fired.append((t, slot))
        m.check_substitutions(20)
        self.assertEqual(fired, [])


class TestC88dBenchPick(unittest.TestCase):
    """C88D: aae8 walks the outgoing position's formation roles against c7eb's bench
    map with the foot expectation, copies the outgoing's position onto the chosen
    bench player, and spends the budget."""

    def test_aae8_picks_formation_role(self):
        st = build_fixture()
        set_player(st, 25, pos=5, role=1)       # team 1's slot 5: formation[5]=[2,7,9]
        # pitch+6 of slot 5 deliberately NOT its address: C88D's s is address-based
        # (C8AE: slot - 0668[t]), so the squad swap hits squad word 5, not word 8
        st.put(0x80E8 + 0x16 * 5 + 6, b"\x08")
        m = quick_engine.QuickMatch(st)
        fired = {}
        m.c5dc = lambda chosen, slot, t, incoming: fired.update(
            chosen=chosen, slot=slot, t=t, incoming=incoming)
        self.assertTrue(m.c88d(1, 5))
        # c7eb: bench 72 has +7 = 7 (foot 1, the expected foot for count 6 > 3)
        self.assertEqual(fired["chosen"], 12)
        self.assertEqual(fired["incoming"], 72)
        self.assertEqual(m._squad(1)[4], 72)     # the swap hit squad word 5 (address)
        self.assertEqual(m.sub_budget[1], 5)     # the rigged c5dc spent nothing
        m2 = quick_engine.QuickMatch(st)
        m2.c88d(1, 5)                            # the real c5dc runs
        self.assertEqual(m2.sub_budget[1], 4)
        self.assertEqual(m2._player(72)[6], 5)   # the position copy (C9AD-C9CA)

    def test_no_candidate_no_sub(self):
        st = build_fixture()
        for w in (72, 73, 74, 75, 76):
            set_player(st, w, country=2, pos=5, role=7, skill=60, bits10=1 << 7)
        m = quick_engine.QuickMatch(st)
        self.assertFalse(m.c88d(1, 5))
        self.assertEqual(m.sub_budget[1], 5)


class TestA9B8KeeperFallback(unittest.TestCase):
    """T24 rework R1: C88D's keeper fallback A9B8 (C912-C96B) — the best bench slot
    12..20 by BENCH_VALUE[14*pos + (+7)] (AA4E-AA68), with the foot-halving
    (AAAD-AAB7) and the STRICT `v > best_v` compare (AABA-AACB) against a best_v
    that starts at 0. The round-1 review's surviving mutation `best, best_v = 0, 255`
    suppresses every valid replacement (a bench value never reaches 255), so this
    test must fail under it (rule 9: the mutation run is in the PR body)."""

    def test_keeper_fallback_selection(self):
        m = quick_engine.QuickMatch(build_fixture())
        # pos 0: Pos(0) = 7 > 3, so the foot expectation is 1 and the halving is
        # armed. Candidates of team 1: 72 -> BENCH_VALUE[7] = 7, foot 1 == expect
        # (no halving); 73 -> BENCH_VALUE[9] = 9 but foot 0 != 1 -> halved to 4;
        # 74..76 -> BENCH_VALUE[5] = 5 (foot 0, also not winning). 7 wins: slot 12.
        self.assertEqual(m.foot_index(72), 1)
        self.assertEqual(m.foot_index(73), 0)
        self.assertEqual(m.a9b8(1, 0), 12)    # 7 beats the halved 4 and the 5s
        # team 0's bench (52..56, role 5): every foot check halves 5 to 2, so the
        # first candidate wins on the strict compare — still a replacement, not 0
        self.assertEqual(m.a9b8(0, 0), 12)

    def test_no_bench_value_beats_255(self):
        # the mutation's premise: BENCH_VALUE bytes max at 0xDF, so nothing can
        # beat a 255 initialiser — only the 0 initialiser lets a candidate win
        m = quick_engine.QuickMatch(build_fixture())
        self.assertLess(max(m.t_benchvalue), 255)


class TestD733Structure(unittest.TestCase):
    """D733: 4 stats draws before the fill; the fill only when fresh > saved; at most
    one goal per call and DA34's end of the team loop; the scorer redrawn while
    unavailable; energy only when 831B % 5 == 0; D5C1 only with 9A3D set."""

    def _match(self, seq, fresh, minute=50, minute_831b=41, st=None):
        m = quick_engine.QuickMatch(st or build_fixture())
        m.rng = ScriptedRNG(seq)
        m.roll_quick_goals = lambda attempts: fresh
        m.after_goal = lambda: None
        m.d733(minute, minute_831b)
        return m

    def test_stats_draws_and_no_fill_without_fresh(self):
        m = self._match([2, 2, 2, 2], [0, 0])
        self.assertEqual(m.rng.calls, [60, 33, 60, 33])   # element 5/1 clear: 60/33
        self.assertEqual(m.score, [0, 0])

    def test_fill_and_goal_phase(self):
        # team 0 fresh 1: the fill draws j=0's minute (50 == 831F); the goal phase
        # scores it; scorer slot r=1 -> t_scorer[1] = 3 -> team 0's squad word 2 = 34
        m = self._match([2, 2, 2, 2, 50, 1], [1, 0])
        self.assertEqual(m.score, [1, 0])
        self.assertEqual(len(m.goals), 1)
        self.assertEqual(m.goals[0]["player"], 34)
        self.assertEqual(m.goals[0]["minute"], 50)
        self.assertEqual(m.goals[0]["team"], 0)
        self.assertEqual(m.eight30b, 11 + 3)    # 0668[0] + the squad slot of player 34

    def test_scored_goal_invokes_scorer_effects(self):
        """T24 rework R2: D733's goal path must run 6443's scorer writes on the
        scorer it selected (the record_goal_scorer_effects call, DA16-DA2C).
        Removing that call leaves the scorer's goals counter, form and fitness
        untouched; the helper-level TestAfterGoal.test_scorer_effects cannot
        catch it, this integrated one must (rule 9, mutation run in the PR body)."""
        st = build_fixture()
        set_player(st, 34, pos=6, form=0x1F, fit12=0x100, goals=2)
        m = self._match([2, 2, 2, 2, 50, 1], [1, 0], st=st)
        self.assertEqual(m.goals[0]["player"], 34)      # the premise: 34 scored
        p = m._player(34)
        self.assertEqual(int.from_bytes(p[0xA:0xC], "little"), 3)         # 6484: inc word
        self.assertEqual(p[0xC], 0x20)                                   # 7CC5: clamp(+1)
        self.assertEqual(int.from_bytes(p[0x12:0x14], "little"), 0x128)   # 1E9C: +40

    def test_goal_ends_the_team_loop(self):
        # both teams fresh 1: j=0 draws 50 and scores, j=1 draws 90 (never scored)
        m = self._match([2, 2, 2, 2, 50, 90, 1], [1, 1])
        self.assertEqual(m.rng.calls, [60, 33, 60, 33, 90, 90, 30])   # n's, not values
        self.assertEqual(m.score, [1, 0])

    def test_one_goal_even_with_two_equal_minutes(self):
        # two fill minutes both equal to 831F: the k-loop break (D93C-D944) keeps it
        # at one goal per D733 call
        m = self._match([2, 2, 2, 2, 50, 50, 1, 1], [2, 0])
        self.assertEqual(len(m.goals), 1)
        self.assertEqual(m.score, [1, 0])

    def test_no_goal_when_minute_differs(self):
        m = self._match([2, 2, 2, 2, 51], [1, 0])
        self.assertEqual(m.score, [0, 0])
        self.assertEqual(m.rng.calls, [60, 33, 60, 33, 90])           # n's, not values

    def test_scorer_table_last_entry(self):
        # R1: the draw reads the byte at 0xA6B + rand(30), r in 1..30, so index 30
        # (byte 0xA89) is legal
        m = self._match([2, 2, 2, 2, 50, 30], [1, 0])
        self.assertEqual(m.goals[0]["player"], 33)   # t_scorer[30] = 2 -> squad word 1

    def test_scorer_redrawn_while_unavailable(self):
        st = build_fixture()
        set_player(st, 34, pos=2, bits10=1 << 7)   # t_scorer[1]=3 -> 34: unavailable
        m = self._match([2, 2, 2, 2, 50, 1, 2], [1, 0], st=st)
        self.assertEqual(m.goals[0]["player"], 35)  # t_scorer[2] = 4 -> squad word 3

    def test_energy_every_fifth_minute(self):
        for minute_831b, expected in ((45, 9), (40, 9), (44, 10), (41, 10)):
            st = build_fixture()
            set_player(st, 21, pos=6, energy=10)
            m = quick_engine.QuickMatch(st)
            m.rng = ScriptedRNG([2, 2, 2, 2])
            m.roll_quick_goals = lambda attempts: [0, 0]
            m.d733(50, minute_831b)             # 45 and 40: % 5 == 0; 44 and 41: not
            self.assertEqual(m._player(21)[0xE], expected, minute_831b)

    def test_d5c1_gated_on_9a3d(self):
        m = quick_engine.QuickMatch(build_fixture())
        m.rng = ScriptedRNG([2, 2, 2, 2])
        m.roll_quick_goals = lambda attempts: [0, 0]
        m.d5c1 = lambda: self.fail("D5C1 called with 9A3D clear")
        m.d733(50, 41)
        m.ninea3d = 1
        m.rng = ScriptedRNG([2, 2, 2, 2])
        called = []
        m.d5c1 = lambda: called.append(1)
        m.d733(50, 41)
        self.assertEqual(called, [1])


class TestD5C1Prefix(unittest.TestCase):
    """R9: r = rand(10) + 1; both availability checks (the r slot first) come before
    the 06FA coin, so a return at either saves the coin draw."""

    def test_r_then_coin_when_both_available(self):
        m = quick_engine.QuickMatch(build_fixture())
        m.rng = ScriptedRNG([3, 1])              # r = 4: slots 4 (team 1) and 20
        with self.assertRaises(quick_engine.FoulPathNotModelled):
            m.d5c1()                            # both slots available: the coin draws
        self.assertEqual(m.rng.calls, [10, 2])

    def test_unavailable_r_slot_returns_before_coin(self):
        st = build_fixture()
        set_player(st, 24, pos=3, energy=0)     # pitch slot 4 = the r slot for r = 4
        m = quick_engine.QuickMatch(st)
        m.rng = ScriptedRNG([3])
        m.d5c1()                                # returns at D618: only rand(10)
        self.assertEqual(m.rng.calls, [10])


class TestRun(unittest.TestCase):
    """run(): 46 D733 calls with 831F = 46..91 and 831B = 45..0; DS:8336 never moves."""

    def test_run_shape_and_clock(self):
        m = quick_engine.QuickMatch(build_fixture())

        class Cycler:
            def __init__(self):
                self.draws = 0
                self.seed = 1

            def rand(self, n):
                self.draws += 1
                return 2

            def chance(self, n):
                return self.rand(n) == 1

        m.rng = Cycler()
        m.roll_quick_goals = lambda attempts: [0, 0]
        m.check_substitutions = lambda minute_831b: None   # covered by its own tests
        seen = []
        real = m.d733

        def spy(minute, minute_831b):
            seen.append((minute, minute_831b))
            return real(minute, minute_831b)

        m.d733 = spy
        out = m.run()
        self.assertEqual(seen[0], (46, 45))
        self.assertEqual(seen[-1], (91, 0))
        self.assertEqual(len(seen), 46)
        self.assertEqual(m.rng.draws, 46 * 4)    # 4 stats draws per minute, no fills
        self.assertEqual(out["score"], (0, 0))
        self.assertEqual(out["seed_DS8336"], 7)


if __name__ == "__main__":
    unittest.main()
