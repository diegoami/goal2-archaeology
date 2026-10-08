#!/usr/bin/env python3
"""Six isolated original B7FA executions from E011's verified guest image.

This is a routine probe, not a DOSBox playthrough. No guest instruction or
RNG result is replaced. B71C and B364 execute as original code. Inputs are
declared I2 record changes; all draws and confidence-call arguments are
retained. Source and memory layout follow E017's original-routine probes.
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
from unicorn.x86_const import UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_CS, UC_X86_REG_IP, UC_X86_REG_AX

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('state')
    ap.add_argument('output')
    args = ap.parse_args()
    data = Path(args.state).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    # The full hash is checked against E011's tracked manifest, not a prefix.
    manifest = json.loads((ROOT / 'evidence/E011/E011-r0002.manifest.json').read_text())
    print('source sha256:', digest)
    if digest not in json.dumps(manifest):
        raise ValueError('source not in E011 manifest')
    output = []
    for case, (scores, winner, kind, ranks) in enumerate([
        ((3, 1), 0, 1, ((1, 1, 1), (1, 1, 1))),
        ((1, 3), 1, 1, ((1, 1, 1), (1, 1, 1))),
        ((0, 0), 2, 2, ((1, 1, 1), (4, 32, 128))),
        ((0, 8), 1, 2, ((4, 32, 128), (1, 1, 1))),
        ((8, 0), 0, 2, ((4, 32, 128), (1, 1, 1))),
        ((1, 1), 2, 1, ((2, 5, 20), (4, 32, 128))),
    ], 1):
        half = WatchedHalf(data)
        mu = half.mu
        load = half.CODE - 0x791
        pb = half.rd(0xA91B) + half.rd(0xA91D) * 16
        cb = half.rd(0xA917) + half.rd(0xA919) * 16
        # The live fixture pointer, established by the match set-up (F010).
        fixture_off, fixture_seg = half.rd(0x7C2A), half.rd(0x7C2C)
        fixture = bytes((*scores, kind, winner, 1, 0, 2, 0))
        mu.mem_write(fixture_seg * 16 + fixture_off, fixture)
        countries, before = [], []
        for side, (continent, crank, wrank) in enumerate(ranks):
            country = bytearray(mu.mem_read(cb + (side + 1) * 191, 191))
            country[42:47] = bytes((crank, wrank, continent, 0, 0))
            words = list(range(1 + side * 20, 21 + side * 20))
            country[0:40] = b''.join(w.to_bytes(2, 'little') for w in words)
            mu.mem_write(cb + (side + 1) * 191, bytes(country))
            countries.append({'country_word': side + 1, 'record': country.hex()})
            for slot, word in enumerate(words, 1):
                record = bytearray(mu.mem_read(pb + word * 20, 20))
                # Healthy, age 25; literal confidence edges; slot 12 participated.
                record[1], record[12], record[13], record[14] = 25, (1, 16, 32)[slot % 3], 16, 16
                # Pascal element 3 occupies bit 2, not zero-based bit 3.
                record[16] = 4 if slot == 12 else 0
                mu.mem_write(pb + word * 20, bytes(record))
                before.append({'player_word': word, 'side': side, 'slot': slot, 'record': record.hex()})
        draws, operations = [], []

        def rng(uc, addr, size, user):
            stack = uc.reg_read(UC_X86_REG_SS) * 16 + uc.reg_read(UC_X86_REG_SP)
            ret = bytes(uc.mem_read(stack, 6))
            return_address = int.from_bytes(ret[:2], 'little') + 16 * int.from_bytes(ret[2:4], 'little')
            item = {'bound': int.from_bytes(ret[4:6], 'little')}
            draws.append(item)
            handle = []

            def returned(uc, addr, size, user):
                item['value'] = uc.reg_read(UC_X86_REG_AX)
                uc.hook_del(handle[0])

            handle.append(uc.hook_add(UC_HOOK_CODE, returned, begin=return_address, end=return_address))

        def confidence(uc, addr, size, user):
            stack = uc.reg_read(UC_X86_REG_SS) * 16 + uc.reg_read(UC_X86_REG_SP)
            raw = bytes(uc.mem_read(stack, 6))
            operations.append({'return_ip': int.from_bytes(raw[:2], 'little'),
                               'delta_word': int.from_bytes(raw[2:4], 'little'),
                               'player_word': int.from_bytes(raw[4:6], 'little'),
                               'draw_count': len(draws)})

        mu.hook_add(UC_HOOK_CODE, rng, begin=(load + 0x214B) * 16 + 0x688, end=(load + 0x214B) * 16 + 0x688)
        mu.hook_add(UC_HOOK_CODE, confidence, begin=half.CODE * 16 + 0xB364, end=half.CODE * 16 + 0xB364)
        stack = mu.reg_read(UC_X86_REG_SS) * 16 + mu.reg_read(UC_X86_REG_SP)
        mu.mem_write(stack, b''.join(v.to_bytes(2, 'little') for v in (0x98C0, half.CODE, fixture_off, fixture_seg)))
        mu.emu_start(half.CODE * 16 + 0xB7FA, half.CODE * 16 + 0x98C0, timeout=10000000)
        if mu.reg_read(UC_X86_REG_CS) != half.CODE or mu.reg_read(UC_X86_REG_IP) != 0x98C0:
            raise ValueError('fixture update failed to return')
        after = [{'player_word': b['player_word'], 'confidence': bytes(mu.mem_read(pb + b['player_word'] * 20 + 12, 1))[0]} for b in before]
        # Actual classifier table bytes are retained: the model does not guess which
        # fixture kinds belong to the Pascal set at DS:0F3E.
        output.append({'case': case, 'method': 'original 0791:B7FA in Unicorn; no skipped reachable calls',
                       'source_sha256': digest, 'source_release': 'E011',
                       'fixture': fixture.hex(), 'countries': countries,
                       'classification_set': bytes(mu.mem_read(half.DS * 16 + 0xF3E, 32)).hex(),
                       'before': before, 'draws': draws, 'operations': operations,
                       'after': after, 'strays': half.strays})
        print('case', case, 'players', len(after), 'draws', len(draws), 'confidence calls', len(operations))
    with Path(args.output).open('x') as f:
        json.dump({'schema': 'E018-confidence-probe/1', 'cases': output}, f, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
