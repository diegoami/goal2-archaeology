#!/usr/bin/env bash
# T29: one command that records the owner's sitting (runtime/human/recorder.py).
#   bash runtime/human/play.sh --self-test        verify the release copy, write a config, exit
#   bash runtime/human/play.sh [play] [--scale N] [--cycles N] [--cadence SECS] [--video] [--quit-after SECS] [--load FILE.GL | --fresh]
#                                                  no subcommand: play; the newest saved game (.GL)
#                                                  of the previous sessions is copied unless
#                                                  --load names one or --fresh asks for none;
#                                                  --scale 1..3 (default 1) sizes the game window;
#                                                  --cycles N|max|auto (default 8000, a 1990s PC) sets the CPU speed;
#                                                  --cadence SECS (default 5) sets the snapshot interval
# Run it from a graphical session (DISPLAY must point at the display the game window opens on).
set -eu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python3 "$ROOT/runtime/human/recorder.py" "$@"
