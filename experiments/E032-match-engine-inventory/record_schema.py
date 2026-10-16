#!/usr/bin/env python3
"""E032: the schema of a match record, in one place (PR 243 review round 3, issue 246).

A match record is one JSON line written by timing.py, skip.py or pilot_movement.py (the E021 harness's
outputs, runtime/emul/watched_match.py). compare.py validates every record against this schema, RECURSIVELY,
before it compares anything: a record that does not conform makes the log malformed (compare.py exit 2), so
missing or mangled evidence is never equality nor a caught falsifier. derive_schema.py checks this schema
against every committed record and prints what the records actually hold.

Every record (completed or not) carries the fields compare.py reads to decide completion and to report:
  seed              int 0..0xFFFF (the main seed word written into the start state)
  error             null, or a non-empty string (why the run stopped)
  stopped_at_board  bool (the run reached the full-time board's key wait)
  strays            list of strings (000E wait-family skips; must be empty for a completed match)
  cpu_s             number >= 0 (reported, not compared)
A COMPLETED record (error null, stopped_at_board true, strays empty) also carries all the evidence compared:
  score             [int 0..255, int 0..255]   (the score bytes DS:9B3C, DS:9B3D)
  ticks             int 1..1_000_000           (clock entries 0791:970C)
  draws             int 1..100_000_000         (writes of the main seed word)
  draws_digest      64 lowercase hex digits    (sha256 of the draw trace)
  statistics_raw    exactly 11 rows, in this order (watched_match.statistics()):
                      rows 0..8:  {"row_label": STAT_LABELS[k], "raw_bytes": [int 0..255, int 0..255],
                                   "address": "DS:7B7E+10*t" .. "DS:7B86+10*t"}  (k = row)
                      rows 9, 10: {"row_label": STAT_LABELS[k], "raw_words": [int 0..65535, int 0..65535],
                                   "address": "DS:80F2/80F4", "DS:80F6/80F8"}
                    no other keys in a row; the labels are the board's (Corners ... Territory), as every
                    committed record holds them
  templates         a non-empty mapping {decimal template id 0..254 as a string: count int >= 1}
Booleans are not numbers here (JSON true is never accepted as 1). Other keys of a record (inputs, wall_s,
hook_counts, ...) are not compared and not validated."""
import re

DIGEST = re.compile(r"^[0-9a-f]{64}$")
TEMPLATE_ID = re.compile(r"^(0|[1-9][0-9]{0,2})$")
STAT_BYTE_ROWS = [f"DS:{0x7B7E + k:04X}+10*t" for k in range(9)]
STAT_WORD_ROWS = ["DS:80F2/80F4", "DS:80F6/80F8"]
# the board's row labels, as every committed record holds them (derive_schema.py)
STAT_LABELS = ["Corners", "Free kicks", "Penalties", "Shots", "On target", "Saves", "Fouls", "Bookings",
               "Red cards", "Possession", "Territory"]


class SchemaError(ValueError):
    pass


def _int(v, lo, hi, path):
    if not isinstance(v, int) or isinstance(v, bool) or not lo <= v <= hi:
        raise SchemaError(f"{path}: {v!r} is not an integer in {lo}..{hi}")


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


def validate_base(r):
    """The fields every record carries. Raises SchemaError."""
    if not isinstance(r, dict):
        raise SchemaError("the record is not an object")
    for key in ("seed", "error", "stopped_at_board", "strays", "cpu_s"):
        if key not in r:
            raise SchemaError(f"{key}: missing")
    _int(r["seed"], 0, 0xFFFF, "seed")
    if r["error"] is not None and not (isinstance(r["error"], str) and r["error"]):
        raise SchemaError(f"error: {r['error']!r} is neither null nor a non-empty string")
    if not isinstance(r["stopped_at_board"], bool):
        raise SchemaError(f"stopped_at_board: {r['stopped_at_board']!r} is not a boolean")
    if not isinstance(r["strays"], list) or not all(isinstance(s, str) for s in r["strays"]):
        raise SchemaError(f"strays: {r['strays']!r} is not a list of strings")
    c = r["cpu_s"]
    if not isinstance(c, (int, float)) or isinstance(c, bool) or c < 0:
        raise SchemaError(f"cpu_s: {c!r} is not a number >= 0")


def is_completed(r):
    """For a record that passed validate_base."""
    return r["error"] is None and r["stopped_at_board"] is True and not r["strays"]


def validate_evidence(r):
    """The evidence of a completed record. Raises SchemaError."""
    for key in ("score", "ticks", "draws", "draws_digest", "statistics_raw", "templates"):
        if key not in r:
            raise SchemaError(f"{key}: missing")
    _pair(r["score"], 0, 255, "score")
    _int(r["ticks"], 1, 1_000_000, "ticks")
    _int(r["draws"], 1, 100_000_000, "draws")
    if not (isinstance(r["draws_digest"], str) and DIGEST.match(r["draws_digest"])):
        raise SchemaError(f"draws_digest: {r['draws_digest']!r} is not 64 lowercase hex digits")
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
        if row["row_label"] != STAT_LABELS[i]:
            raise SchemaError(f"{path}.row_label: {row['row_label']!r} is not {STAT_LABELS[i]!r}")
        if row["address"] != want:
            raise SchemaError(f"{path}.address: {row['address']!r} is not {want!r}")
    t = r["templates"]
    if not isinstance(t, dict) or not t:
        raise SchemaError("templates: not a non-empty object")
    for k, v in t.items():
        if not TEMPLATE_ID.match(k) or int(k) > 254:
            raise SchemaError(f"templates: id {k!r} is not a decimal 0..254")
        _int(v, 1, 1_000_000, f"templates[{k!r}]")


def validate(r):
    """Every field compare.py reads; the evidence only when the record is a completed match."""
    validate_base(r)
    if is_completed(r):
        validate_evidence(r)
