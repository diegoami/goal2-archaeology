#!/usr/bin/env python3
"""Original-routine probe of 0791:7CC5 (adjust_player_form) in Unicorn.

The input is the unpacked GOAL.EXE image (the listed routine runs as original
guest code; no instruction or RNG result is replaced). Each case lays out a
complete 20-byte player record and an 18-byte pitch record (the 0x16-byte
pitch layout from F013), writes the inputs that the routine reads, sets up a
return address at the post-call point of a stub routine at CS:0x98C0, and
calls 0791:7CC5 directly. The after-call player +0xC and DS:9B07 byte are
recorded.

Each case is a (delta_high_word, delta_low_word_with_flag) pair, replicating
the push order of every caller (segments 0791 seg_0791_13.asm:386-394 for
send_off head, 430-438 for send_off tail +2 flag=0, 593-601 for injury,
177-191 for scorer). The clamp and DS:9B07 persistence are checked.
"""
import argparse
import json
import sys
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
from unicorn.x86_const import UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_CS, UC_X86_REG_IP, UC_X86_REG_AX, UC_X86_REG_DS, UC_X86_REG_ES


CODE = 0x0791
DATA = 0x2581
ROUTINE = 0x7CC5
RETURN = 0x98C0
CLAMP_HI = 0x20


HEADER = 8192
# The image has an 8192-byte EXE header before the load module. Listing
# addresses are SEGMENT:OFFSET in the load module (so segment X, offset Y is
# at file offset HEADER + X*16 + Y). The program has no relocations, so the
# file's segment bytes are already post-relocation. To make segment X in the
# listing map to its physical address in our Unicorn memory, we shift every
# listing segment by HEADER/16: CS_listing=0x791 -> CS_unicorn=0x991.
SEG_SHIFT = HEADER // 16
CS_RAW = 0x0791
DS_RAW = 0x2581
CS = CS_RAW + SEG_SHIFT
DS = DS_RAW + SEG_SHIFT
SS = 0x7000 + SEG_SHIFT
SP0 = 0x6FF4


def setup(image):
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    # The first HEADER bytes of the file are the EXE header; the loaded
    # program starts at file offset HEADER. We load the file at address 0
    # so file offset f maps to memory address f; listing segment X then
    # maps to memory address HEADER + X*16. CS=0x791 -> 0x2000 + 0x791*16.
    mu.mem_write(0, image)
    # Listing segments map directly: CS=0x791 -> address HEADER + 0x791*16.
    mu.reg_write(UC_X86_REG_SS, SS)
    mu.reg_write(UC_X86_REG_SP, SP0)
    mu.reg_write(UC_X86_REG_DS, DS)
    mu.reg_write(UC_X86_REG_ES, DS)
    mu.reg_write(UC_X86_REG_CS, CS)
    return mu


def run_case(mu, player_morale, delta_high, delta_low, side, slot):
    # Player record at DS:A91B + player_word*20. Use player_word=1, so the
    # record is at DS:A91B + 20 = DS:A92F.
    pb = DS * 16 + 0xA91B + 20
    # Reset all 20 bytes to zero so the only carry is the morale we set.
    mu.mem_write(pb, bytes(20))
    mu.mem_write(pb + 12, bytes([player_morale]))
    # The pitch record at DS:80E8 + slot*0x16.  Use slot=1, so the pitch is
    # at DS:80E8 + 0x16 = DS:80FE.
    pitch = DS * 16 + 0x80E8 + slot * 0x16
    mu.mem_write(pitch, bytes(0x16))
    # +0xD is the player word. Write player_word=1 there so +0xD's id matches.
    mu.mem_write(pitch + 0xD, b'\x01\x00')
    # DS:9B07[side*20 + slot] = 0
    saved_addr = DS * 16 + 0x9B07 + side * 20 + slot
    mu.mem_write(saved_addr, b'\x00')
    # Stack layout: at entry to 7CC5 the caller has pushed (right-to-left):
    #   delta_high, delta_low, pitch_high (es), pitch_low (di), cs
    # Then a near call pushes the return IP. The routine uses retf 8 which
    # pops CS:IP and skips 8 bytes; the routine reads [bp + 6] = pitch_low,
    # [bp + 8] = pitch_high, [bp + 0xa] = delta_low (the flag byte), [bp + 0xc]
    # = delta_high (the addend).
    pitch_low = (pitch) & 0xFFFF
    pitch_high = (pitch >> 16) & 0xFFFF
    sp = SP0
    mu.mem_write(SS * 16 + sp + 0, (RETURN).to_bytes(2, 'little'))     # IP
    mu.mem_write(SS * 16 + sp + 2, (CS).to_bytes(2, 'little'))         # cs
    mu.mem_write(SS * 16 + sp + 4, pitch_low.to_bytes(2, 'little'))    # di
    mu.mem_write(SS * 16 + sp + 6, pitch_high.to_bytes(2, 'little'))   # es
    mu.mem_write(SS * 16 + sp + 8, delta_low.to_bytes(2, 'little'))     # delta_low (flag in low byte)
    mu.mem_write(SS * 16 + sp + 10, delta_high.to_bytes(2, 'little'))   # delta_high (the addend)
    mu.reg_write(UC_X86_REG_SP, SP0)
    try:
        mu.emu_start(CS * 16 + ROUTINE, 0, timeout=10 * 1000000)
    except Exception as exc:
        # Unicorn 16-bit mode has quirks with `les` and other segment ops.
        # If the routine fails to return cleanly, diagnose from final state.
        cs = mu.reg_read(UC_X86_REG_CS)
        ip = mu.reg_read(UC_X86_REG_IP)
        sp = mu.reg_read(UC_X86_REG_SP)
        ss = mu.reg_read(UC_X86_REG_SS)
        top = bytes(mu.mem_read(ss * 16 + sp, 16))
        raise ValueError(f'unicorn error at cs={hex(cs)} ip={hex(ip)} sp={hex(sp)} top={top.hex()}: {exc}') from exc
    cs = mu.reg_read(UC_X86_REG_CS)
    ip = mu.reg_read(UC_X86_REG_IP)
    if cs != CS or ip != RETURN:
        sp = mu.reg_read(UC_X86_REG_SP)
        ss = mu.reg_read(UC_X86_REG_SS)
        top = bytes(mu.mem_read(ss * 16 + sp, 16))
        raise ValueError(f'failed to return (cs={hex(cs)}, ip={hex(ip)}, sp={hex(sp)}, top={top.hex()})')
    return (bytes(mu.mem_read(pb + 12, 1))[0],
            bytes(mu.mem_read(saved_addr, 1))[0])


CASES = [
    # (label, before, delta_high, delta_low, side, slot)
    ('injury_high_morale', 30, 0xFFFE, 0x0001, 0, 1),
    ('injury_low_morale', 2, 0xFFFE, 0x0001, 0, 1),
    ('injury_floor_morale', 1, 0xFFFE, 0x0001, 0, 1),
    ('scorer_plus_one', 16, 0x0001, 0x0001, 0, 1),
    ('team_reaction_negative', 16, 0xFFFF, 0x0000, 1, 1),
    ('team_reaction_no_persist', 16, 0x0002, 0x0000, 1, 1),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('image')
    ap.add_argument('output')
    args = ap.parse_args()
    image = Path(args.image).read_bytes()
    mu = setup(image)
    output = []
    for case, (label, before, delta_high, delta_low, side, slot) in enumerate(CASES, 1):
        mu_new = setup(image)
        live, saved = run_case(mu_new, before, delta_high, delta_low, side, slot)
        output.append({'case': case, 'label': label,
                       'before_morale': before, 'delta_high': delta_high, 'delta_low': delta_low,
                       'side': side, 'slot': slot,
                       'after_morale': live, 'saved_form': saved})
        print(f"case {case:2d} {label:30s} before={before:3d} delta_high={hex(delta_high)} delta_low={hex(delta_low)} -> live={live:3d} saved={saved:3d}")
    with Path(args.output).open('x') as f:
        json.dump({'schema': 'E019-adjust-form-probe/1', 'cases': output}, f, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()