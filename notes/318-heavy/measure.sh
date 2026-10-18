#!/usr/bin/env bash
# Measurements behind the defaults of tools/harness/heavy.sh (#318): the poll interval and the stale-ticket age.
#
#   notes/318-heavy/measure.sh poll    CPU a waiting job spends, and the delay between a slot freeing and the waiter
#                                      starting, at several poll intervals
#   notes/318-heavy/measure.sh window  the longest gap between a queue ticket being created and locked, with and
#                                      without every core busy (what the stale-ticket age must exceed)
#
# Output is raw lines, one per measurement (the holder is 'sleep 6' and the waiter waits about 5 s); the committed logs are in this folder (never overwritten).
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
heavy="$here/../../tools/harness/heavy.sh"

case "${1:-}" in
poll)
  # per poll interval, 6 repetitions: a holder frees the only slot 6 s after it started; a waiter queues behind it
  # starting at a random fraction of a second (the poll's phase against the freeing is random in real use)
  for poll in 2 1 0.5 0.25 0.1; do
    for rep in 1 2 3 4 5 6; do
      dir="$(mktemp -d)"
      export HARNESS_HEAVY_DIR="$dir" HARNESS_HEAVY_SLOTS=1 HARNESS_HEAVY_POLL="$poll"
      "$heavy" holder -- sh -c 'date +%s%N > "$0"; exec sleep 6' "$dir/held" &
      sleep "0.$((RANDOM % 900 + 100))"
      /usr/bin/time -f "cpu_user=%U cpu_sys=%S wall=%e" -o "$dir/cpu" \
        "$heavy" waiter -- sh -c 'date +%s%N > "$0"' "$dir/started" 2>/dev/null &
      wait
      started="$(cat "$dir/started")"
      t_free=$(( $(cat "$dir/held") + 6000000000 ))
      echo "poll=$poll rep=$rep $(cat "$dir/cpu") wake_delay_ms=$(( (started - t_free) / 1000000 ))"
      rm -rf "$dir"
    done
  done
  ;;
window)
  dir="$(mktemp -d)"
  run() {
    local worst=0 n=2000 i t0 t1 d
    for ((i = 0; i < n; i++)); do
      t0=$EPOCHREALTIME
      exec {fd}>"$dir/t$i"
      flock -n "$fd"
      t1=$EPOCHREALTIME
      exec {fd}>&-
      d=$(( ${t1/./} - ${t0/./} ))
      [ "$d" -gt "$worst" ] && worst=$d
    done
    echo "$1 tickets=$n worst_create_to_lock_us=$worst"
  }
  run idle
  pids=()
  for ((i = 0; i < $(nproc); i++)); do ( while :; do :; done ) & pids+=($!); done
  run "all_cores_busy(nproc=$(nproc))"
  kill "${pids[@]}" 2>/dev/null
  wait 2>/dev/null
  rm -rf "$dir"
  ;;
*)
  echo "usage: measure.sh poll|window" >&2
  exit 2
  ;;
esac
