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


if __name__ == "__main__":
    unittest.main()
