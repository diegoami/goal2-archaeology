"""Ported corroboration of requested, returned and caller-stored takers."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
from original_match import Match,Fixture,Image
import families

receipt={'ports':['takers'],'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted((ROOT/'runtime/original_match').rglob('*.py'))}}
spec=next(m for m in families.discover()['S'].matches if m.id=='S/set-piece-taker')
image=Image.from_savestate((ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes())
m=Match(image,Fixture(*spec.fixture[:2],index=spec.fixture[2],kind=spec.fixture[3]),managed=spec.managed,set_piece=True,ports=["takers"])
returns=[];observations=[];pending=None
def returned(replay):
    if not replay:
        role=m.m.frame_word(m.m.reg('bp'),4)&255
        if role in (2,3,4,5):returns.append({'role':role,'ax':m.m.reg('ax')})
m.m.at('0791:D010',returned)
for ev in m.events():
    if ev.kind=='decision':
        if ev.data['context']=='set_piece':
            pending={'minute':ev.minute,'role':ev.data['role'],'current':ev.data['current'],
                     'requested':next(w for w in reversed(ev.data['available']) if w!=ev.data['current'])}
        spec.policy.answer(m,ev.data)
    elif ev.kind=='set_piece':
        stored=m.m.rd(0x9976+10*m.side+2*ev.data['role'])
        observation={**pending,'returned':returns[-1]['ax'],'event_player':ev.data['player'],'stored':stored}
        assert len({observation[k] for k in ('requested','returned','event_player','stored')})==1,observation
        assert observation['current']!=observation['requested'],observation
        observations.append(observation);pending=None
assert observations and len(observations)==len(returns)
assert not m.port_frames(),m.port_frames()
receipt.update(image_sha256=image.sha256(),scenario=spec.id,spec_sha256=spec.sha256,observations=observations)
(OUT/'ported-taker-observations-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(observations,indent=2))
