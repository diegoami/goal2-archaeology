"""Create an immutable current-source T123 acceptance index; no game execution."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
import pairs as P

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dir',required=True);opts=ap.parse_args();out=Path(opts.dir);out.mkdir()
    rel=lambda path:str(path.relative_to(ROOT));private={}
    def visit(value):
        if isinstance(value,dict):
            path=str(value.get('path',''))
            if path.startswith('.cache/') and 'sha256' in value:
                assert sha((ROOT/path).read_bytes())==value['sha256'];private[path]=value
            for item in value.values():visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    corpus={case[0]:rel(HERE/'paired-final-v3'/(case[0]+'.jsonl')) for case in P.F.runner.CASES}
    natural={case:rel(HERE/('natural-'+case+'-v4.jsonl')) for case in ('continental','world','ageing-continental','ageing-world')}
    managers={case:rel(HERE/name) for case,name in [('both','two-managers-v2.jsonl'),('skip','manager-skip-v2.jsonl')]}
    accepted=[rel(HERE/'ci-missing-published-after-v1.json')]+list(corpus.values())+list(natural.values())+list(managers.values())+[rel(HERE/'return-cpu-after-v2.jsonl'),rel(HERE/'pending-history-v2.json'),rel(HERE/'completed-history-v3.json')]
    sources=dict(P.sources())
    for path in accepted:
        data=(ROOT/path).read_text();row=json.loads(data);visit(row)
        for name,digest in row.get('sources',{}).items():assert sha((ROOT/name).read_bytes())==digest,('stale accepted source',path,name);sources[name]=digest
    extra=[ROOT/'tests'/name for name in ('test_port_route_fixture.py','test_port_silent.py','test_port_display.py','test_port_entrypoints.py','test_port_stages.py','test_port_update.py')]
    extra += [ROOT/'tools/port_test_runtime.py',ROOT/'tools/heavy.sh',ROOT/'experiments/E036-match-port/out/T60/fuzz.py',HERE.parent/'T124d/prepare.py']
    extra += [p for p in HERE.rglob('*.py') if '__pycache__' not in p.parts]
    for path in extra:sources[rel(path)]=sha(path.read_bytes())
    files={rel(path):sha(path.read_bytes()) for path in sorted(HERE.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc' and not any(part.startswith('acceptance') for part in path.relative_to(HERE).parts)}
    extras=[ROOT/'runtime/original_match/README.md',ROOT/'docs/requests/427-route.md',ROOT/'docs/requests/427-route-api.md',ROOT/'docs/tasks/T123.md',ROOT/'static/goal-exe/annotations/routines.tsv']
    extras += [path for path in (ROOT/'static/goal-exe/tables').rglob('*') if path.is_file()]
    names=subprocess.check_output(['git','diff','--name-only','62289f17e3386560537cb32804799765a437cb59','--','static/goal-exe/named'],text=True,cwd=ROOT).splitlines()
    extras += [ROOT/name for name in names]
    extras += [HERE.parent/'T124c/natural-groups-input-v1.jsonl',HERE.parent/'T124d/natural-inputs-v1.jsonl',HERE.parent/'T124t/continuation-context.jsonl']
    for path in extras:files[rel(path)]=sha(path.read_bytes())
    for case in P.F.runner.CASES:
        path=P.F.runner.DL/case[3];digest=P.F.runner.expected(case[3]);assert sha(path.read_bytes())==digest
        private[rel(path)]={'path':rel(path),'sha256':digest,'kind':'published-E040-savestate'}
    retained={rel(path):sha(path.read_bytes()) for path in sorted((ROOT/'.cache/t123').rglob('*')) if path.is_file() and path.suffix in ('.mem','.json')}
    payload={'schema':'t123-acceptance/1','base_commit':'62289f17e3386560537cb32804799765a437cb59',
      'source_freeze_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'source_hashes':sources,'file_hashes':files,'private_inputs':private,'private_retained_hashes':retained,
      'corpus':corpus,'natural':natural,'managers':managers,'return_effects':rel(HERE/'return-cpu-after-v2.jsonl'),
      'pending_history':rel(HERE/'pending-history-v2.json'),'completed_history':rel(HERE/'completed-history-v3.json'),
      'ci_fixture':rel(HERE/'ci-missing-published-after-v1.json'),'preservation':rel(HERE/'preserved-source-v3.json'),'call_audit':rel(HERE/'static-call-audit-v1.json'),
      'model':'inherited Codex GPT-6 family; exact variant unavailable',
      'scope':'actual ordinary port Match; incoming original16CPU preserved; actualreturned16CPU reach first6F1D unchanged; complete state/2 fields/ordered draws/routekeys/pages exact, with no additional exclusions; raw original memory remains private',
      'limits':'annual rollover/pool-list/active-round serialization unsupported; legal11 supplied only by comparison harness; original references CPython, standaloneAPI verifiedPyPy3.11 with positive original import/start/file denials; owner milestone review beforegoal2 adoption'}
    with (out/'index.json').open('x') as stream:json.dump(payload,stream,sort_keys=True,indent=2);stream.write('\n')
if __name__=='__main__':main()
