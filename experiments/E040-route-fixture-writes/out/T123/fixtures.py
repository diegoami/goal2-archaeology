"""Original-backed T123 fixture preparation; reference work only on CPython."""
import hashlib,importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS,GuestError
from original_match.port.tables import load
spec=importlib.util.spec_from_file_location('_t123_e040_runner',HERE.parents[1]/'runner.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

def image(case='E040-r0004',manager2=False):
    row=next(c for c in runner.CASES if c[0]==case);raw=(runner.DL/row[3]).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==runner.expected(row[3])
    img=Image.from_savestate(raw);img.tables=load(ROOT/'static/goal-exe/tables')
    if manager2:
        game=img.far(0xA923);managers=img.far(0xA91F);countries=img.far(0xA917);old=img.memory[managers+3*129]
        other=next(c for c in range(1,129) if c!=old and img.memory[countries+191*c+46]<=128)
        img.memory[countries+191*old+46]=130;img.memory[managers+3*130]=old
        img.memory[countries+191*other+46]=129;img.memory[managers+3*129]=other;img.memory[game]=2
    return img


def entry(case='E040-r0004',manager2=False):
    class EntryOracle(R.Route):
        def _match(self):self.m.stop('t123-original-entry')
    img=image(case,manager2);r=EntryOracle(img,entry='play_round',record_writes=False,match_entry=True)
    try:r.call()
    except GuestError:
        if r.m.stop_reason!='t123-original-entry':raise
    else:raise AssertionError('original F1F6 entry not reached')
    out=Image(r.header+r.m.read(0,MEM_SIZE)+r.tail);out.tables=img.tables
    context={k:r.m.reg(k) for k in REGS}
    assert (context['ESP'],context['EBP'])==(0x3EC0,0x3EDE)
    g=r.m.far(0xA923);idx=r.m.word_at(g+0x26);fx=r.m.read(r.m.far(0xA92B)+8*(idx-1),8)
    return out,context,{'first':int.from_bytes(fx[4:6],'little'),'second':int.from_bytes(fx[6:8],'little'),'index':idx,'kind':fx[2]}
