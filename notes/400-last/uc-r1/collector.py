#!/usr/bin/env python3
"""Research-only exact-CPU replay with existing Core keyboard services.

No Core.start/boot, guest state edits, seed changes, engine ports or entry moves.
Native VRAM is loaded from its own saved Vga component into mapped video RAM.
Only host naming of already-evidenced roles2/5 is adapted; roles3/4 stop naturally.
"""
import hashlib,json,signal,subprocess,sys,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CODE=ROOT/'.cache/400-nice-try/core-source'
SOURCE=ROOT/'.cache/400-last/G1A-r1/0034.sav'
SOURCE_SHA='6731809257089157904884a54148f6f71b87a3073aaa9d433479744ba8844915'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    pub=ROOT/'notes/400-last/uc-r1';pub.mkdir(exist_ok=False)
    private=ROOT/'.cache/400-last/uc-r1';private.mkdir(exist_ok=False)
    rec=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),source=str(SOURCE.relative_to(ROOT)),source_sha256=sha(SOURCE.read_bytes()),core_source_commit='5061474420b842ee98a4a1e4c9c2673c0764b1f2',bound_s=120,fixture_bound=1,status='aborted',keys=[],host_alias_roles=[2,5],method='Exact saved CPU and original memory+VRAM import; original game code; unchanged Core keyboard services; host label aliases only for already-delivered roles2/5')
    rec['runtime_files']={str(p.relative_to(CODE)):sha(p.read_bytes()) for folder in ('goal2/core','goal2/engine/original_match') for p in sorted((CODE/folder).rglob('*.py'))}
    (pub/'collector.py').write_bytes(Path(__file__).read_bytes());(pub/'source.json').write_text(json.dumps(rec,indent=2)+'\n')
    start=time.monotonic();n=0;c=None
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('120-second bound')));signal.alarm(120)
    try:
        assert rec['source_sha256']==SOURCE_SHA
        sys.dont_write_bytecode=True;sys.path.insert(0,str(CODE))
        from goal2.core.runner import Core,cpu_state,text_page,UnknownScreen
        from goal2.core import screens as S
        from goal2.engine.original_match.image import Image
        from goal2.engine.original_match.machine import Machine,MEM_SIZE
        raw=SOURCE.read_bytes();im=Image.from_savestate(raw);assert not im.build_problems();regs=cpu_state(raw)
        original=bytes(im.memory[:MEM_SIZE]);memory=bytearray(original);vram=text_page(raw)
        memory[0xB8000:0xB8000+4000]=vram
        assert memory[:0xB8000]==original[:0xB8000] and memory[0xB8000+4000:]==original[0xB8000+4000:]
        m=Machine(memory,im.load);m.restore(dict(memory=bytes(memory),regs=regs))
        snap=m.snapshot();assert snap['memory']==bytes(memory) and snap['regs']==regs
        rec['initial_import']=dict(cpu_unchanged=True,game_memory_unchanged=True,video_projection=dict(address=0xB8000,bytes=4000,source='exact original Vga text-page bytes',sha256=sha(vram)))
        original_caption=S._captain
        S.KINDS['evidence-taker']=S.Kind('evidence-taker',S.keys(('original keys','Return Escape space c Up Down')),polled=True,evidence='Research I/O label adapter only; F030/T88/T89 roles2/5')
        def caption(f,bp):
            role=f.byte(bp,4)
            return 'evidence-taker' if role in (2,5) else original_caption(f,bp)
        S._captain=caption
        c=Core(m,im.header,bytes(im.memory[MEM_SIZE:]),10_000_000_000,[],SOURCE_SHA,dos_time=(12,0,0,0))
        c.stop_at('captain-select','evidence-taker','substitution-notice','match-live')
        def observe(label):
            nonlocal n
            n+=1;snap=m.snapshot();f=c._frame();bp=f.bp;frames=[]
            for _ in range(12):
                frames.append(dict(bp=bp,parent=f.up(bp),near=f.near_caller(bp),far=f.far_caller(bp)))
                nxt=f.up(bp)
                if nxt<=bp or nxt>65520:break
                bp=nxt
            path=private/f'{n:04}.ucstate'
            with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
                z.writestr('memory.bin',snap['memory']);z.writestr('registers.json',json.dumps(dict(load=snap['load'],regs=snap['regs'],memory_header=im.header.hex())))
            item=None
            if c.wait is not None:
                p=private/f'{n:04}.g2core';p.write_bytes(c.save());item=dict(file=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()),host_alias_required=c.wait.kind=='evidence-taker')
            row=dict(n=n,label=label,kind=c.wait.kind if c.wait else None,site=c.wait.site if c.wait else m.where(m.stack_word(2),m.stack_word(0)),text=c._text(),regs=snap['regs'],load=snap['load'],frames=frames,minute=m.rd(0x831F),core=item,machine=dict(file=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes())))
            with (pub/'steps.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')
            print(json.dumps({k:row[k] for k in ('n','label','kind','site','minute')}),flush=True);return row
        def key(k):
            k=ord(k) if isinstance(k,str) else k;observe(dict(before_key=k));rec['keys'].append(k)
            try:c.press(k)
            except Exception:
                observe(dict(after_key=k,error=True));raise
            return observe(dict(after_key=k))
        with c.live_frames():
            try:c._run()
            except Exception:
                observe('initial exact-CPU forward replay stopped');raise
            observe('first natural poll after exact saved CPU')
            assert c.wait.kind=='captain-select';key(13)
            assert c.wait.kind=='match-live';key(13)  # ordinary pause/menu
            assert c.wait.kind.startswith('match-menu');key(32)
            assert c.wait.kind.startswith(('squad','substitution'))
            def player_state():
                p=m.far(0xA91B)+20*390
                return m.rd(0x0C1B),m.read(p+6,1)[0],m.read(p+15,1)[0]
            key(0xAB)
            for _ in range(9):key(0xB1)
            assert player_state()[0]==10
            for _ in range(9):key('r')
            assert player_state()[1]==8
            key('t');assert c.wait.kind=='own-tactics';key(0xAB)
            for _ in range(3):
                if player_state()[2]&0x11==0x11:break
                key(13)
            assert player_state()[2]&0x11==0x11
            key(0xB1)
            for _ in range(3):
                if player_state()[2]&0x22==0x20:break
                key(13)
            assert player_state()[2]&0x22==0x20
            key(27);key(27);assert c.wait.kind.startswith('match-menu');key(0xB0);key(13)
            for _ in range(6):
                if c.wait.kind!='match-live':break
                key(0xAF)
            last_minute=None;frames=0
            while time.monotonic()-start<120:
                if 'FULL TIME' in c.wait.text:observe('full time');rec['status']='full time without target';break
                if c.wait.kind=='match-live':
                    minute=m.rd(0x831F)
                    if minute!=last_minute and minute%10==0:observe('ten-minute checkpoint');last_minute=minute
                    c.advance();frames+=1
                elif c.wait.kind.startswith('match-menu'):key(0xB0);key(13)
                elif c.wait.kind in ('captain-select','evidence-taker','substitution-notice'):key(13)
                elif c.wait.kind in ('action-replay-prompt','match-summary-save-prompt'):key('n')
                else:key(13)
            else:rec['status']='120-second bound reached'
            rec['live_frames']=frames
    except BaseException as e:
        rec['error']=repr(e)
        if c is not None:
            try:rec['last_observation']=observe('final stopped machine')
            except Exception as capture_error:rec['capture_error']=repr(capture_error)
        print(repr(e),flush=True)
    finally:
        signal.alarm(0);rec.update(elapsed_s=time.monotonic()-start,observations=n)
        (pub/'record.json').write_text(json.dumps(rec,indent=2)+'\n')
if __name__=='__main__':main()
