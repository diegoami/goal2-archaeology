#!/usr/bin/env python3
"""[designed: T86] Bounded original-loader collection. No guest-memory writes or CPU restoration."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'runtime/driver'))
import driver
sys.path.insert(0,str(ROOT/'runtime'))
from original_match.image import Image
from emul.watched_match import cpu_state

SOURCE_SHA='06af479da77db6e1da7847de929bf43531349f2fcddcaeac3ba93e8b16da304d'


def manager_frame(raw):
    image=Image.from_savestate(raw);regs=cpu_state(raw)
    ss,sp=regs['SS'],regs['ESP']&0xffff
    pair=(0x75D1).to_bytes(2,'little')+((image.load+0x000E)&0xffff).to_bytes(2,'little')
    hits=[o-2 for o in range(sp,0xfffc,2) if image.memory[ss*16+o:ss*16+o+4]==pair]
    return image,regs,hits


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--attempt',required=True);a=ap.parse_args()
    public=ROOT/'notes/400'/a.attempt;public.mkdir(parents=True,exist_ok=False)
    private=ROOT/'.cache/400'/a.attempt;private.mkdir(parents=True,exist_ok=False)
    source=ROOT/'.cache/G4C.GL';assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
    class Loaded(driver.Driver):
        def _start_xvfb(self):
            shutil.copy2(source,self.game_dir/'G4C.GL')
            super()._start_xvfb()
    d=Loaded(config=dict(cycles='fixed 8000',dos_date='10/24/2026',dos_time='12:00:00'),
             workdir=private/'driver',game_dir=private/'game',mapper='nohost')
    rec=dict(schema='goal2-g13-original-load/1',source_sha256=SOURCE_SHA,source='G4C.GL',
             source_commit='3cf746abec51dd11dadc695a65f4fb32df7701c8',status='aborted',
             method='Original DOS loader via original keys; no guest-memory edits, restore or CPU rewind',
             max_intervention='I3: explicit DOS date/time; I2 original keys and savestate observation',
             head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             keys=[],checkpoints=[])
    start=time.monotonic()
    def observe(label):
        times,state,raw=d.read();text=state.screen().text()
        with (public/'steps.jsonl').open('a') as out:
            out.write(json.dumps(dict(label=label,times=times,screen=text,digest=state.screen().digest()))+'\n')
        print(label,text,flush=True)
        return raw,text
    def key(*keys):
        rec['keys'].extend(keys);d.keys(*keys)
        return observe('keys '+','.join(keys))
    try:
        d.launch();observe('title')
        raw,text=key('y')
        # The launch can return during the title tune. A key may only dismiss that tune;
        # observe the real prompt before sending another original Y, never guess Escape here.
        for _ in range(3):
            if 'Do you want to load a saved game' not in text:break
            raw,text=key('y')
        if 'Please enter name' not in text and ('G4C' in text or 'select' in text.lower()):
            raw,text=key('Escape')
        if 'Please enter name' not in text:raise RuntimeError('Original filename editor not reached')
        # Original editor permits 80 characters (1771:03FF -> 214B:1086). Clear through
        # actual Backspace keys, including a title Y that may already have entered the editor.
        key(*(['BackSpace']*80))
        key('g','4','c');raw,text=key('Return')
        for _ in range(20):
            image,regs,hits=manager_frame(raw)
            if len(hits)==1 and not image.build_problems():
                path=private/'loaded-manager.sav';path.write_bytes(raw)
                rec['checkpoints'].append(dict(file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),
                    site='000E:75D1',bp=hits[0],ss=regs['SS'],build_problems=image.build_problems()))
                rec['status']='complete';break
            if time.monotonic()-start>120:raise RuntimeError('120-second collection bound reached')
            raw,text=observe('waiting for original manager menu')
        else:raise RuntimeError('Manager read frame not reached')
    except Exception as e:
        rec['error']=str(e);raise
    finally:
        rec['elapsed_s']=round(time.monotonic()-start,3)
        rec['driver_events']=d.events
        rec['runtime']=dict(dosbox=driver.dosbox_x(),config=d.config,clock_readback=d.clock_readback())
        if d.last_blob:
            last=private/'last-observation.sav';last.write_bytes(d.last_blob)
            rec['last_observation']=dict(file=str(last.relative_to(ROOT)),sha256=hashlib.sha256(d.last_blob).hexdigest())
        (public/'record.json').write_text(json.dumps(rec,indent=2)+'\n')
        d.terminate()


if __name__=='__main__':main()
