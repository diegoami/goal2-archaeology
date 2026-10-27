#!/usr/bin/env python3
"""Freeze the preregistered launch inputs and fixed controls without executing a routine."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from construction import ROOT,make_manifest,write_new


def specs():
    cases=[('launch-zero',[0,0],{'velocity':[0,-1],'timer':2,'event':6,'projected':[0,-2]}),
           ('launch-small',[1,0],{'velocity':[1,-1],'timer':2,'event':6,'projected':[2,-2]}),
           ('launch-diagonal',[7,14],{'velocity':[1,2],'timer':7,'event':7,'projected':[7,14]})]
    result=[]
    def row(case,target,backend,role,label,expected=None,**extra):
        return dict(case=case,target=target,backend=backend,role=role,logical=case+'/'+label+'/'+backend,kind='launch',routine='0791:34C1',holder=2,state=5,required_prediction=expected,**extra)
    for case,target,expected in cases:
        for backend in ['original','port']:result.append(row(case,target,backend,'baseline','baseline',expected))
    for backend in ['original','port']:
        result.append(row('launch-zero',[0,0],backend,'no-effect','energy16',cases[0][2],energy=16))
    for case,target,_ in cases[1:]:result.append(row(case,target,'port','mutant','reverse-x',variant='launch-reverse-x'))
    result.append(row('launch-zero',[0,0],'original','repeat','repeat',cases[0][2]))
    result.append(row('launch-diagonal',[7,14],'port','repeat','repeat',cases[2][2]))
    assert len(result)==12 and len({r['logical'] for r in result})==12
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    data=make_manifest('launch',specs(),['notes/engine-study/T106/launch/build_manifest.py'])
    data['controls']=['zero launch energy16/32 no-effect compared on observed field values','production launch-reverse-x changes small/diagonal observations','fixed original zero and port diagonal repeats','wrong zero-idle and universal-halving hypotheses tested against ORIGINAL observations,not an authored actual model']
    write_new(a.out,data);print(f'wrote {len(data["invocations"])} complete synthetic invocation inputs;zero engine calls')


if __name__=='__main__':main()
