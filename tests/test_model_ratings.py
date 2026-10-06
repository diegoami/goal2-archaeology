#!/usr/bin/env python3
"""Unit tests for runtime/model/ratings.py (T26, Q011; E012). Every constant the tests pin
cites the listing line it comes from; the data-file test makes any single delta mutation fail,
and the behaviour tests pin the initial value, the substitution write, the decode (bucket)
threshold and the man-of-the-match scan's order. Run: python3 -m unittest -v tests.test_model_ratings"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import ratings as R  # noqa: E402

TEAMS = [[101 + i for i in range(11)] + [0] * 9,          # slots 1..11 filled, 12..20 empty
         [201 + i for i in range(11)] + [212, 213] + [0] * 7]   # a bench of two


def hex_bytes(path):
    """The initialised data segment as {offset: byte}, '*' rows repeated (the dump's rule)."""
    mem, last_off = {}, None
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if line == "*":
            for i in range(0x20):
                mem[last_off + 0x20 + i] = mem[last_off + i]
            last_off += 0x20
            continue
        m = re.match(r"^([0-9A-F]{4})\s+((?:[0-9A-F]{2} )+)", line)
        if not m:
            continue
        off = int(m.group(1), 16)
        for i, b in enumerate(bytes.fromhex(m.group(2).replace(" ", ""))):
            mem[off + i] = b
        last_off = off
    return mem


class TestDeltaTable(unittest.TestCase):
    def test_table_is_the_image_bytes(self):
        # the table is byte-for-byte DS:0x720..0x762 of the initialised data segment
        # (static/goal-exe/data/ds_2581_01.hex); mutating any single entry fails here
        mem = hex_bytes(ROOT / "static" / "goal-exe" / "data" / "ds_2581_01.hex")
        for i, d in enumerate(R.DELTA_TABLE):
            self.assertEqual(d, mem[0x720 + i] - 0x100 if mem[0x720 + i] >= 0x80 else mem[0x720 + i],
                             f"delta {i} (template {i}) differs from the data segment")
        self.assertEqual(len(R.DELTA_TABLE), 67)          # ids 0..66, the template ids (E004)

    def test_goal_and_own_goal(self):
        # 38 "**** GOAL **** by" +40 and 39 "** OWN GOAL ** by" -50: the task's banked values
        # (F012: the quick goal id 0x26 -> +40, observed 0x2747 + 0x28 = 0x276F)
        self.assertEqual(R.DELTA_TABLE[38], 40)
        self.assertEqual(R.DELTA_TABLE[39], -50)


class TestWords(unittest.TestCase):
    def test_initial_words(self):
        # F2C7: slots 1..11 start at 0x37; every other player keeps the blank 0x7FFF
        r = R.Ratings(TEAMS)
        self.assertEqual(r.word(101), R.START)
        self.assertEqual(r.word(111), R.START)
        self.assertEqual(r.word(212), R.BLANK)             # team 1's bench, slot 12
        self.assertEqual(r.word(212), R.BLANK)
        # and the snapshot mirrors a savestate read of every slot, blank for empty slots
        snap = r.snapshot()
        self.assertEqual(snap[0][:11], [R.START] * 11)
        self.assertEqual(snap[0][11:], [R.BLANK] * 9)

    def test_line_deltas_and_wraparound(self):
        # 1EAB adds s8 deltas with 16-bit wraparound: a word of 10 (a player who began the
        # match unrated, only ever booked) minus SENT OFF's -100 wraps to 0xFF9A, not -90
        r = R.Ratings(TEAMS)
        r.words[101] = 10
        r.apply_line(51, 101)                              # SENT OFF, -100
        self.assertEqual(r.word(101), (10 - 100) & 0xFFFF, "the add is 16-bit with wraparound")
        r.apply_line(38, 102)                              # GOAL, +40
        self.assertEqual(r.word(102), R.START + 40)
        r.apply_line(50, 102)                              # BOOKED, -20
        self.assertEqual(r.word(102), R.START + 20)

    def test_flavour_line_rates_dummy_only(self):
        # 2B0F lines carry p1 = 0: no real player's word moves (1D4A stores 0, E012 notes §2)
        r = R.Ratings(TEAMS)
        before = r.snapshot()
        r.apply_line(63, 0)                                # ---- FULL TIME ----, delta 0
        r.apply_line(66, 0)                                # ** LINESMAN FLAGS **, -10
        self.assertEqual(r.snapshot(), before)

    def test_substitution(self):
        # C5DC: the incoming (p1) takes 0x2747, the squad words swap, the outgoing is
        # eligible for the man of the match from a bench slot (status bit 3)
        r = R.Ratings(TEAMS)
        r.apply_line(38, 205)                              # the outgoing scores first: 0x37 + 40
        r.apply_line(0, 212, 205)                          # 212 on for 205
        self.assertEqual(r.word(212), R.SUB_IN)
        self.assertEqual(r.word(205), R.START + 40)        # the outgoing keeps his word
        self.assertEqual(r.squads[1].index(212), 4)        # the incoming now at slot 5
        self.assertIn(205, r.subbed_off)
        # a later line rating the incoming adds to the flagged word (0x276F: F012's observed)
        r.apply_line(38, 212)
        self.assertEqual(r.word(212), R.SUB_IN + 40)


class TestChallenge(unittest.TestCase):
    """The one ring-invisible writer, 0791:56CB: 5565's +10 to the challenger of a template-65
    "challenge by" line whose invocation ran to its end (DS:8303 set, no bail). A completed
    challenge nets 0 (table −10 + 10); a bailed one keeps the table's −10 — and 5565's bail
    paths are visible in the ring as the FOLLOWING line (539F's 0x0E/0x21 pair, 408E's
    0x16-0x18, 8206's 0x35-0x37, 3FAD(9)'s 0x15), or are silent only when a goalkeeper is the
    holder or the challenger (45d, 4D3F). E012-r0001's first half, positions 294-297, is the
    observed pair: a completed challenge (followed by another player's 0x41) and a bailed one
    (followed by 539F's 0x0E/0x21 pair naming the same player)."""

    def test_completed_challenge_nets_zero(self):
        # 123's line at position 294: followed by 124's 0x41 (a new invocation, not a bail
        # line) -> 56CB fired -> 123's word stays 0x37 (the record's half-time read: 0x8C =
        # 0x37 + the rest of his lines; the plain table gave 0x82, one −10 short)
        r = R.Ratings(TEAMS)
        r.apply_lines([(65, 101, 0), (65, 102, 0)])
        self.assertEqual(r.word(101), R.START, "a completed challenge nets 0, not -10")
        self.assertEqual(r.word(102), R.START, "the follower is judged by its own follower")

    def test_bailed_challenge_keeps_the_table_delta(self):
        # 124's line at position 295: followed by 539F's 0x0E/0x21 pair naming 124 ->
        # 5474's comparison was won, 5565 bailed before 56CB -> the plain -10 stands
        r = R.Ratings(TEAMS)
        r.apply_lines([(65, 101, 0), (14, 101, 0), (33, 101, 0)])
        self.assertEqual(r.word(101), R.START - 10 + 20 + 0, "the bailed challenge keeps -10")

    def test_every_bail_template_stops_the_bonus(self):
        # each of 5565's visible bail lines (CHALLENGE_BAIL) makes the 0x41 line's net -10;
        # any other follower (or none) completes the invocation and nets 0
        for follower in R.CHALLENGE_BAIL:
            r = R.Ratings(TEAMS)
            r.apply_lines([(65, 101, 0), (follower, 101, 0)])
            self.assertEqual(r.word(101) - R.DELTA_TABLE[follower] - R.START, -10,
                             f"follower template {follower} must keep the table's -10")
        for follower in (11, 65, 38, 66, 0):                   # tackle, another challenge, goal...
            r = R.Ratings(TEAMS)
            r.apply_lines([(65, 101, 0), (follower, 102, 0)])
            self.assertEqual(r.word(101), R.START,
                             f"follower template {follower} must complete the challenge")

    def test_last_line_of_a_batch_is_judged_without_a_follower(self):
        # the decision needs the follower, so a trailing 0x41 completes (56CB); a log split
        # at half time must not leave a 0x41 last (none does, in the E012 records)
        r = R.Ratings(TEAMS)
        r.apply_lines([(65, 101, 0)])
        self.assertEqual(r.word(101), R.START)

    def test_the_e012_r0001_record(self):
        # regression: the whole record — its start squads, its line log, its full-time reads
        # and its MoM word. Before the 56CB rule this failed on side 0 slot 3 (predicted
        # 0x00BA, read 0x00C4 at full time; 0x0082 vs 0x008C at half time).
        import json
        d = json.loads((ROOT / "runs" / "E012" / "E012-r0001.json").read_text())
        obs = d["observations"]

        def field(needle):
            return next(o["value"] for o in obs if needle in o.get("field", ""))

        start = json.loads(field("the match's start"))
        full = json.loads(field("full time (the summary screen)"))
        mom = int(field("full time: man of the match").split()[0], 16)
        lines = [(t, p1, p2) for _, t, p1, p2, _ in json.loads(field("line log in ring order"))]
        r = R.Ratings([s["squad"] for s in start]).apply_lines(lines)
        self.assertEqual(r.snapshot(), [s["perf12"] for s in full])
        self.assertEqual(r.man_of_the_match(), mom)

    def test_the_e012_r0002_record(self):
        # regression for the unavailable-partition: two sendings-off and an injury reorder
        # the XIs. Before the rule this failed on every slot from the first removed player's
        # on (the reads are the partitioned order; the plain replay kept the captain-screen
        # order, one slot out from the first removal to the end).
        import json
        d = json.loads((ROOT / "runs" / "E012" / "E012-r0002.json").read_text())
        obs = d["observations"]

        def field(needle):
            return next(o["value"] for o in obs if needle in o.get("field", ""))

        start = json.loads(field("the match's start"))
        half = json.loads(field("half-time team-screen stall"))
        full = json.loads(field("full time (the summary screen)"))
        mom = int(field("full time: man of the match").split()[0], 16)
        n_half = int(field("commentary lines seen at the half-time stall"))
        lines = [(t, p1, p2) for _, t, p1, p2, _ in json.loads(field("line log in ring order"))]
        r = R.Ratings([s["squad"] for s in start])
        r.apply_lines(lines[:n_half])
        self.assertEqual(r.snapshot(), [s["perf12"] for s in half])
        r.apply_lines(lines[n_half:])
        self.assertEqual(r.snapshot(), [s["perf12"] for s in full])
        self.assertEqual(r.man_of_the_match(), mom)


class TestUnavailable(unittest.TestCase):
    """A sending-off (template 51) or injury (template 52) takes the player off the pitch and
    stable-partitions his side's XI: the still-available keep their order, the unavailable move
    to the tail of slots 1..11 in their own relative order; the bench is untouched (0791:7B77 →
    C48D; E012-r0002/r0003, whose side 1 XI ends ...,131,126,130 — the injured 126 then the
    sent-off 130, both in their original relative order). A booking re-orders nothing."""

    def test_one_removal_moves_the_player_to_slot_11(self):
        # side 0 of E012-r0002: 173 sent off from slot 5 -> slot 11, the others shift up
        r = R.Ratings(TEAMS)
        r.apply_line(51, 105)                               # slot 5 SENT OFF
        self.assertEqual(r.squads[0][:12], [101, 102, 103, 104, 106, 107, 108, 109, 110, 111, 105, 0])
        # the bench of team 1 is untouched, and the player keeps his (wrapped) word
        self.assertEqual(r.squads[1], TEAMS[1])
        self.assertEqual(r.word(105), (R.START - 100) & 0xFFFF)

    def test_two_removals_keep_their_original_relative_order(self):
        # side 1 of E012-r0002: 130 sent off first (slot 10), 126 injured later (slot 6);
        # the XI ends with the injured 126 then the sent-off 130 — the ORDER OF EVENTS would
        # give 130, 126, the ORIGINAL relative order gives 126, 130 (the read's order)
        r = R.Ratings(TEAMS)
        r.apply_lines([(51, 210, 0), (52, 206, 0)])
        self.assertEqual(r.squads[1][:13], [201, 202, 203, 204, 205, 207, 208, 209, 211, 206, 210, 212, 213])
        # only the XI is partitioned: slot 12 keeps the bench player 212, slots 13+ untouched

    def test_a_booking_reorders_nothing(self):
        # a booking (template 50) does not take the player off the pitch
        r = R.Ratings(TEAMS)
        r.apply_line(50, 105)
        self.assertEqual(r.squads, [list(t) for t in TEAMS])
        self.assertEqual(r.word(105), R.START - 20)

    def test_off_pitch_player_is_still_scanned_for_the_man_of_the_match(self):
        # the partition keeps the unavailable inside slots 1..11, which CAB0 always scans:
        # a sent-off player who scored enough still wins it
        r = R.Ratings(TEAMS)
        r.apply_lines([(38, 201, 0)] * 5 + [(51, 201, 0)])
        self.assertEqual(r.word(201), R.START + 5 * 40 - 100)   # 155
        self.assertEqual(r.man_of_the_match(), 201)


class TestDecode(unittest.TestCase):
    def test_bucket_rule(self):
        # 1771:3855/0791:CB2E: the flag is stripped only when the SIGNED word is above 5000
        # (0x1388); 5000 itself stays, 5001 loses 0x2710. This is the readers' bucket rule,
        # taken from the listing, never from the displayed string (T19's lesson).
        self.assertEqual(R.decode(5000), 5000)
        self.assertEqual(R.decode(5001), -4999)           # a plain threshold, not mod 10000
        self.assertEqual(R.decode(R.SUB_IN), R.START)      # 10055 -> 55
        self.assertEqual(R.decode(R.SUB_IN + 40), R.START + 40)
        self.assertEqual(R.decode(0xFFD3), -45)            # a raw negative word: no flag
        self.assertEqual(R.decode(R.BLANK), 0x7FFF - 0x2710)   # blank is above 5000: flagged


class TestManOfTheMatch(unittest.TestCase):
    def test_max_scan_and_tie_order(self):
        # CAB0: strict compare, best starts at 1; ties keep the first in scan order
        # (side 0, lower slot). 0x37 decodes to 55 everywhere, so with nobody rated the
        # side 0 slot 1 player wins the tie.
        r = R.Ratings(TEAMS)
        self.assertEqual(r.man_of_the_match(), 101)
        # one goal on side 1 beats every starter: 55 + 40 = 95
        r.apply_line(38, 201)
        self.assertEqual(r.man_of_the_match(), 201)
        # an equal word on side 0 takes it back: the scan is stateless, team 0 scans first
        # and the strict compare keeps the FIRST equal maximum in scan order
        r.apply_line(38, 101)
        self.assertEqual(r.man_of_the_match(), 101)
        # a higher word on side 0 does
        r.apply_line(38, 102)
        r.apply_line(12, 102)                              # a goal and "dodged by" +20: 115
        self.assertEqual(r.man_of_the_match(), 102)

    def test_bench_and_blank_eligibility(self):
        # CAB0 scans slots 12..20 only for players substituted off (status bit 3): a bench
        # player is skipped even when the table of words says he was rated, and 0x7FFF is
        # always skipped.
        r = R.Ratings(TEAMS)
        r.words[212] = 0x100                                # a bench word someone wrote
        self.assertEqual(r.man_of_the_match(), 101)         # 0x100 > 55 but not scanned
        r.subbed_off.add(212)
        self.assertEqual(r.man_of_the_match(), 212)         # now eligible, 0x100 wins
        r2 = R.Ratings(TEAMS)
        r2.subbed_off.add(213)
        self.assertEqual(r2.man_of_the_match(), 101)        # 0x7FFF skipped

    def test_substituted_players_scanned(self):
        # after a real substitution line the incoming (flagged word, in slots 1..11) and the
        # outgoing (bit 3, in a bench slot) are both scanned; the outgoing's 55 + 40 beats
        # every starter's 55 and the incoming's flagged 55
        r = R.Ratings(TEAMS)
        r.apply_line(38, 205)
        r.apply_line(0, 212, 205)
        self.assertEqual(r.man_of_the_match(), 205)

    def test_blank_squad_slot(self):
        # a squad word of 0 (an empty slot) is not a player: no word, no crash, never the man
        # of the match
        r = R.Ratings(TEAMS)
        self.assertEqual(r.word(0), R.BLANK)
        self.assertEqual(r.man_of_the_match(), 101)


if __name__ == "__main__":
    unittest.main(verbosity=2)
