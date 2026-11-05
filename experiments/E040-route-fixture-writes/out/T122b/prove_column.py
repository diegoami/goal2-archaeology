"""Declared synthetic near-call frames for the original-backed T122b branch proof.

[confirmed: F039; code/seg_000E_02.asm11D9-1F4C,
seg_0791_18.asmB71C-B7F9, seg_1771_02.asm10E7-114A,
port/pilot.py rand: original seed LCG and one-based bounded draw.]

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


DECISION_RETURNS = {4861: 'far 1771:5C60', 4909: 'far 1771:5C60', 4919: '0x9db', 5000: 'far 0791:B71C', 5019: 'far 214B:06B1', 5103: 'far 214B:06B1', 5217: 'far 214B:06B1', 5357: 'far 1771:5C60', 5374: 'far 214B:06B1', 5536: 'far 214B:06B1', 5682: 'far 214B:06B1', 5882: 'far 214B:06B1', 6028: 'far 214B:06B1', 6236: 'far 214B:06B1', 6430: 'far 214B:06FA', 6545: 'far 214B:06FA', 6757: 'far 1771:5C60', 6770: '0x9db', 6783: 'far 214B:06B1', 6854: '0xa53', 6867: 'far 214B:06B1', 6940: 'far 214B:06B1', 7019: 'far 1771:5C60', 7059: '0xb77', 7276: 'far 1771:5C60', 7290: '0x9db', 7306: 'far 214B:06B1', 7434: '0xa53', 7450: 'far 214B:06B1', 7587: 'far 214B:06B1', 7690: '0x9db', 7703: 'far 214B:06B1', 7774: '0xa53', 7787: 'far 214B:06B1', 7889: 'far 214B:06B1'}

def cases():
    """Declared branch families. Byte255 ranking is an authored signed-arithmetic
    stress input, not a claim about a naturally reachable ranking. Parent frames
    always select the real managed country, with sides swapped coherently.
    """
    out=[]
    def add(name,**edits):out.append((name,'000E:11D9',('PARENT',),edits))
    for side in (0,1):
        for kind in (0xCB,0x67,0xC9,0x65,0xC8,8):
            for result in ('win','loss'):
                add(f'special-{side}-{kind}-{result}',side=side,kind=kind,result=result,margin=1)
        for result in ('win','loss','draw'):
            for margin in ((0,) if result=='draw' else (0,1,3,6)):
                for rating in ('balanced','strong','weak'):
                    for seed in (0, 1, 6, 7, 11, 16):
                        add(f'ordinary-{side}-{result}-{margin}-{rating}-{seed}',side=side,kind=2,result=result,margin=margin,rating=rating,seed=seed)
        for score in (-128,-11,-10,-8,-7,-6,-5,0):
            for winless in (3,4):
                add(f'sack-{side}-{score}-{winless}',side=side,kind=2,result='loss',margin=2,year=2,confidence=score,winless=winless)
        for result in ('win','loss'):
            for margin in (0,1,3):
                add(f'red-{side}-{result}-{margin}',side=side,kind=2,result=result,margin=margin,red_cards=[1])
    for side in (0,1):
        for rating in ('q-minus-1','q-minus-2','q-minus-3'):
            for margin in (1,3,6):
                for seed in (0,1,6,7,11,16):
                    add(f'confidence-{side}-{rating}-{margin}-{seed}',side=side,kind=2,result='win',margin=margin,rating=rating,seed=seed)
    for seed in (0,1,6,7,11,16):
        add(f'confidence-1-q-minus-6-stress-1-{seed}',side=1,kind=2,result='win',margin=1,rating='q-minus-6-stress',seed=seed)
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
    managed_country=next(c for c in countries if c in managed)
    side=edits.get('side',countries.index(managed_country))
    if countries[side]!=managed_country:
        countries.reverse()
        write(fx+4,b''.join(c.to_bytes(2,'little') for c in countries),'coherently swap published fixture countries for managed side')
    country=countries[side]
    assert country==managed_country
    fxseg=m.rd(0xA92D);fxoff=(m.rd(0xA92B)+8*(index-1))&65535
    word(parent+4,fxoff,'published managed fixture offset');word(parent+6,fxseg,'published managed fixture segment')
    write(m.DS*16+R.DELAY_COUNT,R.DELAY_COUNT_VALUE.to_bytes(4,'little'),'same delay calibration as Route.call()')
    word(parent+8,country,'news country');word(parent-6,1,'selected squad slot');byte(parent-1,side,'selected fixture side')
    # 4865 follows two caller links; start it from outer.
    if address=='000E:4865': params['WRAPPER']=outer
    word(wrapper+6,5,'quote row argument')
    write(ss*16+text,b'\x03ABC','synthetic Pascal text')
    # Result-column inputs use the same published managed fixture and complete
    # original memory. Edits are authored scalar fields, recorded only by hash.
    result=edits.get('result','win');margin=edits.get('margin',1)
    goals=[0,0]
    if result=='win':goals[side]=margin;winner=side
    elif result=='loss':goals[1-side]=margin;winner=1-side
    else:winner=2
    write(fx,bytes(goals),'authored goals for '+result+' margin '+str(margin))
    write(fx+2,bytes([edits.get('kind',2),winner]),'fixture kind and winner')
    game=m.far(0xA923);cbase=m.far(0xA917)+0xBF*country
    manager=m.read(cbase+0x2E,1)[0];assert manager>=0x80
    write(game+0x38,edits.get('year',1).to_bytes(2,'little'),'year word')
    write(game,bytes([1]),'stage1 avoids finals-table exemption')
    write(cbase+0xBE,bytes([0]),'no sack exemption')
    write(cbase+0xB8,bytes([edits.get('winless',0)]),'country winless counter')
    if 'confidence' in edits:
        write(m.far(0xA91F)+3*manager+2,bytes([edits['confidence']&255]),'signed manager confidence byte '+str(edits['confidence']))
    rating=edits.get('rating','balanced')
    ranking_records={
        'balanced':((16,64,1),(16,64,1)),
        'strong':((1,64,1),(255,64,1)),
        'weak':((255,64,1),(1,64,1)),
        # Original10E7 ratings produce B71C's pre-margin quotient -1/-2/-3.
        'q-minus-1':((1,64,1),(32,64,1)),
        'q-minus-2':((1,1,1),(32,64,1)),
        'q-minus-3':((1,1,1),(32,128,1)),
        # Explicit scalar-byte stress beyond a normal regional ranking.
        'q-minus-6-stress':((1,1,1),(72,128,1)),
    }[rating]
    for which,c in enumerate((country,countries[1-side])):
        base=m.far(0xA917)+0xBF*c
        write(base+0x2A,bytes(ranking_records[which]),'ranking/world-ranking/continent fields for '+rating+' rating family')
    write(m.far(0xA978),edits.get('seed',0).to_bytes(2,'little'),'declared original RNG seed')
    for k in (0,1):
        write(m.DS*16+0x7B7E+10*k,bytes([goals[k],0,0,0,0,0,0,0,int(bool(edits.get('red_cards')) and k==side),0]),'coherent bounded match-stat row')
    if 'red_cards' in edits:
        cbase=m.far(0xA917)+0xBF*country
        for slot in range(1,21):
            player=m.word_at(cbase+2*(slot-1));addr=m.far(0xA91B)+20*player+0x10
            before=m.read(addr,1)[0];after=(before&~32)|(32 if slot in edits['red_cards'] else 0)
            write(addr,bytes([after]),'status bit6 for squad slot '+str(slot))
    reg=port._module_registry('news');copy=port.Registry('news',reg.doc);copy.entries={address:reg.entries[address]};copy.variants=reg.variants
    installed=port.install(m,[(copy,variant)])
    decisions=[]
    def capture(ret):
        def visit(replay):
            if not replay:
                value=m.reg('ax')
                decisions.append({'return':f'000E:{ret:04X}','target':DECISION_RETURNS[ret],
                                  'ax':value,'al':value&255,'signed_ax':(value+32768)%65536-32768})
        return visit
    for ret in DECISION_RETURNS:m.at(f'000E:{ret:04X}',capture(ret))
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
    return {'case':name,'routine':address,'synthetic':True,'authored_inputs':edits,'category':'rank-byte-stress' if edits.get('rating') in ('strong','weak','q-minus-6-stress') else 'declared-ordinary','fixture_index':index,'country':country,'side':side,'inputs':declared,'status':status,'error':error,'calls':installed.calls,'proof':prover.summary(),'decision_calls':decisions}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--variant');ap.add_argument('--cases');ap.add_argument('--no-record',action='store_true');ap.add_argument('--group');ap.add_argument('--out',type=Path,default=HERE);a=ap.parse_args()
    if not a.no_record:
        paths=['runtime/original_match','experiments/E040-route-fixture-writes/prove.py',str(Path(__file__).relative_to(ROOT))]
        dirty=subprocess.check_output(['git','status','--porcelain','--',*paths],cwd=ROOT,text=True)
        if dirty: raise SystemExit('refused: uncommitted proof source changes:\n'+dirty)
    chosen=cases()
    if a.cases: chosen=[c for c in chosen if c[0] in a.cases.split(',')]
    if a.group: chosen=[c for c in chosen if c[0].startswith(a.group)]
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
    record={'schema':'e040-t122b-synthetic/1','task':'T122b','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'source_state':{'asset':case[3],'sha256':digest},'variant':a.variant,'caught':caught,'passes':results,
            'command':'python3 -B '+str(Path(__file__).relative_to(ROOT))+' '+' '.join(sys.argv[1:]),'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'runtime/original_match/port/news.py']}}
    if not a.no_record:
        a.out.mkdir(parents=True,exist_ok=True);out=a.out/('synthetic-'+(a.variant or 'normal')+'-'+stamp+'.json');assert not out.exists();out.write_text(json.dumps(record,indent=1)+'\n');print('record:',out,flush=True)
    return 0 if (caught if a.variant else not bad) else 1

if __name__=='__main__':sys.exit(main())
