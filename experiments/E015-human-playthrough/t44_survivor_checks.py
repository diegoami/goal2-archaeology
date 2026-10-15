#!/usr/bin/env python3
"""Fix #169: the three mutate_pause.py survivors on the head of main (T44-mutations-20261015-02.log).

    python3 experiments/E015-human-playthrough/t44_survivor_checks.py

Survivors 1 and 3 are gaps the T44 settle (EVENT_SETTLE_S 0.25 s, as long as PAUSE_POLL_S) opened
in the older tests; each now has a test that must fail on its mutant and pass on the source. The
source is written back in `finally`. Survivor 2 is an equivalent mutant: mapper_text strips every
non-kept host bind (issue 175), so leaving F12+P on `hand_scrshot` changes nothing in its output."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "runtime" / "human" / "recorder.py"
CASES = [
    ("survivor 1: the pause is not read again before a send",
     "if self.pause_probe is not None and self.poll_pause():", "if False:",
     "tests.test_human_pause.PauseLoopTests."
     "test_a_cadence_tick_due_soon_after_a_pause_begins_reads_the_pause_first"),
    ("survivor 3: a split F12 autorepeat pair ends the hold",
     "return self._host_down or now - self._host_released < HOST_RELEASE_GRACE_S",
     "return self._host_down",
     "tests.test_human_resume.ResumeChordTests."
     "test_a_cadence_tick_due_inside_a_split_f12_pair_waits_for_the_hold"),
]


def unittest_run(test):
    return subprocess.run([sys.executable, "-B", "-m", "unittest", "-v", test], cwd=ROOT,
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main():
    bad = 0
    for name, old, new, test in CASES:
        original = REC.read_bytes()
        text = original.decode()
        assert text.count(old) == 1, name
        try:
            REC.write_text(text.replace(old, new))
            mutant = unittest_run(test)
        finally:
            REC.write_bytes(original)
        pristine = unittest_run(test)
        print(f"== {name}\n-- on the mutant: exit {mutant.returncode} (must be 1)\n{mutant.stdout}"
              f"-- on the source: exit {pristine.returncode} (must be 0)\n{pristine.stdout}")
        bad += mutant.returncode != 1 or pristine.returncode != 0
    sys.path.insert(0, str(ROOT / "runtime" / "human"))
    import recorder as rec
    a = rec.mapper_text()
    rec.PAUSE_BINDS = {k: (k if "scrshot" in k else v) for k, v in rec.PAUSE_BINDS.items()}
    b = rec.mapper_text()
    print("== survivor 2: F12+P left on the screenshot")
    print("mapper_text identical with and without the mutation:", a == b)
    print([x for x in a.split("\n") if x.startswith("hand_scrshot")])
    bad += a != b
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
