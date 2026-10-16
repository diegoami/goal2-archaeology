"""Issue 244: the driver's keys reach the guest as themselves, with no Alt.

Found by E031 (play-the-game, lastkey.py): runtime/driver/driver.py sent keys with xdotool, which pressed
Left Alt (X keycode 64) around every function key, so the game read Alt+F10 (BIOS word 0x7100, DS:A976 =
0xD5) instead of F10 (0x4400, 0xA8); and the F12+S savestate chord, sent as keydown and keyup in separate
calls, left Left Alt held in the guest from the launch on (0040:0017 bit 3, 0040:0018 bit 1), so every
run of the driver had Alt held. The driver now sends raw XTEST keycodes (xkeys.py) and presses Scroll Lock
for the savestate, through a mapper file it writes.

Two halves.
KeySending: no emulator. A bare Xvfb, `xinput test-xi2 --root` recording the raw key events the driver's
`keys` and `_hostkey` produce (a Driver given only the display, no DOSBox-X). Fails on the old driver
(it records keycode 64, Alt_L, and F12 for the chord). Skips where Xvfb or xinput is absent (CI).
EndToEnd: the emulator. experiments/fix-244-driver-keys/probe.py launches GOAL, sends keys and F10, and
reads the BIOS flags from the driver's own savestates; no Alt at any read, F10 as DS:A976 = 0xA8 with the
word 0x4400 in the BIOS buffer and no 0x7100. Skips like test_driver_terminate's edge test: without
DOSBox-X 2024.03.01, Xvfb, xdotool or the verified release (setup/goal2-runtime.sh).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "tests"))

import driver  # noqa: E402
import xkeys  # noqa: E402
from test_driver_terminate import release_problem  # noqa: E402

XVFB = all(shutil.which(t) for t in ("Xvfb", "xinput", "xmodmap"))
EMULATOR = all(shutil.which(t) for t in ("Xvfb", "xdotool")) and driver.dosbox_version_of(driver.dosbox_x()) == driver.WANT_DOSBOX
ALT_L = "Alt_L"


class Display:
    """A private Xvfb (never :99) with `xinput test-xi2 --root` recording the raw key events on it."""

    def __init__(self):
        for attempt in range(20):
            num = 300 + (os.getpid() + attempt * 11) % 500
            if os.path.exists(f"/tmp/.X{num}-lock"):
                continue
            self.name = f":{num}"
            self.xvfb = subprocess.Popen(["Xvfb", self.name, "-screen", "0", "640x480x24", "-nolisten", "tcp"],
                                         stderr=subprocess.DEVNULL, start_new_session=True)
            env = dict(os.environ, DISPLAY=self.name)
            for _ in range(100):
                if subprocess.run(["xmodmap", "-pke"], env=env, capture_output=True).returncode == 0:
                    break
                time.sleep(0.1)
            else:
                self.xvfb.kill()
                continue
            self.env = env
            break
        else:
            raise RuntimeError("no Xvfb display")
        km = subprocess.run(["xmodmap", "-pke"], env=self.env, capture_output=True, text=True).stdout
        self.names = {int(m[1]): m[2].split()[0] for m in re.finditer(r"keycode\s+(\d+) = (\S.*)", km)}
        self.rec = subprocess.Popen(["xinput", "test-xi2", "--root"], env=self.env, stdout=subprocess.PIPE,
                                    text=True, start_new_session=True)
        time.sleep(0.7)  # xinput is listening before the first event is sent

    def events(self):
        """The raw key events recorded so far, as ('press'|'release', name of the keycode's first keysym)."""
        time.sleep(0.4)
        self.rec.terminate()
        out = self.rec.stdout.read()
        return [("press" if m[1] == "RawKeyPress" else "release", self.names[int(m[2])])
                for m in re.finditer(r"EVENT type \d+ \((RawKeyPress|RawKeyRelease)\).*?detail: (\d+)", out, re.S)]

    def close(self):
        for p in (self.rec, self.xvfb):
            if p.poll() is None:
                p.terminate()
            p.wait()
            if p.stdout:
                p.stdout.close()


@unittest.skipUnless(XVFB, "needs Xvfb, xinput and xmodmap")
class KeySending(unittest.TestCase):
    def setUp(self):
        self.x = Display()
        self.addCleanup(self.x.close)
        self.tmp = Path(tempfile.mkdtemp(prefix="keys244-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def driver(self, **kw):
        d = driver.Driver({}, workdir=self.tmp / "work", game_dir=self.tmp / "game", **kw)
        d.display, d.env = self.x.name, self.x.env  # the keys' target; no emulator is started
        return d

    def test_a_function_key_is_sent_as_itself_without_alt(self):
        # the fault: xdotool pressed Alt_L (keycode 64) around F10, so the game read Alt+F10
        self.driver().keys("F10", hold=0.02)
        self.assertEqual([("press", "F10"), ("release", "F10")], self.x.events())

    def test_every_function_key_arrives_alone(self):
        names = [f"F{i}" for i in range(1, 13)]
        self.driver().keys(*names, hold=0.01)
        want = [(act, n) for n in names for act in ("press", "release")]
        self.assertEqual(want, self.x.events())

    def test_the_savestate_key_is_one_key_and_never_f12_or_alt(self):
        # the fault: the chord F12+S, and F12 brought Alt_L with it that nothing released in the guest
        d = self.driver()
        d._hostkey("s", hold=0.02)
        d._hostkey("l", hold=0.02)
        self.assertEqual([("press", "Scroll_Lock"), ("release", "Scroll_Lock"),
                          ("press", "Print"), ("release", "Print")], self.x.events())

    def test_the_keys_the_callers_send_are_single_keys(self):
        names = ["n", "y", "r", "0", "9", "Enter", "Esc", "Space", "Up", "Down", "Left", "Right",
                 "Backspace", "Tab", "Insert"]
        self.driver().keys(*names, hold=0.01)
        got = self.x.events()
        self.assertEqual(2 * len(names), len(got), got)
        self.assertNotIn(ALT_L, [n for _, n in got])
        self.assertEqual(["press", "release"] * len(names), [a for a, _ in got])

    def test_an_upper_case_letter_is_sent_with_shift_around_it_and_nothing_else(self):
        self.driver().keys("N", hold=0.01)
        self.assertEqual([("press", "Shift_L"), ("press", "n"), ("release", "n"), ("release", "Shift_L")], self.x.events())

    def test_a_key_that_would_need_a_modifier_or_does_not_exist_is_refused(self):
        d = self.driver()
        for bad in ("XF86Switch_VT_10", "NoSuchKeysym"):
            with self.assertRaises(ValueError, msg=bad):
                d.keys(bad, hold=0.01)
        self.assertEqual([], self.x.events())  # refused before any event was sent

    def test_the_default_hold_of_the_savestate_key_is_the_old_read_pace(self):
        # Earlier experiments' settle (two equal reads) reproduces its records only at the pace of the old F12
        # chord: 3 steps of HOSTKEY_HOLD = 0.45 s and four xdotool calls, 0.512 ... 0.764 s between chords
        # in E003-r0047 and r0049 (median 0.535 s). At 0.15 s E003 d3b stopped on a transient screen.
        self.assertAlmostEqual(0.52, driver.SAVE_HOLD)
        self.assertGreaterEqual(driver.SAVE_HOLD, 3 * driver.HOSTKEY_HOLD)
        d = self.driver()
        self.assertEqual(driver.SAVE_HOLD, d.save_hold)
        t0 = time.monotonic()
        d._hostkey("s")
        took = time.monotonic() - t0
        self.assertTrue(0.50 <= took <= 0.62, f"a savestate key took {took:.3f}s")
        self.assertIn("held 0.52s", " ".join(w for _, w in d.events))
        self.x.events()

    def test_a_custom_save_hold_is_honoured_at_call_time(self):
        d = self.driver(save_hold=0.2)
        t0 = time.monotonic()
        d._hostkey("s")
        self.assertTrue(0.2 <= time.monotonic() - t0 < 0.45)
        d.save_hold = 0.05  # changed after the driver was made: read at the call, not bound earlier
        t0 = time.monotonic()
        d._hostkey("l")
        self.assertLess(time.monotonic() - t0, 0.2)
        d._hostkey("s", hold=0.3)  # an explicit hold wins
        events = " ".join(w for _, w in d.events)
        for held in ("held 0.2s", "held 0.05s", "held 0.3s"):
            self.assertIn(held, events)
        self.x.events()

    def test_legacy_keys_is_the_old_fault_kept_to_reproduce_it(self):
        d = self.driver(legacy_keys=True)
        d.keys("F10", hold=0.02)
        got = self.x.events()
        self.assertIn(ALT_L, [n for _, n in got])


class Mapper(unittest.TestCase):
    def test_the_mapper_is_the_one_e031_wrote(self):
        want = (ROOT / "experiments" / "E031-play-the-game" / "mapper-nohost.map").read_text()
        self.assertEqual(want, xkeys.mapper_text())

    def test_the_mapper_moves_the_savestate_off_f12_to_scroll_lock(self):
        text = xkeys.mapper_text()
        self.assertIn('hand_savestate "key 71" \n', text)
        self.assertIn('hand_loadstate "key 70" \n', text)
        self.assertNotIn('hand_savestate "key 22 host"', text)
        self.assertNotIn('hand_loadstate "key 15 host"', text)

    def test_a_default_bind_that_is_not_there_exactly_once_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "m.map"
            src.write_text("nothing here\n")
            with self.assertRaisesRegex(RuntimeError, "exactly once"):
                xkeys.mapper_text(src)

    def test_launch_writes_the_mapper_and_the_dosbox_mapper_removes_a_stale_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = driver.Driver({}, workdir=Path(tmp) / "work", game_dir=Path(tmp) / "game")
            d.workdir.mkdir()
            d._write_mapper()
            self.assertEqual(xkeys.mapper_text(), (d.workdir / "mapper.map").read_text())
            self.assertIn("mapper file (written)", " ".join(w for _, w in d.events))
            old = driver.Driver({}, workdir=d.workdir, game_dir=Path(tmp) / "game", mapper="dosbox")
            old._write_mapper()
            self.assertFalse((d.workdir / "mapper.map").exists())


class KeyCalls(unittest.TestCase):
    """No emulator and no X: the key calls a driver makes for each combination of the two independent
    settings, the key transport (raw XTEST or xdotool) and the mapper (what the savestate and load keys are).
    A recording stands in for xkeys and xdotool; time.sleep records the holds.

    The table (key = the driver's, E031's play.py `--keys/--fkeys/--mapper`; savestate `s`):
      transport  mapper             keys pressed for the savestate
      raw        nohost (default)   Scroll_Lock, raw
      xdotool    nohost             Scroll_Lock, xdotool
      raw        dosbox / ""        F12 + s, raw (no Alt)
      xdotool    dosbox / ""        F12 + s, xdotool (the old driver: Alt held in the guest on Ubuntu 26.04)
      any        a file             what the file binds; a file it cannot read is refused (ValueError)
    and for play.py, F-keys (and a chord's F12) follow `fkeys`, every other key `keys`."""

    def setUp(self):
        self.calls, self.sleeps = [], []
        patches = [
            mock.patch.object(xkeys, "key_down", lambda d, n: self.calls.append(("raw", "down", n)) or [1], create=True),
            mock.patch.object(xkeys, "key_up", lambda d, n: self.calls.append(("raw", "up", n)) or [1], create=True),
            mock.patch.object(xkeys, "press_release", lambda d, n, h: self.calls.append(("raw", "press", n)) or [1]),
            mock.patch.object(driver.Driver, "_x", lambda self_, *a: self.calls.append(("xdotool",) + a)),
            mock.patch.object(driver.time, "sleep", lambda t: self.sleeps.append(t)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.tmp = Path(tempfile.mkdtemp(prefix="calls244-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def drv(self, **kw):
        d = driver.Driver({}, workdir=self.tmp / "work", game_dir=self.tmp / "game", **kw)
        d.display = ":0"
        return d

    def mapper_file(self, save, load, name="m.map"):
        f = self.tmp / name
        f.write_text(f'hand_savestate {save}\nhand_loadstate {load}\n')
        return f

    def save(self, d, name="s"):
        self.calls.clear()
        self.sleeps.clear()
        d._hostkey(name)
        return list(self.calls)

    def test_raw_with_the_default_mapper_presses_scroll_lock_raw(self):
        self.assertEqual([("raw", "down", "Scroll_Lock"), ("raw", "up", "Scroll_Lock")], self.save(self.drv()))
        self.assertEqual([0.52], self.sleeps)
        self.assertEqual([("raw", "down", "Print"), ("raw", "up", "Print")], self.save(self.drv(), "l"))

    def test_xdotool_with_the_default_mapper_presses_scroll_lock_by_xdotool(self):
        self.assertEqual([("xdotool", "keydown", "Scroll_Lock"), ("xdotool", "keyup", "Scroll_Lock")],
                         self.save(self.drv(legacy_keys=True)))

    def test_raw_with_the_dosbox_mapper_presses_the_f12_chord_raw_without_alt(self):
        got = self.save(self.drv(mapper="dosbox"))
        self.assertEqual([("raw", "down", "F12"), ("raw", "down", "s"), ("raw", "up", "s"), ("raw", "up", "F12")], got)
        self.assertAlmostEqual(0.52, sum(self.sleeps), places=4)  # the same total as one key: the read pace is the total
        self.assertEqual(3, len(self.sleeps))

    def test_xdotool_with_the_dosbox_mapper_is_the_old_driver(self):
        got = self.save(self.drv(legacy_keys=True, mapper="dosbox"))
        self.assertEqual([("xdotool", "keydown", "F12"), ("xdotool", "keydown", "s"), ("xdotool", "keyup", "s"),
                          ("xdotool", "keyup", "F12")], got)
        self.assertEqual([driver.HOSTKEY_HOLD] * 3, self.sleeps)  # the old steps of 0.15 s

    def test_a_custom_mapper_decides_the_keys_pressed(self):
        d = self.drv(mapper=str(self.mapper_file('"key 22"', '"key 15 host"')))  # s alone, F12 + l
        self.assertEqual([("raw", "down", "s"), ("raw", "up", "s")], self.save(d))
        self.assertEqual([("raw", "down", "F12"), ("raw", "down", "l"), ("raw", "up", "l"), ("raw", "up", "F12")],
                         self.save(d, "l"))

    def test_a_mapper_whose_savestate_or_load_bind_cannot_be_read_is_refused_at_once(self):
        for bad in (('"key 22 ctrl"', '"key 15"'), ('"key 999"', '"key 15"'), ('"key 22"', '')):
            with self.assertRaises(ValueError, msg=bad):
                self.drv(mapper=str(self.mapper_file(*bad)))
        nothing = self.tmp / "none.map"
        nothing.write_text("key_f12 \"key 69\" \n")
        with self.assertRaisesRegex(ValueError, "no hand_savestate bind"):
            self.drv(mapper=str(nothing))
        self.assertEqual([], self.calls)  # nothing was sent

    def play(self, **kw):
        sys.path.insert(0, str(ROOT / "experiments" / "E031-play-the-game"))
        try:
            import play
        finally:
            sys.path.pop(0)
        d = play.PlayDriver({}, workdir=self.tmp / "work", game_dir=self.tmp / "game", **kw)
        d.display = ":0"
        return d

    NOHOST = ROOT / "experiments" / "E031-play-the-game" / "mapper-nohost.map"

    def test_play_with_a_custom_f12_mapper_presses_what_that_mapper_binds(self):
        # 88edbd2 pressed Scroll Lock raw whatever mapper file was given, so a mapper with the F12 chords
        # (here the DOSBox-X defaults, as a file) never saw its savestate key and every read timed out
        d = self.play(mapper=str(xkeys.DEFAULT_MAP))
        got = self.save(d)
        self.assertEqual([("raw", "down", "F12"), ("raw", "down", "s"), ("raw", "up", "s"), ("raw", "up", "F12")], got)
        self.assertEqual([driver.HOSTKEY_HOLD] * 3, self.sleeps)  # this tool's own pace, a step of 0.15 s

    def test_play_with_fkeys_xdotool_sends_function_keys_by_xdotool_under_the_normal_mapper(self):
        # 88edbd2 sent F10 raw whatever --fkeys said whenever a mapper was given (the normal case)
        d = self.play(mapper=str(self.NOHOST), fkeys="xdotool")
        self.calls.clear()
        d.keys("F10", "n")
        self.assertEqual([("xdotool", "keydown", "F10"), ("xdotool", "keyup", "F10"), ("raw", "press", "n")], self.calls)
        self.assertEqual([("raw", "down", "Scroll_Lock"), ("raw", "up", "Scroll_Lock")], self.save(d))
        self.assertEqual([0.15], self.sleeps)

    def test_play_the_four_combinations(self):
        nohost, none = str(self.NOHOST), ""
        cases = [  # (keys, fkeys, mapper) -> (F10, n, savestate calls)
            (dict(mapper=nohost), [("raw", "press", "F10"), ("raw", "press", "n")],
             [("raw", "down", "Scroll_Lock"), ("raw", "up", "Scroll_Lock")]),
            (dict(mapper=nohost, keys="xdotool"), [("xdotool", "keydown", "F10"), ("xdotool", "keyup", "F10"),
                                                   ("xdotool", "keydown", "n"), ("xdotool", "keyup", "n")],
             [("xdotool", "keydown", "Scroll_Lock"), ("xdotool", "keyup", "Scroll_Lock")]),
            (dict(mapper=none, fkeys="xdotool"), [("xdotool", "keydown", "F10"), ("xdotool", "keyup", "F10"),
                                                  ("raw", "press", "n")],  # the guide's `--mapper "" --fkeys xdotool`
             [("xdotool", "keydown", "F12"), ("raw", "down", "s"), ("raw", "up", "s"), ("xdotool", "keyup", "F12")]),
            (dict(mapper=none, keys="xdotool"), [("xdotool", "keydown", "F10"), ("xdotool", "keyup", "F10"),
                                                 ("xdotool", "keydown", "n"), ("xdotool", "keyup", "n")],
             [("xdotool", "keydown", "F12"), ("xdotool", "keydown", "s"), ("xdotool", "keyup", "s"),
              ("xdotool", "keyup", "F12")]),  # the old driver, Alt held
        ]
        for kw, keys, saves in cases:
            d = self.play(**kw)
            self.calls.clear()
            d.keys("F10", "n")
            self.assertEqual(keys, self.calls, kw)
            self.assertEqual(saves, self.save(d), kw)

    def test_play_refuses_a_mapper_it_cannot_read_the_savestate_keys_from(self):
        with self.assertRaises(ValueError):
            self.play(mapper=str(self.mapper_file('"key 22 ctrl"', '"key 15"')))


@unittest.skipUnless(EMULATOR, "needs DOSBox-X 2024.03.01, Xvfb and xdotool")
class EndToEnd(unittest.TestCase):
    """The emulator: GOAL launched by the driver, keys sent, the BIOS flags read from its savestates."""

    def setUp(self):
        problem = release_problem()
        if problem:
            self.skipTest(f"the driver's release check failed: {problem}")
        self.tmp = Path(tempfile.mkdtemp(prefix="e2e244-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def probe(self, *extra):
        out = self.tmp / "probe.jsonl"
        probe = ROOT / "experiments" / "fix-244-driver-keys" / "probe.py"
        p = subprocess.run([sys.executable, str(probe), "--driver-dir", str(Path(driver.__file__).parent),
                            "--out", str(out), "--workdir", str(self.tmp / "work"), *extra],
                           capture_output=True, text=True, timeout=300)
        rows = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
        return p, [r for r in rows if "read" in r]

    def test_no_alt_is_held_and_f10_arrives_as_f10(self):
        p, rows = self.probe()
        self.assertEqual(4, len(rows), p.stdout + p.stderr)
        for r in rows:
            self.assertFalse(r["alt_held"], f"Alt held at {r['read']}: {r['0040:0017']} {r['0040:0018']} {r['0040:0096']}")
            self.assertEqual("0000", r["0040:0017"][-4:], r)  # no right or left shift, ctrl or alt (low nibble)
        last = rows[-1]
        self.assertEqual("a8", last["DS:A976"])         # F10 = scan 0x44 + 0x64, not Alt+F10's 0xD5
        self.assertIn("4400", last["buffer_words"])
        self.assertNotIn("7100", last["buffer_words"])
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
