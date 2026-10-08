#!/usr/bin/env python3
"""Run original 1771:3651 on literal edge inputs; no random calls are replaced.

E011's hash-verified guest image supplies code and DS:0E84. Stack layout is
1771:3651 (retf 4; flag at BP+6, player word BP+8). 214B:0688 retf 6 returns
AX: read it at its actual far return. 06B1 and 06D0 independently call 0688
(seg_214B_01.asm:896–935), so hooking only 06B1 misses the healing draw.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from runtime.emul.watched import WatchedHalf
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_CS, UC_X86_REG_AX, UC_X86_REG_IP
from probe_watched import SOURCE_HASH


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state')
    parser.add_argument('output')
    args = parser.parse_args()
    data = Path(args.state).read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_HASH:
        raise ValueError('source hash mismatch')
    # All differences are declared literal input records, not altered guest code.
    cases = [(0, 16, 8, 30), (1, 16, 8, 30), (1, 16, 0, 30),
             (0, 1, 0, 30), (1, 255, 0, 30), (1, 31, 8, 28),
             (1, 31, 8, 29), (1, 16, 255, 30)]
    output = []
    for flag, fitness, energy, age in cases:
        half = WatchedHalf(data)
        mu = half.mu
        load = half.CODE - 0x791
        base = half.rd(0xA91B) + half.rd(0xA91D) * 16
        # Literal word 361 belongs to E011's squad; the word, not its name,
        # determines both the injected record and the measured comparison.
        word = 361
        record = bytes([9, age, 25, 0, 64, 0, 0, 0, 0, 0, 0, 0, 16, fitness, energy, 0, 0, 0, 0, 0])
        mu.mem_write(base + word * 20, record)
        draws, bounds = [], []

        def random_call(uc, addr, size, user):
            stack = uc.reg_read(UC_X86_REG_SS) * 16 + uc.reg_read(UC_X86_REG_SP)
            ret = bytes(uc.mem_read(stack, 6))
            return_address = int.from_bytes(ret[:2], 'little') + 16 * int.from_bytes(ret[2:4], 'little')
            bounds.append(int.from_bytes(ret[4:6], 'little'))
            handle = []

            def returned(uc, addr, size, user):
                draws.append(uc.reg_read(UC_X86_REG_AX))
                uc.hook_del(handle[0])

            handle.append(uc.hook_add(UC_HOOK_CODE, returned, begin=return_address, end=return_address))

        mu.hook_add(UC_HOOK_CODE, random_call, begin=(load + 0x214B) * 16 + 0x688, end=(load + 0x214B) * 16 + 0x688)
        sp = mu.reg_read(UC_X86_REG_SP)
        stack = mu.reg_read(UC_X86_REG_SS) * 16 + sp
        # Stop before an unused guest instruction at 0791:98C0 (the half's ret).
        mu.mem_write(stack, b''.join(v.to_bytes(2, 'little') for v in (0x98C0, half.CODE, flag, word)))
        mu.reg_write(UC_X86_REG_CS, load + 0x1771)
        mu.emu_start((load + 0x1771) * 16 + 0x3651, half.CODE * 16 + 0x98C0, timeout=10000000)
        if mu.reg_read(UC_X86_REG_CS) != half.CODE or mu.reg_read(UC_X86_REG_IP) != 0x98C0:
            raise ValueError('recovery did not return to sentinel')
        after = bytes(mu.mem_read(base + word * 20 + 12, 3)).hex()
        output.append({'schema': 'E017-energy/1', 'method': 'Unicorn original 1771:3651 edge probe',
                       'source_sha256': SOURCE_HASH, 'source_release': 'E011',
                       'before': [{'player_word': word, 'record': record.hex()}],
                       'operations': [{'kind': 'recover', 'player_word': word, 'flag': flag,
                                       'draws': draws, 'caps': [half.rd(0xE84, 1), half.rd(0xE85, 1)]}],
                       'after': [{'player_word': word, 'bytes_c_d_e': after}],
                       'draw_bounds': bounds, 'unknown_stores': [], 'strays': half.strays})
    with Path(args.output).open('x') as handle:
        json.dump({'cases': output}, handle, indent=2)
        handle.write('\n')
    print(f'original recovery cases: {len(output)}')


if __name__ == '__main__':
    main()
