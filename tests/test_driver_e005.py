"""E005's runner, summary and probe wrapper (T12, experiments/E005-q003-cycles/): the cycles setting, the
delay count DS:A9FF, the timing reads, the record checks and the halves, with fakes in place of DOSBox-X."""
import argparse
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
E005 = ROOT / "experiments" / "E005-q003-cycles"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


e005 = _load("e005_run", E005 / "run.py")
summ = _load("e005_summarise", E005 / "summarise.py")
pf = _load("e005_probe_f001", E005 / "probe_f001.py")

DS_BASE = 0x2DA40


class FakeState:
    """ds_bytes, ticks and program over one bytearray, as savestate.Savestate offers them."""

    def __init__(self, ticks=0):
        self.mem = bytearray(0x40000)
        self._ticks = ticks

    def ds_bytes(self, off, n):
        return bytes(self.mem[DS_BASE + off:DS_BASE + off + n])

    def put_ds(self, off, b):
        self.mem[DS_BASE + off:DS_BASE + off + len(b)] = b

    def ticks(self):
        return self._ticks, self._ticks.to_bytes(4, "little")

    def program(self):
        return mock.Mock(ds_base=DS_BASE)


def _screen():
    import savestate
    rows = [" " * 80 for _ in range(25)]
    for r, text in ((1, "a"), (2, "---- HALF TIME ----"), (3, "c")):
        rows[r] = (" " * 31 + text).ljust(80)
    return savestate.Screen("".join(rows).encode("cp437"), bytes([7] * 2000))


SCREEN = _screen()


def state_with_count(count, ticks=0):
    st = FakeState(ticks)
    st.put_ds(0xA9FD, b"\xee\xee")          # DS:A9FD (the year), just below
    st.put_ds(0xA9FF, count.to_bytes(4, "little"))   # 214B:1DA7: `mov [0xa9ff], ax` / `mov [0xaa01], dx`
    st.put_ds(0xAA03, b"\xdd\xdd")          # just above
    return st


class DelayCountTest(unittest.TestCase):
    def test_reads_the_dword_low_word_at_a9ff_high_word_at_aa01(self):
        # seg_214B_04.asm:69-70 store ax at A9FF and dx at AA01; a high word of 1 must be read
        self.assertEqual(e005.a9ff(state_with_count(0x000110B3)), 0x000110B3)
        self.assertEqual(e005.a9ff(state_with_count(0x10B3)), 0x10B3)

    def test_observations_carry_the_count_and_the_ticks(self):
        st = state_with_count(0x2C5, ticks=0x000A1234)
        o = e005.a9ff_observation(3, "full time", st)
        self.assertTrue(o["value"].startswith("0x000002c5 (c5 02 00 00)"))
        st.screen = lambda: SCREEN
        st.ds_word = lambda off: {0x7B62: 0xF3AB}[off]
        with mock.patch.object(e005.commentary, "Snapshot", return_value=mock.Mock(counter=0x2A, score=(1, 2))):
            row = e005.read_row(4, {"utc": "2026-10-04T19:00:00.000Z"}, 1.25, st)
        self.assertEqual(row, [4, "2026-10-04T19:00:00.000Z", 1.25, "0x000a1234", "0x000002c5", SCREEN.digest(),
                               "0x002a", "0xf3ab", 1, 2, "a / ---- HALF TIME ---- / c"])
        t = e005.reads_observation([row, [5, "u", 2.5, "0x000a1240", "0x000002c5", "d", "0x002b", "0xf3ab", 1, 2, "x"]], 9)
        self.assertTrue(t["field"].startswith("match reads, one list per read: [step, host UTC time"))
        # summarise reads them back, in order: (since, ticks, count, rows)
        self.assertEqual(summ.reads({"observations": [t]}), [(1.25, 0x000A1234, 0x2C5, "a / ---- HALF TIME ---- / c"),
                                                             (2.5, 0x000A1240, 0x2C5, "x")])

    def test_the_savestate_lines_of_dosbox_out_are_counted_not_kept(self):
        out = ("LOG: Loading state from slot: 1\nLOG: File : <work>/IntTimer10 is 161 bytes\nLOG: [19:26:25]: Saved. (Slot 1)\n"
               "LOG: File : <work>/IntTimer10 is 161 bytes\nLOG: [19:26:26]: Saved. (Slot 1)\nLOG: Save_Remark x\nLOG: Time_Stamp y\n"
               "LOG: unrelated\nLOG: Save state corrupted! Memory_Size\n")
        self.assertEqual(e005.dosbox_lines(out), (["LOG: Loading state from slot: 1", "LOG: Save state corrupted! Memory_Size"], [2, 2]))


class ClockTest(unittest.TestCase):
    def test_since_counts_from_the_first_call(self):
        times = iter([10.0, 10.5, 12.0, 13.25])
        c = e005.Clock(lambda: next(times))
        self.assertIsNone(c.since())
        self.assertEqual(c(), 10.0)          # match.play: t0 = clock(), just before the burst
        self.assertEqual(c(), 10.5)
        self.assertEqual(c.since(), 2.0)
        self.assertEqual(c.since(), 3.25)


class EmulatorsTest(unittest.TestCase):
    def test_lists_other_dosbox_and_xvfb_only(self):
        ps = "  10   500 Xvfb\n  11   500 dosbox-x\n  12    20 dosbox-x\n  13   20 bash\n  14  7 Xvfb\n"
        with mock.patch.object(e005.subprocess, "run", return_value=mock.Mock(stdout=ps)):
            self.assertEqual(e005.emulators(own={12, 14}), [[10, 500, "Xvfb"], [11, 500, "dosbox-x"]])


class StartState:
    name = "e004-1001"
    config = {"cycles": "30000", "dos_time": "10:01:00", "dos_date": "10/04/2026"}


class RunTest(unittest.TestCase):
    args = argparse.Namespace(batch="t")

    def test_refuses_a_cycles_setting_outside_the_task(self):
        for c in ("20000", "auto", "", "MAX"):
            with self.assertRaises(ValueError, msg=c):
                e005.Run("restores", "quick", 1, self.args, "abc", c, StartState())

    def test_fresh_launch_sets_the_states_clock_and_the_restore_does_not(self):
        f = e005.Run("fresh", "quick", 1, self.args, "abc", "5000", StartState(), slot=2)
        self.assertEqual((f.d.config["cycles"], f.d.config["dos_time"], f.d.config["dos_date"]), ("5000", "10:01:00", "10/04/2026"))
        r = e005.Run("restores", "watched", 2, self.args, "abc", "max", StartState())
        self.assertEqual(r.d.config["cycles"], "max")
        self.assertNotIn("dos_time", r.d.config)
        self.assertIsNone(r.dos_time)

    def test_the_match_gets_e005s_bound_and_the_runs_clock(self):
        r = e005.Run("restores", "watched", 1, self.args, "abc", "5000", StartState())
        r.d = mock.MagicMock()
        r.add_full = lambda *a: None
        seen = {}

        def play(d, arm, on_read, **kw):
            seen.update(kw, arm=arm)
            return [], 1, 1.0
        with mock.patch.object(e005.e004, "at_captain", return_value=True), mock.patch.object(e005.match, "play", play), \
                mock.patch.object(e005, "emulators", return_value=[]), mock.patch.object(r, "record", return_value=True):
            r.go()
        self.assertEqual(seen["timeout"], 2700)
        self.assertIs(seen["clock"], r.clock)
        self.assertIs(seen["keys"], r.keys)
        self.assertEqual(seen["arm"], "watched")

    def test_each_read_is_one_row_of_one_observation(self):
        r = e005.Run("restores", "watched", 1, self.args, "abc", "5000", StartState())
        r.tracker = mock.Mock()
        with mock.patch.object(e005, "read_row", side_effect=lambda step, times, since, state: [step]), \
                mock.patch.object(e005.commentary, "Snapshot"):
            r.on_read("match read 1", {"utc": "u"}, object())
            r.on_read("match read 2", {"utc": "u"}, object())
        self.assertEqual(r.read_rows, [[1], [2]])
        self.assertEqual(r.obs, [])          # no observation per read (amendment 2)
        self.assertEqual(r.reads, 2)

    def test_arm_names_route_state_and_cycles(self):
        self.assertEqual(e005.arm_name("quick", "restores", "e004-1001", "5000"), "quick-restore-e004-1001-cycles-5000")
        self.assertEqual(e005.arm_name("watched", "fresh", "e004-1337", "max"), "watched-fresh-e004-1337-cycles-max")

    def test_load_state_refuses_a_state_made_at_another_setting(self):
        bad = mock.Mock(config={"cycles": "max"})
        with mock.patch.object(e005.e004, "load_state", return_value=bad), self.assertRaises(SystemExit):
            e005.load_state("e004-1001")
        good = mock.Mock(config={"cycles": "30000"})
        with mock.patch.object(e005.e004, "load_state", return_value=good):
            self.assertIs(e005.load_state("e004-1001"), good)


def record(cycles="30000", arm=None, conf_cycles=None, fp=None, clock=False, i3=None, named=True):
    conf = f"[cpu]\ncycles={conf_cycles or cycles}\n[autoexec]\nmount c <game>\nc:\n"
    if clock:
        conf += "date 10/04/2026\ntime 10:01:00\n"
    conf += "mount d <work>/dosclock\ndate /t > d:\\clock.txt\ntime /t >> d:\\clock.txt\nc:\ngoal\n"
    obs = [{"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf}]
    if named:
        obs.append(e005.cycles_observation(cycles))
    inter = [{"level": "I1", "what": "x"}] + ([{"level": "I3", "what": "x"}] if (clock if i3 is None else i3) else [])
    return {"run_id": "E005-r9999", "arm": arm or e005.arm_name("quick", "restores", "e004-1001", cycles),
            "runtime": {"fingerprint": {"cycles": fp or cycles}}, "interventions": inter, "observations": obs}


class CheckTest(unittest.TestCase):
    def test_a_record_naming_its_cycles_passes(self):
        for c in ("5000", "30000", "max"):
            self.assertEqual(summ.check(record(c)), [], c)
        self.assertEqual(summ.check(record("5000", clock=True)), [])

    def test_a_record_not_naming_its_cycles_fails(self):
        self.assertIn("no observation names", summ.check(record(named=False))[0])

    def test_named_cycles_must_agree_with_the_config_fingerprint_and_arm(self):
        self.assertTrue(summ.check(record("5000", conf_cycles="max")))
        self.assertTrue(summ.check(record("5000", fp="30000")))
        self.assertTrue(summ.check(record("5000", arm="quick-restore-e004-1001-cycles-30000")))

    def test_setting_the_clock_without_i3_fails(self):
        self.assertIn("no I3", summ.check(record(clock=True, i3=False))[0])

    def test_reading_the_clock_back_is_not_setting_it(self):
        self.assertFalse(summ.config_sets_clock(record()))
        self.assertTrue(summ.config_sets_clock(record(clock=True)))
        self.assertEqual(summ.check(record(clock=False, i3=False)), [])


def match_record(reads, keys, ko_ticks):
    """Match reads as run.py writes them: per read a commentary-rows and a timing observation."""
    obs = [{"step": 0, "source": "memory", "field": "restored: 4 bytes at 0040:006C (BIOS timer tick count), as a dword", "value": f"0x{ko_ticks:08x} (..)"}]
    for i, (since, ticks, rows) in enumerate(reads, 1):
        obs.append({"step": i, "source": "ui-text", "field": f"match read {i}: commentary rows (rows 1-3, columns 31-66)", "value": rows})
        obs.append({"step": i, "source": "memory", "field": f"match read {i}: host seconds since the starting burst (monotonic, the clock match.play measures with, taken after the savestate was read), BIOS tick count 0040:006C, dword DS:A9FF", "value": f"{since} 0x{ticks:08x} 0x000010b3"})
    rec = {"observations": obs}
    return {"reads": summ.reads(rec), "keys": keys, "ticks_ko": summ.ticks_of(rec, "restored")}


class HalvesTest(unittest.TestCase):
    KEYS = [[0.0, "Enter", "starting burst, no poll between"], [10.0, "Enter", "hit any key"], [11.0, "Enter", "team screen"]]

    def test_host_and_guest_seconds_of_each_half(self):
        t = summ.TICKS_PER_S
        r = match_record([(2.0, 100 + round(1 * t), "a / b / c"), (9.0, 100 + round(30 * t), "b / ---- HALF TIME ---- / x"),
                          (10.5, 100 + round(32 * t), "hit"), (12.0, 100 + round(34 * t), "kick off"),
                          (30.0, 100 + round(64 * t), "y / z / ---- FULL TIME ----")], self.KEYS, 100)
        h = summ.halves(r)
        self.assertEqual((h["host_first"], h["host_ht_to_ft"], h["host_second"]), (9.0, 21.0, 19.0))
        # the second half from the first read after the team-screen Enter (34 s), not from HALF TIME (30 s)
        self.assertAlmostEqual(h["guest_first"], 30.0, delta=0.05)
        self.assertAlmostEqual(h["guest_second"], 30.0, delta=0.05)
        self.assertEqual(h["ratio"], round(9.0 / 19.0, 3))

    def test_the_compact_form_gives_the_same_halves(self):
        t = summ.TICKS_PER_S
        reads = [(9.0, 100 + round(30 * t), "b / ---- HALF TIME ---- / x"), (12.0, 100 + round(34 * t), "kick off"),
                 (30.0, 100 + round(64 * t), "y / z / ---- FULL TIME ----")]
        obs = [{"step": 0, "field": "restored: 4 bytes at 0040:006C (BIOS timer tick count)", "value": "0x00000064 (..)"}]
        # amendment 1's form: one observation per read, its field as the records of that form carry it
        legend = ("[host UTC time, host s since the starting burst, BIOS ticks 0040:006C, dword DS:A9FF, screen sha256, "
                  "DS:80EE, DS:7B62, score DS:9B3C, score DS:9B3D, commentary rows 1-3]")
        obs += [{"step": i, "field": f"match read {i}: {legend}", "value": json.dumps(["u", s, f"0x{k:08x}", "0x10b3", "d", "0x1", "0x2", 0, 0, rows])}
                for i, (s, k, rows) in enumerate(reads, 1)]
        rec = {"observations": obs}
        h = summ.halves({"reads": summ.reads(rec), "keys": self.KEYS, "ticks_ko": summ.ticks_of(rec, "restored")})
        self.assertEqual((h["host_first"], h["host_second"]), (9.0, 19.0))
        self.assertAlmostEqual(h["guest_second"], 30.0, delta=0.05)

    def test_no_halves_without_half_time(self):
        r = match_record([(2.0, 110, "a"), (30.0, 900, "---- FULL TIME ----")], self.KEYS, 100)
        self.assertIsNone(summ.halves(r))

    def test_the_verdict_on_f001s_unequal_halves(self):
        self.assertIn(": reproduced, in 2 of 2", summ.reproduced([0.1, 0.49]))
        self.assertIn("not reproduced, in 0 of 2", summ.reproduced([0.5, 0.95]))
        self.assertIn("reproduced in part, in 1 of 2", summ.reproduced([0.1, 0.95]))
        self.assertIn("no completed watched run", summ.reproduced([]))


class IdentityTest(unittest.TestCase):
    def test_reference_is_the_first_30000_restore_of_the_same_state_and_arm(self):
        mk = lambda i, kind, st, arm, c: {"id": i, "kind": kind, "status": "completed", "state": st, "arm": arm, "cycles": c}  # noqa: E731
        runs = [mk("r1", "restores", "s1", "quick", "5000"), mk("r2", "fresh", "s1", "quick", "30000"),
                mk("r3", "restores", "s2", "quick", "30000"), mk("r4", "restores", "s1", "watched", "30000"),
                mk("r5", "restores", "s1", "quick", "30000"), mk("r6", "restores", "s1", "quick", "30000")]
        self.assertEqual(summ.reference(runs, runs[0])["id"], "r5")
        self.assertEqual(summ.reference(runs, runs[3])["id"], "r4")

    def test_identical_needs_score_events_seed_counter_and_every_line(self):
        a = {"id": "a", "score": ("A", 1, "B", 0), "events": [["goal", 0, "x"]], "seed": "0x1", "counter": "0x0001",
             "lines": [[1, 38, 0, "x"]], "gaps": [], "deltas": [1]}
        self.assertEqual(summ.compare(dict(a, id="b"), a), (summ.NO_DIFFERENCE, ""))
        # the events are the lines of certain templates (commentary.Tracker.events), so a line decides them too
        for k, v in (("score", ("A", 1, "B", 1)), ("seed", "0x2"), ("counter", "0x0002"), ("lines", [[1, 38, 0, "y"]])):
            self.assertEqual(summ.compare(dict(a, id="b", **{k: v}), a)[0], "DIFFERS", k)


ctest = _load("e005_commentary_fixture", ROOT / "tests" / "test_driver_commentary.py")


def tracked(snapshots):
    """A run's commentary as summarise.load gives it, from the real Tracker fed successive snapshots."""
    t = e005.commentary.Tracker()
    for k, st in enumerate(snapshots, 1):
        t.add(e005.commentary.Snapshot(st), f"match read {k}")
    return {"lines": [[x["n"], x["template"], x["team"], x["text"]] for x in t.lines], "gaps": t.gaps, "deltas": t.deltas}


class RecordIntegrityTest(unittest.TestCase):
    """Review R3: the runner never writes a host path, never replaces a record, and refuses to run on
    uncommitted sources."""
    REC = {"run_id": "E005-r9999", "arm": "quick-restore-e004-1001-cycles-5000", "status": "completed", "x": "<work>"}

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "runs"
        self.addCleanup(self.tmp.cleanup)

    def test_a_record_holding_a_host_path_is_refused_unwritten(self):
        leaked = dict(self.REC, x=f"conf at {e005.ROOT}/scratch/driver")
        with mock.patch.object(e005, "OUT", self.out), self.assertRaises(SystemExit) as cm:
            e005.write_record(leaked)
        self.assertIn("host path", str(cm.exception))
        self.assertFalse((self.out / "E005-r9999.json").exists())

    def test_a_record_is_never_replaced(self):
        with mock.patch.object(e005, "OUT", self.out):
            self.assertTrue(e005.write_record(self.REC))
            first = (self.out / "E005-r9999.json").read_text()
            with self.assertRaises(FileExistsError):
                e005.write_record(dict(self.REC, status="aborted: second"))
        self.assertEqual((self.out / "E005-r9999.json").read_text(), first)
        self.assertEqual(json.loads(first)["status"], "completed")

    def test_uncommitted_sources_stop_the_runner_before_any_run(self):
        def git(*a):
            return " M experiments/E005-q003-cycles/run.py" if a[0] == "status" else "abc1234"
        for kind in (["calibrate", "--cycles", "5000"], ["restores", "--cycles", "5000", "--state", "e004-1001"],
                     ["fresh", "--cycles", "max", "--state", "e004-1337"]):
            with mock.patch.object(e005, "git", side_effect=git) as g, mock.patch.object(e005, "calibrate") as cal, \
                    mock.patch.object(e005, "Run") as run, mock.patch.object(e005, "load_state") as ls, \
                    self.assertRaises(SystemExit) as cm:
                e005.main(kind)
            self.assertIn("uncommitted changes", str(cm.exception), kind)
            self.assertEqual(g.call_args_list[0].args[:2], ("status", "--porcelain"))
            for m in (cal, run, ls):
                m.assert_not_called()

    def test_a_clean_tree_runs(self):
        with mock.patch.object(e005, "git", side_effect=lambda *a: "" if a[0] == "status" else "abc1234"), \
                mock.patch.object(e005, "calibrate", return_value=True) as cal, mock.patch.object(e005, "reserve_id", return_value=7):
            self.assertEqual(e005.main(["calibrate", "--cycles", "5000", "--reps", "2"]), 0)
        self.assertEqual(cal.call_count, 2)


def run_of(lines, gaps=(), deltas=None, **kw):
    r = {"id": "run", "score": ("S", 2, "D", 3), "events": [], "seed": "0xa621", "counter": "0x0005",
         "lines": [list(x) for x in lines], "gaps": list(gaps), "deltas": deltas or [len(lines) + len(gaps)]}
    r.update(kw)
    return r


LINES = [[i, 2, 0, f"line {i}"] for i in range(1, 6)]


class VerdictPathsTest(unittest.TestCase):
    """Review rounds 1-4: no verdict claims more than was observed; a line a flag marks unread makes the pair
    undetermined; a flag stands for the
    one occurrence it names; what both sides read and differs makes DIFFERS. Every path of `compare`,
    `identity` and the verdict counts."""
    BASE = {"score": ("S", 2, "D", 3), "events": [], "seed": "0xa621", "counter": "0x0005"}
    ALL = {1: (2, 5, 0, 0), 2: (2, 6, 0, 1), 3: (2, 7, 0, 0), 4: (2, 5, 0, 0), 5: (2, 6, 0, 1)}

    def missed_3(self):
        """A run whose reader's last read saw record 3 still unwritten (0xFF), so the line stayed unread:
        built through the real Tracker, which since it stops at an unwritten record makes a flagged
        record unread only when no later read exists."""
        first = dict(self.ALL)
        first[3] = (0xFF, 0, 0, 0)
        return tracked([ctest.make_state(5, first)])

    def test_both_sides_missed_the_same_line_is_never_identical(self):
        # Sol's round-2 case: both readers' last read saw record 3 still unwritten, so neither side's
        # lines can be placed against the match's occurrences and the pair is never identical.
        ref = dict(self.BASE, id="ref", **self.missed_3())
        run = dict(self.BASE, id="run", **self.missed_3())
        self.assertEqual(run["lines"], ref["lines"])
        self.assertEqual(summ.compare(run, ref)[0], "IDENTITY UNDETERMINED")
        v = summ.identity(run, ref)
        self.assertTrue(v.startswith("IDENTITY UNDETERMINED"), v)
        self.assertIn("the run's reader has lines it cannot locate", v)
        self.assertIn("the reference's reader has lines it cannot locate", v)

    def test_a_line_the_run_never_read_is_undetermined_whatever_it_held(self):
        # Sol's round-1 case: the reference is complete, the run's reader never read record 3.
        ref = dict(self.BASE, id="ref", **tracked([ctest.make_state(5, self.ALL)]))
        run = dict(self.BASE, id="run", **self.missed_3())
        self.assertEqual(run["gaps"], ["match read 1: record 3 is the end marker 0xFF (pending)"])
        self.assertEqual(summ.compare(run, ref)[0], "IDENTITY UNDETERMINED")

    def test_an_incomplete_reference_makes_a_complete_run_undetermined(self):
        ref = dict(self.BASE, id="ref", **self.missed_3())
        run = dict(self.BASE, id="run", **tracked([ctest.make_state(5, self.ALL)]))
        v = summ.identity(run, ref)
        self.assertTrue(v.startswith("IDENTITY UNDETERMINED"), v)
        self.assertIn("the reference's reader has lines it cannot locate", v)
        self.assertEqual(summ.identity(ref, ref), "reference, with unread lines: match read 1: record 3 is the end marker 0xFF (pending)")

    def test_what_both_read_and_differs_makes_differs_even_when_incomplete(self):
        ref = run_of(LINES)
        run = run_of([LINES[0], LINES[1], LINES[3], [5, 2, 0, "other"]], gaps=["match read 1: record 3 is the end marker 0xFF"])
        self.assertEqual(summ.compare(run, ref), ("DIFFERS", "occurrence 5 of the match (1 occurrence(s) seen by both differ)"))

    def test_the_occurrence_is_the_flagged_reads_not_any_with_that_record_number(self):
        # 205 lines: record 3 occurs twice (occurrences 3 and 203). The flag of read 2 names occurrence 203.
        lines = [[(i - 1) % 200 + 1, 2, 0, f"line {i}"] for i in range(1, 206)]
        ref = run_of(lines, deltas=[200, 5])
        flag = ["match read 2: record 3 is the end marker 0xFF"]
        run = run_of([x for i, x in enumerate(lines, 1) if i != 203], gaps=flag, deltas=[200, 5])
        self.assertEqual(summ.unread_occurrences(run), [203])
        self.assertEqual(summ.compare(run, ref)[0], "IDENTITY UNDETERMINED")
        other = dict(run, lines=[x for i, x in enumerate(lines, 1) if i != 3])          # the other occurrence of record 3
        self.assertEqual(summ.compare(other, ref)[0], "DIFFERS")
        both = dict(run, lines=[x for i, x in enumerate(lines, 1) if i not in (3, 203)])  # one flag, two losses
        self.assertEqual(summ.compare(both, ref)[0], "IDENTITY UNDETERMINED")             # the losses do not fit: unlocatable
        self.assertNotEqual(summ.compare(both, ref)[0], summ.NO_DIFFERENCE)

    def test_memory_read_at_full_time_differs_whatever_the_lines(self):
        ref = run_of(LINES)
        for k, v in (("counter", "0x0004"), ("seed", "0x0001"), ("score", ("S", 2, "D", 2))):
            run = run_of(LINES[:2] + LINES[3:], gaps=["match read 1: record 3 is the end marker 0xFF"], **{k: v})
            self.assertEqual(summ.compare(run, ref)[0], "DIFFERS", k)

    def test_unlocatable_losses_are_undetermined(self):
        ref = run_of(LINES)
        wrong = run_of(LINES[:2] + LINES[3:], gaps=["match read 1: record 4 is the end marker 0xFF"], deltas=[5])
        self.assertEqual(summ.compare(wrong, ref)[0], "DIFFERS")    # its flag puts line 4 at occurrence 3, where the reference read line 3
        for gaps in (["match read 1: record 9 is the end marker 0xFF"],               # outside its read's range
                     ["match read 1: record 3 is the end marker 0xFF"] * 2,           # one occurrence, two flags
                     ["match read 1: something else"]):
            run = run_of(LINES[:2] + LINES[3:], gaps=gaps, deltas=[5])
            self.assertEqual(summ.compare(run, ref)[0], "IDENTITY UNDETERMINED", gaps)
        short = run_of(LINES[:4], deltas=[5])                                            # no flag, one line fewer than counted
        self.assertIsNone(summ.located(short))
        self.assertEqual(summ.compare(short, ref)[0], "IDENTITY UNDETERMINED")

    def test_a_stride_flag_is_reported_and_does_not_decide(self):
        stride = ["match read 1: counter 0 -> 150 (150 lines)"]
        lines = [[(i - 1) % 200 + 1, 2, 0, f"line {i}"] for i in range(1, 151)]
        ref = run_of(lines, deltas=[60, 90])
        run = run_of(lines, gaps=stride, deltas=[150])
        self.assertEqual(summ.compare(run, ref), (summ.NO_DIFFERENCE, ""))
        self.assertEqual(summ.identity(run, ref), "no observed difference from run (1 stride flag(s) reported)")
        self.assertEqual(summ.compare(run, dict(run, id="ref2"))[0], summ.NO_DIFFERENCE)              # both sides strided
        self.assertEqual(summ.identity(dict(ref, id="plain"), dict(run, id="strided")),
                         "no observed difference from strided (1 stride flag(s) reported)")             # the reference's flag is reported too
        shorter = run_of(lines[:-1], gaps=stride, deltas=[149])                                         # one line fewer counted
        self.assertEqual(summ.compare(shorter, ref), ("DIFFERS", "lines counted 149 against 150"))
        self.assertEqual(summ.unread_occurrences(run), [])

    def ring_run(self, writes, reads_after):
        """The commentary of a run as the real Tracker reads it from a simulated ring of 200 records:
        `writes` in order, each into the next record (1 … 200, then 1 again), the record after the newest
        holding the end marker 0xFF, and a snapshot after each count of writes in `reads_after`."""
        snaps = []
        for w in reads_after:
            recs = {(k - 1) % 200 + 1: writes[k - 1] for k in range(1, w + 1)}
            recs[w % 200 + 1] = (0xFF, 0, 0, 0)
            snaps.append(ctest.make_state(w % 200, recs))
        return dict(self.BASE, counter=f"0x{reads_after[-1] % 200:04x}", **tracked(snaps))

    def test_sols_hidden_laps_get_no_claim_of_completeness(self):
        # Review round 3: a lap of the 200-record ring between two reads leaves no trace in the reads. Both
        # runs below wrote 200 lines more than the reference, all different and never seen. Under round 4's
        # wording they get "no observed difference": true of what was seen, and it claims nothing more. No
        # verdict says identical or complete, which is what would have been false.
        same = [(2, 5 + i % 3, 0, i % 2) for i in range(150)]          # the reference's 150 lines
        hidden = [(50, 5 + i % 3, 0, 1) for i in range(200)]            # 200 other lines (bookings)
        ref = dict(self.ring_run(same, [60, 150]), id="ref")
        self.assertEqual((ref["deltas"], ref["gaps"]), ([60, 90], []))
        # R1: 350 writes, the first 200 hidden, read once: a stride flag, 150 lines seen, all equal
        r1 = dict(self.ring_run(hidden + same, [350]), id="r1")
        self.assertEqual((r1["deltas"], r1["gaps"]), ([150], ["match read 1: counter 0 -> 150 (150 lines)"]))
        # R2: 60 lines, 200 hidden, 90 lines, read after 60, 260 and 350: a delta of 0 and no flag at all
        r2 = dict(self.ring_run(same[:60] + hidden + same[60:], [60, 260, 350]), id="r2")
        self.assertEqual((r2["deltas"], r2["gaps"]), ([60, 0, 90], []))
        for run in (r1, r2):
            self.assertEqual(run["lines"], ref["lines"])
            self.assertEqual(summ.compare(run, ref), (summ.NO_DIFFERENCE, ""))
            v = summ.identity(run, ref)
            self.assertTrue(v.startswith("no observed difference from ref"), v)
            for word in ("identical", "complete"):
                self.assertNotIn(word, v.lower())
        self.assertEqual(summ.verdict_counts([summ.identity(r1, ref), summ.identity(r2, ref)])[summ.NO_DIFFERENCE], 2)
        self.assertFalse(hasattr(summ, "complete") or hasattr(summ, "complete_against"))

    def test_more_lines_written_is_differs_even_with_a_side_incomplete(self):
        ref = run_of(LINES)                                                         # 5 lines, complete
        run = run_of(LINES, gaps=["match read 1: record 6 is the end marker 0xFF"], deltas=[6])   # 6 written, the 6th unread
        self.assertEqual(summ.compare(run, ref), ("DIFFERS", "lines counted 6 against 5"))

    def test_a_stride_flag_beside_an_unknown_flag_is_undetermined(self):
        lines = [[i, 2, 0, f"line {i}"] for i in range(1, 151)]
        ref = run_of(lines, deltas=[60, 90])
        run = run_of(lines, gaps=["match read 1: counter 0 -> 150 (150 lines)", "match read 1: something else"], deltas=[150])
        self.assertIsNone(summ.located(run))                                       # the unknown flag cannot be located
        self.assertEqual(summ.compare(run, ref)[0], "IDENTITY UNDETERMINED")

    def test_a_reference_with_only_stride_flags_has_no_unread_lines(self):
        lines = [[i, 2, 0, f"line {i}"] for i in range(1, 151)]
        ref = run_of(lines, gaps=["match read 1: counter 0 -> 150 (150 lines)"], deltas=[150])
        self.assertEqual(summ.identity(ref, ref), "reference")
        unknown = dict(ref, gaps=["match read 1: something else"])
        self.assertEqual(summ.identity(unknown, unknown), "reference, with unread lines: match read 1: something else")

    def test_unread_occurrences(self):
        r = {"gaps": ["match read 2: record 7 is the end marker 0xFF"], "deltas": [5, 3]}       # read 2 covers records 6-8
        self.assertEqual(summ.unread_occurrences(r), [7])
        for gaps in (["match read 2: record 9 is the end marker 0xFF"],                         # outside read 2's range
                     ["match read 3: record 7 is the end marker 0xFF"],                         # no read 3
                     ["match read 2: record 7 is the end marker 0xFF"] * 2,                     # one occurrence, two flags
                     ["match read 2: something else"]):                                         # a flag of unknown kind
            self.assertIsNone(summ.unread_occurrences(dict(r, gaps=gaps)), gaps)
        self.assertEqual(summ.unread_occurrences(dict(r, gaps=r["gaps"] + ["match read 1: counter 0 -> 150 (150 lines)"])), [7])

    def test_unequal_totals_differ_even_when_losses_cannot_be_located(self):
        # review round 4, R1: the totals are compared before any placement
        run = run_of(LINES, gaps=["match read 1: something else"], deltas=[205])
        self.assertIsNone(summ.located(run))
        self.assertEqual(summ.compare(run, run_of(LINES)), ("DIFFERS", "lines counted 205 against 5"))

    def test_an_undetermined_verdict_claims_line_equality_only_when_lines_were_compared(self):
        # review round 4, R2: one line each, "x" against "y"; the run's flag cannot be located, so no line was compared
        ref = run_of([[1, 2, 0, "y"]], id="ref")
        run = run_of([[1, 2, 0, "x"]], gaps=["match read 1: something else"], deltas=[1])
        v = summ.identity(run, ref)
        self.assertTrue(v.startswith("IDENTITY UNDETERMINED"), v)
        self.assertIn("the lines could not be compared; the score, DS:7B62 and DS:80EE at full time", v)
        self.assertNotIn("every occurrence both saw", v)
        located_ = run_of(LINES[:2] + LINES[3:], gaps=["match read 1: record 3 is the end marker 0xFF"])
        self.assertIn("every occurrence both saw", summ.identity(located_, dict(run_of(LINES), id="ref")))

    def test_verdict_counts(self):
        ref = dict(run_of(LINES), id="ref", kind="restores", status="completed", state="s", arm="watched", cycles="30000")
        same = dict(ref, id="r2", cycles="5000")
        undet = dict(same, id="r3", lines=LINES[:2] + LINES[3:], gaps=["match read 1: record 3 is the end marker 0xFF"])
        diff = dict(same, id="r4", seed="0x0000")
        verdicts = [summ.identity(r, summ.reference([ref, same, undet, diff], r)) for r in (ref, same, undet, diff)]
        self.assertEqual([v.split(" ")[0] for v in verdicts], ["reference", "no", "IDENTITY", "DIFFERS"])
        verdicts += [summ.identity(undet, undet), summ.identity(dict(undet, id="r5"), ref), summ.identity(same, None)]
        self.assertEqual(summ.verdict_counts(verdicts), {"no observed difference": 1, "identity undetermined": 2, "differ": 1,
                                                         "references": 1, "references with unread lines": 1, "no reference": 1})


class LastCounterTest(unittest.TestCase):
    def test_last_counter_in_each_form(self):
        legend = "match reads, one list per read: " + e005.READ_FIELDS
        one = {"observations": [{"step": 9, "field": legend, "value": json.dumps([[1, "u", 1.0, "t", "a", "d", "0x0001", "s", 0, 0, ""],
                                                                                [2, "u", 2.0, "t", "a", "d", "0x005e", "s", 0, 0, ""]])}]}
        self.assertEqual(summ.last_counter(one), "0x005e")
        per = {"observations": [{"step": s, "field": f"match read {s}: [host UTC time, host s since the starting burst, ...]",
                                 "value": json.dumps(["u", 1.0, "t", "a", "d", c, "s", 0, 0, ""])} for s, c in ((3, "0x0001"), (4, "0x005e"))]}
        self.assertEqual(summ.last_counter(per), "0x005e")
        old = {"observations": [{"step": s, "field": f"match read {s}: words DS:80EE (commentary counter) and DS:7B62 (seed), ...",
                                 "value": f"{c} 0xa621 2 3"} for s, c in ((5, "0x005e"), (4, "0x0001"))]}
        self.assertEqual(summ.last_counter(old), "0x005e")
        self.assertIsNone(summ.last_counter({"observations": []}))


class BeforeFirstKeyTest(unittest.TestCase):
    def test_half_time_before_the_probes_first_key(self):
        row = {"e005_polls": [{"poll": 0, "rows": "a / ---- HALF TIME ---- / b", "counter": 154}, {"poll": 1, "rows": "x", "counter": 154}]}
        self.assertIn("the first half was played before the probe's clock started", summ.before_first_key(row))
        row = {"e005_polls": [{"poll": 0, "rows": "a / b / c", "counter": 0}, {"poll": 1, "rows": "---- HALF TIME ----", "counter": 154}]}
        self.assertEqual(summ.before_first_key(row), "before the probe's key c: no HALF TIME, DS:80EE 0")
        self.assertEqual(summ.before_first_key({"e005_polls": [{"poll": 1, "rows": "---- HALF TIME ----"}]}), "no read before the probe's key c")


class ProbeWrapperTest(unittest.TestCase):
    def test_polls_are_decoded_only_inside_the_match_and_the_keys_are_the_probes(self):
        calls = []

        def screen(self):
            calls.append("screen")
            return "sc", b"data"

        def play(s, row, timeout):
            s.screen()
            s.screen()
            row["full_time_after_s"] = 1.0
            return "sc"

        with mock.patch.object(pf.probe, "play_to_full_time", play), mock.patch.object(pf.probe.dbx.Session, "screen", screen), \
                mock.patch.object(pf, "decode", side_effect=lambda data, since, n: {"poll": n, "data": data}):
            pf.instrument()
            s = pf.probe.dbx.Session.__new__(pf.probe.dbx.Session)
            s.screen()                         # outside the match (a restore, a settle): not decoded
            row = {}
            pf.probe.play_to_full_time(s, row, 5)
            s.screen()                         # after full time: not decoded
        self.assertEqual(calls, ["screen"] * 4)
        self.assertEqual(row["e005_polls"], [{"poll": 1, "data": b"data"}, {"poll": 2, "data": b"data"}])
        self.assertEqual(row["full_time_after_s"], 1.0)

    def test_the_pre_read_is_poll_0_before_the_probes_first_key(self):
        order = []

        def screen(self):
            order.append("screen")
            return "sc", b"data"

        def play(s, row, timeout):
            order.append("key c")             # probe.play_to_full_time's first act is s.key("c")
            s.screen()
            return "sc"

        with mock.patch.object(pf.probe, "play_to_full_time", play), mock.patch.object(pf.probe.dbx.Session, "screen", screen), \
                mock.patch.object(pf, "decode", side_effect=lambda data, since, n: {"poll": n}):
            pf.instrument(pre_read=True)
            s = pf.probe.dbx.Session.__new__(pf.probe.dbx.Session)
            row = {}
            pf.probe.play_to_full_time(s, row, 5)
        self.assertEqual(order, ["screen", "key c", "screen"])
        self.assertEqual(row["e005_polls"], [{"poll": 0}, {"poll": 1}])


if __name__ == "__main__":
    unittest.main()
