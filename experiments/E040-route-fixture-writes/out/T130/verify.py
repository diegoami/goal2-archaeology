"""T130 final-source receipt verifier: reads the committed logs and hashes the sources they were taken on; never runs an
engine. The sources are pinned below (route.py unchanged since d337a9a2, the test file since d063a95a; every log was
taken at or after d063a95a except controls-before.log, which is the pre-change run and is checked as a failure)."""
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCES = {
    "runtime/original_match/route.py": "97b3534c94d891a24eee5053895da268b05ee4d13fd7b2be6d034f9a29af2f41",
    "tests/test_play_action_entry.py": "4d6bb882e4514d364486a2cacb93c036663ab3c1173367de7930ff5526400967",
}
for name, want in SOURCES.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == want, f"{name} changed since the receipts"


def log(name):
    return (HERE / name).read_text()


def passed(name, tests):
    t = log(name)
    assert re.search(rf"^Ran {tests} tests", t, re.M) and re.search(r"^OK$", t, re.M) and t.rstrip().endswith("exit 0"), name


passed("controls-after.log", 15)            # Controls (14) + PortGap (1)
passed("existing-focused-v1.log", 52)       # route harness, live players, substitution control, entry config
passed("route-sealed-v1.log", 21)
for name in ("controls-before.log", "mutation-play_round_sp.log", "mutation-no_local_write.log",
             "mutation-action_sp.log", "mutation-transcribed_pre_step.log"):
    t = log(name)
    assert re.search(r"^FAILED \(", t, re.M) and t.rstrip().endswith("exit 1"), name
t = log("site-frame-v1.log")
assert "0x3ee2', '0x3eea', '0x3ff6', '0x77c2', '0x1'" in t and "('return', '000E:77CB')" in t
assert "SS:3FF0 [bp-6] = di (offset): 0x0006" in t
print("T130 receipts PASS: sources pinned; controls, existing, sealed pass; before and 4 mutations fail; site frame as recorded")
