#!/usr/bin/env python3
"""Bounded native original-key collection; JSON line commands over stdin."""
import hashlib, json, select, shutil, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'runtime/driver'),str(ROOT/'runtime')]
import driver
from original_match.image import Image
from emul.watched_match import cpu_state

def sha(b): return hashlib.sha256(b).hexdigest()

def inspect(raw):
    im=Image.from_savestate(raw); r=cpu_state(raw)
    ss=r['SS']*16; sp=r['ESP']&65535; mem=im.memory
    def w(o):return int.from_bytes(mem[ss+o:ss+o+2],'little')
    frames=[]
    for off in range(sp,65530,2):
        ret=w(off+2); seg=w(off+4)-im.load
        if (seg,ret) in {(0x0791,v) for v in (0xCC54,0xCEDE,0xCEED,0xCF3A,0xE062,0xE19F,0xEC60,0xEE9F)} | {(0x214B,0x098A),(0x214B,0x054E),(0x000E,0x75D1)}:
            frames.append(dict(bp=off,parent=w(off),ret=f'{seg:04X}:{ret:04X}'))
    # Near call 6D71 -> CC7B; BP chain establishes whether this is live.
    takers=[]
    for off in range(sp,65526,2):
        if w(off+2)==0x6D74 and w(off+4) in range(1,6) and w(off+6) in (0,1):
            role,side=w(off+4),w(off+6)
            ds=im.DS*16
            takers.append(dict(bp=off,parent=w(off),role=role,side=side,highlight=w(off-5),selection=w(off-7),stored=int.from_bytes(mem[ds+0x9976+10*side+2*role:ds+0x9978+10*side+2*role],'little')))
    return dict(regs=r,load=im.load,frames=frames,takers=takers,build_problems=im.build_problems())

def main():
    attempt=sys.argv[1]; pub=ROOT/'notes/400-remaining'/attempt; pub.mkdir(exist_ok=False)
    private=ROOT/'.cache/400-remaining'/attempt;private.mkdir(exist_ok=False)
    source=ROOT/'.cache/G4C.GL'
    assert sha(source.read_bytes())=='06af479da77db6e1da7847de929bf43531349f2fcddcaeac3ba93e8b16da304d'
    rec=dict(attempt=attempt,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),source_sha256=sha(source.read_bytes()),runtime='DOSBox-X 2024.03.01; fixed 8000; original raw XTEST keys; nohost mapper; explicit DOS date/time',bound_s=900,status='running')
    (pub/'collector.py').write_bytes(Path(__file__).read_bytes())
    (pub/'source.json').write_text(json.dumps(rec,indent=2)+'\n')
    class Loaded(driver.Driver):
        def _start_xvfb(self):
            shutil.copy2(source,self.game_dir/'G4C.GL');super()._start_xvfb()
    d=Loaded(config=dict(cycles='fixed 8000',dos_date='10/24/2026',dos_time='12:00:00'),workdir=private/'driver',game_dir=private/'game',mapper='nohost')
    n=0; started=time.monotonic(); last=None
    def observe(req):
        nonlocal n,last
        times,state,raw=d.read();n+=1
        fn=private/f'{n:05}.sav';fn.write_bytes(raw)
        info=inspect(raw); text=state.screen().text()
        row=dict(n=n,request=req,times=times,file=str(fn.relative_to(ROOT)),sha256=sha(raw),preceding=last,screen=text,digest=state.screen().digest(),**info)
        with (pub/'steps.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')
        last=row['sha256']
        return row
    def send(keys):
        d.keys(*keys);return observe(dict(keys=keys))
    try:
        d.launch(); row=observe('launch')
        for _ in range(4):
            row=send(['y'])
            if 'Please enter name' in row['screen']:break
        if 'Please enter name' not in row['screen']:raise RuntimeError('filename editor absent')
        send(['BackSpace']*80);send(['g','4','c']);row=send(['Return'])
        for _ in range(10):
            if any(f['ret']=='000E:75D1' for f in row['frames']):break
            row=observe('await manager')
        print(json.dumps(row),flush=True)
        while time.monotonic()-started<900:
            if not select.select([sys.stdin],[],[],min(30,900-(time.monotonic()-started)))[0]:continue
            line=sys.stdin.readline()
            if not line:break
            req=json.loads(line)
            if req.get('stop'):rec['status']='stopped';break
            if 'watch' in req:
                end=min(time.monotonic()+min(req['watch'],55),started+900)
                while time.monotonic()<end:
                    row=observe('bounded watch poll')
                    live=[t for t in row['takers'] if any(f['ret'] in ('0791:CC54','0791:CEDE','0791:CEED') for f in row['frames'])]
                    if live:
                        if live[0]['role']!=1:
                            row=send(['space']);row=send(['Return'])
                        row=send(['Return'])
                    elif any(s in row['screen'] for s in ('hit any key','press any key','PRESS ANY KEY')) or 'team tactics' in row['screen']:
                        break
                print(json.dumps(row),flush=True)
            else:
                row=send(req['keys']) if 'keys' in req else observe(req)
                print(json.dumps(row),flush=True)
        if rec['status']=='running':rec['status']='bound-or-eof'
    except BaseException as e:
        rec['status']='aborted';rec['error']=repr(e);raise
    finally:
        rec.update(elapsed_s=time.monotonic()-started,observations=n,driver_events=d.events,config=d.config,clock_readback=d.clock_readback())
        (pub/'record.json').write_text(json.dumps(rec,indent=2)+'\n');d.terminate()

if __name__=='__main__':main()
