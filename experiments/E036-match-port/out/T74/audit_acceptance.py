"""Read-only final T74 acceptance audit; every input/output is immutable and hash-bound."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'experiments/E036-match-port'),str(ROOT/'runtime')]
import compare,families
from original_match import port
from original_match.port import menus

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def source_matches(receipt):
    return all(digest(ROOT/p)==value for p,value in receipt['sources'].items())

a=argparse.ArgumentParser();a.add_argument('--integrated',required=True);a.add_argument('--out',required=True)
a=a.parse_args();integrated=Path(a.integrated);output=Path(a.out)
assert not output.exists(),'audit outputs are never overwritten'
specs={m.id:m.sha256 for f in families.discover().values() for m in f.matches}
assert len(specs)==63
profile=read(ROOT/'experiments/E036-match-port/families/display/profile.json')
assert profile['mask']==[],'no DS mask is permitted'
rawref=ROOT/'experiments/E036-match-port/families/S-no-managed-side-reference-20261024-v1.jsonl'
displayref=ROOT/profile['reference']
oldraw=ROOT/'experiments/E036-match-port/out/T57/reference.jsonl'
olddisplay=ROOT/'experiments/E036-match-port/families/display/reference-all-20261023-v1.jsonl'
assert rawref.read_bytes().startswith(oldraw.read_bytes())
assert displayref.read_bytes().startswith(olddisplay.read_bytes())
for old in (oldraw,olddisplay):
    baseline=subprocess.check_output(['git','show','53b011249446c4a562624b573b84640726134c6b:'+str(old.relative_to(ROOT))],cwd=ROOT)
    assert baseline==old.read_bytes()
reports={};counter_rows=[]
for label,path,reference,strict in [('own',OUT/'own-menus-desktop-2/own.jsonl',rawref,False),
                                  ('integrated',integrated,displayref,True)]:
    cand=compare.load(path);ref=compare.load(reference)
    lines,ok=compare.check(ref,cand,specs,image_sha256=families.image_sha256(),no_screen=strict,strict_display=strict)
    assert ok,lines[-8:]
    assert all(r['mask']==[] for r in cand.values())
    if strict:assert compare.candidate_display_profile(cand,True)==profile
    expected_modules=set(port.available()) if strict else {'menus'}
    assert len(port.available())==17
    for mid,row in cand.items():
        assert set(row['ports'])==expected_modules,(label,mid,row['ports'])
        assert set(row['counts'])==set(menus.PORTS.entries)
        for address in sorted(menus.PORTS.entries):
            assert row['counts'][address]==row['port_calls'][address],(label,mid,address)
            counter_rows.append({'mode':label,'id':mid,'entry':address,'count':row['counts'][address]})
    n=cand['S/no-managed-side']
    assert n['decisions']==[] and n['strays']==[] and compare.completed(n) is None
    assert n['draws']['count']>0 and n['stopped_at_board']
    reports[label]={'path':str(path),'sha256':digest(path),'comparison':lines[-1],
                    'entry_call_checks':len(cand)*len(menus.PORTS.entries)}
assert len(counter_rows)==3402
assert source_matches(read(OUT/'own-menus-desktop-2/source.json'))
assert source_matches(read(OUT/'falsifiers-desktop-3/source.json'))
# Actions' executed Git object, not its collector's later commit, binds the runtime.
dispatch=(OUT/'all-actions-final-1-dispatch-head.txt').read_text().strip()
for p in sorted((ROOT/'runtime/original_match').rglob('*.py')):
    rel=str(p.relative_to(ROOT));old=subprocess.check_output(['git','show',dispatch+':'+rel],cwd=ROOT)
    assert old==p.read_bytes(),rel
proof=read(OUT/'falsifiers-desktop-3/caught-proof.json')
own=compare.load(OUT/'own-menus-desktop-2/own.jsonl')
reference_original=compare.load(OUT/'coverage-unhooked-1.jsonl')
variant_owners={'tactics-adjacent-bit':'1771:1981','speed-right-increments':'0791:9372','menu-tactics-wrong-country':'0791:ED8A'}
assert len(proof)==3
for witness in proof:
    variant,mid=witness['variant'],witness['match'];owner=variant_owners[variant]
    mutant=compare.load(OUT/f'falsifiers-desktop-3/{variant}.jsonl')
    assert set(mutant)=={mid}
    lines,ok=compare.check(compare.load(rawref),mutant,{mid:specs[mid]},expect='differ',image_sha256=families.image_sha256())
    assert ok and compare.completed(mutant[mid]) is None,(variant,lines)
    assert reference_original[mid]['counts'][witness['branch']]>0
    assert own[mid]['port_calls'][owner]>0
    assert mutant[mid]['counts'][owner]==mutant[mid]['port_calls'][owner]>0
controls=read(OUT/'controls-4/summary.json');assert len(controls['results'])==42 and all(r['caught'] for r in controls['results'])
assert controls['baseline']=='53b011249446c4a562624b573b84640726134c6b'
assert controls['menus_sha256']==digest(ROOT/'runtime/original_match/port/menus.py')
assert controls['tests_sha256']==digest(ROOT/'tests/test_port_menus.py')
mapdata=read(OUT/'unreached-map-3.json');assert mapdata['unreached_blocks']==209
assert mapdata['tests_sha256']==digest(ROOT/'tests/test_port_menus.py')
validation=OUT/'validation-final-1';assert source_matches(read(validation/'source.json'))
assert read(validation/'results.json')=={'owned-unit':0,'check':0,'annotations':0,'full-suite':0}
for name in ('owned-unit','check','annotations','full-suite'):
    assert (validation/(name+'.exit')).read_text().strip()=='0'
assert 'OK' in (validation/'full-suite.log').read_text()
report={'dispatch_head':dispatch,'comparisons':reports,'entry_call_checks':len(counter_rows),
        'menu_entries':27,'port_modules':17,'mask':[],'falsifiers':proof,'controls_caught':42,
        'unit_methods':42,'unvisited_blocks_mapped':209,'references':{str(p.relative_to(ROOT)):digest(p) for p in (rawref,displayref,oldraw,olddisplay)},
        'sources_match':True,'known_limit':'https://github.com/diegoami/goal2-archaeology/issues/394'}
output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
