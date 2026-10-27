#!/usr/bin/env python3
"""Freeze all wall slots, two guard interventions and fixed repeats; no engine calls."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from construction import make_manifest,write_new

LAYOUTS=[
    ('wall-near',[0,25],2,list(range(18,23)),[[x,30] for x in [2,1,0,-1,-2]]),
    ('wall-far-positive',[0,26],2,list(range(18,23)),[[-3,y] for y in range(-28,-23)]),
    ('wall-far-negative',[0,-26],13,list(range(7,12)),[[-3,y] for y in range(28,33)]),
]


def specs():
    rows=[]
    def row(case,spot,holder,slot,backend,role,label,prediction=None):
        return dict(case=case,spot=spot,holder=holder,slot=slot,backend=backend,role=role,
                    logical=f'{case}/{label}/{backend}',kind='wall',routine='0791:7621',
                    state=11,required_prediction=prediction)
    for case,spot,holder,slots,targets in LAYOUTS:
        for slot,target in zip(slots,targets):
            for backend in ['original','port']:
                rows.append(row(case,spot,holder,slot,backend,'baseline',f'slot{slot}',dict(target=target,state=11)))
    # Change only membership, or holder/defending side while leaving the positive spot.
    # Both witnesses must execute the real 4B64 fallback, not the wall target branch.
    for backend in ['original','port']:
        rows.append(row('wall-near',[0,25],2,17,backend,'guard','outside-slot6'))
        rows.append(row('wall-near',[0,25],13,7,backend,'guard','forward-false'))
    rows.append(row('wall-near',[0,25],2,18,'original','repeat','repeat-slot18',dict(target=[2,30],state=11)))
    rows.append(row('wall-far-negative',[0,-26],13,11,'port','repeat','repeat-slot11',dict(target=[-3,32],state=11)))
    assert len(rows)==36 and len({r['logical'] for r in rows})==36
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    data=make_manifest('wall',specs(),['notes/engine-study/T106/wall/build_manifest.py','notes/engine-study/T106/wall/analyse.py'])
    data['controls']={
        'guard_witnesses':'outside relative slot6 and holder_direction*spot_y<0;original and port must reach actual0791:4B64 and agree on observed target/state',
        'repeats':'fixed original near slot18 and port negative-far slot11:identical returned registers and full-memory SHA',
        'rejected_hypotheses':'far branch already at25;positive far y normalised to kick side;both far axes mirrored. Compare these hypotheses with ORIGINAL observations;not executed engine mutants.',
    }
    write_new(a.out,data);print('wrote36 complete synthetic wall inputs;zero engine calls')


if __name__=='__main__':main()
