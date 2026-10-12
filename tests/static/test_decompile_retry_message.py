"""The GOALRETRY message line of tools/static/decompile.sh (fix #69), run as the script has it.

GoalDecompile.java prints GOALRETRY on every failed attempt but retries only after "process died"
and before the last attempt (ATTEMPTS = 3). The sed command is cut out of the script itself, so an
edit of the script cannot drift from this test.
"""
import re
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "static" / "decompile.sh"
PREFIX = "INFO  GoalDecompile.java> GOALRETRY 0791:9564 attempt"


def script_sed():
    for line in SCRIPT.read_text().splitlines():
        if line.startswith("grep 'GOALRETRY'"):
            m = re.search(r"\| (sed .*?) >&2", line)
            return m.group(1)
    raise AssertionError("no GOALRETRY line in decompile.sh")


class RetryMessage(unittest.TestCase):
    def test_message_only_where_a_retry_happens(self):
        cases = [
            (f"{PREFIX} 1: Decompiler process died (GhidraScript)  ", "retrying with a fresh one: 0791:9564 attempt 1: Decompiler process died"),
            (f"{PREFIX} 2: Decompiler process died unexpectedly (GhidraScript)  ", "retrying with a fresh one: 0791:9564 attempt 2: Decompiler process died unexpectedly"),
            (f"{PREFIX} 3: Decompiler process died (GhidraScript)  ", "not retrying: 0791:9564 attempt 3: Decompiler process died"),
            (f"{PREFIX} 1: Timeout exceeded (GhidraScript)  ", "not retrying: 0791:9564 attempt 1: Timeout exceeded"),
        ]
        out = subprocess.run(script_sed(), shell=True, check=True, capture_output=True, text=True,
                             input="\n".join(c[0] for c in cases) + "\n").stdout.splitlines()
        self.assertEqual(len(out), len(cases))
        for got, (_, want) in zip(out, cases):
            self.assertEqual(got, "decompile.sh: decompiler failed, " + want)


if __name__ == "__main__":
    unittest.main()
