"""Corrected DECLARED SYNTHETIC world fixtures; never a natural-season claim.

Original6970 may simulate managed fixtures deliberately; after EACH calendar
actual originalRoute.call at cursor=count executes the FULL outer8757/85F7
finalization at real706E return frame and actualstage_end/nextconstructor.
No host scores/ranks/winnerflags. Formal source is original nativeCP4. Tests
without private captures may synthesize an initial world draw from nativeE006
through original76B1/6730 with explicit stage5/year0/mode1 parameters.
All legacyB1/B2 files/measurements remain unchanged (#673).
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
from original_match import route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE,GuestError
from original_match.match import SS_PARAGRAPH
_spec=importlib.util.spec_from_file_location('_t124d_prepare_reference',HERE/'prepare.py')
P=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(P)


def word(m,p,v):m.write(p,(v&65535).to_bytes(2,'little'))


def original_call(r,target,ret,sp,bp,args=(),far=False):
    m=r.m;ss=m.seg(SS_PARAGRAPH);rs,ro=map(lambda s:int(s,16),ret.split(':'))
    values=[ro]+([m.seg(rs)] if far else [])+list(reversed(args))
    for i,value in enumerate(values):word(m,ss*16+sp+2*i,value)
    seg,off=map(lambda s:int(s,16),target.split(':'))
    for n,v in (('ss',ss),('sp',sp),('bp',bp),('ds',m.DS),('es',m.DS),('cs',m.seg(seg)),('eip',off)):m.set_reg(n,v)
    assert m.run(m.lin(ret),120,fresh=True) is None
    assert m.reg('sp')==sp+2*len(values)


def simulate_calendar(r):
    m=r.m;g=m.far(0xA923);start=m.word_at(g+0x26);end=m.word_at(g+0x28)
    ss=m.seg(SS_PARAGRAPH);parent=0x3EDE
    word(m,ss*16+parent,0x3EEA);word(m,ss*16+parent+2,0x70D4)
    word(m,ss*16+parent-0x10,m.rd(0xA923));word(m,ss*16+parent-0xE,m.rd(0xA925))
    word(m,ss*16+parent-6,start);m.write(ss*16+parent-2,b'\0')
    for n in range(start,end):
        assert m.word_at(g+0x26)==n
        original_call(r,'000E:6970','000E:7017',0x3EC4,parent,(parent,))
        assert m.word_at(g+0x26)==n+1
    return {'start':start,'end':end,'fixtures':end-start,'mechanism':'complete original6970; actualouterRoute finalization follows'}


def component(r):return r.header+r.m.read(0,MEM_SIZE)+r.tail


def make_inputs(base_image=None):
    if base_image is None:r=P.load(P.original_cp4());source={'kind':'nativeCP4','sha256':P.original_cp4()['sha256']}
    else:
        r=R.Route(base_image,entry='play_round',record_writes=False)
        m=r.m;g=m.far(0xA923)
        m.write(g+0x3C,bytes([5,1]));m.write(g+0x40,b'\x01');word(m,g+0x38,0)
        ss=m.seg(SS_PARAGRAPH);word(m,ss*16+0x3EEA,0x3FF6)
        original_call(r,'1771:76B1','000E:70F9',0x3EDE,0x3EEA,far=True)
        source={'kind':'declared synthetic E006 initialworld draw','edits':{'stage':5,'rounds':1,'mode':1,'year_word':0}}
    assert not r.m._ports
    state={'capture':True,'found':None,'index':0};finalizers=[];records=[];images={};afters={}
    def finalizer(replay):
        if not replay:
            m=r.m;s=m.reg('ss')*16+m.reg('sp')
            finalizers.append({'return':m.where(m.word_at(s+2),m.word_at(s)),'game':P.game(m)})
    def entry(replay,address):
        if replay or not state['capture']:return
        phase,target,stage,rounds=P.PHASES[state['index']]
        assert address==target and (P.game(r.m)['stage'],P.game(r.m)['rounds'])==(stage,rounds)
        state['found']={'component':component(r),'context':P.context(r),'phase':phase,'target':target,'game':P.game(r.m)}
        r.m.stop('corrected-synthetic-entry')
    r.m.at('1771:8757',finalizer)
    for target in sorted({v[1] for v in P.PHASES}):r.m.at(target,lambda replay,a=target:entry(replay,a))
    for i,(phase,target,stage,rounds) in enumerate(P.PHASES):
        simulated=simulate_calendar(r);before=len(finalizers)
        # The outer ORIGINAL route supplies706E itself, finalizes all groups/
        # aggregates, advances stage/round/ageing and enters the next constructor.
        try:r.call()
        except GuestError as exc:
            assert state['found'] and str(exc)=='play_round stopped: corrected-synthetic-entry'
        found=state['found'];assert found and found['phase']==phase
        visits=finalizers[before:];assert any(v['return']=='000E:706E' for v in visits)
        images[phase]=Image(found['component'])
        entry_data={'component':found['component'],'context':found['context']}
        aggregates=P.aggregate_records(r.m)
        state['capture']=False
        assert r.m.run(r.m.lin('000E:77C2'),300,fresh=True) is None
        afters[phase]=Image(component(r))
        records.append({'phase':phase,'source':source,'simulated':simulated,'finalizer_visits':visits,
            'entry':entry_data,'after':{'component':component(r),'context':P.context(r)},
            'entry_game':found['game'],'after_game':P.game(r.m),'aggregates_at_entry':aggregates})
        state.update(index=i+1,capture=True,found=None)
    return images,afters,records


def save_part(part,label):
    data=part['component'];h=P.sha(data);p=ROOT/'.cache/t124d/corrected-synthetic'/f'{label}-{h[:16]}.mem'
    p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
        with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    assert P.sha(p.read_bytes())==h
    return {'path':str(p.relative_to(ROOT)),'sha256':h,'context':part['context']}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    out=Path(a.out);assert not out.exists()
    _,_,records=make_inputs()
    with out.open('x') as f:
        P.emit(f,{'schema':'t124d-corrected-synthetic/1','source':'nativeCP4, but deliberate original6970 managedUI bypass',
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'source_hashes':{str(Path(__file__).relative_to(ROOT)):P.sha(Path(__file__).read_bytes()),**P.source_hashes()},
            'scope':'synthetic only; complete8757/85F7 viaactualRoute aftereachcalendar; no hostresults/ranks or B1v4inputs'})
        for r in records:
            phase=r['phase'];r['entry']=save_part(r['entry'],phase+'-entry');r['after']=save_part(r['after'],phase+'-after')
            P.emit(f,{'status':'corrected-phase',**r})
        P.emit(f,{'status':'completed','phases':[v[0] for v in P.PHASES],'fixtures':sum(v['simulated']['fixtures'] for v in records)})
if __name__=='__main__':main()
