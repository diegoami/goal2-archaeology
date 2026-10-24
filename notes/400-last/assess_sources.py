#!/usr/bin/env python3
"""Read-only next-fixture/formation assessment of existing E031 .GL inputs.

Layout: 1771:027B blocks (T89); game+26/+28 and fixture+2/+4/+6 (F023);
country squad words and player+6 position, +0E energy, +10 status (F008/F027).
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'notes/400-next'))
from inventory import SIZES
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=ROOT/'notes/400-last/source-assessment-r1.json';assert not out.exists();rows=[]
    for item in json.loads((ROOT/'notes/390/inventory.json').read_text())['assets']:
        if not item['file'].endswith('.GL'):continue
        raw=(ROOT/'.cache/400-next/assets'/item['file']).read_bytes();assert sha(raw)==item['sha256']
        blocks=[];off=0
        for n in SIZES:blocks.append(raw[off:off+n]);off+=n
        names,countries,players,game,fixtures=blocks[0],blocks[10],blocks[11],blocks[12],blocks[15]
        w=lambda b,o:int.from_bytes(b[o:o+2],'little')
        name=lambda c:names[16*c+1:16*c+1+names[16*c]].decode('cp437')
        country=next(c for c in range(1,129) if countries[191*c+0x2E]>0x80)
        squad=[w(countries,191*country+2*i) for i in range(20)]
        start=w(game,0x26);end=w(game,0x28);upcoming=[]
        for i in range(max(0,start-1),end):
            f=fixtures[8*i:8*i+8]
            if len(f)!=8 or country not in (w(f,4),w(f,6)) or f[0]<0xFE:continue
            upcoming.append(dict(index=i+1,kind=f[2],first=name(w(f,4)),second=name(w(f,6))))
            if len(upcoming)==2:break
        rows.append(dict(file=item['file'],sha256=item['sha256'],country=country,name=name(country),fixture_cursor=start,positions=[players[20*p+6] for p in squad[:11]],zero_energy_slots=[i+1 for i,p in enumerate(squad[:11]) if players[20*p+0x0E]==0],upcoming=upcoming))
    result=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),sources=rows)
    out.write_text(json.dumps(result,indent=2)+'\n');print('existing sources assessed:',len(rows))
if __name__=='__main__':main()
