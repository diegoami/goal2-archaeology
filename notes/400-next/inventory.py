#!/usr/bin/env python3
"""Read-only original .GL inventory; layout: named seg_1771_01.c 027B.

Only block sizes/derived identities and vacancy observations are published.
No load/conversion/reconstruction of a guest machine occurs here.
"""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
# Original 027B calls 0232 with these22 sizes, in this order (then closes).
SIZES=(0x810,0x8387,0xBF5,0x6DB,0x87,0x183,0x81,0x81,0x81,0xA14,
       0x603F,0xEF24,0x10E,0x3C2,0x195,0x4B48,0x2448,0x81,0x1C00,0x348,0x348,0x1E0)
def sha(b):return hashlib.sha256(b).hexdigest()
def inventory(assets):
    known=json.loads((ROOT/'notes/390/inventory.json').read_text())['assets'];out=[]
    for a in known:
        if not a['file'].endswith('.GL'):continue
        raw=(assets/a['file']).read_bytes();assert sha(raw)==a['sha256'] and len(raw)==sum(SIZES)
        countries=raw[sum(SIZES[:10]):sum(SIZES[:11])];managed=[]
        for country in range(1,129):
            record=countries[country*0xBF:(country+1)*0xBF]
            if record[0x2E]<=0x80:continue
            slots=[int.from_bytes(record[2*n:2*n+2],'little') for n in range(20)]
            managed.append(dict(country=country,manager_byte=record[0x2E],empty_slots=[i+1 for i,p in enumerate(slots) if p==0]))
        out.append(dict(file=a['file'],sha256=a['sha256'],managed=managed))
    assert len(out)==17
    return out
if __name__=='__main__':
    out=ROOT/'notes/400-next/inventory-r1.json';assert not out.exists()
    data=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),assets=inventory(Path('/tmp/goal2-archaeology-390/.cache/390/assets')))
    out.write_text(json.dumps(data,indent=2)+'\n');print('retained original .GL files:',len(data['assets']))
