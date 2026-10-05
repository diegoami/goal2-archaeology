#!/usr/bin/env python3
"""E007 (T16, Q009): what the player screen shows, its scale, and where each shown value comes from.

    python3 experiments/E007-q009-player-screen/summarise.py [runs/E007]

Reads every completed record of runs/E007: per player screen the text page (characters and attributes),
the player the screen names, that player's 20 bytes and the data-segment tables, all read from one
savestate. `playerscreen.parse` transcribes the screen; `model` evaluates the formulas of the listing
(`1771:42BC` and its callees, F008) on the record bytes and the tables; the two are compared value by
value over every transcribed player. A line says, per shown value: its name, its scale (numbers or
words, the range seen) and its source: a record field, a formula with the match count, or "not found".
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import playerscreen  # noqa: E402

HERE = Path(__file__).resolve().parent
RUNS = ROOT / "runs" / "E007"
SKILL_ROW_FIELD = "text screen 80x25 as the 4000 bytes B800:0000 holds them"
TABLE_RE = re.compile(r"DS:([0-9A-F]{4})\.\.([0-9A-F]{4}), (\d+) bytes")
STEP_LABEL = re.compile(r"^(player screen \d+ of the list)")


class Tables:
    """The data-segment ranges a record keeps, read by DS offset."""

    def __init__(self, ranges):
        self.ranges = ranges  # {lo: bytes}

    def byte(self, off):
        for lo, b in self.ranges.items():
            if lo <= off < lo + len(b):
                return b[off - lo]
        raise KeyError(f"DS:{off:04X} is in no range the record kept")

    def pstr(self, off, size):
        n = self.byte(off)
        return bytes(self.byte(off + 1 + i) for i in range(min(n, size - 1))).decode("cp437")


# ---- the model: the listing's formulas (F008 cites each) ------------------------------------------------

def height_inches(rec, n, t):
    """1771:2FAD: DS:0E46[+7] + DS:0E54[n mod 12]."""
    return t.byte(0x0E46 + rec[7]) + t.byte(0x0E54 + n % 12)


def two_footed(rec):
    """1771:3041: +5 + +2 = 0x1E."""
    return rec[5] + rec[2] == 0x1E


def foot_index(rec, n, t):
    """1771:3088: DS:0E60[14 * DS:0E7C[n mod 3] + +7]."""
    return t.byte(0x0E60 + 14 * t.byte(0x0E7C + n % 3) + rec[7])


def hardness_value(rec):
    """1771:2FFB: +5 - (bit 0 of +3), as a byte."""
    return (rec[5] - (rec[3] & 1)) & 0xFF


def leadership_value(rec):
    """1771:30D9: (+3 - +5) mod 8 (idiv, the remainder), halved when +1 < 0x15."""
    d = rec[3] - rec[5]
    v = d - 8 * int(d / 8)      # the remainder of idiv (sign of the dividend)
    return v // 2 if rec[1] < 0x15 and v >= 0 else v


def skill_bars(rec, t):
    """1771:3947: for i = 1..12, DS:6DCD[12 * +5 + DS:6D25[12 * +7 + i]] * (+4 + 1) div 256."""
    out = []
    for i in range(1, 13):
        cls = t.byte(0x6D25 + 12 * rec[7] + i)
        out.append(t.byte(0x6DCD + 12 * rec[5] + cls) * (rec[4] + 1) // 256)
    return out


def word(t, idx):
    return t.pstr(0x6EB4 + 16 * idx, 16)


def status_class(rec):
    """1771:42BC from `46E1`: the first test that holds (bit k of +0x10 is Pascal set element k + 1... the
    listing's `214B:0C57(k, +0x10)` is bit k - 1)."""
    bit = lambda k: (rec[0x10] >> (k - 1)) & 1  # noqa: E731
    if bit(8):
        return "suspended"
    if rec[0xE] == 0:
        return "injured"
    if bit(5):
        return "booked"
    if bit(6):
        return "sent off"
    if bit(3):
        return "substituted"
    return "ready"       # 1771:47CD..4845: ready to play / selected / on the bench, from DS:0C1E and 1771:3A82


def model(rec, n, t):
    """What the listing's formulas say the screen shows for the record, in playerscreen.parse's shape
    (the status as one of the listing's classes; the performance as its blank test)."""
    m = {"age": rec[1], "caps": int.from_bytes(rec[8:10], "little"), "goals": int.from_bytes(rec[10:12], "little"),
         "height_in": height_inches(rec, n, t),
         "bias": "two footed" if two_footed(rec) else t.pstr(0x0F2C + 6 * foot_index(rec, n, t), 6),
         "position": t.pstr(0x69B6 + 0x13 * rec[6], 0x13), "club_position": t.pstr(0x69B6 + 0x13 * rec[7], 0x13),
         "status": status_class(rec), "performance_blank": int.from_bytes(rec[0x12:0x14], "little") == 0x7FFF}
    m["skill_bars"] = skill_bars(rec, t)
    h, lead = hardness_value(rec), leadership_value(rec)
    fit_idx = t.byte(0x78D5 + (rec[0xD] if rec[0xE] else 0))
    m["hardness"] = (word(t, t.byte(0x78C4 + h)), h * 14 // 16)
    m["fitness"] = (word(t, fit_idx), rec[0xD] * 14 // 32 if rec[0xE] else 0)
    m["energy"] = (word(t, t.byte(0x78F6 + rec[0xE])), rec[0xE] * 14 // 32)
    m["morale"] = (word(t, t.byte(0x78A3 + min(rec[0xC], 0x20))), rec[0xC] * 14 // 32 if rec[0xC] < 0x20 else 0)
    m["leadership"] = (word(t, t.byte(0x7917 + lead)), lead * 14 // 7)
    return m


# ---- the records ----------------------------------------------------------------------------------------

def load(runs=RUNS):
    """[{run, step, shown, n, rec, tables, start_sha}] over every completed record, in order."""
    out = []
    for path in sorted(Path(runs).glob("E007-r*.json")):
        r = json.loads(path.read_text())
        if r["status"] != "completed":
            continue
        tables = Tables({int(m.group(1), 16): bytes.fromhex(o["value"]) for o in r["observations"]
                         if (m := TABLE_RE.search(o["field"])) and o["source"] == "memory"})
        steps = {}
        for o in r["observations"]:
            steps.setdefault(o["step"], []).append(o)
        for step in sorted(steps):
            raw = next((o for o in steps[step] if SKILL_ROW_FIELD in o["field"]), None)
            if raw is None:
                continue
            ident = next(o for o in steps[step] if "the player the screen names" in o["field"])
            rec = next((o for o in steps[step] if "the 20 bytes of player n's record" in o["field"]), None)
            m = re.match(r"n=(\d+|unresolved)", ident["value"])
            out.append({"run": r["run_id"], "step": step, "shown": playerscreen.parse(playerscreen.screen_of_raw(bytes.fromhex(raw["value"]))),
                        "n": int(m.group(1)) if m.group(1) != "unresolved" else None,
                        "rec": bytes.fromhex(rec["value"]) if rec else None, "tables": tables, "start": r["start_state"]["sha256"]})
    return out


def compare(p):
    """{shown value name: (shown, modelled)} for one transcribed player; None where the player is unresolved."""
    s, m = p["shown"], model(p["rec"], p["n"], p["tables"])
    pairs = {"name": None, "age": (s["age"], m["age"]), "caps": (s["caps"], m["caps"]), "goals": (s["goals"], m["goals"]),
             "height": (s["height_in"], m["height_in"]), "bias": (s["bias"], m["bias"] if m["bias"] == "two footed" else m["bias"] + " foot"),
             "position": (s["position"], m["position"]), "club position": (s["club_position"], m["club_position"]),
             "status": (status_class_of_text(s["status"]), m["status"]),
             "performance": (s["performance"] == "", m["performance_blank"])}
    for i, (label, bar) in enumerate(s["skills"].items()):
        pairs[f"skill {i + 1:2d} {label}"] = (bar, m["skill_bars"][i])
    for label, (w, bar) in ((k, (v["word"], v["bar"])) for k, v in s["panel"].items()):
        pairs[f"{label} word"] = (w, m[label][0])
        pairs[f"{label} bar"] = (bar, m[label][1])
    del pairs["name"]
    return pairs


def status_class_of_text(text):
    if text in ("suspended", "injured", "booked", "sent off", "substituted"):
        return text
    return "ready" if text in ("ready to play", "selected", "on the bench") else text


def scale(values):
    vs = list(values)
    if all(isinstance(v, int) for v in vs):
        return f"numbers {min(vs)}..{max(vs)}"
    if all(isinstance(v, bool) for v in vs):
        return f"blank in {sum(vs)} of {len(vs)}"
    c = Counter(vs)
    return f"words ({len(c)} seen): " + ", ".join(f"{w!r} x{n}" for w, n in sorted(c.items()))


SOURCES = {
    "age": "record field +1 (1771:42BC `4307`)",
    "caps": "record word +8 (`432F`)", "goals": "record word +0xA (`4355`)",
    "height": "formula: DS:0E46[+7] + DS:0E54[player number mod 12], inches (1771:2FAD)",
    "bias": "formula: `two footed` when +5 + +2 = 30 (1771:3041), else DS:0F2C + 6 * DS:0E60[14 * DS:0E7C[n mod 3] + +7] (1771:3088) + ` foot`",
    "position": "record byte +6 (name at DS:69B6 + 0x13 * +6; `4417`)", "club position": "record byte +7 (name at DS:69B6 + 0x13 * +7; `443D`)",
    "status": "record bytes +0x10 bits, +0xE = 0 (1771:42BC `4693`..`4845`); the class `ready` is three texts, which 1771:3A82 and DS:0C1E choose",
    "performance": "record word +0x12 = 0x7FFF is blank (1771:3827 `384B`)",
}


def source_of(name):
    if name in SOURCES:
        return SOURCES[name]
    if name.startswith("skill"):
        return "formula: DS:6DCD[12 * +5 + DS:6D25[12 * +7 + i]] * (+4 + 1) div 256 cells, i the row 1..12 (1771:3947)"
    word_src = {"hardness": "+5 - (+3 & 1) (1771:2FFB), word DS:6EB4 + 16 * DS:78C4[v], bar v * 14 div 16",
                "fitness": "+0xD (the word DS:6EB4 + 16 * DS:78D5[+0xD]; bar +0xD * 14 div 32; none when +0xE = 0)",
                "energy": "+0xE (word DS:78F6[+0xE], bar +0xE * 14 div 32)",
                "morale": "+0xC (word DS:78A3[min(+0xC, 0x20)], bar +0xC * 14 div 32 when +0xC < 0x20)",
                "leadership": "(+3 - +5) mod 8, halved when +1 < 0x15 (1771:30D9), word DS:7917[v], bar v * 14 div 7"}
    label = name.rsplit(" ", 1)[0]
    return f"formula over {word_src[label]}"


def main(argv=None):
    runs = Path(argv[0]) if argv else RUNS
    players = load(runs)
    if not players:
        print("no completed records")
        return 1
    ok = [p for p in players if p["n"] is not None and p["rec"] is not None]
    cols = Counter(p["rec"][0] for p in ok)
    gks = [p for p in ok if p["rec"][6] == 0]
    print(f"{len(players)} player screens in {len({p['run'] for p in players})} records; {len(ok)} resolved to a record; "
          f"countries (record byte +0): {sorted(cols)}; goalkeepers (+6 = 0): {len(gks)}; position codes (+6): {sorted({p['rec'][6] for p in ok})}")
    print(f"start states: {sorted({p['start'][:16] for p in players})}")
    labels = Counter(tuple(p["shown"]["skills"]) for p in players)
    panel = Counter(tuple(p["shown"]["panel"]) for p in players)
    print(f"skill labels (rows 11..22) identical on every screen: {len(labels) == 1}: {', '.join(next(iter(labels)))}")
    print(f"panel labels (rows 18..22) identical on every screen: {len(panel) == 1}: {', '.join(next(iter(panel)))}")
    pairs = [compare(p) for p in ok]
    print()
    print(f"{'shown value':<26} {'scale (over ' + str(len(ok)) + ' players)':<70} source")
    for name in pairs[0]:
        shown = [pr[name][0] for pr in pairs]
        match = sum(1 for pr in pairs if pr[name][0] == pr[name][1])
        print(f"{name:<26} {scale(shown):<70} {source_of(name)}; match {match}/{len(pairs)}")
    bad = [(p["run"], p["step"], k) for p, pr in zip(ok, pairs) for k, (a, b) in pr.items() if a != b]
    print(f"\nvalues that differ from the model: {len(bad)}")
    for b in bad[:20]:
        print("  ", b)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
