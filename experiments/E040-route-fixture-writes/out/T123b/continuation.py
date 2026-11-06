"""T123b leaf on T124t's real original-menu continuation, complete key/CPU context.
Starts at T124t's verified round1 checkpoint; preserves automatic choice only in
RouteMatch's comparison harness. Every subsequent match remains the original.
"""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'runtime'),str(HERE)]
import prove
from original_match import route as R,port
from original_match.route_team import RouteMatch
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS
from original_match.port.prove import Prover

SOURCE_RECEIPT=ROOT/'experiments/E040-route-fixture-writes/out/T124t/continuation-context.jsonl'

def sha(data):return hashlib.sha256(data).hexdigest()
def hashes():
    paths=[Path(__file__),HERE/'prove.py',ROOT/'runtime/original_match/port/selection.py',
           ROOT/'runtime/original_match/route.py',ROOT/'runtime/original_match/route_team.py']
    return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}

def context(route):return {'regs':{r:route.m.reg(r) for r in REGS},'waiting_key':route.keys.waiting}
def restore(route,c):
    assert set(c['regs'])==set(REGS)
    for r,v in c['regs'].items():route.m.set_reg(r,v)
    route.keys.waiting=c['waiting_key']

def parent_state(m,bp):
    ss=m.reg('ss')*16
    def word(k):return int.from_bytes(m.read(ss+((bp+k)&65535),2),'little')
    country=word(6)
    return {'regs':{r:m.reg(r) for r in REGS},'parent_bp':bp,'saved_bp':word(0),
      'parent_return_offset':word(2),'parent_return_segment':word(4),'country':country,
      'mark':m.read(ss+((bp-1)&65535),1)[0],'pane':word(-5),'marked_pane':word(-7),'marked_index':word(-9),
      'marked_scroll':word(-11),'cursor':m.rd(0xC1B),'C1E':m.rd(0xC1E,1),'C1F':m.rd(0xC1F,1),
      'pushed_back':m.rd(0x79AE,1),'current_key':m.rd(0xA976,1),
      'rng':{hex(off):m.rd(off) for off in (0x7B62,0x8336)},
      'squad':[m.word_at(m.far(0xA917)+191*country+2*i) for i in range(20)]}


class LeafMatch(RouteMatch):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.leaf_frames=[]
        def entered(replay):
            bp=self.m.stack_word(2)
            self.leaf_frames.append({'entry':parent_state(self.m,bp)})
        def returned(replay):
            if self.leaf_frames and 'after' not in self.leaf_frames[-1]:
                self.leaf_frames[-1]['after']=parent_state(self.m,self.leaf_frames[-1]['entry']['parent_bp'])
        self.m.at('0791:DEA6',entered);self.m.at('0791:E672',returned)
        self.leaf_inst=port.install(self.m,prove.leaf())
        self.leaf_prover=Prover(self.m,self.leaf_inst,where=lambda:f"T123b fixture {self.opts['index']}")


def run(out,resume=False,stop_after=4):
    accepted=[json.loads(l) for l in SOURCE_RECEIPT.read_text().splitlines()]
    source_round=next(r for r in accepted if r.get('status')=='round' and r['round']==1)
    source_cp=source_round['checkpoint'];source_path=ROOT/source_cp['path'];data=source_path.read_bytes()
    assert sha(data)==source_cp['sha256']
    header={'schema':'t123b-continuation/1','source_receipt':str(SOURCE_RECEIPT.relative_to(ROOT)),
      'source_receipt_sha256':sha(SOURCE_RECEIPT.read_bytes()),'source_checkpoint':source_cp,
      'source_hashes':hashes(),'input_type':'accepted original T124t continuation checkpoint; no record edits',
      'entry':'play_round','method':'original RouteMatch menu key policy, only bounded DEA6 ported in its actual Match machine'}
    previous=[];image=Image(data);cpu=source_cp['context']
    if resume:
        old=[json.loads(l) for l in out.read_text().splitlines()]
        assert old[0]==header,'resume source/context differs'
        previous=[r for r in old if r.get('status')=='round']
        if previous:
            checkpoint=previous[-1]['checkpoint'];data=(ROOT/checkpoint['path']).read_bytes()
            assert sha(data)==checkpoint['sha256'];image=Image(data);cpu=checkpoint['context']
    R.RouteMatch=LeafMatch
    route=R.Route(image,entry='play_round',record_writes=False);restore(route,cpu)
    start=time.monotonic()
    with out.open('a' if resume else 'x') as f:
      def record(v):f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
      if not resume:record(header)
      first=previous[-1]['round']+1 if previous else 2
      for number in range(first,5):
        begin=len(route.record);before=context(route)
        try:route.round()
        except Exception as exc:
            record({'status':'failed','round':number,'error':type(exc).__name__+': '+str(exc),'context':context(route)})
            raise
        entries=route.record[begin:];end=next(e[1] for e in reversed(entries) if e[0]=='round_end')
        current=route.header+route.m.read(0,MEM_SIZE)+route.tail;digest=sha(current)
        checkpoint=ROOT/'.cache/t123b'/out.stem/f'round-{number}-{digest[:16]}.mem';checkpoint.parent.mkdir(parents=True,exist_ok=True)
        if not checkpoint.exists():
            with checkpoint.open('xb') as cp:cp.write(current)
        assert sha(checkpoint.read_bytes())==digest
        matches=[]
        # Route.matches accumulates all matches; this round's fixtures identify the newly completed ones.
        fixtures={e[1]['fixture'] for e in entries if e[0]=='match'}
        for match in route.matches:
            if match.opts['index'] not in fixtures:continue
            summary=match.leaf_prover.summary();count=match.leaf_inst.calls['0791:DEA6']
            assert summary['0791:DEA6']['proved']==count and summary['0791:DEA6']['before']==0
            assert not summary['0791:DEA6']['scratch']
            assert len(match.leaf_frames)==count and all('after' in frame for frame in match.leaf_frames)
            matches.append({'fixture':match.opts['index'],'proof':summary,'calls':match.leaf_inst.calls,
              'frames':match.leaf_frames,'choices':match.team_choices,'keys':match.team_keys,
              'final_regs':{r:match.m.reg(r) for r in REGS},'final_memory_sha256':sha(match.m.read(0,MEM_SIZE))})
        record({'status':'round','round':number,'end':end,'before_context':before,'after_context':context(route),
          'checkpoint':{'path':str(checkpoint.relative_to(ROOT)),'sha256':digest,'context':context(route)},
          'leaf_matches':matches,'route_keys':[e for e in entries if e[0]=='key'],
          'matches':[e[1] for e in entries if e[0]=='match'],'teams':[e[1] for e in entries if e[0]=='team'],
          'elapsed_s':round(time.monotonic()-start,3)})
        print('round',number,'end',end,'leaf_calls',sum(m['calls']['0791:DEA6'] for m in matches),flush=True)
        if number==stop_after and number<4:record({'status':'paused','after_round':number});return
      record({'status':'completed','through_round':4,'final_context':context(route),'elapsed_s':round(time.monotonic()-start,3)})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--resume',action='store_true')
    p.add_argument('--stop-after',type=int,choices=(2,3,4),default=4);a=p.parse_args();run(a.out,a.resume,a.stop_after)
