"""T131 / #707 (closing the roles 3/4 part of #400 item 1): the kept CC7B penalty (role 3) and free-kick (role 4) taker
checkpoints, reached by the original's own keys, and the frames a consumer reads from them.

Two tiers, as every test of a private original-byte input here:
- the committed manifest (notes/400-roles34/delivery.json, steps.jsonl, keys-*.json) always runs: it is what a
  consumer recognises each decision by (role, side, highlight, current pick, the caller 6D4E's own return and arguments,
  the Space -> board -> CF3A read) and it fails if a checkpoint is swapped for a generic captain or text-only state;
- the kept bytes (.cache/400-roles34/readback/, docs/requests/400-roles34.md) are re-derived by frames.py when present,
  and each such test is skipped, with its reason, when they are not (CI has no private states).
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
STEPS = ["preceding-wait", "decision-before-space", "space-pitch-read", "return-back-at-selector", "return-accept"]

# case -> (role, side, country, opponent, highlight, current pick, minute, return offset of CC7B's caller 6D4E, its args)
# [confirmed: T131 kept states; 6D4E returns to 6EEF from the penalty caller 6ECF and to 6F92 from the free-kick caller 6F3E, F030/T92]
CASES = {
    "role3": (3, 1, 7, 9, 11, 131, 33, 0x6EEF, [10, 3, 1]),                # Denmark v England, friendly, round 7
    "role4-england": (4, 0, 9, 23, 3, 163, 71, 0x6F92, [11, 4, 0]),        # England v Portugal, round 3 of England's career
    "role4-albania": (4, 1, 1, 5, 10, 10, 58, 0x6F92, [11, 4, 1]),         # Albania v Cyprus, round 3 of Albania's career
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def inputs(case):
    return {i["label"]: i for i in DELIVERY["roles"][case]["inputs"]}


class Manifest(unittest.TestCase):
    def test_both_roles_are_covered_and_nothing_remains(self):
        self.assertEqual(DELIVERY["covered_roles"], [3, 4])
        self.assertEqual(DELIVERY["remaining"], [])
        self.assertEqual(set(DELIVERY["roles"]), set(CASES))

    def test_each_case_has_the_inputs_item_1_names_in_order(self):
        for case in CASES:
            by = inputs(case)
            # the input before the decision, the decision pending, the Space -> board -> CF3A read, back, accepted
            self.assertEqual(list(by), STEPS, case)
            self.assertEqual([by[s]["site"] for s in STEPS[1:]], ["0791:CC54", "0791:CF3A", "0791:CC54", "0791:93C2"], case)
            self.assertEqual([by[s]["kind"] for s in STEPS[1:]],
                             ["set-piece-select", "set-piece-pitch", "set-piece-select", "match-live"], case)
            self.assertTrue(by["preceding-wait"]["poll"], case)                  # a live poll, immediately before
            self.assertTrue(by["decision-before-space"]["poll"], case)           # the decision pending, at the poll
            self.assertFalse(by["space-pitch-read"]["poll"], case)               # the board: a blocking read, not a poll

    def test_the_decision_frame_is_the_role_asked_for_and_not_a_captain(self):
        for case, (role, side, country, opponent, highlight, pick, minute, ret, args) in CASES.items():
            d = inputs(case)["decision-before-space"]
            f = d["frame"]
            self.assertEqual((f["role"], f["side"], f["country"], f["opponent"], f["highlight"], f["pick"], f["minute"]),
                             (role, side, country, opponent, highlight, pick, minute), case)
            self.assertEqual(f["stored_pick"], f["pick"], case)
            self.assertEqual(f["eleven"][f["highlight"] - 1], f["pick"], case)  # the highlight is the current pick
            self.assertEqual(f["chain"][0]["return_offset"], 0xCED9, case)       # the live wait_or_key frame, CC7B's poll
            self.assertEqual(f["chain"][-1]["return_offset"], 0x6D74, case)      # CC7B called from choose_player 6D4E
            # which restart asked: the penalty caller 6ECF returns 6EEF, the free-kick caller 6F3E returns 6F92
            self.assertEqual((d["origin"]["return_offset"], d["origin"]["args"]), (ret, args), case)

    def test_the_board_read_and_the_return_keep_the_same_decision(self):
        for case in CASES:
            by = inputs(case)
            keep = ("role", "side", "country", "opponent", "highlight", "pick", "stored_pick", "eleven", "minute")
            d = by["decision-before-space"]["frame"]
            for name in ("space-pitch-read", "return-back-at-selector"):
                self.assertEqual({k: by[name]["frame"][k] for k in keep}, {k: d[k] for k in keep}, f"{case} {name}")
                self.assertEqual(by[name]["origin"], by["decision-before-space"]["origin"], f"{case} {name}")
            self.assertIsNone(by["return-accept"]["frame"], case)                # play resumed: no CC7B frame is live

    def test_the_keys_are_the_originals_and_each_step_adds_its_one(self):
        for case in CASES:
            keys = json.loads((NOTES / f"keys-{case}.json").read_text())
            self.assertEqual(keys["count"], len(keys["keys"]))
            self.assertEqual(sha(bytes(keys["keys"])), keys["sha256"])
            self.assertTrue(all(0 < k <= 255 for k in keys["keys"]))
            n = len(keys["keys"])
            by = inputs(case)
            self.assertEqual([by[s]["keys"] for s in STEPS], [n, n, n + 1, n + 2, n + 3], case)  # Space, Return, Return
            self.assertEqual(by["preceding-wait"]["keys_sha256"], keys["sha256"], case)
            self.assertEqual(by["decision-before-space"]["keys_sha256"], keys["sha256"], case)

    def test_the_hashes_are_whole_and_name_the_files(self):
        for case in CASES:
            for i in inputs(case).values():
                self.assertRegex(i["sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(i["file"].startswith(f"t131-{i['sha256'][:16]}-{case}-"))
                self.assertTrue(i["private"].startswith("goal2drive:goal2-archaeology/400-roles34-"))

    def test_the_unchanged_core_stops_at_the_decision_it_has_no_entry_for(self):
        for case in ("role3", "role4-england"):
            u = DELIVERY["unchanged_core_stop"][case]
            self.assertEqual((u["site"], u["kind"]), ("0791:CC54", None), case)   # UnknownScreen: no catalogue entry
            self.assertEqual(u["frame"], inputs(case)["decision-before-space"]["frame"], case)   # the very same machine
        # Albania's unchanged Core stops earlier, at a role 3 of its own, so it never reaches that career's role 4
        a = DELIVERY["albania_first_stop"]
        self.assertEqual(a["frame"]["role"], 3)
        self.assertLess(a["frame"]["minute"], inputs("role4-albania")["decision-before-space"]["frame"]["minute"])

    def test_what_was_met_is_recorded_with_the_search_that_found_it(self):
        p = DELIVERY["prompts"]
        self.assertGreaterEqual(p["managed_matches"], 21)
        self.assertGreaterEqual(p["taker_prompts_by_role"]["3"], 2)      # Denmark's rounds 7 and 10, Albania's round 3
        self.assertGreaterEqual(p["taker_prompts_by_role"]["4"], 2)
        for case, entry in DELIVERY["roles"].items():
            self.assertIn(entry["attempt"], DELIVERY["searches"], case)
        # the interrupted search is kept as it ended, not hidden
        self.assertIn("search-c20", DELIVERY["searches"])
        self.assertIn("InterruptError", DELIVERY["searches"]["search-c20"]["error"])


class Collector(unittest.TestCase):
    def test_no_collector_writes_guest_memory_or_registers_or_moves_the_cpu(self):
        attempts = sorted(p.parent.name for p in NOTES.glob("*/collector.py"))
        self.assertGreaterEqual(len(attempts), 12)
        for attempt in attempts:
            src = (NOTES / attempt / "collector.py").read_text()
            for token in ("set_reg", ".wr(", "restore(", "return_from(", ".m.stop(", "mem_write", "reg_write"):
                self.assertNotIn(token, src, f"{attempt}: {token}")

    def test_the_only_host_adapter_is_a_screen_label_for_roles_3_and_4(self):
        for attempt in ("search-r1", "preceding-r1", "search-c9", "search-c1", "preceding-c9", "preceding-c1"):
            src = (NOTES / attempt / "collector.py").read_text()
            self.assertIn("screens._taker=taker", src, attempt)
            self.assertIn("f.byte(bp,4) in (3,4)", src, attempt)
        # the attempts that show the unchanged Core stop install no adapter at all
        for attempt in ("stop-r1", "stop-c9", "stop-c1"):
            src = (NOTES / attempt / "collector.py").read_text()
            self.assertNotIn("adapt()", src.split("def stop(")[1].split("def search(")[0], attempt)


class KeptBytes(unittest.TestCase):
    """Re-derive every frame from the kept bytes: the manifest is not taken on trust."""

    def read(self, item):
        path = READBACK / item["file"]
        if not path.exists():
            self.skipTest(f"{path.relative_to(ROOT)} not present (private; docs/requests/400-roles34.md)")
        raw = path.read_bytes()
        self.assertEqual(sha(raw), item["sha256"])
        return frames.read_g2core(raw)

    def test_every_state_derives_to_its_manifest_frame_and_origin(self):
        for case in CASES:
            for item in DELIVERY["roles"][case]["inputs"]:
                meta, memory = self.read(item)
                if item["frame"] is not None:
                    self.assertEqual(frames.derive(memory, meta["load"], meta["regs"]), item["frame"], f"{case} {item['label']}")
                    self.assertEqual(frames.origin(memory, meta["load"], meta["regs"]), item["origin"], f"{case} {item['label']}")
                self.assertEqual(len(meta["keys"]), item["keys"], f"{case} {item['label']}")

    def test_the_role_byte_in_the_kept_memory_is_the_roles_and_not_forced(self):
        for case, (role, side, *_rest) in CASES.items():
            item = inputs(case)["decision-before-space"]
            meta, memory = self.read(item)
            ss = meta["regs"]["SS"] * 16
            bp = item["frame"]["chain"][-1]["bp"]
            self.assertEqual((memory[ss + bp + 4], memory[ss + bp + 6]), (role, side), case)
            # the keys the Core was given are all in the state: nothing but key codes reached the original
            self.assertEqual(meta["keys"], json.loads((NOTES / f"keys-{case}.json").read_text())["keys"], case)

    def test_the_accepted_pick_is_the_one_the_original_stored(self):
        for case in CASES:
            meta, memory = self.read(inputs(case)["return-accept"])
            f = inputs(case)["decision-before-space"]["frame"]
            ds = (meta["load"] + frames.GOAL_DS_PARAGRAPH) * 16
            stored = int.from_bytes(memory[ds + 0x9976 + 10 * f["side"] + 2 * f["role"]:][:2], "little")
            self.assertEqual(stored, f["pick"], case)

    def test_the_unchanged_core_stop_is_the_decision_machine(self):
        for case in ("role3", "role4-england"):
            u = DELIVERY["unchanged_core_stop"][case]
            path = READBACK / u["file"]
            if not path.exists():
                self.skipTest(f"{path.relative_to(ROOT)} not present (private; docs/requests/400-roles34.md)")
            umeta, umem = frames.read_ucstate(path.read_bytes())
            gmeta, gmem = self.read(inputs(case)["decision-before-space"])
            self.assertEqual((umeta["regs"], umeta["load"]), (gmeta["regs"], gmeta["load"]), case)
            self.assertEqual(umem, gmem[:len(umem)], case)


if __name__ == "__main__":
    unittest.main()
