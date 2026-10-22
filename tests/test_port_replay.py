"""Save/load must reconstruct a suspended Python generator, using synthetic guest bytes only."""
import unittest

from tests.test_port_guest import Synthetic, Machine, END, INSIDE_G, TARGET, registry
from original_match import port
from original_match.match import Match, MatchError, Event, fresh_state


class ReplayMatch(Match, Synthetic):
    def __init__(self):
        self.m = self.machine()
        self.st = fresh_state({})
        self.opts = {"record_draws": False, "managed": 1, "first": 1, "second": 2}
        self.inputs, self.side = [], 0
        self.image_sha256, self.image_header, self.image_tail = "synthetic", b"", b"tail"
        self.end_lin, self.fixture_ptr, self.timeout_s = END, (0, 0), 5
        self._queue = [Event("tick", 0, (0, 0), {})]
        self._menu = self._result = self._names = self.prover = None
        self._hooks()
        self._install_ports(["test"])

    def _install_ports(self, specs):
        self.ports = port.install(self.m, [(registry(), None)])
        self.opts["ports"] = ["test"]
        self.ports.calls.update(self.st.get("port_calls") or {})
        self.st["port_calls"] = self.ports.calls

    def _hooks(self):
        def decision(replay):
            if not replay:
                self._queue.append(Event("decision", 0, (0, 0), {"context": "pause"}))
                self.m.stop("decision")
        self.m.at(INSIDE_G, decision)

    def _squad(self, country):
        return list(range(1, 21)) if country == 1 else list(range(21, 41))

    def _advance(self):
        if self.st["answer"] is not None:
            self.m.write(self.m.DS * 16 + TARGET + 4, bytes([int(self.st["answer"]["quick"])]))
            self.st["answer"] = None
        fresh, self.st["fresh"] = self.st["fresh"], False
        if self.m.run(END, 5, fresh=fresh) is None:
            self.st["over"] = True
            self._result = list(self.m.read(self.m.DS * 16 + TARGET, 5))
            self._queue.append(Event("end", 0, (0, 0), {}))


@unittest.skipIf(Machine is None, "unicorn not installed")
class ReplayTests(unittest.TestCase):
    def decision(self):
        match = ReplayMatch()
        events = match.events()
        self.assertEqual(next(events).kind, "tick")
        match.pause()
        self.assertEqual(next(events).kind, "decision")
        self.assertTrue(match.m.frames)
        return match

    def finish(self, match):
        events = list(match.events())
        self.assertFalse(match.m.frames)
        self.assertEqual(match.result(), [7, 5, 0x34, 0, 1])
        return events, match.result(), match.m.snapshot()

    def test_live_frame_before_and_after_answer_and_repeated_load(self):
        plain = self.decision()
        saved = ReplayMatch.load(plain.save())
        self.assertEqual(saved.waiting, plain.waiting)
        self.assertTrue(saved.m.frames)  # continuation is a real Python generator, not just guest registers
        for match in (plain, saved):
            match.answer(quick=True, tactics={4: True}, own_tactics={1: {2: False}})
        again = ReplayMatch.load(saved.save())
        self.assertIsNone(again.waiting)
        self.assertTrue(again.m.frames)
        self.assertEqual(self.finish(plain), self.finish(again))

    def test_automatic_answer_is_replayed(self):
        match = ReplayMatch()
        match._queue.insert(0, Event("decision", 0, (0, 0), {"context": "pause"}))
        events = match.events()
        self.assertEqual(next(events).kind, "decision")
        self.assertEqual(next(events).kind, "tick")
        self.assertEqual(next(events).kind, "decision")  # first decision answered automatically
        loaded = ReplayMatch.load(match.save())
        self.assertEqual(len(loaded.st["decisions"]), 1)
        loaded.answer(quick=True)
        match.answer(quick=True)
        self.assertEqual(self.finish(loaded), self.finish(match))

    def test_changed_guest_memory_is_rejected(self):
        match = self.decision()
        match.m.write(match.m.DS * 16 + TARGET + 4, b"\x99")
        with self.assertRaisesRegex(MatchError, "reconstructed state differs"):
            ReplayMatch.load(match.save())

    def test_plain_older_checkpoints_still_load(self):
        match = ReplayMatch()
        state, memory = match._save_state()
        for version in ("2", "3"):
            with self.subTest(version=version):
                state["version"] = version
                loaded = ReplayMatch.load(match._encode_save(state, memory))
                self.assertEqual(loaded.m.snapshot(), match.m.snapshot())

    def test_menu_and_proof_still_refused(self):
        match = self.decision()
        match._menu = object()
        with self.assertRaisesRegex(MatchError, "drives a screen"):
            match.save()
        match._menu, match.prover = None, object()
        with self.assertRaisesRegex(MatchError, "proved match"):
            match.save()
