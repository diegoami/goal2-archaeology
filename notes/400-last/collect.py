#!/usr/bin/env python3
"""Bounded native original-key collection from an existing hash-verified .GL.

No guest-memory/register edits; normal replay requires verified identical mounts. Every observation is
kept privately and every key/CPU/caller observation is recorded append-only.
"""
import hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'runtime/driver'),str(ROOT/'runtime')]
import driver
from original_match.image import Image
from emul.watched_match import cpu_state
def sha(b):return hashlib.sha256(b).hexdigest()

def inspect(raw):
    im=Image.from_savestate(raw);r=cpu_state(raw);m=im.memory;ss=r['SS']*16;ds=im.DS*16;sp=r['ESP']&65535
    w=lambda a:int.from_bytes(m[a:a+2],'little');sw=lambda o:w(ss+o)
    reads=[b for b in range(sp,65530) if sw(b+2)==0xCF3A and sw(b+4)==im.load+0x0791 and b<sw(b)<65530]
    bp=reads[0] if r['CS']==0xF000 and len(reads)==1 else r['EBP']&65535
    chain=[];seen=set();taker=None
    while sp<=bp<65530 and bp not in seen:
        seen.add(bp);chain.append(dict(bp=bp,parent=sw(bp),return_offset=sw(bp+2)))
        if sw(bp+2)==0x6D74 and m[ss+bp+4] in (2,3,4,5) and m[ss+bp+6] in (0,1):
            role,side=m[ss+bp+4],m[ss+bp+6]
            taker=dict(bp=bp,role=role,side=side,highlight=sw(bp-5),selection=sw(bp-7),stored=w(ds+0x9976+10*side+2*role),country=w(ds+0x9B34+2*side),minute=w(ds+0x831F),rng=w(ds+0x7B62),read_CF3A=bool(reads));break
        bp=sw(bp)
    warnings=[dict(bp=b,parent=sw(b),caller=f'0791:{sw(b+2):04X}') for b in range(sp,65530) if sw(b+2) in (0xE062,0xEC60) and sw(b+4)==im.load+0x0791]
    return dict(regs=r,load=im.load,chain=chain,taker=taker,warnings=warnings,build_problems=im.build_problems())

def main():
    attempt,filename=sys.argv[1:3];resume=Path(sys.argv[3]).resolve() if len(sys.argv)>3 else None
    pub=ROOT/'notes/400-last'/attempt;pub.mkdir(exist_ok=False)
    private=ROOT/'.cache/400-last'/attempt;private.mkdir(parents=True,exist_ok=False)
    source=ROOT/'.cache'/filename
    a=next(a for a in json.loads((ROOT/'notes/390/inventory.json').read_text())['assets'] if a['file']==filename)
    assert sha(source.read_bytes())==a['sha256']
    rec=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),source=filename,source_sha256=a['sha256'],bound_s=240,fixture_bound=1,status='aborted',method='Original DOS loader, normal original keys, native observations; no restore or guest edits')
    targets=(3,4);rec['target_roles']=targets
    game=private/'game';work=private/'driver';start_state=None
    if resume:
        rec['method']='Normal replay of a genuine native input on verified identical C/D mounts; original keys; no guest edits or CPU entry manipulation'
        previous=resume.parent;old=json.loads((ROOT/'notes/400-last'/previous.name/'record.json').read_text());assert old['status']=='target captured'
        game=previous/'game';work=previous/'driver';conf=(work/'dosbox.conf').read_bytes()
        mounts=[l for l in conf.decode().splitlines() if l.startswith('mount ')]
        assert mounts==[f'mount c {game}',f'mount d {work/driver.CLOCK_DIR}']
        (pub/'preceding-dosbox.conf').write_bytes(conf)
        rec['resume']=dict(file=str(resume.relative_to(ROOT)),sha256=sha(resume.read_bytes()),verified_mounts=mounts,config_sha256=sha(conf))
    (pub/'collector.py').write_bytes(Path(__file__).read_bytes());(pub/'source.json').write_text(json.dumps(rec,indent=2)+'\n')
    class Loaded(driver.Driver):
        def _start_xvfb(self):shutil.copy2(source,self.game_dir/source.name);super()._start_xvfb()
    d=Loaded(config=dict(cycles='fixed 8000',dos_date='10/24/2026',dos_time='12:00:00'),workdir=work,game_dir=game,mapper='nohost')
    if resume:start_state=SimpleNamespace(name=resume.stem,path=resume,game_dir=str(game),drive_layout=d.drive_layout(),screen_digest=driver.savestate.Savestate(resume.read_bytes()).screen().digest())
    start=time.monotonic();n=0;last=None;speed=bool(resume);own=bool(resume)
    def observe(request):
        nonlocal n,last
        times,state,raw=d.read();n+=1;p=private/f'{n:04}.sav';p.write_bytes(raw)
        row=dict(n=n,request=request,times=times,file=str(p.relative_to(ROOT)),sha256=sha(raw),preceding=last,screen=state.screen().text(),**inspect(raw))
        with (pub/'steps.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')
        last=row['sha256'];return row
    def key(*keys):d.keys(*keys);return observe(dict(keys=keys))
    try:
        d.launch(start_state);row=observe('same-mount genuine resume' if resume else 'launch')
        if not resume:
            for _ in range(4):
                row=key('y')
                if 'Please enter name' in row['screen']:break
            assert 'Please enter name' in row['screen']
            key(*(['BackSpace']*80));key(*list(source.stem.lower()));row=key('Return')
        if filename=='G3C.GL' and not resume:
            # [designed: T90] Normal manager choices: replace the injured right midfielder
            # and the exhausted CF with healthy reserves. Original DEA6 keys do every write.
            # IDs/initial fields are read from unchanged G3C, not assigned to guest memory.
            row=key('space');rec['selection_changes']=[]
            def squad_view():
                im=Image.from_savestate((ROOT/row['file']).read_bytes());mem=im.memory;ds=im.DS*16
                w=lambda a:int.from_bytes(mem[a:a+2],'little');far=lambda o:w(ds+o)+16*w(ds+o+2)
                base=far(0xA917)+20*191;assert mem[base+0x2E]==129
                return [w(base+2*i) for i in range(20)],w(ds+0x0C1B)
            for outgoing,incoming in ((395,2612),(2748,2614)):
                squad,_=squad_view();a=squad.index(outgoing)+1;b=squad.index(incoming)+1
                assert a<=11 and b>11
                before=row['sha256'];row=key('Home')
                for _ in range(a-1):row=key('Down')
                assert squad_view()[1]==a
                row=key('Return');row=key('Home')
                for _ in range(b-1):row=key('Down')
                assert squad_view()[1]==b
                row=key('Return');squad,_=squad_view()
                assert incoming in squad[:11] and outgoing in squad[11:]
                rec['selection_changes'].append(dict(outgoing=outgoing,incoming=incoming,before_sha256=before,after_sha256=row['sha256']))
            row=key('Escape')
        while time.monotonic()-start<240:
            text=row['screen'];t=row['taker']
            if row['warnings']:
                rec['status']='warning candidate captured';rec['candidate']=row['n'];break
            if t:
                if t['role'] in targets:
                    before=row;board=key('space');back=key('Return')
                    assert board['taker'] and board['taker']['role']==t['role'] and board['taker']['read_CF3A']
                    assert back['taker'] and back['taker']['role']==t['role']
                    rec['status']='target captured';rec['target']=dict(role=t['role'],before=before['n'],pitch=board['n'],back=back['n']);break
                row=key('Return')
            elif 'play next game' in text and not own:
                row=key('End');row=key('Return')
            elif 'Do you want to watch this match' in text:
                row=key('y' if 'HOLLAND' in text or 'Holland' in text else 'n')
            elif 'team tactics' in text:
                assert 'Holland' in text or 'HOLLAND' in text
                own=True
                if 'turn automatic action replay OFF' in text:row=key('Insert')
                row=key('End');row=key('Return')
            elif 'CAPTAIN' in text and 'C-computer select' in text:row=key('Return')
            elif 'FULL TIME' in text and own:rec['status']='full time without target';break
            elif 'hit any key' in text or 'press any key' in text or 'PRESS ANY KEY' in text:row=key('Return')
            elif 'R-result' in text and not speed:
                row=key(*(['Right']*6));speed=True
            else:row=observe('bounded original play poll')
        else:rec['status']='240-second bound reached'
    except BaseException as e:rec['error']=repr(e);print(repr(e),flush=True)
    finally:
        rec.update(elapsed_s=time.monotonic()-start,observations=n,events=d.events,runtime=dict(executable=driver.dosbox_x(),config=d.config,clock=d.clock_readback()))
        (pub/'record.json').write_text(json.dumps(rec,indent=2)+'\n');d.terminate();print(rec['status'],n,flush=True)
if __name__=='__main__':main()
