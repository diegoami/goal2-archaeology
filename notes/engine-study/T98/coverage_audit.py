#!/usr/bin/env python3
"""Identify formula distinctions the retained scalar returns cannot validate."""
import argparse
import json
from pathlib import Path
import sys

import skill
import strength

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'notes/engine-study/foundations'))
from check import pin, sha, write_new


def build():
    counts = dict(drop_host_share=0, share_before_manager=0,
                  halve_before_clamp=0, floor_instead_of_trunc=0)
    sources = []
    totals = dict(skill=0, strength=0)
    for name in ['contest-001.json', 'contest-002-events.json', 'contest-003-fitness.json']:
        source = f'{skill.RECORD_DIR}/{name}'; sources.append(source)
        for c in json.loads((ROOT/source).read_text())['comparisons']:
            t = skill.trace(bytes.fromhex(c['record']), c['element'], c['pitch_6'],
                            c['pitch_11'], c['pitch_13'], c['flag_80fc'], c['event_code_8327'])
            assert t['value'] == c['contest']
            totals['skill'] += 1
            counts['drop_host_share'] += t['before_venue'] != c['contest']
            before = t['condition_term'] + t['quarter_term']
            early = before//16 if c['pitch_6'] < 12 and c['flag_80fc'] else 0
            counts['share_before_manager'] += ((before+early+t['extra_added']) & 65535) != c['contest']
    for name in ['strength-001.json', 'strength-002-fitness.json', 'strength-003-structure.json']:
        source = f'{skill.RECORD_DIR}/{name}'; sources.append(source)
        for c in json.loads((ROOT/source).read_text())['comparisons']:
            p = bytes.fromhex(c['record']); t = strength.trace(p, c['player_word'])
            assert t['value'] == c['strength']
            totals['strength'] += 1
            if t['unavailable']: continue
            v = strength.s16(t['after_form_word'])
            h = max(0, min(256, v//2 if t['placement'] else v))
            counts['halve_before_clamp'] += h != c['strength']
            w = t['base_word']
            v = (w-strength.s16(w)//16 if t['form_high'] else w+strength.s8(p[12])) & 65535
            v = max(0, min(256, strength.s16(v)))
            counts['floor_instead_of_trunc'] += (v//2 if t['placement'] else v) != c['strength']
    assert totals == dict(skill=209, strength=376)
    return pin(dict(task='T98-validation-scope', retained_returns=totals,
                    mutation_disagreements=counts,
                    interpretation='Zero disagreements means the retained scalar returns do not distinguish that mutation. Source reading remains the basis; floor/trunc differences can be hidden by later clipping. No fresh original execution or ABI evidence.',
                    analysis_sha256={p: sha((ROOT/p).read_bytes()) for p in [
                        'notes/engine-study/T98/coverage_audit.py', 'notes/engine-study/T98/skill.py',
                        'notes/engine-study/T98/strength.py', 'notes/engine-study/T98/tables.py']}),
               ['0791:278A', '1771:377E'], sources)


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--check', action='store_true')
    args = ap.parse_args(); data = build()
    path = ROOT/'notes/engine-study/T98/validation-scope-v1.json'
    if args.check:
        assert json.loads(path.read_text()) == data, 'validation-scope audit differs'
        print('PASS:', data['retained_returns'], data['mutation_disagreements'])
    else:
        write_new(path, data); print('wrote retained-return validation-scope audit')


if __name__ == '__main__': main()
