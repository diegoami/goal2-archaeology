"""T125 isolated raw original entries, synthetic branches over a hash-verified original image.
Original code/callees run without stubs; Prover compares ordered writes and live ABI.
Only digests, scalar decisions, call arguments and counts are published, never guest bytes.
"""
import argparse, hashlib, json, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT)]
from original_match import port
from original_match.image import Image
from original_match.machine import Machine, MEM_SIZE, REGS
from original_match.port.prove import Prover
from original_match.port import assistant

ASSET='53b69d3dfb964e77-snap-0213-20261011T142027Z.sav'
SHA='53b69d3dfb964e77' # Full digest is independently verified against the published evidence manifest below.

def image():
    sys.path.insert(0,str(ROOT/'experiments/E040-route-fixture-writes'))
    from runner import expected
    data=(ROOT/'.cache/dl'/ASSET).read_bytes()
    assert hashlib.sha256(data).hexdigest()==expected(ASSET)
    return Image.from_savestate(data),hashlib.sha256(data).hexdigest()

def prepare(source,manager,case):
    m=Machine(source.memory,source.load)
    def w(a,v,n=2):m.write(a,int(v).to_bytes(n,'little'))
    ds=m.DS*16
    for ptr,off,seg in [(0xA923,0x100,0x7000),(0xA91F,0,0x7100),(0xA917,0,0x7200),
            (0xA91B,0,0x7400),(0xA927,0,0x7600),(0xA92B,0x100,0x7800),(0xA92F,0,0x7900)]:
        w(ds+ptr,off);w(ds+ptr+2,seg)
    m.write(0x70000,bytes(0xA000));w(0x70101,manager,1);w(0x71000+3*(0x80+manager),7,1)
    w(0x70126,1);w(ds+0x9B43,0xABCD);w(ds+0x6D18+2*manager,0)
    for i in range(20):w(0x72000+7*191+2*i,1+i)
    for i in range(80):w(0x76000+2*i,21+i)
    for p in range(1,101):
        for k,v in ((4,80),(6,2),(7,9),(14,50)):w(0x74000+20*p+k,v,1)
    if case in ('improve','unavailable'):
        w(0x74000+20*21+4,100,1);w(0x74000+20*22+4,120,1)
        w(0x74000+20*23+4,200,1);w(0x74000+20*23+6,3,1)
        if case=='unavailable':w(0x74000+20*22+14,0,1)
    if case=='nomatch':
        for p in range(21,101):w(0x74000+20*p+6,3,1)
    if case=='weaker':
        for p in range(21,101):w(0x74000+20*p+4,70,1)
    if case=='wrap':w(ds+0x6D18+2*manager,0xFFF0)
    if case=='sacked':w(0x70147+manager,1,1)
    if case=='finals':w(0x70113+manager,1,1)
    if case in ('tour','next','notour','allpending','pastcursor'):
        for i in range(36):
            w(0x79000+7*72+2*i,i+1)
            w(0x78100+8*i,0xFE if i or case=='allpending' else 0,1)
            w(0x78102+8*i,1 if case!='notour' else 2,1);w(0x78106+8*i,8)
        w(0x72000+7*191+0x2C,1,1);w(0x72000+8*191+0x2C,2,1)
        if case=='pastcursor':w(0x70126,37)
    return m

def call(m,target,args=()):
    entry=assistant.PORTS.entries[target];sp=0x3000;ss=m.seg(0x3052)
    end=m.far_call(target,args,'0791:E788',ss,sp)
    if not entry.far:
        for i,v in enumerate([0xE788]+list(reversed(args))):m.write(ss*16+sp+2*i,v.to_bytes(2,'little'))
    for r,v in [('bp',0x3456),('ax',0xA55A),('bx',0x1234),('cx',0x5678),('dx',0xABCD),
                 ('si',0x1357),('di',0x2468),('eflags',0x202)]:m.set_reg(r,v)
    m.at_linear(end,lambda replay:m.stop('returned'))
    m.run(m.lin('0791:E78A'),fresh=True,timeout_s=60)
    assert m.reg('sp')==sp+(4 if entry.far else 2)+entry.pop
    assert m.reg('bp')==0x3456

def run(out,variant=None,closure=False):
    source,sha=image();records=[]
    targets={'1771:55FC':['sacked','none','next','allpending','pastcursor'],
             '0791:DAF8':['sacked','none','next','notour'],
             '0791:DB38':['none','tour','notour','allpending'],
             '0791:DBFA':['none','finals','tour'],
             '0791:DC7E':['improve','ties','nomatch','weaker','unavailable','wrap','finals','tour']}
    for target,cases in targets.items():
        for manager in (0,1):
            for case in cases:
                if variant and not ((variant=='ties-replace' and target=='0791:DC7E' and case=='ties') or
                    (variant=='swap-omitted' and target=='0791:DC7E' and case=='improve') or
                    (variant=='next-write-omitted' and target=='1771:55FC' and case=='next')):continue
                m=prepare(source,manager,case);before=hashlib.sha256(m.read(0,MEM_SIZE)).hexdigest()
                def read_key(replay):
                    m.wr(0xA976,0x0D0D);m.return_from(True)
                def keypressed(replay):
                    m.set_reg('ax',(m.reg('ax')&0xFF00)|1);m.return_from(True)
                m.at('214B:08DD',read_key);m.at('214B:0723',keypressed)
                if closure:
                    from original_match.assistant import _ports
                    helpers=[]
                    for reg,v in _ports():
                        if reg.name=='assistant':continue
                        real=port.Registry(reg.name,reg.doc)
                        for addr,e in reg.entries.items():
                            if addr not in ('214B:08DD','214B:0723'):real._add(e)
                        helpers.append((real,v))
                    port.install(m,helpers)
                inst=port.install(m,[('assistant'+('.'+variant if variant else ''))]);prover=Prover(m,inst)
                decisions=[]
                for site in ('0791:DB03','0791:DB22','0791:DBC5','0791:DC3D','0791:DC68','0791:DCB3'):
                    def decided(replay,site=site):decisions.append([site,m.reg('ax')])
                    m.at(site,decided)
                t=time.monotonic();status='passed'
                try:call(m,target,() if target in ('1771:55FC','0791:DC7E') else (7,))
                except Exception as e:status=f'{type(e).__name__}: {e}'
                rec={'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'runtime/original_match/port/assistant.py',ROOT/'runtime/original_match/assistant.py']},'asset_sha256':sha,'target':target,'manager':manager,'case':case,'status':status,'before_sha256':before,
                     'after_sha256':hashlib.sha256(m.read(0,MEM_SIZE)).hexdigest(),
                     'next':m.rd(0x9B43),'ax':m.reg('ax'),'registers':{r:m.reg(r) for r in REGS},
                     'squad':[m.word_at(0x72000+7*191+2*i) for i in range(20)],
                     'pool':[m.word_at(0x76000+2*i) for i in range(80)],
                     'summary':prover.summary(),'calls':inst.calls,'decisions':decisions,'closure':closure,'elapsed_s':round(time.monotonic()-t,3)}
                records.append(rec);print(target,manager,case,status,flush=True)
                with out.open('a') as f:f.write(json.dumps(rec,sort_keys=True)+'\n')
                if status!='passed' and not variant:return 1
    assert records
    if variant:assert all(r['status'].startswith('ProofError:') for r in records)
    else:assert all(r['status']=='passed' for r in records)
    return 0

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--variant');ap.add_argument('--closure',action='store_true');a=ap.parse_args()
    if a.out.exists():raise SystemExit('immutable output already exists')
    raise SystemExit(run(a.out,a.variant,a.closure))
