#!/usr/bin/env python3
"""Bounded original-key replay of the existing T114 sent-off-player input.

Uses only unchanged Core.load/press/save and read-only observations. No collector
write to guest memory/registers; the normal core keyboard service answers original reads.
"""
import hashlib,json,signal,subprocess,sys,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PIN='5061474420b842ee98a4a1e4c9c2673c0764b1f2'
SOURCE='fc5b0f392a66334c3395605d0113d56f67788c7b4a7b4b176364fb028ce119e2'
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    pub=ROOT/'notes/400-remaining/core-r1';pub.mkdir(exist_ok=False)
    private=ROOT/'.cache/400-nice-try/core-r1';private.mkdir(exist_ok=False)
    source=ROOT/'.cache/400-nice-try/source.g2core';code=ROOT/'.cache/400-nice-try/core-source'
    files={str(p.relative_to(code)):sha(p.read_bytes()) for p in sorted((code/'goal2/core').rglob('*.py'))}
    rec=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),core_source_commit=PIN,core_files=files,source_sha256=sha(source.read_bytes()),bound_s=120,status='aborted',method='Unchanged Core.load then original key codes through Core.press; no collector guest writes or register edits',keys=[])
    (pub/'collector.py').write_bytes(Path(__file__).read_bytes());(pub/'source.json').write_text(json.dumps(rec,indent=2)+'\n')
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('120-second bound')));signal.alarm(120)
    start=time.monotonic();n=0;c=None
    def observe(request):
        nonlocal n
        n+=1;m=c.m;snap=m.snapshot();f=c._frame();bp=f.bp;frames=[]
        for _ in range(12):
            frames.append(dict(bp=bp,parent=f.up(bp),near=f.near_caller(bp),far=f.far_caller(bp)))
            nxt=f.up(bp)
            if nxt<=bp or nxt>65520:break
            bp=nxt
        state=private/f'{n:03}.ucstate'
        # A raw, actual stopped machine. It is not relabelled as a DOSBox or Core save.
        with zipfile.ZipFile(state,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('memory.bin',snap['memory']);z.writestr('registers.json',json.dumps(dict(load=snap['load'],regs=snap['regs'])))
        cp=None
        if c.wait is not None:
            p=private/f'{n:03}.g2core';p.write_bytes(c.save());cp=dict(file=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()))
        row=dict(n=n,request=request,kind=c.wait.kind if c.wait else None,view=c.wait.view if c.wait else None,site=c.wait.site if c.wait else m.where(m.stack_word(2),m.stack_word(0)),text=c._text(),regs=snap['regs'],load=snap['load'],frames=frames,cursor=m.rd(0x0C1B),core=cp,machine=dict(file=str(state.relative_to(ROOT)),sha256=sha(state.read_bytes())))
        with (pub/'steps.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')
        print(json.dumps({k:row[k] for k in ('n','request','kind','site','cursor','frames')}),flush=True)
        return row
    def key(k):
        rec['keys'].append(k)
        try:c.press(k)
        except Exception:
            observe(dict(key=k,error=True));raise
        return observe(dict(key=k))
    try:
        assert rec['source_sha256']==SOURCE
        sys.dont_write_bytecode=True;sys.path.insert(0,str(code))
        from goal2.core import Core,views
        c=Core.load(source.read_bytes());row=observe('load genuine T114 input')
        team=views.team(c.wait.state);squad=[r['player'] for r in team['squad']];rec['country']=team['country'];rec['squad']=squad
        m=c.m;players=m.far(0xA91B)
        status=lambda p:m.read(players+20*p+0x10,1)[0]
        energy=lambda p:m.read(players+20*p+0x0E,1)[0]
        assert squad[10]==125 and status(125)&0x20
        incoming=next(i for i,p in enumerate(squad,1) if i>11 and p and status(p)==0 and energy(p)>0)
        rec.update(outgoing=125,outgoing_slot=11,outgoing_status=status(125),incoming=squad[incoming-1],incoming_slot=incoming,incoming_status=status(squad[incoming-1]),incoming_energy=energy(squad[incoming-1]))
        assert c.wait.kind.startswith('match-menu')
        key(32)
        assert 'squad-substitution' in c.wait.kind
        # Normal cursor keys only, keep every intermediate state.
        key(0xAB)
        for _ in range(10):key(0xB1)
        assert m.rd(0x0C1B)==11
        key(13)
        for _ in range(incoming-11):key(0xB1)
        assert m.rd(0x0C1B)==incoming
        rec['pre_second_enter']=observe('preceding genuine input immediately before second Enter')['core']
        row=key(13)
        assert any(fr['far']=='0791:E19F' for fr in row['frames'])
        assert 'Nice try' in row['text']
        rec['status']='E19F captured';rec['message']=row
    except BaseException as e:
        rec['error']=repr(e);print(repr(e),flush=True)
    finally:
        signal.alarm(0);rec.update(elapsed_s=time.monotonic()-start,observations=n)
        (pub/'record.json').write_text(json.dumps(rec,indent=2)+'\n')

if __name__=='__main__':main()
