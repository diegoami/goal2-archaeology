#!/usr/bin/env python3
"""T34 in-place mutation proofs; restores each source even when a test fails."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REC = "runtime/human/recorder.py"
MAP = "experiments/E015-human-playthrough/keymap.py"
MUTATIONS = [
    ("display restriction removed", REC, 'if not env.get("DISPLAY") or env["DISPLAY"] == outer_display:', 'if False:'),
    ("burst capture removed", REC, 'is_burst = burst.due(now)', 'is_burst = False'),
    ("quiet +1", REC, 'BURST_QUIET_S = 0.5', 'BURST_QUIET_S = 1.5'),
    ("quiet -1", REC, 'BURST_QUIET_S = 0.5', 'BURST_QUIET_S = -0.5'),
    ("map quiet +1", MAP, 'quiet=0.5', 'quiet=1.5'),
    ("map quiet -1", MAP, 'quiet=0.5', 'quiet=-0.5'),
    ("text identity removed", MAP, 'hashlib.sha256(text.encode("utf-8")).hexdigest()', 'state["screen_digest"]'),
    ("headline removed", MAP, 'next((row.strip() for row in text.splitlines() if row.strip()), "(blank)")', '"(blank)"'),
    ("invalid snapshot filter removed", MAP, 'if state.get("error") or elapsed is None:', 'if elapsed is None:'),
    ("snapshot ordering removed", MAP, 'samples.sort()', 'pass'),
    ("event ordering removed", MAP, 'sorted(events, key=lambda e: e["monotonic_s"])', 'events'),
    ("burst grouping removed", MAP, 'event["monotonic_s"] > bursts[-1][-1]["monotonic_s"] + quiet', 'True'),
    ("release filter removed", MAP, 'if e["event"] == "press"', 'if True'),
    ("before selection reversed", MAP, 'before[-1]', 'before[0]'),
    ("after selection reversed", MAP, 'after[0]', 'after[-1]'),
    ("before boundary changed", MAP, 'when < burst[0]["monotonic_s"]', 'when <= burst[0]["monotonic_s"]'),
    ("after boundary changed", MAP, 'when >= burst[-1]["monotonic_s"] + quiet', 'when > burst[-1]["monotonic_s"] + quiet'),
    ("missing bracket count removed", MAP, 'unmapped += len(pressed)', 'unmapped += 0'),
    ("transition count removed", MAP, 'transitions.get(key, 0) + 1', '1'),
    ("press count removed", MAP, 'total += len(pressed)', 'total += 0'),
]


def main():
    survivors = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(ROOT / "scratch/t34-tmp"))
    for name, filename, old, new in MUTATIONS:
        path = ROOT / filename
        original = path.read_bytes()
        text = original.decode()
        assert text.count(old) == 1, (name, text.count(old))
        try:
            path.write_text(text.replace(old, new))
            result = subprocess.run([sys.executable, "-B", "-m", "unittest", "-v",
                                     "tests.test_human_keys", "tests.test_human_record"],
                                    cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
            print(f"\nMUTATION: {name}; exit={result.returncode}", flush=True)
            print(result.stdout, flush=True)
            if result.returncode == 0:
                survivors.append(name)
        finally:
            path.write_bytes(original)
    print(f"Survivors: {survivors}", flush=True)
    return bool(survivors)


if __name__ == "__main__":
    sys.exit(main())
