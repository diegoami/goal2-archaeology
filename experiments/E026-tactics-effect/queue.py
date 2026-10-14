#!/usr/bin/env python3
"""E026: run a queue of arm batches one after another in one process (one systemd unit).

    python3 -B experiments/E026-tactics-effect/queue.py base:0:30 e1:0:30 ...

Each item is arm:first:count; its log is experiments/E026-tactics-effect/out/<arm>-s<first>-<last>.jsonl
(arm.py refuses to overwrite one; an existing log makes the item be skipped, so a queue can be restarted)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arm  # noqa: E402


def main(argv):
    for item in argv:
        name, first, count = item.split(":")
        first, count = int(first), int(count)
        log = HERE / "out" / f"{name}-s{first}-{first + count - 1}.jsonl"
        if log.exists():
            print(f"skip {item}: {log.name} exists", flush=True)
            continue
        arm.main(["--arm", name, "--first", str(first), "--count", str(count), "--log", str(log)])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
