#!/usr/bin/env python3
"""#177: mutation check of VideoTests' video assertions, with no tracked file edited.

    python3 -B tests/mutations_177.py

The sitting is a separate process tree (play.sh -> recorder.py), so the mutation is a stand-in `ffmpeg` first on
PATH, in a temp dir, standing for a recorder whose video does not record: (a) writes nothing, (b) writes a fixed
file once and never grows it. The test must fail on each; it must pass with the real ffmpeg (control, run first).
Exits non-zero when a mutation survives or the control fails."""
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = "tests.test_human_keys.VideoTests"
SHIMS = {
    "no video written": 'trap "exit 0" TERM\nwhile :; do sleep 0.2; done\n',
    "video written once, never grows": ('trap "exit 0" TERM\nfor a; do out="$a"; done\n'
                                        'head -c 4096 /dev/zero > "$out"\nwhile :; do sleep 0.2; done\n'),
    "video grows, then is truncated at finalize": (
        'for a; do out="$a"; done\ntrap ": > \\"$out\\"; exit 0" TERM\n: > "$out"\n'
        'while :; do head -c 1000 /dev/zero >> "$out"; sleep 0.3; done\n'),
}


def run(path_prefix):
    env = dict(os.environ)
    if path_prefix:
        env["PATH"] = f"{path_prefix}:{env['PATH']}"
    return subprocess.run([sys.executable, "-B", "-m", "unittest", TEST], cwd=ROOT, env=env,
                          capture_output=True, text=True)


def main():
    bad = 0
    code = run(None).returncode
    print(f"control (real ffmpeg): {'passes' if code == 0 else 'FAILS'}")
    bad += code != 0
    for name, body in SHIMS.items():
        with tempfile.TemporaryDirectory() as d:
            shim = Path(d, "ffmpeg")
            shim.write_text("#!/bin/bash\n" + body)
            shim.chmod(shim.stat().st_mode | stat.S_IXUSR)
            result = run(d)
        code = result.returncode
        why = [l for l in result.stderr.splitlines() if l.startswith('AssertionError')]
        print(f"mutation {name!r}: {'killed' if code else 'SURVIVED'} {why}")
        bad += code == 0
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
