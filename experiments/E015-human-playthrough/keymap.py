#!/usr/bin/env python3
"""Observed text-screen/key bursts, not a causal claim about individual keys.

    python3 experiments/E015-human-playthrough/keymap.py <session>

Prints the summary line and the readable table; it writes nothing (one record per sitting, made
by extract.py, which carries this map; T34 review R5).

The rules (T34 review R1, R2; each pinned by tests/test_human_keys.py):
- A snapshot's screen was taken inside its request window: from the clock read before the save key
  was sent (`request_s`) to the end of the last send (`sent_s`) plus recorder.CAPTURE_MARGIN_S,
  never at staging (`elapsed_s`, up to seconds later). An index entry without `request_s` (a
  sitting recorded before T34's rework) has an open-ended window: every key before its staging is
  ambiguous.
- The snapshots, in request order, cut the key log into gaps. A key inside any window is
  ambiguous: its burst is unmapped. The keys of one gap form one burst when no two consecutive
  ones are more than the recorder's quiet interval apart; a gap holding two bursts is unmapped
  (a snapshot that should lie between them is missing), as is a burst whose bracketing snapshots
  are absent, unparsed, or a request that staged nothing (requests.jsonl, a skipped snapshot).
- A mapped burst is (screen of the snapshot before, its presses in order, screen of the snapshot
  after). Releases are part of the timeline, not of the keys listed.
- A span DOSBox-X was paused (pauses.jsonl, T39b) is no time to the quiet rule: the gap between
  two keys counts only the seconds the emulator ran.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "human"))
import recorder  # noqa: E402  (BURST_QUIET_S, CAPTURE_MARGIN_S: one constant, one place; R7)


def headline(text):
    """The first non-blank row that names no host path (T34 review R9: the DOS shell's first row
    is DOSBox-X's `mount c /home/...` echo). A POSIX path needs '/'; DOS paths use '\\'."""
    for row in text.splitlines():
        row = row.strip()
        if row and "/" not in row:
            return row
    return "(no headline)"


def window(entry, t0, margin):
    """(lo, hi) monotonic seconds in which the snapshot's screen was taken."""
    staged = t0 + entry["elapsed_s"] if entry.get("elapsed_s") is not None else math.inf
    if entry.get("request_s") is None:
        return -math.inf, staged
    sent = entry.get("sent_s")
    sent = entry["request_s"] if sent is None else sent
    return t0 + entry["request_s"], t0 + sent + margin


def paused_before(t, pauses):
    """The paused seconds before monotonic time `t`: the sum of each pause span's part before it."""
    return sum(max(0.0, min(t, hi) - lo) for lo, hi in pauses if lo < t)


def pause_spans(lines, end=math.inf):
    """(start, end) monotonic spans from pauses.jsonl's lines (T39b): each pause to the next
    resume; a pause the sitting ended in runs to `end`."""
    spans, start = [], None
    for line in sorted(lines, key=lambda x: x["monotonic_s"]):
        if line.get("event") == "pause" and start is None:
            start = line["monotonic_s"]
        elif line.get("event") == "resume" and start is not None:
            spans.append((start, line["monotonic_s"]))
            start = None
    if start is not None:
        spans.append((start, end))
    return spans


def build_map(states, events, t0, quiet=None, margin=None, requests=(), pauses=()):
    """`pauses`: (start, end) monotonic spans DOSBox-X was paused (T39b). A paused span is no
    time to the quiet-gap rule: two keys a pause separates are one burst when their gap less the
    paused seconds between them is within the quiet."""
    quiet = recorder.BURST_QUIET_S if quiet is None else quiet
    # injected keys are not the owner's: the recorder's own (`by: recorder` in the log, T39b) and
    # those the extraction names (mark_injected, rework round 1 R2)
    events = [e for e in events if not e.get("by")]
    margin = recorder.CAPTURE_MARGIN_S if margin is None else margin
    screens = {}
    samples = []                       # (lo, hi, digest or None)
    for state in states:
        entry = state.get("entry", {})
        lo, hi = window(entry, t0, margin)
        digest = None
        if not state.get("error") and state.get("screen_text") is not None:
            text = state["screen_text"]
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            screens[digest] = headline(text)
        samples.append((lo, hi, digest))
    for req in requests:
        if req.get("seq") is None:     # a request that staged nothing: a screen not seen
            samples.append(window(req, t0, margin) + (None,))
    samples.sort(key=lambda s: s[0])
    starts = [lo for lo, _, _ in samples]

    gaps = {}                          # gap index -> ordered events in it
    ambiguous = set()
    for event in sorted(events, key=lambda e: e["monotonic_s"]):
        t = event["monotonic_s"]
        gap = sum(1 for lo in starts if lo < t)
        gaps.setdefault(gap, []).append(event)
        if any(lo <= t <= hi for lo, hi, _ in samples):
            ambiguous.add(gap)
    transitions = {}
    total, unmapped = 0, 0
    for gap, gap_events in sorted(gaps.items()):
        # the quiet rule runs on emulated time: each key's clock less the paused seconds before it
        gap_events = [dict(e, monotonic_s=e["monotonic_s"] - paused_before(e["monotonic_s"], pauses))
                      for e in gap_events]
        bursts = []
        for event in gap_events:
            if not bursts or event["monotonic_s"] > bursts[-1][-1]["monotonic_s"] + quiet:
                bursts.append([])
            bursts[-1].append(event)
        pressed = [tuple(e["keysym"] for e in burst if e["event"] == "press") for burst in bursts]
        pressed = [p for p in pressed if p]
        if not pressed:
            continue
        n = sum(len(p) for p in pressed)
        total += n
        before = samples[gap - 1][2] if gap > 0 else None
        after = samples[gap][2] if gap < len(samples) else None
        if len(pressed) > 1 or gap in ambiguous or before is None or after is None:
            unmapped += n
            continue
        key = (before, pressed[0], after)
        transitions[key] = transitions.get(key, 0) + 1
    rows = [{"screen": before, "headline": screens[before], "keys": list(keys),
             "after": after, "after_headline": screens[after], "count": count}
            for (before, keys, after), count in transitions.items()]
    return {"summary": f"screens: {len(screens)}, transitions: {len(rows)}, keys: {total}",
            "screens": screens, "transitions": rows, "unmapped_keys": unmapped,
            "burst_quiet_s": quiet, "capture_margin_s": margin,
            "method": "snapshots in save-request order cut the key log into gaps; a gap's one burst "
                      "maps from the snapshot before to the snapshot after; a key inside a "
                      "snapshot's request window, two bursts in one gap, or a bracket that is "
                      "missing, unparsed or skipped leaves its presses unmapped; ordered burst "
                      "keys, not individual-key causality; screen = SHA256 of UTF-8 text"}


# [designed] How far a named injected key's logged press may lie from the time given for it: the
# record names it from its own keys.jsonl line (to the millisecond), so 10 ms is rounding, not a
# search. Extraction policy.
INJECTED_MATCH_S = 0.01


def mark_injected(events, injected, t0, tolerance=INJECTED_MATCH_S):
    """Copies of `events` with each named injected key marked (rework round 1, R2): `injected` is
    [(keysym, elapsed seconds, who)]; the one press of `keysym` within `tolerance` of t0 +
    elapsed, and the next release of that keysym, get `by: who`. The raw key log is never
    changed. A name that matches no press, or more than one, is an error: a known injection
    must land on a known key."""
    out = [dict(e) for e in events]
    for keysym, at, who in injected:
        hits = [i for i, e in enumerate(out) if e.get("keysym") == keysym
                and e.get("event") == "press" and abs(e["monotonic_s"] - (t0 + at)) <= tolerance]
        if len(hits) != 1:
            raise ValueError(f"injected {keysym}@{at}: {len(hits)} matching presses in keys.jsonl")
        out[hits[0]]["by"] = who
        for e in out[hits[0] + 1:]:
            if e.get("keysym") == keysym and e.get("event") == "release":
                e["by"] = who
                break
    return out


def read_session(session, states=None, injected=()):
    import extract
    session = Path(session)
    meta = json.loads((session / "meta.json").read_text())
    events = [json.loads(line) for line in (session / "keys.jsonl").read_text().splitlines()]
    requests = []
    if (session / "requests.jsonl").is_file():
        requests = [json.loads(line) for line in
                    (session / "requests.jsonl").read_text().splitlines() if line.strip()]
    pauses = []
    if (session / "pauses.jsonl").is_file():
        pauses = pause_spans([json.loads(line) for line in
                              (session / "pauses.jsonl").read_text().splitlines() if line.strip()])
    if states is None:
        states = [extract.read_snapshot(session, e, []) for e in extract.read_index(session)[0]]
    events = mark_injected(events, injected, meta["monotonic_start_s"])
    return build_map(states, events, meta["monotonic_start_s"],
                     quiet=meta.get("burst_quiet_s"), margin=meta.get("capture_margin_s"),
                     requests=requests, pauses=pauses)


def table(result):
    lines = ["# Observed screen/key map", "", result["summary"], "",
             "Ordered bursts are associations between snapshots, not proof of individual-key causality.",
             "", "| Before (text digest) | Keys pressed | After (text digest) | Count |", "| --- | --- | --- | --- |"]
    for r in result["transitions"]:
        clean = lambda text: text.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {clean(r['headline'])} ({r['screen'][:12]}) | {clean(' '.join(r['keys']))} | {clean(r['after_headline'])} ({r['after'][:12]}) | {r['count']} |")
    lines.extend(["", f"Unmapped presses: {result['unmapped_keys']}", ""])
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("session", type=Path)
    a = ap.parse_args(argv)
    result = read_session(a.session)
    print(result["summary"])
    print(table(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
