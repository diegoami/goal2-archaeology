#!/usr/bin/env python3
"""Read-only search for an already existing original-sized multi-manager .GL.

This only finds candidates. A candidate requires original-key provenance before use.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'notes/400-next'))
from inventory import SIZES
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=ROOT/'notes/400-last/multiplayer-save-search-r1.json';assert not out.exists();found={};errors=[]
    roots=(Path('/home/diego/projects/goal2-archaeology/.cache'),Path('/home/diego/projects/goal2-archaeology/scratch'),Path('/home/diego/projects/goal2-keep'))
    for root in roots:
        if not root.exists():continue
        for p in sorted(root.rglob('*')):
            if p.suffix.upper()!='.GL' or not p.is_file():continue
            try:
                raw=p.read_bytes();h=sha(raw)
                if h in found:found[h]['paths'].append(str(p));continue
                if len(raw)!=sum(SIZES):continue
                game=raw[sum(SIZES[:12]):sum(SIZES[:13])];cs=raw[sum(SIZES[:10]):sum(SIZES[:11])]
                found[h]=dict(sha256=h,paths=[str(p)],managers=game[0],managed_countries=[c for c in range(1,129) if cs[c*191+46]>128])
            except Exception as e:errors.append(dict(path=str(p),error=repr(e)))
    result=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),inputs=list(found.values()),errors=errors)
    out.write_text(json.dumps(result,indent=2)+'\n');print('distinct original-sized saves',len(found),'multiplayer candidates',sum(1 for x in found.values() if 1<x['managers']<=6))
if __name__=='__main__':main()
