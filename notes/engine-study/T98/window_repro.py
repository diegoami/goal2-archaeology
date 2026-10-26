#!/usr/bin/env python3
"""Reproduce the legacy table-window limit without altering retained evidence."""
import argparse
import json
from pathlib import Path
import sys
from tables import ROOT,load_ds
from skill import record,trace

sys.path.insert(0,str(ROOT/'runtime'))
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from model.keeping import skill_value
from check import pin,sha,write_new


def build():
    source='experiments/E020-q018-condition-performance/records/contest-001.json'
    old=json.loads((ROOT/source).read_text())
    ct=bytes.fromhex(old['class_table_DS_6D25']);pt=bytes.fromhex(old['profile_table_DS_6DCD'])
    _,ds,sources=load_ds();results=[]
    for profile,club,element in [(8,13,12),(16,2,3)]:
        try:
            skill_value(180,profile,club,element,ct,pt)
        except IndexError:
            error='IndexError'
        else:raise AssertionError('legacy boundary failure did not reproduce')
        extended=skill_value(180,profile,club,element,ds[0x6D25:0x6D25+169],ds[0x6DCD:0x6DCD+205])
        expected=trace(record(profile=profile,club=club),element)['derived_skill']
        assert extended==expected
        results.append(dict(ability=180,profile=profile,club_position=club,element=element,
                            legacy_result=error,extended_source_window_result=extended,independent_formula=expected))
    return pin({'task':'T98a-window-boundary','cases':results,'class_window_bytes':len(ct),'profile_window_bytes':len(pt),
                'scope':'Legacy analytical helper/data window, not the memory-faithful engine port. No new original-code call.',
                'analysis_sha256':sha(Path(__file__).read_bytes())},['1771:3A06'],sources+[source,'runtime/model/keeping.py'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args()
    path=ROOT/'notes/engine-study/T98/window-repro-v1.json';data=build()
    if a.check:
        assert json.loads(path.read_text())==data;print('PASS: two valid-domain legacy IndexErrors reproduced; extended source windows match the formula')
    else:write_new(path,data);print('wrote immutable legacy-window reproduction')


if __name__=='__main__':main()
