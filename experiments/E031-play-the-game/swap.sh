#!/usr/bin/env bash
# On the squad screen: swap two squad players (Enter on A, Enter on B), e.g. one of the eleven with a
# substitute. Prints the eleven after. Usage: bash experiments/E031-play-the-game/swap.sh SESSION "A" "B"
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
p=experiments/E031-play-the-game/play.py
python3 $p find "$1" "$2" --max 40 -q
python3 $p send "$1" Return -q
python3 $p find "$1" "$3" --max 40 -q
python3 $p send "$1" Return | sed -n 3,14p | grep -o '│[A-Z] [^│]*│.│' | tr '\n' ' '
echo
