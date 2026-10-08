#!/usr/bin/env bash
# T29: one command that records the owner's sitting (runtime/human/recorder.py).
#   bash runtime/human/play.sh --self-test        verify the release copy, write a config, exit
#   bash runtime/human/play.sh [--video] [--quit-after SECS]
# Run it from a graphical session (DISPLAY must point at the display the game window opens on).
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python3 "$ROOT/runtime/human/recorder.py" "$@"
