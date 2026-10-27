"""Declared synthetic direct-call states over the hash-verified E006 image; no execution."""
import hashlib,json,subprocess,sys
from pathlib import Path
from check import ROOT,sha,write_new
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image
from original_match.assets import reference_image,REFERENCE
from original_match.machine import MEM_SIZE

ACCEPTED='55d7a479a7288ea044ceaa315eaff87e2077fdb6'
MEMORY_SHA='87400f6a866e0798f61a9f3ab3bfcaa322469fa6b238b0061f1b7ab2b6a3f979'
SS_DELTA=0xAD1  # existing original-call harness T61/diffcheck.py; stack below its0x4000 top
ENTRY_SP=0x3F00
CALLER_BP=0x3F80
RETURN='0791:0000'  # unexecuted sentinel,as T61 direct-call comparisons


def image():
    raw=reference_image(ROOT/'.cache/dl');assert sha(raw)==REFERENCE['sha256']
    value=Image.from_bytes(raw);assert value.sha256()==MEMORY_SHA
    assert not value.build_problems()
    return value


def source_hashes(extra=()):
    names=['notes/engine-study/T106/construction.py','notes/engine-study/T106/runner.py','notes/engine-study/T106/check.py',*extra]
    names += [str(p.relative_to(ROOT)) for p in (ROOT/'runtime/original_match').rglob('*.py')]
    names += ['static/goal-exe/code/seg_0791_06.asm','static/goal-exe/code/seg_0791_12.asm','notes/engine-study/T105/T105a-v2.json','notes/engine-study/T105/T105b-v2.json']
    result={p:sha((ROOT/p).read_bytes()) for p in sorted(set(names))}
    for p in ['runtime/original_match/port/ball.py','runtime/original_match/port/restarts.py','runtime/original_match/port/geometry.py','runtime/original_match/machine.py','runtime/original_match/port/mem.py','runtime/original_match/port/guest.py']:
        assert (ROOT/p).read_bytes()==subprocess.check_output(['git','show',ACCEPTED+':'+p],cwd=ROOT),p
    return result


def construct(img,spec):
    memory=bytearray(bytes(img.memory[:MEM_SIZE]).ljust(MEM_SIZE,b'\0'));ds=img.DS*16;patches=[]
    def put(linear,data,why):
        data=bytes(data)
        assert linear>=ds,'never patch original code'
        assert 0<=linear and linear+len(data)<=MEM_SIZE
        patches.append(dict(linear=linear,after_hex=data.hex(),before_sha256=sha(memory[linear:linear+len(data)]),meaning=why))
        memory[linear:linear+len(data)]=data
    def b(off,value,why):put(ds+off,bytes([value&255]),why)
    def w(off,value,why):put(ds+off,(value&65535).to_bytes(2,'little'),why)
    def far(off):return int.from_bytes(memory[ds+off:ds+off+2],'little')+16*int.from_bytes(memory[ds+off+2:ds+off+4],'little')
    countries,players=far(0xA917),far(0xA91B)
    assert memory[ds+0x668:ds+0x66a]==b'\x0b\x00'
    assert memory[ds+0x7920:ds+0x7922]==b'\xff\x01'
    w(0x9B34,7,'fixture side0 country');w(0x9B36,19,'fixture side1 country')
    bindings=[]
    for slot in range(1,23):
        country,relative=(19,slot) if slot<12 else (7,slot-11)
        ident=int.from_bytes(memory[countries+0xbf*country+2*(relative-1):countries+0xbf*country+2*relative],'little')
        assert 1<=ident<3061
        role=memory[players+20*ident+6];assert role<14
        rec=bytearray(22);rec[4:6]=b'\x20\x07';rec[6]=slot
        rec[9:11]=memory[ds+0x79e+2*role:ds+0x7a0+2*role]
        rec[13:15]=ident.to_bytes(2,'little');rec[15]=5;rec[17]=32;rec[18]=spec.get('state',5)
        put(ds+0x80e8+22*slot,rec,'synthetic live record:point/old/destination0,glyph0720,slot/identity,tablepost,cache32,state,timer/activity0')
        put(players+20*ident+14,b'\x20','synthetic positive energy32 for direct-call bindings')
        put(players+20*ident+16,b'\0','synthetic available status0')
        bindings.append(dict(slot=slot,side=1 if slot<12 else 0,country=country,relative_slot=relative,player=ident,played_role=role))
    assert len({r['player'] for r in bindings})==22,'unique source XI identities required'
    w(0x82f6,0,'ball point0,0');w(0x82fc,0,'initial vx0');w(0x82fe,0,'initial vy0');w(0x8300,0,'initial timer0')
    holder=spec.get('holder',2)
    for off,val,meaning in [(0x8302,0,'initial playflag'),(0x8303,0,'initial flight'),(0x830b,holder,'holder slot'),(0x830c,holder,'same receiver bypasses launch miscue'),(0x830d,0,'challenger'),(0x830e,0,'pending offside'),(0x8323,0,'phase'),(0x8324,0,'kick mode'),(0x8325,0,'stopped activity makes333F take its early enable-and-return'),(0x8326,0,'normal end mode'),(0x8327,0,'initial event'),(0x80fa,0,'ordinary launch selector')]:b(off,val,meaning)
    w(0x8313,0,'initial projected point');b(0x8319,45,'direction threshold45');w(0x831b,45,'remaining45:threshold equality selects direction flag0');w(0x831d,1,'subtick1');w(0x831f,45,'synthetic elapsed45')
    b(0xa9fc,1,'mute speaker hardware;original1EA1 body still executes');put(ds+0xa9ff,(20).to_bytes(4,'little'),'bounded delay calibration20,as existing kit')
    target_slot=spec.get('slot',holder)
    if spec.get('energy') is not None:
        ident=bindings[holder-1]['player'];put(players+20*ident+14,bytes([spec['energy']]),'declared no-effect energy intervention')
    if spec['kind']=='wall':
        w(0x8315,pack(spec['spot']),'declared free-kick restart spot')
    record_off=0x80e8+22*target_slot
    args=[record_off,img.DS,6,pack(spec['target'])] if spec['kind']=='launch' else [record_off,img.DS]
    ss=img.DS+SS_DELTA;end_seg=img.load+0x0791;layout=[0,end_seg]+args
    put(ss*16+ENTRY_SP,b''.join(x.to_bytes(2,'little') for x in layout),'synthetic far return and nearest-first arguments;retf8/4')
    regs=dict(ax=0x1234,bx=0x2345,cx=0x3456,dx=0x4567,si=0x5678,di=0x6789,bp=CALLER_BP,sp=ENTRY_SP,ss=ss,ds=img.DS,es=img.DS,cs=end_seg,eip=int(spec['routine'].split(':')[1],16),eflags=0x202)
    return memory,dict(patches=patches,bindings=bindings,args_nearest_first=args,registers=regs,return_address=RETURN,return_linear=end_seg*16,expected_return_sp=ENTRY_SP+4+(8 if spec['kind']=='launch' else 4),memory_sha256=sha(memory),memory_size=MEM_SIZE,reachability='deliberately synthetic typed bindings/geometry;no claim of natural full-match reach')


def pack(point):return (point[0]&255)|((point[1]&255)<<8)


def make_manifest(group,specs,extra_sources):
    img=image();sources=source_hashes(extra_sources);items=[]
    for spec in specs:
        _,state=construct(img,spec);items.append(dict(spec=spec,input=state))
    return dict(schema=1,group=group,construction_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),reference=REFERENCE,memory_component_sha256=img.sha256(),load=img.load,ds=img.DS,source_sha256=sources,invocations=items,limits='No instruction/code edits,engine setup or Match. Every variable edit is listed;numeric predictions are independently frozen in T105a-v2.')
