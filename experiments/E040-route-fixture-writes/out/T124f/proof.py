"""Actual pre70E6 natural in-season tails and original80DA entry captures.

Both arms restore all16CPU registers and queued key, then resume saved70E6;
no Route.call/round prefix is replayed and no stage/result/data byte is edited.
"""
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import port,route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS
from original_match.port import Registry,ageing,stages
from original_match.port.prove import Prover
from tests.test_port_in_season_ageing import specs as age_specs
from tests.test_port_stage_news import specs as news_specs
_sp=importlib.util.spec_from_file_location('_t124f_dprepare',HERE.parent/'T124d/prepare.py')
D=importlib.util.module_from_spec(_sp);_sp.loader.exec_module(D)
sha=D.sha


def emit(f,v):
    f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v[k] for k in ('schema','case','status','elapsed_s') if k in v}),flush=True)


def sources():
    paths=['runtime/original_match/route.py','runtime/original_match/route_team.py','runtime/original_match/match.py',
      'runtime/original_match/machine.py','runtime/original_match/image.py','runtime/original_match/news.py',
      'tests/test_port_in_season_ageing.py','tests/test_port_stage_news.py','tests/test_port_stages.py',
      str(Path(__file__).relative_to(ROOT)),str((HERE.parent/'T124d/prepare.py').relative_to(ROOT))]
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'runtime/original_match/port').glob('*.py'))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def source(case):
    if case=='continental':
        path=HERE.parent/'T124c/natural-groups-input-v1.jsonl'
        row=next(v for v in map(json.loads,path.read_text().splitlines()) if v.get('status')=='builder-entry')
        expected='bf6d6f0add055ca9765ddfced6d6b2d167056702e23f15b6ebd469d10898250a'
    else:
        path=HERE.parent/'T124d/natural-inputs-v1.jsonl'
        row=next(v for v in map(json.loads,path.read_text().splitlines()) if v.get('status')=='constructor-entry' and v['phase']=='groups')
        expected='90475e959f3263f92b16d6a2161df514dbff6fb6a27a8d177db12bae4666d449'
    cp=row['before_stage_end']['checkpoint'];assert cp['sha256']==expected
    assert (cp['context']['regs']['EIP'],cp['context']['regs']['ESP'],cp['context']['regs']['EBP'])==(0x70E6,0x3EE2,0x3EEA)
    return cp,path


def load(cp):
    data=(ROOT/cp['path']).read_bytes();assert sha(data)==cp['sha256']
    r=R.Route(Image(data),entry='play_round',record_writes=False)
    D.restore(r,cp['context']);assert not r.m._ports
    return r


def checkpoint(r,label):
    assert not r.m.frames and not r.m.muted
    data=r.header+r.m.read(0,MEM_SIZE)+r.tail;h=sha(data)
    p=ROOT/'.cache/t124f'/f'{label}-{h[:16]}.mem';p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():p.write_bytes(data)
    assert sha(p.read_bytes())==h
    return {'path':str(p.relative_to(ROOT)),'sha256':h,'context':D.context(r)}


def specs(variant=None):
    wanted=set(stages.PORTS.entries)|{'214B:1D6F','1771:5C94','1771:5CCB'}
    for reg,_ in age_specs()+news_specs():wanted.update(reg.entries)
    out=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for address,e in reg.entries.items():
            if address in wanted:assert not e.stub;sub._add(e)
        if sub.entries:sub.variants=dict(reg.variants);out.append((sub,variant if reg.name=='ageing' else None))
    assert {a for reg,_ in out for a in reg.entries}==wanted
    return out


def hashes(m):
    return {name:sha(m.read(m.far(ptr),size)) for name,ptr,size in [('players3061',0xA91B,3061*20),
     ('countries129',0xA917,129*191),('managers',0xA91F,0x195),('pool_indices',0xA927,0x3C2),
     ('fixtures2408',0xA92B,2408*8),('country_lists',0xA92F,0x48*129),('groups',0xA933,0x1C00),('game',0xA923,0x10E)]}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['continental','world'],required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    cp,path=source(a.case);start=time.monotonic();ref=load(cp);entry={};before=D.game(ref.m)
    assert before['stage']==(2 if a.case=='continental' else 6)
    def entered(replay):
        if replay:return
        m=ref.m;assert D.game(m)['stage']==(3 if a.case=='continental' else 7)
        assert m.stack_word(0)==0x826D
        entry.update(checkpoint=checkpoint(ref,a.case+'-80DA-entry'),game=D.game(m))
    ref.m.at('1771:80DA',entered)
    assert ref.m.run(ref.m.lin('000E:77C2'),300,fresh=True) is None
    assert entry
    r=load(cp);inst=port.install(r.m,specs());p=Prover(r.m,inst)
    with Path(a.out).open('x') as f:
        emit(f,{'schema':'t124f-natural-tail/1','case':a.case,'source':cp,'source_receipt':str(path.relative_to(ROOT)),
          'source_receipt_sha256':sha(path.read_bytes()),'source_hashes':sources(),
          'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'model':'inherited Codex GPT-6 family; exact variant unavailable',
          'scope':'PRIMARY actual original pre70E6; fullCPU/key restore; m.run77C2, no editedstage or Route.call prefix; no annual rollover'})
        emit(f,{'status':'original-80DA-entry','case':a.case,**entry})
        assert r.m.run(r.m.lin('000E:77C2'),300,fresh=True) is None
        original=ref.m.read(0,MEM_SIZE);candidate=r.m.read(0,MEM_SIZE)
        regs={n:[ref.m.reg(n),r.m.reg(n)] for n in REGS if ref.m.reg(n)!=r.m.reg(n)}
        assert r.record==ref.record and r.keys.waiting==ref.keys.waiting and r.news_history==ref.news_history
        summary=p.summary();assert summary['1771:80DA']['nested']==1
        assert summary['1771:7FDF']['nested']==128
        assert D.game(r.m)['year_word']==before['year_word']
        emit(f,{'status':'completed','case':a.case,'start':before,'end':D.game(r.m),'summary':summary,
          'all_memory_equal':original==candidate,'original_memory_sha256':sha(original),'candidate_memory_sha256':sha(candidate),
          'register_differences':regs,'records_equal':True,'waiting_key_equal':True,'actual_page_history_equal':True,
          'page_hashes':[sha(v.cells) for v in r.news_history],
          'ordered_record_sha256':sha(json.dumps(D.public(r.record),sort_keys=True).encode()),
          'rng_events':sum(v[0]=='rng' for v in r.record),'record_hashes':hashes(r.m),'elapsed_s':round(time.monotonic()-start,4)})
        assert original==candidate and not regs
if __name__=='__main__':main()
