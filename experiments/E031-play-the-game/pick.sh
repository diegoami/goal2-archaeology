#!/usr/bin/env bash
# Pick a pool player into the squad in place of a squad player, on the squad screen (select squad):
# Right (the pool), find IN, Enter, Left (the squad), find OUT, Enter. Prints the squad after.
# Usage: bash experiments/E031-play-the-game/pick.sh SESSION "IN NAME" "OUT NAME"
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
p=experiments/E031-play-the-game/play.py
python3 $p send "$1" Right -q
python3 $p find "$1" "$2" --max 90 -q
python3 $p send "$1" Return -q
python3 $p send "$1" Left -q
python3 $p find "$1" "$3" --max 40 -q
python3 $p send "$1" Return | sed -n 3,25p | grep -o '│[A-Z] [^│]*│.│' | tr '\n' ' '
echo
