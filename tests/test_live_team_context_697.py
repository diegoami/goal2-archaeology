"""#697 synthetic coordinator boundaries; natural backend proof is separate."""
import copy
import unittest
from tests import test_live_player_records_682 as live


class TeamContext(unittest.TestCase):
    def coordinator(self, enabled=True):
        match, words, records, packets, calls = live.LivePlayers().coordinator(enabled)
        memory = {0xC1E: 1, 0xC1F: 0, 0x9B34: 7, 0x9B36: 19}
        previous = match.m.rd
        def read(address, size=2):
            calls.append(('rd', address, size))
            return memory[address] if address in memory else previous(address, size)
        match.m.rd = read
        return match, memory, packets, calls

    def test_every_decision_samples_raw_visibility_bytes_and_both_side_words(self):
        for context in ('pause', 'half_time', 'substitution', 'substitution_opportunity',
                        'extra_time', 'set_piece', 'shootout_order'):
            for setup, used in ((0, 0), (0, 255), (255, 0), (1, 2)):
                with self.subTest(context=context, setup=setup, used=used):
                    match, memory, packets, calls = self.coordinator()
                    memory.update({0xC1E: setup, 0xC1F: used, 0x9B34: 128, 0x9B36: 7})
                    match._decide(context)
                    self.assertEqual(packets[-1][1].get('team_context'),
                        dict(match_set_up=setup, in_match_menu_used=used, sides=[128, 7]))
                    for address, size in ((0xC1E, 1), (0xC1F, 1), (0x9B34, 2), (0x9B36, 2)):
                        self.assertEqual(calls.count(('rd', address, size)), 1)
                    self.assertEqual(calls[0], ('flush',))
                    self.assertEqual(calls[-1], ('stop', 'decision'))

    def test_context_is_fresh_and_previous_emitted_packet_does_not_change(self):
        match, memory, packets, calls = self.coordinator()
        match._decide('pause')
        first = copy.deepcopy(packets[-1])
        memory.update({0xC1E: 9, 0xC1F: 255, 0x9B34: 19, 0x9B36: 7})
        match._decide('half_time')
        self.assertEqual(packets[0], first)
        self.assertEqual(packets[-1][1].get('team_context'),
                         dict(match_set_up=9, in_match_menu_used=255, sides=[19, 7]))

    def test_default_and_false_preserve_legacy_context_omission_and_reads(self):
        for enabled in (None, False):
            match, memory, packets, calls = self.coordinator(enabled)
            match._decide('half_time')
            self.assertNotIn('team_context', packets[-1][1])
            self.assertFalse(any(call[0] == 'rd' and call[1] in memory for call in calls))

    def test_checkpoint_round_trip_retains_raw_context_without_changing_old_payloads(self):
        from original_match.match import Match, VERSION
        match, memory, packets, calls = self.coordinator()
        match._decide('pause')
        waiting = packets[-1][1]
        self.assertIn('team_context', waiting)
        for current in (waiting, {key: value for key, value in waiting.items() if key != 'team_context'}):
            state = dict(version=VERSION, opts={'live_players': True}, st={'waiting': current})
            blob = Match._encode_save(state, b'synthetic-memory')
            _, loaded, _ = Match._checkpoint_state(blob)
            self.assertEqual(loaded, state)

    def test_original_performance_visibility_and_side_selection_use_exact_context(self):
        from decoders.team_performance import shown, match_side
        for setup, used in ((0, 0), (0, 3), (255, 0), (1, 128)):
            match, memory, packets, calls = self.coordinator()
            memory.update({0xC1E: setup, 0xC1F: used})
            match._decide('pause')
            context = packets[-1][1].get('team_context')
            self.assertIsNotNone(context)
            self.assertEqual(shown(context['match_set_up'], context['in_match_menu_used']), bool(setup and used))
            self.assertEqual(match_side(7, context['sides']), 0)
            self.assertEqual(match_side(19, context['sides']), 1)


if __name__ == '__main__':
    unittest.main()
