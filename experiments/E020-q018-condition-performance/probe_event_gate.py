#!/usr/bin/env python3
"""Which DS:8327 values make 0791:278A add pitch+0x11 for element 1 (the second gate, 282D-2842)?

The set tested is the 32 bytes at CS:276A (seg_0791_04.asm:843, first byte 0x18, the rest zero); the
membership test 23E4:08DF reads element e at bit e of byte e>>3 (quick_engine.wrong_foot's comment),
so the byte 0x18 (bits 3 and 4) is the set {3, 4}, not the value 0x18 that
runtime/model/keeping.py names KEEPING_EVENT. This runs the original on a literal record for DS:8327 in 0..0x20 and prints, per
value, whether the +0x11 extra (5) was added. Appends nothing to the tree: the output is the log
the caller redirects to a new file.

    python3 experiments/E020-q018-condition-performance/probe_event_gate.py > experiments/E020-q018-condition-performance/event-gate-001.log
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe_original as P  # noqa: E402


def main():
    h = P.Harness()
    word = 3400
    rec = bytearray(20)
    rec[4], rec[5], rec[7], rec[0xC], rec[0xE] = 0xB4, 8, 2, 0x10, 0x18
    h.put_player(word, rec)
    pitch_off = 0x80E8 + 0x16
    print("original 0791:278A(element 1), pitch+6=1, pitch+0x11=5, DS:80FC=0, E010 half-time image")
    print("event DS:8327 -> contest, extra added?")
    base = None
    for event in range(0, 0x21):
        pitch = bytearray(h.ds_read(pitch_off, 0x16))
        pitch[6], pitch[0xD:0xF], pitch[0x11], pitch[0x13] = 1, word.to_bytes(2, "little"), 0, 0
        h.ds_write(pitch_off, pitch)
        h.ds_write(0x80FC, b"\x00")
        h.ds_write(0x8327, bytes([event]))
        without = h.call(0x791, 0x278A, [pitch_off, h.half.DS, 1])
        pitch[0x11] = 5
        h.ds_write(pitch_off, pitch)
        with_extra = h.call(0x791, 0x278A, [pitch_off, h.half.DS, 1])
        print(f"0x{event:02x} -> {with_extra} (without the extra byte: {without}) "
              f"{'EXTRA ADDED' if with_extra - without == 5 else 'no extra'}")


if __name__ == "__main__":
    main()
