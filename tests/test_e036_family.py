"""E036 (T57): the families as data, the answer policies, and the family runner (family.py).

- the families: F40 (20 seeds as they are, E032's ten among them, and the same 20 with declared edits), O8 (four other
  pairs, a friendly and a qualifier each), S (the kit's scenarios); a family added later is a file of its own, found
  with no list to edit; every field of a family file is checked; a match's digest changes with the seed, the edits, the
  policy and the policy's code;
- the runner, over a stand-in for the kit (no emulator): one valid record per match, an error or a stray decision or a
  time limit is a record and not a gap, the error text keeps no commentary, a pause is made once, `--count` skips the
  kit's replays, a mask changes the digests it covers and no other, every 1 KiB block and every range changes its own
  digest only;
- the command: resumable (a rerun adds only the matches not yet in the log and rewrites no line), refuses a log that is
  not this run's, an exit status that says whether every selected match completed;
- one real match through the kit (skipped without the image): E032's seed 0x1234 equals check.py's EXPECTED_FAMILY, and
  `--count` of the tick routine equals the ticks.
Each rule has a test that fails without it (E036_DIR, as in test_e036_compare.py)."""
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from tests.test_e036_compare import (E036, ROOT, EXPECTED, F40, FAMILIES, IMAGE, dg, incomplete, record, edited,  # noqa: E402
                                     families, family, records)
import original_match  # noqa: E402
from original_match.check import EXPECTED_FAMILY  # noqa: E402

try:
    import unicorn  # noqa: F401
    HAVE_UNICORN = True
except ImportError:             # CI does not install python3-unicorn
    HAVE_UNICORN = False
FAMILY_PY = E036 / "family.py"
IMAGE_FILE = ROOT / ".cache/dl/e0afff6751747233-e006-1000-r0001.sav"


# ---- the families --------------------------------------------------------------------------------------------
class TheFamilies(unittest.TestCase):
    def test_the_three_families_and_their_sizes(self):
        self.assertEqual({n: len(f.matches) for n, f in FAMILIES.items()}, {"F40": 40, "O8": 8, "S": 14})
        self.assertEqual(len(EXPECTED), 62)

    def test_f40_is_twenty_seeds_as_they_are_and_the_same_twenty_edited(self):
        plain = [m for m in FAMILIES["F40"].matches if not m.edits]
        edit = [m for m in FAMILIES["F40"].matches if m.edits]
        self.assertEqual((len(plain), len(edit)), (20, 20))
        self.assertEqual([m.seed for m in plain], [m.seed for m in edit])
        self.assertEqual(len({m.seed for m in plain}), 20)
        for m in plain + edit:
            self.assertEqual((m.fixture, m.managed, m.delay_byte), ([7, 19, 21, 1], 7, 0))
        self.assertEqual(sorted({(e["target"], e["offset"]) for m in edit for e in m.edits}),
                         [("country", 0x2D), ("squad", 4), ("squad", 12), ("squad", 14)])   # tactic, skills, form, energy
        self.assertEqual({e["country"] for m in edit for e in m.edits}, {19})               # one side

    def test_f40_holds_e032s_ten_seeds_exactly(self):
        self.assertEqual({m.seed for m in FAMILIES["F40"].matches if m.id.startswith("F40/e032-")}, set(EXPECTED_FAMILY))

    def test_o8_is_four_other_pairs_each_a_friendly_and_a_qualifier(self):
        o8 = FAMILIES["O8"].matches
        pairs = {tuple(m.fixture[:2]) for m in o8}
        self.assertEqual(len(pairs), 4)
        self.assertNotIn((7, 19), pairs)
        for pair in pairs:
            self.assertEqual(sorted(m.fixture[3] for m in o8 if tuple(m.fixture[:2]) == pair), [1, 2])
            self.assertEqual(len({m.seed for m in o8 if tuple(m.fixture[:2]) == pair}), 2)

    def test_s_holds_the_kits_scenarios_with_their_answer_policies(self):
        s = {m.id: m for m in FAMILIES["S"].matches}
        self.assertEqual(s["S/decisions-70"].policy.pause_at, (20, 60))
        self.assertEqual(s["S/quick-30"].policy.pause_at, (30,))
        self.assertEqual(s["S/quick-1"].policy.pause_at, (1,))
        self.assertEqual(s["S/hard-4"].seed, 4)
        self.assertEqual(s["S/injury-70"].seed, 70)
        self.assertEqual([m.fixture[2:] for m in s.values() if m.fixture[3] == 200],
                         [[39, 200], [42, 200], [30, 200], [9, 200], [53, 200], [42, 200]])
        self.assertEqual(s["S/ko-42-quick-g19"].managed, 19)
        self.assertEqual(s["S/ko-39-budget-5"].substitutions, 5)
        self.assertEqual(s["S/qualifier-21"].fixture, [7, 19, 21, 2])
        self.assertEqual(type(s["S/ko-39-budget-5"].policy).__name__, "Knockout")

    def test_each_family_names_its_reference_and_every_id_is_unique(self):
        for fam in FAMILIES.values():
            self.assertRegex(fam.reference, r"experiments/E036-match-port/out/T57/reference\.jsonl")
            for m in fam.matches:
                self.assertTrue(m.id.startswith(fam.name + "/"))
        self.assertEqual(len(EXPECTED), sum(len(f.matches) for f in FAMILIES.values()))


class TheDirectory(unittest.TestCase):
    """A family or a scenario added later is a file of its own, found with no shared list to edit."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.doc = {"family": "X1", "reference": "experiments/E036-match-port/out/T99/ref.jsonl",
                    "description": "a family added later",
                    "base": {"fixture": [7, 19, 21, 1], "managed": 7, "seed": 5, "delay_byte": 0, "substitutions": None,
                             "edits": [], "policy": {"name": "PlayOn", "contexts": ["half_time"]}},
                    "edit_sets": {"tired": [{"target": "squad", "country": 19, "offset": 14, "op": "set", "value": 3}]},
                    "matches": [{"id": "X1/a"}, {"id": "X1/b", "seed": 6, "edits": "tired"}]}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, doc):
        text = doc if isinstance(doc, str) else json.dumps(doc)
        (self.dir / name).write_text(text)

    def test_a_new_file_is_found_and_the_others_are_unchanged(self):
        self.write("X1.json", self.doc)
        found = families.discover(self.dir)
        self.assertEqual(sorted(found), ["X1"])
        self.assertEqual(found["X1"].matches[1].edits[0]["value"], 3)
        self.assertEqual(sorted(families.discover()), ["F40", "O8", "S"])         # a file of its own, in the real directory

    def test_a_policy_module_in_the_directory_is_found_too(self):
        (self.dir / "mine.py").write_text(
            "import families\n\n\nclass Mine(families.Policy):\n    def answer(self, m, d):\n        m.answer()\n\n\n"
            "POLICIES = {'Mine': Mine}\n")
        self.doc["base"]["policy"] = {"name": "Mine", "contexts": ["half_time"]}
        self.write("X1.json", self.doc)
        self.assertEqual(type(families.discover(self.dir)["X1"].matches[0].policy).__name__, "Mine")
        (self.dir / "other.py").write_text("import families\n\n\nclass Mine(families.Policy):\n    pass\n\n\nPOLICIES = {'Mine': Mine}\n")
        with self.assertRaises(families.FamilyError):                 # a name twice is refused
            families.discover(self.dir)

    def test_the_digest_changes_with_everything_that_makes_the_match(self):
        self.write("X1.json", self.doc)
        base = families.discover(self.dir)["X1"].matches[0].sha256
        changes = {"seed": 6, "fixture": [7, 19, 22, 1], "delay_byte": 1, "substitutions": 3,
                   "edits": [{"target": "country", "country": 7, "offset": 45, "op": "or", "value": 8}],
                   "policy": {"name": "PlayOn", "contexts": ["half_time", "substitution"]},
                   "managed": 19}
        for key, value in changes.items():
            doc = json.loads(json.dumps(self.doc))
            doc["base"][key] = value
            self.write("X1.json", doc)
            with self.subTest(key):
                self.assertNotEqual(families.discover(self.dir)["X1"].matches[0].sha256, base)

    def test_the_digest_changes_with_the_policys_code(self):
        sources = []
        for body in ("m.answer()", "m.answer(speed=1)"):
            (self.dir / "mine.py").write_text(
                f"import families\n\n\nclass Mine(families.Policy):\n    def answer(self, m, d):\n        {body}\n\n\n"
                "POLICIES = {'Mine': Mine}\n")
            self.doc["base"]["policy"] = {"name": "Mine", "contexts": ["half_time"]}
            self.write("X1.json", self.doc)
            sources.append(families.discover(self.dir)["X1"].matches[0].sha256)
        self.assertNotEqual(sources[0], sources[1])

    def test_builtin_policies_have_a_code_digest_of_their_own(self):
        digests = {n: c.code_sha256() for n, c in families.POLICIES.items()}
        self.assertEqual(len(set(digests.values())), len(digests))
        self.assertEqual(families.Quick.code_sha256() == families.PlayOn.code_sha256(), False)

    def test_every_field_of_a_family_file_is_checked(self):
        def variant(**over):
            doc = json.loads(json.dumps(self.doc))
            doc.update(over)
            return doc

        def with_base(**over):
            doc = json.loads(json.dumps(self.doc))
            doc["base"].update(over)
            return doc
        bad = {
            "unknown top key": variant(extra=1), "missing key": {k: v for k, v in self.doc.items() if k != "reference"},
            "name not the stem": variant(family="X2"), "reserved name": variant(family="ALL"),
            "absolute reference": variant(reference="/tmp/r.jsonl"), "parent reference": variant(reference="../r.jsonl"),
            "not a jsonl": variant(reference="experiments/r.txt"), "empty description": variant(description=""),
            "no matches": variant(matches=[]),
            "id of another family": variant(matches=[{"id": "F40/a"}]), "a duplicate id": variant(matches=[{"id": "X1/a"}, {"id": "X1/a"}]),
            "a match with an unknown field": variant(matches=[{"id": "X1/a", "colour": 1}]),
            "an unknown edit set": variant(matches=[{"id": "X1/a", "edits": "nosuch"}]),
            "same country twice": with_base(fixture=[7, 7, 21, 1]), "country 0": with_base(fixture=[0, 19, 21, 1]),
            "country 129": with_base(fixture=[7, 129, 21, 1]), "a kind the builders do not write": with_base(fixture=[7, 19, 21, 4]),
            "a calendar number 0": with_base(fixture=[7, 19, 0, 1]), "managed outside": with_base(managed=3),
            "seed 65536": with_base(seed=65536), "seed negative": with_base(seed=-1), "seed a bool": with_base(seed=True),
            "delay 6": with_base(delay_byte=6), "budget 256": with_base(substitutions=256), "budget triple": with_base(substitutions=[1, 2, 3]),
            "edits not a list": with_base(edits={}), "an edit with an unknown op": with_base(edits=[
                {"target": "squad", "country": 19, "offset": 4, "op": "mul", "value": 2}]),
            "an edit past the record": with_base(edits=[{"target": "squad", "country": 19, "offset": 20, "op": "set", "value": 1}]),
            "an edit of country 0": with_base(edits=[{"target": "country", "country": 0, "offset": 1, "op": "set", "value": 1}]),
            "an edit value 256": with_base(edits=[{"target": "country", "country": 7, "offset": 1, "op": "set", "value": 256}]),
            "an edit with a spare key": with_base(edits=[{"target": "country", "country": 7, "offset": 1, "op": "set", "value": 1, "x": 1}]),
            "a bad edit in an edit set no match uses": variant(edit_sets={**self.doc["edit_sets"], "unused": [
                {"target": "squad", "country": 19, "offset": 99, "op": "set", "value": 1}]}),
            "an unknown policy": with_base(policy={"name": "Nope", "contexts": ["half_time"]}),
            "a policy with an unknown parameter": with_base(policy={"name": "PlayOn", "contexts": ["half_time"], "speed": 1}),
            "a policy without contexts": with_base(policy={"name": "PlayOn"}),
            "a context that does not exist": with_base(policy={"name": "PlayOn", "contexts": ["lunch"]}),
            "a pause at minute 0": with_base(policy={"name": "Decisions", "contexts": ["pause"], "pause_at": [0]}),
            "a quick speed 6": with_base(policy={"name": "Quick", "contexts": ["pause"], "speed": 6}),
            "the base lacks a field": with_base(), }
        del bad["the base lacks a field"]
        for name, doc in bad.items():
            with self.subTest(name):
                self.write("X1.json", doc)
                with self.assertRaises(families.FamilyError):
                    families.discover(self.dir)
        base = json.loads(json.dumps(self.doc))
        del base["base"]["seed"]
        self.write("X1.json", base)
        with self.assertRaises(families.FamilyError):
            families.discover(self.dir)                  # neither the match nor the base gives the seed

    def test_json_is_read_strictly(self):
        text = json.dumps(self.doc)
        for name, bad in {"duplicate key": text.replace('"family": "X1"', '"family": "X1", "family": "X1"', 1),
                          "NaN": text.replace('"seed": 5', '"seed": NaN', 1), "1e999": text.replace('"value": 3', '"value": 1e999', 1),
                          "not json": "{"}.items():
            with self.subTest(name):
                self.write("X1.json", bad)
                with self.assertRaises(families.FamilyError):
                    families.discover(self.dir)

    def test_two_families_are_found_and_an_empty_directory_is_refused(self):
        self.write("X1.json", self.doc)
        other = json.loads(json.dumps(self.doc))
        other["family"] = "X2"
        other["matches"] = [{"id": "X2/a"}]
        self.write("X2.json", other)
        self.assertEqual(sorted(families.discover(self.dir)), ["X1", "X2"])
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(families.FamilyError):
                families.discover(empty)

    def test_select_asks_for_known_distinct_families(self):
        found = families.discover()
        self.assertEqual([f.name for f in families.select("ALL", found)], ["F40", "O8", "S"])
        self.assertEqual([f.name for f in families.select("S,F40", found)], ["S", "F40"])
        for bad in ("F41", "F40,F40", "", "all", "F40,"):
            with self.subTest(bad):
                with self.assertRaises(families.FamilyError):
                    families.select(bad, found)


class TheEdits(unittest.TestCase):
    def setUp(self):
        self.countries = [bytes(families.COUNTRY_SIZE)] * 129
        squad = (b"".join(w.to_bytes(2, "little") for w in (1, 2, 3)) + bytes(34))
        self.countries[5] = squad + bytes(families.COUNTRY_SIZE - 40)
        self.players = [bytes([0] * 4 + [100, 0, 0, 0, 0, 0, 0, 0, 7] + [0] * 7)] * 10
        self.players[3] = bytes([9] * families.PLAYER_SIZE)

    def edit(self, **kw):
        e = {"target": "squad", "country": 5, "offset": 4, "op": "set", "value": 1}
        e.update(kw)
        return families.apply_edits(self.players, self.countries, [e])

    def test_squad_edits_touch_the_named_squad_only(self):
        players, _ = self.edit(op="set", value=77)
        self.assertEqual([p[4] for p in players[:4]], [100, 77, 77, 77])
        self.assertEqual(players[4][4], 100)
        self.assertEqual(self.players[1][4], 100)          # the inputs are not changed

    def test_ops_set_add_xor_or_and_the_clamps(self):
        self.assertEqual(self.edit(op="add", value=-30)[0][1][4], 70)
        self.assertEqual(self.edit(op="add", value=-255)[0][1][4], 0)
        self.assertEqual(self.edit(op="add", value=255)[0][1][4], 255)
        self.assertEqual(self.edit(op="xor", value=0x0F)[0][1][4], 100 ^ 0x0F)
        self.assertEqual(self.edit(op="or", value=0x80)[0][1][4], 100 | 0x80)

    def test_a_country_edit_changes_the_country_record(self):
        _, countries = self.edit(target="country", country=5, offset=0x2D, op="or", value=8)
        self.assertEqual(countries[5][0x2D], 8)
        self.assertEqual(countries[6][0x2D], 0)

    def test_edits_apply_in_order(self):
        e = [{"target": "squad", "country": 5, "offset": 4, "op": "set", "value": 10},
             {"target": "squad", "country": 5, "offset": 4, "op": "add", "value": 5}]
        self.assertEqual(families.apply_edits(self.players, self.countries, e)[0][1][4], 15)


# ---- the runner over a stand-in for the kit ---------------------------------------------------------------------
class FakeUnicorn:
    def __init__(self):
        self.code_hooks = {}

    def hook_add(self, kind, callback, begin=1, end=0):
        self.code_hooks.setdefault(begin, []).append((end, callback))


class FakeMachine:
    DS, load = 0x2DA4, 0x823

    def __init__(self):
        self.mem = bytearray((i * 31 + i // 251) % 256 for i in range(0x110000))
        self.hooks = {}
        self.uc = FakeUnicorn()

    def lin(self, address):
        seg, off = address.split(":")
        return ((self.load + int(seg, 16)) & 0xFFFF) * 16 + int(off, 16)

    def execute(self, address, times=1):
        """The guest executes `address` `times` times: Unicorn calls every code hook registered there."""
        for _ in range(times):
            for _end, cb in self.uc.code_hooks.get(self.lin(address), []):
                cb(None, self.lin(address), 1, None)

    def read(self, linear, n):
        return bytes(self.mem[linear:linear + n])

    def rd(self, off, n=2):
        a = self.DS * 16 + off
        return int.from_bytes(self.mem[a:a + n], "little")

    def at(self, address, handler):
        self.hooks[address] = handler

    def far(self, off):
        return {0xA96A: 0xB8000, 0xA96E: 0x3C750, 0xA972: 0x3D6F0}[off]      # the text page and the two text buffers


class FakeMatch:
    """A stand-in for original_match.Match: `script` is [(kind, minute, data)] and the machine is FakeMachine."""
    script = ()
    seen = []
    on_events = []          # functions called with the match when its events start

    def __init__(self, image, fixture, **kw):
        type(self).seen.append((fixture, kw))
        self.m = FakeMachine()
        self.st = {"draws": [[1, 0, 1, 2], [1, 1, 2, 3], [1, 2, 3, 4], [2, 0, 4, 5], [2, 1, 5, 6], [90, 0, 6, 7], [2, 2, 7, 8]]}
        self.answers, self.pauses, self.minute = [], 0, 0

    def events(self):
        for fn in self.on_events:
            fn(self)
        for kind, minute, data in self.script:
            self.minute = minute
            yield original_match.Event(kind, minute, (0, 0), data)

    def answer(self, **kw):
        self.answers.append(kw)

    def pause(self):
        self.pauses += 1

    def result(self):
        stats = {n: [i, i + 1] for i, n in enumerate(records.STAT_NAMES)}
        return {"score": [1, 0], "ticks": 55, "half_time_score": [0, 0], "goals": [], "goals_disallowed": [],
                "bookings": [], "sendings_off": [], "injuries": [], "substitutions": [], "man_of_the_match": 9,
                "seed_after": 1, "squads_after": {}, "kind": 1, "winner": 0, "score_90": None, "extra_time": False,
                "shootout": None, "substitution_budget": [5, 5], "players": [],
                "board": {"statistics": stats, "bars": [[1, 2], [3, 4]], "man_of_the_match": 9, "final_score": [1, 0],
                          "seed": 77, "screen_sha256": dg("screen")},
                "commentary": [{"template": 3, "text": "Smith shoots"}, {"template": 3, "text": "x"}, {"template": 0, "text": "y"}]}


class FakeImage:
    def players(self):
        return [bytes(families.PLAYER_SIZE)] * 3061

    def countries(self):
        squad = b"".join(w.to_bytes(2, "little") for w in (1, 2, 3)) + bytes(34)
        return [bytes(families.COUNTRY_SIZE)] * 19 + [squad + bytes(families.COUNTRY_SIZE - 40)] + [bytes(families.COUNTRY_SIZE)] * 109


PLAIN_SCRIPT = (("minute", 1, {}), ("commentary", 1, {"text": "a"}), ("minute", 2, {}), ("decision", 46, {"context": "half_time"}),
                ("full_time", 90, {}), ("end", 90, {}))


class RunMatch(unittest.TestCase):
    def setUp(self):
        FakeMatch.script, FakeMatch.seen, FakeMatch.on_events = PLAIN_SCRIPT, [], []
        patcher = mock.patch.object(original_match, "Match", FakeMatch)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.spec = FAMILIES["F40"].matches[0]
        self.edited = next(m for m in FAMILIES["F40"].matches if m.edits)

    def run_one(self, spec=None, **kw):
        return family.run_match(FakeImage(), spec or self.spec, **kw)

    def test_a_record_is_valid_and_complete(self):
        r = self.run_one()
        records.validate(r)
        self.assertTrue(records.is_completed(r))
        self.assertEqual((r["id"], r["family"], r["spec_sha256"], r["image_sha256"]), (self.spec.id, "F40", self.spec.sha256, IMAGE))
        self.assertEqual(r["decisions"], [[46, "half_time"]])
        self.assertEqual(r["templates"], {"0": 1, "3": 2})
        self.assertEqual(r["events"]["count"], len(PLAIN_SCRIPT))
        self.assertEqual(r["counts"], {})

    def test_the_draws_are_counted_and_digested_per_minute(self):
        r = self.run_one()
        draws = FakeMatch.seen and FakeMatch(None, None).st["draws"]
        self.assertEqual(r["draws"]["count"], 7)
        self.assertEqual(r["draws"]["digest"], records.draws_digest(draws))
        self.assertEqual([row[:2] for row in r["draws"]["per_minute"]], [[1, 3], [2, 2], [90, 1], [2, 1]])    # the clock can go back
        self.assertEqual(r["draws"]["per_minute"][0][2], records.draws_digest(draws[:3]))

    def test_the_fixture_seed_budget_and_edits_reach_the_kit(self):
        self.run_one()
        fixture, kw = FakeMatch.seen[0]
        self.assertEqual((fixture.first, fixture.second, fixture.index, fixture.kind), (7, 19, 21, 1))
        self.assertEqual((kw["managed"], kw["seed"], kw["delay_byte"], kw["record_draws"]), (7, self.spec.seed, 0, True))
        self.assertIsNone(kw["players"])
        self.run_one(self.edited)
        _, kw = FakeMatch.seen[1]
        self.assertEqual(kw["players"][1][14], 12)           # the squad's energy byte, set by the edit
        self.assertEqual(kw["countries"][19][0x2D], 42)      # 0 xor 42

    def test_a_stray_decision_is_recorded_and_played_on(self):
        FakeMatch.script = (("decision", 20, {"context": "pause"}), ("decision", 46, {"context": "half_time"}),
                            ("full_time", 90, {}))
        r = self.run_one()
        records.validate(r)
        self.assertEqual(r["strays"], ["pause"])
        self.assertFalse(records.is_completed(r))
        self.assertIsNotNone(r["score"])                     # the match finished: its evidence is kept

    def test_no_board_is_not_completed(self):
        FakeMatch.script = (("minute", 1, {}),)
        r = self.run_one()
        self.assertFalse(r["stopped_at_board"])
        self.assertFalse(records.is_completed(r))

    def test_an_error_is_a_record_without_evidence(self):
        def boom(m):
            raise RuntimeError("the original did something\nSecret Name scores in the 13th minute")
        FakeMatch.on_events = [boom]
        r = self.run_one()
        records.validate(r)
        self.assertEqual(r["error"], "RuntimeError: the original did something")
        for key in records.EVIDENCE:
            self.assertIsNone(r[key])
        self.assertFalse(records.is_completed(r))

    def test_the_error_text_is_one_clean_line(self):
        for message, expect in (("café \x07 bell", "RuntimeError: caf? ? bell"), ("   ", "RuntimeError:"),
                                ("x" * 500, None), ("", "RuntimeError:")):
            with self.subTest(message[:10]):
                text = family.clean_error(RuntimeError(message))
                self.assertRegex(text, records.ERROR_TEXT)
                self.assertLessEqual(len(text), 200)
                if expect:
                    self.assertEqual(text, expect)

    def test_the_time_limit_is_a_record(self):
        FakeMatch.on_events = [lambda m: time.sleep(0.05)]
        r = self.run_one(time_limit=0.01)
        records.validate(r)
        self.assertIn("TimeLimit", r["error"])
        self.assertFalse(records.is_completed(r))

    def test_a_pause_is_made_once_at_its_minute(self):
        spec = next(m for m in FAMILIES["S"].matches if m.id == "S/decisions-70")
        script = (("minute", 19, {}), ("minute", 20, {}), ("minute", 20, {}), ("minute", 21, {}), ("minute", 60, {}),
                  ("decision", 46, {"context": "half_time", "eleven": list(range(11)), "bench": list(range(11, 20)),
                                    "injured": [], "tactics": 0, "refused": None}),
                  ("full_time", 90, {}))
        FakeMatch.script = script
        pauses = []
        orig = FakeMatch.pause
        with mock.patch.object(FakeMatch, "pause", lambda self: (pauses.append(self.minute), orig(self))):
            r = self.run_one(spec)
        self.assertEqual(pauses, [20, 60])
        self.assertTrue(records.is_completed(r))

    @unittest.skipUnless(HAVE_UNICORN, "unicorn is not installed (family.py imports its hook constant for --count)")
    def test_count_counts_each_execution_of_each_address(self):
        def fire(m):
            m.m.execute("0791:970C", 3)
            m.m.execute("0791:9B15")
        FakeMatch.on_events = [fire]
        r = self.run_one(counts=["0791:970C", "0791:9B15", "0791:A10A"])
        self.assertEqual(r["counts"], {"0791:970C": 3, "0791:9B15": 1, "0791:A10A": 0})
        self.assertEqual(self.run_one()["counts"], {})

    def test_memory_digests_one_per_kib_of_ds_and_of_each_range(self):
        r = self.run_one()
        machine = FakeMachine()
        ds = machine.read(machine.DS * 16, 0x10000)
        self.assertEqual(r["after"]["ds"], records.block_digests(ds))
        self.assertEqual(len(r["after"]["ds"]), 64)
        self.assertEqual(r["after"]["seed"], machine.rd(0x7B62))
        for name, (start, length) in records.RANGES.items():
            self.assertEqual(r["after"]["ranges"][name], records.block_digests(machine.read(machine.load * 16 + start, length)))

    def test_one_changed_byte_changes_one_digest(self):
        base = self.run_one()["after"]
        for k in (0, 17, 63):
            FakeMatch.on_events = [lambda m, k=k: m.m.mem.__setitem__(m.m.DS * 16 + k * 1024 + 5, 0xEE)]
            after = self.run_one()["after"]
            changed = [i for i in range(64) if after["ds"][i] != base["ds"][i]]
            self.assertEqual(changed, [k])
        for name, (start, length) in records.RANGES.items():
            last = length - 1
            FakeMatch.on_events = [lambda m, a=start + last: m.m.mem.__setitem__(m.m.load * 16 + a, 0xEE)]
            after = self.run_one()["after"]
            self.assertEqual([i for i, h in enumerate(after["ranges"][name]) if h != base["ranges"][name][i]],
                             [last // 1024], name)
            self.assertEqual(after["ds"], base["ds"])

    def test_a_write_outside_the_declared_ranges_is_an_error(self):
        base = FakeMachine.load * 16
        outside = [base + 5, 0x1000, 0xA0000, 0x10FFFF, base + 262990 - 1,
                   base + max(s + n for s, n in records.RANGES.values())]
        for address in outside:
            FakeMatch.on_events = [lambda m, a=address: m.m.mem.__setitem__(a, m.m.mem[a] ^ 0xFF)]
            r = self.run_one()
            with self.subTest(address=hex(address)):
                records.validate(r)
                self.assertRegex(r["error"], r"^UndeclaredWrite: 1 bytes changed outside the declared ranges, first at P\+0x")
                self.assertIsNone(r["after"])

    def test_the_write_watch_run_leaves_the_undeclared_write_check_out(self):
        FakeMatch.on_events = [lambda m: m.m.mem.__setitem__(0x1000, m.m.mem[0x1000] ^ 0xFF)]
        self.assertIsNotNone(self.run_one()["error"])
        self.assertIsNone(self.run_one(check_writes=False)["error"])

    def test_a_write_inside_ds_a_range_or_the_screen_is_no_error(self):
        base, ds = FakeMachine.load * 16, FakeMachine.DS * 16
        inside = [ds, ds + 0xFFFF, 0xB8000, 0xB8000 + 3999, 0x3C750, 0x3D6F0 + 3999]
        for name, (start, length) in records.RANGES.items():
            inside += [base + start, base + start + length - 1]
        for address in inside:
            FakeMatch.on_events = [lambda m, a=address: m.m.mem.__setitem__(a, m.m.mem[a] ^ 0xFF)]
            with self.subTest(address=hex(address)):
                self.assertIsNone(self.run_one()["error"])

    def test_a_byte_written_back_as_it_was_is_no_change(self):
        FakeMatch.on_events = [lambda m: m.m.mem.__setitem__(0x1000, m.m.mem[0x1000])]
        self.assertIsNone(self.run_one()["error"])

    def test_the_mask_covers_what_it_names_and_nothing_else(self):
        FakeMatch.on_events = [lambda m: m.m.mem.__setitem__(m.m.DS * 16 + 3 * 1024 + 7, 0xEE)]
        masked = self.run_one(mask=[["DS", 3 * 1024 + 7, 1]])
        unmasked = self.run_one()
        FakeMatch.on_events = []
        untouched = self.run_one(mask=[["DS", 3 * 1024 + 7, 1]])
        self.assertEqual(masked["after"], untouched["after"])        # the changed byte is not seen
        self.assertNotEqual(unmasked["after"]["ds"][3], masked["after"]["ds"][3])
        self.assertEqual(masked["mask"], [["DS", 3 * 1024 + 7, 1]])
        self.assertEqual(unmasked["mask"], [])
        FakeMatch.on_events = [lambda m: m.m.mem.__setitem__(m.m.DS * 16 + 3 * 1024 + 7, 0xEE)]
        wrong = self.run_one(mask=[["DS", 5 * 1024, 1]])             # a mask elsewhere masks nothing here
        self.assertEqual(wrong["after"]["ds"][3], unmasked["after"]["ds"][3])

    def test_a_p_space_mask_covers_the_ranges(self):
        name, (start, length) = next(iter(records.RANGES.items()))
        mask = [["P", start + 10, 1]]
        FakeMatch.on_events = [lambda m: m.m.mem.__setitem__(m.m.load * 16 + start + 10, 0xEE)]
        changed = self.run_one()["after"]["ranges"][name]
        changed_masked = self.run_one(mask=mask)["after"]["ranges"][name]
        FakeMatch.on_events = []
        plain_masked = self.run_one(mask=mask)["after"]["ranges"][name]
        plain = self.run_one()["after"]["ranges"][name]
        self.assertNotEqual(changed[0], plain[0])
        self.assertEqual(changed_masked, plain_masked)         # the changed byte is not seen
        self.assertNotEqual(plain_masked[0], plain[0])         # a masked byte reads as zero
        self.assertEqual(plain_masked[1:], plain[1:])          # and no other block moves


class SpanArithmetic(unittest.TestCase):
    def test_merge_joins_spans_within_the_gap(self):
        self.assertEqual(family.merge([[10, 20], [0, 5], [20, 30], [31, 40]]), [[0, 5], [10, 30], [31, 40]])
        self.assertEqual(family.merge([[10, 20], [0, 5], [20, 30], [31, 40]], gap=1), [[0, 5], [10, 40]])
        self.assertEqual(family.merge([[0, 100], [10, 20]]), [[0, 100]])
        self.assertEqual(family.merge([]), [])

    def test_subtract_cuts_a_span_out(self):
        self.assertEqual(family.subtract([[0, 100]], [40, 60]), [[0, 40], [60, 100]])
        self.assertEqual(family.subtract([[0, 100], [200, 300]], [50, 250]), [[0, 50], [250, 300]])
        self.assertEqual(family.subtract([[0, 10]], [10, 20]), [[0, 10]])
        self.assertEqual(family.subtract([[0, 10]], [0, 10]), [])

    def test_undeclared_changes_ignore_the_allowed_spans_and_rewrites(self):
        before = bytes(100)
        after = bytearray(before)
        after[5], after[50], after[51], after[90] = 1, 2, 3, 4
        self.assertEqual(family.undeclared_changes(before, bytes(after), [(0, 10)]), [[50, 52], [90, 91]])
        self.assertEqual(family.undeclared_changes(before, bytes(after), [(0, 100)]), [])
        self.assertEqual(family.undeclared_changes(before, before, []), [])


class Masks(unittest.TestCase):
    def test_apply_mask(self):
        buf = bytes([1] * 100)
        self.assertIs(records.apply_mask(buf, "DS", 0, []), buf)
        out = records.apply_mask(buf, "DS", 1000, [["DS", 1010, 5], ["P", 1020, 5], ["DS", 1095, 20]])
        self.assertEqual(out, bytes([1] * 10 + [0] * 5 + [1] * 80 + [0] * 5))


# ---- the command ------------------------------------------------------------------------------------------------
class TheCommand(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "out.jsonl"
        self.o8 = FAMILIES["O8"].matches

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(FAMILY_PY), *args], capture_output=True, text=True, cwd=ROOT)

    def write(self, recs):
        self.out.write_text("".join(json.dumps(r) + "\n" for r in recs))

    def stub(self, spec):
        r = record(spec.id)
        return dict(r, cpu_s=1.0)

    def test_refused_commands_exit_2(self):
        out = str(self.out)
        for args in (("--family", "O8"), ("--family", "O8", "--out", out, "--find-ranges", out + "2"),
                     ("--family", "O8", "--out", out, "--max", "0"), ("--family", "NOPE", "--out", out),
                     ("--family", "O8", "--out", out, "--count", "0791:970c"), ("--family", "O8", "--out", out, "--count", "0791:970C,0791:970C"),
                     ("--family", "O8", "--out", out, "--mask", str(Path(self.tmp.name) / "none.json")),
                     ("--family", "O8", "--out", out, "--only", "O8/nosuch"), ("--family", "O8", "--out", out, "--time-limit", "0"),
                     ("--family", "O8", "--out", out, "--workers", "3")):
            with self.subTest(args):
                self.assertEqual(self.cli(*args).returncode, 2, args)
        self.assertFalse(self.out.exists())

    def test_a_bad_mask_file_is_refused(self):
        p = Path(self.tmp.name) / "mask.json"
        for text in ('[["DS", 0]]', '[["DS", 5, 1], ["DS", 0, 1]]', '{"a": 1}', '[["DS", 0, 1], ["DS", 0, 1]]', "NaN"):
            p.write_text(text)
            with self.subTest(text):
                self.assertEqual(self.cli("--family", "O8", "--out", str(self.out), "--mask", str(p)).returncode, 2)

    def test_a_complete_log_runs_nothing_and_is_not_rewritten(self):
        self.write([self.stub(m) for m in self.o8])
        before = self.out.read_bytes()
        r = self.cli("--family", "O8", "--out", str(self.out))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("0 to run", r.stdout)
        self.assertEqual(self.out.read_bytes(), before)

    def test_an_incomplete_match_in_the_log_fails_the_command_and_is_not_rerun(self):
        recs = [self.stub(m) for m in self.o8]
        recs[2] = incomplete(self.o8[2].id)
        self.write(recs)
        before = self.out.read_bytes()
        r = self.cli("--family", "O8", "--out", str(self.out))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(self.o8[2].id, r.stdout)
        self.assertEqual(self.out.read_bytes(), before)

    def test_a_log_that_is_not_this_runs_is_refused_and_left_alone(self):
        good = [self.stub(m) for m in self.o8]
        cases = {"an id not selected": good + [record(F40[0])], "an id twice": good + [good[0]],
                 "another declaration": [dict(good[0], spec_sha256=dg("other"))] + good[1:],
                 "another image": [dict(good[0], image_sha256=dg("other"))] + good[1:],
                 "another mask": [dict(good[0], mask=[["DS", 0, 8]])] + good[1:],
                 "an invalid record": [dict(good[0], ticks=-1)] + good[1:]}
        for name, recs in cases.items():
            self.write(recs)
            before = self.out.read_bytes()
            with self.subTest(name):
                r = self.cli("--family", "O8", "--out", str(self.out))
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertEqual(self.out.read_bytes(), before)
        self.out.write_text("".join(json.dumps(r) + "\n" for r in good).rstrip("\n"))      # a killed run's half line
        before = self.out.read_bytes()
        self.assertEqual(self.cli("--family", "O8", "--out", str(self.out)).returncode, 2)
        self.assertEqual(self.out.read_bytes(), before)

    def test_resume_adds_only_the_missing_matches_in_order_and_max_stops_early(self):
        done = [self.stub(m) for m in self.o8[:3]]
        self.write(done)
        before = self.out.read_bytes()
        ran = []

        def run_one(spec):
            ran.append(spec.id)
            return self.stub(spec)
        said = []
        recs = family.run_family(self.o8, str(self.out), max_new=2, run_one=run_one, say=said.append)
        self.assertEqual(ran, [m.id for m in self.o8[3:5]])
        self.assertEqual(len(recs), 5)
        text = self.out.read_bytes()
        self.assertEqual(text[:len(before)], before)                 # no line rewritten: the old bytes are a prefix
        self.assertEqual(len(text.decode().splitlines()), 5)
        ran.clear()
        family.run_family(self.o8, str(self.out), run_one=run_one, say=said.append)
        self.assertEqual(ran, [m.id for m in self.o8[5:]])
        ran.clear()
        family.run_family(self.o8, str(self.out), run_one=run_one, say=said.append)
        self.assertEqual(ran, [])
        self.assertEqual([r["id"] for r in records.read_log(self.out)], [m.id for m in self.o8])

    def test_a_run_appends_each_record_as_its_match_ends(self):
        lines = []

        def run_one(spec):
            lines.append(len(self.out.read_text().splitlines()) if self.out.exists() else 0)
            return self.stub(spec)
        family.run_family(self.o8[:3], str(self.out), run_one=run_one, say=lambda *a: None)
        self.assertEqual(lines, [0, 1, 2])

    def test_find_ranges_never_overwrites_a_file(self):
        existing = Path(self.tmp.name) / "ranges.json"
        existing.write_text("{}")
        r = self.cli("--family", "ALL", "--only", "O8/c1-c2-friendly", "--find-ranges", str(existing))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertEqual(existing.read_text(), "{}")


class TheRanges(unittest.TestCase):
    """The ranges are found once, with a write watch (out/T57/ranges-*.json): every write outside DS and the screen of
    the watched matches lies in a declared range, and the blocks that only hold the screen's text are declared."""

    def reports(self):
        return sorted((E036 / "out/T57").glob("ranges-*.json"))

    def test_every_watched_write_is_in_a_declared_range(self):
        reports = self.reports()
        if not reports:
            self.skipTest("no write-watch report committed")
        for path in reports:
            rep = json.loads(path.read_text())
            spans = [(s, s + n) for s, n in records.RANGES.values()]
            for a, b in rep["written_outside_ds_and_screen"]:
                with self.subTest(report=path.name, span=(a, b)):
                    self.assertTrue(any(lo <= a and b <= hi for lo, hi in spans), (a, b))
            self.assertEqual(sorted(records.SCREEN_DS_BLOCKS), rep["ds_blocks_of_the_screen"])
            written_non_screen = set(rep["ds_blocks_written"]) - set(rep["ds_blocks_of_the_screen"])
            self.assertFalse(written_non_screen & set(records.SCREEN_DS_BLOCKS))

    def test_a_declared_range_lies_in_a_range_the_report_suggests(self):
        for path in self.reports():
            rep = json.loads(path.read_text())
            suggested = [(s, s + n) for s, n in rep["ranges"].values()]
            for name, (start, length) in records.RANGES.items():
                with self.subTest(report=path.name, range=name):
                    self.assertTrue(any(lo <= start and start + length <= hi for lo, hi in suggested))


# ---- one real match ----------------------------------------------------------------------------------------------
@unittest.skipIf(os.environ.get("E036_NO_REAL_MATCH"), "E036_NO_REAL_MATCH is set (the mutation check runs no match)")
@unittest.skipUnless(HAVE_UNICORN, "unicorn is not installed")
@unittest.skipUnless(IMAGE_FILE.is_file(), "the reference image is not in .cache/dl (fetch it with gh, see the kit's README)")
class OneRealMatch(unittest.TestCase):
    def test_seed_0x1234_is_e032s_record_and_count_counts_the_ticks(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "one.jsonl"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = family.main(["--family", "F40", "--only", "F40/e032-1234", "--out", str(out), "--count", "0791:970C",
                                    "--cache", str(IMAGE_FILE.parent)])
            self.assertEqual(code, 0, buf.getvalue())
            (r,) = records.read_log(out)
        want_score, want_ticks, want_draws, want_digest = EXPECTED_FAMILY[0x1234]
        self.assertEqual((r["score"], r["ticks"], r["draws"]["count"], r["draws"]["digest"]),
                         (want_score, want_ticks, want_draws, want_digest))
        self.assertEqual(r["counts"], {"0791:970C": r["ticks"]})
        self.assertTrue(records.is_completed(r))
        self.assertEqual(sum(row[1] for row in r["draws"]["per_minute"]), want_draws)

    def test_the_write_watch_finds_what_is_declared(self):
        """--find-ranges on the quickest match: every span it saw written outside DS and the screen is in a declared
        range, and the DS blocks of the screen's buffers are the declared SCREEN_DS_BLOCKS (read from the live pointers)."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ranges.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = family.main(["--family", "S", "--only", "S/quick-1", "--find-ranges", str(out),
                                    "--cache", str(IMAGE_FILE.parent)])
            self.assertEqual(code, 0, buf.getvalue())
            rep = json.loads(out.read_text())
        spans = [(s, s + n) for s, n in records.RANGES.values()]
        self.assertTrue(rep["written_outside_ds_and_screen"])
        for a, b in rep["written_outside_ds_and_screen"]:
            self.assertTrue(any(lo <= a and b <= hi for lo, hi in spans), (a, b))
        self.assertEqual(rep["ds_blocks_of_the_screen"], list(records.SCREEN_DS_BLOCKS))
        self.assertEqual(rep["records_program_relative"], [records.RANGES["records"][0], sum(records.RANGES["records"])])
        self.assertEqual(rep["matches"], ["S/quick-1"])

    def test_two_workers_play_two_matches_the_same_as_the_reference(self):
        """--workers 2 (run as the script, since a worker process imports it by name): two processes, one match at a
        time each, the records the reference holds (its cpu and wall times apart): the same match in another process is
        the same match."""
        committed = ROOT / FAMILIES["F40"].reference
        if not committed.is_file():
            self.skipTest("the reference is not committed in this tree")
        want = {r["id"]: r for r in records.read_log(committed)}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "two.jsonl"
            r = subprocess.run([sys.executable, "-B", str(FAMILY_PY), "--family", "S", "--only", "S/quick-1,S/quick-30",
                                "--workers", "2", "--out", str(out), "--cache", str(IMAGE_FILE.parent)],
                               capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            got = records.read_log(out)
        self.assertEqual(sorted(x["id"] for x in got), ["S/quick-1", "S/quick-30"])
        for x in got:
            self.assertTrue(records.is_completed(x))
            self.assertEqual({k: v for k, v in x.items() if k not in ("cpu_s", "wall_s")},
                             {k: v for k, v in want[x["id"]].items() if k not in ("cpu_s", "wall_s")})


if __name__ == "__main__":
    unittest.main()
