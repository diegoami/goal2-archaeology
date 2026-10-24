#!/usr/bin/env python3
"""Independent read-only scan of retained native stack bytes for missed role3/4 candidates.

A candidate is not coverage: a live caller/read would still require validation.
No snapshot is modified or executed.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/driver')]
from original_match.image import Image
from emul.watched_match import cpu_state
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=ROOT/'notes/400-last/retained-target-scan-r1.json';assert not out.exists();records=[]
    for folder in sorted((ROOT/'notes/400-last').glob('G*-r*')):
        if not folder.is_dir():continue
        for row in map(json.loads,(folder/'steps.jsonl').read_text().splitlines()):
            raw=(ROOT/row['file']).read_bytes();assert sha(raw)==row['sha256'];im=Image.from_savestate(raw);r=cpu_state(raw);ss=r['SS']*16;m=im.memory;sp=r['ESP']&65535
            w=lambda o:int.from_bytes(m[ss+o:ss+o+2],'little');candidates=[]
            for bp in range(sp,65520):
                if w(bp+2)!=0x6D74:continue
                role=m[ss+bp+4];side=m[ss+bp+6];parent=w(bp)
                if role not in (3,4) or side not in (0,1) or not bp<parent<65520:continue
                if w(parent+2)!={3:0x6EEF,4:0x6F92}[role]:continue
                candidates.append(dict(bp=bp,parent=parent,role=role,side=side))
            records.append(dict(file=row['file'],sha256=row['sha256'],caption_match=bool(__import__('re').search(r'select\s+(?:PENALTY|FREE\s*KICK)\s+taker',row['screen'],__import__('re').I)),stack_candidates=candidates))
    data=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),snapshots=records)
    out.write_text(json.dumps(data,indent=2)+'\n');print('native snapshots inspected',len(records),'caption/stack candidates',sum(bool(r['caption_match'] or r['stack_candidates']) for r in records))
if __name__=='__main__':main()
