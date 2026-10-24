#!/usr/bin/env python3
"""Read-only search of existing decoded run records for managed target prompts."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATTERN=re.compile(r'select\s+(FREE\s*KICK|PENALTY)\s+taker',re.I)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=ROOT/'notes/400-last/record-search-r1.json';assert not out.exists();rows=[];hits=[]
    def walk(obj,path=()):
        if isinstance(obj,dict):
            for k,v in obj.items():yield from walk(v,path+(str(k),))
        elif isinstance(obj,list):
            for k,v in enumerate(obj):yield from walk(v,path+(str(k),))
        elif isinstance(obj,str):yield path,obj
    for file in sorted((ROOT/'runs').glob('E*/E*-r*.json')):
        raw=file.read_bytes()
        try:data=json.loads(raw)
        except Exception:continue
        matches=[]
        for path,value in walk(data):
            m=PATTERN.search(value)
            if m:matches.append(dict(path=list(path),prompt=m.group(0)))
        rows.append(dict(file=str(file.relative_to(ROOT)),sha256=sha(raw),hits=len(matches)))
        if matches:hits.append(dict(file=str(file.relative_to(ROOT)),matches=matches))
    rec=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),records=rows,matches=hits)
    out.write_text(json.dumps(rec,indent=2)+'\n');print('run records inspected',len(rows),'matching records',len(hits));print(hits)
if __name__=='__main__':main()
