#!/usr/bin/env bash
# heavy.sh: one or two heavy jobs at a time on this machine, across every agent, review and worktree (#318).
#
#   tools/harness/heavy.sh [--weight K] [--slots N] <name> -- <command> [args...]
#   tools/harness/heavy.sh --status
#
# A heavy job (a match run, a family run, check.py, the unit suite) takes one of N slots, then runs
# <command> in place of this script (same exit status, same stdin/stdout/stderr). With every slot taken
# it queues, first come first served, and says so on stderr:
#
#   heavy: <name>: waiting for a slot (k ahead)
#
# k is the number of jobs queued before this one. The slot is held for as long as the command, or any
# process that inherited it, runs; a job that dies, even by SIGKILL, frees its slot (the lock is a flock
# on a file, so the kernel releases it). A job started inside a heavy job (HARNESS_HEAVY_HELD is set) runs
# at once and takes no slot: the outer job already holds one, and a second would deadlock a full machine.
#
# --weight K holds K slots (a job that runs K processes at a time, as family.py --workers K). N is --slots,
# else $HARNESS_HEAVY_SLOTS, else harness.json's heavy.slots, else 2. The slots and the queue live in
# $HARNESS_HEAVY_DIR (default ~/.cache/goal2-heavy), shared by every worktree of the machine.
#
# While it waits it touches $HARNESS_HEAVY_QUEUE_FILE (when set) every poll: review.mjs sets it, and its
# idle limit does not count the time the reviewer's command spends in the queue (lib/opencode.mjs).
# $HARNESS_HEAVY_POLL is the poll interval in seconds (default 1); a queue entry whose job died is removed
# once it is $HARNESS_HEAVY_STALE_SEC (default 5) seconds old.
#
# Exit status: the command's; 2 for a refused command line (a weight over the slots, no command).

set -u

die() { echo "heavy: $*" >&2; exit 2; }

dir="${HARNESS_HEAVY_DIR:-$HOME/.cache/goal2-heavy}"
slots=""
weight=1
status=0
while [ $# -gt 0 ]; do
  case "$1" in
    --weight) [ $# -ge 2 ] || die "--weight needs a number"; weight="$2"; shift 2 ;;
    --slots) [ $# -ge 2 ] || die "--slots needs a number"; slots="$2"; shift 2 ;;
    --status) status=1; shift ;;
    --) break ;;
    -*) die "unknown option $1" ;;
    *) break ;;
  esac
done

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -z "$slots" ]; then slots="${HARNESS_HEAVY_SLOTS:-}"; fi
if [ -z "$slots" ]; then
  slots="$(node -e '
    try { const c = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")); process.stdout.write(String(c.heavy?.slots ?? "")); } catch {}
  ' "$here/../../harness.json" 2>/dev/null)"
fi
[ -n "$slots" ] || slots=2
case "$slots" in ''|*[!0-9]*|0) die "the number of slots must be a positive whole number; got '$slots'" ;; esac
case "$weight" in ''|*[!0-9]*|0) die "--weight must be a positive whole number; got '$weight'" ;; esac

mkdir -p "$dir/slots" "$dir/queue" || die "cannot create $dir"

if [ "$status" = 1 ]; then
  busy=0
  for ((i = 0; i < slots; i++)); do
    f="$dir/slots/$i"
    if [ -e "$f" ] && ! flock -n "$f" true 2>/dev/null; then
      busy=$((busy + 1)); echo "slot $i: busy: $(cat "$f" 2>/dev/null)"
    else
      echo "slot $i: free"
    fi
  done
  waiting=0
  for t in "$dir"/queue/*; do
    [ -e "$t" ] || continue
    if ! flock -n "$t" true 2>/dev/null; then waiting=$((waiting + 1)); echo "queued: $(basename "$t")"; fi
  done
  echo "heavy: $busy of $slots slots busy, $waiting queued"
  exit 0
fi

[ "$weight" -le "$slots" ] || die "--weight $weight is more than the $slots slots"
[ "${1:-}" = "--" ] && shift
[ $# -ge 2 ] || die "usage: heavy.sh [--weight K] <name> -- <command> [args...]"
name="$1"; shift
[ "${1:-}" = "--" ] || die "usage: heavy.sh [--weight K] <name> -- <command> [args...]"
shift
[ $# -ge 1 ] || die "no command after --"
case "$name" in *[!A-Za-z0-9._-]*|'') die "the job's name uses letters, digits, '.', '_' and '-' only; got '$name'" ;; esac

# Inside a heavy job: the outer job holds the slot.
if [ -n "${HARNESS_HEAVY_HELD:-}" ]; then exec "$@"; fi

poll="${HARNESS_HEAVY_POLL:-1}"
stale="${HARNESS_HEAVY_STALE_SEC:-5}"
queue_file="${HARNESS_HEAVY_QUEUE_FILE:-}"
ticket="$dir/queue/$(date +%s%N)-$$-$name"
exec {tfd}>"$ticket" || die "cannot create $ticket"
flock -n "$tfd" || die "cannot lock $ticket"
cleanup() { rm -f "$ticket"; }
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

# Tickets whose owner died (the file is not locked, and it is no longer new) are removed.
live_ahead() {
  local n=0 t b
  for t in "$dir"/queue/*; do
    [ -e "$t" ] || continue
    [ "$t" = "$ticket" ] && break
    if flock -n "$t" true 2>/dev/null; then
      b=$(stat -c %Y "$t" 2>/dev/null || echo 0)
      [ $(( $(date +%s) - b )) -gt "$stale" ] && rm -f "$t"
      continue
    fi
    n=$((n + 1))
  done
  echo "$n"
}

held=()      # file descriptors of the slots taken
heldno=()    # their numbers
take_slots() {
  local i fd
  held=(); heldno=()
  for ((i = 0; i < slots && ${#held[@]} < weight; i++)); do
    exec {fd}<>"$dir/slots/$i" || continue
    if flock -n "$fd"; then held+=("$fd"); heldno+=("$i"); else exec {fd}>&-; fi
  done
  if [ ${#held[@]} -lt "$weight" ]; then
    for fd in "${held[@]}"; do exec {fd}>&-; done
    held=(); heldno=()
    return 1
  fi
  return 0
}

start=$(date +%s)
last=""
while :; do
  ahead="$(live_ahead)"
  if [ "$ahead" = 0 ] && take_slots; then break; fi
  if [ "$ahead" != "$last" ]; then
    echo "heavy: $name: waiting for a slot ($ahead ahead)" >&2
    last="$ahead"
  fi
  if [ -n "$queue_file" ]; then touch "$queue_file" 2>/dev/null; fi
  sleep "$poll"
done

slotlist="${heldno[*]}"
for fd in "${held[@]}"; do
  printf 'job %s pid %s since %s\n' "$name" "$$" "$(date +%H:%M:%S)" > "/proc/self/fd/$fd" 2>/dev/null || true
done
waited=$(( $(date +%s) - start ))
if [ -n "$last" ]; then echo "heavy: $name: got slot $slotlist after $waited s" >&2; fi
rm -f "$ticket"
exec {tfd}>&-
trap - EXIT TERM INT
export HARNESS_HEAVY_HELD="$name" HARNESS_HEAVY_SLOTS_HELD="$slotlist"
exec "$@"
