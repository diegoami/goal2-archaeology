"""T93: independent display expectations, including the shipped Germany length anomaly."""
import unittest
from runtime.decoders.manager import manager_payload, manager_text, screen_text


def record(payload, length=None):
    return bytes([len(payload) if length is None else length])+payload+bytes(12-len(payload))


class ManagerDecoder(unittest.TestCase):
    def test_germany_nul_is_a_blank_cell_not_a_terminator(self):
        self.assertEqual(manager_payload(ord('B'), record(b'Vogts', 6)), b'B Vogts\0')
        self.assertEqual(manager_text(ord('B'), record(b'Vogts', 6)), 'B Vogts ')

    def test_declared_length_not_printable_run_or_zero_termination(self):
        self.assertEqual(manager_text(ord('O'), record(b'Olsenn', 5)), 'O Olsen')
        self.assertEqual(manager_text(ord('X'), record(b'A\0B')), 'X A B')

    def test_space_separator_empty_name_and_full_width(self):
        self.assertEqual(manager_text(ord('X'), record(b'')), 'X ')
        self.assertEqual(manager_text(ord('X'), record(b'ABCDEFGHIJKL')), 'X ABCDEFGHIJKL')
        self.assertEqual(manager_text(0, record(b'')), '  ')

    def test_display_glyphs_preserve_controls_and_non_ascii(self):
        self.assertEqual(manager_text(ord('X'), record(b'A\x01\x82\x7f')), 'X A☺é⌂')
        self.assertEqual(screen_text(bytes(range(32))), ' ☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼')
        self.assertEqual(screen_text(b' A\xff '), ' A\u00a0 ')

    def test_host_rejects_truncated_overwide_or_overrun_record(self):
        for bad in (b'', b'\x01A', b'\x0d'+b'A'*12, b'\x01A'+bytes(12)):
            with self.subTest(record=bad), self.assertRaises(ValueError):
                manager_payload(65, bad)
        for initial in (-1, 256, True, 'B'):
            with self.subTest(initial=initial), self.assertRaises(ValueError):
                manager_payload(initial, record(b'Name'))
