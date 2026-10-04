#!/usr/bin/env python3
"""Play one GOAL2 match from the captain screen to full time, as a quick result or watched (T10, E004).

The match starts with the Enter on the captain screen. The arm decides the keys sent with it, in one
burst with no poll between (F004: then the keys reach the match's key poll `0791:9372` at its first
polls, whatever the host's timing):
- `quick`: Enter, r (F004's d3b; `r` is acted on at the first poll where the match clock runs,
  `0791:92FC`);
- `watched`: Enter, then Right five times, the game's own speed raised to its top (F001 M:match-speed
  raised it the same way): each Right lowers the delay byte [DS:A923]+0x3F by one, down to 0 (the key
  branch that decrements it and stops at 0, seg_0791_15.asm:785-791; E004's records read it at full
  time).
After that burst a key is sent only where the game waits for one: a screen that is stable (two equal
reads) and either shows `hit any key` on its last row before full time (half time), or is the team
screen (`location:`; Enter on its default option, ` play `). Any other screen is left alone, however long it
is stable (the kick-off and half-time pauses, the action-replay prompt, which ends by itself). The
match ends at the first stable screen whose commentary rows hold `FULL TIME`. Each read is a
savestate (I2), polled without sleeping; every key sent is logged with its moment and reason."""
import time

COMMENTARY_ROWS = (1, 2, 3)            # the three newest commentary lines, columns 31-66 of rows 1-3
COMMENTARY_COLS = slice(31, 66)
START_KEYS = {"quick": ("Enter", "r"), "watched": ("Enter",) + ("Right",) * 5}
# [designed] bound of one match, seconds from the starting keys to full time. Searched: F001
# M:match-speed (kick-off to FULL TIME 20.27, 20.35 s at cycles 30000, speed raised, half-time keys
# sent at once); E004's own records give each match's duration (summarise.py, `seconds`). The bound
# leaves room for the waits the game makes by itself (half-time and action-replay pauses).
MATCH_TIMEOUT = 300
# [designed] reads after a key during which the screen must change, else the key was not acted on
# and the match is aborted rather than the key sent again.
KEY_TAKEN_READS = 10


class MatchError(RuntimeError):
    """The match left the expected path: a key not acted on, or no full time within the bound."""


def commentary_rows(sc):
    rows = sc.lines()
    return [rows[r][COMMENTARY_COLS].strip() for r in COMMENTARY_ROWS]


def is_full_time(sc):
    return any("FULL TIME" in r for r in commentary_rows(sc))


def wants_key(sc):
    """Enter when the game waits for a key: `hit any key` (before full time) or the team screen."""
    if "location:" in sc.text():
        return "team screen"
    if "hit any key" in sc.lines()[-1] and not is_full_time(sc):
        return "hit any key"
    return None


def play(d, arm, on_read=None, timeout=MATCH_TIMEOUT, clock=time.monotonic):
    """Send the arm's starting keys, then poll until full time. `on_read(label, times, state)` is called
    for every read. Returns (keys, reads, seconds): keys = [(seconds since the start, key, reason)]."""
    if arm not in START_KEYS:
        raise ValueError(f"unknown arm {arm!r}")
    keys = []
    t0 = clock()
    d.keys(*START_KEYS[arm])
    keys.extend((0.0, k, "starting burst, no poll between") for k in START_KEYS[arm])
    d.log(f"match {arm}: starting keys {' '.join(START_KEYS[arm])} sent in one burst")
    prev, reads, waiting_since = None, 0, None
    while clock() - t0 < timeout:
        times, state, _ = d.read()
        reads += 1
        sc = state.screen()
        if on_read:
            on_read(f"match read {reads}", times, state)
        dg = sc.digest()
        stable = dg == prev
        prev = dg
        if waiting_since is not None:
            if dg != waiting_since[0]:
                waiting_since = None
            elif reads - waiting_since[1] > KEY_TAKEN_READS:
                raise MatchError(f"key {keys[-1][1]} ({keys[-1][2]}) not acted on within {KEY_TAKEN_READS} reads")
            else:
                continue
        if not stable:
            continue
        if is_full_time(sc):
            d.log(f"match {arm}: full time after {reads} reads")
            return keys, reads, round(clock() - t0, 2)
        why = wants_key(sc)
        if why:
            d.keys("Enter")
            keys.append((round(clock() - t0, 2), "Enter", why))
            d.log(f"match {arm}: Enter ({why})")
            waiting_since = (dg, reads)
    raise MatchError(f"no full time within {timeout}s ({reads} reads)")
