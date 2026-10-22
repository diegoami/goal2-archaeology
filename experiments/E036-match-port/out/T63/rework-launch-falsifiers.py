"""Queue the three final-source T63 reached-branch falsifiers under family.py's slots."""
import os
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path("experiments/E036-match-port/out/T63")
VARIANTS = ("depth-plus-one", "marking-no-copy", "keeper-no-state")


def main():
    for variant in VARIANTS:
        candidate = OUT / f"falsifier-rework-cbbfb28-{variant}-F40.jsonl"
        log = OUT / f"falsifier-rework-cbbfb28-{variant}-F40-run.txt"
        assert not (ROOT / candidate).exists() and not (ROOT / log).exists()
        command = ["/usr/bin/python3", "-B", "experiments/E036-match-port/family.py",
                   "--family", "F40", "--ports", "positioning", "--variant", f"positioning.{variant}",
                   "--workers", "2", "--time-limit", "3000", "--out", str(candidate)]
        shell = f"exec {shlex.join(command)} > {shlex.quote(str(log))} 2>&1"
        env = {
            "HARNESS_SESSION_FAMILY": "openai", "HARNESS_CLIENT": "codex", "HARNESS_HEAVY_SLOTS": "4",
            "HOME": "/home/diego", "PATH": os.environ["PATH"], "TMPDIR": "/tmp",
        }
        unit = f"goal2-t63-fz-cbbfb28-{variant}"
        invocation = ["systemd-run", "--user", f"--unit={unit}", f"--working-directory={ROOT}",
                      "--property=StandardInput=null", *[f"--setenv={k}={v}" for k, v in env.items()],
                      "/bin/bash", "-c", shell]
        result = subprocess.run(invocation, capture_output=True, text=True, check=True)
        print(unit, result.stdout.strip(), "candidate", candidate, "log", log, flush=True)


if __name__ == "__main__":
    main()
