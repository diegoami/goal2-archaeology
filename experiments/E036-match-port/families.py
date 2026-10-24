#!/usr/bin/env python3
"""E036 (T57): the families of matches, as data, and the answer policies their scenarios use.

A family is one JSON file under families/ (F40.json, O8.json, S.json); a later task adds a family or a scenario as a
file of its own there, found by this module with no shared list to edit. A file holds:
  family       the family's name (the file's stem)
  reference    the repository-relative path of the log of the unhooked kit over this family (a family names its own
               reference, so one added later brings its reference with it)
  description  text
  base         the fields every match shares (below)
  edit_sets    named lists of edits, which a match names in `edits`
  matches      the matches: {"id": "<family>/<name>", ...fields that replace the base's}
and a match has
  fixture      [first country, second country, calendar number, kind] (original_match.Fixture)
  image        optional registered source key (default E006); nondefault source SHA enters the spec digest
  managed      the country the kit makes the human's (may be outside the fixture)
  seed         the main RNG word written at the captain prompt, or null (the set-up's own)
  delay_byte   the speed byte written there, or null (the image's)
  substitutions  null (the original's budget), a number, or [team 0's, team 1's]
  edits        a list of edits to the image's records before the match, or the name of an edit set:
               {"target": "country"|"squad", "country": 1..128, "offset": byte, "op": "set"|"add"|"xor"|"or",
                "value": int}; "squad" is the 20 players the country's record names; "add" clamps to 0..255
  policy       {"name": a class of POLICIES, ...its parameters}: how the managed side answers each decision

A file in families/ ending in .py may define POLICIES = {name: class} for a scenario whose answers the classes here
do not give; it is loaded first. The spec of a match (`MatchSpec.spec`) is everything that makes it, and
`spec_sha256` is its digest, with the code of its policy: change a policy and the reference no longer matches.

This module imports no emulator (compare.py uses it too)."""
import hashlib
import importlib.util
import inspect
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILIES_DIR = HERE / "families"
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(HERE))
import records  # noqa: E402
import image_sources  # noqa: E402
from original_match.assets import REFERENCE  # noqa: E402    (imports the kit's package, which needs no unicorn)
from original_match.match import KINDS  # noqa: E402

OPS = ("set", "add", "xor", "or")
TARGETS = ("country", "squad")
COUNTRY_SIZE, PLAYER_SIZE = 0xBF, 0x14
RESERVED = ("ALL",)


class FamilyError(ValueError):
    pass


# ---- the answer policies ---------------------------------------------------------------------------
class Policy:
    """How the managed side answers. `contexts` are the decisions the scenario declares it will be asked: one the
    scenario does not declare is a stray (the runner records it and the match is not completed). `pause_at` are the
    minutes at which the runner calls Match.pause() (once each, at the first `minute` event of that minute)."""
    uses = ()

    def __init__(self, contexts, pause_at=None):
        pause_at = [] if pause_at is None else pause_at
        if not (isinstance(contexts, list) and contexts and all(c in records.CONTEXTS for c in contexts)
                and len(set(contexts)) == len(contexts)):
            raise FamilyError(f"{type(self).__name__}: contexts {contexts!r} are not distinct entries of {records.CONTEXTS}")
        if not (isinstance(pause_at, list) and all(records.is_int(x) and 1 <= x <= 119 for x in pause_at)):
            raise FamilyError(f"{type(self).__name__}: pause_at {pause_at!r} is not a list of minutes")
        self.contexts, self.pause_at = list(contexts), tuple(pause_at)

    def params(self):
        return {"contexts": self.contexts, "pause_at": list(self.pause_at)}

    def declare(self):
        return {"name": type(self).__name__, **self.params()}

    @classmethod
    def code_sha256(cls):
        return hashlib.sha256("\n".join(inspect.getsource(c) for c in (cls,) + cls.uses).encode()).hexdigest()

    def answer(self, m, d):
        raise NotImplementedError


class PlayOn(Policy):
    """Play on at every decision (a manager who only presses Enter)."""

    def answer(self, m, d):
        m.answer()


class Decisions(Policy):
    """E033 stamps.py `decisions`: at a pause the 4th tactic element is flipped and the eleven's last player is
    replaced by the bench's eighth; at half time (not refused) the eleven's tenth by the bench's second; an injured
    player of the eleven by the bench's third; anything else, play on."""

    def answer(self, m, d):
        if d["context"] == "pause" and d["eleven"]:
            m.answer(tactics={4: not bool(d["tactics"] >> 3 & 1)}, substitutions=[(d["eleven"][10], d["bench"][7])])
        elif d["context"] == "half_time" and not d.get("refused"):
            m.answer(substitutions=[(d["eleven"][9], d["bench"][1])])
        elif d["context"] == "substitution" and d["injured"]:
            m.answer(substitutions=[(d["injured"][0], d["bench"][2])])
        else:
            m.answer()


class Quick(Policy):
    """E033 stamps.py `quick`: a pause from minute `at` on is answered with the quick result (R) at `speed`; the
    other decisions are played on, or, with then="Decisions", answered as Decisions does."""
    uses = (Decisions,)

    def __init__(self, contexts, speed, at=0, then=None, pause_at=None):
        super().__init__(contexts, pause_at)
        if not (records.is_int(speed) and 0 <= speed <= 5 and records.is_int(at) and 0 <= at <= 119
                and then in (None, "Decisions")):
            raise FamilyError(f"Quick: speed {speed!r}, at {at!r}, then {then!r} are out of range")
        self.speed, self.at, self.then = speed, at, then
        self._then = Decisions(contexts, pause_at) if then else PlayOn(contexts)

    def params(self):
        return {**super().params(), "speed": self.speed, "at": self.at, "then": self.then}

    def answer(self, m, d):
        if d["context"] == "pause" and m.minute >= self.at:
            m.answer(quick=True, speed=self.speed)
        else:
            self._then.answer(m, d)


class QuickAtHalfTime(Policy):
    """E034 stamps_competitive.py `quick_at_half_time`: the quick result at half time, play on elsewhere."""

    def answer(self, m, d):
        m.answer(quick=True) if d["context"] == "half_time" else m.answer()


class Knockout(Policy):
    """E034's knockout answers, the kit's example.knockout_answer (three substitutions and a tactic before extra
    time, the shoot-out order reversed, an injured player replaced while the budget lasts)."""

    def answer(self, m, d):
        from original_match import example
        example.knockout_answer(m, d, lambda *a: None)


POLICIES = {c.__name__: c for c in (PlayOn, Decisions, Quick, QuickAtHalfTime, Knockout)}


def policy_from(spec, policies=POLICIES):
    """The policy object a match's `policy` spec names."""
    if not isinstance(spec, dict) or not isinstance(spec.get("name"), str):
        raise FamilyError(f"policy {spec!r}: not an object with a name")
    if spec["name"] not in policies:
        raise FamilyError(f"policy {spec['name']!r}: not one of {sorted(policies)}")
    params = {k: v for k, v in spec.items() if k != "name"}
    try:
        return policies[spec["name"]](**params)
    except TypeError as e:
        raise FamilyError(f"policy {spec['name']!r}: {e}")


# ---- the edits ----------------------------------------------------------------------------------------
def check_edit(e, where):
    if not isinstance(e, dict) or set(e) != {"target", "country", "offset", "op", "value"}:
        raise FamilyError(f"{where}: an edit is {{target, country, offset, op, value}}, not {e!r}")
    if e["target"] not in TARGETS or e["op"] not in OPS:
        raise FamilyError(f"{where}: target {e['target']!r} or op {e['op']!r} is not one of {TARGETS}, {OPS}")
    if not (records.is_int(e["country"]) and 1 <= e["country"] <= 128):
        raise FamilyError(f"{where}: country {e['country']!r} is not 1..128")
    size = COUNTRY_SIZE if e["target"] == "country" else PLAYER_SIZE
    if not (records.is_int(e["offset"]) and 0 <= e["offset"] < size):
        raise FamilyError(f"{where}: offset {e['offset']!r} is not inside a {e['target']} record ({size} bytes)")
    lo = -255 if e["op"] == "add" else 0
    if not (records.is_int(e["value"]) and lo <= e["value"] <= 255):
        raise FamilyError(f"{where}: value {e['value']!r} is not an integer in {lo}..255")


def apply_edit(byte, op, value):
    return {"set": value, "add": min(255, max(0, byte + value)), "xor": byte ^ value, "or": byte | value}[op]


def apply_edits(players, countries, edits):
    """New lists of player and country records (bytes) with the edits made, in order."""
    players, countries = [bytearray(p) for p in players], [bytearray(c) for c in countries]
    for e in edits:
        if e["target"] == "country":
            rec = countries[e["country"]]
            rec[e["offset"]] = apply_edit(rec[e["offset"]], e["op"], e["value"])
        else:
            squad = [int.from_bytes(countries[e["country"]][2 * i:2 * i + 2], "little") for i in range(20)]
            for w in squad:
                if w:
                    players[w][e["offset"]] = apply_edit(players[w][e["offset"]], e["op"], e["value"])
    return [bytes(p) for p in players], [bytes(c) for c in countries]


# ---- the matches ---------------------------------------------------------------------------------------
REQUIRED_MATCH_FIELDS = ("fixture", "managed", "seed", "delay_byte", "substitutions", "edits", "policy")
MATCH_FIELDS = REQUIRED_MATCH_FIELDS + ("image",)


class MatchSpec:
    """One declared match. `spec()` is the JSON-able declaration and `sha256` its digest with the policy's code."""

    def __init__(self, id, family, fixture, managed, seed, delay_byte, substitutions, edits, policy, policies=POLICIES,
                 image=image_sources.DEFAULT):
        where = f"match {id!r}"
        if not (isinstance(id, str) and records.RECORD_ID.fullmatch(id) and id.split("/")[0] == family):
            raise FamilyError(f"{where}: the id is not '{family}/<name>'")
        if not (isinstance(fixture, list) and len(fixture) == 4 and all(records.is_int(x) for x in fixture)
                and 1 <= fixture[0] <= 128 and 1 <= fixture[1] <= 128 and fixture[0] != fixture[1]
                and 1 <= fixture[2] <= 0xFFFF and fixture[3] in KINDS):
            raise FamilyError(f"{where}: fixture {fixture!r} is not [first, second, index, kind] of two countries "
                              f"1..128, a calendar number and one of the kinds {KINDS}")
        if not (records.is_int(managed) and 1 <= managed <= 128):
            raise FamilyError(f"{where}: managed {managed!r} is not a country 1..128")
        if seed is not None and not (records.is_int(seed) and 0 <= seed <= 0xFFFF):
            raise FamilyError(f"{where}: seed {seed!r} is not null or 0..65535")
        if delay_byte is not None and not (records.is_int(delay_byte) and 0 <= delay_byte <= 5):
            raise FamilyError(f"{where}: delay_byte {delay_byte!r} is not null or 0..5")
        ok_budget = lambda b: records.is_int(b) and 0 <= b <= 255  # noqa: E731
        if not (substitutions is None or ok_budget(substitutions) or (
                isinstance(substitutions, list) and len(substitutions) == 2 and all(ok_budget(b) for b in substitutions))):
            raise FamilyError(f"{where}: substitutions {substitutions!r} is not null, 0..255 or [0..255, 0..255]")
        if not isinstance(edits, list):
            raise FamilyError(f"{where}: edits is not a list")
        for i, e in enumerate(edits):
            check_edit(e, f"{where} edits[{i}]")
        self.id, self.family = id, family
        self.fixture, self.managed, self.seed, self.delay_byte = fixture, managed, seed, delay_byte
        self.substitutions, self.edits, self.policy_spec = substitutions, edits, policy
        self.policy = policy_from(policy, policies)
        self.policy_cls = type(self.policy)
        try:
            image_sources.get(image)
        except image_sources.SourceError as e:
            raise FamilyError(f"{where}: {e}") from e
        self.image = image

    def spec(self):
        declaration = {"id": self.id, "fixture": self.fixture, "managed": self.managed, "seed": self.seed,
                "delay_byte": self.delay_byte, "substitutions": self.substitutions, "edits": self.edits,
                "policy": self.policy.declare(), "policy_code_sha256": self.policy_cls.code_sha256()}
        if self.image != image_sources.DEFAULT:
            declaration["image_sha256"] = self.image_sha256
        return declaration

    @property
    def image_sha256(self):
        return image_sha256() if self.image == image_sources.DEFAULT else image_sources.get(self.image)["sha256"]

    @property
    def sha256(self):
        return records.sha256_text(records.canonical(self.spec()))


class Family:
    def __init__(self, name, reference, description, matches):
        self.name, self.reference, self.description, self.matches = name, reference, description, matches

    def expected(self):
        """{match id: spec digest}."""
        return {m.id: m.sha256 for m in self.matches}


def load_policies(directory):
    """POLICIES of every .py file in the directory, merged over the built-in ones; a name twice is an error."""
    policies = dict(POLICIES)
    for path in sorted(Path(directory).glob("*.py")):
        name = f"e036_families_{path.stem}"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod               # inspect.getsource (the policy's code digest) finds a class by its module
        spec.loader.exec_module(mod)
        for name, cls in getattr(mod, "POLICIES", {}).items():
            if name in policies:
                raise FamilyError(f"{path.name}: policy {name!r} is declared twice")
            policies[name] = cls
    return policies


FILE_KEYS = ("family", "reference", "description", "base", "edit_sets", "matches")


def load_family(path, policies=POLICIES):
    """One family file, strictly (records.loads: no NaN, no duplicate key), every field checked."""
    path = Path(path)
    try:
        doc = records.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise FamilyError(f"{path.name}: {e}")
    if not isinstance(doc, dict) or set(doc) != set(FILE_KEYS):
        raise FamilyError(f"{path.name}: keys {sorted(doc) if isinstance(doc, dict) else doc!r} are not {sorted(FILE_KEYS)}")
    name = doc["family"]
    if not (isinstance(name, str) and records.FAMILY_NAME.fullmatch(name) and name not in RESERVED and name == path.stem):
        raise FamilyError(f"{path.name}: family {name!r} is not the file's stem, a name, and not {RESERVED}")
    if not (isinstance(doc["reference"], str) and re.fullmatch(r"[A-Za-z0-9_./-]+\.jsonl", doc["reference"])
            and not doc["reference"].startswith("/") and ".." not in doc["reference"].split("/")):
        raise FamilyError(f"{path.name}: reference {doc['reference']!r} is not a repository-relative .jsonl path")
    if not isinstance(doc["description"], str) or not doc["description"]:
        raise FamilyError(f"{path.name}: description is not text")
    base, sets = doc["base"], doc["edit_sets"]
    if not isinstance(base, dict) or not set(base) <= set(MATCH_FIELDS):
        raise FamilyError(f"{path.name}: base holds {sorted(base) if isinstance(base, dict) else base!r}, not fields of {MATCH_FIELDS}")
    if not isinstance(sets, dict) or not all(isinstance(v, list) for v in sets.values()):
        raise FamilyError(f"{path.name}: edit_sets is not an object of lists")
    for set_name, edits in sets.items():            # every edit of every set, used or not
        for i, e in enumerate(edits):
            check_edit(e, f"{path.name} edit_sets[{set_name!r}][{i}]")
    if not isinstance(doc["matches"], list) or not doc["matches"]:
        raise FamilyError(f"{path.name}: matches is not a non-empty list")
    matches, seen = [], set()
    for i, entry in enumerate(doc["matches"]):
        if not isinstance(entry, dict) or "id" not in entry or not set(entry) <= set(MATCH_FIELDS) | {"id"}:
            raise FamilyError(f"{path.name}: matches[{i}] is not an object with an id and fields of {MATCH_FIELDS}")
        fields = {**base, **{k: v for k, v in entry.items() if k != "id"}}
        missing = [k for k in REQUIRED_MATCH_FIELDS if k not in fields]
        if missing:
            raise FamilyError(f"{path.name}: {entry['id']!r} lacks {missing} (neither it nor the base gives them)")
        if isinstance(fields["edits"], str):
            if fields["edits"] not in sets:
                raise FamilyError(f"{path.name}: {entry['id']!r} names the edit set {fields['edits']!r}, not one of {sorted(sets)}")
            fields["edits"] = sets[fields["edits"]]
        m = MatchSpec(entry["id"], name, policies=policies, **fields)
        if m.id in seen:
            raise FamilyError(f"{path.name}: the id {m.id!r} twice")
        seen.add(m.id)
        matches.append(m)
    return Family(name, doc["reference"], doc["description"], matches)


def discover(directory=FAMILIES_DIR):
    """{name: Family} of every families/*.json (the .py files' policies loaded first)."""
    policies = load_policies(directory)
    out = {}
    for path in sorted(Path(directory).glob("*.json")):
        fam = load_family(path, policies)
        out[fam.name] = fam            # an id starts with its family's name and a family is a file's stem: no id twice
    if not out:
        raise FamilyError(f"no family file in {directory}")
    return out


def select(arg, families):
    """The families a --family argument names: ALL, or comma-separated names (each once, each known)."""
    if arg == "ALL":
        return [families[n] for n in sorted(families)]
    names = arg.split(",")
    if len(set(names)) != len(names) or any(n not in families for n in names):
        raise FamilyError(f"--family {arg!r}: ALL, or distinct names among {sorted(families)}")
    return [families[n] for n in names]


def image_sha256():
    return REFERENCE["sha256"]
