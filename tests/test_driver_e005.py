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

    def test_identical_needs_score_events_seed_and_every_line(self):
        a = {"score": ("A", 1, "B", 0), "events": [["goal", 0, "x"]], "seed": "0x1", "lines": [[1, 2, 0, "x"]]}
        self.assertTrue(summ.same(a, dict(a)))
        for k, v in (("score", ("A", 1, "B", 1)), ("events", []), ("seed", "0x2"), ("lines", [[1, 2, 0, "y"]])):
            self.assertFalse(summ.same(a, dict(a, **{k: v})), k)


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


class UnreadLinesTest(unittest.TestCase):
    """Review R1 and R2: a line the reader never read leaves the run's identity undetermined; it is never
    counted as identical, and a flag covers only the occurrence it names."""
    BASE = {"score": ("S", 2, "D", 3), "events": [["booking", 1, "Brolin BOOKED"]], "seed": "0xa621", "counter": "0x0005"}
    ALL = {1: (2, 5, 0, 0), 2: (50, 6, 0, 1), 3: (2, 7, 0, 0), 4: (2, 5, 0, 0), 5: (2, 6, 0, 1)}

    def ref(self):
        return dict(self.BASE, id="ref", **tracked([ctest.make_state(5, self.ALL)]))

    def test_a_line_the_reader_never_read_is_undetermined_whatever_it_held(self):
        # Sol's case: record 3 is the end marker at read 1, and at read 2 holds another line than the
        # reference's (Ekstrom makes a pass there; here Nilsson's). The run is not identical.
        first = dict(self.ALL)
        first[3] = (0xFF, 0, 0, 0)
        later = dict(self.ALL)
        later[3] = (2, 5, 0, 0)
        run = dict(self.BASE, id="run", **tracked([ctest.make_state(3, first), ctest.make_state(5, later)]))
        self.assertEqual(run["gaps"], ["match read 1: record 3 is the end marker 0xFF"])
        self.assertEqual(summ.unread_occurrences(run), [3])
        self.assertEqual(summ.unread_only(run, self.ref()), [3])
        v = summ.identity(run, self.ref())
        self.assertTrue(v.startswith("IDENTITY UNDETERMINED"), v)
        self.assertNotIn("identical to", v)

    def test_the_occurrence_is_the_flagged_reads_not_any_with_that_record_number(self):
        # 205 lines: record 3 occurs twice (occurrences 3 and 203). The flag of read 2 names occurrence 203.
        ref = dict(self.BASE, id="ref", counter="0x0005", gaps=[], deltas=[200, 5],
                   lines=[[(i - 1) % 200 + 1, 2, 0, f"line {i}"] for i in range(1, 206)])
        flag = ["match read 2: record 3 is the end marker 0xFF"]
        run = dict(ref, id="run", gaps=flag, lines=[x for i, x in enumerate(ref["lines"], 1) if i != 203])
        self.assertEqual(summ.unread_occurrences(run), [203])
        self.assertEqual(summ.unread_only(run, ref), [203])
        other = dict(run, lines=[x for i, x in enumerate(ref["lines"], 1) if i != 3])       # the other occurrence of record 3
        self.assertIsNone(summ.unread_only(other, ref))
        self.assertTrue(summ.identity(other, ref).startswith("DIFFERS"))
        both = dict(run, lines=[x for i, x in enumerate(ref["lines"], 1) if i not in (3, 203)])   # one flag, two losses
        self.assertIsNone(summ.unread_only(both, ref))
        self.assertTrue(summ.identity(both, ref).startswith("DIFFERS"))

    def test_anything_else_differs(self):
        ref = dict(self.BASE, id="ref", counter="0x0005", gaps=[], deltas=[5],
                   lines=[[i, 2, 0, f"line {i}"] for i in range(1, 6)])
        run = dict(ref, id="run", gaps=["match read 1: record 3 is the end marker 0xFF"],
                   lines=[x for x in ref["lines"] if x[0] != 3])
        self.assertEqual(summ.unread_only(run, ref), [3])
        for k, v in (("counter", "0x0004"), ("seed", "0x0001"), ("score", ("S", 2, "D", 2)), ("events", [])):
            self.assertIsNone(summ.unread_only(dict(run, **{k: v}), ref), k)
        self.assertIsNone(summ.unread_only(dict(run, gaps=[]), ref))                                   # not flagged
        self.assertIsNone(summ.unread_only(dict(run, gaps=["match read 1: record 4 is the end marker 0xFF"]), ref))  # another record
        self.assertIsNone(summ.unread_only(dict(run, gaps=run["gaps"] + ["match read 1: counter 0 -> 150 (150 lines)"]), ref))
        self.assertIsNone(summ.unread_only(run, dict(ref, gaps=["match read 1: record 2 is the end marker 0xFF"])))  # reference incomplete
        self.assertIsNone(summ.unread_only(dict(run, lines=run["lines"][:2] + [[4, 2, 0, "other"]] + run["lines"][3:]), ref))
        self.assertIsNone(summ.unread_only(dict(run, gaps=run["gaps"] * 2), ref))                     # one occurrence, two flags
        self.assertTrue(summ.identity(dict(run, gaps=[]), ref).startswith("DIFFERS"))

    def test_a_flag_outside_its_reads_range_is_refused(self):
        r = {"gaps": ["match read 2: record 9 is the end marker 0xFF"], "deltas": [5, 3]}   # read 2 covers records 6-8
        self.assertIsNone(summ.unread_occurrences(r))
        self.assertEqual(summ.unread_occurrences(dict(r, gaps=["match read 2: record 8 is the end marker 0xFF"])), [8])
        self.assertIsNone(summ.unread_occurrences(dict(r, gaps=["match read 3: record 8 is the end marker 0xFF"])))


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
