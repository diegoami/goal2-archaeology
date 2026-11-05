"""#663: same admitted E006 input, two half-time pairs, original and port.
Input decisions contain deliberate extra edit acknowledgements in incremental mode;
all original output events and all memory remain compared without masks.
"""
import argparse, copy, hashlib, json, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import family, records
from original_match import Image, Fixture, Match
p=argparse.ArgumentParser()
p.add_argument('--engine',choices=('original','port'),required=True)
p.add_argument('--mode',choices=('incremental','batch'),required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
raw=(ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
image_hash=hashlib.sha256(raw).hexdigest()
assert image_hash=='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
m=Match(Image.from_savestate(raw),Fixture(7,19,index=21),managed=7,seed=0x1234,delay_byte=0,
        record_draws=True,engine=a.engine,ports=['all'] if a.engine=='port' else [],timeout_s=600)
events=[]; snapshots=[]; pairs=[]; original_left=None; started=time.monotonic()
for e in m.events():
    events.append((e.kind,e.minute,e.score,copy.deepcopy(e.data)))
    if e.kind!='decision': continue
    d=e.data
    if d['context']!='half_time': m.answer(); continue
    if not pairs:
        pairs=[[d['eleven'][6],d['bench'][0]],[d['eleven'][7],d['bench'][1]]]
        original_left=d['substitutions_left']
        if a.mode=='batch': m.answer(substitutions=pairs); continue
    if a.mode=='batch': raise AssertionError('unexpected repeat half-time decision')
    made=[event for event in events if event[0]=='substitution' and event[3]['team']==m.side]
    done=len(snapshots)
    assert len(made)==done,(done,made)
    assert d['substitutions_left']==original_left-done
    assert not d.get('requested')
    assert e.minute==45,e
    for off,on in pairs[:done]:
        assert off in d['bench'] and on in d['eleven']
        assert sum(event[3]['off']==off and event[3]['on']==on for event in made)==1
    snapshots.append(dict(minute=e.minute,eleven=d['eleven'],bench=d['bench'],left=d['substitutions_left'],made=done))
    if done<2: m.answer(substitutions=[pairs[done]],edit_only=True)
    else: m.answer()
result=m.result()
for off,on in pairs:
    assert sum(e['off']==off and e['on']==on and e['team']==m.side for e in result['substitutions'])==1
receipt=dict(engine=a.engine,mode=a.mode,elapsed_s=time.monotonic()-started,completed=True,pairs=pairs,
 snapshots=snapshots,result_sha256=records.result_digest(result),events_sha256=family.display_events_digest(events),
 original_output_sha256=family.display_events_digest([e for e in events if e[0]!='decision']),
 after=family.digest_memory(m,[],image_hash),memory_mask=[],draws=result['draws'],draws_digest=result['draws_digest'],
 score=result['score'],substitutions=result['substitutions'])
a.out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('engine','mode','elapsed_s','score','draws')}),flush=True)
