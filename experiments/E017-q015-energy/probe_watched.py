#!/usr/bin/env python3
"""Guest-code corroboration of a complete E011 half, with energy input transcript.

No guest code is patched. Hooks only read arguments before the instruction
paths that write +0xC/+0xD/+0xE. Unknown stores fail the comparison checker.
See WatchedHalf for its BIOS/display interventions. Source is verified by its
release hash; output is exclusive-create and is never overwritten.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from runtime.emul.watched import WatchedHalf
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_BP, UC_X86_REG_SS, UC_X86_REG_CS, UC_X86_REG_IP, UC_X86_REG_DI, UC_X86_REG_ES

SOURCE_HASH = '092f5f74bc5dc0c0f133709ca46be04122d3813a716c54fd23a686e9194ab9ff'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state')
    parser.add_argument('output')
    args = parser.parse_args()
    data = Path(args.state).read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_HASH:
        raise ValueError('E011 half-time source hash mismatch')
    half = WatchedHalf(data)
    mu = half.mu

    def read(addr, count=2):
        return int.from_bytes(mu.mem_read(addr, count), 'little')

    base = half.rd(0xA91B) + half.rd(0xA91D) * 16  # F007 player-array far pointer
    country_base = half.rd(0xA917) + half.rd(0xA919) * 16
    words = set()
    for side in range(2):
        country = half.rd(0x9B34 + side * 2)
        for slot in range(20):
            # country stride 0xBF and squad +0, F007/F008 record layout
            word = read(country_base + country * 0xBF + slot * 2)
            if word:
                words.add(word)
    if not words:
        raise ValueError('empty match squads')
    before = [{'player_word': w, 'record': bytes(mu.mem_read(base + w * 20, 20)).hex()} for w in sorted(words)]
    operations, stores, unknown = [], {}, []

    def frame():
        return mu.reg_read(UC_X86_REG_SS) * 16 + mu.reg_read(UC_X86_REG_BP)

    def pitch():
        bp = frame()
        return read(bp + 6) + 16 * read(bp + 8)

    def activity(uc, addr, size, user):
        p = pitch()
        counter = read(p + 20)
        enabled = bool(half.rd(0x8325, 1))
        # Only tails with an active reset can change a player byte. Keep floor
        # visits too: the replay, not the guest's energy gate, decides decrement.
        if enabled and counter > 180:
            operations.append({'kind': 'watched', 'player_word': read(p + 13),
                               'counter': counter, 'enabled': enabled, 'counter_after': 0})

    def form(uc, addr, size, user):
        delta = read(frame() + 12)
        if delta >= 32768:
            delta -= 65536
        operations.append({'kind': 'form', 'player_word': read(pitch() + 13), 'delta': delta})

    def injury(uc, addr, size, user):
        address = mu.reg_read(UC_X86_REG_ES) * 16 + mu.reg_read(UC_X86_REG_DI)
        word, remainder = divmod(address - base, 20)
        if remainder:
            raise ValueError('injury pointer is not a player record')
        operations.append({'kind': 'injury', 'player_word': word})

    def store(uc, address, size, value, user):
        for offset in range(size):
            word, field = divmod(address + offset - base, 20)
            if word in words and field in (12, 13, 14):
                cs = mu.reg_read(UC_X86_REG_CS) - (half.CODE - 0x791)
                ip = mu.reg_read(UC_X86_REG_IP)
                site = f'{cs:04X}:{ip:04X}'
                stores[site] = stores.get(site, 0) + 1
                if site not in ('0791:8C54', '0791:7D09', '0791:7D9B'):
                    unknown.append({'site': site, 'player_word': word, 'field': field})

    for off, callback in ((0x8C35, activity), (0x7CE3, form), (0x7D9B, injury)):
        mu.hook_add(UC_HOOK_CODE, callback, begin=half.CODE * 16 + off, end=half.CODE * 16 + off)
    mu.hook_add(UC_HOOK_MEM_WRITE, store, begin=base + min(words) * 20, end=base + max(words) * 20 + 19)
    half.run()
    record = {'schema': 'E017-energy/1', 'method': 'Unicorn complete watched second half',
              'source_sha256': SOURCE_HASH, 'source_release': 'E011',
              'source_asset': '092f5f74bc5dc0c0-E011-r0001-halftime.sav',
              'before': before, 'operations': operations,
              'after': [{'player_word': w, 'bytes_c_d_e': bytes(mu.mem_read(base + w * 20 + 12, 3)).hex()} for w in sorted(words)],
              'stores': stores, 'unknown_stores': unknown, 'strays': half.strays,
              'start': half.start_state, 'final': half.final}
    with Path(args.output).open('x') as output:
        json.dump(record, output, indent=2)
        output.write('\n')
    print(f'players: {len(words)}; operations: {len(operations)}; stores: {stores}; unknown: {len(unknown)}', flush=True)


if __name__ == '__main__':
    main()
