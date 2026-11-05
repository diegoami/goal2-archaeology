"""Declared synthetic near-call frames for the original-backed T122a branch proof.

The source state is published E040-r0004, hash verified by E040's manifest.
Only the declared private-memory inputs below are changed. No guest bytes enter
this record. A direct call uses the original near-call stack layout (words pushed
in order); Prover compares the translated routine with the original including
ordered non-frame writes, kit visits, nested results and returned AX/DX.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'runtime'))
sys.path.insert(0,str(ROOT/'experiments/E040-route-fixture-writes'))
# Kept separate from the normal route input edits; these are synthetic frames.
from original_match import port, route as R
from original_match.image import Image
from original_match.port.prove import Prover, ProofError
import runner


def cases():
    out=[]
    def add(name,address,words=(),**edits): out.append((name,'000E:'+address,words,edits))
    add('center-short','03C4',('OUT_SEG','OUT_OFF','TEXT_SEG','TEXT_OFF',9))
    add('center-exact','03C4',('OUT_SEG','OUT_OFF','TEXT_SEG','TEXT_OFF',3))
    for char in (6,7): add('crowd-char-'+str(char),'045D',(2,'PARENT'),video_char=char)
    add('tune-first-poll','04F5',(8,'PARENT'))
    add('tune-one-note','04F5',(4,'PARENT'),tune_polls=[None,13])
    add('tune-all-notes','04F5',(0,'PARENT'),tune_polls=[None]*16)
    for flags in ((0,0,0),(1,0,0),(1,0,1),(0,1,0)):
        add('celebrate-'+''.join(map(str,flags)),'0572',('PARENT',),flags=flags)
    add('manager-quote','0868', (5,'TEXT_SEG','TEXT_OFF','TEXT_SEG','TEXT_OFF'))
    add('player-name','08F9',('OUT_SEG','OUT_OFF','PARENT'))
    add('red-name-none','094A',('OUT_SEG','OUT_OFF','PARENT'),red_cards=[])
    add('red-name-multiple','094A',('OUT_SEG','OUT_OFF','PARENT'),red_cards=[1,20])
    for side in (0,1):
        for address in ('09DB','0A53','0B0A','1F4D'):
            words=('OUT_SEG','OUT_OFF','PARENT') if address=='0B0A' else ('PARENT',)
            add(address+'-side-'+str(side),address,words,side=side)
    for address in ('0ACB','0B4D'): add(address,address,('OUT_SEG','OUT_OFF','PARENT'))
    for year,kind,finals,group,exempt in ((1,2,0,0,0),(2,1,0,0,0),(2,2,1,1,0),(2,2,1,0,0),(2,2,0,0,1),(65535,2,0,0,0)):
        add('sack-'+ '-'.join(map(str,(year,kind,finals,group,exempt))),'0B77',('PARENT',),year=year,kind=kind,finals=finals,group=group,exempt=exempt)
    add('red-headline','0C3A',('WRAPPER',),red_cards=[1])
    add('result-headings','2E1F',('TEXT_SEG','TEXT_OFF')*3+('PARENT',))
    add('fan-quote','3A5E',('TEXT_SEG','TEXT_OFF','WRAPPER'))
    add('manager-row','4045',('TEXT_SEG','TEXT_OFF')*2+('WRAPPER',))
    add('board-quote','47E6',('TEXT_SEG','TEXT_OFF')*2+('WRAPPER',))
    for values in ((10,2,1),(11,2,1),(10,3,1),(10,2,2)):
        add('discipline-'+ '-'.join(map(str,values)),'4865',('WRAPPER',),discipline=values)
    return out


def prove(data,case,variant=None):
    name,address,args,edits=case
    image=Image.from_savestate(data)
    image.memory=bytearray(image.memory)
    r=R.Route(image,record_writes=False)
    m=r.m
    ss=m.seg(0x3052); sp=0x3900; parent=0x4200; wrapper=0x4300; outer=0x4400
    text=0x4500; output=0x4700
    params={'OUT_SEG':ss,'OUT_OFF':output,'TEXT_SEG':ss,'TEXT_OFF':text,'PARENT':parent,'WRAPPER':wrapper}
    declared=[]
    def write(linear,data,why):
        before=m.read(linear,len(data));m.write(linear,data)
        declared.append({'linear':linear,'old_sha256':hashlib.sha256(before).hexdigest(),'new_sha256':hashlib.sha256(data).hexdigest(),'why':why})
    def word(off,value,why): write(ss*16+off,(value&65535).to_bytes(2,'little'),why)
    def byte(off,value,why): write(ss*16+off,bytes([value]),why)
    word(wrapper+4,parent,'wrapper parent link');word(outer+4,wrapper,'outer parent link')
    # A real published managed fixture, keeping country/side coherent.
    managed=set(image.managed_countries())
    fixtures=[]
    for index in range(image.fixture_index(),image.rd_far(0xA923,0x28)):
        fx=m.far(0xA92B)+8*(index-1)
        countries=[m.word_at(fx+4),m.word_at(fx+6)]
        if any(c in managed for c in countries):
            fixtures.append((index,fx,countries))
    index,fx,countries=fixtures[0]
    side=edits.get('side',next(i for i,c in enumerate(countries) if c in managed))
    country=countries[side]
    fxseg=m.rd(0xA92D);fxoff=(m.rd(0xA92B)+8*(index-1))&65535
    word(parent+4,fxoff,'published managed fixture offset');word(parent+6,fxseg,'published managed fixture segment')
    write(m.DS*16+R.DELAY_COUNT,R.DELAY_COUNT_VALUE.to_bytes(4,'little'),'same delay calibration as Route.call()')
    word(parent+8,country,'news country');word(parent-6,1,'selected squad slot');byte(parent-1,side,'selected fixture side')
    # 4865 follows two caller links; start it from outer.
    if address=='000E:4865': params['WRAPPER']=outer
    word(wrapper+6,5,'quote row argument')
    write(ss*16+text,b'\x03ABC','synthetic Pascal text')
    for off,value in zip((4,6),edits.get('flags',(0,0,0))[:2]): byte(parent+off,value,'celebration flag')
    if 'flags' in edits:
        game=m.far(0xA923); write(game+0x40,bytes([edits['flags'][2]]),'world-mode flag')
    # Restore fixture pointer overwritten above: celebration uses flags, other routines use fixture.
    if address!='000E:0572':
        word(parent+4,fxoff,'published managed fixture offset');word(parent+6,fxseg,'published managed fixture segment')
    if 'video_char' in edits:
        write(m.far(0xA96A),bytes([edits['video_char'],0x70])*2000,'controlled video character/attribute cells')
    if 'red_cards' in edits:
        cbase=m.far(0xA917)+0xBF*country
        for slot in range(1,21):
            player=m.word_at(cbase+2*(slot-1));addr=m.far(0xA91B)+20*player+0x10
            before=m.read(addr,1)[0];after=(before&~32)|(32 if slot in edits['red_cards'] else 0)
            write(addr,bytes([after]),'status bit6 for squad slot '+str(slot))
    if 'year' in edits:
        game=m.far(0xA923); cbase=m.far(0xA917)+0xBF*country;manager=m.read(cbase+0x2E,1)[0]
        assert country in managed and manager>=0x80, (country,manager)
        write(game+0x38,edits['year'].to_bytes(2,'little'),'year word')
        write(fx+2,bytes([edits['kind']]),'fixture kind')
        write(game+0x3C,bytes([3 if edits['finals'] else 2]),'actual stage byte +3C for original59D8')
        write(game+manager-0x7F,bytes([edits['group']]),'manager group')
        write(cbase+0xBE,bytes([edits['exempt']]),'country sack exemption')
    if 'discipline' in edits:
        for off,value in zip((0x7B84,0x7B85,0x7B86),edits['discipline']):
            write(m.DS*16+off+10*side,bytes([value]),'discipline statistic')
    if 'tune_polls' in edits:
        values=iter(edits['tune_polls']);r.keys.policy['000E:0515']=lambda route,site: next(values)
    reg=port._module_registry('news');copy=port.Registry('news',reg.doc);copy.entries={address:reg.entries[address]};copy.variants=reg.variants
    installed=port.install(m,[(copy,variant)])
    prover=Prover(m,installed)
    words=[0x7080]+list(reversed([params.get(w,w) for w in args]))
    for i,value in enumerate(words): word(sp+2*i,value,'near-call stack')
    for key,value in (('ss',ss),('sp',sp),('bp',0x3F00),('ds',m.DS),('es',m.DS),('cs',m.seg(0xE)),('eip',int(address.split(':')[1],16))):m.set_reg(key,value)
    m.at('000E:7080',lambda replay:m.stop('synthetic-return'))
    status,error='completed',None
    try:
        reason=m.run(m.lin('000E:7080')+1,fresh=True)
        if reason!='synthetic-return':raise RuntimeError('unexpected stop '+str(reason))
    except ProofError as exc: status,error='differs',str(exc)
    except Exception as exc:status,error='aborted',type(exc).__name__+': '+str(exc)
    return {'case':name,'routine':address,'synthetic':True,'fixture_index':index,'country':country,'side':side,'inputs':declared,'status':status,'error':error,'calls':installed.calls,'proof':prover.summary()}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--variant');ap.add_argument('--cases');ap.add_argument('--no-record',action='store_true');a=ap.parse_args()
    if not a.no_record:
        paths=['runtime/original_match','experiments/E040-route-fixture-writes/prove.py',str(Path(__file__).relative_to(ROOT))]
        dirty=subprocess.check_output(['git','status','--porcelain','--',*paths],cwd=ROOT,text=True)
        if dirty: raise SystemExit('refused: uncommitted proof source changes:\n'+dirty)
    chosen=cases()
    if a.cases: chosen=[c for c in chosen if c[0] in a.cases.split(',')]
    if a.variant: chosen=[c for c in chosen if c[1]==('000E:045D' if a.variant=='crowd-draw-dropped' else '000E:03C4')]
    case=next(c for c in runner.CASES if c[0]=='E040-r0004');path=ROOT/'.cache/dl'/case[3]
    digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==runner.expected(case[3])
    results=[]
    for c in chosen:
        result=prove(path.read_bytes(),c,a.variant);results.append(result)
        print(c[0],result['status'],result['error'],flush=True)
        if result['status']!='completed':break
    bad=[r for r in results if r['status']!='completed' or r['proof'][r['routine']]['proved']!=1 or r['proof'][r['routine']]['before']]
    caught=bool(a.variant and results and results[-1]['status']=='differs')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    record={'schema':'e040-t122a-synthetic/1','task':'T122a','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'source_state':{'asset':case[3],'sha256':digest},'variant':a.variant,'caught':caught,'passes':results,
            'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'runtime/original_match/port/news.py']}}
    if not a.no_record:
        out=HERE/('synthetic-'+(a.variant or 'normal')+'-'+stamp+'.json');assert not out.exists();out.write_text(json.dumps(record,indent=1)+'\n');print('record:',out,flush=True)
    return 0 if (caught if a.variant else not bad) else 1

if __name__=='__main__':sys.exit(main())
