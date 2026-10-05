"""E003's runner (experiments/E003-q001-inputs/run.py): a record's actions.sha256 names the script
as it was when the module was loaded, not as the file stands when the record is written. The edge
is a mid-batch edit of the script (E004-r0231): the test loads a copy of run.py, edits the copy
after the import, writes a record and requires the load-time hash."""
import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import driver  # noqa: E402


def load_copy(tmp):
    """A copy of E003's run.py, loaded as a module from tmp/c1/c2/c3/: three levels down so the
    copy module's own ROOT (parents[2]) is a path that cannot appear in a record's text, which
    record() refuses to write. The test then edits the copy, as a mid-batch edit would."""
    copy = Path(tmp) / "c1" / "c2" / "c3" / "run.py"
    copy.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "experiments" / "E003-q001-inputs" / "run.py", copy)
    spec = importlib.util.spec_from_file_location("e003_run_copy", copy)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, copy


class RecordNamesTheLoadedScript(unittest.TestCase):
    def write_record(self, mod, tmp):
        """Run.record with the launch-time machinery absent: no config (a fresh Driver has none),
        no artifact check, the record into tmp/out."""
        args = argparse.Namespace(dos_time=None, dos_date=None, batch="t")
        out = Path(tmp) / "out"
        with mock.patch.object(mod, "OUT", out), \
                mock.patch.object(driver, "verify_release", return_value="goal2-a949da2f"):
            mod.Run("d0", 8888, args, "abc1234").record("completed", True)
        return json.loads((out / "E003-r8888.json").read_text())

    def test_record_carries_the_load_time_script_hash(self):
        """A record names the code that ran: an edit of the script after the module was loaded
        (E004-r0231's defect) must not change the actions.sha256 a later record carries."""
        with tempfile.TemporaryDirectory() as tmp:
            mod, copy = load_copy(tmp)
            load_sha = driver.sha256(copy.read_bytes())  # the hash as the module was loaded
            copy.write_bytes(copy.read_bytes() + b"\n# mid-batch edit\n")
            self.assertNotEqual(driver.sha256(copy.read_bytes()), load_sha)
            rec = self.write_record(mod, tmp)
            self.assertEqual(rec["actions"]["sha256"], load_sha)

    def test_module_hashes_the_script_at_load(self):
        """The mechanism: the module computes its own hash once, at load, from the file as loaded."""
        with tempfile.TemporaryDirectory() as tmp:
            mod, copy = load_copy(tmp)
            load_sha = driver.sha256(copy.read_bytes())
            self.assertEqual(mod.SCRIPT_SHA, load_sha)


if __name__ == "__main__":
    unittest.main()
