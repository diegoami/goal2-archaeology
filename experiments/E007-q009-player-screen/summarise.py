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
    """The data-segment bytes the records kept, read by DS offset. The tables are the same in every
    record (one start state); `add` refuses a byte two records give differently, and the records of
    E007-r0001..r0003 kept fewer ranges than the later ones (README amendment 1), so the bytes are
    pooled over every record."""

    def __init__(self):
        self.mem = {}

    def add(self, lo, data, source=""):
        for i, b in enumerate(data):
            if self.mem.setdefault(lo + i, b) != b:
                raise ValueError(f"DS:{lo + i:04X} differs between records ({source})")

    def byte(self, off):
        try:
            return self.mem[off]
        except KeyError:
            raise KeyError(f"DS:{off:04X} is in no range the records kept") from None

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
    if d < 0:     # idiv's remainder takes the dividend's sign and the listing then halves it with an unsigned div: not modelled
        raise ValueError(f"+3 - +5 = {d} is negative; a new game's records have +3 >= 128 and +5 <= 16")
    v = d % 8
    return v // 2 if rec[1] < 0x15 else v


def skill_bars(rec, t):
    """1771:3947: for i = 1..12, DS:6DCD[12 * +5 + DS:6D25[12 * +7 + i]] * (+4 + 1) div 256."""
    out = []
    for i in range(1, 13):
        cls = t.byte(0x6D25 + 12 * rec[7] + i)
        out.append(t.byte(0x6DCD + 12 * rec[5] + cls) * (rec[4] + 1) // 256)
    return out


def skill_tables(t):
    """The two tables of `1771:3947` as the screen uses them: ({position +7: [class of row i for i = 1..12]},
    {profile +5: [base value of class c for c = 1..12]}); positions 0..13, profiles 0..16."""
    classes = {pos: [t.byte(0x6D25 + 12 * pos + i) for i in range(1, 13)] for pos in range(14)}
    profiles = {prof: [t.byte(0x6DCD + 12 * prof + c) for c in range(1, 13)] for prof in range(17)}
    return classes, profiles


def word(t, idx):
    return t.pstr(0x6EB4 + 16 * idx, 16)


def bit(value, k):
    """214B:0C57(k, value): Pascal set element k of a byte, bit k - 1 (`seg_214B_02.asm:0C57`)."""
    return (value >> (k - 1)) & 1


def status_class(rec):
    """1771:42BC from `46E1`: the first test that holds."""
    if bit(rec[0x10], 8):
        return "suspended"
    if rec[0xE] == 0:
        return "injured"
    if bit(rec[0x10], 5):
        return "booked"
    if bit(rec[0x10], 6):
        return "sent off"
    if bit(rec[0x10], 3):
        return "substituted"
    return "ready"       # 1771:47CD..4845: ready to play / selected / on the bench, from DS:0C1E and 1771:3A82


def status_text(rec, t):
    """The status text: the listing's class, and for `ready` the branch `47E6` takes when DS:0C1E is 0."""
    c = status_class(rec)
    if c != "ready":
        return c
    return "ready to play" if t.byte(0x0C1E) == 0 else "selected or on the bench"   # 1771:3A82's branch is not modelled


def tactics(rec, country, t):
    """The five rows of the tactics panel (1771:3BD3 rows 1..4, 1771:3B3F and 1771:3AE2 for `mark`): per row i,
    the player's own bit when +0xF bit i + 4 is set (and the text then ends in ` P`), else the country's byte
    +0x2D; the text index is bit i of that byte. A goalkeeper (+6 = 0) has its own words for rows 1 and 3.
    `mark` is the path DS:0C1E = 0 takes (`3D11`: `3B3F` at once); with DS:0C1E not 0 the listing (`3D1F`..`3E0A`)
    may print the name of a marked player first, which is not modelled (DS:0C1E is 0 in every record)."""
    out = {}
    for i, label in enumerate(("position", "possession", "passing", "tackling"), 1):
        own = bit(rec[0xF], i + 4)
        b = bit(rec[0xF] if own else country[0x2D], i)
        off = ((0x0EA6 if i == 1 else 0x0EC6) if rec[6] == 0 and i in (1, 3) else 0x6AA0 + 32 * i) + 16 * b
        out[label] = t.pstr(off, 16) + (" P" if own else "")
    if rec[6] < 2:
        out["mark"] = ""
    elif bit(rec[0x10], 7):
        out["mark"] = "Protect zone P"
    else:
        b = bit(country[0x2D], 8)
        out["mark"] = "Protect zone" if t.byte(0x0C1E) and b else t.pstr(0x0E90 + 11 * b, 11)
    return out


def model(rec, n, t):
    """What the listing's formulas say the screen shows for the record, in playerscreen.parse's shape
    (the status as one of the listing's classes; the performance as its blank test)."""
    m = {"age": rec[1], "caps": int.from_bytes(rec[8:10], "little"), "goals": int.from_bytes(rec[10:12], "little"),
         "height_in": height_inches(rec, n, t),
         "bias": "two footed" if two_footed(rec) else t.pstr(0x0F2C + 6 * foot_index(rec, n, t), 6),
         "position": t.pstr(0x69B6 + 0x13 * rec[6], 0x13), "club_position": t.pstr(0x69B6 + 0x13 * rec[7], 0x13),
         "status": status_text(rec, t), "performance_blank": int.from_bytes(rec[0x12:0x14], "little") == 0x7FFF}
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
    out, tables = [], Tables()
    records = [json.loads(p.read_text()) for p in sorted(Path(runs).glob("E007-r*.json"))]
    records = [r for r in records if r["status"] == "completed"]
    for r in records:
        for o in r["observations"]:
            m = TABLE_RE.search(o["field"])
            if m and o["source"] == "memory":
                tables.add(int(m.group(1), 16), bytes.fromhex(o["value"]), r["run_id"])
    for r in records:
        # a record is `full` when it holds the country record of each player and the tables up to DS:0EE5, the
        # last byte of the goalkeeper's tactic words (README amendment 2); the earlier records are replicated against
        full = any(int(m.group(1), 16) <= 0x0E40 and int(m.group(2), 16) >= 0x0EE5 for o in r["observations"] if (m := TABLE_RE.search(o["field"])))
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
            out.append({"run": r["run_id"], "arm": r["arm"], "full": full, "step": step, "raw": bytes.fromhex(raw["value"]),
                        "shown": playerscreen.parse(playerscreen.screen_of_raw(bytes.fromhex(raw["value"]))),
                        "n": int(m.group(1)) if m.group(1) != "unresolved" else None,
                        "named": json.loads(re.search(r"named=(\[[^\]]*\])", ident["value"]).group(1)),
                        "rec": bytes.fromhex(rec["value"]) if rec else None,
                        "country": next((bytes.fromhex(o["value"]) for o in steps[step] if "the record of the player's country" in o["field"]), None),
                        "tables": tables, "start": r["start_state"]["sha256"]})
    return out


def compare(p):
    """{shown value name: (shown, modelled)} for one transcribed player; None where the player is unresolved."""
    s, m = p["shown"], model(p["rec"], p["n"], p["tables"])
    pairs = {"name": None, "age": (s["age"], m["age"]), "caps": (s["caps"], m["caps"]), "goals": (s["goals"], m["goals"]),
             "height": (s["height_in"], m["height_in"]), "bias": (s["bias"], m["bias"] if m["bias"] == "two footed" else m["bias"].ljust(5) + " foot"),
             "position": (s["position"], m["position"]), "club position": (s["club_position"], m["club_position"]),
             "status": (s["status"], m["status"]),
             "performance": (s["performance"] or "blank", "blank" if m["performance_blank"] else "not blank"),
             "cards": (s["cards"] or "blank", "blank" if p["rec"][0x10] & 0x38 == 0 else "not blank")}
    for i, (label, bar) in enumerate(s["skills"].items()):
        pairs[f"skill {i + 1:2d} {label}"] = (bar, m["skill_bars"][i])
    for label, (w, bar) in ((k, (v["word"], v["bar"])) for k, v in s["panel"].items()):
        pairs[f"{label} word"] = (w, m[label][0])
        pairs[f"{label} bar"] = (bar, m[label][1])
    del pairs["name"]
    if p["country"] is not None:
        for label, text in tactics(p["rec"], p["country"], p["tables"]).items():
            pairs[f"tactics {label}"] = (s["tactics"][label], text)
    return pairs


def scale(values):
    vs = list(values)
    if all(isinstance(v, int) for v in vs):
        return f"numbers {min(vs)}..{max(vs)}"
    c = Counter(vs)
    return f"words ({len(c)} seen): " + ", ".join(f"{w!r} x{n}" for w, n in sorted(c.items()))


SOURCES = {
    "age": "record field +1 (1771:42BC `4307`)",
    "caps": "record word +8 (`432F`)", "goals": "record word +0xA (`4355`)",
    "height": "formula: DS:0E46[+7] + DS:0E54[player number mod 12], inches (1771:2FAD)",
    "bias": "formula: `two footed` when +5 + +2 = 30 (1771:3041), else the 5-character string at DS:0F2C + 6 * DS:0E60[14 * DS:0E7C[n mod 3] + +7] (1771:3088), then the template's ` foot`",
    "position": "record byte +6 (name at DS:69B6 + 0x13 * +6; `4417`)", "club position": "record byte +7 (name at DS:69B6 + 0x13 * +7; `443D`)",
    "status": "record bytes +0x10 bits and +0xE = 0 (1771:42BC `4693`..`4845`); `ready to play` when DS:0C1E is 0 (`47E6`); `selected` and `on the bench` (1771:3A82, DS:0C1E not 0) not seen",
    "performance": "record word +0x12 = 0x7FFF is blank (1771:3827 `384B`); a string of 1..9 characters otherwise, not seen here",
    "cards": "record byte +0x10 bits 3..5, one icon each when set (1771:42BC `4654`..`46B2`); never set here, so not exercised",
}


TACTIC_SOURCES = {
    "position": "bit 1 of +0xF if +0xF bit 5 is set (then ` P`), else of the country's byte +0x2D (R008): DS:6AA0 + 32 + 16 * bit; a goalkeeper reads DS:0EA6 + 16 * bit",
    "possession": "as `position` with bit 2 and +0xF bit 6: DS:6AA0 + 64 + 16 * bit",
    "passing": "as `position` with bit 3 and +0xF bit 7: DS:6AA0 + 96 + 16 * bit; a goalkeeper reads DS:0EC6 + 16 * bit",
    "tackling": "as `position` with bit 4 and +0xF bit 8: DS:6AA0 + 128 + 16 * bit",
    "mark": "blank when +6 < 2; `Protect zone P` when +0x10 bit 7; else DS:0E90 + 11 * (bit 8 of the country's byte +0x2D) (1771:3B3F, 1771:3AE2)",
}


def source_of(name):
    if name in SOURCES:
        return SOURCES[name]
    if name.startswith("tactics"):
        return "formula: " + TACTIC_SOURCES[name.split(" ", 1)[1]] + " (1771:3BD3)"
    if name.startswith("skill"):
        return "formula: DS:6DCD[12 * +5 + DS:6D25[12 * +7 + i]] * (+4 + 1) div 256 cells, i the row 1..12 (1771:3947)"
    word_src = {"hardness": "+5 - (+3 & 1) (1771:2FFB), word DS:6EB4 + 16 * DS:78C4[v], bar v * 14 div 16",
                "fitness": "+0xD (the word DS:6EB4 + 16 * DS:78D5[+0xD]; bar +0xD * 14 div 32; none when +0xE = 0)",
                "energy": "+0xE (word DS:78F6[+0xE], bar +0xE * 14 div 32)",
                "morale": "+0xC (word DS:78A3[min(+0xC, 0x20)], bar +0xC * 14 div 32 when +0xC < 0x20)",
                "leadership": "(+3 - +5) mod 8, halved when +1 < 0x15 (1771:30D9), word DS:7917[v], bar v * 14 div 7"}
    label = name.rsplit(" ", 1)[0]
    return f"formula over {word_src[label]}"


def alternative_counts(ok):
    """Bars matched by the formula with +4, and with +3 in its place (a different reading of the scale)."""
    c = {"+4": 0, "+3": 0, "total": 0, "reduced": sum(1 for p in ok if p["rec"][4] < p["rec"][3])}
    for p in ok:
        rec, t = p["rec"], p["tables"]
        shown = list(p["shown"]["skills"].values())
        swapped = bytearray(rec)
        swapped[4] = rec[3]
        for name, r in (("+4", rec), ("+3", bytes(swapped))):
            c[name] += sum(1 for a, b in zip(shown, skill_bars(r, t)) if a == b)
        c["total"] += len(shown)
    return c


def replication(players):
    """(identical, total): the screens of every record that is not `full` against the screen of a full record
    at the same list position and player (the same arm, the same place in the record), byte for byte (the
    text page, characters and attributes)."""
    full = {}
    for p in players:
        if p["full"]:
            full.setdefault(p["arm"], []).append(p["raw"])
    seen, same, total = {}, 0, 0
    for p in players:
        if not p["full"]:
            k = seen[p["run"]] = seen.get(p["run"], -1) + 1
            total += 1
            same += k < len(full.get(p["arm"], [])) and full[p["arm"]][k] == p["raw"]
    return same, total


def main(argv=None):
    args = [a for a in (argv or []) if a != "--tables"]
    runs = Path(args[0]) if args else RUNS
    players = load(runs)
    if not players:
        print("no completed records")
        return 1
    if "--tables" in (argv or []):
        classes, profiles = skill_tables(players[0]["tables"])
        print("DS:6D25 + 12 * position + i: the class (1..12) of the skill in row i = 1..12, per position +7 (0..13)")
        for pos, row in classes.items():
            print(f"  +7 = {pos:2d}: {row}")
        print("DS:6DCD + 12 * profile + c: the base value of class c = 1..12, per profile +5 (0..16)")
        for prof, row in profiles.items():
            print(f"  +5 = {prof:2d}: {row}")
        return 0
    ok = [p for p in players if p["full"] and p["n"] is not None and p["rec"] is not None and p["country"] is not None]
    cols = Counter(p["rec"][0] for p in ok)
    gks = [p for p in ok if p["rec"][6] == 0]
    print(f"{len(players)} player screens in {len({p['run'] for p in players})} records; the {len(ok)} screens of the full records (the player's country record and the tables to DS:0EE5) "
          f"({len({p['run'] for p in ok})} records) are analysed, all resolved to a player record; "
          f"countries (record byte +0): {sorted(cols)}; goalkeepers (+6 = 0): {len(gks)}; position codes (+6): {sorted({p['rec'][6] for p in ok})}")
    same, total = replication(players)
    print(f"the earlier records' screens at the same list positions: {same} of {total} screens identical to the byte")
    print(f"start states: {sorted({p['start'][:16] for p in players})}")
    labels = Counter(tuple(p["shown"]["skills"]) for p in players)
    panel = Counter(tuple(p["shown"]["panel"]) for p in players)
    tactic = Counter(tuple(p["shown"]["tactics"]) for p in players)
    print(f"skill labels (rows 11..22) identical on every screen: {len(labels) == 1}: {', '.join(next(iter(labels)))}")
    print(f"panel labels (rows 18..22) identical on every screen: {len(panel) == 1}: {', '.join(next(iter(panel)))}")
    print(f"tactics labels (rows 11..15) identical on every screen: {len(tactic) == 1}: {', '.join(next(iter(tactic)))}")
    pairs = [compare(p) for p in ok]
    print()
    print(f"{'shown value':<26} {'scale (over ' + str(len(ok)) + ' players)':<70} source")
    print(f"{'name':<26} {'initial and surname, 12 characters':<70} names array: [DS:9B70] + n, a space, 11 bytes at [DS:9B6C] + 11 n (1771:2E93); the number n is not shown; "
          f"the shown name names exactly one player on {sum(1 for p in ok if len(p['named']) == 1)}/{len(ok)} screens")
    for name in pairs[0]:
        shown = [pr[name][0] for pr in pairs]
        match = sum(1 for pr in pairs if pr[name][0] == pr[name][1])
        print(f"{name:<26} {scale(shown):<70} {source_of(name)}; match {match}/{len(pairs)}")
    alt = alternative_counts(ok)
    print()
    print("F007's inferred meanings against the screen:")
    print(f"  +1 (age, about 75%): the shown age equals byte +1 on {sum(1 for pr in pairs if pr['age'][0] == pr['age'][1])} of {len(pairs)} screens")
    print(f"  +4 (current ability, about 75%): all 12 skill bars scale with (+4 + 1): the formula with +4 matches {alt['+4']} of {alt['total']} bars; "
          f"with +3 in its place {alt['+3']}; players with +4 < +3: {alt['reduced']} of {len(ok)}")
    print(f"  +2 (peak age, about 70%) and +3 (potential, about 70%) are not shown: +2 enters only the two-footed test (+5 + +2 = 30: "
          f"{sum(1 for p in ok if two_footed(p['rec']))} players) and +4's value; +3 enters only +4, the hardness word (bit 0) and the leadership word ((+3 - +5) mod 8)")
    bad = [(p["run"], p["step"], k) for p, pr in zip(ok, pairs) for k, (a, b) in pr.items() if a != b]
    print(f"\nvalues that differ from the model: {len(bad)}")
    for b in bad[:20]:
        print("  ", b)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
