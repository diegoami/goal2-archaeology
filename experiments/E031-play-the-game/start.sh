#!/usr/bin/env bash
# Start a play session's server as its own systemd user unit (CLAUDE.md "Monitoring" rule 9), and wait
# until it serves. Usage: bash experiments/E031-play-the-game/start.sh SESSION [serve options...]
# The unit is goal2-play-SESSION; its output goes to scratch/play-SESSION.log. Stop it with
# `play.py stop SESSION` (the server terminates its DOSBox-X and Xvfb), or
# `systemctl --user stop goal2-play-SESSION` (SIGTERM: the same clean-up).
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
s=$1; shift
mkdir -p scratch
log=$PWD/scratch/play-$s.log
: > "$log"
systemd-run --user --unit="goal2-play-$s" --collect -E PATH="$PATH" -p WorkingDirectory="$PWD" \
  -p StandardInput=null -p StandardOutput=file:"$log" -p StandardError=file:"$log" \
  /usr/bin/python3 experiments/E031-play-the-game/play.py serve "$s" "$@"
for _ in $(seq 60); do
  grep -q serving "$log" && { cat "$log"; exit 0; }
  systemctl --user is-active --quiet "goal2-play-$s" || break
  sleep 1
done
cat "$log"; exit 1
