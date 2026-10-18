"""runtime/original_match/port/runtime.py (T60): the runtime primitives, on synthetic memory (no byte of the original).

Each test gives a port the stack arguments and registers of the listing's call on plain memory (port/mem.py PlainMem)
and compares memory, AX, DX and the flag the routine leaves with values worked out from the listing by hand. The
branches the 62 matches of ALL never reach (0CCB, 0CF4 mostly, 0676, 072F, 0787, 07DB, 08BF, the negative wrap-add,
the upper clamp, a negative dividend of 0294, a truncated or saturated string) are here. FuzzAgainstOriginal runs each
port against the original's own code on random inputs when the reference image is in .cache/dl and unicorn is
installed (T60's out/T60/fuzz.py; CI has neither and skips it)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import port  # noqa: E402
from original_match.port import runtime  # noqa: E402
from original_match.port.mem import PlainMem, PortError  # noqa: E402

S = 0x4000                  # a data segment for the buffers (linear 0x40000)
SIZE = 0x60000
DF, CF, ZF, SF = 0x400, 1, 0x40, 0x80


class Rig:
    """Plain memory with a stack at SS:0x2000 and the DS of the image's layout."""

    def __init__(self):
        self.mem = PlainMem(bytearray(SIZE))
        self.mem.regs.update(ss=0, sp=0x2000, ds=self.mem.DS, eflags=0x202)

    def poke(self, off, data, seg=S):
        self.mem.memory[seg * 16 + off:seg * 16 + off + len(data)] = bytes(data)

    def peek(self, off, n, seg=S):
        return bytes(self.mem.memory[seg * 16 + off:seg * 16 + off + n])

    def pstr(self, off, text, seg=S):
        self.poke(off, bytes([len(text)]) + text, seg)

    def ds_poke(self, off, data):
        self.poke(off, data, self.mem.DS)

    def run(self, address, args=(), far=None, variant=None, **regs):
        entry = port._module_registry("runtime").entries[address]
        far = entry.far if far is None else far
        sp = 0x2000
        layout = [0x1234] + ([0x5678] if far else []) + [a & 0xFFFF for a in args]
        for i, w in enumerate(layout):
            self.mem.memory[sp + 2 * i:sp + 2 * i + 2] = (w & 0xFFFF).to_bytes(2, "little")
        self.mem.regs["sp"] = sp
        for k, v in regs.items():
            self.mem.regs[k] = v
        self.mem._entries.append((sp, far))
        try:
            out = entry.fn(self.mem, variant)
            if out is not None and hasattr(out, "send"):
                raise AssertionError("a runtime port does not call the original")
        finally:
            self.mem._entries.pop()
        return self.mem.regs

    def writes(self):
        return self.mem.regs


class FillAndMove(unittest.TestCase):
    def test_fill_words_wraps_in_the_segment_and_leaves_ax_and_cx(self):
        r = Rig()
        regs = r.run("214B:0000", [0x1234, 3, 0xFFFC, S])
        self.assertEqual(r.peek(0xFFFC, 4), bytes([0x34, 0x12, 0x34, 0x12]))
        self.assertEqual(r.peek(0, 2), bytes([0x34, 0x12]))                # the third word wrapped to offset 0
        self.assertEqual((regs["ax"], regs["cx"], regs["di"]), (0x1234, 0, 2))
        self.assertFalse(regs["eflags"] & DF)

    def test_fill_bytes_uses_the_low_byte_twice_and_the_odd_byte(self):
        r = Rig()
        r.poke(0x100, b"\xEE" * 8)
        regs = r.run("214B:0018", [0x01AB, 5, 0x100, S])
        self.assertEqual(r.peek(0x100, 7), b"\xAB" * 5 + b"\xEE\xEE")
        self.assertEqual(regs["ax"], 0xABAB)

    def test_fill_bytes_zero_count_writes_nothing(self):
        r = Rig()
        r.poke(0x100, b"\xEE" * 2)
        r.run("214B:0018", [0x01AB, 0, 0x100, S])
        self.assertEqual(r.peek(0x100, 2), b"\xEE\xEE")

    def test_move_bytes_overlapping_upwards_goes_backwards_and_leaves_df_set(self):
        r = Rig()
        r.poke(0x100, b"abcdefghij")
        regs = r.run("214B:003C", [7, 0x103, S, 0x100, S])                 # count, dest, src: src <= dest
        self.assertEqual(r.peek(0x100, 10), b"abcabcdefg")                 # as memmove
        self.assertTrue(regs["eflags"] & DF, "the backward copy ends with DF set (no cld follows its std)")
        self.assertEqual((regs["ax"], regs["dx"]), (7, 1))

    def test_move_bytes_overlapping_downwards_goes_forwards_and_clears_df(self):
        r = Rig()
        r.poke(0x100, b"abcdefghij")
        regs = r.run("214B:003C", [7, 0x0FD, S, 0x100, S], eflags=0x202 | DF)
        self.assertEqual(r.peek(0x0FD, 10), b"abcdefgefg", "as memmove: the bytes above the copy are the source's own")
        self.assertFalse(regs["eflags"] & DF)
        self.assertEqual((regs["ax"], regs["dx"]), (7, 1))

    def test_move_bytes_even_count_and_a_zero_count(self):
        r = Rig()
        r.poke(0x100, b"abcdef")
        r.run("214B:003C", [4, 0x200, S, 0x100, S])
        self.assertEqual(r.peek(0x200, 5), b"abcd\x00")
        r.run("214B:003C", [0, 0x300, S, 0x100, S])
        self.assertEqual(r.peek(0x300, 2), b"\x00\x00")

    def test_swap_bytes_exchanges_and_the_ax_low_byte_is_the_last_byte_taken(self):
        r = Rig()
        r.poke(0x100, b"abc")
        r.poke(0x200, b"XYZ")
        regs = r.run("214B:007B", [3, 0x200, S, 0x100, S], ax=0x7700)      # count, b, a
        self.assertEqual((r.peek(0x100, 3), r.peek(0x200, 3)), (b"XYZ", b"abc"))
        self.assertEqual(regs["ax"], 0x7700 | ord("c"))

    def test_swap_bytes_with_a_count_of_zero_swaps_65536_bytes(self):
        r = Rig()
        r.poke(0, bytes([1, 2, 3]), 0x3000)
        r.poke(0xFFFF, b"\x09", 0x3000)
        r.poke(0, bytes([7, 8, 9]), 0x4000)
        r.poke(0xFFFF, b"\x0A", 0x4000)
        r.run("214B:007B", [0, 0, 0x4000, 0, 0x3000])
        self.assertEqual((r.peek(0, 3, 0x3000), r.peek(0xFFFF, 1, 0x3000)), (bytes([7, 8, 9]), b"\x0A"))
        self.assertEqual((r.peek(0, 3, 0x4000), r.peek(0xFFFF, 1, 0x4000)), (bytes([1, 2, 3]), b"\x09"))

    def test_upcase_string_keeps_the_length_and_clips_the_characters_at_0x50(self):
        r = Rig()
        r.pstr(0x100, b"ab{Z`z")
        regs = r.run("214B:009C", [0x100, S, 0x300, S])
        self.assertEqual(r.peek(0x300, 7), bytes([6]) + b"AB{Z`Z")
        self.assertEqual(regs["ax"], ord("Z"))                              # the last character stored
        r = Rig()
        r.poke(0x100, bytes([0x60]) + b"a" * 0x60)
        r.poke(0x300, b"\xEE" * 0x70)
        regs = r.run("214B:009C", [0x100, S, 0x300, S])
        self.assertEqual(r.peek(0x300, 1), bytes([0x60]), "the length byte is the source's, not the clipped one")
        self.assertEqual(r.peek(0x301, 0x50), b"A" * 0x50)
        self.assertEqual(r.peek(0x351, 4), b"\xEE" * 4)


class Screens(unittest.TestCase):
    STREAM = bytes([1, 0, 2, 3, 0xFF, 0x1F, 0x41, 0, 2, 0x42, 0x43, 0x44])

    def test_unpack_screen_attribute_prefix_run_and_row_step(self):
        r = Rig()
        r.poke(0x100, self.STREAM)
        regs = r.run("214B:0147", [0x100, S, 0x2000, S])
        self.assertEqual(r.peek(0x2000, 6), bytes([0x41, 0x1F] * 3))
        self.assertEqual(r.peek(0x20A0, 6), bytes([0x42, 0x1F, 0x43, 0x1F, 0x44, 0x1F]))
        self.assertEqual(regs["ax"], 0x1F44)

    def test_unpack_screen_first_cell_is_one_based(self):
        r = Rig()
        r.poke(0x100, bytes([3, 0, 1, 1, 0x41]))
        r.run("214B:0147", [0x100, S, 0x2000, S])
        self.assertEqual(r.peek(0x2004, 2), bytes([0x41, 0]))

    def test_unpack_via_a_pointer_variable_and_the_row_record(self):
        r = Rig()
        r.poke(0x100, self.STREAM)
        r.poke(0x80, bytes([0x00, 0x30, S & 0xFF, S >> 8]))                # the variable points at S:0x3000
        r.run("214B:0329", [0x80, S, 0x100, S])
        self.assertEqual(r.peek(0x3000, 2), bytes([0x41, 0x1F]))
        r = Rig()
        r.ds_poke(0xA96E, bytes([0x00, 0x30, S & 0xFF, S >> 8]))
        r.ds_poke(0x79A6, self.STREAM[2:])                                  # rows, columns, data after the record
        r.run("214B:05F0", [4])
        self.assertEqual(int.from_bytes(r.peek(0x79A4, 2, r.mem.DS), "little"), 3 * 0x50 + 1,
                         "05F0 writes (row - 1) * 0x50 + 1 to DS:79A4")
        self.assertEqual(r.peek(0x3000 + 3 * 0x50 * 2, 2), bytes([0x41, 0x1F]))
        r = Rig()
        r.ds_poke(0xA96E, bytes([0x00, 0x30, S & 0xFF, S >> 8]))
        r.ds_poke(0x796A, self.STREAM)
        r.run("214B:05DB")
        self.assertEqual(r.peek(0x3000, 2), bytes([0x41, 0x1F]))


class Draw(unittest.TestCase):
    def draw_rig(self, seed):
        r = Rig()
        r.ds_poke(0xA978, bytes([0x62, 0x7B, r.mem.DS & 0xFF, r.mem.DS >> 8]))     # the seed word is DS:7B62
        r.ds_poke(0x7B62, seed.to_bytes(2, "little"))
        return r

    def test_random_is_one_steps_the_seed_and_reports_the_draw(self):
        for seed, n in ((0x1234, 5), (0, 1), (0xFFFF, 2), (0x4000, 33)):
            r = self.draw_rig(seed)
            new = (seed * 0x7ABD + 0x1B0F) & 0xFFFF
            draw = ((new * n) >> 16) + 1
            regs = r.run("214B:06D0", [n], ax=0xAB00)
            self.assertEqual(int.from_bytes(r.peek(0x7B62, 2, r.mem.DS), "little"), new)
            self.assertEqual(regs["dx"], draw)
            self.assertEqual(regs["ax"], draw if draw > 0xFF else (draw & 0xFF00) | (1 if draw == 1 else 0))

    def test_random_is_one_is_one_on_a_draw_of_one(self):
        r = self.draw_rig(0x1234)
        regs = r.run("214B:06D0", [1])                                       # n = 1: the draw is always 1
        self.assertEqual((regs["ax"] & 0xFF, regs["dx"]), (1, 1))


class NumberToString(unittest.TestCase):
    def test_number_to_string_signed_32_bits(self):
        for value, text in ((0, b"0"), (-12345, b"-12345"), (2 ** 31 - 1, b"2147483647"), (-2 ** 31, b"-2147483648"),
                            (10, b"10")):
            r = Rig()
            regs = r.run("214B:09DA", [value & 0xFFFF, (value >> 16) & 0xFFFF, 0x300, S])
            self.assertEqual(r.peek(0x300, 1 + len(text)), bytes([len(text)]) + text, value)
            self.assertEqual((regs["ax"], regs["dx"]), (len(text), r.mem.DS))

    def test_str_of_long_pads_to_width_and_clips_to_max(self):
        cases = ((42, 5, 20, b"   42"), (42, 1, 20, b"42"), (42, 0, 20, b"42"), (42, 3, 1, b"4"), (-7, 4, 20, b"  -7"),
                 (123456, 3, 20, b"123456"), (5, 0xFFFF, 20, b"5"))
        for value, width, mx, text in cases:
            r = Rig()
            r.poke(0x300, b"\xEE" * 40)
            regs = r.run("23E4:12F6", [mx, 0x300, S, width, value & 0xFFFF, (value >> 16) & 0xFFFF])
            self.assertEqual(r.peek(0x300, 1 + len(text)), bytes([len(text)]) + text, (value, width, mx))
            self.assertEqual(r.peek(0x301 + len(text), 1), b"\xEE", "nothing past the string is written")
            self.assertEqual(regs["dx"], mx)

    def test_long_to_digits_near_with_registers(self):
        r = Rig()
        regs = r.run("23E4:11E4", far=False, ax=0xFFF9, dx=0xFFFF, es=S, di=0x300)       # -7
        self.assertEqual(r.peek(0x300, 3), b"-7\x00")
        self.assertEqual((regs["cx"], regs["di"], regs["si"]), (2, 0x300, 0x125E))


class SetBits(unittest.TestCase):
    def test_test_bit_is_bit_k_minus_one_and_far_shifts_give_zero(self):
        r = Rig()
        self.assertEqual(r.run("214B:0C57", [0b0100, 3])["ax"], 1)
        self.assertEqual(r.run("214B:0C57", [0b0100, 2])["ax"], 0)
        self.assertEqual(r.run("214B:0C57", [0x8000, 16])["ax"], 1)
        self.assertEqual(r.run("214B:0C57", [0xFFFF, 17])["ax"], 0, "a shift of 16 or more leaves nothing")
        regs = r.run("214B:0C57", [0xFFFF, 33])                              # the count is taken modulo 32: bit 0
        self.assertEqual((regs["ax"], regs["dx"]), (1, 32))

    def test_include_exclude_toggle_assign(self):
        r = Rig()
        r.poke(0x100, b"\x01")
        regs = r.run("214B:0C79", [0x100, S, 3])
        self.assertEqual(r.peek(0x100, 1), b"\x05")
        self.assertEqual((regs["ax"], regs["dx"]), (5, 4))
        regs = r.run("214B:0CA1", [0x100, S, 1])
        self.assertEqual(r.peek(0x100, 1), b"\x04")
        self.assertEqual((regs["ax"], regs["dx"]), (4, 0xFFFE))
        regs = r.run("214B:0CF4", [0x100, S, 8])
        self.assertEqual(r.peek(0x100, 1), b"\x84")
        self.assertEqual((regs["ax"], regs["dx"]), (0x84, 0x80))
        r.run("214B:0CF4", [0x100, S, 8])
        self.assertEqual(r.peek(0x100, 1), b"\x04", "toggling twice restores")

    def test_set_assign_includes_for_a_nonzero_byte_and_excludes_for_zero(self):
        r = Rig()
        r.poke(0x100, b"\x00")
        r.run("214B:0CCB", [0x100, 0x100, S, 2])                              # flag word 0x0100: its low byte is 0
        self.assertEqual(r.peek(0x100, 1), b"\x00", "only the low byte of the flag is tested")
        r.run("214B:0CCB", [0x0001, 0x100, S, 2])
        self.assertEqual(r.peek(0x100, 1), b"\x02")
        r.run("214B:0CCB", [0x0000, 0x100, S, 2])
        self.assertEqual(r.peek(0x100, 1), b"\x00")

    def test_include_with_a_far_element_changes_nothing_but_the_write(self):
        r = Rig()
        r.poke(0x100, b"\x07")
        r.run("214B:0C79", [0x100, S, 17])                                    # bit 16 of a 16-bit mask: 0
        self.assertEqual(r.peek(0x100, 1), b"\x07")


class Longs(unittest.TestCase):
    def test_min_and_max_signed_high_words_then_unsigned_low_words(self):
        r = Rig()
        # arguments: b low, b high, a low, a high
        cases = [((0x0005, 0x0000), (0x0003, 0x0000)), ((0x0001, 0xFFFF), (0x0001, 0x0000)),
                 ((0xFFFF, 0x0001), (0x0001, 0x0001)), ((0x0002, 0x0002), (0x0002, 0x0002)),
                 ((0x0000, 0x8000), (0xFFFF, 0x7FFF))]
        for a, b in cases:
            a_val = a[0] | a[1] << 16
            b_val = b[0] | b[1] << 16
            sa = a_val - (1 << 32) if a_val >> 31 else a_val
            sb = b_val - (1 << 32) if b_val >> 31 else b_val
            for address, expected in (("214B:0D56", max(sa, sb)), ("214B:0D1C", min(sa, sb))):
                regs = r.run(address, [b[0], b[1], a[0], a[1]])
                got = regs["ax"] | regs["dx"] << 16
                self.assertEqual(got, expected & 0xFFFFFFFF, (address, a, b))


class WrapAndClamp(unittest.TestCase):
    def wrap(self, v, lo, hi, delta, address="214B:1C86", fmt=2):
        r = Rig()
        r.poke(0x100, v.to_bytes(2, "little") + b"\xAA")
        regs = r.run(address, [delta & 0xFFFF, hi, lo, 0x100, S])
        return int.from_bytes(r.peek(0x100, 2), "little"), regs, r

    def test_positive_delta_inside_at_the_bound_and_past_it(self):
        self.assertEqual(self.wrap(5, 0, 9, 2)[0], 7)
        v, regs, _ = self.wrap(7, 0, 9, 2)
        self.assertEqual(v, 9, "a sum equal to the upper bound stays")
        self.assertEqual((regs["ax"], regs["dx"]), (2, 0))
        v, regs, _ = self.wrap(8, 0, 9, 3)
        self.assertEqual(v, 1, "v + delta - hi + lo - 1")
        self.assertEqual((regs["ax"], regs["dx"]), (1, 0))
        self.assertEqual(self.wrap(8, 5, 9, 3)[0], 6)

    def test_delta_zero_and_negative_take_the_lower_bound_branch(self):
        self.assertEqual(self.wrap(4, 2, 9, 0)[0], 4)
        self.assertEqual(self.wrap(4, 2, 9, -1)[0], 3)
        v, regs, _ = self.wrap(2, 2, 9, -1)
        self.assertEqual(v, 9, "below the lower bound wraps to v + delta + hi - lo + 1")
        self.assertEqual((regs["ax"], regs["dx"]), (9, 0))
        self.assertEqual(self.wrap(0, 0, 9, -1)[0], 9)
        v, regs, _ = self.wrap(2, 2, 9, -1)
        self.assertEqual(v, 9)

    def test_sum_past_sixteen_bits_wraps_and_leaves_the_high_word_in_dx(self):
        v, regs, _ = self.wrap(0xFFF0, 0, 0xFFF8, 0x20)
        self.assertEqual(v, (0xFFF0 + 0x20 - 0xFFF8 + 0 - 1) & 0xFFFF)
        self.assertEqual(regs["dx"], 0, "the 32-bit result is 0x17")

    def test_byte_version_writes_the_low_byte_of_the_word_result(self):
        r = Rig()
        r.poke(0x100, b"\x08\xAA")
        regs = r.run("214B:1D6F", [3, 9, 0, 0x100, S])
        self.assertEqual(r.peek(0x100, 2), b"\x01\xAA")
        self.assertEqual(regs["ax"] & 0xFF, 1)
        r.poke(0x100, b"\x02\xAA")
        r.run("214B:1D6F", [0xFFFF, 9, 2, 0x100, S])
        self.assertEqual(r.peek(0x100, 1), b"\x09")

    def test_the_commentary_counter_is_written_by_the_instructions_match_py_names(self):
        w = []
        r = Rig()
        r.mem.listeners.append((S * 16 + 0x100, S * 16 + 0x101, lambda lin, size, value, at: w.append((size, value, at))))
        r.poke(0x100, b"\x05\x00")
        r.run("214B:1C86", [2, 9, 0, 0x100, S])
        r.run("214B:1C86", [6, 9, 0, 0x100, S])
        pc = lambda a: r.mem.lin(a)
        self.assertEqual(w, [(2, 7, pc("214B:1CBC")), (2, 7 + 6 - 9 + 0 - 1, pc("214B:1CF8"))])

    def test_clamp_int_signed_both_sides(self):
        r = Rig()
        for v, lo, hi, want in ((5, 0, 9, 5), (-3, 0, 9, 0), (12, 0, 9, 9), (-9, -5, 3, -5), (0x7FFF, -2, 2, 2)):
            r.poke(0x100, (v & 0xFFFF).to_bytes(2, "little"))
            regs = r.run("214B:2000", [hi & 0xFFFF, lo & 0xFFFF, 0x100, S])
            self.assertEqual(int.from_bytes(r.peek(0x100, 2), "little"), want & 0xFFFF, (v, lo, hi))
            self.assertEqual(regs["ax"], want & 0xFFFF)

    def test_clamp_byte_signed_and_ah_untouched(self):
        r = Rig()
        for v, lo, hi, want in ((5, 0, 9, 5), (0xFB, 0, 9, 0), (12, 0, 9, 9), (0xF0, 0xFB, 3, 0xFB)):
            r.poke(0x100, bytes([v]))
            regs = r.run("214B:2031", [hi, lo, 0x100, S], ax=0x4200)
            self.assertEqual(r.peek(0x100, 1), bytes([want]), (v, lo, hi))
            self.assertEqual(regs["ax"], 0x4200 | want)


class LongArithmetic(unittest.TestCase):
    def test_long_multiply_low_32_bits_and_the_cross_terms(self):
        r = Rig()
        regs = r.run("23E4:0279", ax=2, dx=1, cx=4, bx=3)                     # 0x10002 * 0x30004
        self.assertEqual((regs["dx"] << 16 | regs["ax"]), 0x000A0008)
        self.assertEqual((regs["si"], regs["di"]), (2, 1))

    def test_long_divide_signs_truncate_towards_zero(self):
        r = Rig()
        for dividend, divisor in ((7, 2), (-7, 2), (7, -2), (-7, -2), (100000, 7), (-2 ** 31, 3), (5, 2 ** 31 - 1),
                                  (0, 5), (2 ** 31 - 1, -1)):
            ud, uv = dividend & 0xFFFFFFFF, divisor & 0xFFFFFFFF
            regs = r.run("23E4:0294", ax=ud & 0xFFFF, dx=ud >> 16, cx=uv & 0xFFFF, bx=uv >> 16)
            q = int(dividend / divisor)
            rem = dividend - q * divisor
            self.assertEqual(regs["dx"] << 16 | regs["ax"], q & 0xFFFFFFFF, (dividend, divisor))
            self.assertEqual(regs["bx"] << 16 | regs["cx"], rem & 0xFFFFFFFF, (dividend, divisor))

    def test_zero_divisor_is_refused_where_the_original_ends_with_runtime_error_200(self):
        r = Rig()
        with self.assertRaises(PortError):
            r.run("23E4:0294", ax=5, dx=0, cx=0, bx=0)


class Strings(unittest.TestCase):
    def test_move_and_str_store(self):
        r = Rig()
        r.poke(0x100, b"abcdef")
        regs = r.run("23E4:025D", [4, 0x200, S, 0x100, S])
        self.assertEqual(r.peek(0x200, 5), b"abcd\x00")
        self.assertEqual((regs["dx"], regs["bx"], regs["cx"]), (r.mem.DS, 0x2000, 0))
        r.pstr(0x100, b"hello")
        regs = r.run("23E4:062A", [0x100, S, 0x300, S], ax=0x5500)
        self.assertEqual(r.peek(0x300, 6), b"\x05hello")
        self.assertEqual(regs["ax"], 0x5505)

    def test_str_store_max_clips_the_length_to_the_low_byte_of_max(self):
        r = Rig()
        r.pstr(0x100, b"hello")
        r.poke(0x300, b"\xEE" * 8)
        regs = r.run("23E4:0644", [3, 0x300, S, 0x100, S], ax=0x6600)
        self.assertEqual(r.peek(0x300, 5), b"\x03hel\xEE")
        self.assertEqual(regs["ax"], 0x6603)
        r.run("23E4:0644", [0x0105, 0x300, S, 0x100, S])
        self.assertEqual(r.peek(0x300, 6), b"\x05hello", "max 0x105 is 5 as a byte")

    def test_copy_index_count_edges(self):
        r = Rig()
        r.pstr(0x100, b"abcdef")
        cases = ((2, 3, b"bcd"), (0, 2, b"ab"), (-3, 2, b"ab"), (5, 10, b"ef"), (7, 2, b""), (2, -1, b""),
                 (1, 0x7FFF, b"abcdef"), (6, 1, b"f"))
        for index, count, want in cases:
            r.poke(0x300, b"\xEE" * 8)
            regs = r.run("23E4:0676", [count & 0xFFFF, index & 0xFFFF, 0x100, S, 0x300, S])
            self.assertEqual(r.peek(0x300, 1 + len(want)), bytes([len(want)]) + want, (index, count))
            self.assertEqual(r.peek(0x301 + len(want), 1), b"\xEE")
            self.assertEqual(regs["ax"], len(want))

    def test_concat_appends_and_saturates_at_255(self):
        r = Rig()
        r.pstr(0x100, b"cd")
        r.pstr(0x300, b"ab")
        r.run("23E4:06B7", [0x100, S, 0x300, S])
        self.assertEqual(r.peek(0x300, 5), b"\x04abcd")
        r.poke(0x400, bytes([250]) + b"x" * 250 + b"\xEE" * 10)
        r.pstr(0x100, b"1234567890")
        writes = []
        r.mem.listeners.append((S * 16 + 0x400, S * 16 + 0x400, lambda lin, size, value, at: writes.append((value, at))))
        regs = r.run("23E4:06B7", [0x100, S, 0x400, S])
        self.assertEqual(r.peek(0x400, 1), b"\xFF")
        self.assertEqual(r.peek(0x401 + 250, 6), b"12345\xEE", "255 - 250 = 5 characters are appended")
        self.assertEqual([v for v, _ in writes], [(250 + 10) & 0xFF, 0xFF], "the sum's low byte first, then 255")
        self.assertEqual(regs["ax"] & 0xFF, 5)

    def test_pos(self):
        r = Rig()
        r.pstr(0x100, b"abcabd")
        cases = ((b"ca", 3), (b"abd", 4), (b"b", 2), (b"d", 6), (b"x", 0), (b"abcabd", 1), (b"abcabde", 0), (b"", 1))
        for sub, want in cases:
            r.pstr(0x400, sub)
            self.assertEqual(r.run("23E4:06E3", [0x100, S, 0x400, S])["ax"], want, sub)
        r.pstr(0x100, b"")
        r.pstr(0x400, b"")
        self.assertEqual(r.run("23E4:06E3", [0x100, S, 0x400, S])["ax"], 0, "an empty string holds nothing, not even ''")

    def test_compare_sets_the_flags_of_the_first_against_the_second(self):
        r = Rig()
        cases = ((b"abc", b"abd", CF), (b"abd", b"abc", 0), (b"abc", b"abc", ZF), (b"ab", b"abc", CF), (b"abc", b"ab", 0),
                 (b"", b"", ZF), (b"", b"a", CF), (b"b", b"a", 0))
        for a, b, want in cases:
            r.pstr(0x100, a)
            r.pstr(0x400, b)
            regs = r.run("23E4:072F", [0x400, S, 0x100, S])
            flags = regs["eflags"]
            self.assertEqual(flags & (CF | ZF), want, (a, b))
            self.assertEqual(regs["ax"], len(b) << 8 | len(a))

    def test_char_to_string(self):
        r = Rig()
        regs = r.run("23E4:075A", [0x141, 0x300, S], ax=0x3300)
        self.assertEqual(r.peek(0x300, 3), b"\x01A\x00")
        self.assertEqual(regs["ax"], 0x3341)

    def test_insert_and_delete(self):
        r = Rig()
        r.pstr(0x100, b"abcd")
        r.pstr(0x400, b"XY")
        r.run("23E4:0787", [3, 0xFF, 0x100, S, 0x400, S])                      # Insert('XY', s, 3)
        self.assertEqual(r.peek(0x100, 7), b"\x06abXYcd")
        r.pstr(0x100, b"abcd")
        r.run("23E4:0787", [3, 5, 0x100, S, 0x400, S])                         # clipped to 5
        self.assertEqual(r.peek(0x100, 6), b"\x05abXYc")
        r.pstr(0x100, b"abcd")
        r.run("23E4:0787", [9, 0xFF, 0x100, S, 0x400, S])                      # past the end: appended
        self.assertEqual(r.peek(0x100, 7), b"\x06abcdXY")
        r.pstr(0x100, b"abcdef")
        regs = r.run("23E4:07DB", [2, 2, 0x100, S])                            # Delete(s, 2, 2)
        self.assertEqual(r.peek(0x100, 5), b"\x04adef")
        self.assertEqual(regs["ax"], 4)
        r.pstr(0x100, b"abcdef")
        before = dict(r.mem.regs)
        regs = r.run("23E4:07DB", [0, 2, 0x100, S], ax=0x1111, dx=0x2222)
        self.assertEqual(r.peek(0x100, 7), b"\x06abcdef", "a count of 0 deletes nothing")
        self.assertEqual((regs["ax"], regs["dx"]), (0x1111, 0x2222), "and leaves AX and DX as they came")

    def test_set_compact_copies_bl_bytes_from_byte_bh(self):
        r = Rig()
        r.poke(0x100, bytes(range(32)))
        regs = r.run("23E4:08BF", [0x0304, 0x300, S, 0x100, S])                 # offset 3, 4 bytes
        self.assertEqual(r.peek(0x300, 5), bytes([3, 4, 5, 6, 0]))
        self.assertEqual(regs["bx"], 0x0304)

    def test_upcase(self):
        r = Rig()
        for ch, want in ((ord("a"), ord("A")), (ord("z"), ord("Z")), (ord("`"), ord("`")), (ord("{"), ord("{")),
                         (ord("A"), ord("A")), (0x161, ord("A"))):
            self.assertEqual(r.run("23E4:19B2", [ch], ax=0x4400)["ax"], 0x4400 | want)


class Registry(unittest.TestCase):
    def test_every_address_of_the_row_has_its_port(self):
        reg = port._module_registry("runtime")
        self.assertEqual(len(reg.entries), 38)
        self.assertEqual(sorted(a for a in reg.entries if a.startswith("214B")).__len__(), 22)
        self.assertEqual(sorted(a for a in reg.entries if a.startswith("23E4")).__len__(), 16)

    def test_returns_are_the_listings(self):
        reg = port._module_registry("runtime")
        far = {a: (e.far, e.pop) for a, e in reg.entries.items()}
        self.assertEqual(far["214B:0000"], (True, 8))
        self.assertEqual(far["214B:05DB"], (True, 0))
        self.assertEqual(far["23E4:11E4"], (False, 0))
        self.assertEqual(far["23E4:0279"], (True, 0))
        self.assertEqual(far["23E4:12F6"], (True, 0xC))


def _image_available():
    try:
        import unicorn  # noqa: F401
    except ImportError:
        return False
    return (ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav").is_file()


@unittest.skipUnless(_image_available(), "needs unicorn and the reference image in .cache/dl")
class FuzzAgainstOriginal(unittest.TestCase):
    """Each runtime port against the original's code on 40 random inputs (out/T60/fuzz.py): the same AX, DX, BP, SP, DS,
    the direction flag and every byte of memory but the callee's dead frame."""

    def test_every_port_equals_the_original(self):
        sys.path.insert(0, str(ROOT / "experiments" / "E036-match-port" / "out" / "T60"))
        import contextlib
        import io
        import fuzz
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            failed = fuzz.fuzz("runtime", sorted(port._module_registry("runtime").entries), 40, "unit", False,
                               str(ROOT / ".cache" / "dl"), False, None, 2)
        self.assertEqual(failed, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
