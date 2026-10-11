"""Shared reading of the screen records and the screen-kind rules (T39a).

Standard library only. A record is a committed `runs/E015/E015-r<nnnn>.json` (run/1). Its screens
are read from the observations extract.py wrote: per state the sha256 of the 4000 chars+attributes
bytes, and per unique digest the 80x25 CP437 text. Nothing here reads a savestate; render.py does.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "runs" / "E015"
KINDS = ROOT / "static" / "screens" / "kinds.tsv"
CATALOGUE = ROOT / "static" / "screens" / "catalogue.tsv"
OWNER = ROOT / "static" / "screens" / "owner.tsv"

STATE_DIGEST = re.compile(r"^state (\d+) \((.*?)\): text screen 80x25, chars\+attributes")
TEXT_DIGEST = re.compile(r"text screen rows 0-24, CP437 decoded.*\(digest ([0-9a-f]{64})\)")


def normalize(text):
    """Runs of whitespace (spaces and newlines) become one space: a phrase on one screen row is
    found whatever columns surround it."""
    return re.sub(r"\s+", " ", text).strip()


def parse_rule(rule):
    """`+phrase ;; -phrase`: every + phrase must occur, no - phrase may occur (normalized text)."""
    items = []
    for part in rule.split(" ;; "):
        part = part.strip()
        if not part or part[0] not in "+-":
            raise ValueError(f"rule item must start with + or -: {part!r} in {rule!r}")
        items.append((part[0], normalize(part[1:])))
    return items


def load_kinds(path=KINDS):
    """[(kind, rule string, parsed rule, description)] in file order."""
    kinds = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines()):
        if n == 0 or not line.strip():
            continue
        kind, rule, description = line.split("\t")
        kinds.append((kind, rule, parse_rule(rule), description))
    return kinds


def matches(parsed, text):
    norm = normalize(text)
    return all((phrase in norm) == (sign == "+") for sign, phrase in parsed)


def kinds_matching(text, kinds=None):
    kinds = load_kinds() if kinds is None else kinds
    return [k[0] for k in kinds if matches(k[2], text)]


def identify_text(text, kinds=None):
    """The kind whose rule the text satisfies, `unknown` when none does. Two kinds matching one
    screen is a defect in the rules, not a choice: it raises."""
    found = kinds_matching(text, kinds)
    if len(found) > 1:
        raise ValueError(f"rules of {found} all match one screen")
    return found[0] if found else "unknown"


def read_record(path):
    """{run_id, states: {n: {digest, text, file}}, keymap}; a state with no screen is absent."""
    path = Path(path)
    if not path.is_file() and not str(path).endswith(".json"):
        path = RUNS / f"{path}.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    digests, texts, keymap = {}, {}, None
    for o in rec["observations"]:
        field = str(o.get("field"))
        m = STATE_DIGEST.match(field)
        if m:
            digests[int(m.group(1))] = (o["value"], m.group(2))
            continue
        m = TEXT_DIGEST.search(field)
        if m:
            texts[m.group(1)] = o["value"]
        elif field == "screen/key map (JSON)":
            keymap = json.loads(o["value"])
    states = {n: {"digest": d, "file": f, "text": texts.get(d)} for n, (d, f) in sorted(digests.items())}
    return {"run_id": rec["run_id"], "states": states, "keymap": keymap}


def record_paths():
    return sorted(RUNS.glob("E015-r*.json"))
