#!/usr/bin/env python3
"""E032: the schema of a match record, in one place (PR 243 review rounds 3 and 4, issue 246).

A match record is one JSON line written by timing.py, skip.py or pilot_movement.py (the E021 harness's
outputs, runtime/emul/watched_match.py). compare.py reads every log with `loads` below and validates every
record with `validate`, RECURSIVELY, before it compares anything: a record that does not conform makes the
log malformed (compare.py exit 2), so missing or mangled evidence is never equality nor a caught falsifier.
derive_schema.py checks this schema against every committed record.

The grammar is meant to be exactly as wide as the intent (round 4: "a validator whose grammar is looser
than its intent"):
- JSON is parsed strictly (`loads`): NaN, Infinity and -Infinity tokens, numbers that overflow to infinity
  (1e999) and duplicate keys in an object are refused;
- every string pattern is matched against the WHOLE string (re.fullmatch) with ASCII-only character classes
  ([0-9], [0-9a-f]: never the backslash-d class, which also matches other scripts' digits);
- integers are Python ints, never booleans nor floats (1.0 is refused where an int is meant); floats must be
  finite and not -0.0; every number has a range;
- the set of a record's keys is closed: an unknown key is refused.

Every record (completed or not):
  seed              int 0..0xFFFF, and equal to the declared seed write in `inputs`
  error             null, or a non-empty string without control characters nor leading/trailing white space
  stopped_at_board  bool
  strays            list of 000E wait-family addresses (watched_match.WAIT_FAMILY); empty when completed
  cpu_s, wall_s     finite numbers 0..1e6 (not -0.0)
  start_record      "E" + 3 digits + "-r" + 4 digits (the run record whose watchstart state was used)
  watchstart_sha256 64 lowercase hex digits
  inputs            list of {"what", "linear", "old", "new"}: `what` one of the harness's declared input
                    descriptions (INPUT_WHAT), `linear` int 0..0x10FFFF, `old`/`new` lowercase hex of whole
                    bytes, equal lengths; no input twice; exactly one "main seed word DS:7B62", whose `new`
                    is the seed, little end first
  score             [int 0..255, int 0..255]
  ticks, draws      int 0..1_000_000 / 0..100_000_000 (>= 1 when completed)
  draws_digest      64 lowercase hex digits
  statistics_raw    null when not completed; else exactly 11 rows in order (watched_match.statistics()):
                      rows 0..8:  {"row_label": STAT_LABELS[k], "raw_bytes": [int 0..255, int 0..255],
                                   "address": "DS:7B7E+10*t" .. "DS:7B86+10*t"}
                      rows 9, 10: {"row_label": STAT_LABELS[k], "raw_words": [int 0..65535, int 0..65535],
                                   "address": "DS:80F2/80F4", "DS:80F6/80F8"}
                    no other keys in a row
  templates         null when not completed; else a non-empty mapping {decimal id 0..66 (the game's 67
                    templates, watched_match.N_TEMPLATES) without leading zeros: count int 1..1_000_000}
Optional keys, each with its own grammar: delay_count (null or int 1..0xFFFFFFFF), fast_delay (bool),
skipped and ported (non-empty lists of distinct SSSS:OOOO addresses), hook_counts ({SSSS:OOOO: int >= 0}),
variant (one of pilot_movement.VARIANTS), port_calls (int >= 0). Nothing else."""
import json
import math
import re

ADDRESS = re.compile(r"[0-9A-F]{4}:[0-9A-F]{4}")
DIGEST = re.compile(r"[0-9a-f]{64}")
HEX_BYTES = re.compile(r"(?:[0-9a-f]{2})+")
TEMPLATE_ID = re.compile(r"0|[1-9][0-9]{0,2}")
START_RECORD = re.compile(r"E[0-9]{3}-r[0-9]{4}")
WAIT_FAMILY = ("000E:05F6", "000E:0572", "000E:04F5", "000E:045D")        # watched_match.WAIT_FAMILY
VARIANTS = ("exact", "coin-swapped", "bound-36", "no-picture")           # pilot_movement.VARIANTS
N_TEMPLATES = 67                                                         # watched_match.N_TEMPLATES
SEED_INPUT = "main seed word DS:7B62"
INPUT_WHAT = [re.compile(re.escape(s)) for s in (
    SEED_INPUT, "delay byte [DS:A923]+0x3F", "delay calibration dword DS:A9FF/AA01",
    "delay calibration dword DS:A9FF/AA01, at the first 0791:970C entry")] + [
    re.compile(r"country (?:0|[1-9][0-9]{0,2}) \+0x2D \(default team tactic set\)"),
    re.compile(r"country (?:0|[1-9][0-9]{0,2}) squad words \+0\.\.\+0x27"),
    re.compile(r"player (?:0|[1-9][0-9]{0,4}) \+0x[0-9A-F]{1,2}")]
STAT_BYTE_ROWS = [f"DS:{0x7B7E + k:04X}+10*t" for k in range(9)]
STAT_WORD_ROWS = ["DS:80F2/80F4", "DS:80F6/80F8"]
# the board's row labels, as every committed record holds them (derive_schema.py)
STAT_LABELS = ["Corners", "Free kicks", "Penalties", "Shots", "On target", "Saves", "Fouls", "Bookings",
               "Red cards", "Possession", "Territory"]
REQUIRED = ("seed", "error", "stopped_at_board", "strays", "cpu_s", "wall_s", "start_record", "watchstart_sha256",
            "inputs", "score", "ticks", "draws", "draws_digest", "statistics_raw", "templates")
OPTIONAL = ("delay_count", "fast_delay", "skipped", "ported", "hook_counts", "variant", "port_calls")


class SchemaError(ValueError):
    pass


# ---- strict JSON ---------------------------------------------------------------------------------
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


# ---- value grammar ---------------------------------------------------------------------------------
def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def finite_number(v, lo, hi):
    """True for an int, or a finite float that is not -0.0, in lo..hi (never a bool)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    if isinstance(v, float) and (not math.isfinite(v) or (v == 0 and math.copysign(1, v) < 0)):
        return False
    return lo <= v <= hi


def _int(v, lo, hi, path):
    if not is_int(v) or not lo <= v <= hi:
        raise SchemaError(f"{path}: {v!r} is not an integer in {lo}..{hi}")


def _num(v, lo, hi, path):
    if not finite_number(v, lo, hi):
        raise SchemaError(f"{path}: {v!r} is not a finite number in {lo}..{hi}")


def _str(v, pattern, path):
    if not isinstance(v, str) or not pattern.fullmatch(v):
        raise SchemaError(f"{path}: {v!r} does not match {pattern.pattern!r} as a whole")


def _pair(v, lo, hi, path):
    if not isinstance(v, list) or len(v) != 2:
        raise SchemaError(f"{path}: {v!r} is not a list of two")
    for i, x in enumerate(v):
        _int(x, lo, hi, f"{path}[{i}]")


def _keys(d, want, path):
    if not isinstance(d, dict):
        raise SchemaError(f"{path}: not an object")
    if set(d) != set(want):
        raise SchemaError(f"{path}: keys {sorted(d)} are not {sorted(want)}")


def _addresses(v, path):
    if not isinstance(v, list) or not v:
        raise SchemaError(f"{path}: not a non-empty list")
    for i, a in enumerate(v):
        _str(a, ADDRESS, f"{path}[{i}]")
    if len(set(v)) != len(v):
        raise SchemaError(f"{path}: an address appears twice")


def _text(v, path):
    """Free text: non-empty, no control characters, no leading or trailing white space."""
    if not isinstance(v, str) or not v or v != v.strip() or any(ord(c) < 0x20 or 0x7F <= ord(c) < 0xA0 for c in v):
        raise SchemaError(f"{path}: {v!r} is not clean non-empty text")


# ---- the record ---------------------------------------------------------------------------------------
def is_completed(r):
    """For a record that passed validate_base."""
    return r["error"] is None and r["stopped_at_board"] is True and not r["strays"]


def validate_base(r):
    """Every field of every record. Raises SchemaError."""
    if not isinstance(r, dict):
        raise SchemaError("the record is not an object")
    for key in REQUIRED:
        if key not in r:
            raise SchemaError(f"{key}: missing")
    unknown = sorted(set(r) - set(REQUIRED) - set(OPTIONAL))
    if unknown:
        raise SchemaError(f"unknown keys {unknown}")
    _int(r["seed"], 0, 0xFFFF, "seed")
    if r["error"] is not None:
        _text(r["error"], "error")
    if not isinstance(r["stopped_at_board"], bool):
        raise SchemaError(f"stopped_at_board: {r['stopped_at_board']!r} is not a boolean")
    if not isinstance(r["strays"], list) or not all(isinstance(s, str) and s in WAIT_FAMILY for s in r["strays"]):
        raise SchemaError(f"strays: {r['strays']!r} is not a list of 000E wait-family addresses")
    _num(r["cpu_s"], 0, 1e6, "cpu_s")
    _num(r["wall_s"], 0, 1e6, "wall_s")
    _str(r["start_record"], START_RECORD, "start_record")
    _str(r["watchstart_sha256"], DIGEST, "watchstart_sha256")
    inputs = r["inputs"]
    if not isinstance(inputs, list):
        raise SchemaError("inputs: not a list")
    seeds = []
    for i, d in enumerate(inputs):
        path = f"inputs[{i}]"
        _keys(d, ("what", "linear", "old", "new"), path)
        if not isinstance(d["what"], str) or not any(p.fullmatch(d["what"]) for p in INPUT_WHAT):
            raise SchemaError(f"{path}.what: {d['what']!r} is not a declared input")
        _int(d["linear"], 0, 0x10FFFF, path + ".linear")
        _str(d["old"], HEX_BYTES, path + ".old")
        _str(d["new"], HEX_BYTES, path + ".new")
        if len(d["old"]) != len(d["new"]):
            raise SchemaError(f"{path}: old and new differ in length")
        if d["what"] == SEED_INPUT:
            seeds.append(d["new"])
    whats = [d["what"] for d in inputs]
    if len(set(whats)) != len(whats):
        raise SchemaError("inputs: one input declared twice")
    if seeds != [r["seed"].to_bytes(2, "little").hex()]:
        raise SchemaError(f"inputs: the declared seed writes {seeds} are not exactly seed 0x{r['seed']:04x}")
    _pair(r["score"], 0, 255, "score")
    _int(r["ticks"], 0, 1_000_000, "ticks")
    _int(r["draws"], 0, 100_000_000, "draws")
    _str(r["draws_digest"], DIGEST, "draws_digest")
    if "delay_count" in r and r["delay_count"] is not None:
        _int(r["delay_count"], 1, 0xFFFFFFFF, "delay_count")
    if "fast_delay" in r and not isinstance(r["fast_delay"], bool):
        raise SchemaError("fast_delay: not a boolean")
    for key in ("skipped", "ported"):
        if key in r:
            _addresses(r[key], key)
    if "hook_counts" in r:
        h = r["hook_counts"]
        if not isinstance(h, dict):
            raise SchemaError("hook_counts: not an object")
        for k, v in h.items():
            _str(k, ADDRESS, "hook_counts key")
            _int(v, 0, 10 ** 12, f"hook_counts[{k!r}]")
    if "variant" in r and r["variant"] not in VARIANTS:
        raise SchemaError(f"variant: {r['variant']!r} is not one of {VARIANTS}")
    if "port_calls" in r:
        _int(r["port_calls"], 0, 10 ** 12, "port_calls")
    if not is_completed(r):
        for key in ("statistics_raw", "templates"):
            if r[key] is not None:
                _evidence_containers(r)
                break


def _evidence_containers(r):
    rows = r["statistics_raw"]
    if not isinstance(rows, list) or len(rows) != len(STAT_BYTE_ROWS) + len(STAT_WORD_ROWS):
        raise SchemaError("statistics_raw: not a list of 11 rows")
    for i, row in enumerate(rows):
        path = f"statistics_raw[{i}]"
        if i < len(STAT_BYTE_ROWS):
            _keys(row, ("row_label", "raw_bytes", "address"), path)
            _pair(row["raw_bytes"], 0, 255, path + ".raw_bytes")
            want = STAT_BYTE_ROWS[i]
        else:
            _keys(row, ("row_label", "raw_words", "address"), path)
            _pair(row["raw_words"], 0, 0xFFFF, path + ".raw_words")
            want = STAT_WORD_ROWS[i - len(STAT_BYTE_ROWS)]
        if not isinstance(row["row_label"], str) or row["row_label"] != STAT_LABELS[i]:
            raise SchemaError(f"{path}.row_label: {row['row_label']!r} is not {STAT_LABELS[i]!r}")
        if not isinstance(row["address"], str) or row["address"] != want:
            raise SchemaError(f"{path}.address: {row['address']!r} is not {want!r}")
    t = r["templates"]
    if not isinstance(t, dict) or not t:
        raise SchemaError("templates: not a non-empty object")
    for k, v in t.items():
        _str(k, TEMPLATE_ID, "templates id")
        if int(k) >= N_TEMPLATES:
            raise SchemaError(f"templates: id {k!r} is not one of the game's {N_TEMPLATES} templates")
        _int(v, 1, 1_000_000, f"templates[{k!r}]")


def validate_evidence(r):
    """The evidence of a completed record. Raises SchemaError."""
    _int(r["ticks"], 1, 1_000_000, "ticks")
    _int(r["draws"], 1, 100_000_000, "draws")
    _evidence_containers(r)


def validate(r):
    """Every field of the record; the compared evidence in full when it is a completed match."""
    validate_base(r)
    if is_completed(r):
        validate_evidence(r)
