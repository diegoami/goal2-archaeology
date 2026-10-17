#!/usr/bin/env python3
"""E036 (T57): the record of one match, its grammar, and the digests it holds, in one place.

family.py writes one JSON line per match and compare.py reads every line with `loads` and `validate` below, to the
leaves, before it compares anything: a record that does not conform makes the log MALFORMED (compare.py exit 2), so
missing or mangled evidence is neither a match nor a caught falsifier. The classes of E032's review (PR 243,
rounds 1-5) are the grammar's rules:
- JSON is read strictly (`loads`): NaN/Infinity tokens, numbers that overflow to infinity and duplicate keys in an
  object are refused; a log is UTF-8 without a byte-order mark;
- every string pattern is matched against the WHOLE string (re.fullmatch) with ASCII-only classes ([0-9], [0-9a-f]);
- integers are ints, never booleans nor floats; floats are finite and not -0.0; every number has a range;
- the keys of every object are closed: a missing key and an unknown key are both refused; a container is checked
  down to its contents (a container's length is not enough);
- evidence is all present or all null; a completed match has all of it.

A record (REQUIRED below; nothing else):
  id                family "/" name, equal to a match a family file declares
  family            the family's name
  spec_sha256       the digest of the match's declaration (families.py `spec_sha256`): the fixture, the seed, the
                    edits, the answer policy and its code; compare.py checks it against the declared match
  image_sha256      the start image's SHA-256 (assets.REFERENCE)
  kit               the kit's version ("2")
  mask              the declared mask the digests below were taken over: [] (nothing masked) or sorted, disjoint
                    [space, start, length], space "DS" (an offset in the data segment) or "P" (a program-relative
                    linear address: the linear address less 16 * the load segment)
  error             null, or one line of clean ASCII text (the exception's class and its first line)
  stopped_at_board  true when the full-time board was reached
  strays            the contexts of decisions the match's answer policy does not declare (empty when completed)
  cpu_s, wall_s     finite numbers 0..1e6
  score             [0..255, 0..255]
  ticks             1..1_000_000
  draws             {count, digest, per_minute}: every main-RNG write [minute, sub-tick, old, new] from the captain
                    prompt to the board (record_draws); `digest` the kit's; `per_minute` one [minute, count, digest]
                    per run of writes at one minute (the clock is set back for extra time, so a minute can recur),
                    the counts adding up to `count`
  board             the board's raw statistics (ten rows, [team 0, team 1]), bars (two rows of two words), the man of
                    the match (a player word), the final score bytes, the seed word and the board screen's digest
  templates         the commentary's template ids (0..66) with their counts; no text
  result_sha256     the result's digest without the screen (`result_digest`)
  events            {count, sha256}: the events' digest (`events_digest`)
  decisions         [[minute, context], ...] in the order the original asked
  after             after the post-match update: the main seed word, one digest per 1 KiB of DS, and one digest per
                    1 KiB of each of RANGES (the record arrays, the competition tables, the pitch picture and the
                    rest a match writes outside the screen), taken over the mask
  counts            the executions of each --count address ({} without --count)
The evidence fields (score .. after) are all null when the match did not reach its result (an error)."""
import hashlib
import json
import math
import re

KIT_VERSION_PATTERN = re.compile(r"[0-9]{1,3}")
DIGEST = re.compile(r"[0-9a-f]{64}")
ADDRESS = re.compile(r"[0-9A-F]{4}:[0-9A-F]{4}")
RECORD_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,15}/[A-Za-z0-9][A-Za-z0-9._-]{0,47}")
FAMILY_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,15}")
TEMPLATE_ID = re.compile(r"0|[1-9][0-9]{0,2}")
ERROR_TEXT = re.compile(r"[\x21-\x7e](?:[\x20-\x7e]{0,198}[\x21-\x7e])?")     # one line, printable ASCII, no edge blanks
CONTEXTS = ("half_time", "substitution", "pause", "extra_time", "shootout_order")   # match.py `decision` contexts
STAT_NAMES = ("corners", "free_kicks", "penalties", "shots", "on_target", "saves", "fouls", "bookings", "red_cards",
              "injuries")                                                          # match.py STAT_NAMES
N_TEMPLATES = 67                       # match.py/image.py: the game's commentary templates
DS_SIZE, BLOCK = 0x10000, 1024         # one digest per 1 KiB of DS
DS_BLOCKS = DS_SIZE // BLOCK
# The ranges a match writes outside DS and the screen, as program-relative linear spans (start, length), each
# digested per 1 KiB. FOUND by a write watch over 18 matches that cover the families' paths
# (out/T57/ranges-20261017.json, family.py --find-ranges; notes/T57.md says what each is). family.py also checks, at the
# end of every match, that no byte outside DS, these ranges and the screen's three buffers has changed, so a range the
# sample missed is an error in the record and not a silent gap.
RANGES = {
    "records": (262990, 93648),         # the country, player, manager, game and fixture arrays (DS:A917 .. A92B + 8n)
    "w5c8a0": (379040, 1776),           # small writes at a fixed stride; DS:7C4C points into it
    "w5eb30": (387888, 64),             # 64 bytes that three of the kind-200 matches change (notes/T57.md)
    "pitch_background": (388368, 4016),     # DS:7C1E's block: the pitch picture's background copy, which 8E24
}                                           # restores cells from (E032 notes), with its 6-byte header and tail
# The 1 KiB blocks of DS that only the screen's text buffers carry (DS:A96E and DS:A972 point at the two 4000-byte
# buffers from DS:ED10; block 59 is the first that holds any of it): compare.py --no-screen leaves them out.
SCREEN_DS_BLOCKS = (59, 60, 61, 62, 63)
MASK_SPACES = ("DS", "P")
P_SIZE = 0x110000                      # the guest memory the kit maps (machine.py MEM_SIZE)


class SchemaError(ValueError):
    pass


# ---- strict JSON ------------------------------------------------------------------------------------
def _constant(token):
    raise SchemaError(f"the JSON token {token} is not a finite number")


def _float(text):
    v = float(text)
    if not math.isfinite(v):
        raise SchemaError(f"the number {text} is not finite")
    return v


def _object(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise SchemaError(f"the key {k!r} appears twice in one object")
        seen.add(k)
    return dict(pairs)


def loads(text):
    """json.loads without NaN/Infinity tokens, overflowing numbers or duplicate keys."""
    return json.loads(text, parse_constant=_constant, parse_float=_float, object_pairs_hook=_object)


def dumps(record):
    """One line of strict JSON (no NaN/Infinity), the form `loads` reads back."""
    return json.dumps(record, allow_nan=False)


def read_log(path):
    """The lines of a log as records, in file order. UTF-8 without a byte-order mark; blank lines are skipped; each
    line strict JSON and a valid record. Raises SchemaError (the file's name and line in the message)."""
    try:
        with open(path, "rb") as f:
            text = f.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SchemaError(f"{path}: {e}")
    if text.startswith("\ufeff"):
        raise SchemaError(f"{path}: starts with a byte-order mark")
    if text and not text.endswith("\n"):
        raise SchemaError(f"{path}: ends with an incomplete line (a run stopped mid-write?)")
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        try:
            r = loads(line)
        except (ValueError, RecursionError) as e:
            raise SchemaError(f"{path}:{n}: not strict JSON ({e})")
        try:
            validate(r)
        except SchemaError as e:
            raise SchemaError(f"{path}:{n}: {e}")
        out.append(r)
    return out


# ---- value grammar ----------------------------------------------------------------------------------
def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _int(v, lo, hi, path):
    if not is_int(v) or not lo <= v <= hi:
        raise SchemaError(f"{path}: {v!r} is not an integer in {lo}..{hi}")


def _num(v, lo, hi, path):
    ok = isinstance(v, (int, float)) and not isinstance(v, bool)
    if ok and isinstance(v, float):
        ok = math.isfinite(v) and not (v == 0 and math.copysign(1, v) < 0)
    if not ok or not lo <= v <= hi:
        raise SchemaError(f"{path}: {v!r} is not a finite number in {lo}..{hi}")


def _str(v, pattern, path):
    if not isinstance(v, str) or not pattern.fullmatch(v):
        raise SchemaError(f"{path}: {v!r} does not match {pattern.pattern!r} as a whole")


def _keys(d, want, path):
    if not isinstance(d, dict):
        raise SchemaError(f"{path}: not an object")
    if set(d) != set(want):
        raise SchemaError(f"{path}: keys {sorted(d)} are not {sorted(want)}")


def _list(v, path, size=None):
    if not isinstance(v, list) or (size is not None and len(v) != size):
        raise SchemaError(f"{path}: not a list" + (f" of {size}" if size is not None else ""))


def _pair(v, lo, hi, path):
    _list(v, path, 2)
    for i, x in enumerate(v):
        _int(x, lo, hi, f"{path}[{i}]")


# ---- the record ---------------------------------------------------------------------------------------
REQUIRED = ("id", "family", "spec_sha256", "image_sha256", "kit", "mask", "error", "stopped_at_board", "strays",
            "cpu_s", "wall_s", "score", "ticks", "draws", "board", "templates", "result_sha256", "events",
            "decisions", "after", "counts")
EVIDENCE = ("score", "ticks", "draws", "board", "templates", "result_sha256", "events", "decisions", "after")


def is_completed(r):
    """For a record that passed validate: a match that reached the full-time board with no error and no stray
    decision."""
    return r["error"] is None and r["stopped_at_board"] is True and not r["strays"]


def validate_mask(mask, path="mask"):
    """A mask: [] or a sorted list of disjoint [space, start, length] within its space."""
    _list(mask, path)
    prev = {}
    for i, s in enumerate(mask):
        p = f"{path}[{i}]"
        _list(s, p, 3)
        if not isinstance(s[0], str) or s[0] not in MASK_SPACES:
            raise SchemaError(f"{p}[0]: {s[0]!r} is not one of {MASK_SPACES}")
        size = DS_SIZE if s[0] == "DS" else P_SIZE
        _int(s[1], 0, size - 1, p + "[1]")
        _int(s[2], 1, size - s[1], p + "[2]")
        if s[0] in prev and s[1] < prev[s[0]]:
            raise SchemaError(f"{p}: the mask is not sorted and disjoint")
        prev[s[0]] = s[1] + s[2]


def validate(r):
    """Every field of the record, to its leaves. Raises SchemaError."""
    if not isinstance(r, dict):
        raise SchemaError("the record is not an object")
    _keys(r, REQUIRED, "record")
    _str(r["id"], RECORD_ID, "id")
    _str(r["family"], FAMILY_NAME, "family")
    if r["id"].split("/")[0] != r["family"]:
        raise SchemaError(f"id {r['id']!r} is not in family {r['family']!r}")
    _str(r["spec_sha256"], DIGEST, "spec_sha256")
    _str(r["image_sha256"], DIGEST, "image_sha256")
    _str(r["kit"], KIT_VERSION_PATTERN, "kit")
    validate_mask(r["mask"])
    if r["error"] is not None:
        _str(r["error"], ERROR_TEXT, "error")
    if not isinstance(r["stopped_at_board"], bool):
        raise SchemaError(f"stopped_at_board: {r['stopped_at_board']!r} is not a boolean")
    _list(r["strays"], "strays")
    for i, s in enumerate(r["strays"]):
        if not isinstance(s, str) or s not in CONTEXTS:
            raise SchemaError(f"strays[{i}]: {s!r} is not one of {CONTEXTS}")
    _num(r["cpu_s"], 0, 1e6, "cpu_s")
    _num(r["wall_s"], 0, 1e6, "wall_s")
    c = r["counts"]
    if not isinstance(c, dict):
        raise SchemaError("counts: not an object")
    for k, v in c.items():
        _str(k, ADDRESS, "counts key")
        _int(v, 0, 10 ** 12, f"counts[{k!r}]")
    if all(r[k] is None for k in EVIDENCE):
        if is_completed(r):
            raise SchemaError("a completed record without its evidence")
        return
    if r["error"] is not None:
        raise SchemaError("evidence beside an error")
    validate_evidence(r)


def validate_evidence(r):
    _pair(r["score"], 0, 255, "score")
    _int(r["ticks"], 1, 1_000_000, "ticks")
    d = r["draws"]
    _keys(d, ("count", "digest", "per_minute"), "draws")
    _int(d["count"], 1, 100_000_000, "draws.count")
    _str(d["digest"], DIGEST, "draws.digest")
    _list(d["per_minute"], "draws.per_minute")
    total = 0
    for i, row in enumerate(d["per_minute"]):
        p = f"draws.per_minute[{i}]"
        _list(row, p, 3)
        _int(row[0], 0, 0xFFFF, p + "[0]")
        _int(row[1], 1, 100_000_000, p + "[1]")
        _str(row[2], DIGEST, p + "[2]")
        total += row[1]
    if total != d["count"]:
        raise SchemaError(f"draws.per_minute counts add up to {total}, not {d['count']}")
    b = r["board"]
    _keys(b, ("statistics", "bars", "man_of_the_match", "final_score", "seed", "screen_sha256"), "board")
    _keys(b["statistics"], STAT_NAMES, "board.statistics")
    if list(b["statistics"]) != list(STAT_NAMES):
        raise SchemaError(f"board.statistics: rows {list(b['statistics'])} are not in the board's order {list(STAT_NAMES)}")
    for n in STAT_NAMES:
        _pair(b["statistics"][n], 0, 255, f"board.statistics.{n}")
    _list(b["bars"], "board.bars", 2)
    for i, row in enumerate(b["bars"]):
        _pair(row, 0, 0xFFFF, f"board.bars[{i}]")
    _int(b["man_of_the_match"], 0, 0xFFFF, "board.man_of_the_match")
    _pair(b["final_score"], 0, 255, "board.final_score")
    _int(b["seed"], 0, 0xFFFF, "board.seed")
    _str(b["screen_sha256"], DIGEST, "board.screen_sha256")
    t = r["templates"]
    if not isinstance(t, dict) or not t:
        raise SchemaError("templates: not a non-empty object")
    for k, v in t.items():
        _str(k, TEMPLATE_ID, "templates id")
        if int(k) >= N_TEMPLATES:
            raise SchemaError(f"templates: id {k!r} is not one of the game's {N_TEMPLATES} templates")
        _int(v, 1, 1_000_000, f"templates[{k!r}]")
    _str(r["result_sha256"], DIGEST, "result_sha256")
    _keys(r["events"], ("count", "sha256"), "events")
    _int(r["events"]["count"], 1, 10_000_000, "events.count")
    _str(r["events"]["sha256"], DIGEST, "events.sha256")
    _list(r["decisions"], "decisions")
    for i, row in enumerate(r["decisions"]):
        p = f"decisions[{i}]"
        _list(row, p, 2)
        _int(row[0], 0, 0xFFFF, p + "[0]")
        if not isinstance(row[1], str) or row[1] not in CONTEXTS:
            raise SchemaError(f"{p}[1]: {row[1]!r} is not one of {CONTEXTS}")
    a = r["after"]
    _keys(a, ("seed", "ds", "ranges"), "after")
    _int(a["seed"], 0, 0xFFFF, "after.seed")
    _list(a["ds"], "after.ds", DS_BLOCKS)
    for i, h in enumerate(a["ds"]):
        _str(h, DIGEST, f"after.ds[{i}]")
    _keys(a["ranges"], tuple(RANGES), "after.ranges")
    for name, (_, length) in RANGES.items():
        _list(a["ranges"][name], f"after.ranges.{name}", -(-length // BLOCK))
        for i, h in enumerate(a["ranges"][name]):
            _str(h, DIGEST, f"after.ranges.{name}[{i}]")


# ---- digests ------------------------------------------------------------------------------------------
def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def draw_line(d):
    return "%d %d %04x %04x" % tuple(d)


def draws_digest(draws):
    """The kit's draws digest (match.py `_finish`): one line per write, joined by newlines."""
    return sha256_text("\n".join(draw_line(d) for d in draws))


def draws_per_minute(draws):
    """[[minute, count, digest], ...], one per run of consecutive writes at one minute."""
    out, run = [], []
    for d in draws:
        if run and run[-1][0] != d[0]:
            out.append([run[0][0], len(run), draws_digest(run)])
            run = []
        run.append(d)
    if run:
        out.append([run[0][0], len(run), draws_digest(run)])
    return out


def block_digests(data, block=BLOCK):
    return [hashlib.sha256(data[i:i + block]).hexdigest() for i in range(0, len(data), block)]


def result_digest(r):
    """The result without the board screen: score, half-time score, goals (with their taken-back ones), bookings,
    sendings off, injuries, substitutions, man of the match, ticks, the seed after, the squads after, the board's
    statistics and bars, the commentary's lines, and what a competitive fixture adds (kind, winner, score after
    90, extra time, shoot-out, budget, the players' confidence, energy and status before and after). Only the
    digest is kept: no text, no name."""
    keep = {k: r[k] for k in ("score", "half_time_score", "goals", "goals_disallowed", "bookings", "sendings_off",
                              "injuries", "substitutions", "man_of_the_match", "ticks", "seed_after", "squads_after",
                              "kind", "winner", "score_90", "extra_time", "shootout", "substitution_budget",
                              "players")}
    keep["board"] = {k: r["board"][k] for k in ("statistics", "bars")}
    keep["commentary"] = [c["text"] for c in r["commentary"]]
    return sha256_text(canonical(keep))


def events_digest(events):
    """One digest of the event stream: kind, minute, score and data of every event, in order."""
    h = hashlib.sha256()
    n = 0
    for kind, minute, score, data in events:
        h.update(canonical([kind, minute, list(score), data]).encode() + b"\n")
        n += 1
    return n, h.hexdigest()


def template_counts(commentary):
    out = {}
    for c in commentary:
        out[str(c["template"])] = out.get(str(c["template"]), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def apply_mask(buf, base_space, base, mask):
    """buf (bytes) is the span of `base_space` ("DS" or "P") starting at `base`; return it with the masked bytes
    zeroed (a copy; the mask itself is [] by default, which returns buf unchanged)."""
    if not mask:
        return buf
    out = bytearray(buf)
    for space, start, length in mask:
        if space != base_space:
            continue
        a, b = max(start, base), min(start + length, base + len(buf))
        if a < b:
            out[a - base:b - base] = bytes(b - a)
    return bytes(out)
