"""T34 nested-display recorder tests."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location("human_recorder", Path(__file__).resolve().parents[1] / "runtime/human/recorder.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


class NestedDisplayTests(unittest.TestCase):
    def test_try_start_skips_busy_number_and_changes_only_child_display(self):
        busy, free = Mock(), Mock()
        busy.poll.return_value = 1
        free.poll.return_value = None
        env = {"DISPLAY": ":612", "OTHER": "kept"}
        with patch.object(rec.subprocess, "Popen", side_effect=[busy, free]) as launch, patch.object(rec.time, "sleep"):
            proc, nested = rec.start_nested(env, "800x600", None)
        self.assertIs(proc, free)
        self.assertEqual(env["DISPLAY"], ":612")
        self.assertEqual(nested, {"DISPLAY": ":601", "OTHER": "kept"})
        self.assertEqual(launch.call_args_list[0].args[0], ["Xephyr", ":600", "-screen", "800x600", "-nolisten", "tcp"])
        self.assertEqual(launch.call_args_list[1].kwargs["env"], env)

    def test_self_test_requires_nested_tools(self):
        with patch.object(rec, "ensure_cache", return_value="fixture"), patch.object(rec, "dosbox_version", return_value="2024.03.01"), patch.object(rec.shutil, "which", side_effect=lambda name: None if name in ("Xephyr", "xinput") else name):
            self.assertEqual(rec.self_test(), 1)
