#!/usr/bin/env bash
# The penalty shoot-out order screen ("use ↑↓ then ◄┘ to select the order  Hit Esc to undo"): pick the
# players in the order given (find, Enter each). Usage: bash experiments/E031-play-the-game/order.sh S "A" "B" ...
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
s=$1; shift
for name in "$@"; do
  python3 experiments/E031-play-the-game/play.py find "$s" "$name" --max 15 -q
  python3 experiments/E031-play-the-game/play.py send "$s" Return -q
done
G2P_ROWS=12:25 G2P_COLS=60:80 python3 experiments/E031-play-the-game/play.py show "$s"
