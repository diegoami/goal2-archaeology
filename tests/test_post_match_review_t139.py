"""T139 uses the retained route SDK and the existing review callback."""
import copy
from dataclasses import asdict
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import Match, route
from original_match.machine import MEM_SIZE, REGS
from original_match.match import TEAM_MENU
from original_match.port.tables import from_record, to_record
from tests.test_route_sealed import _fixtures


def cpu(match):
    return match.m.read(0, MEM_SIZE), [match.m.reg(register) for register in REGS]


def play(state, tables, review, quick=False):
    assert sys.implementation.name == "pypy" and sys.version_info[:2] == (3, 11)
    step = route.play_round(state, from_record(tables), route.DEFAULT_KEYS)
    match = step.match
    options = {"post_match_review": True} if review else {}
    match.configure_route_entry(live_players=True, ticks=quick, **options)
    callbacks = []

    def observe_menu(replay):
        if not replay and match.st["menu_context"] == "post_match":
            callbacks.append(match.m.rd(0x9A3E, 1))

    match.m.at(TEAM_MENU, observe_menu)
    events = []
    reviews = 0
    pause_requested = False
    stream = match.events()
    for event in stream:
        if quick and event.kind == "tick" and not pause_requested:
            match.pause()
            pause_requested = True
        if event.kind != "decision" or event.data["context"] != "post_match":
            events.append(asdict(event))
            if event.kind == "decision":
                match.answer(quick=quick and event.data["context"] == "pause")
            continue
        reviews += 1
        assert not match.over
        assert event.data["board"] == next(row["data"] for row in events if row["kind"] == "full_time")
        assert event.data["team_context"]["match_set_up"] == match.m.rd(0xC1E, 1)
        assert event.data["team_context"]["in_match_menu_used"] == match.m.rd(0xC1F, 1)
        before = cpu(match), copy.deepcopy(match.st), copy.deepcopy(match.opts), copy.deepcopy(match._replay_actions)
        native = match.records_after()
        from original_match import Image
        image = Image.from_state(native, from_record(tables))
        for country in event.data["team_context"]["sides"]:
            assert image.squad(country) == match._squad(country)
        assert [[word, image.players()[word].hex()] for word in event.data["eleven"] + event.data["bench"]
                if word] == event.data["player_records"]
        assert native == match.records_after()
        for bad in ({}, {"post_match_exit": 1}, {"post_match_exit": False},
                    {"post_match_exit": True, "quick": True},
                    {"post_match_exit": True, "tactics": {1: True}}):
            try:
                match.answer(**bad)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid review answer accepted")
        assert before == (cpu(match), match.st, match.opts, match._replay_actions)
        saved = Match.load(match.save())
        assert cpu(saved) == cpu(match) and saved.waiting == match.waiting
        saved.answer(post_match_exit=True)
        suffix = [asdict(item) for item in saved.events()]
        match.answer(post_match_exit=True)
        remaining = [asdict(item) for item in stream]
        assert remaining == suffix and cpu(saved) == cpu(match)
        assert saved.result() == match.result()
        events.extend(remaining)
        break
    final = cpu(match)
    result = match.result()
    resumed = route.resume_round(step.continuation, match)
    return reviews, callbacks, events, final, result, resumed.state, resumed.played_fixtures, resumed.news_pages


class Review(unittest.TestCase):
    def test_actual_watched_exit_and_quick_control_preserve_sdk_continuation(self):
        from port_test_runtime import call_in_pypy

        image = _fixtures().image()
        args = image.state(image.tables), to_record(image.tables)
        for quick in (False, True):
            with self.subTest(quick=quick):
                baseline = call_in_pypy("test_post_match_review_t139", "play", args=(*args, False, quick))
                candidate = call_in_pypy("test_post_match_review_t139", "play", args=(*args, True, quick))
                # [confirmed: port/postmatch.py F331] The managed review branch
                # and the quick-result summary-save gate are separate.
                self.assertEqual(baseline[1], [int(quick)])
                self.assertEqual(candidate[0], len(baseline[1]))
                self.assertTrue(candidate[1:] == baseline[1:], "canonical events, CPU, result or round differ")


if __name__ == "__main__":
    unittest.main()
