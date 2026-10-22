"""Run the T63 review blockers as isolated source mutations of the focused tests."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "runtime/original_match/port/positioning.py"
MUTATIONS = {
    "A920-element-push-deleted": ('push_word(mem, element, "2074")', 'pass'),
    "49D3-terminal-increment-deleted": ('f.w16(-3, slot + 1, "0791:49D3")', 'pass'),
    "4A1B-stale-clear-deleted": ('mem.wds16(mark_off, 0, "0791:4A1B")', 'pass'),
    "group4-attack-limit-zero": (
        'limit = mem.ds8(0x07DB + ((s8(tactic & 0xff) * 4 + group) & 0xffff))',
        'limit = 0 if group == 4 else mem.ds8(0x07DB + ((s8(tactic & 0xff) * 4 + group) & 0xffff))'),
    "group4-defend-limit-255": (
        'limit = mem.ds8(0x07CB + ((s8(t5 & 0xff) * 8 + s8(t6 & 0xff) * 4 + group) & 0xffff))\n    if',
        'limit = 255 if group == 4 else mem.ds8(0x07CB + ((s8(t5 & 0xff) * 8 + s8(t6 & 0xff) * 4 + group) & 0xffff))\n    if'),
}


def run(root):
    return subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_positioning"],
                          cwd=root, capture_output=True, text=True)


def main():
    original = SOURCE.read_text()
    with tempfile.TemporaryDirectory(prefix="t63-rework-mut-") as temporary:
        root = Path(temporary)
        shutil.copytree(ROOT / "runtime", root / "runtime")
        shutil.copytree(ROOT / "tests", root / "tests")
        copy = root / "runtime/original_match/port/positioning.py"
        baseline = run(root)
        assert baseline.returncode == 0, baseline.stderr
        records = []
        for name, (before, after) in MUTATIONS.items():
            assert original.count(before) == (2 if name == "49D3-terminal-increment-deleted" else 1), name
            changed = original.replace(before, after)
            try:
                copy.write_text(changed)
                result = run(root)
            finally:
                copy.write_text(original)
            record = {"mutation": name, "exit": result.returncode,
                      "assertion_failure": "FAIL:" in result.stderr,
                      "import_or_test_error": "ERROR:" in result.stderr}
            records.append(record)
            assert result.returncode and record["assertion_failure"] and not record["import_or_test_error"], record
        assert run(root).returncode == 0
        print(json.dumps({"baseline": "14 tests pass", "restored": "14 tests pass", "mutants": records}, indent=2))


if __name__ == "__main__":
    main()
