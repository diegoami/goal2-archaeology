"""Diagnose preserved T117 golden metadata/full memory on actual PyPy drives.
Historical-profile arm overrides only the old006C stub through existing ports=
configuration; no production source or golden file is changed.
"""
import argparse,hashlib,importlib.util,json,subprocess,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
from original_match import Image,Match,Fixture,port
from original_match.assets import reference_image
from tests.test_port_overhead_t117 import RECEIPT,RECEIPT_PORTS

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,default=repr).encode()).hexdigest()
def drive(historical):
    spec=importlib.util.spec_from_file_location('_t123_t117_boundaries',ROOT/'experiments/E033-original-match-kit/save_boundaries.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    overrides=[]
    if historical:
        module=types.ModuleType('_t123_old_display');module.__package__='original_match.port'
        source=subprocess.check_output(['git','show','62289f17e3386560537cb32804799765a437cb59:runtime/original_match/port/display.py'],text=True,cwd=ROOT)
        exec(compile(source,'pre-T123-display.py','exec'),module.__dict__)
        registry=port.Registry('display','historicalT117 profile006C only')
        for entry in port._module_registry('display').entries.values():registry._add(module.PORTS.entries['0791:006C'] if entry.address=='0791:006C' else entry)
        overrides=[(registry,None)]
    m=Match(Image.from_savestate(reference_image(ROOT/'.cache/dl')),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True,ports=overrides)
    def policy(match,data):match.answer(quick=True) if data['context']=='half_time' else match.answer()
    events=h.drive(m,policy,());result=m.result();actual_calls=dict(result['ports']['calls']);before=json.loads(RECEIPT.read_text())
    added=[name for name in result['ports']['names'] if name not in RECEIPT_PORTS]
    for registry,_ in port.load(added):
        for address in registry.entries:assert result['ports']['calls'].pop(address)==0,(registry.name,address)
    result['ports']['names']=[name for name in result['ports']['names'] if name in RECEIPT_PORTS]
    for address in ('0791:DEA6','1771:5BF6','1771:7812','23E4:0831','23E4:0900'):assert result['ports']['calls'].pop(address)==0,address
    return {'profile':'historical006C' if historical else 'current-real006C','events':len(events),'events_equal':digest(events)==before['events_sha256'],
       'result_equal_after_asserted_zero_metadata_removal':digest(result)==before['result_sha256'],
       'memory_equal':hashlib.sha256(m.m.read(0,0x110000)).hexdigest()==before['memory_sha256'],
       'result_sha256':digest(result),'memory_sha256':hashlib.sha256(m.m.read(0,0x110000)).hexdigest(),
       '006C_calls':actual_calls['0791:006C'],'00DB_calls':actual_calls['214B:00DB'],
       'new_existing_module_calls':{a:actual_calls[a] for a in ('1771:5BF6','1771:7812','23E4:0831','23E4:0900')}}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    with Path(args.out).open('x') as stream:
        for historical in (False,True):
            row=drive(historical);stream.write(json.dumps(row,sort_keys=True)+'\n');stream.flush();print(json.dumps(row,sort_keys=True),flush=True)
