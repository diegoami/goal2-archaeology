"""Queue fresh integrated T63 ALL halves on the already merged main 53d7ef5 base."""
import os
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path("experiments/E036-match-port/out/T63")
STAMP = "all-rework-main53-cbbfb28"


def main():
    subprocess.run(["git", "merge-base", "--is-ancestor", "53d7ef5", "HEAD"], cwd=ROOT, check=True)
    for half in "ab":
        recorded = (ROOT / OUT / f"all-main53-{half}.args").read_text().splitlines()[1]
        parts = shlex.split(recorded)
        assert parts[:6] == ["tools/harness/heavy.sh", "--weight", "2", f"t63-all-main53-{half}",
                             "--", "python3"], parts[:6]
        parts = parts[:parts.index(">")]
        command = ["/usr/bin/python3", *parts[6:]]
        assert command[command.index("--ports") + 1] == "all"
        candidate = OUT / f"{STAMP}-{half}.jsonl"
        log = OUT / f"{STAMP}-{half}-run.txt"
        assert not (ROOT / candidate).exists() and not (ROOT / log).exists()
        command[command.index("--out") + 1] = str(candidate)
        unit = f"goal2-t63-all-main53-cbbfb28-{half}"
        shell = f"exec {shlex.join(command)} > {shlex.quote(str(log))} 2>&1"
        env = {
            "HARNESS_SESSION_FAMILY": "openai", "HARNESS_CLIENT": "codex", "HARNESS_HEAVY_SLOTS": "4",
            "HOME": "/home/diego", "PATH": os.environ["PATH"], "TMPDIR": "/tmp",
        }
        invocation = ["systemd-run", "--user", f"--unit={unit}", f"--working-directory={ROOT}",
                      "--property=StandardInput=null", *[f"--setenv={k}={v}" for k, v in env.items()],
                      "/bin/bash", "-c", shell]
        result = subprocess.run(invocation, capture_output=True, text=True, check=True)
        print(unit, result.stdout.strip(), "candidate", candidate, "log", log, flush=True)


if __name__ == "__main__":
    main()
