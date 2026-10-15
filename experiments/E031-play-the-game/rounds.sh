#!/usr/bin/env bash
# Play N rounds as quick results (play.py round), stopping at the first round that stops on a screen it
# does not know (an injury, a new prompt). Prints one line per match and the round summary.
# Usage: bash experiments/E031-play-the-game/rounds.sh SESSION N [TEAM]
set -uo pipefail  # not -e: a round's failure is reported below, with its output
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
for i in $(seq "$2"); do
  out=$(python3 experiments/E031-play-the-game/play.py round "$1" --team "${3:-Holland}" -q 2>&1)
  echo "$out" | grep -E 'match:|board:.*FULL|round done|stopped|ERROR|timeout|watch prompt' | cut -c1-200
  echo "$out" | grep -q 'round done' || { echo "round $i did not finish"; echo "$out" | tail -30; exit 1; }
done
