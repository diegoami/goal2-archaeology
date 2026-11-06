"""T123b isolated frames, real original helpers and native-population corroboration.
Named DEA6 then exact assembly establish flow. Runs corroborate call frames,
ordered caller-visible writes, both real re-sorts, final ALLREGS/memory and RNG.
Only synthetic parent/edge edits are declared; guest bytes stay private.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'runtime'),str(HERE.parent.parent)]
from runner import expected
from original_match import port
from original_match.image import Image
from original_match.machine import Machine,REGS,MEM_SIZE
from original_match.match import Match,Fixture,TEAM_MENU
from original_match.port import selection
from original_match.port.prove import Prover

ASSET='c6b4796bbd02b1ab-e006-0000-r0007.sav'
SS=0x9000;SP=0x3000;PARENT=0x4000

def sha(data):return hashlib.sha256(data).hexdigest()
def hashes():return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [Path(__file__),ROOT/'runtime/original_match/port/selection.py']}
def leaf(variant=None):
    reg=port.Registry('selection','T123b bounded DEA6 only')
    reg._add(selection.PORTS.entries['0791:DEA6']);reg.variants=dict(selection.PORTS.variants)
    return [(reg,variant)]

def source():
    data=(ROOT/'.cache/dl'/ASSET).read_bytes();assert sha(data)==expected(ASSET)
    return Image.from_savestate(data),sha(data)

def setup_source(original):
    memory=original.memory;g=original.far(0xA923);manager=memory[g+1]
    country=memory[original.far(0xA91F)+3*(128+manager)]
    count=int.from_bytes(memory[g+0x28:g+0x2A],'little')
    for index in range(1,count+1):
        off=original.far(0xA92B)+8*(index-1);raw=memory[off:off+8]
        a,b=int.from_bytes(raw[4:6],'little'),int.from_bytes(raw[6:8],'little')
        if country in (a,b):break
    match=Match(original,Fixture(first=a,second=b,index=index,kind=raw[2]),tail=False)
    match.m.at(TEAM_MENU,lambda replay:match.m.stop('t123b-original-pre-match-menu'))
    match._advance()
    assert match.m.stop_reason=='t123b-original-pre-match-menu'
    assert match.m.rd(0xC1E,1)==1 and match.m.rd(0xC1F,1)==0
    return match.image(),{'method':'original Match F1F6/A4A1 to ED8A pre-match menu entry',
        'fixture':index,'inputs':[{'what':item['what'],'linear':item['linear'],'size':len(item['old'])//2,'before_sha256':sha(bytes.fromhex(item['old'])),'after_sha256':sha(bytes.fromhex(item['new']))} for item in match.inputs],
        'snapshot_regs':{r:match.m.reg(r) for r in REGS},'memory_sha256':sha(match.m.read(0,MEM_SIZE))}

def squad(m,country):return [m.word_at(m.far(0xA917)+191*country+2*i) for i in range(20)]
def parent(m):return {str(k):int.from_bytes(m.read(SS*16+PARENT+k,n),'little') for k,n in [(-1,1),(-3,1),(-5,2),(-7,2),(-9,2),(-11,2),(0,2),(2,2),(4,2),(6,2)]}
def seed(m):return {hex(off):m.rd(off) for off in (0x7B62,0x8336,0x9B43)}

def prepare(image,setup,case):
    m=Machine(image.memory,image.load);ds=m.DS*16;g=m.far(0xA923);manager=m.read(g+1,1)[0]
    country=m.read(m.far(0xA91F)+3*(128+manager),1)[0]
    def w(a,v,n=2):m.write(a,int(v).to_bytes(n,'little'))
    edits=[]
    def edit(a,value,n,why):
        before=m.read(a,n);w(a,value,n);edits.append({'linear':a,'size':n,'before_sha256':sha(before),'after_sha256':sha(m.read(a,n)),'why':why})
    edit(ds+0xC1F,0,1,'bounded outside-match context');edit(ds+0xC1E,setup,1,'re-sort branch')
    marked=case not in ('mark','empty');cursor=13 if case=='swap' else 3;marked_slot=13 if case=='empty-outgoing' else 3
    edit(ds+0xC1B,cursor,2,'synthetic cursor')
    # Synthetic parent chain, deliberately separate from the natural-entry continuation.
    for k,value,n in [(6,country,2),(0,0x4200,2),(2,0xE99C,2),(4,m.seg(0x0791),2),
       (-1,int(marked),1),(-3,int(country==m.rd(0x9B36)),1),(-5,1,2),(-7,1,2),(-9,marked_slot,2),(-11,0xBEEF,2)]:
        edit(SS*16+PARENT+k,value,n,'synthetic E44F parent field')
    if case in ('empty','empty-outgoing'):
        edit(m.far(0xA917)+191*country+2*(cursor-1),0,2,'synthetic empty-slot edge')
    return m,country,edits

def call(m):
    m.far_call('0791:DEA6',(PARENT,),'0791:E672',SS,SP)
    m.write(SS*16+SP,(0xE672).to_bytes(2,'little')+PARENT.to_bytes(2,'little'));m.set_reg('bp',PARENT)
    for name,value in [('ax',0xA55A),('bx',0x1234),('cx',0x5678),('dx',0xABCD),('si',0x1357),('di',0x2468),('eflags',0x202)]:m.set_reg(name,value)
    m.at('0791:E672',lambda replay:m.stop('returned'))
    m.run(m.lin('0791:E673'),fresh=True,timeout_s=60)
    assert m.reg('sp')==SP+4 and m.reg('bp')==PARENT


def run(out,variant=None):
    original,asset_sha=source();prepared,setup_context=setup_source(original)
    for setup,image in [(0,original),(1,prepared)]:
      for case in ('mark','empty','same','swap','empty-outgoing'):
        if variant and case!='swap':continue
        raw,country,edits=prepare(image,setup,case);translated,_,_=prepare(image,setup,case)
        events=[]
        for address,far,nargs in [('0791:DE27',False,1),('0791:DE51',False,3),('214B:007B',True,5),('1771:52CC',True,1),('0791:230C',False,0)]:
          def entered(replay,address=address,far=far,nargs=nargs):
            offset=4 if far else 2
            events.append({'call':address,'regs':{r:raw.reg(r) for r in REGS},'args_nearest_first':[raw.stack_word(offset+2*i) for i in range(nargs)],
              'retained_pane':raw.stack_word(4) if address=='0791:DE27' else None})
          raw.at(address,entered)
        for ret,sort in [('0791:DF33','0791:230C'),('0791:DF41','1771:52CC')]:
          def sorted_read(replay,sort=sort):
            actual=next((e['call'] for e in reversed(events) if e.get('call') in ('0791:230C','1771:52CC')),None)
            if actual==sort:events.append({'post_sort':sort,'live_squad':squad(raw,country),'regs':{r:raw.reg(r) for r in REGS}})
          raw.at(ret,sorted_read)
        before={'squad':squad(raw,country),'parent':parent(raw),'rng':seed(raw),'memory_sha256':sha(raw.read(0,MEM_SIZE))}
        inst=port.install(translated,leaf(variant));prover=Prover(translated,inst)
        started=time.monotonic();status='passed'
        try:
            call(raw);call(translated)
            assert raw.read(0,MEM_SIZE)==translated.read(0,MEM_SIZE),'complete memory difference'
            assert all(raw.reg(r)==translated.reg(r) for r in REGS),'ALLREGS difference'
            assert prover.summary()['0791:DEA6']['proved']==1
            assert not prover.summary()['0791:DEA6']['scratch']
        except Exception as exc:status=type(exc).__name__+': '+str(exc)
        result={'setup':setup,'case':case,'variant':variant,'status':status,'asset':ASSET,'asset_sha256':asset_sha,
          'input_type':'native records plus declared synthetic parent/edge edits','edits':edits,'setup_context':setup_context if setup else None,
          'source_hashes':hashes(),'before':before,'after':{'squad':squad(translated,country),'parent':parent(translated),'rng':seed(translated),
          'memory_sha256':sha(translated.read(0,MEM_SIZE)),'registers':{r:translated.reg(r) for r in REGS}},'actual_original_events':events,
          'proof':prover.summary(),'calls':inst.calls,'elapsed_s':round(time.monotonic()-started,3)}
        with out.open('a') as f:f.write(json.dumps(result,sort_keys=True)+'\n')
        print(setup,case,status,flush=True)
        if variant:assert status.startswith('ProofError:'),status
        else:assert status=='passed',status

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--variant');a=ap.parse_args()
    if a.out.exists():raise SystemExit('immutable output exists')
    run(a.out,a.variant)
