#!/usr/bin/env python3
"""Build static/screens/catalogue.tsv from the committed E015 records.

    python3 tools/screens/build.py            rewrite the catalogue (byte-identical on a rerun)
    python3 tools/screens/build.py --check    exit 1 when the committed file differs from a rebuild

One row per screen kind and key. Every row has a source:
  screen          the key is named by a hint the screen itself prints; `quote` is that text and
                  `state` the record state it was read in (the quote occurs in that state's text);
  run:<id> state <n>
                  a mapped burst of the record (screen before, presses, screen after; T34's rules:
                  never a per-key cause); `state` n is the first state with the screen before, and
                  `to_state` the first with the screen after; `count` the bursts seen;
  owner           a hand row of static/screens/owner.tsv, the only hand rows;
  static:<path>:<line>  left for later tasks (code reading of the key handlers); none here.
A kind with no key found yet has one row with an empty key, whose source is its own rule text.
Nothing is invented: a hint row is an entry of HINTS below confirmed on a recorded screen.
"""
import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import identify  # noqa: E402

COLUMNS = ["kind", "key", "keysyms", "effect", "source", "quote", "state", "to_kind", "to_state", "count", "rule"]

# Records whose key bursts the catalogue counts: the owner's own sittings (T39a task file, Evidence:
# r0003 of 2026-10-07, r0007 of 2026-10-11, r0008 the 22 s false start of 2026-10-11). r0004-r0006
# are scripted acceptance sittings whose keys (a, b, c ...) test the recorder, not the game.
REAL_SITTINGS = ("E015-r0003", "E015-r0007", "E015-r0008")

# The screen's glyph or word for a key -> X keysym(s) the recorder's key log and xdotool use.
KEYSYMS = {
    "◄┘": "Return", "Esc": "Escape", "←→": "Left Right", "←→↑↓": "Left Right Up Down", "↑↓": "Up Down",
    "↑↓←→": "Up Down Left Right", "↓↑": "Up Down", "spacebar": "space", "INS": "Insert",
    "Y": "y", "N": "n", "Y N": "y n", "R": "r", "C": "c", "T": "t", "R,C": "r c", "F1": "F1", "F2": "F2",
    "F3": "F3", "F4": "F4", "F5": "F5", "F7": "F7", "F9": "F9", "F10": "F10", "Esc ◄┘": "Escape Return",
    "↑↓ Pgup Pgdn Home End": "Up Down Prior Next Home End", "any key": "(any)", "characters": "(typed)",
}

# (quote, key as the screen prints it, effect in the screen's own words, other text that must be on
# the same screen). A row is made for every kind with a recorded state whose text holds the quote
# and the other text. The key and the effect are copied from the screen, not interpreted.
HINTS = [
    ("(Y/N)", "Y N", "answer the question the screen asks", ""),
    ("Hit Y for yes, N for no", "Y", "yes", ""),
    ("Hit Y for yes, N for no", "N", "no", ""),
    ("Use ←→ to choose number", "←→", "choose number", ""),
    ("to choose number, ◄┘ to select", "◄┘", "select", ""),
    ("Use ←→↑↓ keys to browse", "←→↑↓", "browse", ""),
    ("then hit ◄┘ to select", "◄┘", "select", ""),
    ("use INS to", "INS", "swap between world and continental rankings", "continental"),
    ("spacebar-players", "spacebar", "players", ""),
    ("Type in characters (maximum 14)", "characters", "type in characters (maximum 14)", ""),
    ("◄┘-accept", "◄┘", "accept", ""),
    ("Esc-abort", "Esc", "abort", ""),
    ("Please enter name of saved game", "characters", "enter name of saved game", ""),
    ("hit any key", "any key", "(the screen says only: hit any key)", ""),
    ("PRESS ANY KEY", "any key", "(the screen says only: PRESS ANY KEY)", ""),
    ("F1help", "F1", "help", ""),
    ("F3load goal", "F3", "load goal", ""),
    ("F4load summary", "F4", "load summary", ""),
    ("F5print screen", "F5", "print screen", ""),
    ("F7save", "F7", "save", ""),
    ("F10quit", "F10", "quit", ""),
    ("Use ↑↓ to", "↑↓", "find option", "find option"),
    ("Hit ◄┘ to", "◄┘", "select option", "F1help"),
    ("Use ↑↓ to scroll", "↑↓", "scroll", ""),
    ("Hit ◄┘ to", "◄┘", "watch match", "watch match"),
    ("Hit ◄┘ for", "◄┘", "auto result", "auto result"),
    ("Esc-exit", "Esc", "exit", ""),
    ("spacebar-pause", "spacebar", "pause", ""),
    ("←→-speed", "←→", "speed", ""),
    ("Hit INS to turn automatic action replay", "INS", "turn automatic action replay OFF", "replay OFF"),
    ("Hit INS to turn automatic action replay", "INS", "turn automatic action replay ON", "replay ON"),
    ("Use ↑↓←→", "↑↓←→", "select option", "then ◄┘"),
    ("then ◄┘", "◄┘", "select option (after moving)", ""),
    ("↓↑-display", "↓↑", "display", ""),
    ("R-result", "R", "result", ""),
    ("spacebar-commentary", "spacebar", "commentary", ""),
    ("F9-♫", "F9", "♫", ""),
    ("Esc,◄┘-bench", "Esc ◄┘", "bench", ""),
    ("↑↓,Pgup,Pgdn,Home,End-view commentary", "↑↓ Pgup Pgdn Home End", "view commentary", ""),
    ("Esc-play", "Esc", "play", ""),
    ("F2-new name", "F2", "new name", ""),
    ("R,C-reposition", "R,C", "reposition", ""),
    ("T-tactics", "T", "tactics", ""),
    ("◄┘-take off this player", "◄┘", "take off this player", ""),
    ("◄┘-put on this player", "◄┘", "put on this player", ""),
    ("↓↑←→-select", "↑↓←→", "select", ""),
    ("◄┘-alter tactic", "◄┘", "alter tactic", ""),
    ("◄┘-change tactic", "◄┘", "change tactic", ""),
    ("◄┘-select", "◄┘", "select (captain)", "CAPTAIN"),
    ("C-computer select", "C", "computer select", ""),
    ("use ↑↓ to move", "↑↓", "move", ""),
]


# A prompt drawn over another screen leaves that screen's hints printed but not in force: such a
# kind lists only the hints of its own line.
OVERLAYS = {
    "country-select-name-entry": {"Type in characters (maximum 14)", "◄┘-accept", "Esc-abort"},
    "save-game-name-entry": {"Please enter name of saved game"},
    "quit-confirm": {"(Y/N)"},
    "save-game-prompt": {"(Y/N)"},
    "file-not-found-prompt": {"(Y/N)"},
    "squad-substitution-illegal": {"PRESS ANY KEY"},
    "match-summary-save-prompt": {"(Y/N)"},
    "match-watch-prompt": {"Hit Y for yes, N for no"},
}


def keysyms(key):
    return KEYSYMS.get(key, "")


def tsv(row):
    return "\t".join(str(row.get(c, "")) for c in COLUMNS)


def load_records():
    recs = []
    for path in common.record_paths():
        rec = common.read_record(path)
        rec["kinds"] = identify.identify_record(rec)
        recs.append(rec)
    return recs


def first_state(recs, kind, needs=()):
    """(run id, state) of the first record state of the kind whose text holds every phrase."""
    for rec in recs:
        for n, s in rec["states"].items():
            if rec["kinds"][n] == kind and s["text"] is not None:
                norm = common.normalize(s["text"])
                if all(common.normalize(p) in norm for p in needs):
                    return rec["run_id"], n
    return None


def screen_rows(recs, kinds):
    rows = []
    for kind, rule, parsed, _ in kinds:
        found = False
        for quote, key, effect, other in HINTS:
            if kind in OVERLAYS and quote not in OVERLAYS[kind]:
                continue
            where = first_state(recs, kind, [quote] + ([other] if other else []))
            if where is None:
                continue
            found = True
            rows.append({"kind": kind, "key": key, "keysyms": keysyms(key), "effect": effect,
                         "source": "screen", "quote": quote, "state": f"{where[0]} state {where[1]}",
                         "rule": rule})
        if not found:
            first_plus = next(p for sign, p in parsed if sign == "+")
            where = first_state(recs, kind, [first_plus])
            if where is None:
                print(f"build: kind {kind} occurs in no record", file=sys.stderr)
                continue
            rows.append({"kind": kind, "key": "", "keysyms": "", "effect": "no key known",
                         "source": "screen", "quote": first_plus, "state": f"{where[0]} state {where[1]}",
                         "rule": rule})
    return rows


def run_rows(recs, rule_of):
    """One row per (kind before, keys, kind after), over every record's mapped bursts. A burst is
    `screen before, presses in order, screen after`: the row says what was seen, not what a key
    caused (T34). Bursts whose screens no rule names are left out."""
    groups = {}
    for rec in recs:
        km = rec["keymap"]
        if not km or rec["run_id"] not in REAL_SITTINGS:
            continue
        by_digest = {}      # the key map names a screen by the SHA256 of its UTF-8 text (keymap.py)
        for n, s in rec["states"].items():
            if s["text"] is not None:
                by_digest.setdefault(hashlib.sha256(s["text"].encode("utf-8")).hexdigest(), n)
        for t in km["transitions"]:
            b, a = by_digest.get(t["screen"]), by_digest.get(t["after"])
            if b is None or a is None:
                continue
            kb, ka = rec["kinds"][b], rec["kinds"][a]
            if "unknown" in (kb, ka):
                continue
            key = (kb, " ".join(t["keys"]), ka)
            g = groups.setdefault(key, {"count": 0, "first": (rec["run_id"], b, a)})
            g["count"] += t["count"]
    rows = []
    for (kb, keys, ka), g in groups.items():
        run_id, b, a = g["first"]
        rows.append({"kind": kb, "key": keys, "keysyms": keys, "effect": f"burst: {kb} -> {ka}",
                     "source": f"run:{run_id} state {b}", "state": "", "to_kind": ka,
                     "to_state": f"{run_id} state {a}", "count": g["count"], "rule": rule_of[kb]})
    return rows


def owner_rows(rule_of):
    rows = []
    if common.OWNER.is_file():
        for n, line in enumerate(common.OWNER.read_text(encoding="utf-8").splitlines()):
            if n == 0 or not line.strip():
                continue
            kind, key, ks, effect = line.split("\t")
            rows.append({"kind": kind, "key": key, "keysyms": ks, "effect": effect, "source": "owner",
                         "rule": rule_of.get(kind, "")})
    return rows


def build():
    kinds = common.load_kinds()
    rule_of = {k[0]: k[1] for k in kinds}
    recs = load_records()
    order = {k[0]: i for i, k in enumerate(kinds)}
    rows = screen_rows(recs, kinds) + run_rows(recs, rule_of) + owner_rows(rule_of)
    rank = {"screen": 0, "owner": 2}
    rows.sort(key=lambda r: (order[r["kind"]], rank.get(r["source"], 1), r["source"], r["key"], r["effect"]))
    return "\n".join(["\t".join(COLUMNS)] + [tsv(r) for r in rows]) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    text = build()
    if a.check:
        if common.CATALOGUE.read_text(encoding="utf-8") != text:
            print("build: the committed catalogue differs from a rebuild", file=sys.stderr)
            return 1
        return 0
    common.CATALOGUE.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {common.CATALOGUE.relative_to(common.ROOT)}: {text.count(chr(10)) - 1} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
