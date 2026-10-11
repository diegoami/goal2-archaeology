"""#117: the DOSBox-X the project runs is the 2024.03.01 it is calibrated to. driver.dosbox_x()
resolves $DOSBOX_X, else the bundle setup/dosbox-x-2024.03.01.sh installs, else dosbox-x on PATH;
the driver, the recorder and its version check use it, and scripted_keys.py refuses another version
before any display or emulator starts."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "human"))
import driver  # noqa: E402
import recorder  # noqa: E402


def fake_dosbox(folder, version):
    """An executable that prints a DOSBox-X version banner, as `dosbox-x -version` does."""
    p = Path(folder) / "dosbox-x"
    p.write_text(f"#!/bin/sh\necho 'DOSBox-X version {version} SDL2, copyright' >&2\nexit 1\n")
    p.chmod(0o755)
    return p


class ResolverTests(unittest.TestCase):
    def test_dosbox_x_env_wins(self):
        self.assertEqual(driver.dosbox_x({"DOSBOX_X": "/opt/x/dosbox-x"}), "/opt/x/dosbox-x")

    def test_the_bundle_when_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = fake_dosbox(tmp, "2024.03.01")
            with mock.patch.object(driver, "DOSBOX_BUNDLE", bundle):
                self.assertEqual(driver.dosbox_x({}), str(bundle))

    def test_path_when_no_bundle(self):
        with mock.patch.object(driver, "DOSBOX_BUNDLE", Path("/nonexistent/dosbox-x")):
            self.assertEqual(driver.dosbox_x({}), "dosbox-x")

    def test_the_recorder_checks_the_resolved_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            # a version no real dosbox-x reports, so the one on PATH cannot pass for the fake
            fake = fake_dosbox(tmp, "1999.09.09")
            with mock.patch.dict(os.environ, {"DOSBOX_X": str(fake)}):
                self.assertIn("1999.09.09", recorder.dosbox_version())


class ExactVersionTests(unittest.TestCase):
    """Luna's R1-R3 on PR 120: the version is matched exactly, and every launch refuses another."""

    def test_the_exact_version_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = fake_dosbox(tmp, "2024.03.01")
            self.assertEqual(driver.require_dosbox({"DOSBOX_X": str(fake)}), str(fake))

    def test_a_longer_or_other_version_is_refused(self):
        for version in ("2024.03.010", "2024.03.01.1", "2024.03.01-rc", "2026.01.02", "12024.03.01"):
            with tempfile.TemporaryDirectory() as tmp:
                fake = fake_dosbox(tmp, version)
                with self.assertRaises(RuntimeError, msg=version):
                    driver.require_dosbox({"DOSBOX_X": str(fake)})

    def test_the_driver_launch_refuses_before_anything_starts(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = driver.Driver({}, workdir=Path(tmp) / "work", game_dir=Path(tmp) / "game")
            started = []
            with mock.patch.object(driver, "require_dosbox", side_effect=RuntimeError("refused")), \
                    mock.patch.object(driver.Driver, "_start_xvfb", lambda self: started.append("xvfb")):
                with self.assertRaisesRegex(RuntimeError, "refused"):
                    d.launch()
            self.assertEqual(started, [])
            self.assertFalse((Path(tmp) / "work").exists(), "a work folder was made before the check")

    def test_bare_and_banner_versions_parse_exactly(self):
        self.assertEqual(driver.version_in("DOSBox-X version 2024.03.01 SDL2, copyright"), "2024.03.01")
        self.assertEqual(driver.version_in("2024.03.01"), "2024.03.01")
        self.assertEqual(driver.version_in("DOSBox-X version 2024.03.01.1 SDL2"), "2024.03.01.1")
        self.assertIsNone(driver.version_in(None))

    def test_the_recorder_play_refuses_before_any_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = fake_dosbox(tmp, "2026.01.02")
            with mock.patch.dict(os.environ, {"DOSBOX_X": str(fake), "DISPLAY": ":12345"}), \
                    mock.patch.object(recorder, "new_session", side_effect=AssertionError("a session was made")):
                self.assertEqual(recorder.play(), 2)


class ScriptedKeysRefusesTests(unittest.TestCase):
    def test_another_version_is_refused_before_anything_starts(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = fake_dosbox(tmp, "2026.01.02")
            r = subprocess.run([sys.executable, str(ROOT / "experiments/E015-human-playthrough/scripted_keys.py"),
                                "--keys", "a"], env=dict(os.environ, DOSBOX_X=str(fake)),
                               capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("refused: dosbox-x 2024.03.01 is required, found", r.stderr)
            self.assertIn("2026.01.02", r.stderr)

    def test_a_longer_version_is_refused_too(self):
        # Luna's R3 on PR 120: the old substring check accepted 2024.03.010
        with tempfile.TemporaryDirectory() as tmp:
            fake = fake_dosbox(tmp, "2024.03.010")
            r = subprocess.run([sys.executable, str(ROOT / "experiments/E015-human-playthrough/scripted_keys.py"),
                                "--keys", "a"], env=dict(os.environ, DOSBOX_X=str(fake)),
                               capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("found 2024.03.010", r.stderr)


if __name__ == "__main__":
    unittest.main()
