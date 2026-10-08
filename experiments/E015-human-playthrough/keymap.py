#!/usr/bin/env python3
"""Observed text-screen/key bursts, not a causal claim about individual keys."""
import argparse
import hashlib
import json
from pathlib import Path


def build_map(states, events, t0, quiet=0.5):
    screens = {}
    samples = []
    for state in states:
        elapsed = state.get("entry", {}).get("elapsed_s")
        if state.get("error") or elapsed is None:
            continue
        text = state["screen_text"]
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        headline = next((row.strip() for row in text.splitlines() if row.strip()), "(blank)")
        screens[digest] = headline
        samples.append((t0 + elapsed, digest))
    samples.sort()
    bursts = []
    for event in sorted(events, key=lambda e: e["monotonic_s"]):
        if not bursts or event["monotonic_s"] > bursts[-1][-1]["monotonic_s"] + quiet:
            bursts.append([])
        bursts[-1].append(event)
    transitions = {}
    total, unmapped = 0, 0
    for burst in bursts:
        pressed = tuple(e["keysym"] for e in burst if e["event"] == "press")
        if not pressed:
            continue
        total += len(pressed)
        before = [digest for when, digest in samples if when < burst[0]["monotonic_s"]]
        after = [digest for when, digest in samples if when >= burst[-1]["monotonic_s"] + quiet]
        if not before or not after:
            unmapped += len(pressed)
            continue
        key = (before[-1], pressed, after[0])
        transitions[key] = transitions.get(key, 0) + 1
    rows = [{"screen": before, "headline": screens[before], "keys": list(keys),
             "after": after, "after_headline": screens[after], "count": count}
            for (before, keys, after), count in transitions.items()]
    return {"summary": f"screens: {len(screens)}, transitions: {len(rows)}, keys: {total}",
            "screens": screens, "transitions": rows, "unmapped_keys": unmapped,
            "method": "nearest snapshot before burst and first snapshot after quiet interval; ordered burst keys, not individual-key causality; text SHA256 UTF-8"}


def read_session(session, states=None):
    import extract
    session = Path(session)
    meta = json.loads((session / "meta.json").read_text())
    events = [json.loads(line) for line in (session / "keys.jsonl").read_text().splitlines()]
    if states is None:
        states = [extract.read_snapshot(session, e, []) for e in extract.read_index(session)[0]]
    return build_map(states, events, meta["monotonic_start_s"])


def table(result):
    lines = ["# Observed screen/key map", "", result["summary"], "",
             "Ordered bursts are associations between snapshots, not proof of individual-key causality.",
             "", "| Before (text digest) | Keys pressed | After (text digest) | Count |", "| --- | --- | --- | --- |"]
    for r in result["transitions"]:
        clean = lambda text: text.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {clean(r['headline'])} ({r['screen'][:12]}) | {clean(' '.join(r['keys']))} | {clean(r['after_headline'])} ({r['after'][:12]}) | {r['count']} |")
    lines.extend(["", f"Unmapped presses: {result['unmapped_keys']}", ""])
    return "\n".join(lines)


def main():
    import extract
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("session", type=Path)
    ap.add_argument("--scripted-keys", action="store_true", help="include raw keys of a scripted sitting only")
    a = ap.parse_args()
    result = read_session(a.session)
    # extract claims a NEW run id; an existing record is never edited.
    extract.main([str(a.session), "--countries", ""] + (["--scripted-keys"] if a.scripted_keys else []))
    print(result["summary"])
    print(table(result))


if __name__ == "__main__":
    main()
