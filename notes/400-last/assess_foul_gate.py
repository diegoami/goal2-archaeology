#!/usr/bin/env python3
"""Read-only source ranking input for the existing 4DA9 foul gate (F027).

No guest execution, random draw, seed inspection or simulation. Reports actual
intrinsic hardness and saved tactic fields; setup may change tactics, so this
is a source-selection hypothesis, not a measured incident probability.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'notes/400-next'))
from inventory import SIZES
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=ROOT/'notes/400-last/foul-gate-assessment-r1.json';assert not out.exists();rows=[]
    assessment=json.loads((ROOT/'notes/400-last/source-assessment-r1.json').read_text())
    for source in assessment['sources']:
        if not source['upcoming']:continue
        raw=(ROOT/'.cache/400-next/assets'/source['file']).read_bytes();assert sha(raw)==source['sha256']
        cs=raw[sum(SIZES[:10]):sum(SIZES[:11])];ps=raw[sum(SIZES[:11]):sum(SIZES[:12])];names=raw[:SIZES[0]]
        name=lambda c:names[c*16+1:c*16+1+names[c*16]].decode('cp437')
        fixture=source['upcoming'][0];opponent=fixture['second'] if fixture['first']==source['name'] else fixture['first']
        other=next(c for c in range(1,129) if name(c)==opponent)
        def team(c):
            out=[]
            for i in range(11):
                p=int.from_bytes(cs[c*191+2*i:c*191+2*i+2],'little');r=ps[p*20:p*20+20]
                out.append(dict(slot=i+1,player=p,position=r[6],hardness=r[5]-(r[3]&1),energy=r[14],status=r[16],saved_own_tactic4=bool(r[15]&8),saved_own_override4=bool(r[15]&128)))
            return out
        rows.append(dict(file=source['file'],sha256=source['sha256'],opponent=opponent,own=team(source['country']),other=team(other)))
    data=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),collector_sha256=sha(Path(__file__).read_bytes()),sources=rows)
    out.write_text(json.dumps(data,indent=2)+'\n');print('source foul-gate fields inspected:',len(rows))
if __name__=='__main__':main()
