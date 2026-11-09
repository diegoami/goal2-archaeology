"""T131 / #707 (closing the roles 3/4 part of #400 item 1): the kept CC7B penalty (role 3) and free-kick (role 4) taker
checkpoints, reached by the original's own keys, and the frames a consumer reads from them.

Two tiers, as every test of a private original-byte input here:
- the committed manifest (notes/400-roles34/delivery.json, steps.jsonl, keys-role*.json) always runs: it is what a
  consumer recognises the decision by (role, side, highlight, current pick, the Space -> board -> CF3A read) and what
  fails if a checkpoint is swapped for a generic captain or text-only state;
- the kept bytes (.cache/400-roles34/readback/, python3 tools of notes/400-roles34/verify.py) are re-derived by
  frames.py when present, and the test is skipped, with its reason, when they are not (CI has no private states).
Nothing here executes a guest instruction.
"""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes/400-roles34"
sys.path.insert(0, str(NOTES))
import frames  # noqa: E402

DELIVERY = json.loads((NOTES / "delivery.json").read_text())
READBACK = ROOT / ".cache/400-roles34/readback"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def inputs(role):
    return {i["label"].split("-", 1)[1] if i["label"] != "preceding-wait" else "preceding-wait": i
            for i in DELIVERY["roles"][str(role)]["inputs"]}


class Role3Manifest(unittest.TestCase):
    """The role-3 checkpoint: Denmark v England, friendly, round 7 of the 1992/stage 2 career, minute 33."""

    def setUp(self):
        self.by = inputs(3)

    def test_role3_is_covered_and_the_inputs_are_the_ones_item_1_names(self):
        self.assertIn(3, DELIVERY["covered_roles"])
        # the input before the decision, the decision pending, the Space -> board -> CF3A read, back, accepted
        self.assertEqual(list(self.by), ["preceding-wait", "decision-before-space", "space-pitch-read",
                                         "return-back-at-selector", "return-accept"])
        self.assertEqual([i["site"] for i in self.by.values()],
                         ["0791:93C2", "0791:CC54", "0791:CF3A", "0791:CC54", "0791:93C2"])
        self.assertEqual([i["kind"] for i in self.by.values()],
                         ["match-live", "set-piece-select", "set-piece-pitch", "set-piece-select", "match-live"])

    def test_the_decision_frame_is_a_penalty_taker_not_a_captain(self):
        f = self.by["decision-before-space"]["frame"]
        self.assertEqual((f["role"], f["side"]), (3, 1))                       # CC7B's byte arguments
        self.assertEqual((f["country_name"], f["opponent_name"]), ("Denmark", "England"))
        self.assertEqual((f["highlight"], f["pick"], f["stored_pick"]), (11, 131, 131))
        self.assertEqual(f["eleven"][f["highlight"] - 1], f["pick"])           # the highlight is the current pick
        self.assertEqual(f["chain"][-1]["return_offset"], 0x6D74)              # CC7B called from choose_player 6D4E
        self.assertEqual(f["chain"][0]["return_offset"], 0xCED9)               # the live wait_or_key frame
        self.assertEqual(self.by["decision-before-space"]["poll"], True)       # the decision is pending, at the poll

    def test_the_board_read_and_the_return_keep_the_same_decision(self):
        d = self.by["decision-before-space"]["frame"]
        for name in ("space-pitch-read", "return-back-at-selector"):
            f = self.by[name]["frame"]
            self.assertEqual({k: f[k] for k in ("role", "side", "country", "highlight", "pick", "stored_pick", "eleven", "minute")},
                             {k: d[k] for k in ("role", "side", "country", "highlight", "pick", "stored_pick", "eleven", "minute")}, name)
        self.assertEqual(self.by["space-pitch-read"]["poll"], False)           # a blocking read, not a poll
        self.assertIsNone(self.by["return-accept"]["frame"])                  # play resumed: no CC7B frame is live

    def test_the_keys_are_the_originals_and_each_step_adds_one(self):
        keys = json.loads((NOTES / "keys-role3.json").read_text())
        self.assertEqual(keys["count"], len(keys["keys"]))
        self.assertEqual(sha(bytes(keys["keys"])), keys["sha256"])
        self.assertTrue(all(0 < k <= 255 for k in keys["keys"]))
        n = len(keys["keys"])
        self.assertEqual([i["keys"] for i in self.by.values()], [n, n, n + 1, n + 2, n + 3])
        self.assertEqual(self.by["preceding-wait"]["keys_sha256"], self.by["decision-before-space"]["keys_sha256"])
        self.assertEqual(self.by["decision-before-space"]["keys_sha256"], keys["sha256"])

    def test_the_hashes_are_whole_and_name_the_files(self):
        for i in self.by.values():
            self.assertRegex(i["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(i["file"].startswith(f"t131-{i['sha256'][:16]}-role3-"))
            self.assertTrue(i["private"].startswith("goal2drive:goal2-archaeology/400-roles34-"))

    def test_the_unchanged_core_stops_at_this_very_poll(self):
        u = DELIVERY["unchanged_core_stop"]
        self.assertEqual((u["site"], u["kind"]), ("0791:CC54", None))           # UnknownScreen: no catalogue entry
        self.assertEqual((u["frame"]["role"], u["frame"]["side"], u["frame"]["highlight"], u["frame"]["pick"]), (3, 1, 11, 131))


class Role4Outcome(unittest.TestCase):
    def test_role4_is_either_covered_or_recorded_as_remaining_with_what_was_tried(self):
        r4 = DELIVERY["role4"]
        self.assertEqual(r4["covered"], 4 in DELIVERY["covered_roles"])
        self.assertEqual(r4["covered"], "role4_free_kick" not in DELIVERY["remaining"])
        if not r4["covered"]:
            # the whole deterministic season (rounds 1-26: the terminal boundary) is among the attempts, and no role 4 prompt
            # was met in any managed match, only roles 2, 3 and 5
            self.assertIn("search-r2", r4["attempts"])
            self.assertGreaterEqual(r4["managed_matches"], 21)
            self.assertNotIn("4", r4["taker_prompts_by_role"])
            self.assertEqual(sorted(r4["taker_prompts_by_role"]), ["2", "3", "5"])

    def test_every_search_attempt_is_listed_with_its_rounds_and_status(self):
        for name in DELIVERY["role4"]["attempts"][1:]:
            s = DELIVERY["searches"][name]
            self.assertTrue(s["status"] or s["error"], name)
            self.assertGreaterEqual(s["max_round"], s["first_round"], name)

    def test_a_covered_role4_has_the_same_inputs_with_its_own_role_byte(self):
        if 4 not in DELIVERY["covered_roles"]:
            self.skipTest("no role-4 checkpoint was reached by the original's keys within the bound (see delivery.json)")
        by = inputs(4)
        f = by["decision-before-space"]["frame"]
        self.assertEqual(f["role"], 4)
        self.assertIn(f["side"], (0, 1))
        self.assertEqual([i["site"] for i in by.values()], ["0791:CC54", "0791:CF3A", "0791:CC54", "0791:93C2"])


class Collector(unittest.TestCase):
    def test_no_collector_writes_guest_memory_or_registers_or_moves_the_cpu(self):
        attempts = sorted(p.parent.name for p in NOTES.glob("*/collector.py"))
        self.assertGreaterEqual(len(attempts), 4)
        for attempt in attempts:
            src = (NOTES / attempt / "collector.py").read_text()
            for token in ("set_reg", ".wr(", "restore(", "return_from(", ".m.stop(", "mem_write", "reg_write"):
                self.assertNotIn(token, src, f"{attempt}: {token}")

    def test_the_only_host_adapter_is_a_screen_label_for_roles_3_and_4(self):
        for attempt in ("search-r1", "preceding-r1"):
            src = (NOTES / attempt / "collector.py").read_text()
            self.assertIn("screens._taker=taker", src)
            self.assertIn("f.byte(bp,4) in (3,4)", src)
        # the attempt that shows the unchanged Core stop installs no adapter at all
        self.assertNotIn("adapt()", (NOTES / "stop-r1" / "collector.py").read_text().split("def stop(")[1].split("def search(")[0])


class KeptBytes(unittest.TestCase):
    """Re-derive every frame from the kept bytes: the manifest is not taken on trust."""

    def read(self, item):
        path = READBACK / item["file"]
        if not path.exists():
            self.skipTest(f"{path.relative_to(ROOT)} not present (private; docs/requests/400-roles34.md)")
        raw = path.read_bytes()
        self.assertEqual(sha(raw), item["sha256"])
        return frames.read_g2core(raw)

    def test_every_role3_state_derives_to_its_manifest_frame(self):
        for item in DELIVERY["roles"]["3"]["inputs"]:
            meta, memory = self.read(item)
            if item["frame"] is not None:
                self.assertEqual(frames.derive(memory, meta["load"], meta["regs"]), item["frame"], item["label"])
            self.assertEqual(len(meta["keys"]), item["keys"])

    def test_the_role_byte_in_the_kept_memory_is_3_and_not_forced(self):
        item = inputs(3)["decision-before-space"]
        meta, memory = self.read(item)
        ss = meta["regs"]["SS"] * 16
        chain = item["frame"]["chain"]
        bp = chain[-1]["bp"]
        self.assertEqual((memory[ss + bp + 4], memory[ss + bp + 6]), (3, 1))
        # the keys the Core was given are all in the state: nothing but key codes reached the original
        self.assertEqual(meta["keys"], json.loads((NOTES / "keys-role3.json").read_text())["keys"])

    def test_the_accepted_pick_is_the_one_the_original_stored(self):
        item = inputs(3)["return-accept"]
        meta, memory = self.read(item)
        f = inputs(3)["decision-before-space"]["frame"]
        ds = (meta["load"] + frames.GOAL_DS_PARAGRAPH) * 16
        stored = int.from_bytes(memory[ds + 0x9976 + 10 * f["side"] + 2 * f["role"]:][:2], "little")
        self.assertEqual(stored, f["pick"])


if __name__ == "__main__":
    unittest.main()
