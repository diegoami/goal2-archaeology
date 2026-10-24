#!/usr/bin/env python3
"""Read-only G13 core input inventory; parses stored memory, executes no guest."""
import hashlib,json,subprocess,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def observe(raw):
    assert raw[:4]==b'G2C1';n=int.from_bytes(raw[4:8],'little');meta=json.loads(raw[8:8+n]);mem=zlib.decompress(raw[8+n:]);ds=(meta['load']+0x2581)*16
    w=lambda a:int.from_bytes(mem[a:a+2],'little');far=lambda o:w(ds+o)+16*w(ds+o+2)
    countries=far(0xA917);pool=far(0xA927);managed=[]
    for c in range(1,129):
        cr=countries+c*191;manager=mem[cr+0x2E]-0x80
        if manager<=0:continue
        assert manager<=6
        base=w(ds+0x6D18+2*manager)
        managed.append(dict(country=c,manager=manager,empty_squad_slots=[s+1 for s in range(20) if w(cr+2*s)==0],empty_pool_rows=[s+1 for s in range(80) if w(pool+2*(base+s))==0]))
    return managed
def main():
    out=ROOT/'notes/400-next/core-inventory-r1.json';assert not out.exists()
    kept=ROOT/'.cache/400-next/core-inventory-assets';kept.mkdir(exist_ok=False)
    found={};errors=[]
    for base in (Path('/home/diego/projects/goal2/.cache'),Path('/home/diego/projects/goal2-keep')):
        for p in sorted(base.rglob('g13-*.g2core')):
            try:
                raw=p.read_bytes();h=sha(raw)
                if h in found:found[h]['sources'].append(str(p));continue
                managed=observe(raw);f=kept/(h+'.g2core');f.write_bytes(raw)
                found[h]=dict(sha256=h,sources=[str(p)],file=str(f.relative_to(ROOT)),managed=managed)
            except Exception as e:errors.append(dict(source=str(p),error=repr(e)))
    data=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),inputs=list(found.values()),errors=errors)
    out.write_text(json.dumps(data,indent=2)+'\n');print('unique G13 inputs inspected:',len(found),'errors:',len(errors))
if __name__=='__main__':main()
